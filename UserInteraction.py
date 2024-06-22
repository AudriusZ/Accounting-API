from datetime import datetime

class UserInteraction:
    @staticmethod
    def select_option(prompt, options):
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        while True:
            try:
                choice = int(input("Select by entering the number: ")) - 1
                return options[choice]
            except (IndexError, ValueError):
                print("Invalid selection, please try again.")

    @staticmethod
    def confirm_date(suggested_date):
        print(f"Suggested Invoice Date: {suggested_date}")
        user_input = input("Is this date correct? (y/n): ")
        if user_input.lower() != 'y':
            new_date = input("Enter the new date (format YYYY-MM-DD): ")
            try:
                datetime.strptime(new_date, '%Y-%m-%d')
                return new_date
            except ValueError:
                print("Invalid date format. Using the suggested invoice date.")
        return suggested_date

    @staticmethod
    def ask_for_customer_details():
        details = {}
        details['customer_type'] = "Business" if int(input("Enter the number for the customer type (1 for Business, 2 for Private): ")) == 1 else "Private"
        details['business_name'] = input("Enter full business name: ")
        details['vat_number'] = input("Enter VAT number: ")
        details['address_street'] = input("Enter address street: ")
        details['address_city'] = input("Enter address city: ")
        details['address_post_code'] = input("Enter address post code: ")
        details['address_country'] = input("Enter address country: ")
        return details
