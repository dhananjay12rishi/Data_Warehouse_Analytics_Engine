"""
etl.py
------
Loads the raw Olist CSV files, cleans them up, and builds a small SQLite
database out of them.

Run: python etl.py
"""

import pandas as pd
import sqlite3
import os

RAW_DIR = "data/raw"
DB_PATH = "data/warehouse.db"


def load(filename):
    df = pd.read_csv(os.path.join(RAW_DIR, filename))
    print(f"Loaded {filename}: {len(df)} rows")
    return df


def main():
    print("=== Loading raw CSVs ===")
    customers = load("olist_customers_dataset.csv")
    sellers = load("olist_sellers_dataset.csv")
    products = load("olist_products_dataset.csv")
    orders = load("olist_orders_dataset.csv")
    order_items = load("olist_order_items_dataset.csv")
    order_payments = load("olist_order_payments_dataset.csv")
    order_reviews = load("olist_order_reviews_dataset.csv")
    category_translation = load("product_category_name_translation.csv")

    print("\n=== Data quality check ===")
    print("Missing categories in products:", products["product_category_name"].isnull().sum())
    print("Duplicate review_id rows:", order_reviews.duplicated(subset=["review_id"]).sum())
    print("Missing delivery dates (undelivered orders):", orders["order_delivered_customer_date"].isnull().sum())

    print("\n=== Cleaning ===")
    # Standardize text columns
    customers["customer_city"] = customers["customer_city"].str.strip().str.title()
    customers["customer_state"] = customers["customer_state"].str.upper()
    sellers["seller_city"] = sellers["seller_city"].str.strip().str.title()
    sellers["seller_state"] = sellers["seller_state"].str.upper()

    # Fill missing product category with "unknown"
    products["product_category_name"] = products["product_category_name"].fillna("unknown")
    category_translation = pd.concat([
        category_translation,
        pd.DataFrame([{"product_category_name": "unknown", "product_category_name_english": "unknown"}]),
    ], ignore_index=True)

    # Parse dates
    for col in ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")
    orders["order_status"] = orders["order_status"].str.lower()

    # review_id isn't always unique on its own - keep a surrogate key
    order_reviews = order_reviews.drop_duplicates(subset=["review_id", "order_id"]).reset_index(drop=True)
    order_reviews.insert(0, "review_pk", range(1, len(order_reviews) + 1))

    print("\n=== Building database ===")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    customers[["customer_id", "customer_unique_id", "customer_city", "customer_state"]].to_sql("customers", conn, index=False)
    sellers[["seller_id", "seller_city", "seller_state"]].to_sql("sellers", conn, index=False)
    category_translation.to_sql("category_translation", conn, index=False)
    products[["product_id", "product_category_name"]].to_sql("products", conn, index=False)
    orders[["order_id", "customer_id", "order_status", "order_purchase_timestamp",
            "order_delivered_customer_date", "order_estimated_delivery_date"]].to_sql("orders", conn, index=False)
    order_items[["order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"]].to_sql("order_items", conn, index=False)
    order_payments[["order_id", "payment_type", "payment_installments", "payment_value"]].to_sql("order_payments", conn, index=False)
    order_reviews[["review_pk", "review_id", "order_id", "review_score"]].to_sql("order_reviews", conn, index=False)

    conn.commit()
    conn.close()
    print(f"Database ready at {DB_PATH}")


if __name__ == "__main__":
    main()
