import xml.etree.ElementTree as ET
import os

class CustomerDatabase:
    def __init__(self, filename):
        self.filename = filename
        try:
            if os.path.exists(self.filename):
                self.tree = ET.parse(self.filename)
                self.root = self.tree.getroot()
            else:
                self.root = ET.Element("Customers")
                self.tree = ET.ElementTree(self.root)
        except ET.ParseError as e:
            print(f"Failed to parse XML file: {e}")
            raise SystemExit("Please correct your XML file before running the script again.")

    def create_blank_database(self):
            """Creates a blank XML database with just the root element."""
            self.root = ET.Element("Customers")
            self.tree = ET.ElementTree(self.root)
            self.save()  # Save the newly created blank database
    
    def get_customer_details(self, name):
        print("Searching for:", name)
        for customer in self.root.findall('Customer'):
            customer_name = customer.find('Name').text
            #print("Checking customer:", customer_name)
            if customer_name == name:
                details = {
                    "buyer_name": customer.find('BusinessName').text if customer.find('BusinessName').text else "_",
                    "buyer_tax_no": customer.find('VATNumber').text if customer.find('VATNumber').text else "-",
                    "buyer_street": customer.find('Street').text if customer.find('Street').text else "Address not available",
                    "buyer_city": customer.find('City').text if customer.find('City').text else "City not available",
                    "buyer_post_code": customer.find('PostCode').text if customer.find('PostCode').text else "Post code not available",
                    "buyer_country": customer.find('Country').text if customer.find('Country').text else "Country not available"
                }
                #print("Found details:", details)
                return details
            else:
                print(f"No match for {name} in {customer_name}")
        #print("No customer found with name:", name)
        return None


    def add_customer(self, name, customer_type, business_name, vat_number, address_street, address_city, address_post_code, address_country):
        if customer_type not in ["Business", "Private"]:
            raise ValueError("Type must be either 'Business' or 'Private'")

        vat = 0 if customer_type == "Business" else 21
        customer = ET.Element("Customer")
        ET.SubElement(customer, "Name").text = name
        ET.SubElement(customer, "Type").text = customer_type
        ET.SubElement(customer, "VAT").text = str(vat)
        ET.SubElement(customer, "BusinessName").text = business_name
        ET.SubElement(customer, "VATNumber").text = vat_number
        ET.SubElement(customer, "Street").text = address_street
        ET.SubElement(customer, "City").text = address_city
        ET.SubElement(customer, "PostCode").text = address_post_code
        ET.SubElement(customer, "Country").text = address_country
        self.root.append(customer)


    def list_customers(self):
        customers = [customer.find('Name').text for customer in self.root.findall('Customer')]
        return customers

    def delete_customer(self, name):
        for customer in self.root.findall('Customer'):
            if customer.find('Name').text == name:
                self.root.remove(customer)
                return True
        return False  # No customer found

    def save(self):
        # Save the file with new data appended
        self.tree.write(self.filename, xml_declaration=True, encoding='utf-8')

    def customer_exists(self, name):
            for customer in self.root.findall('Customer'):
                if customer.find('Name').text == name:
                    return True
            return False
    
    def get_vat_for_customer(self, name):
        for customer in self.root.findall('Customer'):
            if customer.find('Name').text == name:
                return float(customer.find('VAT').text)
        return None  # Return None if the customer does not exist

