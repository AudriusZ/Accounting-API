import TransactionData as TD
import CustomerDatabase
import InvoiceOceanAPI as IO
from UserInteraction import UserInteraction
from datetime import datetime
import calendar

class MainApplication:
    def __init__(self, api_token, domain, customer_db_file, csv_file_path, folder_path):
        self.customer_database = CustomerDatabase.CustomerDatabase(customer_db_file)
        self.api_client = IO.InvoiceOceanAPI(api_token, domain, self.customer_database)
        self.transaction_data = TD.TransactionData(csv_file_path)
        self.folder_path = folder_path

    def run(self):
        self.transaction_data.read_data()
        selected_month = self.select_month()
        team = self.select_team()
        if not self.customer_database.customer_exists(team):
            self.add_new_customer(team)
        self.update_transaction_data_with_pdf()
        self.transaction_data.filter_by_invoice_month(selected_month)
        self.issue_invoice(selected_month, team)
        self.save_summary_locally(selected_month, team)

    def select_month(self):
        months = self.transaction_data.get_months()
        selected_month = UserInteraction.select_option("Available Months:", months)
        self.transaction_data.filter_by_summary_month(selected_month)
        return selected_month

    def select_team(self):
        teams = self.transaction_data.get_teams()
        selected_team = UserInteraction.select_option("Available Teams:", teams)
        self.transaction_data.filter_by_team(selected_team)
        return selected_team

    def add_new_customer(self, team):
        print(f"'{team}' does not exist in the database.")
        details = UserInteraction.ask_for_customer_details()
        self.customer_database.add_customer(
            team, details['customer_type'], details['business_name'],
            details['vat_number'], details['address_street'],
            details['address_city'], details['address_post_code'],
            details['address_country']
        )
        self.customer_database.save()

    def update_transaction_data_with_pdf(self):
        self.transaction_data.update_data_with_pdf_info(self.folder_path)

    def issue_invoice(self, month, team):
        sales, commissions, project_name = self.transaction_data.organize_data()
        if not sales:
            print("No sales data to process.")
            return

        invoice_date = self.get_invoice_date(month)
        invoice_numbers = {invoice for _, _, _, invoice, _ in sales}
        invoice_numbers_str = ', '.join(invoice_numbers)
        total_sales = sum([amount for _, _, _, _, amount in sales])

        seller_info = self.api_client.seller_information()
        invoice_info = self.api_client.invoice_details(
            paid=total_sales,
            date=invoice_date.strftime('%Y-%m-%d'),
            references=invoice_numbers_str,
            project_name=project_name
        )
        buyer_info = self.api_client.buyer_transaction_details(team)

        complete_invoice_data = {**seller_info, **invoice_info, **buyer_info}
        self.api_client.create_invoice(complete_invoice_data)
        print("Invoice created successfully.")

    def save_summary_locally(self, month, team):
        sales, commissions, _ = self.transaction_data.organize_data()
        if not sales:
            print("No summary data to save.")
            return

        # Convert dates in sales data to datetime objects to ensure compatibility
        updated_sales = []
        for sale in sales:
            date, ref_id, invoice_date, invoice_number, amount = sale
            # Ensure invoice_date is a datetime object
            if isinstance(invoice_date, str):
                try:
                    invoice_date = datetime.strptime(invoice_date, '%b %d, %Y')  # Adjusted to the correct format
                except ValueError:
                    print(f"Date format error: {invoice_date} is not in the expected format. Skipping this sale.")
                    continue
            updated_sales.append((date, ref_id, invoice_date, invoice_number, amount))
        
        if updated_sales:  # Ensure there's valid sales data to process
            self.transaction_data.save_summary(updated_sales, commissions, self.folder_path)
            print("Summary saved locally.")
        else:
            print("No valid sales data to save after processing.")



    def get_invoice_date(self, month):
        year_today = datetime.now().year
        month_number = datetime.strptime(month, '%b').month
        last_day = calendar.monthrange(year_today, month_number)[1]
        return datetime(year_today, month_number, last_day)

if __name__ == "__main__":
    app = MainApplication(
        api_token="1W1Ek5DP1MLTVFLyc2f",
        domain="zidoniseng",
        customer_db_file="CustomerDatabase.xml",
        csv_file_path='sample_report.csv',
        folder_path='sample_invoices'
    )
    app.run()
