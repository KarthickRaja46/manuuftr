import argparse
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DIMENSION_FILES = {
    "dim_plant.csv": "dim_plant",
    "dim_line.csv": "dim_line",
    "dim_machine.csv": "dim_machine",
    "dim_product.csv": "dim_product",
    "dim_shift.csv": "dim_shift",
    "dim_date.csv": "dim_date",
}
FACT_FILES = {
    "fact_production.csv": "fact_production",
    "fact_downtime.csv": "fact_downtime",
    "fact_sensor_readings.csv": "fact_sensor_readings",
}


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def generate_static_dimensions(fake: Faker, force: bool) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    dims = {}

    # Plants
    plant_path = DATA_DIR / "dim_plant.csv"
    if force or not plant_path.exists():
        plant_names = ["Detroit", "Shanghai", "Frankfurt", "Singapore"]
        regions = ["North America", "Asia Pacific", "Europe", "Asia Pacific"]
        dims["dim_plant"] = pd.DataFrame([
            {
                "PlantID": f"P{i:03d}",
                "PlantName": f"{plant_name} Manufacturing Hub",
                "Location": plant_name,
                "Region": region,
                "Country": random.choice(["USA", "China", "Germany", "Singapore"]),
                "Capacity_UnitsPerDay": random.randint(5000, 15000),
                "EmployeeCount": random.randint(200, 800),
                "OperationalSince": fake.date_between(start_date="-10y", end_date="-1y").isoformat(),
            }
            for i, (plant_name, region) in enumerate(zip(plant_names, regions), 1)
        ])
        save_csv(dims["dim_plant"], plant_path)
    else:
        dims["dim_plant"] = load_csv(plant_path)

    # Production lines
    line_path = DATA_DIR / "dim_line.csv"
    if force or not line_path.exists() or dims["dim_plant"].empty:
        lines = []
        line_types = ["Assembly Line", "Welding Station", "Packaging Line", "Quality Check", "Finishing Line"]
        for plant_id in dims["dim_plant"]["PlantID"]:
            for i in range(1, 6):
                lines.append({
                    "LineID": f"{plant_id}-L{i}",
                    "LineName": f"{random.choice(line_types)} {i}",
                    "PlantID": plant_id,
                    "LineManager": fake.name(),
                    "TargetOEE_Percent": random.randint(75, 95),
                    "StandardCycletime_Seconds": random.randint(30, 300),
                    "Status": random.choice(["Active", "Active", "Active", "Maintenance"]),
                })
        dims["dim_line"] = pd.DataFrame(lines)
        save_csv(dims["dim_line"], line_path)
    else:
        dims["dim_line"] = load_csv(line_path)

    # Machines
    machine_path = DATA_DIR / "dim_machine.csv"
    if force or not machine_path.exists() or dims["dim_line"].empty:
        machines = []
        machine_types = ["CNC Lathe", "Industrial Robot", "Hydraulic Press", "Assembly Machine", "Welding Robot"]
        for line_id in dims["dim_line"]["LineID"]:
            for i in range(1, 4):
                machines.append({
                    "MachineID": f"{line_id}-M{i}",
                    "MachineName": f"{random.choice(machine_types)} #{i}",
                    "LineID": line_id,
                    "PlantID": line_id.split("-")[0],
                    "MachineType": random.choice(machine_types),
                    "Manufacturer": random.choice(["Siemens", "ABB", "Fanuc", "KUKA", "Bosch"]),
                    "MaxCapacity_UnitsPerHour": random.randint(300, 800),
                    "InstallationDate": fake.date_between(start_date="-7y", end_date="today").isoformat(),
                    "Age_Years": random.randint(1, 7),
                    "LastMaintenanceDate": fake.date_between(start_date="-6m", end_date="today").isoformat(),
                    "MaintenanceFrequency_Days": random.choice([30, 60, 90, 180]),
                    "Status": random.choice(["Active", "Active", "Active", "Under Repair"]),
                    "Cost": random.randint(50000, 500000),
                })
        dims["dim_machine"] = pd.DataFrame(machines)
        save_csv(dims["dim_machine"], machine_path)
    else:
        dims["dim_machine"] = load_csv(machine_path)

    # Products
    product_path = DATA_DIR / "dim_product.csv"
    if force or not product_path.exists():
        categories = ["Electronics", "Mechanical Parts", "Hydraulics", "Electrical Components", "Assemblies"]
        dims["dim_product"] = pd.DataFrame([
            {
                "ProductID": f"PRD{i:04d}",
                "ProductName": f"{fake.word().title()}-{fake.word().title()}-{i}",
                "ProductCategory": random.choice(categories),
                "SKU": f"SKU-{fake.bothify(text='????-####')}",
                "UnitPrice": random.randint(100, 2000),
                "CostPerUnit": random.randint(30, 1000),
                "StandardCycletime_Seconds": random.randint(30, 600),
                "Weight_kg": round(random.uniform(0.5, 50), 2),
                "Status": random.choice(["Active", "Active", "Active", "Discontinued"]),
            }
            for i in range(1, 21)
        ])
        save_csv(dims["dim_product"], product_path)
    else:
        dims["dim_product"] = load_csv(product_path)

    # Shifts
    shift_path = DATA_DIR / "dim_shift.csv"
    if force or not shift_path.exists():
        dims["dim_shift"] = pd.DataFrame([
            {"ShiftID": "S1", "ShiftName": "Day Shift", "StartTime": "06:00", "EndTime": "14:00", "Capacity_UnitsPerShift": 2000},
            {"ShiftID": "S2", "ShiftName": "Evening Shift", "StartTime": "14:00", "EndTime": "22:00", "Capacity_UnitsPerShift": 1900},
            {"ShiftID": "S3", "ShiftName": "Night Shift", "StartTime": "22:00", "EndTime": "06:00", "Capacity_UnitsPerShift": 1700},
        ])
        save_csv(dims["dim_shift"], shift_path)
    else:
        dims["dim_shift"] = load_csv(shift_path)

    # Date dimension
    date_path = DATA_DIR / "dim_date.csv"
    if force or not date_path.exists():
        dims["dim_date"] = generate_date_dimension(datetime(2025, 1, 1), 365)
        save_csv(dims["dim_date"], date_path)
    else:
        dims["dim_date"] = load_csv(date_path)

    return dims


