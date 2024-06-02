import CustomerDatabase

# Initialize the customer database
customer_database = CustomerDatabase.CustomerDatabase("CustomerDatabase.xml")

# List customers
customers = customer_database.list_customers()
if not customers:
    print("No customers available to delete.")
else:
    print("List of Customers:")
    for i, customer in enumerate(customers, 1):
        print(f"{i}. {customer}")

    # Ask user which customer to delete
    try:
        customer_index = int(input("Enter the number of the customer you want to delete: ")) - 1
        customer_name = customers[customer_index]

        # Delete the customer
        if customer_database.delete_customer(customer_name):
            customer_database.save()
            print(f"{customer_name} has been deleted successfully.")
        else:
            print("Failed to delete the customer.")
    except IndexError:
        print("Invalid selection, please enter a valid number.")
    except ValueError:
        print("Invalid input, please enter a number.")
