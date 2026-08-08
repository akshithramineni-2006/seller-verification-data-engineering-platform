from pathlib import Path

import duckdb
import pandas as pd

from app.config import SILVER_DATA
from app.logger import logger

DATABASE = Path("data/gold/warehouse.duckdb")

con = duckdb.connect(DATABASE)

def load_data():

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

    con.register("sellers", sellers)

    con.register("verification", verification)

    con.register("transactions", transactions)

    con.register("fraud", fraud)

    logger.info("Silver datasets registered.")
    
def create_schema():

    with open("sql/schema.sql") as f:

        con.execute(f.read())

    logger.info("Schema created.")

def build_country_dimension():

    con.execute("""

    INSERT INTO dim_country

    SELECT

        ROW_NUMBER() OVER(
            ORDER BY country
        ) AS country_key,

        country

    FROM

    (

        SELECT DISTINCT country

        FROM sellers

    );

    """)

    logger.info("Country dimension created.")
    
def build_business_dimension():

    con.execute("""

    INSERT INTO dim_business

    SELECT

        ROW_NUMBER() OVER(
            ORDER BY business_type
        ),

        business_type,

        industry

    FROM

    (

        SELECT DISTINCT

            business_type,

            industry

        FROM sellers

    );

    """)

    logger.info("Business dimension created.")
    
def build_date_dimension():

    con.execute("""

    INSERT INTO dim_date

    SELECT

        ROW_NUMBER() OVER(
            ORDER BY registration_date
        ),

        registration_date,

        YEAR(registration_date),

        MONTH(registration_date),

        DAY(registration_date)

    FROM

    (

        SELECT DISTINCT registration_date

        FROM sellers

    );

    """)

    logger.info("Date dimension created.")
    
def build_verification_dimension():

    con.execute("""

    INSERT INTO dim_verification

    SELECT

        ROW_NUMBER() OVER(

            ORDER BY verification_status

        ),

        verification_status,

        pan_status,

        gst_status,

        bank_status

    FROM

    (

        SELECT DISTINCT

            verification_status,

            pan_status,

            gst_status,

            bank_status

        FROM verification

    );

    """)

    logger.info("Verification dimension created.")
    
def build_risk_dimension():

    con.execute("""

    INSERT INTO dim_risk

    SELECT

        ROW_NUMBER() OVER(
            ORDER BY risk_score
        ),

        risk_score,

        fraud_flag

    FROM

    (

        SELECT DISTINCT

            risk_score,

            fraud_flag

        FROM fraud

    );

    """)

    logger.info("Risk dimension created.")
    
def build_fact_table():

    with open("sql/fact_load.sql", "r") as f:

        con.execute(f.read())

    logger.info("Fact table loaded.")

def validate_tables():

    tables = [

        "dim_country",

        "dim_business",

        "dim_date",

        "dim_verification",

        "dim_risk",

        "fact_seller"

    ]

    print("\nWarehouse Summary")

    print("-" * 30)

    for table in tables:

        count = con.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table:<20} {count}")
    
if __name__ == "__main__":

    create_schema()

    load_data()

    build_country_dimension()

    build_business_dimension()

    build_date_dimension()

    build_verification_dimension()

    build_risk_dimension()

    build_fact_table()

    validate_tables()

    print("\nWarehouse build completed.")