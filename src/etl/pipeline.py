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
        amount_val = float(amount)
        if amount_val < 0:
            logging.warning(f"Skipping row with negative amount: {row}")
            continue
        row["amount"] = amount_val
        cleaned.append(row)
    return cleaned


def validate_customer_id_quality(rows, threshold=0.05):
    if not rows:
        return

    missing_count = 0
    for row in rows:
        customer_id = row.get("customer_id")
        if customer_id is None:
            missing_count += 1
            continue
        if isinstance(customer_id, str) and not customer_id.strip():
            missing_count += 1

    missing_ratio = missing_count / len(rows)
    if missing_ratio > threshold:
        message = (
            f"customer_id quality check failed: {missing_count} of {len(rows)} rows "
            f"have missing customer_id values"
        )
        logging.error(message)
        raise ValueError(message)


def total_revenue(rows):
    return sum(row["amount"] for row in rows)


if __name__ == "__main__":
    rows = clean_rows(load_sales("data/raw/sales.csv"))
    logging.info(f"Total revenue: {total_revenue(rows)}")
