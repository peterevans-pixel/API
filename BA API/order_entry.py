"""Display the customer and product catalogs from Supabase."""
from pathlib import Path
from decimal import Decimal
import sys

project_dir = Path(__file__).resolve().parent
if not (project_dir / "database.py").is_file():
    extracted_project = project_dir / "class-20261014-main"
    if (extracted_project / "database.py").is_file():
        sys.path.insert(0, str(extracted_project))

import httpx
from postgrest.exceptions import APIError

from database import create_order, get_customers, get_order, get_products


def display_table(title, headers, rows):
    """Print rows as a simple, readable ASCII table."""
    rows = list(rows)
    widths = [
        max([len(header), *(len(str(row[index])) for row in rows)])
        for index, header in enumerate(headers)
    ]
    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    print(title)
    print(separator)
    print("| " + " | ".join(
        header.ljust(width) for header, width in zip(headers, widths)
    ) + " |")
    print(separator)
    for row in rows:
        print("| " + " | ".join(
            str(value).ljust(width) for value, width in zip(row, widths)
        ) + " |")
    print(separator)


def prompt_existing_id(entity, records):
    valid_ids = {record[f"{entity.lower()}_id"] for record in records}
    while True:
        value = input(f"Enter an existing {entity.lower()} ID: ").strip()
        try:
            record_id = int(value)
        except ValueError:
            print(f"Please enter a whole-number {entity.lower()} ID.")
            continue
        if record_id not in valid_ids:
            print(f"No {entity.lower()} with ID {record_id} exists. Try again.")
            continue
        return record_id


def prompt_quantity():
    while True:
        value = input("Enter quantity to purchase: ").strip()
        try:
            quantity = int(value)
        except ValueError:
            print("Please enter a positive whole number for quantity.")
            continue
        if quantity <= 0:
            print("Quantity must be greater than zero. Try again.")
            continue
        return quantity


def prompt_confirmation():
    while True:
        response = input("Confirm purchase? (Y/N): ").strip().upper()
        if response in ("Y", "N"):
            return response
        print("Please enter Y to confirm or N to cancel.")


def main():
    customers = get_customers()
    products = get_products()

    display_table(
        "Customers",
        ("Customer ID", "Customer Name"),
        ((customer["customer_id"], customer["name"]) for customer in customers),
    )
    print()
    display_table(
        "Products",
        ("Product ID", "Product Name", "Current Price"),
        (
            (product["product_id"], product["product_name"], f"${float(product['price']):.2f}")
            for product in products
        ),
    )

    if not customers:
        print("No customers are available to select.")
        return
    if not products:
        print("No products are available to select.")
        return

    customer_id = prompt_existing_id("Customer", customers)
    product_id = prompt_existing_id("Product", products)
    quantity = prompt_quantity()
    customer = next(c for c in customers if c["customer_id"] == customer_id)
    product = next(p for p in products if p["product_id"] == product_id)
    unit_price = Decimal(str(product["price"]))
    total = unit_price * quantity

    print("\nOrder summary")
    print(f"Customer: {customer['name']}")
    print(f"Product: {product['product_name']}")
    print(f"Quantity: {quantity}")
    print(f"Current unit price: ${unit_price:.2f}")
    print(f"Order total: ${total:.2f}")

    if prompt_confirmation() == "N":
        print("Order canceled. No order was submitted.")
        return

    try:
        saved_order = create_order(customer_id, product_id, quantity)
    except (APIError, httpx.HTTPError, RuntimeError, ValueError):
        print(
            "Unable to confirm that the order was saved. Check your connection, "
            "Supabase settings, and table permissions."
        )
        return

    order_id = saved_order.get("order_id")
    if order_id is None:
        print("The order was submitted, but verification could not be completed: "
              "Supabase did not return an order ID.")
        return

    try:
        verified_order = get_order(order_id)
    except (APIError, httpx.HTTPError, RuntimeError, ValueError):
        print("The order was submitted, but verification could not be completed "
              "because the follow-up database query failed.")
        return
    if verified_order is None:
        print("The order was submitted, but verification could not be completed: "
              "no matching order was found.")
        return

    stored_price = Decimal(str(verified_order["unit_price"]))
    verified_total = stored_price * verified_order["quantity"]
    display_table(
        "Verified saved order",
        ("Order ID", "Customer", "Product", "Quantity", "Unit Price", "Total", "Order Date"),
        ((
            verified_order["order_id"],
            verified_order["customers"]["name"],
            verified_order["products"]["product_name"],
            verified_order["quantity"],
            f"${stored_price:.2f}",
            f"${verified_total:.2f}",
            verified_order["order_date"],
        ),),
    )
    print("Order saved and verified successfully.")


if __name__ == "__main__":
    main()
