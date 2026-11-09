# Coffee Machine — agent guide

## Scope and current state

This is a student Python console project implementing seven incremental coffee
machine tasks. Keep solutions readable and proportionate to a small learning
project; prefer the standard library and straightforward functions.

Assessment date: 2026-11-09. The application is an early prototype, with parts of
Tasks 1–5 present and Tasks 6–7 missing. No task is fully verified end to end.
The bugs below are observed behavior, not intended requirements.

Update after the ordering fixes: menu and coin inputs now validate integer ranges
before indexing, invalid menu retries use a loop, payment `exit` returns `False`,
and exact payment succeeds. Payment totals use integer cents. `main()` has an
import guard. The progress table below records the original assessment; its
input-crash and exact-payment findings are resolved by this update. Resource,
refund, physical change, and missing-feature findings remain open.

## Repository and development

- `main.py`: all menu, payment, resource logic, and the interactive loop.
- `pyproject.toml`: Python >=3.12; Black, Pylint, Mypy, and pytest configuration.
- `requirements.txt`: no runtime packages; its tkinter comment is stale (the app
  currently imports only `time`).
- `requirements-dev.txt`: development/checking tools.
- `.github/workflows/ci.yml`: Pylint, Black, and Mypy checks.
- `.github/workflows/security.yml`: dependency audit.
- `tests/test_ordering.py`: seven unittest regression tests, also discoverable by
  pytest. No report files, replenishment log, or CSV persistence exists yet.

Run with `python main.py` (Windows local environment:
`.\.venv\Scripts\python.exe main.py`). Importing `main.py` is safe: the interactive
loop runs only through the guarded `main()` entry point.

For code changes, run appropriate regression tests and the configured checks:
`python -m pytest`, `python -m black --check .`, `python -m pylint main.py`, and
`python -m mypy .` once the tools are installed. Pytest is configured for `tests/`,
and tests can also run with `python -m unittest discover -s tests -v`. All seven
regression tests passed using unittest after the ordering fixes. Pytest, Black,
Pylint, and Mypy were unavailable in the local virtual environment, so those
checks have not passed verification. Do not describe configured checks as passing
without running them.

## Progress against the assignment

| Task | Status | Evidence and gaps |
| --- | --- | --- |
| 1: menu, selection, pouring, repetition, off | Partial | Dictionary contains Latte EUR 5, Espresso EUR 3, Cappuccino EUR 4.50. Selection and a repeated loop exist; pouring is simulated. `exit` terminates from the menu, but `off` is unsupported. Payment bugs prevent normal exact-payment orders. |
| 2: price, accepted coins, payment and change | Partial / broken | Price shown before payment; all five denominations exist. Exact payment returns `None`; excess payment only prints change. No finite payment submission or proper insufficient-payment rejection/refund. Coin inputs can crash. |
| 3: recipes in menu | Partial | All recipes have water, coffee and oat milk entries, but units differ from resource storage. Espresso water is 0.025 instead of the required 50 ml. |
| 4: overall resources and coin compartments | Mostly represented | Tanks start at 2000 ml water, 500 g coffee, 1000 ml oat milk. Cash drawer has counters for all five coins, initially zero. Operational correctness remains blocked by payment/resource bugs. |
| 5: check and deduct resources, collect money | Partial / incorrect | Checks and mutations exist, but the shortage condition, units, and timing are wrong. Inserted coins are counted immediately, including for failed orders; change is never deducted. |
| 6: report, text file, replenish and log | Missing | No commands, report output file, refill logic, or replenishment log. |
| 7: save on off, restore state, load prices CSV | Missing | No CSV read/write or startup loading; prices are hardcoded. |

## Required values and conventions for future fixes

Use millilitres for liquids and grams for coffee throughout inventory and recipes:

| Drink | Price | Water (ml) | Coffee (g) | Oat milk (ml) |
| --- | --- | --- | --- | --- |
| Latte / Latte Macchiato | EUR 5.00 | 100 | 25 | 250 |
| Espresso | EUR 3.00 | 50 | 20 | 0 |
| Cappuccino | EUR 4.50 | 250 | 25 | 100 |

The assignment calls the first drink Latte in Task 1 and Latte Macchiato in
Task 3; treat these as the same menu item unless instructed otherwise.
Tank capacities: 2000 ml water, 500 g coffee, 1000 ml oat milk. Accepted coins:
10, 20, 50, 100, and 200 euro cents. Prefer integer cents for all money and coin
denominations to avoid float rounding problems.

