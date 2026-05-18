import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


def main() -> None:
    fake = Faker()
    # Remove fixed seeds so each run generates new, dynamic data
    # random.seed(42)
    # np.random.seed(42)

    output_dir = Path(__file__).resolve().parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(output_dir)

    print("=" * 60)
    print("MANUFACTURING DATA GENERATOR")
    print("=" * 60)

    print("\n📊 Generating Dimension Tables...")

    plants_data = []
    plant_names = ["Detroit", "Shanghai", "Frankfurt", "Singapore"]
    regions = ["North America", "Asia Pacific", "Europe", "Asia Pacific"]

    for i, (plant_name, region) in enumerate(zip(plant_names, regions), 1):
        plants_data.append({
            "PlantID": f"P{i:03d}",
            "PlantName": f"{plant_name} Manufacturing Hub",
            "Location": plant_name,
            "Region": region,
            "Country": random.choice(["USA", "China", "Germany", "Singapore"]),
            "Capacity_UnitsPerDay": random.randint(5000, 15000),
            "EmployeeCount": random.randint(200, 800),
            "OperationalSince": fake.date_between(start_date="-10y", end_date="-1y").isoformat(),
        })

    df_plants = pd.DataFrame(plants_data)
    df_plants.to_csv("dim_plant.csv", index=False)
    print(f"    ✓ {len(df_plants)} plants created")

    lines_data = []
    line_types = ["Assembly Line", "Welding Station", "Packaging Line", "Quality Check", "Finishing Line"]

    print("  → Creating Production Lines...")
    for plant_id in df_plants["PlantID"]:
        for i in range(1, 6):
            lines_data.append({
                "LineID": f"{plant_id}-L{i}",
                "LineName": f"{random.choice(line_types)} {i}",
                "PlantID": plant_id,
                "LineManager": fake.name(),
                "TargetOEE_Percent": random.randint(75, 95),
                "StandardCycletime_Seconds": random.randint(30, 300),
                "Status": random.choice(["Active", "Active", "Active", "Maintenance"]),
            })

    df_lines = pd.DataFrame(lines_data)
    df_lines.to_csv("dim_line.csv", index=False)
    print(f"    ✓ {len(df_lines)} production lines created")

    machines_data = []
    machine_types = ["CNC Lathe", "Industrial Robot", "Hydraulic Press", "Assembly Machine", "Welding Robot"]

    print("  → Creating Machines...")
    for line_id in df_lines["LineID"]:
        for i in range(1, 4):
            machines_data.append({
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

    df_machines = pd.DataFrame(machines_data)
    df_machines.to_csv("dim_machine.csv", index=False)
    print(f"    ✓ {len(df_machines)} machines created")

    products_data = []
    categories = ["Electronics", "Mechanical Parts", "Hydraulics", "Electrical Components", "Assemblies"]

    print("  → Creating Products...")
    for i in range(1, 21):
        products_data.append({
            "ProductID": f"PRD{i:04d}",
            "ProductName": f"{fake.word().title()}-{fake.word().title()}-{i}",
            "ProductCategory": random.choice(categories),
            "SKU": f"SKU-{fake.bothify(text='????-####')}",
            "UnitPrice": random.randint(100, 2000),
            "CostPerUnit": random.randint(30, 1000),
            "StandardCycletime_Seconds": random.randint(30, 600),
            "Weight_kg": round(random.uniform(0.5, 50), 2),
            "Status": random.choice(["Active", "Active", "Active", "Discontinued"]),
        })

    df_products = pd.DataFrame(products_data)
    df_products.to_csv("dim_product.csv", index=False)
    print(f"    ✓ {len(df_products)} products created")

    shifts_data = [
        {"ShiftID": "S1", "ShiftName": "Day Shift", "StartTime": "06:00", "EndTime": "14:00", "Capacity_UnitsPerShift": 2000},
        {"ShiftID": "S2", "ShiftName": "Evening Shift", "StartTime": "14:00", "EndTime": "22:00", "Capacity_UnitsPerShift": 1900},
        {"ShiftID": "S3", "ShiftName": "Night Shift", "StartTime": "22:00", "EndTime": "06:00", "Capacity_UnitsPerShift": 1700},
    ]

    df_shifts = pd.DataFrame(shifts_data)
    df_shifts.to_csv("dim_shift.csv", index=False)
    print(f"    ✓ {len(df_shifts)} shifts created")

    print("  → Creating Date Dimension...")
    dates_data = []
    start_date = datetime(2025, 1, 1)

    for day_offset in range(365):
        current_date = start_date + timedelta(days=day_offset)
        dates_data.append({
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

    df_dates = pd.DataFrame(dates_data)
    df_dates.to_csv("dim_date.csv", index=False)
    print(f"    ✓ {len(df_dates)} dates created")

    print("\n📈 Generating Fact Tables...")
    production_data = []
    production_id = 1

    for day_offset in range(365):
        current_date = start_date + timedelta(days=day_offset)
        if current_date.weekday() >= 5 and random.random() < 0.3:
            continue

        for shift in df_shifts["ShiftID"].values:
            active_machines = random.sample(df_machines["MachineID"].tolist(), k=int(len(df_machines) * 0.65))
            for machine_id in active_machines:
                machine_info = df_machines.loc[df_machines["MachineID"] == machine_id].iloc[0]
                planned_qty = random.randint(int(machine_info["MaxCapacity_UnitsPerHour"] * 7), int(machine_info["MaxCapacity_UnitsPerHour"] * 8))
                actual_qty = int(planned_qty * random.uniform(0.8, 0.95))

                production_data.append({
                    "ProductionID": production_id,
                    "MachineID": machine_id,
                    "DateProduced": current_date.strftime("%Y-%m-%d"),
                    "ShiftID": shift,
                    "ProductID": random.choice(df_products["ProductID"].values),
                    "PlannedQuantity": planned_qty,
                    "ActualQuantity": actual_qty,
                    "DefectiveUnits": random.randint(0, int(actual_qty * 0.05)),
                    "PlannedHours": 8,
                    "ActualProductionHours": round(random.uniform(7.5, 8.0), 2),
                    "OEE_Percent": round(random.uniform(65, 95), 2),
                    "Production_Cost": round(actual_qty * 30, 2),
                })
                production_id += 1

    df_production = pd.DataFrame(production_data)
    df_production.to_csv("fact_production.csv", index=False)
    print(f"    ✓ {len(df_production)} production records created")

    print("  → Creating Downtime Records...")
    downtime_data = []
    downtime_reasons = [
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
        "Maintenance Window",
    ]
    downtime_reasons_planned = ["Scheduled Maintenance", "Tool Change", "Calibration", "Safety Inspection"]

    for i in range(800):
        random_date = start_date + timedelta(days=random.randint(0, 364))
        is_planned = random.choice([True, True, True, False])
        downtime_data.append({
            "DowntimeID": i + 1,
            "MachineID": random.choice(df_machines["MachineID"].values),
            "DateDowntime": random_date.strftime("%Y-%m-%d"),
            "StartTime": f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}",
            "DowntimeDuration_Minutes": random.randint(15, 480) if not is_planned else random.randint(30, 300),
            "RootCause": random.choice(downtime_reasons_planned if is_planned else downtime_reasons),
            "DowntimeCategory": "Planned" if is_planned else "Unplanned",
            "ImpactedUnits": random.randint(50, 500),
            "RepairCost": random.randint(100, 5000) if not is_planned else random.randint(50, 2000),
            "MaintenanceType": "Preventive" if is_planned else "Corrective",
            "TechnicianName": fake.name(),
            "ResolutionTime_Minutes": random.randint(15, 300),
        })

    df_downtime = pd.DataFrame(downtime_data)
    df_downtime.to_csv("fact_downtime.csv", index=False)
    print(f"    ✓ {len(df_downtime)} downtime events created")

    print("\n📁 Creating Excel Workbook...")
    with pd.ExcelWriter("Manufacturing_Data_Complete.xlsx", engine="openpyxl") as writer:
        df_plants.to_excel(writer, sheet_name="dim_plant", index=False)
        df_lines.to_excel(writer, sheet_name="dim_line", index=False)
        df_machines.to_excel(writer, sheet_name="dim_machine", index=False)
        df_products.to_excel(writer, sheet_name="dim_product", index=False)
        df_shifts.to_excel(writer, sheet_name="dim_shift", index=False)
        df_dates.to_excel(writer, sheet_name="dim_date", index=False)
        df_production.to_excel(writer, sheet_name="fact_production", index=False)
        df_downtime.to_excel(writer, sheet_name="fact_downtime", index=False)

    print("    ✓ Excel workbook created: Manufacturing_Data_Complete.xlsx")

    print("\n" + "=" * 60)
    print("✅ DATA GENERATION COMPLETE!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   • Plants: {len(df_plants)}")
    print(f"   • Production Lines: {len(df_lines)}")
    print(f"   • Machines: {len(df_machines)}")
    print(f"   • Products: {len(df_products)}")
    print(f"   • Production Records: {len(df_production)}")
    print(f"   • Downtime Events: {len(df_downtime)}")
    print(f"   • Date Range: {df_production['DateProduced'].min()} to {df_production['DateProduced'].max()}")

    print("\n📁 Files Created:")
    for file_name in [
        "dim_plant.csv",
        "dim_line.csv",
        "dim_machine.csv",
        "dim_product.csv",
        "dim_shift.csv",
        "dim_date.csv",
        "fact_production.csv",
        "fact_downtime.csv",
        "Manufacturing_Data_Complete.xlsx",
    ]:
        print(f"   • {file_name}")

    print("\n🚀 Ready for Power BI import!")
    print("=" * 60)


if __name__ == "__main__":
    main()
