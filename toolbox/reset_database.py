import CustomerDatabase

def main():
    # Path to the XML database file
    xml_file_path = "CustomerDatabase.xml"

    # Create an instance of the CustomerDatabase
    customer_db = CustomerDatabase.CustomerDatabase(xml_file_path)

    # Call the method to create a blank XML database
    customer_db.create_blank_database()

    # Confirm the database has been reset
    print("The customer database has been reset to blank.")

if __name__ == "__main__":
    main()
