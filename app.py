"""Simple Invoicing: a local invoicing app for Assignment 4 (BILD-AI)."""

import sqlite3
from pathlib import Path

from flask import Flask, render_template

HOST = "127.0.0.1"
PORT = 5880
DATABASE = Path(__file__).parent / "invoices.db"

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


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    init_db()
    app.run(host=HOST, port=PORT)
