import InvoiceOceanAPI as IO
# Example usage
api_client = IO.InvoiceOceanAPI(api_token="1W1Ek5DP1MLTVFLyc2f", domain="zidoniseng")
invoice_data = {
    "kind": "vat",
    "number": None,
    "sell_date": "2024-05-11",
    "issue_date": "2024-05-11",
    "payment_to": "2024-05-18",
    "seller_name": "Židonis, MB",
    "seller_tax_no": "LT100011515215",
    "buyer_name": "Client1 SA",
    "buyer_tax_no": "5252445767",
    "positions": [
        {"name": "Produkt A1", "tax": 23, "total_price_gross": 10.23, "quantity": 1},
        {"name": "Produkt A2", "tax": 0, "total_price_gross": 50, "quantity": 2}
    ]
}

api_client.create_invoice(invoice_data)
