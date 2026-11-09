"""Interactive coffee machine with menu selection and coin payments."""

import time

MACHINE_CURRENCY = "€"
RESOURCE_CAPACITIES = {"water": 2000, "coffee": 500, "oat_milk": 1000}
WATER_TANK = RESOURCE_CAPACITIES["water"]
COFFEE_STORAGE = RESOURCE_CAPACITIES["coffee"]
OAT_MILK_TANK = RESOURCE_CAPACITIES["oat_milk"]

# All coin values and earned money are stored as integer euro cents.
COINS = {10: "10 Cent", 20: "20 Cent", 50: "50 Cent", 100: "1 Euro", 200: "2 Euro"}
CASH_DRAWER = dict.fromkeys(COINS, 0)
EARNED_CENTS = 0

menu = {
    "(1) Latte": {
        "price": 5.0,
        "recipe": {"water": 100, "coffee": 25, "oat_milk": 250},
    },
    "(2) Espresso": {
        "price": 3.0,
        "recipe": {"water": 50, "coffee": 20, "oat_milk": 0},
    },
    "(3) Cappuccino": {
        "price": 4.5,
        "recipe": {"water": 250, "coffee": 25, "oat_milk": 100},
    },
}


def display_menu():
    """Prompt until a valid drink is selected, or exit the program."""
    for item, details in menu.items():
        print(f"{item}: {details['price']:.2f}{MACHINE_CURRENCY}")

    while True:
        order = input("Choose a drink (1-3), or off to shut down:\n").strip().lower()
        if order in {"exit", "off"}:
            raise SystemExit
        try:
            selection = int(order)
        except ValueError:
            print("Invalid order. Please try again.")
            continue
        if 1 <= selection <= len(menu):
            return list(menu)[selection - 1]
        print("Invalid order. Please try again.")


def pour_coffee(order):
    """Simulate pouring the selected drink after checking stock and payment."""
    if check_ingredients(order):
        if pay_coffee(order):
            deduct_ingredients(order)
            item = order[order.find(" ") + 1 :]
            print(f"Pouring {item}...")
            time.sleep(3)
            print(f"{item} is ready!")
        else:
            print("Payment was not successful")


def find_change(amount, available):
    """Find exact change with bounded coin counts; return None if impossible."""
    combinations = {0: dict.fromkeys(COINS, 0)}
    for value in sorted(COINS, reverse=True):
        for total, counts in list(combinations.items()):
            limit = min(available[value], (amount - total) // value)
            for count in range(1, limit + 1):
                new_total = total + count * value
                if new_total not in combinations:
                    combination = counts.copy()
                    combination[value] = count
                    combinations[new_total] = combination
    return combinations.get(amount)


def refund(inserted):
    """Return escrowed coins without changing the cash drawer."""
    amount = sum(value * count for value, count in inserted.items())
    print(f"Refund: {amount / 100:.2f}{MACHINE_CURRENCY}")


def complete_payment(price, inserted):
    """Commit cash and sales earnings only if exact change is available."""
    global EARNED_CENTS  # pylint: disable=global-statement
    paid = sum(value * count for value, count in inserted.items())
    available = {value: CASH_DRAWER[value] + inserted[value] for value in COINS}
    change = find_change(paid - price, available)
    if change is None:
        print("Cannot make exact change. Order refused.")
        refund(inserted)
        return False
    for value in COINS:
        CASH_DRAWER[value] = available[value] - change[value]
    EARNED_CENTS += price
    if paid > price:
        print(f"You get: {(paid - price) / 100:.2f}{MACHINE_CURRENCY} back")
    return True


def pay_coffee(order):
    """Collect coins in escrow; refund cancellations and refused payments."""
    price = round(menu[order]["price"] * 100)
    inserted = dict.fromkeys(COINS, 0)
    paid = 0
    print(f"Your total is: {price / 100:.2f}{MACHINE_CURRENCY}")
    for number, label in enumerate(COINS.values(), start=1):
        print(f"({number}) {label}")

    while paid < price:
        try:
            coin = input("Coin (1-5), done, cancel, or off: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            refund(inserted)
            raise SystemExit from None
        if coin in {"done", "cancel", "exit", "off"}:
            print(
                "Insufficient payment. Order refused."
                if coin == "done"
                else "Order cancelled."
            )
            refund(inserted)
            if coin == "off":
                raise SystemExit
            return False
        try:
            selection = int(coin)
        except ValueError:
            print("Invalid coin. Please try again.")
            continue
        if not 1 <= selection <= len(COINS):
            print("Invalid coin. Please try again.")
            continue
        value = list(COINS)[selection - 1]
        inserted[value] += 1
        paid += value
    return complete_payment(price, inserted)


def check_ingredients(order):
    """Check availability without changing stock or accepting payment."""

    recipe = menu[order]["recipe"]
    if (
        WATER_TANK < recipe["water"]
        or COFFEE_STORAGE < recipe["coffee"]
        or OAT_MILK_TANK < recipe["oat_milk"]
    ):
        print("Insufficient ingredients!")
        print(WATER_TANK, COFFEE_STORAGE, OAT_MILK_TANK)
        return False

    return True


def deduct_ingredients(order):
    """Consume ingredients only after a successful payment."""
    global WATER_TANK, COFFEE_STORAGE, OAT_MILK_TANK  # pylint: disable=global-statement
    recipe = menu[order]["recipe"]
    WATER_TANK -= recipe["water"]
    COFFEE_STORAGE -= recipe["coffee"]
    OAT_MILK_TANK -= recipe["oat_milk"]


def main():
    """Run the interactive ordering loop."""
    while True:
        pour_coffee(display_menu())
        time.sleep(2)


if __name__ == "__main__":
    main()
