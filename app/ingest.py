import pandas as pd

from app.config import RAW_DATA, BRONZE_DATA
from app.logger import logger

def ingest_file(file_name):

    csv_path = RAW_DATA / file_name

    parquet_path = BRONZE_DATA / file_name.replace(".csv", ".parquet")

    df = pd.read_csv(csv_path)

    logger.info(f"Loaded {file_name}")

    df.to_parquet(
        parquet_path,
        index=False
    )

    logger.info(
        f"Saved {parquet_path.name}"
    )

    print(f"{file_name} completed")
    
if __name__ == "__main__":

    files = [

        "sellers.csv",

        "verification.csv",

        "transactions.csv",

        "login_activity.csv",

        "fraud_events.csv"

    ]

    for file in files:

        ingest_file(file)

    print("\nBronze layer completed.")