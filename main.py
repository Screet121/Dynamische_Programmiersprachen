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
    if pay_coffee(order):
        item = order[order.find(" ") + 1 :]
        print(f"Pouring {item}...")
        time.sleep(3)
        print(f"{item} is ready!")
    else:
        print("Payment was not succesful")

def pay_coffee(order):
    coins = {
        "(1) 10 Cent": 0.10,
        "(2) 20 Cent": 0.20,
        "(3) 50 Cent": 0.50,
        "(4) 1 Euro": 1.00,
        "(5) 2 Euro": 2.00,
    }
    price = menu[order]
    money_payed = 0
    print(f"Yout total is: {price:.2f}€")

    while money_payed < price:
        for coin, value in coins.items():
         print(f"{coin}: {value:}€")

        coin = input("Throw in a coin: ")
        if coin == "exit":
            return False
        selected_coin = list(coins)[int(coin)-1]
        money_payed += coins[selected_coin]

    if(money_payed > price):
        print(f"You get: {(money_payed-price):.2f}€ back")
        return True

while True:
    pour_coffee(display_menu())
    time.sleep(2)

# TASK 1
