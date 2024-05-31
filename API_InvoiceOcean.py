import InvoiceOceanAPI as IO
# Example usage
api_client = IO.InvoiceOceanAPI(api_token="1W1Ek5DP1MLTVFLyc2f", domain="zidoniseng")

invoice_data = {
    "kind": "vat",
    "description_footer": " Židonis, MB, trading as Zidonis Engineering, is the legal entity issuing this invoice. Thank you for your business.",
    "description" : "Upwork Global Inc is the agent of payment for this invoice. Payment references: T..", 
    "number": None,
    "sell_date": "2024-04",
    "issue_date": "2024-05-11",
    "payment_to": "2024-05-18",
    "payment_type" : "Upwork Global Inc", 
    "seller_name": "Židonis, MB",
    "seller_post_code" : "LT50174", 
    "seller_city" : "Kaunas", 
    "status" : "paid",
    "paid" : "60.23",  
    "seller_street" : "CRN 304502074, Savanorių pr. 151-25", 
    "seller_country" : "LT", 
    "seller_email" : "audrius@zidoniseng.com", 
    "seller_www" : "www.zidoniseng.com",     
    "seller_phone" : "+37067512920", 
    "seller_tax_no": "LT100011515215",
    "seller_bank_account" : "LT594010051004038414",
    "seller_bank" : "Luminor Bank AB (SWIFT: AGBLLT2X)", 
    "buyer_name": "Marathon Digital Holdings, Inc",
    "buyer_tax_no": "-",
    "buyer_street": "101 NE 3rd Avenue #1200",
    "buyer_city": "Fort Lauderdale",
    "buyer_post_code": "FL 33301",
    "buyer_country": "US",       
    "positions": [        
        {"name": "Services for period (Project Name: Desalination Prototype Design)", "tax": "disabled", "total_price_gross":  1212.50 , "quantity": 1}
    ]
}

api_client.create_invoice(invoice_data)
