import logging
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _clean_text_series(series: pd.Series) -> pd.Series:
    """Trim whitespace and normalize empty values for text-like columns."""
    if pd.api.types.is_bool_dtype(series) or pd.api.types.is_numeric_dtype(series):
        return series

    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "none": pd.NA, "null": pd.NA})
    return cleaned.astype("object")


def _coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert numeric-looking columns to numeric dtype without rejecting rows."""
    for column in df.columns:
        if column in {"is_active", "is_weekend", "is_month_end"}:
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            continue

        if pd.api.types.is_datetime64_any_dtype(df[column]) or pd.api.types.is_timedelta64_dtype(df[column]):
            continue

        converted = pd.to_numeric(df[column], errors="coerce")
        if converted.notna().any():
            df[column] = converted

    return df


def _coerce_boolean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert common boolean-like columns to boolean dtype."""
    for column in [col for col in df.columns if col.startswith("is_") or col in {"is_active"}]:
        if pd.api.types.is_bool_dtype(df[column]):
            continue

        cleaned = df[column].astype("string").str.strip().str.lower()
        mapping = {
            "true": True,
            "false": False,
            "1": True,
            "0": False,
            "yes": True,
            "no": False,
        }
        df[column] = cleaned.map(mapping).astype("boolean")

    return df


def _standardize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim values and standardize commonly used text fields."""
    lowercase_columns = {
        "payment_method",
        "delivery_status",
        "transaction_status",
        "category",
        "region",
        "city",
        "outlet_type",
        "team",
        "month_name",
        "day_of_week",
    }

    for column in df.columns:
        if column in df.select_dtypes(exclude=["number", "bool", "datetime"]).columns:
            cleaned = _clean_text_series(df[column])
            if column in lowercase_columns:
                cleaned = cleaned.str.lower()
            df[column] = cleaned

    return df


def _transform_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = _standardize_text_columns(df)
    df = _coerce_numeric_columns(df)
    df = _coerce_boolean_columns(df)

    accepted_value_mapping = {
        "payment_method": {"cash": "cash", "credit": "credit", "transfer": "transfer"},
        "delivery_status": {"delivered": "delivered", "in transit": "in_transit", "pending": "pending"},
        "transaction_status": {"completed": "completed", "pending": "pending", "returned": "returned"},
    }

    for column, mapping in accepted_value_mapping.items():
        if column in df.columns:
            df[column] = df[column].map(
                lambda value: mapping.get(str(value).strip().lower(), str(value).strip().lower())
            )

    for column in ["transaction_date", "onboarding_date", "hire_date", "date"]:
        if column in df.columns:
            parsed = pd.to_datetime(df[column], errors="coerce")
            if parsed.notna().any():
                df[column] = parsed.dt.tz_localize(None) if getattr(parsed.dt, "tz", None) is not None else parsed
            else:
                df[column] = parsed

    return df


def _transform_monthly_targets(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = _standardize_text_columns(df)
    df = _coerce_numeric_columns(df)

    required_columns = {"achievement_pct", "target_revenue_ngn", "actual_revenue_ngn"}
    if required_columns.issubset(df.columns):
        target_revenue = pd.to_numeric(df["target_revenue_ngn"], errors="coerce")
        actual_revenue = pd.to_numeric(df["actual_revenue_ngn"], errors="coerce")
        missing_achievement = df["achievement_pct"].isna()
        derived_achievement = (actual_revenue / target_revenue * 100).where(
            (target_revenue.notna()) & (target_revenue != 0) & missing_achievement,
            pd.NA,
        )
        df["achievement_pct"] = df["achievement_pct"].where(~missing_achievement, derived_achievement)

    return df


def _derive_date_from_year_month(df: pd.DataFrame) -> pd.DataFrame:
    """Create a date column from year/month values when needed for calendar-like tables."""
    if "year" in df.columns and "month" in df.columns:
        if "date" not in df.columns or df["date"].isna().all():
            df = df.copy()
            df["date"] = pd.to_datetime(
                df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01",
                errors="coerce",
            )

    return df


def _transform_dimension_tables(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = _standardize_text_columns(df)
    df = _coerce_numeric_columns(df)
    df = _coerce_boolean_columns(df)
    df = _derive_date_from_year_month(df)

    for column in ["onboarding_date", "hire_date", "date"]:
        if column in df.columns:
            parsed = pd.to_datetime(df[column], errors="coerce")
            if parsed.notna().any():
                df[column] = parsed.dt.tz_localize(None) if getattr(parsed.dt, "tz", None) is not None else parsed
            else:
                df[column] = parsed

    return df


def transform_tables(tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Clean and standardize each extracted table without rejecting records."""
    transformed_tables: Dict[str, pd.DataFrame] = {}

    for table_name, df in tables.items():
        if table_name == "transactions":
            transformed_tables[table_name] = _transform_transactions(df)
        elif table_name == "monthly_targets":
            transformed_tables[table_name] = _transform_monthly_targets(df)
        elif table_name in {"products", "distributors", "salespersons", "date_table"}:
            transformed_tables[table_name] = _transform_dimension_tables(df)
        else:
            transformed_tables[table_name] = df.copy()

    logger.info("Applied transformation cleaning to %s table(s).", len(transformed_tables))
    return transformed_tables
