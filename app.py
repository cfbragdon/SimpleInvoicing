"""Simple Invoicing: a local invoicing app for Assignment 4 (BILD-AI)."""

import sqlite3
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

HOST = "127.0.0.1"
PORT = 5880
DATABASE = Path(__file__).parent / "invoices.db"

LINE_ROWS = 10
DUE_DAYS = 15
CENT = Decimal("0.01")

# Amounts are stored as whole cents and quantities as hundredths.
SCHEMA = """
CREATE TABLE IF NOT EXISTS invoices (
    id           INTEGER PRIMARY KEY,
    number       INTEGER NOT NULL UNIQUE,
    client_name  TEXT    NOT NULL,
    invoice_date TEXT    NOT NULL,
    due_date     TEXT    NOT NULL,
    total_cents  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS invoice_lines (
    id                  INTEGER PRIMARY KEY,
    invoice_id          INTEGER NOT NULL REFERENCES invoices (id),
    position            INTEGER NOT NULL,
    description         TEXT    NOT NULL,
    quantity_hundredths INTEGER NOT NULL,
    unit_price_cents    INTEGER NOT NULL,
    amount_cents        INTEGER NOT NULL
);
"""

app = Flask(__name__)


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.executescript(SCHEMA)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def parse_amount(text):
    """Turn typed text into a Decimal with at most two decimals, or None."""
    try:
        value = Decimal(text.strip().replace(",", "."))
        if not value.is_finite() or value != value.quantize(CENT):
            return None
    except InvalidOperation:  # also raised by quantize for huge values such as 1e30
        return None
    return value


def check_amount(position, label, text):
    """Return (value, error) for a quantity or price typed on a line."""
    if not text:
        return None, f"Line {position}: please enter a {label}."
    value = parse_amount(text)
    if value is None:
        return None, f"Line {position}: the {label} must be a number with at most two decimals."
    if value < 0:
        return None, f"Line {position}: the {label} cannot be negative."
    return value, None


def line_amount(quantity, price):
    """Quantity x price, rounded half up to two decimals."""
    return (quantity * price).quantize(CENT, rounding=ROUND_HALF_UP)


@app.template_filter("money")
def format_money(cents):
    return f"{Decimal(cents) / 100:.2f}"


@app.template_filter("quantity")
def format_quantity(hundredths):
    return f"{Decimal(hundredths) / 100:f}"


@app.template_filter("date")
def format_date(iso_text):
    return date.fromisoformat(iso_text).strftime("%d.%m.%Y")


@app.route("/")
def index():
    conn = get_db()
    try:
        # Newest first: the highest number is the most recently created invoice.
        invoices = conn.execute(
            "SELECT number, client_name, invoice_date, total_cents"
            " FROM invoices ORDER BY number DESC"
        ).fetchall()
    finally:
        conn.close()
    return render_template("index.html", invoices=invoices)


@app.route("/invoices/new", methods=["GET", "POST"])
def new_invoice():
    if request.method == "GET":
        form = {"client_name": "", "invoice_date": date.today().isoformat(), "due_date": ""}
        rows = [{"description": "", "quantity": "", "price": ""}] * LINE_ROWS
        return render_template("new_invoice.html", form=form, rows=rows, errors=[])

    form = {
        "client_name": request.form.get("client_name", "").strip(),
        "invoice_date": request.form.get("invoice_date", "").strip(),
        "due_date": request.form.get("due_date", "").strip(),
    }
    rows = [
        {
            "description": request.form.get(f"description_{i}", "").strip(),
            "quantity": request.form.get(f"quantity_{i}", "").strip(),
            "price": request.form.get(f"price_{i}", "").strip(),
        }
        for i in range(LINE_ROWS)
    ]

    # Every problem is collected so they can all be fixed in one go.
    errors = []
    try:
        invoice_date = date.fromisoformat(form["invoice_date"])
    except ValueError:
        errors.append("Please enter the invoice date.")
    else:
        # Left blank, the due date is 15 days after the invoice date.
        if not form["due_date"]:
            due_date = invoice_date + timedelta(days=DUE_DAYS)
        else:
            try:
                due_date = date.fromisoformat(form["due_date"])
            except ValueError:
                errors.append("Please enter a valid due date, or leave it blank.")

    lines = []
    for position, row in enumerate(rows, start=1):
        if not (row["description"] or row["quantity"] or row["price"]):
            continue  # completely empty rows are ignored
        line_errors = []
        if not row["description"]:
            line_errors.append(f"Line {position}: please enter a description.")
        quantity, error = check_amount(position, "quantity", row["quantity"])
        if error:
            line_errors.append(error)
        price, error = check_amount(position, "price", row["price"])
        if error:
            line_errors.append(error)
        if line_errors:
            errors.extend(line_errors)
        else:
            lines.append((row["description"], quantity, price, line_amount(quantity, price)))

    if not errors and not lines:
        errors.append("Please enter at least one line.")

    if errors:
        return render_template("new_invoice.html", form=form, rows=rows, errors=errors)

    total = sum(amount for _, _, _, amount in lines)

    conn = get_db()
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")  # lock so two saves cannot take the same number
            number = conn.execute(
                "SELECT COALESCE(MAX(number), 0) + 1 FROM invoices"
            ).fetchone()[0]
            invoice_id = conn.execute(
                "INSERT INTO invoices (number, client_name, invoice_date, due_date, total_cents)"
                " VALUES (?, ?, ?, ?, ?)",
                (number, form["client_name"], invoice_date.isoformat(),
                 due_date.isoformat(), int(total * 100)),
            ).lastrowid
            conn.executemany(
                "INSERT INTO invoice_lines (invoice_id, position, description,"
                " quantity_hundredths, unit_price_cents, amount_cents)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (invoice_id, position, description, int(quantity * 100),
                     int(price * 100), int(amount * 100))
                    for position, (description, quantity, price, amount)
                    in enumerate(lines, start=1)
                ],
            )
    finally:
        conn.close()

    return redirect(url_for("show_invoice", number=number))


@app.route("/invoices/<int:number>")
def show_invoice(number):
    conn = get_db()
    try:
        invoice = conn.execute(
            "SELECT * FROM invoices WHERE number = ?", (number,)
        ).fetchone()
        if invoice is None:
            abort(404)
        lines = conn.execute(
            "SELECT * FROM invoice_lines WHERE invoice_id = ? ORDER BY position",
            (invoice["id"],),
        ).fetchall()
    finally:
        conn.close()
    return render_template("invoice.html", invoice=invoice, lines=lines)


if __name__ == "__main__":
    init_db()
    app.run(host=HOST, port=PORT)
