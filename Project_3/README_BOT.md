Project 3 - Bot Run Instructions and Project Details

Purpose:
This file provides step-by-step instructions for an automation bot (or CI) to run Project_3 (a copy of Project_1) and generate analysis outputs.

Project structure (top-level):
- code files/
  - src/
    - import_data.py    # imports Dataset.xlsx into sales.db
    - run_analysis.py   # runs SQL queries and writes CSV results to report/query_results/
- report/
  - query_results/     # CSV outputs
  - Project_Report.md  # human-readable report
- Dataset.xlsx          # dataset used by the project
- README.md
- README_BOT.md         # this file
- requirements.txt      # Python dependencies

Bot/Automation Instructions:
1. Environment setup
   - Ensure Python 3.8+ is installed
   - Create and activate a virtual environment (recommended)
     Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - Install requirements:
     ```powershell
     pip install -r requirements.txt
     ```

2. Folder and file expectations
   - `Dataset.xlsx` must be present in the Project_3 root. If missing, the script will fail.
   - The scripts assume they are run from the project root. Working directory should be `Project_3`.

3. Run steps for the bot (non-interactive)
   - Run import to create SQLite DB:
     ```powershell
     python "code files/src/import_data.py"
     ```
   - Run analysis queries:
     ```powershell
     python "code files/src/run_analysis.py"
     ```
   - After completion, CSV outputs will be in `report/query_results/` and `Project_Report.md` should be present in `report/`.

4. Exit codes and error handling
   - Both scripts call `sys.exit(1)` on fatal errors (missing dataset or DB connection failure). The bot should detect non-zero exit codes and capture logs.
   - Check stdout/stderr for `INFO:` / `ERROR:` messages for diagnostics.

5. Optional: clean and re-run
   - To regenerate outputs from scratch, remove `sales.db` in the project root and delete files in `report/query_results/`, then re-run the two scripts above.

6. Notes for maintainers
   - The dataset column names may vary; `import_data.py` already maps common variants to canonical names used by SQL queries.
   - If running in CI, ensure `openpyxl` is available (it is listed in `requirements.txt`).

Project Details (summary):
- Objective: Import sales data, run predefined SQL queries, and save results as CSV for reporting.
- Dataset columns used: order id, date, product, quantity, price/total. See `code files/src/sql_queries.sql` for queries.
- Outputs: CSVs in `report/query_results/` and a human-readable report in `report/Project_Report.md`.

Contact:
- If the bot encounters unexpected errors, please open an issue or contact the project owner.
