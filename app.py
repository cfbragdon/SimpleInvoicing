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
    except InvalidOperation:
        return None
    if not value.is_finite() or value != value.quantize(CENT):
        return None
    return value


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
    return render_template("index.html")


@app.route("/invoices/new", methods=["GET", "POST"])
def new_invoice():
    if request.method == "GET":
        form = {"client_name": "", "invoice_date": date.today().isoformat()}
        rows = [{"description": "", "quantity": "", "price": ""}] * LINE_ROWS
        return render_template("new_invoice.html", form=form, rows=rows, error=None)

    form = {
        "client_name": request.form.get("client_name", "").strip(),
        "invoice_date": request.form.get("invoice_date", "").strip(),
    }
    rows = [
        {
            "description": request.form.get(f"description_{i}", "").strip(),
            "quantity": request.form.get(f"quantity_{i}", "").strip(),
            "price": request.form.get(f"price_{i}", "").strip(),
        }
        for i in range(LINE_ROWS)
    ]

    error = None
    lines = []
    for position, row in enumerate(rows, start=1):
        if not (row["description"] or row["quantity"] or row["price"]):
            continue  # completely empty rows are ignored
        quantity = parse_amount(row["quantity"])
        price = parse_amount(row["price"])
        if quantity is None or price is None:
            error = f"Line {position}: quantity and price must be numbers with at most two decimals."
            break
        lines.append((row["description"], quantity, price, line_amount(quantity, price)))

    if error is None and not lines:
        error = "Please enter at least one line."

    if error is None:
        try:
            invoice_date = date.fromisoformat(form["invoice_date"])
        except ValueError:
            error = "Please enter the invoice date."

    if error:
        return render_template("new_invoice.html", form=form, rows=rows, error=error)

    total = sum(amount for _, _, _, amount in lines)
    # The due date field arrives in Stage 5; until then it is the default.
    due_date = invoice_date + timedelta(days=DUE_DAYS)

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
