"""Data visualization pipeline for Project_4.

Loads dataset, cleans data, generates charts, saves them to report/charts,
generates business insights and project report, and saves screenshots.

Usage:
    python data_visualization.py
"""
from pathlib import Path
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from insights_generator import generate_insights
from dashboard_summary import write_dashboard_summary


def _clean_column_name(name: str) -> str:
    s = str(name).strip().lower()
    for ch in [' ', '-', '/', '\\', ',', '(', ')', '%']:
        s = s.replace(ch, '_')
    while '__' in s:
        s = s.replace('__', '_')
    return s


def locate_dataset(project_root: Path) -> Path:
    """Locate Dataset.xlsx in project root or fallback to Project_1 dataset.

    If the dataset is not present inside Project_4, it will copy the file
    from ../Project_1/Dataset.xlsx if available.
    """
    local = project_root / 'Dataset.xlsx'
    if local.exists():
        return local

    # check sibling Project_1 and workspace root locations
    alt = project_root.parent / 'Project_1' / 'Dataset.xlsx'
    alt2 = project_root.parent / 'Project_1' / 'Dataset.xlsx'
    # also check workspace root Project_1
    alt_workspace = project_root.parent / 'Project_1' / 'Dataset.xlsx'
    candidates = [alt, alt2, alt_workspace]
    for candidate in candidates:
        if candidate.exists():
            alt = candidate
            break
    else:
        alt = None

    if alt and alt.exists():
        # copy to current project for consistency
        shutil.copy(alt, local)
        print(f"Copied dataset from {alt} to {local}")
        return local

    raise FileNotFoundError('Dataset.xlsx not found in Project_4 or ../Project_1')


def load_and_clean(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, engine='openpyxl')

    # Normalize column names to lowercase canonical names mapping
    col_map = {}
    for c in df.columns:
        clean = _clean_column_name(c)
        col_map[c] = clean
    df = df.rename(columns=col_map)

    # Standardize expected names
    # map common variants
    mappings = {
        'orderid': 'order_id',
        'order_id': 'order_id',
        'order_date': 'order_date',
        'date': 'order_date',
        'product': 'product',
        'product_name': 'product',
        'revenue': 'revenue',
        'amount': 'revenue',
        'total': 'revenue',
        'unitprice': 'revenue',
        'unit_price': 'revenue',
        'sale_amount': 'revenue',
        'totalprice': 'revenue',
        'total_price': 'revenue',
        'quantity': 'quantity',
        'qty': 'quantity',
        'payment_method': 'payment_method',
        'paymentmethod': 'payment_method',
        'payment': 'payment_method',
        'referral_source': 'referral_source',
        'referralsource': 'referral_source',
        'source': 'referral_source',
        'customer_id': 'customer_id'
    }

    df = df.rename(columns={c: mappings.get(c, c) for c in df.columns})

    # Parse dates
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

    # Coerce numeric
    if 'revenue' in df.columns:
        # handle potential duplicate columns named 'revenue' (pandas may return a DataFrame)
        rev = df['revenue']
        if isinstance(rev, pd.DataFrame):
            # take first non-null value across duplicate columns per row
            newrev = rev.apply(lambda row: row.dropna().iloc[0] if row.dropna().size > 0 else np.nan, axis=1)
            # drop all existing columns named 'revenue' to avoid duplicates
            df = df.drop(columns=[c for c in df.columns if c == 'revenue'])
            df['revenue'] = newrev
        else:
            df['revenue'] = rev
        # ensure numeric
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    if 'quantity' in df.columns:
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')

    # Drop rows without revenue and product
    df = df.dropna(subset=[col for col in ['revenue', 'product'] if col in df.columns])

    return df


def save_chart(fig, out_path: Path, dpi=150):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches='tight', dpi=dpi)
    plt.close(fig)


