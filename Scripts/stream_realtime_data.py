import json
import random
import time
from datetime import datetime

import requests


def generate_event() -> dict:
    return {
        "Timestamp": datetime.utcnow().isoformat() + "Z",
        "MachineID": f"P001-L1-M{random.randint(1, 60):02d}",
        "Production_Units": random.randint(100, 500),
        "OEE_Percent": round(random.uniform(60, 95), 2),
        "Downtime_Minutes": random.choice([0, 0, 0, 15, 30, 45, 60]),
        "Temperature_Celsius": round(random.uniform(65, 85), 1),
        "Status": random.choice(["Running", "Running", "Idle", "Error"]),
    }


def main() -> None:
    push_url = input("Enter your Power BI push dataset URL: ").strip()
    if not push_url:
        print("Push dataset URL is required.")
        raise SystemExit(1)

    print("🔄 Starting real-time stream. Press Ctrl+C to stop.")
    while True:
        try:
            event = generate_event()
            payload = json.dumps([event])
            headers = {"Content-Type": "application/json"}
            response = requests.post(push_url, data=payload, headers=headers)

            if response.status_code == 200:
                print(f"✓ {event['Timestamp']} | {event['MachineID']} | {event['Production_Units']} units")
            else:
                print(f"✗ HTTP {response.status_code} | {response.text}")

            time.sleep(10)
        except KeyboardInterrupt:
            print("\n🛑 Stream stopped by user.")
            break
        except Exception as err:
            print(f"Error: {err}")
            time.sleep(10)
