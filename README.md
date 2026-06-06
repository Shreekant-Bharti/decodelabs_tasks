# DecodeLabs_Tasks — Run Instructions & Project Summaries

This repository contains several DecodeLabs data analytics projects. This top-level README provides quick run instructions and brief summaries for Project_3 and Project_4.

## Quick Prerequisites
- Python 3.8 or newer
- Recommended: create and activate a virtual environment
- Install dependencies per-project using each `requirements.txt` file

## Projects Overview

### Project_3 (copy of Project_1)
- Location: `Project_3/`
- Purpose: Import a sales Excel dataset to SQLite and run a set of predefined SQL analyses producing CSV reports.
- Key scripts:
  - `Project_3/code files/src/import_data.py` — reads `Dataset.xlsx` and writes `sales.db`.
  - `Project_3/code files/src/run_analysis.py` — executes SQL queries in `sql_queries.sql` and saves CSVs to `report/query_results/`.
- How to run:
  ```powershell
  cd "Project_3"
  python -m venv .venv          # optional
  .\.venv\Scripts\Activate.ps1  # Windows PowerShell
  pip install -r "requirements.txt"
  python "code files/src/import_data.py"
  python "code files/src/run_analysis.py"
  ```
- Notes:
  - `Dataset.xlsx` should be present in the `Project_3` root. If missing, copy it from `Project_1/Dataset.xlsx`.
  - Outputs: CSV files in `Project_3/report/query_results/` and `Project_3/report/Project_Report.md`.

### Project_4
- Location: `Project_4/`
- Purpose: Produce professional visualizations and business insights from the same sales dataset used by Project_3.
- Key scripts:
  - `Project_4/code files/src/data_visualization.py` — main runner that cleans data, creates charts, generates insights and a Markdown report, and saves screenshots.
  - `Project_4/code files/src/insights_generator.py` — produces `report/insights/business_insights.txt`.
  - `Project_4/code files/src/dashboard_summary.py` — writes a small JSON summary for quick dashboards.
- How to run:
  ```powershell
  cd "Project_4"
  python -m venv .venv          # optional
  .\.venv\Scripts\Activate.ps1  # Windows PowerShell
  pip install -r "requirements.txt"
  python "code files/src/data_visualization.py"
  ```
- Output locations:
  - Charts: `Project_4/report/charts/`
  - Insights: `Project_4/report/insights/business_insights.txt`
  - Report: `Project_4/report/Project_Report.md`
  - Screenshots: `Project_4/screenshots/`

## Bot / CI Tips
- Run scripts from each project root to ensure relative paths resolve correctly.
- Capture stdout/stderr and fail the CI job on non-zero exit codes.
- If running in CI, ensure `openpyxl` is available (listed in `requirements.txt`).

## Repository Notes
- Large generated files (SQLite DB, CSV outputs, screenshots) are currently present in the projects. If you prefer a lightweight repo, consider removing them and regenerating in CI.
- To regenerate Project_3 outputs from scratch: delete `Project_3/sales.db` and the files in `Project_3/report/query_results/`, then re-run the import and analysis scripts.

## Contact
If something fails or you want a different layout (for example, to store only code and regenerate artifacts in CI), tell me and I will update the repo accordingly.