def make_charts(df: pd.DataFrame, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    charts = {}

    sns.set_theme(style='whitegrid')
    palette = sns.color_palette('tab10')

    # 1. Revenue by Product
    rev_by_prod = df.groupby('product', dropna=True)['revenue'].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=rev_by_prod.values, y=rev_by_prod.index, palette=palette, ax=ax)
    ax.set_title('Revenue by Product', fontsize=14)
    ax.set_xlabel('Total Revenue')
    ax.set_ylabel('Product')
    save_chart(fig, out_dir / 'revenue_by_product.png')
    charts['revenue_by_product'] = rev_by_prod

    # 2. Revenue by Payment Method
    if 'payment_method' in df.columns:
        rev_by_pay = df.groupby('payment_method')['revenue'].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(x=rev_by_pay.index, y=rev_by_pay.values, palette=palette, ax=ax)
        ax.set_title('Revenue by Payment Method')
        ax.set_xlabel('Payment Method')
        ax.set_ylabel('Total Revenue')
        plt.xticks(rotation=30)
        save_chart(fig, out_dir / 'revenue_by_payment_method.png')
        charts['revenue_by_payment_method'] = rev_by_pay

    # 3. Monthly Revenue Trend
    if 'order_date' in df.columns:
        monthly = df.set_index('order_date').resample('M')['revenue'].sum()
        fig, ax = plt.subplots(figsize=(10,5))
        sns.lineplot(x=monthly.index, y=monthly.values, marker='o', ax=ax)
        ax.set_title('Monthly Revenue Trend')
        ax.set_xlabel('Month')
        ax.set_ylabel('Revenue')
        save_chart(fig, out_dir / 'monthly_revenue_trend.png')
        charts['monthly_revenue_trend'] = monthly

    # 4. Top Performing Products
    top_products = rev_by_prod.head(10)
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=top_products.values, y=top_products.index, palette=palette, ax=ax)
    ax.set_title('Top Performing Products (by Revenue)')
    ax.set_xlabel('Revenue')
    ax.set_ylabel('Product')
    save_chart(fig, out_dir / 'top_products.png')
    charts['top_products'] = top_products

    # 5. Revenue by Referral Source
    if 'referral_source' in df.columns:
        rev_by_ref = df.groupby('referral_source')['revenue'].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(x=rev_by_ref.values, y=rev_by_ref.index, palette=palette, ax=ax)
        ax.set_title('Revenue by Referral Source')
        ax.set_xlabel('Revenue')
        ax.set_ylabel('Referral Source')
        save_chart(fig, out_dir / 'revenue_by_referral_source.png')
        charts['revenue_by_referral_source'] = rev_by_ref

    # 6. Quantity Sold by Product
    if 'quantity' in df.columns:
        qty_by_prod = df.groupby('product')['quantity'].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10,6))
        sns.barplot(x=qty_by_prod.values, y=qty_by_prod.index, palette=palette, ax=ax)
        ax.set_title('Quantity Sold by Product')
        ax.set_xlabel('Quantity')
        ax.set_ylabel('Product')
        save_chart(fig, out_dir / 'quantity_by_product.png')
        charts['quantity_by_product'] = qty_by_prod

    # 7. Revenue Distribution Histogram
    fig, ax = plt.subplots(figsize=(8,5))
    sns.histplot(df['revenue'].dropna(), bins=30, kde=True, color=palette[0], ax=ax)
    ax.set_title('Revenue Distribution')
    ax.set_xlabel('Revenue')
    ax.set_ylabel('Count')
    save_chart(fig, out_dir / 'revenue_distribution.png')
    charts['revenue_distribution'] = df['revenue']

    # 8. Correlation Heatmap
    numeric_cols = []
    for c in ['revenue', 'quantity']:
        if c in df.columns:
            numeric_cols.append(c)
    # also add encoded categorical counts for product if needed
    if 'product' in df.columns:
        df['product_code'] = df['product'].astype('category').cat.codes
        numeric_cols.append('product_code')

    if numeric_cols:
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(6,5))
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt='.2f')
        ax.set_title('Correlation Heatmap')
        save_chart(fig, out_dir / 'correlation_heatmap.png')
        charts['correlation'] = corr

    return charts


