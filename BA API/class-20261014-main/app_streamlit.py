"""Optional LOCAL admin demo. Do not publish this unauthenticated write interface."""
import streamlit as st
from database import get_products, get_customers, get_orders, create_order

st.title("Campus Store — Database Demo")
st.caption("Local classroom admin exercise. All records are fictional.")
products = get_products()
customers = get_customers()
st.subheader("Product catalog")
st.dataframe(products, hide_index=True)
if not products or not customers:
    st.info("Run 02_import_data.py first.")
    st.stop()
with st.form("purchase"):
    customer = st.selectbox("Customer", customers, format_func=lambda x: x["name"])
    product = st.selectbox("Product", products, format_func=lambda x: x["product_name"])
    quantity = st.number_input("Quantity", min_value=1, max_value=100, value=1, step=1)
    submit = st.form_submit_button("Record purchase")
if submit:
    try:
        order = create_order(customer["customer_id"], product["product_id"], int(quantity))
        st.success(f"Saved order {order['order_id']} to Supabase.")
    except Exception:
        st.error("Purchase could not be saved. Check your database configuration and connection.")
st.subheader("Orders")
st.dataframe(get_orders(), hide_index=True)
