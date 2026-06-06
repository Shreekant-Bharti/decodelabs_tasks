"""Run SQL analysis against the generated SQLite database and save results.

This script reads `src/sql_queries.sql`, executes each named query against
the `sales.db` SQLite database created by `import_data.py`, prints concise
results to stdout and saves each query result to CSV inside
`report/query_results/`.

Usage:
    python src/run_analysis.py
"""
from pathlib import Path
import sqlite3
import logging
import sys
from typing import Dict

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_named_queries(sql_file: Path) -> Dict[str, str]:
    """Parse SQL file with blocks preceded by `-- name: block_name`.

    Returns a dict mapping block_name -> SQL statement (string).
    """
    content = sql_file.read_text(encoding="utf-8")
    blocks = {}
    current_name = None
    current_sql_lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("-- name:"):
            # store previous
            if current_name and current_sql_lines:
                blocks[current_name] = "\n".join(current_sql_lines).strip()
            # start new
            current_name = stripped.split(":", 1)[1].strip()
            current_sql_lines = []
        else:
            # skip standalone comment lines that start with -- but not name
            current_sql_lines.append(line)

    if current_name and current_sql_lines:
        blocks[current_name] = "\n".join(current_sql_lines).strip()

    return blocks


def run_queries(db_path: Path, queries: Dict[str, str], out_dir: Path) -> None:
    """Execute queries and save results as CSV files in out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        logging.error("Failed to connect to database %s: %s", db_path, e)
        sys.exit(1)

    for name, sql in queries.items():
        logging.info("Running query: %s", name)
        try:
            df = pd.read_sql_query(sql, conn)
        except Exception as e:
            logging.error("Query failed (%s): %s", name, e)
            continue

        # Print a concise preview
        logging.info("Result for %s: %d rows", name, len(df))
        if not df.empty:
            # print top rows
            print(f"\n=== {name} (top 5 rows) ===")
            print(df.head(5).to_string(index=False))

        # Save to CSV
        out_file = out_dir / f"{name}.csv"
        try:
            df.to_csv(out_file, index=False)
            logging.info("Saved results to %s", out_file)
        except Exception as e:
            logging.error("Failed to write CSV for %s: %s", name, e)

    conn.close()


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    db_path = project_root / "sales.db"
    sql_file = project_root / "src" / "sql_queries.sql"
    out_dir = project_root / "report" / "query_results"

    if not db_path.exists():
        logging.error("Database not found: %s. Run import_data.py first.", db_path)
        sys.exit(1)
    if not sql_file.exists():
        logging.error("SQL queries file not found: %s", sql_file)
        sys.exit(1)

    queries = parse_named_queries(sql_file)
    if not queries:
        logging.error("No queries found in %s", sql_file)
        sys.exit(1)

    run_queries(db_path, queries, out_dir)


if __name__ == "__main__":
    main()
