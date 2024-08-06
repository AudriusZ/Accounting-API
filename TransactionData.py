#This class deals with invoice data and summary extracted from Upwork

import pandas as pd
import os
import pdfplumber
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime
import shutil
import CustomerDatabase
import itertools



class TransactionData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.rejected_data = None

    def read_data(self):
        try:
            self.data = pd.read_csv(self.file_path, parse_dates=['Date'])
            print(self.data['Date'].head())  # Add this to see the format
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

            # Calculate the previous month
            previous_month_date = month_date - relativedelta(months=1)
            previous_month = next_month_date.strftime('%b')

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
            # Convert 'Date' to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(self.data['Invoice Date']):
                self.data['Invoice Date'] = pd.to_datetime(self.data['Invoice Date'], errors='coerce')

            # Ensure month format is abbreviated (e.g., 'Jan', 'Feb', etc.)
            #month_date = pd.to_datetime('01 ' + month + ' 2000', format='%d %b %Y')
            
            # Calculate the next month
            #next_month_date = month_date + relativedelta(months=1)
            #next_month = next_month_date.strftime('%b')

            # Filter data by month and the consecutive month
            is_selected_month = self.data['Invoice Date'].dt.strftime('%b') == month
            #is_next_month = self.data['Invoice Date'].dt.strftime('%b') == next_month

            # Combine the two conditions
            #combined_filter = is_selected_month | is_next_month

            self.rejected_data = self.data[~is_selected_month]
            self.data = self.data[is_selected_month]

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
            return self.data['Team'].dropna().unique()
        return []

    def filter_by_team(self, team_name):
        """
        Filters the data to include only the records from the specified team.
        """
        if self.data is not None:
            self.data = self.data[self.data['Team'] == team_name]
        else:
            print("Data is not loaded or no data available to filter.")    

    def get_ref_ids(self):
            """
            Returns a list of unique teams from the 'Team' column.
            """
            if self.data is not None and 'Ref ID' in self.data.columns:
                return self.data['Ref ID'].dropna().unique()
            return []

    def extract_pdf_data(self, ref_ids, folder_path):
        pdf_data = {}
        for ref_id in ref_ids:
            file_name = f"T{ref_id}.pdf"
            file_path = os.path.join(folder_path, file_name)
            try:
                with pdfplumber.open(file_path) as pdf:
                    page = pdf.pages[0]
                    text = page.extract_text()
                    print(f"Processing file: {file_path}")  # Print the current PDF file being processed

                    # Existing Regex patterns
                    invoice_number_pattern = r"INVOICE\s*#\s*(T\d+)"
                    date_pattern = r"DATE\s*(\w+ \d{1,2}, \d{4})"
                    contract_title_pattern = r"Contract title:\s*(.+)\n"  # New pattern for extracting contract title

                    # Extracting data using Regex
                    invoice_number = re.search(invoice_number_pattern, text, re.IGNORECASE)
                    invoice_date = re.search(date_pattern, text, re.IGNORECASE)
                    contract_title = re.search(contract_title_pattern, text, re.IGNORECASE)  # Searching for contract title

                    # Check if data was found and assign to dictionary
                    if invoice_number and invoice_date:
                        invoice_number = invoice_number.group(1)
                        invoice_date = invoice_date.group(1)
                        contract_title = contract_title.group(1) if contract_title else None  # Handles missing contract title
                        pdf_data[ref_id] = {'Invoice Number': invoice_number, 'Date': invoice_date, 'Contract Title': contract_title}
                    else:
                        pdf_data[ref_id] = {'Invoice Number': None, 'Date': None, 'Contract Title': None}

            except FileNotFoundError:
                print(f"File not found: {file_path}")
                pdf_data[ref_id] = {'Invoice Number': None, 'Date': None, 'Contract Title': None}
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                pdf_data[ref_id] = {'Invoice Number': None, 'Date': None, 'Contract Title': None}

        return pdf_data
    
    def update_data_with_pdf_info(self, folder_path):
        ref_ids = self.get_ref_ids()
        pdf_info = self.extract_pdf_data(ref_ids, folder_path)
        for index, row in self.data.iterrows():
                ref_id = row['Ref ID']
                if ref_id in pdf_info and pdf_info[ref_id]['Invoice Number'] is not None:
                    self.data.at[index, 'Invoice Number'] = pdf_info[ref_id]['Invoice Number']
                    self.data.at[index, 'Invoice Date'] = pdf_info[ref_id]['Date']
                    self.data.at[index, 'Contract Title'] = pdf_info[ref_id]['Contract Title']

    def organize_data(self):
        if self.data is not None:
            # Sorting data by 'Type'
            self.data.sort_values(by='Type', inplace=True)

            # Filtering and collecting 'Hourly' and 'Service Fee' data
            hourly_data = self.data[self.data['Type'] == 'Hourly']
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


    def save_summary(self, sales, commissions, folder_path):
        team = self.data['Team'].iloc[0]
        customer_database = CustomerDatabase.CustomerDatabase("CustomerDatabase.xml")
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
                date = sales[0][2]  # Assume this is a datetime object
                folder_date = date.strftime('%Y-%m')
                #team = self.data['Team'].iloc[0]  # Assuming team data is valid and present
            else:
                date = commissions[0][2]  # Assume this is a datetime object
                folder_date = date.strftime('%Y-%m')
                #team = self.data['Team'].iloc[0]

            # Create a directory for summary
            folder_name = f"{folder_date}_{team}"
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
            summary_file_path = f"{folder_name}/{folder_name}.csv"
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
                for (timestamp, ref_id, _, _, _), folder in itertools.chain(
                        zip(sales, [sales_folder] * len(sales)),
                        zip(commissions, [commissions_folder] * len(commissions))
                    ):
                    src_pdf = os.path.join(folder_path, f"T{ref_id}.pdf")
                    dst_pdf = os.path.join(folder, f"T{ref_id}.pdf")
                    shutil.copy(src_pdf, dst_pdf)

            print(f"Data saved to {summary_file_path}")
        else:
            print("No data available to save.")
