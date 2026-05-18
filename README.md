# Manufacturing Analytics Project

This project generates synthetic manufacturing data, loads it to Azure, and connects it to Power BI.

## Overview

- `Scripts/generate_manufacturing_data.py` - generates manufacturing CSV and Excel files with static dimensions and incremental fact append behavior
- `Scripts/upload_to_azure.py` - uploads CSV files to Azure Blob Storage
- `Scripts/load_to_sql.py` - loads CSV files into Azure SQL Database
- `Scripts/stream_realtime_data.py` - pushes real-time events to a Power BI push dataset

## Quick Start

### 1. Activate the Python virtual environment

Open a VS Code terminal and run:

```powershell
cd D:\BI\Manufacturing-Analytics-Project\Scripts
.\.venv\Scripts\Activate.ps1
```

### 2. Install required libraries

If you need packages, install them in the venv:

```powershell
pip install pandas numpy faker openpyxl python-dateutil azure-storage-blob requests sqlalchemy pyodbc
```

### 3. Generate initial data

Run:

```powershell
python generate_manufacturing_data.py --reset
```

This creates the baseline static dimensions and the first year of historical production, downtime, and sensor readings.

### 4. Append new operational data

After initial setup, use incremental append mode:

```powershell
python generate_manufacturing_data.py --days 7
```

That generates and appends a week of new operational rows to:

- `fact_production.csv`
- `fact_downtime.csv`
- `fact_sensor_readings.csv`

Existing dimension files stay static unless you use `--force-dims` or `--reset`.

Output files will be created in the project `data/` folder:

- `dim_plant.csv`
- `dim_line.csv`
- `dim_machine.csv`
- `dim_product.csv`
- `dim_shift.csv`
- `dim_date.csv`
- `fact_production.csv`
- `fact_downtime.csv`
- `fact_sensor_readings.csv`
- `Manufacturing_Data_Complete.xlsx`

### 4. Load into Power BI

Open Power BI Desktop and load the CSV files from `data/`.

Recommended relationships:

- `dim_plant[PlantID]` → `dim_line[PlantID]`
- `dim_line[LineID]` → `dim_machine[LineID]`
- `dim_machine[MachineID]` → `fact_production[MachineID]`
- `dim_machine[MachineID]` → `fact_downtime[MachineID]`
- `dim_product[ProductID]` → `fact_production[ProductID]`
- `dim_shift[ShiftID]` → `fact_production[ShiftID]`

## Azure Upload

### Upload to Blob Storage

Set these environment variables first:

```powershell
$env:AZURE_STORAGE_CONNECTION_STRING = "<your connection string>"
$env:AZURE_STORAGE_CONTAINER = "manufacturing-data"
```

Then run:

```powershell
python upload_to_azure.py
```

### Load to Azure SQL

Set environment variables:

```powershell
$env:AZURE_SQL_SERVER = "<server>.database.windows.net"
$env:AZURE_SQL_DATABASE = "ManufacturingDB"
$env:AZURE_SQL_USER = "sqladmin"
$env:AZURE_SQL_PASSWORD = "<password>"
```

Then run:

```powershell
python load_to_sql.py
```

This loads all dimension tables plus production, downtime, and sensor-readings fact tables.

## Real-Time Power BI Streaming

Run the stream script and enter your Power BI push dataset URL when prompted:

```powershell
python stream_realtime_data.py
```

## Notes

- The generator now writes CSV and Excel output directly into `data/`.
- Use Power BI Desktop first to validate the dashboard locally.
- After that, connect to Azure Blob Storage or Azure SQL Database for cloud-based reporting.
