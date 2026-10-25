# Simple Invoicing: Development Plan

A simple local invoicing app, built for Assignment 4 of the BILD-AI training program.

> **Status:** planning only. No application code exists yet.

---

## 1. Scope

Only the Bronze requirements are built. Nothing beyond Bronze is added unless it is technically necessary.

### 🥉 Bronze requirements (Assignment 4)

| # | Requirement | Acceptance test |
|---|---|---|
| B1 | Create an invoice: client name, date, and lines with description, quantity and price | Create one with three lines |
| B2 | Each line's amount and the invoice total are calculated | Check with a calculator |
| B3 | Each new invoice gets the next number automatically | Create two and compare their numbers |
| B4 | A list of invoices, newest first, with number, client, date and total | Look at the list after creating three |
| B5 | Refuse a line without a description, or with a negative quantity or price | Try each one. A clear message appears |
| B6 | Invoices are still there after closing and reopening the app | Close the app, open it again, and look |
| B7 | A due date on each invoice, 15 days after the invoice date unless changed | Create one and check the date |
| B8 | Amounts shown with two decimals and the currency, e.g. `1.250,00 KM` | Enter a price of 1250 and look at the total |
| B9 | Duplicate an invoice: a copy with the next number and today's date | Duplicate one and compare the two |

---

## 2. Technical approach

- **Stack:** Python + Flask, SQLite database, plain HTML. No JavaScript.
- **Runs locally only:** the server listens on `127.0.0.1` on port `5880`, so only this computer can reach it. No internet hosting, no user accounts.
- **Python environment:** a `.venv` folder inside the project (git-ignored).
- **All checks and calculations happen on the server** when the form is saved.
- **Money calculations** use Python's `Decimal` type with `ROUND_HALF_UP`, never floating-point numbers:
  - line amount = quantity × price, rounded to two decimal places;
  - invoice total = sum of the rounded line amounts.
- **Storage:** amounts are stored as whole cents and quantities as hundredths (integers), so stored values are always exact.
- **Currency:** KM only. All amounts are displayed through one shared formatting function.
- **Dates:** shown as `25.10.2026`.
- **Invoice numbers:** plain numbers `1, 2, 3, …`, starting at 1, unique in the database.
- **Quantity and price:** zero allowed, up to two decimal places, negative refused.

### Data model

- **invoices**: number, client name, invoice date, due date, total.
- **invoice_lines**: invoice, position, description, quantity, unit price, line amount.

---

## 3. Development workflow

Every stage follows the same loop:

1. **Implement** only that stage's features.
2. **Test in the browser** using that stage's acceptance tests, plus a quick check that earlier stages still work.
3. **Review** the change together.
4. **Commit** with the suggested message once all the stage's tests pass. Never commit with failing tests.
5. **Before every commit,** confirm `git status` shows no `.db`, `.venv` or `.env` files.

---

## 4. Stages

### Stage 0: Project setup
- `.gitignore` and `PLAN.md` (this file), reviewed before any code is written.

**Test:** `git status` shows only `.gitignore` and `PLAN.md`.
**Commit:** `Add .gitignore and development plan`

---

### Stage 1: Minimal working app
Only the files needed to launch the app in the browser:
- `app.py`: Flask app on `127.0.0.1:5880`. Creates the database file and its tables on first start.
- `templates/index.html`: the home page.
- `requirements.txt`: Flask.
- `Start Invoicing.bat`: opens the browser and starts the app with the project's own Python, `.venv\Scripts\python.exe`. If that file is missing, it shows a clear message instead.
- One-time setup: create `.venv` and install `requirements.txt` into it.

**Tests:**
- Double-click the launcher: the home page opens in the browser (refresh once if the browser was faster than the app).
- The launcher window shows it is running `.venv\Scripts\python.exe`, not another Python on the computer.
- The database file appears in the project folder, and `git status` does **not** list it.

**Commit:** `Add minimal Flask app, database setup and Windows launcher`

---

### Stage 2: Create an invoice with lines and calculations
**Requirements:** B1, B2
- "New invoice" form: client name, invoice date, and a fixed set of 10 line rows (description, quantity, unit price).
- Completely empty rows are ignored.
- At least one completed line is required. If every row is empty, nothing is saved and the message "Please enter at least one line." appears.
- Line amounts and the total are calculated on save, as described in section 2.
- Basic sequential numbering, needed to save an invoice: each saved invoice gets the next number (1, 2, 3, …), unique in the database.
- Invoice page showing the saved invoice, its number, lines, line amounts and total.

