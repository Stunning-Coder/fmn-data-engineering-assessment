import pandas as pd
import re
from pathlib import Path

def extract_all_sheets(workbook_path):
    """
    Reads all worksheets from the Excel workbook,
    normalizes worksheet names and column names,
    and returns a dictionary of DataFrames.
    """

    workbook_path = Path(workbook_path)
    workbook = pd.ExcelFile(workbook_path)
    tables = {}

    for sheet in workbook.sheet_names:

        df = workbook.parse(sheet_name=sheet)
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(r"\s+", "_", regex=True)
        )

        clean_sheet_name = re.sub(r"\s+", "_", sheet.strip().lower())

        tables[clean_sheet_name] = df

    return tables

if __name__ == "__main__":
    tables = extract_all_sheets("data/raw/fmn_data.xlsx")
    print(tables.keys())