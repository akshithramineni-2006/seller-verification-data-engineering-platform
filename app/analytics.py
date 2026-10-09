
from pathlib import Path

import duckdb

DATABASE = Path("data/gold/warehouse.duckdb")
SQL_FILE = Path("sql/analytics.sql")
EXPORT_DIR = Path("dashboard/exports")

EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_query(title, filename, query):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    con = duckdb.connect(str(DATABASE), read_only=True)

    try:
        df = con.execute(query).fetchdf()
    finally:
        con.close()

    print(df)

    output = EXPORT_DIR / filename
    df.to_csv(output, index=False)

    print(f"\nSaved -> {output}")
    return df



def load_queries():
    """Read named analytics queries from the SQL file."""
    import re

    content = SQL_FILE.read_text(encoding="utf-8")

    sections = re.split(
        r"(?m)^--\s+\d+\.\s+",
        content
    )

    queries = {}

    for section in sections[1:]:
        lines = section.splitlines()
        title = lines[0].strip()

        sql_lines = [
            line for line in lines[1:]
            if not line.strip().startswith("--")
        ]

        query = "\n".join(sql_lines).strip()

        if query:
            queries[title] = query

    return queries



if __name__ == "__main__":
    queries = load_queries()

    exports = [
        ("Total Sellers", "total_sellers.csv"),
        ("Revenue by Country", "revenue_by_country.csv"),
        ("Revenue by Business Type", "revenue_by_business.csv"),
        ("Top 10 High Risk Sellers", "high_risk_sellers.csv"),
        ("Monthly Seller Registrations", "monthly_registrations.csv"),
        ("Refund Rate by Business Type", "refund_rate.csv"),
        ("Average Revenue by Industry", "industry_revenue.csv"),
        ("Verification Status", "verification_status.csv"),
        ("Country Verification Summary", "country_verification.csv"),
    ]

    for title, filename in exports:
        if title not in queries:
            raise ValueError(
                f"Query '{title}' was not found in {SQL_FILE}"
            )

        run_query(title, filename, queries[title])
