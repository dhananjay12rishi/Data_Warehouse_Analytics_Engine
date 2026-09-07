# Analytics_Engine

A simple DBMS + EDA project on the Olist Brazilian E-Commerce dataset:
clean the raw CSVs, load them into a relational SQLite database, run
SQL business queries, explore with matplotlib, and view an interactive
Streamlit dashboard.

## Project structure

```text
Analytics_Engine/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── raw/          put the 9 Olist CSVs here (not committed)
├── etl.py             loads, cleans, and builds data/warehouse.db
├── queries.sql          6 business-question SQL queries
├── eda.py                 matplotlib charts, saved to plots/
└── dashboard.py             interactive Streamlit dashboard
```

## Database

7 tables: `customers`, `sellers`, `products`, `category_translation`,
`orders`, `order_items`, `order_payments`, `order_reviews` — linked by
foreign keys (customer → orders → order_items → products/sellers,
orders → payments/reviews).

## How to run

```bash
pip install -r requirements.txt

# 1. Put the 9 Olist CSVs in data/raw/
python etl.py              # cleans the data, builds data/warehouse.db

# 2. Explore
python eda.py               # saves charts to plots/
streamlit run dashboard.py   # interactive dashboard
```

## A few real findings

- Late-delivered orders average a **2.57** review score vs **4.29** for
  on-time orders.
- Only **3.0%** of customers placed more than one order.
- `health_beauty`, `watches_gifts`, and `bed_bath_table` are the top 3
  categories by revenue.

## Push to GitHub

```bash
cd Analytics_Engine
git remote add origin https://github.com/<your-username>/Analytics_Engine.git
git push -u origin main
```
(the repo is already git-initialized and committed — just create the
empty repo on GitHub and run the two commands above)
