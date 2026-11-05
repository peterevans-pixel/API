"""Reusable API functions for local classroom scripts and a future backend.
Every .execute() sends an HTTP request; this is not a direct PostgreSQL connection.
"""
from datetime import date
from decimal import Decimal
from functools import lru_cache
from supabase import create_client
from config import get_settings


@lru_cache(maxsize=1)
def get_client():
    url, key = get_settings()
    return create_client(url, key)


def get_products(max_price=None):
    query = get_client().table("products").select("*")
    if max_price is not None:
        query = query.lte("price", float(max_price))
    return query.order("product_id").execute().data


def get_customers(city=None):
    query = get_client().table("customers").select("*")
    if city:
        query = query.eq("city", city)
    return query.order("customer_id").execute().data


def add_customer(name, email, city):
    if not all(value.strip() for value in (name, email, city)):
        raise ValueError("Name, email, and city are required.")
    response = get_client().table("customers").insert({
        "name": name.strip(), "email": email.strip().lower(), "city": city.strip()
    }).execute()
    return response.data[0]


def update_product_price(product_id, price):
    price = Decimal(str(price))
    if not price.is_finite() or price < 0 or price != price.quantize(Decimal("0.01")):
        raise ValueError("Use a nonnegative price with at most two decimal places.")
    response = (get_client().table("products").update({"price": str(price)})
                .eq("product_id", int(product_id)).execute())
    if not response.data:
        raise ValueError("Product not found.")
    return response.data[0]



def create_order(customer_id, product_id, quantity, expected_price):
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")

    customers = (
        get_client().table("customers")
        .select("customer_id")
        .eq("customer_id", int(customer_id))
        .execute().data
    )
    if not customers:
        raise ValueError("Customer not found.")

    products = (
        get_client().table("products")
        .select("price")
        .eq("product_id", int(product_id))
        .execute().data
    )
    if not products:
        raise ValueError("Product not found.")

    current_price = Decimal(str(products[0]["price"]))
    if current_price != Decimal(str(expected_price)):
        raise ValueError(
            "The product price changed. Review the new price "
            "and confirm the order again."
        )

    response = get_client().table("orders").insert({
        "customer_id": int(customer_id),
        "product_id": int(product_id),
        "quantity": quantity,
        "order_date": date.today().isoformat(),
        "unit_price": str(current_price)
    }).execute()

    if not response.data:
        raise RuntimeError(
            "Order insertion may have succeeded, but no record was returned. "
            "Check order history before retrying."
        )

    return response.data[0]



def get_order(order_id):
    orders = (get_client().table("orders")
              .select("*, customers(name), products(product_name)")
              .eq("order_id", int(order_id)).execute().data)
    return orders[0] if orders else None


def get_orders():
    # Foreign keys let the API embed the related records in one response.
    return (get_client().table("orders")
            .select("*, customers(name, city), products(product_name)")
            .order("order_id").execute().data)


def delete_order(order_id):
    return (get_client().table("orders").delete()
            .eq("order_id", int(order_id)).execute().data)
