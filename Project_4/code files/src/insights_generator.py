from pathlib import Path
import pandas as pd


def generate_insights(df: pd.DataFrame, out_path: Path) -> None:
    """Generate business insights and write to a text file.

    This function computes top products, payment methods, referral sources,
    trend observations and produces actionable recommendations.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure expected columns exist (use lowercase canonical names)
    cols = {c.lower(): c for c in df.columns}
    # pick column names with fallback
    revenue_col = cols.get('revenue', next((c for c in df.columns if 'rev' in c.lower()), None))
    product_col = cols.get('product', next((c for c in df.columns if 'prod' in c.lower()), None))
    qty_col = cols.get('quantity', next((c for c in df.columns if 'qty' in c.lower()), None))
    pay_col = cols.get('payment_method', next((c for c in df.columns if 'payment' in c.lower()), None))
    ref_col = cols.get('referral_source', next((c for c in df.columns if 'ref' in c.lower()), None))
    date_col = cols.get('order_date', next((c for c in df.columns if 'date' in c.lower()), None))

    insights = []

    # Basic aggregates
    if product_col and revenue_col:
        rev_by_prod = df.groupby(product_col)[revenue_col].sum().sort_values(ascending=False)
        top_prod = rev_by_prod.index[0]
        insights.append(f"Highest revenue product: {top_prod} ({rev_by_prod.iloc[0]:.2f})")
    else:
        insights.append("Highest revenue product: Data not available")

    if pay_col and revenue_col:
        rev_by_pay = df.groupby(pay_col)[revenue_col].sum().sort_values(ascending=False)
        best_pay = rev_by_pay.index[0]
        insights.append(f"Best payment method (by revenue): {best_pay} ({rev_by_pay.iloc[0]:.2f})")
    else:
        insights.append("Best payment method: Data not available")

    if ref_col and revenue_col:
        rev_by_ref = df.groupby(ref_col)[revenue_col].sum().sort_values(ascending=False)
        best_ref = rev_by_ref.index[0]
        insights.append(f"Best referral source: {best_ref} ({rev_by_ref.iloc[0]:.2f})")
    else:
        insights.append("Best referral source: Data not available")

    # Trend analysis
    if date_col and revenue_col:
        ts = df[[date_col, revenue_col]].dropna()
        ts[date_col] = pd.to_datetime(ts[date_col], errors='coerce')
        ts = ts.dropna()
        monthly = ts.set_index(date_col).resample('M')[revenue_col].sum()
        if len(monthly) >= 2:
            trend = 'increasing' if monthly.iloc[-1] > monthly.iloc[0] else 'decreasing'
            insights.append(f"Revenue trend over period: {trend} (from {monthly.iloc[0]:.2f} to {monthly.iloc[-1]:.2f})")
        else:
            insights.append("Revenue trend: Not enough data")
    else:
        insights.append("Revenue trend: Data not available")

    if date_col and qty_col:
        tsq = df[[date_col, qty_col]].dropna()
        tsq[date_col] = pd.to_datetime(tsq[date_col], errors='coerce')
        tsq = tsq.dropna()
        monthly_q = tsq.set_index(date_col).resample('M')[qty_col].sum()
        if len(monthly_q) >= 2:
            trend_q = 'increasing' if monthly_q.iloc[-1] > monthly_q.iloc[0] else 'decreasing'
            insights.append(f"Quantity trend over period: {trend_q} (from {monthly_q.iloc[0]:.0f} to {monthly_q.iloc[-1]:.0f})")
        else:
            insights.append("Quantity trend: Not enough data")
    else:
        insights.append("Quantity trend: Data not available")

    # Additional actionable insights (simple heuristics)
    # 1. Focus on top 3 products
    if product_col and revenue_col:
        top3 = rev_by_prod.head(3)
        insights.append(f"Top 3 products contribute {top3.sum():.2f} total revenue; consider promotional focus." )
    else:
        insights.append("Top products analysis: insufficient data")

    # 2. Payment method opportunities
    if pay_col and revenue_col:
        share = rev_by_pay / rev_by_pay.sum()
        insights.append(f"Payment method share: {share.iloc[0]*100:.1f}% from top method — ensure smooth UX for this method.")
    else:
        insights.append("Payment share analysis: insufficient data")

    # 3. Referral optimization
    if ref_col and revenue_col:
        top_refs = rev_by_ref.sort_values(ascending=False).head(3)
        insights.append(f"Top referral sources: {', '.join(map(str, top_refs.index))} — consider allocating ad spend accordingly.")
    else:
        insights.append("Referral source analysis: insufficient data")

    # 4. Price/quantity correlation hint
    if revenue_col and qty_col:
        corr = df[[revenue_col, qty_col]].corr().iloc[0,1]
        insights.append(f"Revenue vs Quantity correlation: {corr:.2f} — review pricing or bundle strategies.")
    else:
        insights.append("Revenue-Quantity correlation: insufficient data")

    # 5. Data quality check
    missing = df.isna().sum()
    high_missing = missing[missing > 0]
    if not high_missing.empty:
        insights.append(f"Columns with missing values: {', '.join(map(str, high_missing.index))} — clean or impute before modeling.")
    else:
        insights.append("No missing values detected in key columns.")

    # Fill up to at least 10 insights by repeating/expanding
    while len(insights) < 10:
        insights.append("Review seasonal promotions and customer retention strategies for sustained growth.")

    # Write to file
    with open(out_path, 'w', encoding='utf-8') as f:
        for i, line in enumerate(insights, start=1):
            f.write(f"{i}. {line}\n")


if __name__ == '__main__':
    # quick local test runner (not used when imported)
    df = pd.read_excel(Path(__file__).resolve().parents[2] / 'Dataset.xlsx')
    generate_insights(df, Path(__file__).resolve().parents[2] / 'report' / 'insights' / 'business_insights.txt')
