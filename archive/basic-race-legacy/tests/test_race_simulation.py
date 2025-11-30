"""
Archived: Race simulation test (legacy)
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

def test_race_simulation():
    print("📊 Fetching drivers...")
    response = requests.get(f"{API_BASE}/drivers")
    if response.status_code != 200:
        print(f"❌ Failed to get drivers: {response.status_code}")
        return

    drivers_data = response.json()
    all_drivers = drivers_data.get("drivers", [])
    print(f"✅ Found {len(all_drivers)} drivers")

if __name__ == "__main__":
    test_race_simulation()
