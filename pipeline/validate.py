import logging
from typing import Any, Dict, List
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

VALIDATION_CONFIG: Dict[str, Dict[str, Any]] = {
    "transactions": {
        "primary_keys": ["transaction_id"],
        "nullable_columns": ["notes"],
        "unique_columns": ["transaction_id"],
        "required_columns": [
            "transaction_id",
            "product_id",
            "distributor_id",
            "salesperson_id",
            "quantity",
            "unit_price_ngn",
            "discount_amount_ngn",
            "revenue_ngn",
            "cogs_ngn",
            "gross_profit_ngn",
            "transaction_date",
            "discount_pct",
            "payment_method",
            "transaction_status",
            "delivery_status",
        ],
        "greater_than_zero_columns": [
            "quantity",
            "unit_price_ngn",
            "revenue_ngn",
            "cogs_ngn",
            "gross_profit_ngn",
        ],
        "accepted_values": {
            "payment_method": ["cash", "credit", "transfer"],
            "delivery_status": ["delivered", "in_transit", "pending"],
            "transaction_status": ["completed", "pending", "returned"],
        },
    },

    "monthly_targets": {
        "primary_keys": ["record_id"],
        "required_columns": ["record_id", "salesperson_id", "year", "month"],
        "greater_than_zero_columns": ["target_revenue_ngn", "actual_revenue_ngn"],
        "nullable_columns": ["achievement_pct"],
    },

    "distributors": {
        "primary_keys": ["distributor_id"],
        "required_columns": [
            "distributor_id",
            "distributor_name",
            "region",
            "city",
            "outlet_type",
            "onboarding_date",
            "is_active",
        ],
        "unique_columns": ["distributor_id", "distributor_name"],
    },

    "products": {
        "primary_keys": ["product_id"],
        "required_columns": [
            "product_id",
            "product_name",
            "category",
            "unit_price_ngn",
            "unit_cost_ngn",
            "pack_size",
            "is_active",
        ],
        "greater_than_zero_columns": [
            "unit_price_ngn",
            "unit_cost_ngn",
            "pack_size",
        ],
    },

    "salespersons": {
        "primary_keys": ["salesperson_id"],
        "required_columns": [
            "salesperson_id",
            "salesperson_name",
            "region",
            "team",
            "hire_date",
            "monthly_target_ngn",
        ],
        "greater_than_zero_columns": ["monthly_target_ngn"],
    },

    "date_table": {
        "primary_keys": ["date"],
        "required_columns": [
            "date",
            "year",
            "quarter",
            "month",
            "month_name",
            "week",
            "day_of_week",
            "is_weekend",
            "is_month_end",
        ],
    },
}
RELATIONSHIP_CONFIG = [
    {
        "child_table": "transactions",
        "child_key": "product_id",
        "parent_table": "products",
        "parent_key": "product_id"
    },
    {
        "child_table": "transactions",
        "child_key": "salesperson_id",
        "parent_table": "salespersons",
        "parent_key": "salesperson_id"
    },
    {
        "child_table": "transactions",
        "child_key": "distributor_id",
        "parent_table": "distributors",
        "parent_key": "distributor_id"
    },
    {
        "child_table": "monthly_targets",
        "child_key": "salesperson_id",
        "parent_table": "salespersons",
        "parent_key": "salesperson_id"
    }
]
# let's get started with the validation sub-routines. :)

# validate required tables
def validate_required_tables(
    tables: Dict[str, pd.DataFrame], report: Dict[str, List[str]]) -> None:

    """ Checks if all required tables are present in the extracted data. """

    expected = set(VALIDATION_CONFIG.keys())
    extracted = set(tables.keys())

    # catch missing tables
    for table in (expected - extracted):
        report["errors"].append(f"Missing required table:[{table}]. Not found in Workbook.")
    # catch unexpected tables 
    for table in (extracted - expected):
        report["errors"].append(f"Unexpected table:[{table}]. Not defined in validation config.")

# validate table relationships    
def validate_relationships(
    tables: Dict[str, pd.DataFrame],
    report: Dict[str, List[str]]
) -> None:
    """
    Validates foreign-key relationships between tables.
    """

    for relation in RELATIONSHIP_CONFIG:

        child_df = tables.get(relation["child_table"])
        parent_df = tables.get(relation["parent_table"])

        if child_df is None or parent_df is None:
            continue

        child_key = relation["child_key"]
        parent_key = relation["parent_key"]

        if child_key not in child_df.columns or parent_key not in parent_df.columns:
            continue

        invalid_rows = (
            ~child_df[child_key]
            .dropna()
            .isin(parent_df[parent_key])
        ).sum()

        if invalid_rows > 0:
            report["errors"].append(
                f"[{relation['child_table']}]: "
                f"{invalid_rows} invalid {child_key} value(s) "
                f"not found in {relation['parent_table']}.{parent_key}."
            )

