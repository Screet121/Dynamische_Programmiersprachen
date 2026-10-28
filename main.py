"""Coffee machine simulation with payment, ingredients and status reports."""

import csv
import sys
import time

MACHINE_CURRENCY = "€"
STOCK = {
    "water": 2000,
    "coffee": 500,
    "oat_milk": 1000,
}

CASH_DRAWER = {
    0.10: 0,
    0.20: 0,
    0.50: 0,
    1.00: 0,
    2.00: 0,
}

menu = {
    "(1) Latte": {
        "price": 5.0,
        "recipe": {"water": 0.1, "coffee": 0.025, "oat_milk": 0.25},
    },
    "(2) Espresso": {
        "price": 3.0,
        "recipe": {"water": 0.025, "coffee": 0.02, "oat_milk": 0},
    },
    "(3) Cappuccino": {
        "price": 4.5,
        "recipe": {"water": 0.25, "coffee": 0.025, "oat_milk": 0.1},
    },
}


def display_menu():
    """Show the menu, handle service commands and return the chosen item."""
    for item, details in menu.items():
        print(f"{item}: ${details['price']:.2f}{MACHINE_CURRENCY}")

    order = input("What would you like to order?\n")
    if order == "status":
        status_report()
    if order == "replenish":
        refill_machine()
    if order == "exit":
        sys.exit()
    try:
        return list(menu)[int(order) - 1]  # check if order is in menu
    except (ValueError, IndexError):
        print("Invalid order. Please try again.")
        return display_menu()


def pour_coffee(order):
    """Prepare the ordered drink if ingredients and payment are available."""
    if check_ingredients(order):
        if pay_coffee(order):
            item = order[order.find(" ") + 1 :]
            print(f"Pouring {item}...")
            time.sleep(3)
            print(f"{item} is ready!")
        else:
            print("Payment was not succesful")


def pay_coffee(order):
    """Collect coins until the price is paid; return False if cancelled."""
    coins = {
        "(1) 10 Cent": 0.10,
        "(2) 20 Cent": 0.20,
        "(3) 50 Cent": 0.50,
        "(4) 1 Euro": 1.00,
        "(5) 2 Euro": 2.00,
    }
    price = menu[order]["price"]
    money_payed = 0
    print(f"Yout total is: {price:.2f}€")

    while money_payed < price:
        for coin, value in coins.items():
            print(f"{coin}: {value:}€")

        coin = input("Throw in a coin: ")
        CASH_DRAWER[(coins[list(coins)[int(coin) - 1]])] += 1
        print(CASH_DRAWER)
        if coin == "exit":
            return False
        selected_coin = list(coins)[int(coin) - 1]
        money_payed += coins[selected_coin]

    if money_payed > price:
        print(f"You get: {(money_payed - price):.2f}€ back")
    return True


def check_ingredients(order):
    """Consume the recipe ingredients; return False if stock is insufficient."""
    recipe = menu[order]["recipe"]
    if (
        STOCK["water"] < recipe["water"]
        and STOCK["coffee"] < recipe["coffee"]
        and STOCK["oat_milk"] < recipe["oat_milk"]
    ):
        print("Insufficient ingredients!")
        print(STOCK["water"], STOCK["coffee"], STOCK["oat_milk"])
        return False

    STOCK["water"] -= recipe["water"]
    STOCK["coffee"] -= recipe["coffee"]
    STOCK["oat_milk"] -= recipe["oat_milk"]
    return True


def status_report():
    """Print the machine status and write it to the txt and csv reports."""
    report = (
        f"Water: {STOCK['water']}ml, Coffee: {STOCK['coffee']}g, "
        f"Oat Milk: {STOCK['oat_milk']}ml \n{CASH_DRAWER}"
    )
    pathtxt = "/home/jogi/uni/2.Semester/Konzeptedp/reportfolder/report.txt"
    pathcsv = "/home/jogi/uni/2.Semester/Konzeptedp/reportfolder/report.csv"
    print(report)

    with open(pathtxt, "w", encoding="utf-8") as file:
        file.write(report)

    with open(pathcsv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "value"])
        writer.writerow(["watertank", STOCK["water"]])
        writer.writerow(["coffeeStorage", STOCK["coffee"]])
        writer.writerow(["oatMilkTank", STOCK["oat_milk"]])
        for coin, count in CASH_DRAWER.items():
            writer.writerow([f"{coin:.2f}", count])


def refill_machine():
    """Refill all ingredient tanks to their maximum capacity."""
    STOCK["water"] = 2000
    STOCK["coffee"] = 500
    STOCK["oat_milk"] = 1000


while True:
    pour_coffee(display_menu())
    time.sleep(2)
