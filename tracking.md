# Simple Invoicing: Progress Tracking

Tracks progress against [PLAN.md](PLAN.md). Updated at each stage commit.

## Stages

| Stage | Description | Status | Commit |
|---|---|---|---|
| 0 | Project setup: `.gitignore` and `PLAN.md` | ✅ Done | `5bec93c` |
| 1 | Minimal working app, database setup, Windows launcher | ✅ Done | `4c069fe` |
| 2 | Create an invoice with lines and calculations | ✅ Done | `8ef0293` |
| 3 | Numbering tests and the invoice list | ✅ Done | `f23a025` |
| 4 | Validation | ✅ Done | `99424cf` |
| 5 | Due date and persistence check | ✅ Done | `65ebbdb` |
| 6 | Money formatting | ✅ Done | this commit |
| 7 | Duplicate an invoice | ⬜ Not started | |

## Bronze requirements

| # | Requirement | Status | Notes |
|---|---|---|---|
| B1 | Create an invoice with client, date and lines | ✅ Done | Stage 2. Form with 10 line rows |
| B2 | Line amounts and invoice total calculated | ✅ Done | Stage 2. `Decimal`, `ROUND_HALF_UP`, each line rounded then summed |
| B3 | Next invoice number assigned automatically | ✅ Done | Built in Stage 2, tested in Stage 3. Numbering continues correctly after a restart |
| B4 | Invoice list, newest first | ✅ Done | Stage 3. Home page lists invoices by number, highest first, each linking to the invoice |
| B5 | Refuse invalid lines with a clear message | ✅ Done | Stage 4. Missing description, negative, missing or invalid quantity or price, and missing date are refused. Every problem is listed, naming the line, and nothing is saved |
| B6 | Invoices persist after restarting the app | ✅ Done | Saved in SQLite since Stage 2. Restart confirmed in Stage 5 |
| B7 | Due date, 15 days after the invoice date unless changed | ✅ Done | Stage 5. Optional due date field; left blank it is the invoice date + 15 days. Shown on the invoice page |
| B8 | Amounts shown as `1.250,00 KM` | ✅ Done | Stage 6. One shared function formats every amount; calculations and stored cents unchanged |
| B9 | Duplicate an invoice | ⬜ Not started | Stage 7 |

## Stage 2 browser test results

All passed and were confirmed by the user:

- Three lines (2 × 100, 1.5 × 40, 3 × 12.50) → 200.00, 60.00, 37.50; total 297.50.
- Rounding half up (1.5 × 0.25 → 0.38, 0.5 × 0.05 → 0.03), and a completely empty row was ignored.
- All rows empty → "Please enter at least one line.", nothing saved.
- Invoice 1 unchanged after reloading the page.

## Stage 3 browser test results

All passed and were confirmed by the user:

- Existing invoices appear in descending numerical order.
- Invoices 3 and 4 received consecutive numbers and correct totals.
- After restarting the app, Invoice 5 received the correct next number.
- The list shows the correct clients, dates, totals and order.
- Clicking an invoice number opens the correct invoice.

## Stage 4 test results

Automated: 16 checks run with Flask's test client against a temporary database, all passed. They cover each refusal case, several errors at once, typed values kept, rejected invoices not saved, an empty row between filled rows, zero values, and the Stage 2 total of 297.50.

Browser tests, confirmed passed by the user:

- Missing description (quantity 2, price 10) → "Line 1: please enter a description.", nothing saved.
- Quantity −1 → "Line 1: the quantity cannot be negative."
- Price −5 → "Line 1: the price cannot be negative."
- Quantity `abc` → "Line 1: the quantity must be a number with at most two decimals."
- Errors on lines 2 and 3 at once → all three messages shown together.
- Valid invoice with an empty row between two filled rows → saved with the next number, total 260.00.

## Stage 5 test results

Automated: 26 checks, all passed. The 16 Stage 4 checks still pass. The 10 new checks cover the blank default (01.10.2026 → 16.10.2026), a changed due date (30.10.2026), the default across a year end (20.12.2026 → 04.01.2027), an invalid due date refused, a restart simulated by reopening the database in a new process, and all existing invoices displaying with a due date (run on a copy of the database).

Browser tests, confirmed passed by the user:

- Invoice dated 01.10.2026 with the due date blank → due date 16.10.2026.
- Invoice dated 01.10.2026 with due date 30.10.2026 entered → 30.10.2026 saved and shown.
- Both invoices still there after closing and restarting the app.

## Stage 6 test results

Automated: 40 checks, all passed. The Stage 4 and Stage 5 checks still pass (three Stage 4 checks updated to expect the new format, e.g. `297,50 KM`). The 14 new checks cover the format itself (`1.250,00 KM`, `0,50 KM`, `1.000.000,00 KM`, `0,00 KM` and others), price 1250 on the invoice page and list, half-up rounding shown as `0,38 KM`, stored cents unchanged, and all existing invoices showing formatted totals (run on a copy of the database).

Browser test, confirmed passed by the user:

- Price 1250 → amounts shown as `1.250,00 KM`.

## Known limitations

- No upper limit on amounts; absurdly large values (around 17+ digits) can fail when saving. Not required by the plan.
- The client name may be left empty. Not required by the plan.
- A due date earlier than the invoice date is accepted. Not required by the plan.
- Quantities are shown with a dot for decimals (e.g. `1.5`); the KM format applies to amounts only.
- Typed amounts with thousands separators (e.g. `1.250,00`) are refused; enter `1250` instead.