def generate_date_dimension(start_date: datetime, num_days: int) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "DateKey": int((start_date + timedelta(days=day_offset)).strftime("%Y%m%d")),
            "Date": (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
            "Year": (start_date + timedelta(days=day_offset)).year,
            "Quarter": ((start_date + timedelta(days=day_offset)).month - 1) // 3 + 1,
            "Month": (start_date + timedelta(days=day_offset)).month,
            "MonthName": (start_date + timedelta(days=day_offset)).strftime("%B"),
            "Week": (start_date + timedelta(days=day_offset)).isocalendar()[1],
            "DayOfWeek": (start_date + timedelta(days=day_offset)).weekday(),
            "DayName": (start_date + timedelta(days=day_offset)).strftime("%A"),
            "IsWeekend": int((start_date + timedelta(days=day_offset)).weekday() >= 5),
            "IsHoliday": 0,
        }
        for day_offset in range(num_days)
    ])


def extend_date_dimension(df_dates: pd.DataFrame, target_end_date: datetime) -> pd.DataFrame:
    if df_dates.empty:
        return generate_date_dimension(target_end_date, 0)

    existing_max = pd.to_datetime(df_dates["Date"]).max()
    if existing_max >= target_end_date:
        return df_dates

    new_rows = []
    current_date = existing_max + timedelta(days=1)
    while current_date <= target_end_date:
        new_rows.append({
            "DateKey": int(current_date.strftime("%Y%m%d")),
            "Date": current_date.strftime("%Y-%m-%d"),
            "Year": current_date.year,
            "Quarter": (current_date.month - 1) // 3 + 1,
            "Month": current_date.month,
            "MonthName": current_date.strftime("%B"),
            "Week": current_date.isocalendar()[1],
            "DayOfWeek": current_date.weekday(),
            "DayName": current_date.strftime("%A"),
            "IsWeekend": int(current_date.weekday() >= 5),
            "IsHoliday": 0,
        })
        current_date += timedelta(days=1)

    result = pd.concat([df_dates, pd.DataFrame(new_rows)], ignore_index=True)
    return result


def get_next_start_date(existing_df: pd.DataFrame, default_start: datetime) -> datetime:
    if existing_df.empty:
        return default_start
    if "DateProduced" in existing_df.columns:
        latest = pd.to_datetime(existing_df["DateProduced"]).max()
    elif "DateDowntime" in existing_df.columns:
        latest = pd.to_datetime(existing_df["DateDowntime"]).max()
    else:
        latest = pd.to_datetime(existing_df["Date"]).max()
    return latest + timedelta(days=1)


def season_multiplier(current_date: datetime) -> float:
    if current_date.month in [10, 11, 12]:
        return 1.25
    if current_date.month in [4, 5]:
        return 1.12
    return 1.0


