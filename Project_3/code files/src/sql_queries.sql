-- name: display_all
-- Display all records from the sales table
SELECT *
FROM sales;

-- name: filter_high_revenue
-- Filter records using WHERE: orders with revenue greater than 100
SELECT *
FROM sales
WHERE revenue > 100
ORDER BY revenue DESC;

-- name: sort_by_date_and_revenue
-- Sort records using ORDER BY: order_date ascending, revenue descending
SELECT
    order_id,
    order_date,
    product,
    revenue,
    quantity
FROM sales
ORDER BY order_date ASC, revenue DESC;

-- name: count_records
-- Count total number of orders
SELECT
    COUNT(*) AS total_orders
FROM sales;

-- name: total_revenue
-- Calculate total revenue across all orders
SELECT
    SUM(revenue) AS total_revenue
FROM sales;

-- name: average_revenue
-- Calculate average revenue per order
SELECT
    AVG(revenue) AS avg_revenue
FROM sales;

-- name: revenue_by_payment_method
-- Revenue grouped by payment method
SELECT
    COALESCE(payment_method, 'Unknown') AS payment_method,
    COUNT(*) AS orders,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_revenue
FROM sales
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- name: revenue_by_product
-- Revenue aggregated by product
SELECT
    product,
    COUNT(*) AS orders_sold,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_revenue
FROM sales
GROUP BY product
ORDER BY total_revenue DESC;

-- name: orders_by_referral_source
-- Orders and revenue by referral source
SELECT
    COALESCE(referral_source, 'Direct') AS referral_source,
    COUNT(*) AS orders,
    SUM(revenue) AS total_revenue
FROM sales
GROUP BY referral_source
ORDER BY orders DESC;

-- name: top_products_by_revenue
-- Top 10 products by revenue
SELECT
    product,
    SUM(revenue) AS total_revenue,
    COUNT(*) AS orders_sold
FROM sales
GROUP BY product
ORDER BY total_revenue DESC
LIMIT 10;
