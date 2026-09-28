# Comments within quotation marks ("") represent quotes from the task slides.

import time

machine_currency = "€"

# "Define the items on the menu in a Python dictionary"
# "We will offer Latte, Espresso, and Cappuccino"
# "The price for a Latte will be 5 Euros, for an Espresso 3 Euros, and a Cappuccino 4.5 Euros"
menu = {
    "Latte": 5.0,
    "Espresso": 3.0,
    "Cappuccino": 4.5,
}

def display_menu():
    for item, price in menu.items():
        print(f"{item}: ${price:.2f}{machine_currency}")

    order = input("What would you like to order?\n") # "Allow the user to select an item"
    order = order[0].upper() + order[1:].lower()  # Auto-adjusts user order to match menu notation
    if order == "Exit": # "Allow the coffee machine to be turned off"
        exit()
    elif order not in menu:
        print("Invalid order. Please try again.")
        return display_menu()
    return order

# "Pour the coffee and repeat"
def pour_coffee(order):
    print(f"Pouring {order}...")
    time.sleep(3)
    print(f"{order} is ready!")

while True:
    pour_coffee(display_menu())
    time.sleep(2)