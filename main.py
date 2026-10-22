import time

machine_currency = "€"
watertank = 2000
coffeeStorage = 500
oatMilkTank = 1000

cashDrawer = {
    0.10: 0,
    0.20: 0,
    0.50: 0,
    1.00: 0,
    2.00: 0,
}

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
        cashDrawer[(coins[list(coins)[int(coin) - 1]])] += 1
        print(cashDrawer)
        if coin == "exit":
            return False
        selected_coin = list(coins)[int(coin) - 1]
        money_payed += coins[selected_coin]

    if money_payed > price:
        print(f"You get: {(money_payed - price):.2f}€ back")
        return True

def check_ingredients(order):
        global watertank, coffeeStorage, oatMilkTank

        recipe = menu[order]["recipe"]
        if (
            watertank < recipe['water'] 
            and coffeeStorage < recipe['coffee'] 
            and oatMilkTank < recipe['oat_milk']
        ):
            print("Insufficient ingredients!")
            print(watertank, coffeeStorage, oatMilkTank)
            return False

        watertank -= recipe['water']
        coffeeStorage -= recipe['coffee']
        oatMilkTank -= recipe['oat_milk']
        return True

while True:
    pour_coffee(display_menu())
    time.sleep(2)