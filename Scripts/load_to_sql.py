import os

import pandas as pd
from sqlalchemy import create_engine


def build_connection_string(server: str, database: str, username: str, password: str) -> str:
    template = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=tcp:{server},1433;"
        "Database={database};"
        "Uid={username};"
        "Pwd={password};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return template.format(
        server=server,
        database=database,
        username=username,
        password=password,
    )


def main() -> None:
    server = os.environ.get("AZURE_SQL_SERVER")
    database = os.environ.get("AZURE_SQL_DATABASE")
    username = os.environ.get("AZURE_SQL_USER")
    password = os.environ.get("AZURE_SQL_PASSWORD")

    if not all([server, database, username, password]):
        print("Set AZURE_SQL_SERVER, AZURE_SQL_DATABASE, AZURE_SQL_USER, and AZURE_SQL_PASSWORD environment variables.")
        raise SystemExit(1)

    conn_str = build_connection_string(server, database, username, password)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={conn_str}")

    csv_files = {
        "dim_plant.csv": "dim_plant",
        "dim_line.csv": "dim_line",
        "dim_machine.csv": "dim_machine",
        "dim_product.csv": "dim_product",
        "dim_shift.csv": "dim_shift",
        "dim_date.csv": "dim_date",
        "fact_production.csv": "fact_production",
        "fact_downtime.csv": "fact_downtime",
        "fact_sensor_readings.csv": "fact_sensor_readings",
    }

    for csv_file, table_name in csv_files.items():
        if not os.path.exists(csv_file):
            print(f"✗ {csv_file} not found")
            continue

        df = pd.read_csv(csv_file)
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)
        print(f"✓ Loaded {table_name} ({len(df)} rows)")

    print("\n✅ Data loaded to Azure SQL Database!")


if __name__ == "__main__":
    main()
