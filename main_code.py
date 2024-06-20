import TransactionData as TD
from datetime import datetime
import CustomerDatabase

# Assuming you have the CSV file path
csv_file_path = 'sample_report.csv'

# Define the folder where PDFs are stored
folder_path = 'sample_invoices'

customer_database = CustomerDatabase.CustomerDatabase("CustomerDatabase.xml")

# Create an instance of the class and read the data
transaction_data = TD.TransactionData(csv_file_path)
transaction_data.read_data()

# List all months and ask for user input
months = transaction_data.get_months()
print("Available Months:")
for i, month in enumerate(months, 1):
    print(f"{i}. {month}")

try:
    month_index = int(input("Select a month by entering the number: ")) - 1
    selected_month = months[month_index]
    transaction_data.filter_by_month(selected_month)

    # List all teams and ask for user input
    teams = transaction_data.get_teams()
    print("Available Teams:")
    for i, team in enumerate(teams, 1):
        print(f"{i}. {team}")

    team_index = int(input("Select a team by entering the number: ")) - 1
    selected_team = teams[team_index]
    
    # Check if team exists in the customer database
    if not customer_database.customer_exists(selected_team):
        print(f"'{selected_team}' does not exist in the database. Please select:")
        print("1. Business")
        print("2. Private")
        customer_type_input = int(input("Enter the number for the customer type: "))
        customer_type = "Business" if customer_type_input == 1 else "Private"

        # Prompt for additional details
        business_name = input("Enter full business name:")
        vat_number = input("Enter VAT number: ")
        address_street = input("Enter address street: ")
        address_city = input("Enter address city: ")
        address_post_code = input("Enter address post code: ")
        address_country = input("Enter address country: ")

        # Add the new customer with all details
        customer_database.add_customer(selected_team, customer_type, business_name, vat_number, address_street, address_city, address_post_code, address_country)
        customer_database.save()
    
    
    transaction_data.filter_by_team(selected_team)

    # Display the filtered data by team
    print('Filtered by Team:')
    print(transaction_data.get_data())
except IndexError:
    print("Invalid selection, please enter a valid number.")
except ValueError:
    print("Invalid input, please enter a number.")


ref_ids = transaction_data.get_ref_ids()

#print("Ref_IDs:")
#for i, ref_id in enumerate(ref_ids, 1):
#        print(f"{i}. {ref_id}")

transaction_data.update_data_with_pdf_info(folder_path)
#data_frame = transaction_data.get_data()
#print(data_frame)  

has_data,_ = transaction_data.filter_by_invoice_month(selected_month)

if not has_data:
    print("There were no sales for this customer in selected month")
else:
     

    #Calculate sales and comissions
    sales, commissions = transaction_data.organize_data()

    # Calculate totals and save summary as before
    total_sales = sum([amount for _, _, _, _, amount in sales])
    total_commissions = sum([amount for _, _, _, _, amount in commissions])
    balance = total_sales + total_commissions

    # Print the updated data structures and totals to verify

    print("Total Sales:", total_sales)
    print("Total Commissions:", total_commissions)
    print("Balance:", balance)

    transaction_data.save_summary(sales, commissions, folder_path)


