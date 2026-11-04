"""Explicit local demonstration. Creates a customer and restores its demo price change."""
from uuid import uuid4
from pprint import pprint
from database import add_customer, get_products, update_product_price, create_order, delete_order

if __name__ == "__main__":
    if input("Modify your classroom database? Type YES: ") != "YES":
        raise SystemExit("No changes made.")
    customer = add_customer("Demo Customer", f"demo-{uuid4().hex}@example.com", "Fairfield")
    print("Inserted customer (retained so you can inspect it):")
    pprint(customer)
    product = get_products()[0]
    try:
        print("Temporarily changing product price to $9.99:")
        pprint(update_product_price(product["product_id"], "9.99"))
        order = create_order(customer["customer_id"], product["product_id"], 2)
        print("Created order with price snapshot:")
        pprint(order)
        print("Deleting only that demonstration order:")
        pprint(delete_order(order["order_id"]))
    finally:
        update_product_price(product["product_id"], product["price"])
        print("Original product price restored.")
