import requests
import json

class InvoiceOceanAPI:
    def __init__(self, api_token, domain):
        """
        Initialize the Invoice Ocean API client.
        :param api_token: The API token for authenticating requests.    
        :param domain: The domain for the Invoice Ocean account.
        """
        self.api_token = api_token
        self.base_url = f"https://{domain}.invoiceocean.com"

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

