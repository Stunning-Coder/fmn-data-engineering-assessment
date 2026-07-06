FROM apache/airflow:2.9.3-python3.12

USER root
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

USER airflow
WORKDIR /opt/airflow
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir dbt-duckdb==1.9.6 dbt-core==1.9.10 duckdb==1.5.4

COPY . /opt/airflow/project
ENV PYTHONPATH=/opt/airflow/project
