
from pathlib import Path
import pandas as pd
import duckdb


def test_schema_sql_creates_expected_warehouse_tables(tmp_path):
    """Verify that the schema creates all six warehouse tables."""

    schema_file = Path("sql/schema.sql")
    database = tmp_path / "test_warehouse.duckdb"

    con = duckdb.connect(str(database))

    try:
        con.execute(schema_file.read_text(encoding="utf-8"))

        tables = {
            row[0]
            for row in con.execute(
                "SHOW TABLES"
            ).fetchall()
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
    finally:
        con.close()


def test_analytics_sql_loads_all_nine_queries():
    """Verify that all nine named analytics queries are loaded."""

    from app import analytics

    queries = analytics.load_queries()

    expected_queries = {
        "Total Sellers",
        "Revenue by Country",
        "Revenue by Business Type",
        "Top 10 High Risk Sellers",
        "Monthly Seller Registrations",
        "Refund Rate by Business Type",
        "Average Revenue by Industry",
        "Verification Status",
        "Country Verification Summary",
    }

    assert set(queries) == expected_queries
    assert all(query.strip().upper().startswith("SELECT")
               for query in queries.values())


def test_dimension_and_fact_sql_files_are_not_empty():
    """Verify that dimension and fact loading SQL files contain statements."""

    dimensions_sql = Path("sql/dimensions.sql").read_text(
        encoding="utf-8"
    )
    facts_sql = Path("sql/facts.sql").read_text(
        encoding="utf-8"
    )

    assert "insert into dim_country" in dimensions_sql.lower()
    assert "insert into dim_business" in dimensions_sql.lower()
    assert "insert into dim_date" in dimensions_sql.lower()
    assert "insert into dim_verification" in dimensions_sql.lower()
    assert "insert into dim_risk" in dimensions_sql.lower()
    assert "insert into fact_seller" in facts_sql.lower()


def test_run_query_executes_sql_and_exports_csv(tmp_path, monkeypatch):
    """Verify query execution and CSV export using an isolated database."""

    from app import analytics

    database = tmp_path / "test_analytics.duckdb"
    export_dir = tmp_path / "exports"
    export_dir.mkdir()

    con = duckdb.connect(str(database))
    try:
        con.execute(
            """
            CREATE TABLE test_sellers (
                seller_id INTEGER,
                annual_revenue DOUBLE
            )
            """
        )
        con.execute(
            """
            INSERT INTO test_sellers VALUES
                (1, 1000.0),
                (2, 2000.0),
                (3, 3000.0)
            """
        )
    finally:
        con.close()

    monkeypatch.setattr(analytics, "DATABASE", database)
    monkeypatch.setattr(analytics, "EXPORT_DIR", export_dir)

    result = analytics.run_query(
        "Test Total Sellers",
        "test_total_sellers.csv",
        "SELECT COUNT(*) AS total_sellers FROM test_sellers",
    )

    assert result.loc[0, "total_sellers"] == 3

    output_file = export_dir / "test_total_sellers.csv"
    assert output_file.exists()

    exported = pd.read_csv(output_file)
    assert exported.loc[0, "total_sellers"] == 3
