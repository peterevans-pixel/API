
import streamlit as st
import pandas as pd
from decimal import Decimal
from database import (
    get_customers, get_products, get_orders,
    get_order, create_order
)

st.set_page_config(page_title="Order Entry App", layout="wide")
st.title("Customer Order Entry")
st.write("Select a customer and product to create an order using Supabase.")

# Require access before any database calls
def check_password():
    if st.session_state.get("authenticated"):
        return True

    password = st.text_input("App Password", type="password")
    if st.button("Log In"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False

if not check_password():
    st.stop()

# Initialize state
if "confirmed_order" not in st.session_state:
    st.session_state.confirmed_order = None
if "verified_order" not in st.session_state:
    st.session_state.verified_order = None
if "save_notice" not in st.session_state:
    st.session_state.save_notice = None

@st.cache_data(ttl=60)
def load_data():
    return get_customers(), get_products(), get_orders()

if st.button("Refresh Data"):
    load_data.clear()
    st.rerun()

try:
    customers, products, orders = load_data()
except Exception:
    st.error("Could not connect to Supabase. Check your configuration.")
    st.stop()

st.header("Customers")
st.dataframe(
    pd.DataFrame(customers)[["customer_id", "name"]],
    hide_index=True,
    use_container_width=True
)

st.header("Products")
st.dataframe(
    pd.DataFrame(products)[
        ["product_id", "product_name", "category", "price"]
    ].assign(price=lambda df: df["price"].map(
        lambda x: f"${Decimal(str(x)):,.2f}"
    )),
    hide_index=True,
    use_container_width=True
)

st.header("Create an Order")

customer_map = {c["customer_id"]: c["name"] for c in customers}
product_map = {p["product_id"]: p["product_name"] for p in products}

if not customers or not products:
    st.warning("Customers and products must exist before creating orders.")
    st.stop()

customer_id = st.selectbox(
    "Select Customer",
    list(customer_map),
    format_func=lambda x: customer_map[x]
)
product_id = st.selectbox(
    "Select Product",
    list(product_map),
    format_func=lambda x: product_map[x]
)
quantity = st.number_input("Quantity", min_value=1, step=1, value=1)

product = next(p for p in products if p["product_id"] == product_id)
unit_price = Decimal(str(product["price"]))
total = unit_price * quantity

st.subheader("Order Review")
st.write(f"Customer: {customer_map[customer_id]}")
st.write(f"Product: {product_map[product_id]}")
st.write(f"Quantity: {quantity}")
st.write(f"Unit Price: ${unit_price:,.2f}")
st.write(f"Total: ${total:,.2f}")

confirmed = st.checkbox("I confirm this order.")

if st.button("Submit Order"):
    if not confirmed:
        st.warning("Please confirm the order before submitting.")
    else:
        try:
            # Recheck the current price before saving
            fresh_products = get_products()
            fresh_product = next(
                (p for p in fresh_products
                 if p["product_id"] == product_id), None
            )

            if fresh_product is None:
                st.error("This product is no longer available.")
            elif Decimal(str(fresh_product["price"])) != unit_price:
                st.warning(
                    "The product price changed. "
                    "Refresh the data and confirm the updated order."
                )
            else:
                saved = create_order(
                    customer_id, product_id, int(quantity), unit_price
                )
                st.session_state.save_notice = saved["order_id"]

                # New API request to verify saved order
                st.session_state.verified_order = get_order(
                    saved["order_id"]
                )
                load_data.clear()
                st.rerun()
        except Exception:
            st.error(
                "The order could not be completed or verified. "
                "Check Supabase before trying again."
            )

if st.session_state.save_notice is not None:
    st.success(
        f"Order #{st.session_state.save_notice} was saved."
    )
    verified = st.session_state.verified_order

    if verified:
        st.subheader("Verified Saved Order")
        stored_price = Decimal(str(verified["unit_price"]))
        stored_total = stored_price * verified["quantity"]

        st.dataframe(pd.DataFrame([{
            "Order ID": verified["order_id"],
            "Customer": verified["customers"]["name"],
            "Product": verified["products"]["product_name"],
            "Quantity": verified["quantity"],
            "Unit Price": f"${stored_price:,.2f}",
            "Total": f"${stored_total:,.2f}",
            "Order Date": verified["order_date"]
        }]), hide_index=True, use_container_width=True)
    else:
        st.warning("Order saved, but verification was unsuccessful.")

st.header("Order History")

history_rows = []
for order in orders:
    price = Decimal(str(order["unit_price"]))
    history_rows.append({
        "Order ID": order["order_id"],
        "Customer": order["customers"]["name"],
        "Product": order["products"]["product_name"],
        "Quantity": order["quantity"],
        "Unit Price": f"${price:,.2f}",
        "Total": f"${price * order['quantity']:,.2f}",
        "Order Date": order["order_date"]
    })

# Extra credit: customer filter
filter_customer = st.selectbox(
    "Filter Orders by Customer",
    ["All Customers"] + list(customer_map.values())
)

if filter_customer != "All Customers":
    history_rows = [
        row for row in history_rows
        if row["Customer"] == filter_customer
    ]

st.dataframe(
    pd.DataFrame(history_rows),
    hide_index=True,
    use_container_width=True
)

filtered_total = sum(
    Decimal(row["Total"].replace("$", "").replace(",", ""))
    for row in history_rows
)
st.metric("Total Order Value", f"${filtered_total:,.2f}")
