import pandas as pd

from app.config import BRONZE_DATA, SILVER_DATA
from app.logger import logger


def read_parquet(file_name):
    return pd.read_parquet(BRONZE_DATA / file_name)


def save_parquet(df, file_name):
    df.to_parquet(SILVER_DATA / file_name, index=False)
    logger.info(f"Saved cleaned file: {file_name}")


def clean_sellers():
    df = read_parquet("sellers.parquet")

    df = df.drop_duplicates(subset=["seller_id"])

    country_map = {
        "INDIA": "India",
        "india": "India",
        "IN": "India"
    }

    df["country"] = df["country"].replace(country_map)

    median_revenue = df["annual_revenue"].median()

    df["annual_revenue"] = df["annual_revenue"].fillna(median_revenue)
    
    df["registration_date"] = pd.to_datetime(
      df["registration_date"]
      )
    
    save_parquet(df, "sellers.parquet")


def clean_verification():

    df = read_parquet("verification.parquet")

    df["pan_status"] = df["pan_status"].fillna("Unknown")

    df = df.drop_duplicates(
        subset=["verification_id"]
    )
    
    df["verification_date"] = pd.to_datetime(
      df["verification_date"]
    )
    
    save_parquet(df, "verification.parquet")


def clean_transactions():

    df = read_parquet("transactions.parquet")

    numeric_cols = [
        "orders",
        "sales",
        "returns",
        "refunds"
    ]

    for col in numeric_cols:

        df[col] = df[col].clip(lower=0)

    save_parquet(df, "transactions.parquet")


def clean_login():

    df = read_parquet("login_activity.parquet")

    df["failed_logins"] = df[
        "failed_logins"
    ].clip(lower=0)

    save_parquet(df, "login_activity.parquet")


def clean_fraud():

    df = read_parquet("fraud_events.parquet")

    df["risk_score"] = df[
        "risk_score"
    ].clip(0,100)

    save_parquet(df, "fraud_events.parquet")


if __name__ == "__main__":

    clean_sellers()

    clean_verification()

    clean_transactions()

    clean_login()

    clean_fraud()

    print("Silver layer completed.")