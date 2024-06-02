import InvoiceOceanAPI as IO
import CustomerDatabase


# Initialize API client
customer_db = CustomerDatabase.CustomerDatabase("CustomerDatabase.xml")
api_client = IO.InvoiceOceanAPI(api_token="1W1Ek5DP1MLTVFLyc2f", domain="zidoniseng", customer_db=customer_db)
    
seller_info = api_client.seller_information()
invoice_info = api_client.invoice_details()
buyer_info = api_client.buyer_transaction_details("Marathon Digital Holdings")

# Combine all data into one dictionary
complete_invoice_data = {**seller_info, **invoice_info, **buyer_info}

# Issue the invoice
api_client.create_invoice(complete_invoice_data)