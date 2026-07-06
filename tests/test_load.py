import duckdb
import pandas as pd

from pipeline.load import load_tables


def test_load_tables_writes_dataframes_to_duckdb(tmp_path):
    tables = {
        "products": pd.DataFrame(
            [{"product_id": "P1", "product_name": "Sample"}]
        ),
        "transactions": pd.DataFrame(
            [{"transaction_id": "T1", "quantity": 2, "revenue_ngn": 100.0}]
        ),
    }

    output_path = tmp_path / "warehouse.duckdb"

    load_tables(tables=tables, destination=output_path)

    conn = duckdb.connect(output_path)
    try:
        products = conn.execute("SELECT * FROM products").fetchdf()
        transactions = conn.execute("SELECT * FROM transactions").fetchdf()
    finally:
        conn.close()

    assert len(products) == 1
    assert products.iloc[0]["product_name"] == "Sample"
    assert len(transactions) == 1
    assert transactions.iloc[0]["quantity"] == 2
