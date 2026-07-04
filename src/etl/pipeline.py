import csv
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def load_sales(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def clean_rows(rows):
    cleaned = []
    for row in rows:
        amount = row.get("amount", "")
        if amount in (None, ""):
            logging.warning(f"Skipping row with missing amount: {row}")
            continue
        row["amount"] = float(amount)
        cleaned.append(row)
    return cleaned


def total_revenue(rows):
    return sum(row["amount"] for row in rows)