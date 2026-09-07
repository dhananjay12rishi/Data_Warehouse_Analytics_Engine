"""
dashboard.py
------------
Simple interactive dashboard for the Olist warehouse.

Run: streamlit run dashboard.py
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Olist Analytics Dashboard", layout="wide")
conn = sqlite3.connect("data/warehouse.db", check_same_thread=False)

st.title("Olist E-Commerce Analytics Dashboard")

# ---- one simple filter ----
states = pd.read_sql("SELECT DISTINCT customer_state FROM customers ORDER BY customer_state", conn)["customer_state"].tolist()
selected_state = st.selectbox("Filter by customer state", ["All"] + states)

where = "o.order_status = 'delivered'"
if selected_state != "All":
    where += f" AND c.customer_state = '{selected_state}'"

data = pd.read_sql(f"""
    SELECT o.order_id, oi.price, r.review_score
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    LEFT JOIN order_reviews r ON r.order_id = o.order_id
    WHERE {where}
""", conn)

# ---- KPIs ----
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"R$ {data['price'].sum():,.0f}")
col2.metric("Total Orders", f"{data['order_id'].nunique():,}")
col3.metric("Avg Review Score", f"{data['review_score'].mean():.2f} / 5")

st.markdown("---")

# ---- charts ----
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 categories by revenue")
    categories = pd.read_sql(f"""
        SELECT ct.product_category_name_english AS category, SUM(oi.price) AS revenue
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        JOIN category_translation ct ON ct.product_category_name = p.product_category_name
        JOIN orders o ON o.order_id = oi.order_id
        JOIN customers c ON c.customer_id = o.customer_id
        WHERE {where}
        GROUP BY category ORDER BY revenue DESC LIMIT 10
    """, conn)
    fig, ax = plt.subplots()
    ax.barh(categories["category"][::-1], categories["revenue"][::-1])
    st.pyplot(fig)

with col2:
    st.subheader("Review score distribution")
    fig, ax = plt.subplots()
    data["review_score"].value_counts().sort_index().plot(kind="bar", ax=ax, color="steelblue")
    st.pyplot(fig)