def generate_production_rows(df_machines: pd.DataFrame, df_products: pd.DataFrame, df_shifts: pd.DataFrame, start_date: datetime, days: int, starting_id: int) -> pd.DataFrame:
    rows = []
    current_id = starting_id
    machine_ids = df_machines["MachineID"].tolist()
    product_ids = df_products["ProductID"].tolist()
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        weekend = current_date.weekday() >= 5
        holiday_factor = 0.75 if current_date.weekday() == 6 else 1.0
        seasonal = season_multiplier(current_date)
        for shift in df_shifts["ShiftID"]:
            shift_efficiency = random.uniform(0.75, 0.9) if shift == "S3" else random.uniform(0.88, 1.02)
            active_share = 0.35 if current_date.weekday() == 6 else 0.75
            active_machines = random.sample(machine_ids, k=max(1, int(len(machine_ids) * active_share)))
            for machine_id in active_machines:
                machine = df_machines.loc[df_machines["MachineID"] == machine_id].iloc[0]
                age_penalty = 1.0 - (machine["Age_Years"] * 0.02)
                demand = seasonal * random.uniform(0.9, 1.08)
                planned_qty = int(machine["MaxCapacity_UnitsPerHour"] * 7 * shift_efficiency * demand * age_penalty * holiday_factor)
                planned_qty = max(planned_qty, 20)
                actual_qty = max(0, int(planned_qty * random.uniform(0.7 if shift == "S3" else 0.82, 0.96)))
                defective_units = int(actual_qty * random.uniform(0.01, 0.05 + (machine["Age_Years"] * 0.003)))
                actual_hours = round(random.uniform(7.0, 7.9) if shift == "S3" else random.uniform(7.5, 8.0), 2)
                oee = round(min(100.0, max(45.0, (actual_qty / planned_qty) * 100 + random.uniform(-5.0, 5.0))), 2)
                rows.append({
                    "ProductionID": current_id,
                    "MachineID": machine_id,
                    "DateProduced": current_date.strftime("%Y-%m-%d"),
                    "ShiftID": shift,
                    "ProductID": random.choice(product_ids),
                    "PlannedQuantity": planned_qty,
                    "ActualQuantity": actual_qty,
                    "DefectiveUnits": defective_units,
                    "PlannedHours": 8,
                    "ActualProductionHours": actual_hours,
                    "OEE_Percent": oee,
                    "Production_Cost": round(actual_qty * random.uniform(25.0, 35.0), 2),
                })
                current_id += 1
    return pd.DataFrame(rows), current_id


def generate_downtime_rows(df_machines: pd.DataFrame, start_date: datetime, days: int, starting_id: int) -> pd.DataFrame:
    rows = []
    current_id = starting_id
    downtime_causes = [
        "Mechanical Failure",
        "Electrical Issue",
        "Software Glitch",
        "Material Jam",
        "Operator Error",
        "Tool Wear",
        "Calibration Drift",
        "Sensor Failure",
        "Hydraulic Leak",
        "Belt Slippage",
        "Overheating",
    ]
    planned_causes = ["Scheduled Maintenance", "Tool Change", "Calibration", "Safety Inspection"]

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        is_sunday = current_date.weekday() == 6
        for _, machine in df_machines.iterrows():
            base_probability = 0.015 + (machine["Age_Years"] * 0.01)
            if is_sunday and random.random() < 0.45:
                rows.append({
                    "DowntimeID": current_id,
                    "MachineID": machine["MachineID"],
                    "DateDowntime": current_date.strftime("%Y-%m-%d"),
                    "StartTime": f"{random.randint(6, 11):02d}:{random.randint(0, 59):02d}",
                    "DowntimeDuration_Minutes": random.randint(60, 240),
                    "RootCause": random.choice(planned_causes),
                    "DowntimeCategory": "Planned",
                    "ImpactedUnits": random.randint(20, 180),
                    "RepairCost": random.randint(80, 800),
                    "MaintenanceType": "Preventive",
                    "TechnicianName": Faker().name(),
                    "ResolutionTime_Minutes": random.randint(60, 240),
                })
                current_id += 1
            elif random.random() < min(0.15, base_probability):
                duration = random.randint(15, 360)
                is_planned = random.random() < 0.25
                rows.append({
                    "DowntimeID": current_id,
                    "MachineID": machine["MachineID"],
                    "DateDowntime": current_date.strftime("%Y-%m-%d"),
                    "StartTime": f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}",
                    "DowntimeDuration_Minutes": duration,
                    "RootCause": random.choice(planned_causes if is_planned else downtime_causes),
                    "DowntimeCategory": "Planned" if is_planned else "Unplanned",
                    "ImpactedUnits": random.randint(40, 600),
                    "RepairCost": random.randint(100, 5000) if not is_planned else random.randint(60, 1500),
                    "MaintenanceType": "Preventive" if is_planned else "Corrective",
                    "TechnicianName": Faker().name(),
                    "ResolutionTime_Minutes": min(duration + random.randint(10, 120), 720),
                })
                current_id += 1
    return pd.DataFrame(rows), current_id


