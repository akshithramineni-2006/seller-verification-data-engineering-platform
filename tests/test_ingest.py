
import pandas as pd

from app import ingest


def test_ingest_file_converts_csv_to_parquet(tmp_path, monkeypatch):
    """Verify that ingestion converts CSV data into Parquet correctly."""

    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"

    raw_dir.mkdir()
    bronze_dir.mkdir()

    sample = pd.DataFrame(
        {
            "seller_id": [101, 102, 103],
            "country": ["India", "USA", "Germany"],
            "annual_revenue": [10000, 20000, 30000],
        }
    )

    sample.to_csv(raw_dir / "sellers.csv", index=False)

    monkeypatch.setattr(ingest, "RAW_DATA", raw_dir)
    monkeypatch.setattr(ingest, "BRONZE_DATA", bronze_dir)

    ingest.ingest_file("sellers.csv")

    output_file = bronze_dir / "sellers.parquet"

    assert output_file.exists()

    result = pd.read_parquet(output_file)

    pd.testing.assert_frame_equal(result, sample)


def test_ingest_file_preserves_row_count(tmp_path, monkeypatch):
    """Verify that ingestion preserves the input row count."""

    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"

    raw_dir.mkdir()
    bronze_dir.mkdir()

    sample = pd.DataFrame(
        {
            "seller_id": [201, 202, 203, 204, 205],
            "annual_revenue": [100, 200, 300, 400, 500],
        }
    )

    sample.to_csv(raw_dir / "sample.csv", index=False)

    monkeypatch.setattr(ingest, "RAW_DATA", raw_dir)
    monkeypatch.setattr(ingest, "BRONZE_DATA", bronze_dir)

    ingest.ingest_file("sample.csv")

    result = pd.read_parquet(bronze_dir / "sample.parquet")

    assert len(result) == len(sample)
