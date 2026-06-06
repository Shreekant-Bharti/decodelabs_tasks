from pathlib import Path
import json


def write_dashboard_summary(summary: dict, out_path: Path) -> None:
    """Write a small JSON summary of dashboard metrics for quick reference."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)


if __name__ == '__main__':
    sample = {
        "total_revenue": 0.0,
        "total_orders": 0,
        "top_product": None
    }
    write_dashboard_summary(sample, Path(__file__).resolve().parents[2] / 'report' / 'dashboard_summary.json')
