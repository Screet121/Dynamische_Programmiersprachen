# Konzepte dynamischer Programmiersprachen (Python) | FOM Hochschulzentrum Düsseldorf | B.Sc Wirtschaftsinformatik

Repo für die Aufgabe "Coffee Machine" innerhalb des Moduls.

## Using the machine

Run `python main.py`. Choose a drink with `1`, `2`, or `3`, then insert coins by
selecting `1` through `5` (10 cents, 20 cents, 50 cents, EUR 1, EUR 2).

Payment completes automatically when the price is reached. Use `done` to submit
an insufficient payment, or `cancel` / `exit` to abandon payment; inserted coins
are refunded. Use `off` to shut down, including during payment (with a refund).
At the drink menu, `exit` also shuts down.

The drawer starts empty. Change uses available drawer coins and inserted coins;
if exact change is unavailable, the order is refused and all inserted coins are
refunded. Stock and earnings change only for successful orders. Money is stored
in euro cents, liquids in millilitres, and coffee in grams. Reports, replenishment,
and CSV persistence (Tasks 6–7) are not implemented yet.

## Local Git checks

Install development dependencies and enable both hooks after cloning:

```powershell
python -m pip install -r requirements-dev.txt
python -m pre_commit install --install-hooks
```

Use the project's virtual environment for these commands. On Windows, you can
replace `python` with `.\.venv\Scripts\python.exe` without activating it.

- Before committing: Black checks formatting across the project; Pylint checks
  staged Python files. Black reports formatting changes rather than applying them.
- Before pushing: pytest runs the full test suite and Mypy checks the project.

Run both stages manually before committing or pushing:

```powershell
python -m pre_commit run --all-files
python -m pre_commit run --all-files --hook-stage pre-push
```

To fix formatting, run `python -m black .`, review the changes, and stage them.
Hooks install their tools in isolated environments on first setup, which requires
network access. Subsequent runs reuse those environments and do not require an
activated virtual environment. Install the hooks again if you recreate `.venv`.
GitHub Actions remains the final check; hooks use your local Python version,
while CI uses Python 3.12.
