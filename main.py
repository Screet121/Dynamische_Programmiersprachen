# TASK 1

import time

machine_currency = "€"
cashDrawer = []
watertank = 2000
coffeeStorage = 500
oatMilkTank = 1000

menu = {
    "(1) Latte": {
        "price": 5.0,
        "recipe": {
            "water": 0.1,
            "coffee": 0.025,
            "oat_milk": 0.25
        }
    },
    "(2) Espresso": {
        "price": 3.0,
        "recipe": {
            "water": 0.025,
            "coffee": 0.02,
            "oat_milk": 0
        }
    },
    "(3) Cappuccino": {
        "price": 4.5,
        "recipe": {
            "water": 0.25,
            "coffee": 0.025,
            "oat_milk": 0.1
        }
    },
}


def display_menu():
    for item, details in menu.items():
        print(f"{item}: ${details['price']:.2f}{machine_currency}")

    order = input("What would you like to order?\n")
    if order == "exit":
        exit()
    try:
        return list(menu)[int(order) - 1]  # check if order is in menu
    except:
        print("Invalid order. Please try again.")
        return display_menu()


def pour_coffee(order):
    if(check_ingredients(order)):
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
    price = menu[order]['price']
    money_payed = 0
    print(f"Yout total is: {price:.2f}€")

    while money_payed < price:
        for coin, value in coins.items():
            print(f"{coin}: {value:}€")

        coin = input("Throw in a coin: ")
        cashDrawer.append(coins[list(coins)[int(coin) - 1]])
        if coin == "exit":
            return False
        selected_coin = list(coins)[int(coin) - 1]
        money_payed += coins[selected_coin]

    if money_payed > price:
        print(f"You get: {(money_payed - price):.2f}€ back")
        return True

def check_ingredients(order):
        global watertank, coffeeStorage, oatMilkTank
        if (
            watertank >= menu[order]['recipe']['water'] 
            and coffeeStorage >= menu[order]['recipe']['coffee'] 
            and oatMilkTank >= menu[order]['recipe']['oat_milk']
        ):

            watertank -= menu[order]['recipe']['water']
            coffeeStorage -= menu[order]['recipe']['coffee']
            oatMilkTank -= menu[order]['recipe']['oat_milk']
            print(watertank, coffeeStorage, oatMilkTank)
            return True
        else:
            print("Insufficient ingrediens!")
            return False

while True:
    pour_coffee(display_menu())
    time.sleep(2)

# TASK 1
