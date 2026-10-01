import tkinter as tk
from tkinter import ttk

window = tk.Tk()
window.title("Coffee Machine")
window.geometry("400x250")

menu = {
    "Latte": 5.0,
    "Espresso": 3.0,
    "Cappuccino": 4.5,
}

label = ttk.Label(
    window,
    text="Welcome to the Coffee Machine!"
)

label.grid(
    row=0,
    column=0,
    columnspan=3,
    pady=20
)


def select_item(name, price):
    item = name[name.find(" ") + 1:]

    label.config(
        text=f"Pouring {item}..."
    )

    window.after(
        3000,
        lambda: label.config(
            text=f"{item} is ready! ({price:.2f} €)"
        )
    )


def display_menu():
    for i, (name, price) in enumerate(menu.items()):
        row = i // 3 + 1
        column = i % 3

        button = ttk.Button(
            window,
            text=f"{name}\n{price:.2f} €",
            command=lambda n=name, p=price: select_item(n, p)
        )

        button.grid(
            row=row,
            column=column,
            padx=10,
            pady=10
        )


display_menu()

window.mainloop()