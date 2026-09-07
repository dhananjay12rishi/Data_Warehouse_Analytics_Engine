-- queries.sql
-- Core business questions for the Olist warehouse.
-- Covers joins, a subquery, a CTE, and a window function.

-- 1. Monthly revenue trend
SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS month,
       COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(oi.price), 2) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;

-- 2. Top 10 categories by revenue
SELECT ct.product_category_name_english AS category,
       ROUND(SUM(oi.price), 2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN category_translation ct ON ct.product_category_name = p.product_category_name
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY revenue DESC
LIMIT 10;

-- 3. Top 10 sellers by revenue (window function: RANK)
SELECT seller_id, ROUND(revenue, 2) AS revenue,
       RANK() OVER (ORDER BY revenue DESC) AS rank
FROM (
    SELECT oi.seller_id, SUM(oi.price) AS revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.seller_id
)
ORDER BY revenue DESC
LIMIT 10;

-- 4. Repeat vs one-time customers (subquery)
SELECT CASE WHEN order_count > 1 THEN 'repeat' ELSE 'one_time' END AS customer_type,
       COUNT(*) AS num_customers
FROM (
    SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
GROUP BY customer_type;

-- 5. Delivery performance vs review score (CTE)
WITH delivery AS (
    SELECT o.order_id, r.review_score,
           CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                THEN 'late' ELSE 'on_time' END AS status
    FROM orders o
    JOIN order_reviews r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
)
SELECT status, COUNT(*) AS orders, ROUND(AVG(review_score), 2) AS avg_review_score
FROM delivery
GROUP BY status;

-- 6. Payment method breakdown
SELECT payment_type, COUNT(*) AS num_payments, ROUND(SUM(payment_value), 2) AS total_value
FROM order_payments
GROUP BY payment_type
ORDER BY total_value DESC;
