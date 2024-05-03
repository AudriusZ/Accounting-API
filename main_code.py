import TransactionData as TD
from datetime import datetime

def filter_by_selected_month(data, selected_month):
    # Filter the data by checking if the month part of `invoice_date` matches `selected_month`
    filtered_data = []
    for date, ref_id, invoice_date, invoice_number, amount in data:
        try:
            # Convert the string date to a datetime object
            parsed_date = datetime.strptime(invoice_date, "%b %d, %Y")
            # Check if the month matches the selected month
            if parsed_date.strftime("%b") == selected_month:
                filtered_data.append((date, ref_id, invoice_date, invoice_number, amount))
        except ValueError:
            print(f"Error parsing date: {invoice_date}")
    return filtered_data



# Assuming you have the CSV file path
#csv_file_path = 'C:/Users/AudriusZidonis/Desktop/Accounting API/20240502/2024-05-02_transaction_report.csv'
csv_file_path = '2024-05-02_transaction_report.csv'

# Create an instance of the class and read the data
transaction_data = TD.TransactionData(csv_file_path)
transaction_data.read_data()

# If data was read successfully, it will be stored in the object
data_frame = transaction_data.get_data()

# You can now work with 'data_frame' which is a pandas DataFrame
#print('Raw: \n -----------------------------\n')
#print(data_frame)  

#transaction_data.filter_by_month('Apr')
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
    transaction_data.filter_by_team(selected_team)

    # Display the filtered data by team
    print('Filtered by Team:')
    print(transaction_data.get_data())
except IndexError:
    print("Invalid selection, please enter a valid number.")
except ValueError:
    print("Invalid input, please enter a number.")

#Calculate sales and comissions
sales, commissions = transaction_data.organize_data()

# Define the folder where PDFs are stored
#folder_path = 'C:/Users/AudriusZidonis/Desktop/Accounting API/20240502/2024-05-02_transaction_report'
folder_path = '2024-05-02_transaction_report'

# Extract Ref IDs for sales and commissions
sales_ref_ids = [ref_id for _, ref_id, _ in sales]
commissions_ref_ids = [ref_id for _, ref_id, _ in commissions]

# Extract PDF data for sales and commissions
sales_pdf_data = transaction_data.extract_pdf_data(sales_ref_ids, folder_path)
commissions_pdf_data = transaction_data.extract_pdf_data(commissions_ref_ids, folder_path)

# Update sales with PDF data, ensuring amount is a float
updated_sales = []
for date, ref_id, amount in sales:
    pdf_info = sales_pdf_data.get(ref_id, {})
    invoice_date = pdf_info.get('Date')
    invoice_number = pdf_info.get('Invoice Number')
    # Convert amount to float to avoid TypeError during summation
    updated_sales.append((date, ref_id, invoice_date, invoice_number, float(amount)))

# Update commissions with PDF data, ensuring amount is a float
updated_commissions = []
for date, ref_id, amount in commissions:
    pdf_info = commissions_pdf_data.get(ref_id, {})
    invoice_date = pdf_info.get('Date')
    invoice_number = pdf_info.get('Invoice Number')
    # Convert amount to float to avoid TypeError during summation
    updated_commissions.append((date, ref_id, invoice_date, invoice_number, float(amount)))

filtered_sales = filter_by_selected_month(updated_sales, selected_month)
filtered_commissions = filter_by_selected_month(updated_commissions, selected_month)

# Calculate totals and save summary as before
total_sales = sum([amount for _, _, _, _, amount in filtered_sales])
total_commissions = sum([amount for _, _, _, _, amount in filtered_commissions])
balance = total_sales + total_commissions

# Print the updated data structures and totals to verify
print("Updated Sales:", filtered_sales)
print("Updated Commissions:", filtered_commissions)
print("Total Sales:", total_sales)
print("Total Commissions:", total_commissions)
print("Balance:", balance)

transaction_data.save_summary(filtered_sales, filtered_commissions, folder_path)


