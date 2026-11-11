"""Regression tests for interactive order and payment handling."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import mock_open, patch

# Direct execution puts tests/ on the import path, rather than the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main  # pylint: disable=wrong-import-position


class MachineTestCase(unittest.TestCase):
    """Isolate machine state and replace interactive output and sleeps."""

    def setUp(self):
        self.output = io.StringIO()
        self.enterContext(redirect_stdout(self.output))
        self.enterContext(
            patch.object(main, "RESOURCE_TANKS", main.RESOURCE_CAPACITIES.copy())
        )
        self.enterContext(patch.object(main, "EARNED_CENTS", 0))
        self.report = self.enterContext(patch("builtins.open", mock_open()))
        self.enterContext(patch.object(main.time, "sleep"))
        drawer = patch.object(main, "CASH_DRAWER", dict.fromkeys(main.CASH_DRAWER, 0))
        drawer.start()
        self.addCleanup(drawer.stop)


class OrderingTests(MachineTestCase):
    """Check input boundaries and payment choices."""

    def test_menu_rejects_invalid_input_without_recursion(self):
        """Many invalid entries must retry without exhausting the call stack."""
        invalid = ["0", "-1", "-5", "4", "999", "text", ""] * 200
        with patch("builtins.input", side_effect=invalid + ["2"]):
            self.assertEqual(main.display_menu(), "(2) Espresso")
        self.assertEqual(self.output.getvalue().count("Invalid order."), len(invalid))

    def test_all_menu_choices(self):
        """Each displayed selection must return its corresponding drink."""
        for selection, drink in enumerate(main.menu, start=1):
            with self.subTest(selection=selection):
                with patch("builtins.input", return_value=str(selection)):
                    self.assertEqual(main.display_menu(), drink)

    def test_menu_exit(self):
        """The exit command must terminate menu selection."""
        with patch("builtins.input", return_value="exit"):
            with self.assertRaises(SystemExit):
                main.display_menu()

    def test_invalid_coins_do_not_change_drawer(self):
        """Invalid selections and exit must not add coins to the drawer."""
        invalid = ["0", "-1", "-5", "6", "999", "text", ""]
        with patch("builtins.input", side_effect=invalid + ["exit"]):
            self.assertFalse(main.pay_coffee("(2) Espresso"))
        self.assertEqual(sum(main.CASH_DRAWER.values()), 0)
        self.assertEqual(self.output.getvalue().count("Invalid coin."), len(invalid))

    def test_exact_payment_with_each_denomination(self):
        """Exact totals must succeed for all accepted coin denominations."""
        for selection, value in enumerate(main.CASH_DRAWER, start=1):
            with self.subTest(value=value):
                main.CASH_DRAWER = dict.fromkeys(main.CASH_DRAWER, 0)
                count = 500 // value
                # EUR 5 is not divisible by EUR 2; add EUR 1 for that case.
                entries = [str(selection)] * count
                if value == 200:
                    entries.append("4")
                with patch("builtins.input", side_effect=entries):
                    self.assertTrue(main.pay_coffee("(1) Latte"))
                self.assertEqual(main.CASH_DRAWER[value], count)

    def test_exact_payment_pours_coffee(self):
        """An exactly paid order must reach the pouring step."""
        with (
            patch("builtins.input", side_effect=["4", "4", "4"]),
            patch.object(main, "check_ingredients", return_value=True),
            patch.object(main.time, "sleep"),
        ):
            main.pour_coffee("(2) Espresso")
        self.assertIn("Espresso is ready!", self.output.getvalue())
        self.assertEqual(main.CASH_DRAWER[100], 3)

    def test_overpayment_still_succeeds(self):
        """Excess payment must still succeed and display change."""
        main.CASH_DRAWER[100] = 1
        with patch("builtins.input", side_effect=["5", "5"]):
            self.assertTrue(main.pay_coffee("(2) Espresso"))
        self.assertIn("1.00", self.output.getvalue())
        self.assertEqual(main.CASH_DRAWER[200], 2)
        self.assertEqual(main.CASH_DRAWER[100], 0)
        self.assertEqual(main.EARNED_CENTS, 300)


class ResourceTests(MachineTestCase):
    """Check dynamic tank creation, recipes, reports and refilling."""

    def test_new_resource_is_created_and_existing_drinks_still_work(self):
        """A capacity entry creates a full tank without changing old recipes."""
        with patch.dict(main.RESOURCE_CAPACITIES, {"syrup": 300}):
            main.RESOURCE_TANKS.clear()
            main.replenish_tanks()
            self.assertEqual(main.RESOURCE_TANKS, main.RESOURCE_CAPACITIES)
            self.assertEqual(main.RESOURCE_TANKS["syrup"], 300)
            main.RESOURCE_TANKS["syrup"] = 0
            with patch("builtins.input", side_effect=["5", "4"]):
                main.pour_coffee("(2) Espresso")
            self.assertEqual(main.RESOURCE_TANKS["syrup"], 0)
            self.assertEqual(main.RESOURCE_TANKS["water"], 1950)
            self.assertEqual(main.EARNED_CENTS, 300)
            main.replenish_tanks()
            self.assertEqual(main.RESOURCE_TANKS, main.RESOURCE_CAPACITIES)
            self.assertEqual(main.EARNED_CENTS, 300)

    def test_recipe_can_use_new_resource(self):
        """A new recipe ingredient is checked and consumed by its name."""
        with (
            patch.dict(main.RESOURCE_CAPACITIES, {"syrup": 300}),
            patch.dict(main.RESOURCE_TANKS, {"syrup": 10}),
            patch.dict(main.menu["(2) Espresso"]["recipe"], {"syrup": 10}),
        ):
            self.assertTrue(main.check_ingredients("(2) Espresso"))
            main.deduct_ingredients("(2) Espresso")
            self.assertEqual(main.RESOURCE_TANKS["syrup"], 0)
            self.assertFalse(main.check_ingredients("(2) Espresso"))

    def test_report_includes_dynamic_stock_and_preserves_state(self):
        """Reports show the actual quantities and capacities of every tank."""
        with (
            patch.dict(main.RESOURCE_CAPACITIES, {"syrup": 300}),
            patch.dict(main.RESOURCE_TANKS, {"syrup": 75}),
        ):
            before = main.RESOURCE_TANKS.copy()
            main.generate_report()
            written = "".join(
                call.args[0] for call in self.report.return_value.write.call_args_list
            )
            self.assertIn("Syrup: 75/300\n", written)
            self.assertIn("Water: 2000/2000\n", written)
            self.assertEqual(main.RESOURCE_TANKS, before)
            self.report.assert_called_with("levels.txt", "w", encoding="utf-8")

    def test_menu_commands_return_to_selection(self):
        """Report and replenish are handled without becoming drink orders."""
        main.RESOURCE_TANKS["water"] = 0
        with patch("builtins.input", side_effect=["report", "replenish", "2"]):
            self.assertEqual(main.display_menu(), "(2) Espresso")
        self.assertEqual(main.RESOURCE_TANKS, main.RESOURCE_CAPACITIES)


class TransactionTests(MachineTestCase):
    """Check resource accounting and successful or refused transactions."""

    def snapshot(self):
        """Capture inventory, cash and earnings for failed-order assertions."""
        return (
            main.RESOURCE_TANKS.copy(),
            main.CASH_DRAWER.copy(),
            main.EARNED_CENTS,
        )

    def test_cancelled_and_underpaid_orders_preserve_state(self):
        """Refund partial payments without consuming stock or earning money."""
        for command in ("cancel", "exit", "done"):
            with self.subTest(command=command):
                before = self.snapshot()
                with patch("builtins.input", side_effect=["4", command]):
                    main.pour_coffee("(2) Espresso")
                self.assertEqual(self.snapshot(), before)
                self.assertIn("Refund: 1.00", self.output.getvalue())

    def test_off_during_payment_preserves_state(self):
        """Shutdown must return inserted coins and leave inventory untouched."""
        before = self.snapshot()
        with patch("builtins.input", side_effect=["4", "off"]):
            with self.assertRaises(SystemExit):
                main.pour_coffee("(2) Espresso")
        self.assertEqual(self.snapshot(), before)

    def test_interrupted_payment_preserves_state(self):
        """Input interruption must refund coins before shutting down."""
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error):
                before = self.snapshot()
                with patch("builtins.input", side_effect=["4", error]):
                    with self.assertRaises(SystemExit):
                        main.pour_coffee("(2) Espresso")
                self.assertEqual(self.snapshot(), before)

    def test_unavailable_change_refuses_order(self):
        """An empty drawer cannot change two EUR 2 coins for an Espresso."""
        before = self.snapshot()
        with patch("builtins.input", side_effect=["5", "5"]):
            main.pour_coffee("(2) Espresso")
        self.assertEqual(self.snapshot(), before)
        self.assertIn("Refund: 4.00", self.output.getvalue())
        self.assertNotIn("Pouring", self.output.getvalue())

    def test_each_ingredient_shortage_refuses_before_payment(self):
        """One insufficient resource must refuse an order before collecting coins."""
        for resource in main.RESOURCE_CAPACITIES:
            with (
                self.subTest(resource=resource),
                patch.dict(main.RESOURCE_TANKS, {resource: 0}),
            ):
                before = self.snapshot()
                with patch("builtins.input") as prompt:
                    main.pour_coffee("(1) Latte")
                prompt.assert_not_called()
                self.assertEqual(self.snapshot(), before)

    def test_availability_check_does_not_deduct_stock(self):
        """Checking availability alone must be read-only."""
        before = self.snapshot()
        self.assertTrue(main.check_ingredients("(1) Latte"))
        self.assertEqual(self.snapshot(), before)

    def test_all_recipes_deduct_required_units(self):
        """Successful orders consume the specified ml and grams and earn the price."""
        cases = [
            ("(1) Latte", ["5", "5", "4"], (100, 25, 250), 500),
            ("(2) Espresso", ["5", "4"], (50, 20, 0), 300),
            ("(3) Cappuccino", ["5", "5", "3"], (250, 25, 100), 450),
        ]
        for drink, coins, recipe, price in cases:
            with self.subTest(drink=drink):
                before = self.snapshot()
                with patch("builtins.input", side_effect=coins):
                    main.pour_coffee(drink)
                after = self.snapshot()
                self.assertEqual(
                    tuple(
                        before[0][key] - after[0][key]
                        for key in ("water", "coffee", "oat_milk")
                    ),
                    recipe,
                )
                self.assertEqual(main.EARNED_CENTS - before[2], price)
                self.assertEqual(
                    sum(v * n for v, n in main.CASH_DRAWER.items()), main.EARNED_CENTS
                )

    def test_exact_remaining_resources_can_be_used(self):
        """An Espresso can use the last water and coffee without needing milk."""
        main.RESOURCE_TANKS.update(water=50, coffee=20, oat_milk=0)
        with patch("builtins.input", side_effect=["5", "4"]):
            main.pour_coffee("(2) Espresso")
        self.assertEqual(main.RESOURCE_TANKS, {"water": 0, "coffee": 0, "oat_milk": 0})
        with patch("builtins.input") as prompt:
            main.pour_coffee("(2) Espresso")
        prompt.assert_not_called()
        self.assertEqual(main.EARNED_CENTS, 300)

    def test_change_can_use_inserted_coins(self):
        """Inserted coins may supply change while net cash equals the sale price."""
        # EUR 0.20 + EUR 0.50 + EUR 2 + EUR 2 requires returning the inserted 20 cents.
        with patch("builtins.input", side_effect=["2", "3", "5", "5"]):
            self.assertTrue(main.pay_coffee("(3) Cappuccino"))
        self.assertEqual(main.CASH_DRAWER[20], 0)
        self.assertEqual(main.CASH_DRAWER[50], 1)
        self.assertEqual(main.CASH_DRAWER[200], 2)
        self.assertEqual(main.EARNED_CENTS, 450)

    def test_change_search_handles_greedy_dead_end(self):
        """Three 20-cent coins can make 60 cents when taking 50 would fail."""
        available = dict.fromkeys(main.COINS, 0)
        available.update({50: 1, 20: 3})
        before = available.copy()
        change = main.find_change(60, available)
        self.assertIsNotNone(change)
        self.assertEqual(change[20], 3)
        self.assertEqual(change[50], 0)
        self.assertEqual(available, before)

    def test_off_menu_command(self):
        """The assignment's off command must terminate menu selection."""
        with patch("builtins.input", return_value=" off "):
            with self.assertRaises(SystemExit):
                main.display_menu()

    def test_order_loop_recovers_and_shuts_down(self):
        """A cancelled order can be followed by a successful sale and shutdown."""
        with patch(
            "builtins.input",
            side_effect=["0", "2", "4", "cancel", "2", "5", "4", "off"],
        ):
            with self.assertRaises(SystemExit):
                main.main()
        self.assertEqual(
            main.RESOURCE_TANKS,
            {"water": 1950, "coffee": 480, "oat_milk": 1000},
        )
        self.assertEqual(main.EARNED_CENTS, 300)
        self.assertEqual(main.CASH_DRAWER, {10: 0, 20: 0, 50: 0, 100: 1, 200: 1})


if __name__ == "__main__":
    unittest.main()
