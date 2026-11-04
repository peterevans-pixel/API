from decimal import Decimal
from pprint import pprint
from database import get_products, get_customers, get_orders

if __name__ == "__main__":
    print("1. What products do we sell?")
    pprint(get_products())
    print("2. Which products cost $25 or less?")
    pprint(get_products(max_price=25))
    print("3. Which customers live in Fairfield?")
    pprint(get_customers(city="Fairfield"))
    print("4. Who bought what? (First five orders)")
    orders = get_orders()
    pprint(orders[:5])
    revenue = sum((Decimal(str(o["unit_price"])) * o["quantity"] for o in orders), Decimal("0"))
    print(f"5. Revenue across the returned {len(orders)} orders: ${revenue:,.2f}")
