# FMN Data Engineering Assessment

This repository implements a lightweight analytics engineering workflow for an FMCG sales dataset. It ingests an Excel workbook, validates and transforms the data, loads it into a DuckDB warehouse, builds analytics models with dbt, and orchestrates the flow with Apache Airflow.

## Why DuckDB?

DuckDB was chosen as the analytical data warehouse for this assessment for several reasons:

- Zero infrastructure setup: DuckDB is embedded and stores data in a single database file, eliminating the need to provision or administer a database server.
- Fast analytical performance: DuckDB is optimized for OLAP workloads and executes aggregation-heavy SQL queries efficiently.
- Excellent Pandas integration: Since the ETL pipeline is implemented in Python, DuckDB integrates naturally with pandas DataFrames, allowing transformed data to be loaded directly into the warehouse.
- Lightweight and reproducible: Anyone cloning the repository can run the project without installing PostgreSQL or configuring a database server.
- Ideal for local analytics: The assessment focuses on analytical reporting rather than transactional processing, making DuckDB a suitable technology choice.

Although the assessment mentions PostgreSQL as an example, the orchestration and modeling approach remain database-agnostic and can be migrated to PostgreSQL or another warehouse with minimal changes.

## Architecture

The solution follows a modular ELT architecture:

```text
Excel Workbook
      │
      ▼
Extract (pandas)
      │
      ▼
Validation
      │
      ▼
Transformation
      │
      ▼
DuckDB Warehouse
      │
      ▼
dbt Staging Models
      │
      ▼
dbt Mart Models
      │
      ▼
Business SQL
```

Each stage has a single responsibility:

| Layer | Responsibility |
| --- | --- |
| Extract | Read Excel workbook into DataFrames |
| Validate | Run data quality checks, referential integrity checks, and required-field validation |
| Transform | Standardize data types, clean text, and derive fields |
| Load | Persist curated tables into DuckDB |
| dbt | Build staging and analytical marts |
| SQL | Answer business questions |
| Airflow | Orchestrate the complete workflow |

## Data Quality

The validation layer performs several categories of quality checks before loading data into the warehouse.

Implemented validations include:

- Required table validation
- Required column validation
- Primary key validation
- Duplicate detection
- Positive numeric checks
- Accepted value validation
- Foreign-key relationship validation

Rather than silently failing, validation errors are collected into a report and surfaced before downstream processing.

## Transformation Strategy

Transformations were intentionally kept deterministic and non-destructive.

Examples include:

- Trimming whitespace
- Standardizing text casing
- Numeric type coercion
- Boolean normalization
- Datetime parsing
- Deriving missing achievement percentages
- Handling missing values without deleting records

This approach preserves source data while ensuring consistency for downstream analytics.

## Why dbt?

dbt was introduced after the warehouse load to separate transformation logic from ingestion.

The project uses:

- Staging models for cleaned warehouse tables
- Mart models for analytical reporting
- Schema documentation
- Built-in tests including unique, not_null, relationships, and accepted_values

This keeps business logic version-controlled and modular.

## Airflow orchestration

Apache Airflow orchestrates the complete pipeline:

```text
ETL Pipeline
      │
      ▼
dbt Run
      │
      ▼
dbt Test
```

The DAG includes:

- Task dependencies
- Retry logic
- Failure alert configuration
- Modular Python tasks

## Project structure

The repository separates each responsibility into its own module:

```text
pipeline/
├── extract.py
├── validate.py
├── transform.py
├── load.py
└── main.py
```

This design improves:

- Readability
- Maintainability
- Unit testing
- Future extensibility

## Challenges and trade-offs

Some design decisions made during development included:

- Choosing DuckDB instead of PostgreSQL to reduce infrastructure complexity while maintaining SQL compatibility.
- Keeping validation and transformation as separate stages to isolate data quality concerns from data cleaning.
- Using dbt only after the warehouse load so that analytical models operate on trusted warehouse tables.
- Building the ETL pipeline as modular Python components to simplify testing and future extension.

## Future improvements

Given additional time, the project could be extended with:

- Incremental dbt models
- Slowly Changing Dimension (SCD Type 2) support
- Great Expectations for richer data validation
- Environment-based configuration management
- CI/CD with GitHub Actions
- Data lineage documentation
- Automated monitoring and alerting
- Unit tests for each pipeline component
- Cloud deployment (AWS, GCP, or Azure)

## Technology choices

| Technology | Why it was chosen |
| --- | --- |
| Python | ETL orchestration and data processing |
| Pandas | Excel ingestion and transformations |
| DuckDB | Lightweight analytical warehouse with zero setup |
| dbt | SQL transformations, testing, and documentation |
| Airflow | Workflow orchestration and scheduling |
| Docker | Reproducible execution environment |
| SQL | Business analytics and reporting |
| DBeaver | Interactive exploration and validation of warehouse data |

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
