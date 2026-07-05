import os
import numpy as np
import pandas as pd


def report_shape(df):
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")


def report_columns(df):
    print("\nColumns")
    for col in df.columns:
        print(f"  • {col}")


def report_dtypes(df):
    print("\nData Types")
    print(df.dtypes)


def report_missing(df):
    print("\nMissing Values")

    missing = df.isna().sum()

    if missing.sum() == 0:
        print("None")
        return

    missing_pct = (missing / len(df) * 100).round(2)

    report = pd.DataFrame({
        "Missing Count": missing,
        "Missing %": missing_pct
    })

    print(report[report["Missing Count"] > 0])


def report_candidate_keys(df):
    print("\nCandidate Keys")

    keys = []

    for col in df.columns:
        if df[col].is_unique and not df[col].isna().any():
            keys.append(col)

    if keys:
        for key in keys:
            print(f"  • {key}")
    else:
        print("None found")

def report_duplicates(df, key_columns=None):

    print("\nDuplicate Check")

    if not key_columns:
        print("Skipped")
        return

    valid = [c for c in key_columns if c in df.columns]

    if not valid:
        print("No matching key columns")
        return

    duplicates = df.duplicated(subset=valid).sum()

    print(f"Checked using: {', '.join(valid)}")
    print(f"Duplicate Rows: {duplicates}")


def report_unique_examples(df):

    print("\nExample Values")

    for col in df.columns:

        if df[col].dtype == object:

            examples = (
                df[col]
                .dropna()
                .astype(str)
                .unique()[:5]
            )

            print(f"{col}: {list(examples)}")


def report_numeric_summary(df):

    numeric = df.select_dtypes(include=np.number)

    if numeric.empty:
        return

    print("\nNumeric Summary")

    print(numeric.describe().T.round(2))


def inspect_sheet(sheet_name, workbook):

    df = workbook.parse(sheet_name)

    print("\n" + "="*70)
    print(sheet_name.upper())
    print("="*70)

    report_shape(df)

    report_columns(df)

    report_dtypes(df)

    report_candidate_keys(df)

    report_missing(df)

    report_duplicates(
        df,
        key_columns=[
            "Transaction Id",
            "Distributor Id",
            "Product Id",
            "Salesperson Id",
            "Record Id"
        ]
    )

    report_unique_examples(df)

    report_numeric_summary(df)


def main():

    workbook_path = "data/raw/fmn_data.xlsx"
    workbook = pd.ExcelFile(workbook_path)

    print("="*70)
    print("FMN DATA ENGINEERING ASSESSMENT")
    print("="*70)

    print(f"Workbook: {os.path.basename(workbook_path)}")
    print(f"Sheets: {len(workbook.sheet_names)}")

    for sheet in workbook.sheet_names:
        inspect_sheet(sheet, workbook)


if __name__ == "__main__":
    main()