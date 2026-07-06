from pathlib import Path

from pipeline.main import run_pipeline


def test_run_pipeline_reports_validation_errors(tmp_path, monkeypatch):
    workbook_path = tmp_path / "sample.xlsx"
    workbook_path.write_bytes(b"not a real workbook")

    report = run_pipeline(workbook_path, tmp_path / "warehouse.duckdb")

    assert report["errors"]
    assert report["warnings"] == []
