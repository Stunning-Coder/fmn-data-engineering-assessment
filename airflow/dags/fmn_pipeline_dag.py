from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_WORKBOOK = ROOT_DIR / "data" / "raw" / "fmn_data.xlsx"
WAREHOUSE_DB = ROOT_DIR / "data" / "warehouse.duckdb"
DBT_PROJECT_DIR = ROOT_DIR / "dbt"
DBT_EXECUTABLE = str(ROOT_DIR / ".venv-dbt" / "bin" / "dbt") if (ROOT_DIR / ".venv-dbt" / "bin" / "dbt").exists() else "dbt"


def run_etl_pipeline():
    import sys

    sys.path.append(str(ROOT_DIR))
    from pipeline.main import run_pipeline

    report = run_pipeline(RAW_WORKBOOK, WAREHOUSE_DB)
    if report.get("errors"):
        raise RuntimeError(f"Pipeline failed: {report['errors']}")


def build_dbt_env() -> dict[str, str]:
    env = os.environ.copy()
    venv_bin = ROOT_DIR / ".venv-dbt" / "bin"
    if venv_bin.exists():
        env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
    return env


with DAG(
    dag_id="fmn_pipeline",
    description="FMN ETL pipeline with DuckDB and dbt",
    tags=["etl", "duckdb", "dbt"],
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "email_on_failure": True,
        "email": ["airflow@example.com"],
    },
) as dag:
    run_etl_pipeline_task = PythonOperator(
        task_id="run_etl_pipeline",
        python_callable=run_etl_pipeline,
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd '{DBT_PROJECT_DIR}' && {DBT_EXECUTABLE} run --profiles-dir .",
        env=build_dbt_env(),
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd '{DBT_PROJECT_DIR}' && {DBT_EXECUTABLE} test --profiles-dir .",
        env=build_dbt_env(),
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    run_etl_pipeline_task >> dbt_run >> dbt_test
