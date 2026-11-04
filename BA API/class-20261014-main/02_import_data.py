"""Validate all CSV files before uploading. Run with --check-only to work offline."""
import argparse
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).with_name("data")
FIELDS = {
    "customers": ["customer_id", "name", "email", "city"],
    "products": ["product_id", "product_name", "category", "price"],
    "orders": ["order_id", "customer_id", "product_id", "quantity", "order_date", "unit_price"],
}


def load_data():
    tables = {}
    for table, fields in FIELDS.items():
        with (DATA / f"{table}.csv").open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != fields:
                raise ValueError(f"Unexpected columns in {table}.csv")
            rows = list(reader)
        for row in rows:
            if any(value is None or not value.strip() for value in row.values()):
                raise ValueError(f"Missing value in {table}.csv")
            for field in fields:
                if field.endswith("_id") or field == "quantity":
                    row[field] = int(row[field])
                elif field in ("price", "unit_price"):
                    amount = Decimal(row[field])
                    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal("0.01")):
                        raise ValueError("Invalid price")
                    row[field] = str(amount)  # JSON-compatible; exact decimal text
            if table == "orders":
                date.fromisoformat(row["order_date"])
                if row["quantity"] <= 0:
                    raise ValueError("Quantity must be positive")
        primary_key = fields[0]
        ids = [row[primary_key] for row in rows]
        if len(ids) != len(set(ids)) or any(not 0 < i < 1000 for i in ids):
            raise ValueError(f"Seed IDs must be unique and between 1 and 999: {table}")
        tables[table] = rows
    emails = [r["email"] for r in tables["customers"]]
    if len(emails) != len(set(emails)):
        raise ValueError("Duplicate customer email")
    customers = {r["customer_id"] for r in tables["customers"]}
    products = {r["product_id"] for r in tables["products"]}
    for order in tables["orders"]:
        if order["customer_id"] not in customers or order["product_id"] not in products:
            raise ValueError("An order references a missing customer or product")
    return tables


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    tables = load_data()
    for name, rows in tables.items():
        print(f"Validated {name}: {len(rows)} records")
    if args.check_only:
        return
    from database import get_client
    for table, rows in tables.items():
        # Parents first, then orders. Upsert makes repeated seed loads predictable.
        get_client().table(table).upsert(rows, on_conflict=FIELDS[table][0]).execute()
        print(f"Uploaded {table}: {len(rows)} records")
    print("Done. Re-running restores seed rows; it does not delete additional rows.")


if __name__ == "__main__":
    main()
