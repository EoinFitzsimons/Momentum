"""
Test Race Simulation - Quick Demo

Tests the /simulate/race endpoint with a simple single-seater race.
"""

import requests
import json

API_BASE = "http://127.0.0.1:8000"

def test_race_simulation():
    """Test a simple race simulation"""
    
    # Step 1: Get some drivers
    print("📊 Fetching drivers...")
    response = requests.get(f"{API_BASE}/drivers")
    if response.status_code != 200:
        print(f"❌ Failed to get drivers: {response.status_code}")
        return
    
    drivers_data = response.json()
    all_drivers = drivers_data.get("drivers", [])
    print(f"✅ Found {len(all_drivers)} drivers")
    
    # Get first 10 single-seater drivers
    driver_ids = [d["id"] for d in all_drivers[:10]]
    print(f"🏎️  Selected {len(driver_ids)} drivers for race")
    
    # Step 2: Get single-seater teams
    print("\n📊 Fetching teams...")
    response = requests.get(f"{API_BASE}/teams?discipline=SINGLE_SEATER")
    if response.status_code != 200:
        print(f"❌ Failed to get teams: {response.status_code}")
        return
    
    teams_data = response.json()
    teams = teams_data.get("teams", [])
    print(f"✅ Found {len(teams)} Single Seater teams")
    
    # Step 3: Simulate a race
    print("\n🏁 Simulating race at Silverstone...")
    
    race_request = {
        "discipline": "SINGLE_SEATER",
        "race_id": 0,  # Will be created
        "drivers": driver_ids
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/simulate/race",
            json=race_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Race simulation completed!")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    except requests.exceptions.Timeout:
        print("⏱️  Simulation timed out (this is normal for Monte Carlo - increase timeout)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("MOMENTUM RACE SIMULATION TEST")
    print("="*60)
    test_race_simulation()
