# TASK 1

import time

machine_currency = "€"

menu = {
    "(1) Latte": 5.0,
    "(2) Espresso": 3.0,
    "(3) Cappuccino": 4.5,
}


def display_menu():
    for item, price in menu.items():
        print(f"{item}: ${price:.2f}{machine_currency}")

    order = input("What would you like to order?\n")
    if order == "exit":
        exit()
    try:
        return list(menu)[int(order) - 1]  # check if order is in menu
    except:
        print("Invalid order. Please try again.")
        return display_menu()


def pour_coffee(order):
    item = order[order.find(" ") + 1 :]
    print(f"Pouring {item}...")
    time.sleep(3)
    print(f"{item} is ready!")


while True:
    pour_coffee(display_menu())
    time.sleep(2)

# TASK 1