def generate_sensor_rows(df_machines: pd.DataFrame, df_production: pd.DataFrame, df_downtime: pd.DataFrame, starting_id: int) -> pd.DataFrame:
    rows = []
    current_id = starting_id
    downtime_keys = set(zip(df_downtime["MachineID"], df_downtime["DateDowntime"])) if not df_downtime.empty else set()
    grouped = (
        df_production.groupby(["MachineID", "DateProduced", "ShiftID"], as_index=False)
        .agg({"ActualQuantity": "sum", "PlannedQuantity": "sum", "ActualProductionHours": "mean"})
    )

    for _, row in grouped.iterrows():
        machine = df_machines.loc[df_machines["MachineID"] == row["MachineID"]].iloc[0]
        base_temp = 64 + machine["Age_Years"] * 0.9 + (3 if row["ShiftID"] == "S3" else 0)
        base_vibration = 0.9 + (machine["Age_Years"] * 0.1)
        base_pressure = 6.0 + random.uniform(-0.3, 0.3)
        base_energy = max(120.0, (machine["MaxCapacity_UnitsPerHour"] * row["ActualProductionHours"] * 0.18))
        key = (row["MachineID"], row["DateProduced"])
        anomaly = key in downtime_keys or random.random() < 0.05

        if anomaly:
            temp = round(base_temp + random.uniform(5.0, 16.0), 1)
            vibration = round(base_vibration + random.uniform(0.8, 1.8), 2)
            pressure = round(base_pressure + random.uniform(0.4, 1.5), 2)
            energy = round(base_energy * random.uniform(1.05, 1.28), 2)
            anomaly_score = round(random.uniform(0.65, 0.98), 2)
        else:
            temp = round(base_temp + random.uniform(-2.0, 2.5), 1)
            vibration = round(base_vibration + random.uniform(-0.3, 0.3), 2)
            pressure = round(base_pressure + random.uniform(-0.2, 0.2), 2)
            energy = round(base_energy * random.uniform(0.95, 1.08), 2)
            anomaly_score = round(random.uniform(0.0, 0.12), 2)

        rows.append({
            "SensorReadingID": current_id,
            "MachineID": row["MachineID"],
            "DateRecorded": row["DateProduced"],
            "ShiftID": row["ShiftID"],
            "Temperature_C": temp,
            "Vibration_mm_s": vibration,
            "Pressure_bar": pressure,
            "Energy_kWh": energy,
            "AnomalyScore": anomaly_score,
        })
        current_id += 1

    return pd.DataFrame(rows)


def summarize_df(df: pd.DataFrame, name: str) -> str:
    if df.empty:
        return f"{name}: 0 rows"
    first_date = df.iloc[0]["DateProduced"] if "DateProduced" in df.columns else df.iloc[0].get("DateRecorded", df.iloc[0].get("DateDowntime", ""))
    last_date = df.iloc[-1]["DateProduced"] if "DateProduced" in df.columns else df.iloc[-1].get("DateRecorded", df.iloc[-1].get("DateDowntime", ""))
    return f"{name}: {len(df)} rows ({first_date} to {last_date})"


