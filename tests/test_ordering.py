"""Regression tests for interactive order and payment handling."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

# Direct execution puts tests/ on the import path, rather than the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


class OrderingTests(unittest.TestCase):
    """Check input boundaries and payment without interactive input or sleeps."""

    def setUp(self):
        self.output = io.StringIO()
        self.stdout = redirect_stdout(self.output)
        self.stdout.__enter__()
        self.addCleanup(self.stdout.__exit__, None, None, None)
        drawer = patch.object(main, "cashDrawer", dict.fromkeys(main.cashDrawer, 0))
        drawer.start()
        self.addCleanup(drawer.stop)

    def test_menu_rejects_invalid_input_without_recursion(self):
        invalid = ["0", "-1", "-5", "4", "999", "text", ""] * 200
        with patch("builtins.input", side_effect=invalid + ["2"]):
            self.assertEqual(main.display_menu(), "(2) Espresso")
        self.assertEqual(
            self.output.getvalue().count("Invalid order."), len(invalid)
        )

    def test_all_menu_choices(self):
        for selection, drink in enumerate(main.menu, start=1):
            with self.subTest(selection=selection):
                with patch("builtins.input", return_value=str(selection)):
                    self.assertEqual(main.display_menu(), drink)

    def test_menu_exit(self):
        with patch("builtins.input", return_value="exit"):
            with self.assertRaises(SystemExit):
                main.display_menu()

    def test_invalid_coins_do_not_change_drawer(self):
        invalid = ["0", "-1", "-5", "6", "999", "text", ""]
        with patch("builtins.input", side_effect=invalid + ["exit"]):
            self.assertFalse(main.pay_coffee("(2) Espresso"))
        self.assertEqual(sum(main.cashDrawer.values()), 0)
        self.assertEqual(
            self.output.getvalue().count("Invalid coin."), len(invalid)
        )

    def test_exact_payment_with_each_denomination(self):
        for selection, value in enumerate(main.cashDrawer, start=1):
            with self.subTest(value=value):
                main.cashDrawer = dict.fromkeys(main.cashDrawer, 0)
                count = 500 // round(value * 100)
                # EUR 5 is not divisible by EUR 2; add EUR 1 for that case.
                entries = [str(selection)] * count
                if value == 2:
                    entries.append("4")
                with patch("builtins.input", side_effect=entries):
                    self.assertTrue(main.pay_coffee("(1) Latte"))
                self.assertEqual(main.cashDrawer[value], count)

    def test_exact_payment_pours_coffee(self):
        with (
            patch("builtins.input", side_effect=["4", "4", "4"]),
            patch.object(main, "check_ingredients", return_value=True),
            patch.object(main.time, "sleep"),
        ):
            main.pour_coffee("(2) Espresso")
        self.assertIn("Espresso is ready!", self.output.getvalue())
        self.assertEqual(main.cashDrawer[1.0], 3)

    def test_overpayment_still_succeeds(self):
        with patch("builtins.input", side_effect=["5", "5"]):
            self.assertTrue(main.pay_coffee("(2) Espresso"))
        self.assertIn("1.00", self.output.getvalue())
        self.assertEqual(main.cashDrawer[2.0], 2)


if __name__ == "__main__":
    unittest.main()
