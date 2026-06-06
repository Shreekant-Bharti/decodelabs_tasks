# Project 3: SQL Data Analysis

## Introduction

This report documents the SQL-based analysis performed on the provided Excel
dataset (`Dataset for Data Analytics.xlsx`). The analysis demonstrates core
SQL concepts and provides actionable insights about sales, revenue, and
product performance.

## Objective

Use SQL to analyze sales data and demonstrate SELECT, WHERE, ORDER BY,
GROUP BY, COUNT(), SUM(), and AVG() using an SQLite-backed workflow.

## Dataset Overview

The dataset is an Excel spreadsheet containing sales/order level records.
Key fields used in the analysis include `order_id`, `order_date`, `product`,
`revenue`, `quantity`, `payment_method`, and `referral_source`.

## Methodology

1. Import the Excel data into an SQLite database using `src/import_data.py`.
2. Execute a curated set of SQL queries located in `src/sql_queries.sql`.
3. Save query outputs to CSV files in `report/query_results/` and review
   results to derive insights.

## SQL Queries Used

- Display all records
- Filter: orders with `revenue > 100`
- Sort: order by `order_date`, then `revenue`
- Aggregations: `COUNT(*)`, `SUM(revenue)`, `AVG(revenue)`
- Grouped metrics: revenue by payment method, by product, and by referral
  source
- Top products by revenue (LIMIT 10)

## Results and Insights

The code saves each query result to `report/query_results/` as CSV files. Run
the scripts in this repository to generate up-to-date numeric results from the
actual dataset. The queries are designed to reveal:

- Total revenue and average revenue per order
- Which payment methods generate the most revenue
- Top-performing products by revenue
- The distribution of orders across referral sources

Inspect the generated CSVs for precise numeric values and export them to your
preferred visualization tool if needed.

## Conclusion

This project provides a reproducible, SQL-first analysis pipeline for the
provided sales dataset. The included queries cover foundational SQL
operations and produce ready-to-share CSV outputs useful for further
visualization and reporting.

## Learning Outcomes

- Built an end-to-end ETL flow from Excel to SQLite using Python and pandas
- Applied SQL aggregation and grouping for business metrics
- Automated query execution and reporting
