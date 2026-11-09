# Coffee Machine - agent guide

## Current state

Student Python console project, reviewed 2026-11-09. Tasks 1-5 are implemented
and regression tested. The application is ready for development of Tasks 6-7;
reports, replenishment, logging and CSV persistence are intentionally absent.
Keep implementations readable and proportionate to a small learning project,
using the standard library where practical.

## Repository and checks

- `main.py`: menu, shared stock, payment, change, earnings and interactive loop.
  The guarded `main()` makes imports safe.
- `tests/test_ordering.py`: unittest regressions, also discoverable by pytest;
  direct execution resolves the project root without relying on the working directory.
  Currently 19 tests, split into `OrderingTests` and `TransactionTests`, with
  shared state isolation in `MachineTestCase`.
- `pyproject.toml`: Python >=3.12 and Black, Pylint, Mypy and pytest settings.
- `requirements-dev.txt`: development tools including pre-commit.
- `.pre-commit-config.yaml`: Black checks all formatting and Pylint checks staged
  Python files at commit; full pytest and Mypy checks run at push.
- `.github/workflows/ci.yml`: Black, Pylint and Mypy on Python 3.12.
  `security.yml` audits dependencies. CI does not currently run pytest.

Run `python main.py`. Install development dependencies with
`python -m pip install -r requirements-dev.txt`, then install both hook types
with `python -m pre_commit install --install-hooks`. The executable is named
`pre-commit`; the Python module is `pre_commit`.

Verify changes with `python -m pytest`, `python -m black --check .`,
`python -m pylint main.py tests/test_ordering.py`, and `python -m mypy .`.
Also check `python tests/test_ordering.py` when changing test imports.
Manual hook checks: `python -m pre_commit run --all-files` and
`python -m pre_commit run --all-files --hook-stage pre-push`.
On Windows the local interpreter is `.\.venv\Scripts\python.exe`.
Local checks use Python 3.14; do not claim remote Python 3.12 checks passed
without observing a new workflow run.

Latest local verification (2026-11-09): pytest and direct unittest execution
both pass all 19 tests; Black reports both Python files unchanged; Pylint scores
10/10; Mypy reports no issues. Hook configuration and installation instructions
are present, but `.pre-commit-config.yaml` is currently untracked. Include it
when committing the hook setup so other checkouts can install the same hooks.

## Task status and data conventions

| Task | State |
| --- | --- |
| 1 | Menu dictionary, prices, validated selection, simulated pouring, repeated orders, `off` and `exit` shutdown. |
| 2 | Price displayed before payment; accepted coins, exact payment, coin-count change accounting, underpayment refusal and refunds. All dispensing is simulated in the console. |
| 3 | Correct recipes using millilitres and grams. Latte uses the Task 3 Latte Macchiato recipe. |
| 4 | Water 2000 ml, coffee 500 g, oat milk 1000 ml; coin compartments start empty. |
| 5 | Availability checked before payment; stock deducted only after success; cash and earnings updated only for accepted payments. |
| 6 | To develop: report command, text report, replenish command and replenishment log. |
| 7 | To develop: shutdown CSV, startup state restore and specialty-coffee prices CSV. |

| Drink | Price (EUR) | Water (ml) | Coffee (g) | Oat milk (ml) |
| --- | --- | --- | --- | --- |
| Latte / Latte Macchiato | 5.00 | 100 | 25 | 250 |
| Espresso | 3.00 | 50 | 20 | 0 |
| Cappuccino | 4.50 | 250 | 25 | 100 |

`RESOURCE_CAPACITIES` defines refill targets. Current stock remains in
`WATER_TANK`, `COFFEE_STORAGE`, and `OAT_MILK_TANK`; these uppercase variables
are mutable state, not capacity constants. `COINS` and `CASH_DRAWER` use integer
cent keys (10, 20, 50, 100, 200). `EARNED_CENTS` counts successful sale prices,
not gross inserted coins or an initial cash float. Menu prices remain euros for
readability and convert to cents at payment. Do not mix euros and cents.

## Order and payment behavior

- Menu inputs must be within 1-3; coin selections within 1-5. Invalid input
  retries iteratively without modifying state. `off` shuts down; menu `exit`
  is a shutdown alias, while payment `exit` cancels only the order.
- `check_ingredients` checks any shortage and does not mutate stock. After
  successful payment, `pour_coffee` calls `deduct_ingredients` exactly once.
- Inserted coins stay in payment escrow. `done` below the price refuses the
  order; `cancel` and `exit` cancel it. All refund the inserted coins without
  altering the drawer or stock. Payment EOF/interrupt and `off` refund and exit.
- Payment completes automatically on reaching the price. `complete_payment`
  checks change against drawer plus inserted coins before updating cash and
  earnings. `find_change` uses bounded combinations rather than greedy-only
  selection, so available exact change is not missed.
- If change is impossible, refuse and refund the entire payment. Do not invent
  a starting cash float. Refusal and cancellation preserve stock, cash and earnings.
- `pay_coffee` commits cash/earnings and returns a success bool; it is a payment
  helper, not a full order. Production orders must go through `pour_coffee` so
  resource checks and consumption happen too.

## Resolved bugs and regression coverage

Resolved: menu/coin index errors, nonnumeric input crashes, recursive retries,
zero/negative indexing, exact-payment failure, mixed inventory units, incorrect
Espresso water, all-shortages-only checks, premature stock consumption, retained
cancelled payments, fictitious change, missing earnings tracking and mixed
currency output. No known blockers remain in Tasks 1-5 under the current model.

Regression tests cover input boundaries and repeated retries, all drink and coin
choices, exact payment, actual change and unavailable change, cancellation and
underpayment, shutdown/interrupt refunds, individual shortages, exact remaining
stock, correct recipes and earnings, read-only availability, bounded change
search and repeated order flow. Keep tests free of real sleeps and input.

## Current limitations

- All stock, cash and earnings are in memory and reset on a fresh process.
  Shutdown currently raises `SystemExit` without saving anything (Task 7).
- Graceful EOF/interrupt handling and refunds exist at the payment prompt;
  menu input and pouring sleeps do not have equivalent shutdown handling.
  Centralize shutdown paths when adding persistence, including `off` in payment.
- Menu prices are hardcoded; report and replenish commands are not recognized.
- `requirements.txt` has a stale tkinter comment; runtime code only imports
  `time`. This documentation cleanup does not block Task 6.

## Next development

1. Task 6: dispatch `report` and `replenish` at the drink menu without treating
   them as drinks. Report current stock with units and `EARNED_CENTS / 100` as
   euros; write the same data to a text file. Keep capacities separate from stock.
2. Replenish to `RESOURCE_CAPACITIES` and append a timestamped log describing
   actual changes. Do not reset earned money or invent cash refill quantities.
3. Task 7: save current stock, individual coin counts and earnings on shutdown;
   restore on startup. Add a prices CSV and load prices before showing the menu.
   Choose and document filenames and schemas during that task. Validate loaded
   values before applying them; avoid partial state and corrupting valid snapshots.
4. Add tests for report files, refill limits/log entries and CSV round trips,
   missing files and malformed input as those capabilities are implemented.
5. Hook environments are isolated; add runtime dependencies to appropriate hook
   environments if the application stops being standard-library-only.

Preserve unrelated user work, IDE files and assets. Do not commit or push changes
unless requested.
