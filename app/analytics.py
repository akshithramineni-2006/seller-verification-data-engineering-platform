from pathlib import Path

EXPORT_DIR = Path("dashboard/exports")

EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)
import duckdb
import pandas as pd
from pathlib import Path

DATABASE = Path("data/gold/warehouse.duckdb")

con = duckdb.connect(DATABASE)


from pathlib import Path

EXPORT_DIR = Path("dashboard") / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_query(title, filename, query):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    df = con.execute(query).fetchdf()

    print(df)

    output = EXPORT_DIR / filename

    df.to_csv(output, index=False)

    print(f"\nSaved -> {output}")

    return df


if __name__ == "__main__":

    run_query(
        "Total Sellers",
        "total_sellers.csv",
        """
        SELECT COUNT(*) AS total_sellers
        FROM fact_seller;
        """
    )

    run_query(
        "Revenue by Country",
        "revenue_by_country.csv",
        """
        SELECT

            c.country_name,

            SUM(f.sales) total_sales

        FROM fact_seller f

        JOIN dim_country c

        ON f.country_key = c.country_key

        GROUP BY c.country_name

        ORDER BY total_sales DESC;
        """
    )

    run_query(
        "Revenue by Business Type",
        "revenue_by_business.csv",
        """
        SELECT

            b.business_type,

            SUM(f.sales) total_sales

        FROM fact_seller f

        JOIN dim_business b

        ON f.business_key = b.business_key

        GROUP BY b.business_type

        ORDER BY total_sales DESC;
        """
    )

    run_query(
        "Top 10 High Risk Sellers",
        "high_risk_sellers.csv",
        """
        SELECT

            seller_id,

            risk_score

        FROM fact_seller f

        JOIN dim_risk r

        ON f.risk_key = r.risk_key

        ORDER BY risk_score DESC

        LIMIT 10;
        """
    )
    
    run_query(

    "Monthly Seller Registrations",

    "monthly_registrations.csv",

    """

    SELECT

        d.year,

        d.month,

        COUNT(*) AS sellers

    FROM fact_seller f

    JOIN dim_date d

    ON f.date_key = d.date_key

    GROUP BY

        d.year,

        d.month

    ORDER BY

        d.year,

        d.month;

    """

)
    
    run_query(

    "Refund Rate",

    "refund_rate.csv",

    """

    SELECT

        b.business_type,

        SUM(refunds) AS refunds,

        SUM(sales) AS sales,

        ROUND(

            (SUM(refunds) * 100.0) /

            NULLIF(SUM(sales),0),

            2

        ) AS refund_percentage

    FROM fact_seller f

    JOIN dim_business b

    ON f.business_key = b.business_key

    GROUP BY

        b.business_type

    ORDER BY

        refund_percentage DESC;

    """

)
    
    run_query(
    "Average Revenue by Industry",
    "industry_revenue.csv",
    """
    SELECT

        b.industry,

        ROUND(
            AVG(f.annual_revenue),
            2
        ) AS avg_revenue

    FROM fact_seller f

    JOIN dim_business b

    ON f.business_key = b.business_key

    GROUP BY b.industry

    ORDER BY avg_revenue DESC;
    """
)
   
run_query(
    "Verification Status",
    "verification_status.csv",
    """
    SELECT
        dv.verification_status,
        COUNT(*) AS seller_count
    FROM fact_seller f
    JOIN dim_verification dv
        ON f.verification_key = dv.verification_key
    GROUP BY dv.verification_status
    ORDER BY seller_count DESC;
    """
)
    
run_query(
    "Country Verification Summary",
    "country_verification.csv",
    """
    SELECT
        dc.country_name,
        dv.verification_status,
        COUNT(*) AS seller_count
    FROM fact_seller f
    JOIN dim_country dc
        ON f.country_key = dc.country_key
    JOIN dim_verification dv
        ON f.verification_key = dv.verification_key
    GROUP BY
        dc.country_name,
        dv.verification_status
    ORDER BY
        dc.country_name,
        seller_count DESC;
    """
)