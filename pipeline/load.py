from pathlib import Path
from typing import Dict, Union

import duckdb
import pandas as pd


def load_tables(tables: Dict[str, pd.DataFrame], destination: Union[str, Path]) -> None:
    """Write each dataframe to a DuckDB database as a table."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(destination))
    try:
        for table_name, df in tables.items():
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.register("temp_frame", df)
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_frame")
    finally:
        conn.close()
