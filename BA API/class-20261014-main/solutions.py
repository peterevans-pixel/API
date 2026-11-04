"""Worked answers: review after trying exercises.py."""
from decimal import Decimal
from pprint import pprint
from database import get_client, get_products, get_customers, get_orders


def exercise_1():
    return get_products(max_price=20)


def exercise_2():
    return get_customers(city="Stamford")


def exercise_3():
    return (get_client().table("orders").select("*")
            .gte("quantity", 3).order("order_id").execute().data)


def exercise_4():
    totals = {}
    for order in get_orders():
        name = order["products"]["product_name"]
        amount = Decimal(str(order["unit_price"])) * order["quantity"]
        totals[name] = totals.get(name, Decimal("0")) + amount
    return totals


if __name__ == "__main__":
    for exercise in (exercise_1, exercise_2, exercise_3, exercise_4):
        print(exercise.__name__)
        pprint(exercise())