def main(days: int | None = None, reset: bool = False, force_dims: bool = False) -> None:
    fake = Faker()
    random.seed()
    np.random.seed()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    os.chdir(DATA_DIR)

    if reset:
        for file_name in list(DIMENSION_FILES) + list(FACT_FILES):
            file_path = DATA_DIR / file_name
            if file_path.exists():
                file_path.unlink()

    dims = generate_static_dimensions(fake, force_dims)
    df_machines = dims["dim_machine"]
    df_products = dims["dim_product"]
    df_shifts = dims["dim_shift"]
    df_dates = dims["dim_date"]

    existing_production = load_csv(DATA_DIR / "fact_production.csv")
    existing_downtime = load_csv(DATA_DIR / "fact_downtime.csv")
    existing_sensor = load_csv(DATA_DIR / "fact_sensor_readings.csv")

    if existing_production.empty or reset:
        target_days = 365 if days is None else days
        start_date = datetime(2025, 1, 1)
    else:
        target_days = 7 if days is None else days
        start_date = get_next_start_date(existing_production, datetime(2025, 1, 1))

    if target_days <= 0:
        raise ValueError("--days must be a positive integer")

    end_date = start_date + timedelta(days=target_days - 1)
    df_dates = extend_date_dimension(df_dates, end_date)
    save_csv(df_dates, DATA_DIR / "dim_date.csv")

    next_production_id = int(existing_production["ProductionID"].max()) + 1 if not existing_production.empty else 1
    next_downtime_id = int(existing_downtime["DowntimeID"].max()) + 1 if not existing_downtime.empty else 1
    next_sensor_id = int(existing_sensor["SensorReadingID"].max()) + 1 if not existing_sensor.empty else 1

    new_production, next_production_id = generate_production_rows(
        df_machines,
        df_products,
        df_shifts,
        start_date,
        target_days,
        next_production_id,
    )
    new_downtime, next_downtime_id = generate_downtime_rows(
        df_machines,
        start_date,
        target_days,
        next_downtime_id,
    )
    new_sensor = generate_sensor_rows(df_machines, new_production, new_downtime, next_sensor_id)

    updated_production = pd.concat([existing_production, new_production], ignore_index=True) if not existing_production.empty else new_production
    updated_downtime = pd.concat([existing_downtime, new_downtime], ignore_index=True) if not existing_downtime.empty else new_downtime
    updated_sensor = pd.concat([existing_sensor, new_sensor], ignore_index=True) if not existing_sensor.empty else new_sensor

    save_csv(updated_production, DATA_DIR / "fact_production.csv")
    save_csv(updated_downtime, DATA_DIR / "fact_downtime.csv")
    save_csv(updated_sensor, DATA_DIR / "fact_sensor_readings.csv")

    print("=" * 60)
    print("MANUFACTURING DATA GENERATOR")
    print("=" * 60)
    print("\n📊 Generation Summary")
    print(f"   • Dates generated: {start_date.strftime('%Y-%m-%d')} through {end_date.strftime('%Y-%m-%d')}")
    print(f"   • Production rows appended: {len(new_production)}")
    print(f"   • Downtime rows appended: {len(new_downtime)}")
    print(f"   • Sensor readings appended: {len(new_sensor)}")
    print(f"   • Total production rows: {len(updated_production)}")
    print(f"   • Total downtime rows: {len(updated_downtime)}")
    print(f"   • Total sensor rows: {len(updated_sensor)}")

    print("\n📁 Updated CSV files:")
    for file_name in [
        "dim_plant.csv",
        "dim_line.csv",
        "dim_machine.csv",
        "dim_product.csv",
        "dim_shift.csv",
        "dim_date.csv",
        "fact_production.csv",
        "fact_downtime.csv",
        "fact_sensor_readings.csv",
    ]:
        print(f"   • {file_name}")

    print("\n📁 Creating Excel Workbook...")
    with pd.ExcelWriter(DATA_DIR / "Manufacturing_Data_Complete.xlsx", engine="openpyxl") as writer:
        dims["dim_plant"].to_excel(writer, sheet_name="dim_plant", index=False)
        dims["dim_line"].to_excel(writer, sheet_name="dim_line", index=False)
        dims["dim_machine"].to_excel(writer, sheet_name="dim_machine", index=False)
        dims["dim_product"].to_excel(writer, sheet_name="dim_product", index=False)
        dims["dim_shift"].to_excel(writer, sheet_name="dim_shift", index=False)
        df_dates.to_excel(writer, sheet_name="dim_date", index=False)
        updated_production.to_excel(writer, sheet_name="fact_production", index=False)
        updated_downtime.to_excel(writer, sheet_name="fact_downtime", index=False)
        updated_sensor.to_excel(writer, sheet_name="fact_sensor_readings", index=False)

    print("    ✓ Excel workbook created: Manufacturing_Data_Complete.xlsx")
    print("\n✅ DATA GENERATION COMPLETE!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate manufacturing data with incremental append behavior.")
    parser.add_argument("--days", type=int, default=None, help="Number of new days to append. Default: 7 when existing facts exist, otherwise 365.")
    parser.add_argument("--reset", action="store_true", help="Remove existing CSV files and regenerate a full dataset from scratch.")
    parser.add_argument("--force-dims", action="store_true", help="Regenerate dimension tables even if they already exist.")
    args = parser.parse_args()
    main(days=args.days, reset=args.reset, force_dims=args.force_dims)
