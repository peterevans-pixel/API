"""Complete each TODO using database.py or the Supabase client."""
from database import get_client, get_products, get_customers, get_orders


def exercise_1():
    # Return products costing $20 or less.
    raise NotImplementedError("Complete exercise 1")


def exercise_2():
    # Return customers who live in Stamford.
    raise NotImplementedError("Complete exercise 2")


def exercise_3():
    # Return orders with quantity >= 3, ordered by order_id.
    raise NotImplementedError("Complete exercise 3")


def exercise_4():
    # Calculate revenue per product using quantity * unit_price.
    # Return a dictionary: product name -> Decimal total.
    raise NotImplementedError("Complete exercise 4")


if __name__ == "__main__":
    from pprint import pprint
    for exercise in (exercise_1, exercise_2, exercise_3, exercise_4):
        print(exercise.__name__)
        try:
            pprint(exercise())
        except NotImplementedError as error:
            print(error)
