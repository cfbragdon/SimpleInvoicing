# Simple Invoicing

A simple local invoicing app for Windows, built with Python, Flask and SQLite for Assignment 4 of the BILD-AI training program.

It runs only on your own computer, in your browser, at http://127.0.0.1:5880. There are no user accounts and nothing is hosted online.

## What it does

- Create invoices with a client name, invoice date, due date and up to 10 lines (description, quantity, unit price).
- Calculates each line amount and the invoice total, rounded half up to two decimals.
- Numbers invoices automatically: 1, 2, 3, …
- Lists invoices newest first, with number, client, date and total.
- Refuses invalid input with a clear message, such as a missing description or a negative quantity or price.
- Sets the due date to 15 days after the invoice date unless you enter another one.
- Shows amounts as `1.250,00 KM`.
- Duplicates an invoice with the next number and today's date.

## Setup (once)

You need Python 3.9 or newer. In the project folder, run:

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Launch

Double-click **`Start Invoicing.bat`**. It starts the app with the project's own Python (`.venv\Scripts\python.exe`) and opens http://127.0.0.1:5880 in your browser. If the page does not load at first, refresh it once.

Close the launcher window to stop the app.

## Where the data is stored

Invoices are saved in **`invoices.db`**, a SQLite file in the project folder. It is created automatically the first time the app starts and keeps your invoices between restarts.

`invoices.db` is excluded from Git (see `.gitignore`), so your invoice data is never uploaded to GitHub. To keep a backup, copy this file while the app is stopped.

## More information

- [PLAN.md](PLAN.md): requirements, technical approach and development stages.
- [tracking.md](tracking.md): progress, test results and known limitations.
