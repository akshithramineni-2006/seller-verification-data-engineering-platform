
from pathlib import Path

import duckdb
import pandas as pd

from app.config import SILVER_DATA

DATABASE = Path("data/gold/warehouse.duckdb")
SQL_FILE = Path("sql/validation.sql")
EXPORT_DIR = Path("dashboard/exports")

EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def generate_quality_report():
    con = duckdb.connect(str(DATABASE), read_only=False)

    try:
        # Register Silver Parquet files as temporary DuckDB views.
        con.execute(
            "CREATE OR REPLACE VIEW sellers AS "
            f"SELECT * FROM read_parquet('{(SILVER_DATA / 'sellers.parquet').as_posix()}')"
        )

        con.execute(
            "CREATE OR REPLACE VIEW verification AS "
            f"SELECT * FROM read_parquet('{(SILVER_DATA / 'verification.parquet').as_posix()}')"
        )

        con.execute(
            "CREATE OR REPLACE VIEW transactions AS "
            f"SELECT * FROM read_parquet('{(SILVER_DATA / 'transactions.parquet').as_posix()}')"
        )

        con.execute(
            "CREATE OR REPLACE VIEW fraud AS "
            f"SELECT * FROM read_parquet('{(SILVER_DATA / 'fraud_events.parquet').as_posix()}')"
        )

        # Execute each validation query and combine its result.
        script = SQL_FILE.read_text(encoding="utf-8")
        statements = [
            statement.strip()
            for statement in script.split(";")
            if statement.strip()
            and not all(
                line.strip().startswith("--") or not line.strip()
                for line in statement.splitlines()
            )
        ]

        results = []

        for statement in statements:
            result = con.execute(statement).fetchdf()
            results.append(result)

        quality_report = pd.concat(results, ignore_index=True)

    finally:
        con.close()

    output = EXPORT_DIR / "quality_report.csv"
    quality_report.to_csv(output, index=False)

    print("\nQuality Report")
    print("-" * 40)
    print(quality_report)
    print(f"\nSaved -> {output}")


if __name__ == "__main__":
    generate_quality_report()
