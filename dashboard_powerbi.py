"""
Power BI-style interactive dashboard for the Olist Data Warehouse.

Run:
    python -m streamlit run dashboard.py
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

DB_PATH = Path("data/warehouse.db")

st.set_page_config(
    page_title="Olist | Data Warehouse Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 10px;
        padding: 14px 16px;
        background: rgba(128,128,128,.06);
    }
    .dashboard-subtitle {
        color: #6b7280;
        margin-top: -12px;
        margin-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "data/warehouse.db was not found. Run `python etl.py` first."
        )

    conn = sqlite3.connect(DB_PATH)

    orders = pd.read_sql_query(
        """
        SELECT
            o.order_id,
            o.customer_id,
            o.order_status,
            o.order_purchase_timestamp,
            o.order_delivered_customer_date,
            o.order_estimated_delivery_date,
            c.customer_unique_id,
            c.customer_state
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        """,
        conn,
        parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )

    items = pd.read_sql_query(
        """
        SELECT
            oi.order_id,
            oi.product_id,
            oi.seller_id,
            oi.price,
            oi.freight_value,
            p.product_category_name,
            COALESCE(ct.product_category_name_english, 'unknown') AS category
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        LEFT JOIN category_translation ct
          ON ct.product_category_name = p.product_category_name
        """,
        conn,
    )

    payments = pd.read_sql_query(
        """
        SELECT
            order_id,
            GROUP_CONCAT(DISTINCT payment_type) AS payment_type,
            SUM(payment_value) AS payment_value
        FROM order_payments
        GROUP BY order_id
        """,
        conn,
    )

    reviews = pd.read_sql_query(
        """
        SELECT
            order_id,
            AVG(review_score) AS review_score
        FROM order_reviews
        GROUP BY order_id
        """,
        conn,
    )

    conn.close()

    df = (
        items.merge(orders, on="order_id", how="left")
        .merge(payments, on="order_id", how="left")
        .merge(reviews, on="order_id", how="left")
    )

    df["order_date"] = pd.to_datetime(df["order_purchase_timestamp"]).dt.date
    df["month"] = pd.to_datetime(df["order_purchase_timestamp"]).dt.to_period("M").astype(str)

    delivered = df["order_delivered_customer_date"].notna()
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    df["delivery_status"] = "Not delivered"
    df.loc[delivered, "delivery_status"] = "On time"
    df.loc[
        delivered
        & (
            df["order_delivered_customer_date"]
            > df["order_estimated_delivery_date"]
        ),
        "delivery_status",
    ] = "Late"

    return df


def money(value):
    return f"R$ {value:,.0f}"


def pct(value):
    return f"{value:.1f}%"


def apply_filters(df, selected_state, selected_category, selected_status,
                   selected_payment, start_date, end_date):
    mask = (
        (df["order_date"] >= start_date)
        & (df["order_date"] <= end_date)
    )

    if selected_state != "All":
        mask &= df["customer_state"].eq(selected_state)

    if selected_category != "All":
        mask &= df["category"].eq(selected_category)

    if selected_status != "All":
        mask &= df["order_status"].eq(selected_status)

    if selected_payment != "All":
        mask &= df["payment_type"].fillna("").str.contains(
            selected_payment, regex=False
        )

    return df.loc[mask].copy()


def bar_chart(data, x, y, title, horizontal=False):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    if horizontal:
        data = data.sort_values(y)
        ax.barh(data[x].astype(str), data[y])
        ax.set_xlabel(y.replace("_", " ").title())
        ax.set_ylabel("")
    else:
        ax.bar(data[x].astype(str), data[y])
        ax.set_ylabel(y.replace("_", " ").title())
        ax.tick_params(axis="x", rotation=35)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return fig


def line_chart(data, x, y, title):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(data[x].astype(str), data[y], marker="o")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_ylabel(y.replace("_", " ").title())
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    return fig


# ---------- Load ----------
try:
    df = load_data()
except Exception as exc:
    st.error(str(exc))
    st.stop()

# ---------- Header ----------
st.title("📊 Olist E-Commerce Analytics")
st.markdown(
    '<div class="dashboard-subtitle">Data Warehouse & Business Intelligence Dashboard</div>',
    unsafe_allow_html=True,
)

# ---------- Sidebar filters ----------
with st.sidebar:
    st.header("🎛️ Report Filters")

    min_date = df["order_date"].min()
    max_date = df["order_date"].max()

    date_range = st.date_input(
        "Order date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    states = ["All"] + sorted(df["customer_state"].dropna().unique().tolist())
    categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
    statuses = ["All"] + sorted(df["order_status"].dropna().unique().tolist())

    payment_values = sorted(
        {
            value.strip()
            for values in df["payment_type"].dropna()
            for value in str(values).split(",")
            if value.strip()
        }
    )

    selected_state = st.selectbox("Customer state", states)
    selected_category = st.selectbox("Product category", categories)
    selected_status = st.selectbox("Order status", statuses)
    selected_payment = st.selectbox("Payment type", ["All"] + payment_values)

    st.divider()
    st.caption("Filters apply across all dashboard pages.")

filtered = apply_filters(
    df,
    selected_state,
    selected_category,
    selected_status,
    selected_payment,
    start_date,
    end_date,
)

# ---------- Navigation ----------
page = st.radio(
    "Dashboard",
    ["Executive Overview", "Sales & Products", "Customers & Operations"],
    horizontal=True,
    label_visibility="collapsed",
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------- Common metrics ----------
orders_count = filtered["order_id"].nunique()
revenue = filtered["price"].sum()
customers_count = filtered["customer_unique_id"].nunique()
aov = revenue / orders_count if orders_count else 0
avg_review = filtered["review_score"].mean()
delivered_orders = filtered.loc[
    filtered["order_status"].eq("delivered"), "order_id"
].nunique()
total_orders = filtered["order_id"].nunique()
delivery_rate = delivered_orders / total_orders * 100 if total_orders else 0

# ---------- PAGE 1 ----------
if page == "Executive Overview":
    st.subheader("Executive Overview")
    st.caption("A high-level view of sales, customers, satisfaction, and delivery.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Revenue", money(revenue))
    c2.metric("Orders", f"{orders_count:,}")
    c3.metric("Customers", f"{customers_count:,}")
    c4.metric("Avg Order Value", money(aov))
    c5.metric("Avg Review", f"{avg_review:.2f} / 5" if pd.notna(avg_review) else "N/A")

    st.markdown("---")

    monthly = (
        filtered.groupby("month", as_index=False)
        .agg(revenue=("price", "sum"), orders=("order_id", "nunique"))
        .sort_values("month")
    )

    left, right = st.columns(2)
    with left:
        st.pyplot(line_chart(monthly, "month", "revenue", "Monthly Revenue"), use_container_width=True)
    with right:
        st.pyplot(line_chart(monthly, "month", "orders", "Monthly Orders"), use_container_width=True)

    left, right = st.columns(2)

    with left:
        status = (
            filtered.groupby("order_status", as_index=False)
            .agg(orders=("order_id", "nunique"))
            .sort_values("orders", ascending=False)
        )
        st.pyplot(
            bar_chart(status, "order_status", "orders", "Orders by Status"),
            use_container_width=True,
        )

    with right:
        reviews = (
            filtered.dropna(subset=["review_score"])
            .groupby("review_score", as_index=False)
            .agg(orders=("order_id", "nunique"))
        )
        reviews["review_score"] = reviews["review_score"].astype(int)
        st.pyplot(
            bar_chart(reviews, "review_score", "orders", "Review Score Distribution"),
            use_container_width=True,
        )

    st.info(
        f"Delivery success rate: **{pct(delivery_rate)}** of filtered orders are delivered."
    )

# ---------- PAGE 2 ----------
elif page == "Sales & Products":
    st.subheader("Sales & Products")
    st.caption("Understand what generates revenue and how customers pay.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", money(revenue))
    c2.metric("Units Sold", f"{len(filtered):,}")
    c3.metric("Freight Value", money(filtered["freight_value"].sum()))

    st.markdown("---")

    categories_df = (
        filtered.groupby("category", as_index=False)
        .agg(revenue=("price", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        top10 = categories_df.head(10)
        st.pyplot(
            bar_chart(
                top10,
                "category",
                "revenue",
                "Top 10 Categories by Revenue",
                horizontal=True,
            ),
            use_container_width=True,
        )

    with right:
        payment_df = (
            filtered.groupby("payment_type", as_index=False)
            .agg(value=("payment_value", "sum"))
            .sort_values("value", ascending=False)
        )
        st.pyplot(
            bar_chart(payment_df, "payment_type", "value", "Payment Value by Type"),
            use_container_width=True,
        )

    st.markdown("#### Category Performance")

    category_table = categories_df.copy()
    category_table["revenue"] = category_table["revenue"].round(2)
    category_table["avg_order_value"] = (
        category_table["revenue"] / category_table["orders"]
    ).round(2)

    st.dataframe(
        category_table.rename(
            columns={
                "category": "Category",
                "revenue": "Revenue",
                "orders": "Orders",
                "avg_order_value": "Avg Order Value",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# ---------- PAGE 3 ----------
else:
    st.subheader("Customers & Operations")
    st.caption("Customer behavior, geography, sellers, and delivery performance.")

    repeat_base = (
        filtered.groupby("customer_unique_id")
        .agg(order_count=("order_id", "nunique"))
        .reset_index()
    )
    repeat_customers = (repeat_base["order_count"] > 1).sum()
    repeat_rate = (
        repeat_customers / len(repeat_base) * 100 if len(repeat_base) else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unique Customers", f"{customers_count:,}")
    c2.metric("Repeat Customers", f"{repeat_customers:,}")
    c3.metric("Repeat Rate", pct(repeat_rate))
    c4.metric("Avg Delivery Days", f"{filtered['delivery_days'].mean():.1f}")

    st.markdown("---")

    state_df = (
        filtered.groupby("customer_state", as_index=False)
        .agg(revenue=("price", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    delivery_df = (
        filtered.groupby("delivery_status", as_index=False)
        .agg(orders=("order_id", "nunique"))
        .sort_values("orders", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        st.pyplot(
            bar_chart(
                state_df,
                "customer_state",
                "revenue",
                "Top 10 States by Revenue",
                horizontal=True,
            ),
            use_container_width=True,
        )

    with right:
        st.pyplot(
            bar_chart(
                delivery_df,
                "delivery_status",
                "orders",
                "Delivery Performance",
            ),
            use_container_width=True,
        )

    st.markdown("#### Top Sellers")

    seller_df = (
        filtered.groupby("seller_id", as_index=False)
        .agg(
            revenue=("price", "sum"),
            orders=("order_id", "nunique"),
            items=("order_id", "size"),
        )
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    seller_df.insert(0, "Rank", range(1, len(seller_df) + 1))

    st.dataframe(
        seller_df.rename(
            columns={
                "seller_id": "Seller ID",
                "revenue": "Revenue",
                "orders": "Orders",
                "items": "Items",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    late = filtered.loc[
        filtered["delivery_status"].isin(["Late", "On time"])
    ].copy()

    if not late.empty:
        delivery_review = (
            late.groupby("delivery_status", as_index=False)
            .agg(
                orders=("order_id", "nunique"),
                avg_review=("review_score", "mean"),
                avg_days=("delivery_days", "mean"),
            )
        )
        delivery_review["avg_review"] = delivery_review["avg_review"].round(2)
        delivery_review["avg_days"] = delivery_review["avg_days"].round(1)

        st.markdown("#### Delivery vs Customer Satisfaction")
        st.dataframe(
            delivery_review.rename(
                columns={
                    "delivery_status": "Delivery Status",
                    "orders": "Orders",
                    "avg_review": "Avg Review",
                    "avg_days": "Avg Delivery Days",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

st.markdown("---")
st.caption("Olist Data Warehouse Analytics Engine • Streamlit BI Dashboard")