**Tests:**
- Save an invoice: it shows number 1.
- All rows empty → "Please enter at least one line.", nothing saved.
- Three lines: 2 × 100, 1.5 × 40, 3 × 12.50 → line amounts 200.00, 60.00, 37.50; total 297.50. Check with a calculator.
- Rounding half up: 1.5 × 0.25 = 0.375 → 0.38. And 0.5 × 0.05 = 0.025 → 0.03.
- Reload the invoice page: the same numbers appear.

**Commit:** `Create numbered invoices with line items and calculated totals`

---

### Stage 3: Numbering tests and the invoice list
**Requirements:** B3, B4
- Numbering itself was added in Stage 2. This stage confirms it meets B3.
- Invoice list: number, client, date, total, newest first.

**Tests:**
- Create two invoices: the second number is exactly one higher.
- Close and restart the app, create another: numbering continues from the last number, with no repeats.
- Create three: the list shows them newest first, with correct number, client, date and total.

**Commit:** `Add invoice list, newest first`

---

### Stage 4: Validation
**Requirement:** B5
- Refuse, with a clear message naming the line (e.g. "Line 2: please enter a description."):
  - a row that has a quantity or a price but no description;
  - a negative quantity or price;
  - a quantity or price that is missing, not a number, or has more than two decimal places (technically necessary to calculate the line amount);
  - a missing invoice date (technically necessary to calculate the due date).
- Nothing is saved when any check fails, and the form keeps what was typed.

**Tests:**
- Description empty, quantity 2, price 10 → clear message, nothing saved.
- Description empty, price only → clear message, nothing saved.
- Quantity −1 → clear message, nothing saved.
- Price −5 → clear message, nothing saved.
- A completely empty row between filled rows → ignored, invoice saved.
- All rows empty → still refused (rule added in Stage 2).

**Commit:** `Validate invoice lines with clear error messages`

---

### Stage 5: Due date and persistence check
**Requirements:** B6, B7
- Due date field on the form. Left blank: invoice date + 15 days. Filled in: the date entered is used.
- Due date shown on the invoice page.

**Tests:**
- Invoice dated 01.10.2026, due date blank → due date 16.10.2026.
- Invoice dated 01.10.2026, due date 30.10.2026 entered → 30.10.2026 is saved.
- Create invoices, close the launcher window, start it again: all invoices are still there with the same data.

**Commit:** `Add due dates and confirm data persists across restarts`

---

### Stage 6: Money formatting
**Requirement:** B8
- Every amount shown with two decimals and the currency, through one shared formatting function: `1.250,00 KM` (dot for thousands, comma for decimals).

**Tests:**
- Price 1250 → total shown as `1.250,00 KM`.
- 0.5 → `0,50 KM`. 1000000 → `1.000.000,00 KM`.

**Commit:** `Format amounts with two decimals and currency`

---

### Stage 7: Duplicate an invoice
**Requirement:** B9
- "Duplicate" button on the invoice page: copies the client and lines. The copy gets the **next number**, **today's date**, and a due date of today + 15 days.

**Tests:**
- Duplicate an invoice: the copy has the next number and today's date, the lines and total match the original, and the original is unchanged.

**Commit:** `Duplicate invoices with next number and today's date`

**Final check:** run every Bronze test (B1–B9) from section 1 again.

---

## 5. Later (not in scope)

Silver requirements of Assignment 4, kept for reference only. Nothing here is built until requested.

- **S1** Edit an invoice, and delete one after a confirmation question.
- **S2** Mark an invoice as paid or unpaid, and see the total of unpaid invoices.
- **S3** VAT (PDV, 17%): amount without VAT, the VAT, and the total.
- **S4** A client list, to choose a saved client.
- **S5** Filter invoices by month, and export them to CSV.

---

## 6. Decisions (settled)

| ID | Decision | Choice |
|---|---|---|
| D3 | Date format | `25.10.2026` |
| D5 | Invoice number format | Plain numbers starting at 1 |
| D9 | Zero and decimal values | Zero allowed. Up to two decimal places for quantity and price |
| D11 | Python environment location | `.venv` inside the project |
| — | Rounding | `Decimal` with `ROUND_HALF_UP`. Each line rounded to two decimals, then summed |
| — | Empty rows | Completely empty rows ignored. A quantity or price without a description is an error. At least one completed line is required |
| — | Launcher | Always runs `.venv\Scripts\python.exe` |
