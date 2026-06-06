# Project 3: SQL Data Analysis

This repository contains an end-to-end SQL data analysis pipeline for the
DecodeLabs internship Project 3. The dataset is an Excel file and the
analysis uses SQLite with SQL queries executed from Python.

Overview

- Objective: Demonstrate SQL data analysis using SELECT, WHERE, ORDER BY,
  GROUP BY, COUNT(), SUM(), and AVG().
- Dataset: `Dataset for Data Analytics.xlsx` (place in `dataset/`).
- Output: `sales.db` (SQLite), CSVs in `report/query_results/`, and a
  written report `report/Project_Report.md`.

Quick start

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
python src/import_data.py
python src/run_analysis.py
```

Files

- `src/import_data.py` — imports Excel into SQLite `sales` table
- `src/sql_queries.sql` — authored SQL queries for analysis
- `src/run_analysis.py` — runs queries and exports CSVs
- `report/Project_Report.md` — formal analysis report

Author: Shreekant Bharti
