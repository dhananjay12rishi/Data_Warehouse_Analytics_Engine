# Data Warehouse & Analytics Engine

An end-to-end **data engineering and business intelligence project** built using the Brazilian Olist E-Commerce dataset.

The project demonstrates a complete analytics workflow:

**Raw Data → ETL & Data Cleaning → Relational Data Warehouse → SQL Analytics → Interactive BI Dashboard**

---

## 📊 Project Overview

This project transforms raw Brazilian e-commerce data into a structured analytical data warehouse and an interactive Streamlit dashboard.

The system integrates information about:

- Customers
- Orders
- Products
- Sellers
- Order items
- Payments
- Reviews
- Product categories
- Brazilian geography

The final dashboard provides business insights into **sales performance, customer behavior, product performance, payments, reviews, sellers, and delivery operations**.

---

## 🏗️ Architecture

```text
                    Olist Raw Dataset
                           │
                           ▼
                    ┌─────────────┐
                    │    ETL      │
                    │   etl.py    │
                    └──────┬──────┘
                           │
                 Cleaning & Transformation
                           │
                           ▼
                 ┌──────────────────┐
                 │ SQLite Warehouse │
                 │  warehouse.db    │
                 └────────┬─────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       SQL Analytics              EDA / Plots
      queries.sql                  eda.py
              │
              └───────────┬───────────┘
                          ▼
                 ┌─────────────────┐
                 │ Streamlit BI    │
                 │    Dashboard    │
                 └─────────────────┘
```

---

## 🚀 Key Features

### 1. ETL Pipeline

`etl.py` performs the data engineering workflow:

- Loads raw CSV datasets
- Performs data quality checks
- Handles missing values
- Removes duplicate review records
- Converts date fields
- Creates derived analytical fields
- Builds the SQLite warehouse

---

### 2. Relational Data Warehouse

The project uses **SQLite** as the analytical warehouse.

The warehouse integrates multiple interconnected entities including:

- Customers
- Orders
- Order Items
- Products
- Sellers
- Payments
- Reviews
- Product Category Translation

This structure enables relational SQL analysis across the e-commerce ecosystem.

---

### 3. SQL Analytics

`queries.sql` contains analytical queries using:

- `JOIN`
- `GROUP BY`
- Aggregations
- Subqueries
- Common Table Expressions (CTEs)
- Window functions
- Ranking
- Time-based analysis

The queries answer practical business questions around revenue, customers, products, sellers, payments, and reviews.

---

## 📈 Interactive Power BI-Style Dashboard

The project includes two Streamlit dashboards:

### `dashboard.py`

The original interactive analytics dashboard.

### `dashboard_powerbi.py`

A more advanced **Power BI-style business intelligence dashboard** with:

- Executive Overview
- Sales & Products analysis
- Customers & Operations analysis
- KPI cards
- Revenue trends
- Order trends
- Product category analysis
- Payment analysis
- Customer geography
- Seller performance
- Delivery performance
- Review analysis
- Interactive filters

Available filters include:

- Date range
- Customer state
- Product category
- Order status
- Payment type

---

## 📊 Dashboard Sections

### Executive Overview

Provides a high-level business summary including:

- Total Revenue
- Total Orders
- Total Customers
- Average Order Value
- Average Review Score
- Monthly Revenue
- Monthly Orders
- Order Status Distribution
- Review Score Distribution
- Delivery Success Rate

### Sales & Products

Analyzes:

- Revenue by product category
- Top 10 categories
- Payment methods
- Freight value
- Units sold
- Category-level performance

### Customers & Operations

Analyzes:

- Unique customers
- Repeat customers
- Repeat purchase rate
- Revenue by Brazilian state
- Delivery performance
- Average delivery time
- Top sellers
- Delivery vs customer satisfaction

---

## 🛠️ Technology Stack

| Technology   | Purpose                        |
| ------------ | ------------------------------ |
| Python       | Core programming               |
| Pandas       | Data processing                |
| SQLite       | Data warehouse                 |
| SQL          | Business analytics             |
| Matplotlib   | Data visualization             |
| Streamlit    | Interactive BI dashboard       |
| Git & GitHub | Version control and deployment |

---

## 📁 Project Structure

```text
Data_Warehouse_Analytics_Engine/
│
├── dashboard.py
├── dashboard_powerbi.py
├── etl.py
├── eda.py
├── queries.sql
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── Olist CSV datasets
│   └── warehouse.db
│
└── plots/
    ├── monthly_revenue.png
    ├── top_categories.png
    └── review_distribution.png
```

---

## ⚙️ Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Data_Warehouse_Analytics_Engine.git
cd Data_Warehouse_Analytics_Engine
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Add the Olist dataset

Place the required CSV files inside:

```text
data/raw/
```

### 5. Build the warehouse

```powershell
python etl.py
```

This creates:

```text
data/warehouse.db
```

### 6. Launch the dashboard

Original dashboard:

```powershell
python -m streamlit run dashboard.py
```

Power BI-style dashboard:

```powershell
python -m streamlit run dashboard_powerbi.py
```

---

## 📦 Requirements

The project uses:

```text
pandas
matplotlib
streamlit
```

See `requirements.txt` for the exact dependency specification.

---

## 🔍 Data Quality Checks

During ETL, the pipeline checks for issues including:

- Missing product categories
- Duplicate review IDs
- Missing delivery dates
- Undelivered orders

These checks are performed before the warehouse is constructed.

---

## 💡 Business Questions Answered

The analytics engine can be used to investigate questions such as:

- How is revenue changing over time?
- Which product categories generate the most revenue?
- Which states contribute the most sales?
- Which payment methods are most commonly used?
- Which sellers generate the most revenue?
- How many customers make repeat purchases?
- What is the average order value?
- How long does delivery take?
- How frequently are orders delivered late?
- Does delivery performance relate to customer reviews?
- Which categories have the strongest commercial performance?

---

## 🎯 Project Objective

The objective is to demonstrate an end-to-end **data warehouse and analytics engineering workflow** rather than simply performing exploratory data analysis.

The project combines:

**Data Engineering + Relational Modeling + SQL Analytics + Business Intelligence**

into a single deployable analytics application.

---

## 🌐 Deployment

The Streamlit application is designed to be deployed using **Streamlit Community Cloud**.

The production deployment will use:

```text
GitHub Repository
        ↓
Streamlit Community Cloud
        ↓
Interactive BI Dashboard
```

---

## 📚 Dataset

The project uses the **Brazilian Olist E-Commerce Dataset**, containing anonymized commercial information from orders placed on the Olist marketplace.

The dataset is used for educational and analytical purposes.

---

## 👤 Author

**Dhananjay Pratap Singh**

Data Analytics | Data Engineering | Machine Learning

---

## ⭐ Project Highlights

This project demonstrates practical experience with:

- End-to-end ETL pipelines
- Data cleaning and quality validation
- Relational data warehousing
- SQL-based analytics
- Business intelligence
- Interactive dashboards
- Data visualization
- Python data engineering
- Streamlit deployment
- Git/GitHub workflow
