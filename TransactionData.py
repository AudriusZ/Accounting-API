#This class deals with invoice data and summary extracted from Upwork

import pandas as pd
import os, glob
import pdfplumber
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime
import shutil
import CustomerDatabase
import itertools
from UserInteraction import UserInteraction



class TransactionData:
    def __init__(self, file_path, private_dir="."):
        self.file_path = file_path
        self.private_dir = private_dir
        self.data = None
        self.rejected_data = None
        self.processed_log_file = os.path.join(private_dir, "processed_ref_ids.log")
        self.previous_month_filter = None
        self.next_month_filter = None

    def read_data(self):
        """Load 2025-format Upwork CSV and normalize column names & datatypes."""
        try:
            df = pd.read_csv(self.file_path)
            df['Date'] = (df['Date']
              .astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
              .pipe(pd.to_datetime, format='%b %d, %Y', errors='coerce'))
            bad_rows = df['Date'].isna()
            if bad_rows.any():
                raise ValueError(f"Unparseable dates in rows: {df.index[bad_rows].tolist()}")

            # --- add / replace inside read_data() ------------------------------------
            # Map the true column names in your CSV to the legacy names that
            # the rest of the program expects
            col_map = {
                'Transaction ID':    'Ref ID',
                'Transaction type':  'Type',
                'Team':              'Team',        # unchanged
                'Client team':       'Team',        # Map 'Client team' to 'Team'
                'Amount $':          'Amount',      # new
                'Date':              'Date'         # unchanged
            }
            df = df.rename(columns=col_map)            
            df = df.loc[:, ~df.columns.duplicated()]
            if 'Transaction summary' in df.columns:
                df['Contract Title'] = df['Transaction summary']

            # Amount column is already a plain number with possible minus sign
            df['Amount'] = df['Amount'].astype(float)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            self.data = df            
            print()

        except FileNotFoundError:
            print("The file was not found.")
        except pd.errors.EmptyDataError:
            print("The file is empty.")
        except pd.errors.ParserError:
            print("The file is not in a valid CSV format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    
    def get_data(self):
            return self.data

    def get_months(self):
        """
        Returns a list of unique months from the 'Date' column.
        """
        if self.data is not None:
            return self.data['Date'].dt.strftime('%b').dropna().unique()
        return []

    def filter_by_summary_month(self, month):
        if self.data is not None:
            # Convert 'Date' to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(self.data['Date']):
                self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')

            # Ensure month format is abbreviated (e.g., 'Jan', 'Feb', etc.)
            month_date = pd.to_datetime('01 ' + month + ' 2000', format='%d %b %Y')
            
            # Calculate the next month
            next_month_date = month_date + relativedelta(months=1)
            next_month = next_month_date.strftime('%b')
            self.next_month_filter = next_month

            # Calculate the previous month
            previous_month_date = month_date - relativedelta(months=1)
            previous_month = previous_month_date.strftime('%b')
            self.previous_month_filter = previous_month

            # Filter data by selected month, previous month and the consecutive month
            is_selected_month = self.data['Date'].dt.strftime('%b') == month
            is_next_month = self.data['Date'].dt.strftime('%b') == next_month
            is_previous_month = self.data['Date'].dt.strftime('%b') == previous_month

            # Combine the two conditions
            combined_filter = is_selected_month | is_next_month | is_previous_month

            self.rejected_data = self.data[~combined_filter]
            self.data = self.data[combined_filter]
        else:
            print("Data is not loaded. Please load the data first.")

    def filter_by_invoice_month(self, month):
        if self.data is not None:
            print("Data before everything:\n", self.data)
            
            # Define the date format
            date_format = '%b %d, %Y'
            
            # Convert 'Invoice Date' to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(self.data['Invoice Date']):
                self.data['Invoice Date'] = pd.to_datetime(self.data['Invoice Date'], format=date_format, errors='coerce')

            # Ensure month format is abbreviated (e.g., 'Jan', 'Feb', etc.)
            print("Filtering for month:", month)

            # Filter data by month
            is_selected_month = self.data['Invoice Date'].dt.strftime('%b') == month
            
            print("Data before filtering:\n", self.data)
            print("Selected month filter:\n", is_selected_month)

            self.rejected_data = self.data[~is_selected_month]
            self.data = self.data[is_selected_month]

            print("Data after filtering:\n", self.data)

            # Check if there is any data left and return a tuple
            has_data = len(self.data) > 0
            return (has_data, self.data)
        else:
            print("Data is not loaded. Please load the data first.")

    def get_teams(self):
        """
        Returns a list of unique teams from the 'Team' column.
        """
        if self.data is not None and 'Team' in self.data.columns:
            teams = self.data['Team'].dropna().unique()
            
            filtered_teams = []
            for team in teams:
                team_data = self.data[self.data['Team'] == team]
                team_months = team_data['Date'].dt.strftime('%b').unique()
                
                # 1. If team has data in the Previous Month ONLY -> Exclude
                if self.previous_month_filter and len(team_months) == 1 and team_months[0] == self.previous_month_filter:
                    continue
                
                # 2. If team has data in the Next Month ONLY -> Check dates
                if self.next_month_filter and len(team_months) == 1 and team_months[0] == self.next_month_filter:
                    continue

                filtered_teams.append(team)
            return filtered_teams
        return []

    def filter_by_team(self, team_name):
        """
        Filters the data to include only the records from the specified team.
        """
        if self.data is not None:
            self.data = self.data[self.data['Team'] == team_name]
        else:
            print("Data is not loaded or no data available to filter.")    

    def exclude_processed_ids(self):
        """
        Scans a log file for previously processed Ref IDs and excludes them
        from the current dataset.
        """
        if self.data is None or self.data.empty:
            return

        if not os.path.exists(self.processed_log_file):
            print("[Info] No processed transaction log found. All transactions are considered new.")
            return

        try:
            with open(self.processed_log_file, 'r') as f:
                excluded_ids = {line.strip() for line in f if line.strip()}
        except Exception as e:
            print(f"Warning: Could not read log file '{self.processed_log_file}': {e}")
            return

        if excluded_ids:
            print(f"Found {len(excluded_ids)} previously processed transactions in log. Excluding them.")
            # Ensure Ref ID is string for comparison
            self.data = self.data.copy()
            self.data['Ref ID'] = self.data['Ref ID'].astype(str)
            initial_count = len(self.data)
            self.data = self.data[~self.data['Ref ID'].isin(excluded_ids)]
            print(f"Transactions reduced from {initial_count} to {len(self.data)}.")

    def get_ref_ids(self):
            """
            Returns a list of unique teams from the 'Team' column.
            """
            if self.data is not None and 'Ref ID' in self.data.columns:
                return self.data['Ref ID'].dropna().unique()
            return []

    def extract_pdf_data(self, ref_ids, folder_path):
        """Parse summary‑invoice PDFs and pull the date from the INVOICE header."""
        pdf_data = {}

        # ── regex patterns ──────────────────────────────────────────────
        id_re = re.compile(r'(?:INVOICE|Transaction ID)\s*#\s*([0-9]+)', re.I)

        # invoice header looks like:  INVOICE # T794252032  DATE Mar 30, 2025
        invoice_date_re = re.compile(
            r'INVOICE\s*#\s*T?\d+\s*DATE\s*([A-Z][a-z]{2} \d{1,2}, \d{4})',
            re.I | re.S
        )

        title_re = re.compile(
            r'\b(?:Hourly|Fixed Price|Bonus|Milestone)\s+(.+?)\s+[A-Z].+?[+-]\$',
            re.M
        )
        # ────────────────────────────────────────────────────────────────

        for ref_id in ref_ids:
            # find matching PDF(s) — new long filenames first, legacy fallback
            files = (glob.glob(os.path.join(folder_path, f'*T{ref_id}*_summary-invoice.pdf'))
                     or glob.glob(os.path.join(folder_path, f'T{ref_id}.pdf')))

            if not files:
                # Get transaction details for context
                row = self.data[self.data['Ref ID'] == ref_id].iloc[0]
                print(f"\n[!] PDF Missing for Ref ID: {ref_id}")
                print(f"    Date: {row['Date'].strftime('%Y-%m-%d')} | Amount: {row['Amount']} | Team: {row['Team']}")
                
                options = ["Retry (I have added the file)", "Use CSV Data (Fallback)", "Ignore (Skip transaction)"]
                choice = UserInteraction.select_option("Select action:", options)
                
                if choice.startswith("Retry"):
                    # Recursive call for this specific ID to try again
                    retry_data = self.extract_pdf_data([ref_id], folder_path)
                    pdf_data.update(retry_data)
                    continue
                elif choice.startswith("Ignore"):
                    pdf_data[ref_id] = {'Ignore': True}
                    continue
                else:
                    # Use CSV Data (Default behavior)
                    pdf_data[ref_id] = {'Invoice Number': None, 'Date': None, 'Contract Title': None}
                    continue

            file_path = files[0]
            try:
                # read *all* pages in case the invoice is multi‑page
                with pdfplumber.open(file_path) as pdf:
                    txt = "".join(p.extract_text() or "" for p in pdf.pages)

                m_id   = id_re.search(txt)
                m_date = invoice_date_re.search(txt)
                m_ttl  = title_re.search(txt)

                pdf_data[ref_id] = {
                    'Invoice Number': f"T{m_id.group(1)}" if m_id else None,
                    'Date':           m_date.group(1) if m_date else None,
                    'Contract Title': m_ttl.group(1).strip() if m_ttl else None
                }

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                pdf_data[ref_id] = {'Invoice Number': None,
                                    'Date': None,
                                    'Contract Title': None}

        return pdf_data


    
    def update_data_with_pdf_info(self, folder_path):
        # Initialize columns if they don't exist to prevent KeyErrors on empty DataFrames
        if 'Invoice Number' not in self.data.columns:
            self.data['Invoice Number'] = None
        if 'Invoice Date' not in self.data.columns:
            self.data['Invoice Date'] = None

        ref_ids = self.get_ref_ids()
        pdf_info = self.extract_pdf_data(ref_ids, folder_path)
        for index, row in self.data.iterrows():
            ref_id = row['Ref ID']
            
            # Handle "Ignore" choice
            if ref_id in pdf_info and pdf_info[ref_id].get('Ignore'):
                self.data.drop(index, inplace=True)
                continue

            if ref_id in pdf_info and pdf_info[ref_id]['Invoice Number'] is not None:
                self.data.at[index, 'Invoice Number'] = pdf_info[ref_id]['Invoice Number']
                self.data.at[index, 'Invoice Date'] = pdf_info[ref_id]['Date']
                # only overwrite title if it was missing
                if not pd.isna(row.get('Contract Title')) and row['Contract Title']:
                    # keep existing CSV title
                    pass
                else:
                    self.data.at[index, 'Contract Title'] = pdf_info[ref_id]['Contract Title']
            elif ref_id in pdf_info and not pdf_info[ref_id].get('Ignore'):
                # Fallback: Use CSV data if PDF is missing and not ignored
                self.data.at[index, 'Invoice Number'] = f"T{ref_id}"
                self.data.at[index, 'Invoice Date'] = row['Date']

    def organize_data(self):
        if self.data is not None:
            # Sorting data by 'Type'
            self.data = self.data[~self.data['Type'].eq('Withdrawal')]
            self.data.sort_values(by='Type', inplace=True)

            # Filtering and collecting 'Hourly' and 'Service Fee' data
            hourly_data = self.data[self.data['Type'].isin(['Fixed Price', 'Hourly'])]
            service_fee_data = self.data[self.data['Type'] == 'Service Fee']

            # Collecting Date, Amounts, and Ref IDs into lists
            sales = list(zip(hourly_data['Date'], hourly_data['Ref ID'], hourly_data['Invoice Date'], hourly_data['Invoice Number'], hourly_data['Amount']))
            commissions = list(zip(service_fee_data['Date'], service_fee_data['Ref ID'], service_fee_data['Invoice Date'], service_fee_data['Invoice Number'], service_fee_data['Amount']))

            # Collecting Contract Titles separately and checking for identical titles
            contract_titles = list(service_fee_data['Contract Title'].dropna().unique())
            
            # Check if all contract titles are identical
            if len(contract_titles) == 1:
                contract_title = contract_titles[0]  # If all identical, return only one title
            else:
                contract_title = contract_titles  # If not identical, return the list or handle differently

            return sales, commissions, contract_title
        else:
            print("Data is not loaded or not available.")
            return [], [], None

    def _is_month_partially_processed(self, team, folder_date_str):
        """
        Checks if any transactions for the given team and month (YYYY-MM)
        have already been processed by looking at the log file.
        """
        if not os.path.exists(self.processed_log_file):
            return False
            
        try:
            with open(self.processed_log_file, 'r') as f:
                processed_ids = {line.strip() for line in f if line.strip()}
            
            if not processed_ids:
                return False

            # Read CSV to find IDs for this month/team
            # We perform a lightweight read similar to read_data
            df = pd.read_csv(self.file_path)
            
            # Normalize Date
            df['Date'] = (df['Date']
              .astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
              .pipe(pd.to_datetime, errors='coerce'))
              
            # Map columns to ensure we find Team and Ref ID
            col_map = {'Transaction ID': 'Ref ID', 'Client team': 'Team'}
            df = df.rename(columns=col_map)
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Filter for the specific team and month
            df['Ref ID'] = df['Ref ID'].astype(str)
            relevant_ids = df[(df['Team'] == team) & (df['Date'].dt.strftime('%Y-%m') == folder_date_str)]['Ref ID']
            
            return any(rid in processed_ids for rid in relevant_ids)
            
        except Exception as e:
            print(f"Warning: Could not check processing history: {e}")
            return False

    def save_summary(self, sales, commissions, folder_path):
        team = self.data['Team'].iloc[0]
        db_path = os.path.join(self.private_dir, "CustomerDatabase.xml")
        customer_database = CustomerDatabase.CustomerDatabase(db_path)
        vat_rate = customer_database.get_vat_for_customer(team)
        if sales or commissions:
            # Calculate totals
            total_sales_gross = sum([amount for _, _, _, _, amount in sales])
            if vat_rate is None:
                vat_rate = 0  # default to 0% if VAT is not specified
            total_sales_net = total_sales_gross / (1 + vat_rate/100)
            total_commissions = sum([amount for _, _, _, _, amount in commissions])
            balance = total_sales_gross + total_commissions  # Adjusted to reflect net balance

            # Format date and team name for folder creation
            if sales:
                date = sales[0][2] if sales[0][2] else sales[0][0] # Use PDF date, fallback to CSV date
                folder_date = date.strftime('%Y-%m')
                #team = self.data['Team'].iloc[0]  # Assuming team data is valid and present
            else:
                date = commissions[0][2] if commissions[0][2] else commissions[0][0]
                folder_date = date.strftime('%Y-%m')
                #team = self.data['Team'].iloc[0]

            # Create a directory for summary
            base_folder_name = f"{folder_date}_{team}"
            folder_name = base_folder_name
            
            if self._is_month_partially_processed(team, folder_date):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                folder_name = f"{base_folder_name}_{timestamp}"

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            # Create subfolders for sales and commissions
            sales_folder = os.path.join(folder_name, 'sales')
            commissions_folder = os.path.join(folder_name, 'commissions')
        
            # Delete and recreate folders as needed
            for folder in [sales_folder, commissions_folder]:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
                os.makedirs(folder)

            # Save to a CSV file            
            summary_file_path = f"{folder_name}/{os.path.basename(folder_name)}.csv"
            with open(summary_file_path, 'w') as file:
                file.write(f"Total Sales Gross,{total_sales_gross:.2f}\n")
                file.write(f"VAT,{vat_rate:.2f}\n")
                file.write(f"Total Sales Net,{total_sales_net:.2f}\n")
                file.write(f"Total Commissions,{total_commissions:.2f}\n")
                file.write(f"Balance,{balance:.2f}\n")
                
                # Write payment references line to the summary file
                payment_references = ', '.join([f"T{invoice_number}" for _, _, _, invoice_number, _ in sales])
                payment_line = f"Upwork Global Inc is the agent of payment for this invoice. Payment references: {payment_references}\n"
                file.write(payment_line)

                # Write data for sales and commissions directly into the summary file
                file.write("\nSales\n")
                file.write("Date,Ref ID,Invoice Date,Invoice Number,Amount\n")
                for timestamp, ref_id, invoice_date, invoice_number, amount in sales:
                    date_only = timestamp.strftime('%Y-%m-%d')
                    file.write(f"\"{date_only}\",{ref_id},\"{invoice_date}\",{invoice_number},{amount:.2f}\n")
                
                file.write("\nCommissions\n")
                file.write("Date,Ref ID,Invoice Date,Invoice Number,Amount\n")
                for timestamp, ref_id, invoice_date, invoice_number, amount in commissions:
                    date_only = timestamp.strftime('%Y-%m-%d')
                    file.write(f"\"{date_only}\",{ref_id},\"{invoice_date}\",{invoice_number},{amount:.2f}\n")

                # Copy relevant PDF invoices to sales and commissions folders
                for (ts, ref_id, *_), folder in zip(sales, [sales_folder]*len(sales)):
                    for src in glob.glob(os.path.join(folder_path, f'*T{ref_id}*_summary-invoice.pdf')):
                        shutil.copy(src, os.path.join(folder, os.path.basename(src)))

            # Log the processed Ref IDs to a persistent file
            processed_ids = []
            if sales:
                processed_ids.extend([str(sale[1]) for sale in sales])  # sale[1] is Ref ID
            if commissions:
                processed_ids.extend([str(comm[1]) for comm in commissions])  # comm[1] is Ref ID

            if processed_ids:
                try:
                    with open(self.processed_log_file, 'a') as f:
                        for ref_id in set(processed_ids):  # Use set to avoid duplicates in the log
                            f.write(f"{ref_id}\n")
                    print(f"Logged {len(set(processed_ids))} new transaction IDs to '{self.processed_log_file}'.")
                except Exception as e:
                    print(f"Warning: Failed to log processed IDs: {e}")

            print(f"Data saved to {summary_file_path}")
        else:
            print("No data available to save.")
