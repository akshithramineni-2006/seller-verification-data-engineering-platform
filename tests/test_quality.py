
from pathlib import Path

import pandas as pd

from app.quality import generate_quality_report


def test_validation_sql_contains_five_checks():
    """Ensure all five expected data quality checks are defined."""
    sql_file = Path("sql/validation.sql")
    sql = sql_file.read_text(encoding="utf-8")

    expected_checks = [
        "Duplicate Seller IDs",
        "Missing Revenue",
        "Missing PAN Status",
        "Invalid Risk Score",
        "Negative Sales",
    ]

    for check in expected_checks:
        assert check in sql


def test_quality_report_has_expected_checks():
    """Ensure the quality report contains all five validation checks."""
    generate_quality_report()

    report_path = Path("dashboard/exports/quality_report.csv")
    assert report_path.exists()

    report = pd.read_csv(report_path)

    expected_checks = {
        "Duplicate Seller IDs",
        "Missing Revenue",
        "Missing PAN Status",
        "Invalid Risk Score",
        "Negative Sales",
    }

    assert set(report["Check"]) == expected_checks


def test_current_silver_data_passes_quality_checks():
    """Verify that the current Silver data has no quality violations."""
    generate_quality_report()

    report_path = Path("dashboard/exports/quality_report.csv")
    report = pd.read_csv(report_path)

    assert len(report) == 5
    assert (report["Count"] == 0).all()


import duckdb


def run_validation_check(setup_sql, validation_sql):
    """Run one validation query against isolated in-memory test data."""
    con = duckdb.connect(":memory:")

    try:
        con.execute(setup_sql)
        result = con.execute(validation_sql).fetchone()
        return result[0], result[1]
    finally:
        con.close()


def test_duplicate_seller_ids_are_detected():
    check, count = run_validation_check(
        """
        CREATE TABLE sellers (
            seller_id INTEGER,
            annual_revenue DOUBLE
        );

        INSERT INTO sellers VALUES
            (1, 1000),
            (1, 2000),
            (2, 3000);
        """,
        """
        SELECT
            'Duplicate Seller IDs' AS "Check",
            COUNT(*) AS "Count"
        FROM (
            SELECT seller_id
            FROM sellers
            GROUP BY seller_id
            HAVING COUNT(*) > 1
        ) duplicates;
        """,
    )

    assert check == "Duplicate Seller IDs"
    assert count == 1


def test_missing_revenue_is_detected():
    check, count = run_validation_check(
        """
        CREATE TABLE sellers (
            seller_id INTEGER,
            annual_revenue DOUBLE
        );

        INSERT INTO sellers VALUES (1, NULL), (2, 5000);
        """,
        """
        SELECT 'Missing Revenue' AS "Check", COUNT(*) AS "Count"
        FROM sellers
        WHERE annual_revenue IS NULL;
        """,
    )

    assert check == "Missing Revenue"
    assert count == 1


def test_missing_pan_status_is_detected():
    check, count = run_validation_check(
        """
        CREATE TABLE verification (
            seller_id INTEGER,
            pan_status VARCHAR
        );

        INSERT INTO verification VALUES (1, NULL), (2, 'Verified');
        """,
        """
        SELECT 'Missing PAN Status' AS "Check", COUNT(*) AS "Count"
        FROM verification
        WHERE pan_status IS NULL;
        """,
    )

    assert check == "Missing PAN Status"
    assert count == 1


def test_invalid_risk_scores_are_detected():
    check, count = run_validation_check(
        """
        CREATE TABLE fraud (
            seller_id INTEGER,
            risk_score INTEGER
        );

        INSERT INTO fraud VALUES (1, -1), (2, 101), (3, 50);
        """,
        """
        SELECT 'Invalid Risk Score' AS "Check", COUNT(*) AS "Count"
        FROM fraud
        WHERE risk_score < 0 OR risk_score > 100;
        """,
    )

    assert check == "Invalid Risk Score"
    assert count == 2


def test_negative_sales_are_detected():
    check, count = run_validation_check(
        """
        CREATE TABLE transactions (
            seller_id INTEGER,
            sales DOUBLE
        );

        INSERT INTO transactions VALUES (1, -100), (2, 500), (3, 0);
        """,
        """
        SELECT 'Negative Sales' AS "Check", COUNT(*) AS "Count"
        FROM transactions
        WHERE sales < 0;
        """,
    )

    assert check == "Negative Sales"
    assert count == 1
