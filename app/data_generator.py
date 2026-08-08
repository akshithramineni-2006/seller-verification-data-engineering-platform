import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from app.config import RAW_DATA

fake = Faker()

random.seed(42)
np.random.seed(42)
Faker.seed(42)

NUM_SELLERS = 10000

COUNTRIES = [
    "India",
    "USA",
    "UK",
    "Germany",
    "Canada",
    "Australia",
    "Singapore"
]

BUSINESS_TYPES = [
    "Individual",
    "Private Limited",
    "LLP",
    "Partnership",
    "Sole Proprietor"
]

INDUSTRIES = [
    "Electronics",
    "Fashion",
    "Books",
    "Beauty",
    "Sports",
    "Automotive",
    "Home"
]

def random_date():

    start = datetime(2022, 1, 1)
    end = datetime(2026, 7, 31)

    delta = end - start

    return start + timedelta(
        days=random.randint(0, delta.days)
    )

def generate_sellers():

    records = []

    for i in range(NUM_SELLERS):

        records.append({

            "seller_id": f"S{i+100001}",

            "seller_name": fake.company(),

            "country": random.choice(COUNTRIES),

            "business_type": random.choice(BUSINESS_TYPES),

            "industry": random.choice(INDUSTRIES),

            "registration_date": random_date(),

            "annual_revenue": random.randint(
                50000,
                10000000
            )

        })

    sellers = pd.DataFrame(records)

    duplicate_rows = sellers.sample(50)

    sellers = pd.concat(
        [sellers, duplicate_rows],
        ignore_index=True
    )

    sellers.loc[
        sellers.sample(100).index,
        "annual_revenue"
    ] = np.nan

    sellers.loc[
        sellers.sample(80).index,
        "country"
    ] = "INDIA"

    sellers.loc[
        sellers.sample(60).index,
        "country"
    ] = "india"

    sellers.loc[
        sellers.sample(40).index,
        "country"
    ] = "IN"

    return sellers

def generate_verification(sellers):

    records = []

    for seller_id in sellers["seller_id"].unique():

        verification_date = random_date()

        status = random.choices(
            ["Approved", "Rejected", "Pending"],
            weights=[80, 10, 10],
            k=1
        )[0]

        records.append({

            "verification_id": fake.uuid4(),

            "seller_id": seller_id,

            "pan_status": random.choice(
                ["Verified", "Failed"]
            ),

            "gst_status": random.choice(
                ["Verified", "Failed"]
            ),

            "bank_status": random.choice(
                ["Verified", "Failed"]
            ),

            "verification_status": status,

            "verification_date": verification_date

        })

    verification = pd.DataFrame(records)

    verification.loc[
        verification.sample(50).index,
        "pan_status"
    ] = None

    return verification

def generate_transactions(sellers):

    records = []

    for seller_id in sellers["seller_id"].unique():

        orders = random.randint(0, 500)

        sales = orders * random.randint(400, 2500)

        returns = random.randint(
            0,
            max(orders // 5, 1)
        )

        refunds = returns * random.randint(
            300,
            2000
        )

        records.append({

            "seller_id": seller_id,

            "orders": orders,

            "sales": sales,

            "returns": returns,

            "refunds": refunds

        })

    return pd.DataFrame(records)

def generate_login_activity(sellers):

    records = []

    devices = [
        "Desktop",
        "Mobile",
        "Tablet"
    ]

    for seller_id in sellers["seller_id"].unique():

        records.append({

            "seller_id": seller_id,

            "last_login": random_date(),

            "device": random.choice(devices),

            "failed_logins": random.randint(0, 8),

            "ip_country": random.choice(COUNTRIES)

        })

    return pd.DataFrame(records)

def generate_fraud_events(sellers):

    records = []

    for seller_id in sellers["seller_id"].unique():

        risk = random.randint(1, 100)

        records.append({

            "seller_id": seller_id,

            "fraud_flag": risk > 85,

            "risk_score": risk,

            "fraud_reason": random.choice([

                "Multiple Accounts",

                "Document Mismatch",

                "Fake Address",

                "None"

            ])

        })

    return pd.DataFrame(records)

def save_csv(df, filename):

    output = RAW_DATA / filename

    df.to_csv(output, index=False)

    print(f"{filename} saved successfully")
    
if __name__ == "__main__":

    sellers = generate_sellers()

    verification = generate_verification(sellers)

    transactions = generate_transactions(sellers)

    login = generate_login_activity(sellers)

    fraud = generate_fraud_events(sellers)

    save_csv(sellers, "sellers.csv")

    save_csv(verification, "verification.csv")

    save_csv(transactions, "transactions.csv")

    save_csv(login, "login_activity.csv")

    save_csv(fraud, "fraud_events.csv")
    
