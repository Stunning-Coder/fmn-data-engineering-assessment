# FMN Data Engineering Assessment

This repository implements a lightweight analytics engineering workflow for an FMCG sales dataset. It ingests an Excel workbook, validates and transforms the data, loads it into a DuckDB warehouse, builds analytics models with dbt, and orchestrates the flow with Apache Airflow.

## What this project does

The pipeline follows a practical end-to-end data stack:

1. Extract data from the workbook in [data/raw/fmn_data.xlsx](data/raw/fmn_data.xlsx)
2. Clean and standardize the source tables in Python
3. Validate the transformed data before loading it
4. Load the results into DuckDB at [data/warehouse.duckdb](data/warehouse.duckdb)
5. Build staging and mart models with dbt
6. Run business-analysis SQL against the warehouse
7. Orchestrate the workflow in Airflow

## Project structure

- [pipeline/](pipeline/) – ETL modules for extraction, transformation, validation, and loading
- [dbt/](dbt/) – dbt project, source definitions, staging models, and marts
- [airflow/](airflow/) – Airflow DAGs for orchestration
- [sql/](sql/) – business-question SQL scripts
- [data/](data/) – raw source files, intermediate data, and the DuckDB warehouse
- [docs/](docs/) – supporting documentation and data discovery notes
- [tests/](tests/) – basic validation tests for transformation logic

## Tech stack

- Python
- pandas and openpyxl
- DuckDB
- dbt
- Apache Airflow
- Docker Compose

## Quick start

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the ETL pipeline

The ETL entrypoint was verified with the sample workbook and writes the warehouse to [data/warehouse.duckdb](data/warehouse.duckdb).

```bash
python - <<'PY'
from pipeline.main import run_pipeline
result = run_pipeline('data/raw/fmn_data.xlsx', 'data/warehouse.duckdb')
print(result)
PY
```

### 4. Run dbt models

```bash
cd dbt
dbt run
dbt test
```

### 5. Run the business SQL questions

The repository includes sample analytics queries in [sql/business_questions.sql](sql/business_questions.sql). These can be run directly against the DuckDB warehouse.

## Airflow demo

The repository includes a Docker-based Airflow setup so the ETL and dbt steps can be orchestrated together.

```bash
docker compose up -d --build
```

Then open:

- http://localhost:8080

The compose stack uses Postgres only for Airflow metadata; the analytics warehouse remains DuckDB.

## Output artifacts

The main generated outputs are:

- [data/warehouse.duckdb](data/warehouse.duckdb) – the analytical warehouse
- [dbt/target/](dbt/target/) – dbt build artifacts
- [airflow/logs/](airflow/logs/) – Airflow runtime logs

These generated files are intended to stay out of version control.

## Notes

This project is designed as a practical assessment deliverable: it focuses on a working pipeline, clear transformation logic, dbt-based analytics modeling, and an orchestration layer that can be demonstrated end to end.
