# Simple Invoicing: Progress Tracking

Tracks progress against [PLAN.md](PLAN.md). Updated at each stage commit.

## Stages

| Stage | Description | Status | Commit |
|---|---|---|---|
| 0 | Project setup: `.gitignore` and `PLAN.md` | ✅ Done | `5bec93c` |
| 1 | Minimal working app, database setup, Windows launcher | ✅ Done | `4c069fe` |
| 2 | Create an invoice with lines and calculations | ✅ Done | `8ef0293` |
| 3 | Numbering tests and the invoice list | ✅ Done | this commit |
| 4 | Validation | ⬜ Not started | |
| 5 | Due date and persistence check | ⬜ Not started | |
| 6 | Money formatting | ⬜ Not started | |
| 7 | Duplicate an invoice | ⬜ Not started | |

## Bronze requirements

| # | Requirement | Status | Notes |
|---|---|---|---|
| B1 | Create an invoice with client, date and lines | ✅ Done | Stage 2. Form with 10 line rows |
| B2 | Line amounts and invoice total calculated | ✅ Done | Stage 2. `Decimal`, `ROUND_HALF_UP`, each line rounded then summed |
| B3 | Next invoice number assigned automatically | ✅ Done | Built in Stage 2, tested in Stage 3. Numbering continues correctly after a restart |
| B4 | Invoice list, newest first | ✅ Done | Stage 3. Home page lists invoices by number, highest first, each linking to the invoice |
| B5 | Refuse invalid lines with a clear message | 🟡 Partial | Stage 2 refuses non-numeric values, more than two decimals and a missing date. Negative values and missing descriptions come in Stage 4 |
| B6 | Invoices persist after restarting the app | 🟡 Partial | Saved in SQLite. Restart test in Stage 5 |
| B7 | Due date, 15 days after the invoice date unless changed | 🟡 Partial | The default is saved but not shown yet. Field and display in Stage 5 |
| B8 | Amounts shown as `1.250,00 KM` | ⬜ Not started | Stage 6. Amounts currently show as `1250.00` |
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
