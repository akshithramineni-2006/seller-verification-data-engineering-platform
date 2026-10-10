
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


def test_run_stage_logs_success(monkeypatch, caplog):
    import logging

    from app import run_pipeline

    def successful_subprocess(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0)

    monkeypatch.setattr(
        run_pipeline.subprocess,
        "run",
        successful_subprocess,
    )

    with caplog.at_level(logging.INFO, logger="pipeline"):
        duration = run_pipeline.run_stage(
            1,
            6,
            "TEST STAGE",
            "app.test_module",
        )

    assert duration >= 0
    assert "Stage 1/6 started: TEST STAGE" in caplog.text
    assert "Stage 1/6 succeeded: TEST STAGE" in caplog.text


def test_run_stage_logs_failure(monkeypatch, caplog):
    import logging

    from app import run_pipeline

    def failed_subprocess(*args, **kwargs):
        raise subprocess.CalledProcessError(
            2,
            args[0],
        )

    monkeypatch.setattr(
        run_pipeline.subprocess,
        "run",
        failed_subprocess,
    )

    with caplog.at_level(logging.ERROR, logger="pipeline"):
        try:
            run_pipeline.run_stage(
                2,
                6,
                "FAILING STAGE",
                "app.test_module",
            )
        except subprocess.CalledProcessError as error:
            assert error.returncode == 2
        else:
            raise AssertionError("Expected stage failure")

    assert "Stage 2/6 failed: FAILING STAGE" in caplog.text
    assert "exit_code=2" in caplog.text


def test_main_stops_when_stage_fails(monkeypatch, caplog):
    import logging

    from app import run_pipeline

    def fake_run_stage(index, total, name, module):
        if index == 2:
            raise subprocess.CalledProcessError(1, module)
        return 0.5

    monkeypatch.setattr(
        run_pipeline,
        "run_stage",
        fake_run_stage,
    )

    with caplog.at_level(logging.ERROR, logger="pipeline"):
        try:
            run_pipeline.main()
        except subprocess.CalledProcessError:
            pass
        else:
            raise AssertionError("Expected pipeline failure")

    assert "Pipeline failed" in caplog.text
    assert "completed_stages=1/6" in caplog.text
