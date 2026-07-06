import pandas as pd

from pipeline.transform import transform_tables


def test_transform_tables_cleans_and_derives_fields():
    tables = {
        "transactions": pd.DataFrame(
            [
                {
                    "transaction_id": " TXN001 ",
                    "transaction_date": pd.Timestamp("2025-06-27"),
                    "product_id": " PROD1 ",
                    "distributor_id": " DIST1 ",
                    "salesperson_id": " SP1 ",
                    "quantity": "10",
                    "unit_price_ngn": "200",
                    "discount_pct": "5",
                    "discount_amount_ngn": "10",
                    "revenue_ngn": "1900",
                    "cogs_ngn": "1000",
                    "gross_profit_ngn": "900",
                    "payment_method": " Cash ",
                    "delivery_status": " Delivered ",
                    "transaction_status": " Completed ",
                    "notes": "  ",
                }
            ]
        ),
        "monthly_targets": pd.DataFrame(
            [
                {
                    "record_id": " TGT001 ",
                    "salesperson_id": " SP1 ",
                    "year": 2024,
                    "month": 1,
                    "target_revenue_ngn": 1000,
                    "actual_revenue_ngn": 500,
                    "achievement_pct": None,
                }
            ]
        ),
        "products": pd.DataFrame(
            [
                {
                    "product_id": " PROD1 ",
                    "product_name": "  Sample Drink  ",
                    "category": " Beverages ",
                    "unit_price_ngn": "350",
                    "unit_cost_ngn": "200",
                    "pack_size": "12",
                    "is_active": "TRUE",
                }
            ]
        ),
        "date_table": pd.DataFrame(
            [
                {"year": 2024, "month": 1},
                {"year": 2024, "month": 2},
            ]
        ),
    }

    transformed = transform_tables(tables)

    tx = transformed["transactions"]
    assert tx["transaction_id"].iloc[0] == "TXN001"
    assert tx["transaction_date"].iloc[0] == pd.Timestamp("2025-06-27")
    assert pd.api.types.is_datetime64_any_dtype(tx["transaction_date"])
    assert tx["payment_method"].iloc[0] == "cash"
    assert tx["delivery_status"].iloc[0] == "delivered"
    assert tx["transaction_status"].iloc[0] == "completed"
    assert pd.isna(tx["notes"].iloc[0])
    assert tx["quantity"].dtype.kind in {"i", "u", "f"}

    targets = transformed["monthly_targets"]
    assert targets["achievement_pct"].iloc[0] == 50.0

    products = transformed["products"]
    assert products["product_name"].iloc[0] == "Sample Drink"
    assert products["category"].iloc[0] == "beverages"
    assert pd.api.types.is_bool_dtype(products["is_active"])

    date_table = transformed["date_table"]
    assert date_table["date"].iloc[0] == pd.Timestamp("2024-01-01")
    assert date_table["date"].iloc[1] == pd.Timestamp("2024-02-01")
