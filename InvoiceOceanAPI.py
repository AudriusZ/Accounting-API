import requests
import json

class InvoiceOceanAPI:
    def __init__(self, api_token, domain, customer_db):
        """
        Initialize the Invoice Ocean API client.
        :param api_token: The API token for authenticating requests.    
        :param domain: The domain for the Invoice Ocean account.
        """
        self.api_token = api_token
        self.base_url = f"https://{domain}.invoiceocean.com"
        self.customer_db = customer_db

    def download_invoice(self, invoice_id, output_path):
        """
        Downloads an invoice as a PDF file.
        :param invoice_id: The ID of the invoice to download.
        :param output_path: The local path to save the downloaded PDF.
        """
        url = f"{self.base_url}/invoices/{invoice_id}.pdf?api_token={self.api_token}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully and saved as {output_path}")
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")

    def create_invoice(self, invoice_data):
        """
        Creates an invoice with the specified data.
        :param invoice_data: A dictionary containing invoice data.
        """
        url = f"{self.base_url}/invoices.json"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = json.dumps({
            "api_token": self.api_token,
            "invoice": invoice_data
        })

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200 or response.status_code == 201:
            print("Invoice created successfully.")
            return response.json()  # Returning the JSON response from the API
        else:
            print(f"Failed to create the invoice. Status code: {response.status_code}, Response: {response.text}")
    
    def seller_information(self):
        return {
            "seller_name": "Židonis, MB",
            "seller_post_code": "LT50174",
            "seller_city": "Kaunas",
            "seller_street": "CRN 304502074, Savanorių pr. 151-25",
            "seller_country": "LT",
            "seller_email": "audrius@zidoniseng.com",
            "seller_www": "www.zidoniseng.com",
            "seller_phone": "+37067512920",
            "seller_tax_no": "LT100011515215",
            "seller_bank_account": "LT594010051004038414",
            "seller_bank": "Luminor Bank AB (SWIFT: AGBLLT2X)",
            "description_footer": "Židonis, MB, trading as Zidonis Engineering, is the legal entity issuing this invoice. Thank you for your business."
        }

    def invoice_details(self):
        return {
            "kind": "vat", #for vat invoices add dual currency and exchange rate
            "description": "Upwork Global Inc is the agent of payment for this invoice. Payment references: TT698917149, TT696731290, TT694539281", #get from main code
            "number": None,
            "sell_date": "2024-06", #get from main code
            "issue_date": "2024-06-31", #get from main code
            "payment_to": "2024-06-31", #get from main code
            "payment_type": "Upwork Global Inc",
            "status": "paid",
            "paid": "1800.00", #get from main code
            "positions": [
                {"name": "		Services for period (Project Name: <blank>)", "tax": "disabled", "total_price_gross": 1800.00, "quantity": 1}#1) get cost from main code, 2) get project name from invoices
            ]
        }

    # Method to fetch buyer details from the XML database
    def buyer_transaction_details(self, customer_name):
        buyer_details = self.customer_db.get_customer_details(customer_name)
        if buyer_details:
            return buyer_details
        else:
            return {
                "buyer_name": "Buyer name not available",
                "buyer_tax_no": "-",
                "buyer_street": "Address not available",
                "buyer_city": "City not available",
                "buyer_post_code": "Post code not available",
                "buyer_country": "Country not available"
            }