# validate required columns
def validate_required_columns(
    sheet_name: str, df: pd.DataFrame, config: Dict[str, Any], 
    report: Dict[str, List[str]]) -> None:

    """ Checks that all the required columns are present in DF for each sheet. """
    expected_cols = set(config.get("required_columns", []))
    expected_cols.update(config.get("primary_keys", []))
    expected_cols.update(config.get("unique_columns", []))
    expected_cols.update(config.get("greater_than_zero_columns", []))
    expected_cols.update(config.get("accepted_values", {}).keys())
    
    for col in expected_cols:
        if col not in df.columns:
            report["errors"].append(f"[{sheet_name}]: Missing required column:[{col}].")

# validate primary keys
def validate_primary_keys(
    sheet_name: str, df: pd.DataFrame, config: Dict[str, Any],
    report: Dict[str, List[str]]) -> None:

    """ Checks that the primary key columns are unique and not null. """
    primary_keys = config.get("primary_keys", [])
    if not primary_keys:
        return

    # check for presence before validating
    existing_pks = [pk for pk in primary_keys if pk in df.columns]
    if len(existing_pks) != len(primary_keys):
        return

    # check for nulls
    for pk in existing_pks:
        null_count = int(df[pk].isnull().sum())
        if null_count > 0:
            report["errors"].append(f"[{sheet_name}]: Primary key column '{pk}' contains null values.")
    
    # check for duplicates
    dup_count = int(df.duplicated(subset=existing_pks).sum())
    if dup_count > 0:
        if len(existing_pks) > 1:
            report["errors"].append(f"[{sheet_name}]: Duplicate primary key combination detected. Found {dup_count} duplicated row(s).")
        else:
            report["errors"].append(f"[{sheet_name}]: Primary key column '{existing_pks[0]}' contains {dup_count} duplicate values.")

# validate positive values
def validate_positive_values(
    sheet_name:str, df: pd.DataFrame, config: Dict[str, Any], report: Dict[str, List[str]]) -> None:
    
    """ Checks that specified columns have values greater than zero. """
    positive_cols = config.get("greater_than_zero_columns", [])
    for col in positive_cols:
        if col in df.columns:
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            invalid_rows = int((numeric_series <= 0).sum())
            if invalid_rows > 0:
                report["errors"].append(
                    f"[{sheet_name}]: Column '{col}' contains {invalid_rows} rows with values less than or equal to zero."
                )
# validate accepted values
def validate_accepted_values(
    sheet_name:str, df: pd.DataFrame, config: Dict[str, Any], report: Dict[str, List[str]]) -> None:
    
    """ Checks that specified columns have values within the accepted set. """
    accepted_values_config = config.get("accepted_values", {})
    for col, accepted_values in accepted_values_config.items():
        if col in df.columns:
            invalid_rows = int((~df[col].isin(accepted_values)).sum())
            if invalid_rows > 0:
                report["errors"].append(
                    f"[{sheet_name}]: Column '{col}' contains {invalid_rows} rows with values outside the accepted set: {accepted_values}."
                )

# orchestrate all validations
def generate_report(tables: Dict[str, pd.DataFrame]) -> Dict[str, List[str]]:
    report: Dict[str, List[str]] = {
        "errors": [], 
        "warnings": []
    }
    
    logger.info("Starting validation checks...")

    # check for required tables
    validate_required_tables(tables, report)
    validate_relationships(tables, report)
    # validate each table's columns and constraints
    for sheet_name, df in tables.items():

        if sheet_name not in VALIDATION_CONFIG:
            continue  # Skip validation for unknown tables
        config = VALIDATION_CONFIG[sheet_name]

        validate_required_columns(sheet_name, df, config, report)
        validate_primary_keys(sheet_name, df, config, report)
        validate_positive_values(sheet_name, df, config, report)
        validate_accepted_values(sheet_name, df, config, report)
    error_count = len(report["errors"])
    warning_count = len(report["warnings"])

    if error_count == 0:
        logger.info(f"Validation completed successfully. | Errors: {error_count} | Warnings: {warning_count}")
    else:
        logger.warning(f"Validation completed with exceptions. | Errors: {error_count} | Warnings: {warning_count}")

    return report