## Original bug findings and resolution status

Findings 1–3 below are resolved, including negative/zero input validation. Their
reproductions are retained as context for regression tests. Findings 4–9 remain
open, except that payment cancellation via `exit` now works without an exception;
refunds of earlier coins and restoration of deducted ingredients remain missing.

1. **Ordering/payment IndexError (highest priority):** select a drink, then enter
   `6` at `Throw in a coin:`. In `pay_coffee`,
   `list(coins)[int(coin) - 1]` indexes beyond five entries before validation.
   Nonnumeric input raises `ValueError`; `exit` also raises `ValueError` because
   conversion occurs before the exit check. Zero and some negative numbers
   silently select coins through Python negative indexing. Validate commands,
   conversion, and the inclusive range before indexing or changing state.
2. **Menu input validation:** `display_menu` uses the same unchecked index
   approach. Entering `0` selects Cappuccino. Invalid large indices are caught,
   but the bare `except` hides unrelated errors, and recursive retries can
   exhaust the call stack. Use an iterative prompt and specific validation.
3. **Exact payment fails:** `pay_coffee` returns `True` only for overpayment.
   For Espresso, three `4` coin selections (three EUR 1 coins) return `None`,
   so `pour_coffee` reports unsuccessful payment despite collecting EUR 3.
4. **Insufficient funds/cancellation:** payment loops until the price is reached;
   there is no working finish/cancel path for underpayment. Coins already mutate
   the drawer and are not refunded if the order fails or the input crashes.
5. **Change is only printed:** no coins leave the drawer. Physical change
   availability is not checked; printed change and actual cash can disagree.
6. **Resource units:** recipes use fractional litres/kilograms while inventory
   uses millilitres/grams, so deductions are about 1000 times too small.
7. **Shortage logic:** `check_ingredients` joins shortages with `and`; a single
   insufficient ingredient must refuse the order. Check each ingredient and
   reject when any required quantity exceeds stock.
8. **Premature resource deduction:** `check_ingredients` changes inventory before
   payment succeeds. Split availability checking from committing deductions.
9. **Currency display:** `display_menu` prints both `$` and the euro symbol.
   Keep output consistently in euros. There are also minor prompt spelling errors.

The coin `6` crash, coin `exit` crash, and exact-payment `None` result were
reproduced by executing the existing functions with controlled inputs, excluding
the interactive top-level loop during the original assessment. The subsequent
ordering fixes are covered by the regression suite described above.

## Prioritized ToDos and implementation guidance

1. Input validation, iterative menu retries, exact payment, and the import guard
   are complete. Add `off` explicitly in future command work; currently only
   `exit` is supported (shutdown at the menu, cancellation during payment).
2. Correct recipes/units and availability checks. Keep failed, cancelled, and
   invalid orders from consuming ingredients or retaining payment.
3. Implement underpayment rejection/refund and actual change
   handling. Stage inserted coins, determine whether change can be made, then
   commit inventory and drawer updates only for successful orders. An empty
   initial drawer means some overpayments cannot be changed; define and test a
   clear refusal/refund policy. Track earned money as successful sale prices,
   separately from inserted amounts and returned change.
4. Implement `report`: display resource levels with units and earned money;
   write the same data to a text file.
5. Implement `replenish`: refill resources to the stated capacities and append a
   dated log entry recording what changed. Do not invent initial cash floats or
   coin refill quantities without documenting the chosen behavior.
6. Implement `off` CSV snapshot and startup restore of resources and each coin
   compartment. Persist any separate earnings value needed for accurate reports.
   Add a specialty-coffee prices CSV and load its prices at startup. Document
   filenames/schema and behavior for missing or malformed files; validate values
   before applying them and avoid overwriting a valid snapshot with partial data.
7. Update README usage and remove stale dependency comments once behavior is
   implemented. Keep changes focused; preserve unrelated user work.

Regression coverage should exercise menu/coin boundaries (including zero,
negative values, nonnumeric text and commands), exact and excess payment,
underpayment/cancellation, unavailable change, one depleted ingredient at a time,
exact remaining quantities, and unchanged state after failed orders. As Tasks
6–7 are implemented, cover report/log output and CSV round trips, including
missing/malformed files. Avoid real sleeps and real interactive input in tests.
