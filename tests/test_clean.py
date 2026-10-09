
import pandas as pd

from app import clean


def test_clean_transactions_clips_negative_values(tmp_path, monkeypatch):
    """Negative transaction values should become zero."""

    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()
    silver_dir.mkdir()

    sample = pd.DataFrame(
        {
            "orders": [-2, 5],
            "sales": [-100.0, 500.0],
            "returns": [-1, 2],
            "refunds": [-50.0, 25.0],
        }
    )

    sample.to_parquet(bronze_dir / "transactions.parquet", index=False)

    monkeypatch.setattr(clean, "BRONZE_DATA", bronze_dir)
    monkeypatch.setattr(clean, "SILVER_DATA", silver_dir)

    clean.clean_transactions()

    result = pd.read_parquet(silver_dir / "transactions.parquet")

    assert (result[["orders", "sales", "returns", "refunds"]] >= 0).all().all()
    assert result.loc[0, "sales"] == 0


def test_clean_login_clips_negative_failed_logins(tmp_path, monkeypatch):
    """Negative failed-login counts should become zero."""

    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()
    silver_dir.mkdir()

    sample = pd.DataFrame({"failed_logins": [-3, 0, 4]})
    sample.to_parquet(bronze_dir / "login_activity.parquet", index=False)

    monkeypatch.setattr(clean, "BRONZE_DATA", bronze_dir)
    monkeypatch.setattr(clean, "SILVER_DATA", silver_dir)

    clean.clean_login()

    result = pd.read_parquet(silver_dir / "login_activity.parquet")

    assert result["failed_logins"].tolist() == [0, 0, 4]


def test_clean_fraud_clips_risk_scores_to_zero_through_100(
    tmp_path, monkeypatch
):
    """Risk scores below 0 or above 100 should be clipped."""

    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()
    silver_dir.mkdir()

    sample = pd.DataFrame({"risk_score": [-10, 50, 120]})
    sample.to_parquet(bronze_dir / "fraud_events.parquet", index=False)

    monkeypatch.setattr(clean, "BRONZE_DATA", bronze_dir)
    monkeypatch.setattr(clean, "SILVER_DATA", silver_dir)

    clean.clean_fraud()

    result = pd.read_parquet(silver_dir / "fraud_events.parquet")

    assert result["risk_score"].tolist() == [0, 50, 100]


def test_clean_sellers_standardizes_and_cleans_data(tmp_path, monkeypatch):
    """Verify seller deduplication, country mapping, revenue filling and dates."""

    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()
    silver_dir.mkdir()

    sample = pd.DataFrame(
        {
            "seller_id": [1, 1, 2],
            "country": ["INDIA", "USA", "IN"],
            "annual_revenue": [1000.0, 9999.0, None],
            "registration_date": [
                "2025-01-01",
                "2025-01-02",
                "2025-01-03",
            ],
        }
    )

    sample.to_parquet(bronze_dir / "sellers.parquet", index=False)

    monkeypatch.setattr(clean, "BRONZE_DATA", bronze_dir)
    monkeypatch.setattr(clean, "SILVER_DATA", silver_dir)

    clean.clean_sellers()

    result = pd.read_parquet(silver_dir / "sellers.parquet")

    assert len(result) == 2
    assert result["seller_id"].is_unique
    assert result.loc[result["seller_id"] == 1, "country"].iloc[0] == "India"
    assert result.loc[result["seller_id"] == 2, "country"].iloc[0] == "India"
    assert result["annual_revenue"].isna().sum() == 0
    assert pd.api.types.is_datetime64_any_dtype(result["registration_date"])


def test_clean_verification_fills_missing_status_and_removes_duplicates(
    tmp_path, monkeypatch
):
    """Verify PAN status filling, deduplication and date conversion."""

    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()
    silver_dir.mkdir()

    sample = pd.DataFrame(
        {
            "verification_id": [101, 101, 102],
            "pan_status": ["Verified", "Rejected", None],
            "verification_date": [
                "2025-02-01",
                "2025-02-02",
                "2025-02-03",
            ],
        }
    )

    sample.to_parquet(bronze_dir / "verification.parquet", index=False)

    monkeypatch.setattr(clean, "BRONZE_DATA", bronze_dir)
    monkeypatch.setattr(clean, "SILVER_DATA", silver_dir)

    clean.clean_verification()

    result = pd.read_parquet(silver_dir / "verification.parquet")

    assert len(result) == 2
    assert result["verification_id"].is_unique
    assert result.loc[
        result["verification_id"] == 102, "pan_status"
    ].iloc[0] == "Unknown"
    assert pd.api.types.is_datetime64_any_dtype(result["verification_date"])