def generate_report(project_root: Path, charts: dict, insights_path: Path) -> None:
    report_path = project_root / 'report' / 'Project_Report.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Read insights
    insights = []
    if insights_path.exists():
        with open(insights_path, 'r', encoding='utf-8') as f:
            insights = f.read().splitlines()

    # Build report content
    lines = []
    lines.append('# Project 4 — Data Analytics Report')
    lines.append('')
    lines.append('## Project Overview')
    lines.append('Professional dashboard and visualizations for sales dataset.')
    lines.append('')
    lines.append('## Objectives')
    lines.append('- Data Storytelling')
    lines.append('- Data Visualization')
    lines.append('- Business Insights')
    lines.append('- Executive-Level Reporting')
    lines.append('')
    lines.append('## Tools Used')
    lines.append('- Python, pandas, matplotlib, seaborn')
    lines.append('')
    lines.append('## Visualizations')

    chart_files = {
        'Revenue by Product': 'revenue_by_product.png',
        'Revenue by Payment Method': 'revenue_by_payment_method.png',
        'Monthly Revenue Trend': 'monthly_revenue_trend.png',
        'Top Performing Products': 'top_products.png',
        'Revenue by Referral Source': 'revenue_by_referral_source.png',
        'Quantity Sold by Product': 'quantity_by_product.png',
        'Revenue Distribution Histogram': 'revenue_distribution.png',
        'Correlation Heatmap': 'correlation_heatmap.png'
    }

    for title, fname in chart_files.items():
        path = Path('report') / 'charts' / fname
        lines.append(f'### {title}')
        lines.append('- Purpose: Visualize ' + title.lower())
        lines.append('- Observation: See chart')
        lines.append(f'- Chart file: {path}')
        lines.append('')

    lines.append('## Key Findings')
    if insights:
        lines.append('Top insights:')
        for line in insights[:10]:
            lines.append(f'- {line}')
    else:
        lines.append('Insights file not found.')

    lines.append('')
    lines.append('## Business Recommendations')
    lines.append('- Focus marketing on top referral channels.')
    lines.append('- Promote top 3 products with bundles and discounts.')
    lines.append('- Improve checkout UX for top payment methods.')
    lines.append('')
    lines.append('## Conclusion')
    lines.append('The visualizations and insights provide a data-driven starting point for commercial decisions.')

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def make_screenshots(project_root: Path) -> None:
    """Create simple screenshot images for requested items.

    Since this environment cannot take OS-level screenshots, generate
    representative PNGs with text and embed chart images where possible.
    """
    import matplotlib.pyplot as plt

    shots = project_root / 'screenshots'
    shots.mkdir(parents=True, exist_ok=True)

    # 1. Project structure (list files)
    files = []
    for p in sorted(project_root.rglob('*')):
        rel = p.relative_to(project_root)
        files.append(str(rel))
    fig, ax = plt.subplots(figsize=(8,10))
    ax.axis('off')
    ax.text(0, 1, 'Project Structure:\n' + '\n'.join(files[:60]), va='top', fontsize=8, family='monospace')
    fig.savefig(shots / 'project_structure.png', bbox_inches='tight', dpi=120)
    plt.close(fig)

    # 2. Generated charts folder (list chart files)
    charts_dir = project_root / 'report' / 'charts'
    charts_list = [p.name for p in charts_dir.glob('*.png')]
    fig, ax = plt.subplots(figsize=(6,4))
    ax.axis('off')
    ax.text(0, 1, 'Charts generated:\n' + '\n'.join(charts_list), va='top', fontsize=10, family='monospace')
    fig.savefig(shots / 'generated_charts_folder.png', bbox_inches='tight', dpi=120)
    plt.close(fig)

    # 3-5: copy some chart images for specific screenshots if they exist
    def copy_chart(name, dest_name):
        src = charts_dir / name
        if src.exists():
            shutil.copy(src, shots / dest_name)

    copy_chart('correlation_heatmap.png', 'correlation_heatmap.png')
    copy_chart('revenue_by_product.png', 'revenue_by_product.png')
    copy_chart('monthly_revenue_trend.png', 'monthly_revenue_trend.png')

    # 6. README preview
    readme = project_root / 'README.md'
    txt = readme.read_text(encoding='utf-8') if readme.exists() else 'No README'
    fig, ax = plt.subplots(figsize=(8,6))
    ax.axis('off')
    ax.text(0, 1, txt[:400], va='top', fontsize=9, family='monospace')
    fig.savefig(shots / 'README_preview.png', bbox_inches='tight', dpi=120)
    plt.close(fig)

    # 7. Project report preview
    report_md = project_root / 'report' / 'Project_Report.md'
    txt = report_md.read_text(encoding='utf-8') if report_md.exists() else 'No report yet'
    fig, ax = plt.subplots(figsize=(8,6))
    ax.axis('off')
    ax.text(0, 1, txt[:800], va='top', fontsize=9, family='monospace')
    fig.savefig(shots / 'project_report_preview.png', bbox_inches='tight', dpi=120)
    plt.close(fig)


def main():
    project_root = Path(__file__).resolve().parents[2]
    try:
        dataset = locate_dataset(project_root)
    except FileNotFoundError as e:
        print(e)
        return

    df = load_and_clean(dataset)

    charts = make_charts(df, project_root / 'report' / 'charts')

    insights_path = project_root / 'report' / 'insights' / 'business_insights.txt'
    generate_insights(df, insights_path)

    # Dashboard summary
    summary = {
        'total_revenue': float(df['revenue'].sum()),
        'total_orders': int(df.shape[0]),
        'top_product': charts.get('top_products').index[0] if charts.get('top_products') is not None else None
    }
    write_dashboard_summary(summary, project_root / 'report' / 'dashboard_summary.json')

    generate_report(project_root, charts, insights_path)

    make_screenshots(project_root)

    print('Project 4 completed successfully.')


if __name__ == '__main__':
    main()
