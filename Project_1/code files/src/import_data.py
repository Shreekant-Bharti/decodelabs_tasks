"""Import Excel dataset into a local SQLite database.

This script reads 'Dataset for Data Analytics.xlsx' from the project's
`dataset/` folder, normalizes column names to a small canonical set and
exports the DataFrame to an SQLite database file `sales.db` placed at the
project root.

Usage:
    python src/import_data.py

The script will attempt to locate the Excel file inside the project `dataset/`
folder. If not found, it will attempt the user's `Downloads` folder as a
fallback. It writes `sales` table to `sales.db` (created or replaced).
"""
from pathlib import Path
import logging
import sys
import sqlite3
from typing import Dict, Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _clean_column_name(name: str) -> str:
    """Return a normalized column name suitable for mapping.

    Lowercase, strip, replace whitespace and punctuation with underscore.
    """
    if not isinstance(name, str):
        name = str(name)
    s = name.strip().lower()
    for ch in [" ", "-", "/", "\\", ",", "(", ")", "%"]:
        s = s.replace(ch, "_")
    # collapse multiple underscores
    while "__" in s:
        s = s.replace("__", "_")
    return s


def _find_column(df: pd.DataFrame, keywords) -> Optional[str]:
    """Find first column name in DataFrame containing any of the keywords."""
    cols = list(df.columns)
    for col in cols:
        low = _clean_column_name(col)
        for kw in keywords:
            if kw in low:
                return col
    return None


def build_canonical_mapping(df: pd.DataFrame) -> Dict[str, str]:
    """Map dataset columns to a canonical set expected by the analysis.

    The canonical columns used in SQL queries are:
      - order_id
      - order_date
      - product
      - revenue
      - quantity
      - payment_method
      - referral_source
      - customer_id

    Only columns found in the dataset will be included in the mapping. This
    makes generated SQL robust to varying dataset column names.
    """
    mapping = {}
    # detect common fields using keywords
    candidates = {
        "order_id": ["order_id", "orderid", "order_id", "order"],
        "order_date": ["order_date", "date", "orderdate", "purchase_date"],
        "product": ["product", "product_name", "item", "sku"],
        "revenue": ["revenue", "amount", "total", "price", "sales", "sale_amount"],
        "quantity": ["quantity", "qty", "count"],
        "payment_method": ["payment", "payment_method", "paymenttype", "method"],
        "referral_source": ["referral", "source", "referrer", "utm_source", "channel"],
        "customer_id": ["customer_id", "customer", "client_id", "client"]
    }

    for canonical, keys in candidates.items():
        found = _find_column(df, keys)
        if found is not None:
            mapping[found] = canonical

    return mapping


def import_excel_to_sqlite(excel_path: Path, db_path: Path) -> None:
    """Read an Excel file and write its contents to `sales` table in SQLite.

    The function normalizes columns and attempts to coerce numeric columns
    such as `revenue` and `quantity` to numeric types.
    """
    logging.info("Reading Excel file: %s", excel_path)
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        logging.error("Failed to read Excel file: %s", e)
        raise

    if df.empty:
        logging.warning("Input dataset is empty. No data imported.")

    # Build mapping from original column names to canonical names
    mapping = build_canonical_mapping(df)
    if mapping:
        logging.info("Mapping detected for columns: %s", mapping)
        df = df.rename(columns=mapping)
    else:
        logging.info("No canonical mappings detected. Using original column names.")

    # Coerce revenue-like and quantity-like columns if present
    if "revenue" in df.columns:
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    # Ensure target directory for DB exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to SQLite
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql("sales", conn, if_exists="replace", index=False)
        conn.close()
        logging.info("Successfully wrote %d rows to database: %s", len(df), db_path)
    except Exception as e:
        logging.error("Failed to write to SQLite database: %s", e)
        raise


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    db_path = project_root / "sales.db"

    # Try a set of common candidate paths for the dataset file. This makes the
    # script robust to small filename or placement changes made by the user.
    candidates = [
        project_root / "dataset" / "Dataset for Data Analytics.xlsx",
        project_root / "dataset" / "Dataset.xlsx",
        project_root / "Dataset for Data Analytics.xlsx",
        project_root / "Dataset.xlsx",
        Path.home() / "Downloads" / "Dataset for Data Analytics.xlsx",
        Path.home() / "Downloads" / "Dataset.xlsx",
    ]

    excel_path = None
    for p in candidates:
        if p.exists():
            excel_path = p
            # warn if using a fallback from Downloads
            if str(p).lower().find(str(Path.home()).lower()) != -1:
                logging.warning("Using fallback Excel path: %s", p)
            break

    # If still not found, attempt to discover any .xlsx in project dataset or root
    if excel_path is None:
        for folder in (project_root / "dataset", project_root):
            if folder.exists():
                found = next(folder.glob("*.xlsx"), None)
                if found:
                    excel_path = found
                    logging.warning("Using discovered Excel file: %s", found)
                    break

    if excel_path is None:
        logging.error("Dataset not found. Checked candidate locations.")
        sys.exit(1)

    import_excel_to_sqlite(excel_path, db_path)


if __name__ == "__main__":
    main()
