from pathlib import Path
from typing import Dict, List, Union

from pipeline.extract import extract_all_sheets
from pipeline.load import load_tables
from pipeline.transform import transform_tables
from pipeline.validate import generate_report


def run_pipeline(workbook_path: Union[str, Path], destination: Union[str, Path]) -> Dict[str, List[str]]:
    """Run the ETL pipeline end to end: extract, validate, transform, and load."""
    workbook_path = Path(workbook_path)
    destination = Path(destination)

    try:
        tables = extract_all_sheets(workbook_path)
    except Exception as exc:  # pragma: no cover - defensive behavior for bad input
        return {"errors": [f"Extraction failed: {exc}"], "warnings": []}

    report = generate_report(tables)
    if report["errors"]:
        return report

    transformed_tables = transform_tables(tables.copy())
    load_tables(transformed_tables, destination)

    return report
