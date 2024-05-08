import xml.etree.ElementTree as ET
import os

class CustomerDatabase:
    def __init__(self, filename):
        self.filename = filename
        # Check if the file already exists and load it
        if os.path.exists(self.filename):
            self.tree = ET.parse(self.filename)
            self.root = self.tree.getroot()
        else:
            self.root = ET.Element("Customers")
            self.tree = ET.ElementTree(self.root)

    def add_customer(self, name, customer_type):
        if customer_type not in ["Business", "Private"]:
            raise ValueError("Type must be either 'Business' or 'Private'")

        vat = 0 if customer_type == "Business" else 21
        
        customer = ET.Element("Customer")
        ET.SubElement(customer, "Name").text = name
        ET.SubElement(customer, "Type").text = customer_type
        ET.SubElement(customer, "VAT").text = str(vat)
        self.root.append(customer)

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

