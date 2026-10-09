
import shutil
import subprocess
import sys
from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_complete_pipeline_runs_in_isolated_project(tmp_path):
    # Copy the project so the test cannot overwrite the real data.
    isolated_project = tmp_path / "seller-verification-test"

    shutil.copytree(
        PROJECT_ROOT,
        isolated_project,
        ignore=shutil.ignore_patterns(
            ".git",
            ".pytest_cache",
            "__pycache__",
            "venv",
            ".venv",
            "*.pyc",
        ),
    )

    # Execute all six pipeline stages in the isolated copy.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.run_pipeline",
        ],
        cwd=isolated_project,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, (
        f"Pipeline failed.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    assert "PIPELINE COMPLETED SUCCESSFULLY" in result.stdout

    # Verify the warehouse tables and seller count.
    database = (
        isolated_project / "data" / "gold" / "warehouse.duckdb"
    )

    assert database.exists()

    con = duckdb.connect(str(database), read_only=True)

    try:
        tables = {
            row[0]
            for row in con.execute("SHOW TABLES").fetchall()
        }

        expected_tables = {
            "dim_country",
            "dim_business",
            "dim_date",
            "dim_verification",
            "dim_risk",
            "fact_seller",
        }

        assert expected_tables.issubset(tables)

        seller_count = con.execute(
            "SELECT COUNT(*) FROM fact_seller"
        ).fetchone()[0]

        assert seller_count == 10000

    finally:
        con.close()

    # Verify that all nine analytics exports were generated.
    export_dir = isolated_project / "dashboard" / "exports"

    expected_exports = {
        "total_sellers.csv",
        "revenue_by_country.csv",
        "revenue_by_business.csv",
        "high_risk_sellers.csv",
        "monthly_registrations.csv",
        "refund_rate.csv",
        "industry_revenue.csv",
        "verification_status.csv",
        "country_verification.csv",
        "quality_report.csv",
    }

    for filename in expected_exports:
        assert (export_dir / filename).exists(), (
            f"Missing export: {filename}"
        )

    # Verify that all five quality checks report zero issues.
    quality_report = pd.read_csv(
        export_dir / "quality_report.csv"
    )

    assert len(quality_report) == 5
    assert (quality_report["Count"] == 0).all()
