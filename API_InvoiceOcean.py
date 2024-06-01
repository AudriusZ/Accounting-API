import InvoiceOceanAPI as IO

# Initialize API client
api_client = IO.InvoiceOceanAPI(api_token="1W1Ek5DP1MLTVFLyc2f", domain="zidoniseng")

# First entry: Seller Information
entry_one = {
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
    "seller_bank": "Luminor Bank AB (SWIFT: AGBLLT2X)"
}

# Second entry: Invoice details until 'status'
entry_two = {
    "kind": "vat",
    "description": "Upwork Global Inc is the agent of payment for this invoice. Payment references: T..",
    "number": None,
    "sell_date": "2024-04",
    "issue_date": "2024-05-11",
    "payment_to": "2024-05-18",
    "payment_type": "Upwork Global Inc",
    "status": "paid"
}

# Third entry: Buyer and transaction details
entry_three = {
    "paid": "60.23",
    "buyer_name": "Marathon Digital Holdings, Inc",
    "buyer_tax_no": "-",
    "buyer_street": "101 NE 3rd Avenue #1200",
    "buyer_city": "Fort Lauderdale",
    "buyer_post_code": "FL 33301",
    "buyer_country": "US",
    "positions": [
        {"name": "Services for period (Project Name: Desalination Prototype Design)", "tax": "disabled", "total_price_gross": 1212.50, "quantity": 1}
    ],
    "description_footer": "Židonis, MB, trading as Zidonis Engineering, is the legal entity issuing this invoice. Thank you for your business."
}

# Merge the entries into a single dictionary for the API call
complete_invoice_data = {**entry_one, **entry_two, **entry_three}

# Call to create an invoice
api_client.create_invoice(complete_invoice_data)
