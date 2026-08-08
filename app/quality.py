import pandas as pd
from pathlib import Path

from app.config import SILVER_DATA

EXPORT_DIR = Path("dashboard") / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def generate_quality_report():

    sellers = pd.read_parquet(
        SILVER_DATA / "sellers.parquet"
    )

    verification = pd.read_parquet(
        SILVER_DATA / "verification.parquet"
    )

    transactions = pd.read_parquet(
        SILVER_DATA / "transactions.parquet"
    )

    fraud = pd.read_parquet(
        SILVER_DATA / "fraud_events.parquet"
    )

    report = []

    report.append({
        "Check": "Duplicate Seller IDs",
        "Count": sellers.duplicated(
            subset=["seller_id"]
        ).sum()
    })

    report.append({
        "Check": "Missing Revenue",
        "Count": sellers["annual_revenue"].isna().sum()
    })

    report.append({
        "Check": "Missing PAN Status",
        "Count": verification["pan_status"].isna().sum()
    })

    report.append({
        "Check": "Invalid Risk Score",
        "Count": fraud[
            (fraud["risk_score"] < 0) |
            (fraud["risk_score"] > 100)
        ].shape[0]
    })

    report.append({
        "Check": "Negative Sales",
        "Count": transactions[
            transactions["sales"] < 0
        ].shape[0]
    })

    quality_report = pd.DataFrame(report)

    output = EXPORT_DIR / "quality_report.csv"

    quality_report.to_csv(
        output,
        index=False
    )

    print("\nQuality Report")
    print("-" * 40)
    print(quality_report)
    print(f"\nSaved -> {output}")


if __name__ == "__main__":
    generate_quality_report()