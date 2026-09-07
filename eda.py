"""
eda.py
------
Quick exploratory analysis with matplotlib. Saves 3 charts to plots/.

Run: python eda.py
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("data/warehouse.db")

# 1. Monthly revenue trend
monthly = pd.read_sql("""
    SELECT strftime('%Y-%m', order_purchase_timestamp) AS month, SUM(oi.price) AS revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month ORDER BY month
""", conn)
plt.figure(figsize=(9, 4))
plt.plot(monthly["month"], monthly["revenue"], marker="o")
plt.xticks(rotation=75)
plt.title("Monthly Revenue")
plt.tight_layout()
plt.savefig("plots/monthly_revenue.png")
plt.close()

# 2. Top 10 categories by revenue
categories = pd.read_sql("""
    SELECT ct.product_category_name_english AS category, SUM(oi.price) AS revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN category_translation ct ON ct.product_category_name = p.product_category_name
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY category ORDER BY revenue DESC LIMIT 10
""", conn)
plt.figure(figsize=(8, 5))
plt.barh(categories["category"][::-1], categories["revenue"][::-1])
plt.title("Top 10 Categories by Revenue")
plt.tight_layout()
plt.savefig("plots/top_categories.png")
plt.close()

# 3. Review score distribution
reviews = pd.read_sql("SELECT review_score, COUNT(*) AS n FROM order_reviews GROUP BY review_score", conn)
plt.figure(figsize=(5, 4))
plt.bar(reviews["review_score"], reviews["n"], color="steelblue")
plt.title("Review Score Distribution")
plt.xlabel("Score")
plt.tight_layout()
plt.savefig("plots/review_distribution.png")
plt.close()

print("Saved 3 charts to plots/")
