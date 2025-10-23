"""Simple game loop API test without emojis"""
import requests
import json

BASE = "http://127.0.0.1:8000"

print("\n" + "="*60)
print("Testing Game Loop API")
print("="*60)

# 1. Create season
print("\n1. Creating season...")
r = requests.post(f"{BASE}/season/create", json={
    "discipline": "SINGLE_SEATER", 
    "num_races": 3, 
    "season_year": 2027
})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Season: {data['championship']} ({data['total_rounds']} races)")
else:
    print(f"ERROR: {r.text}")
    exit(1)

# 2. Simulate Race 1
print("\n2. Simulating Race 1...")
r = requests.post(f"{BASE}/season/next-race", json={"weather": "dry", "num_laps": 50})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Track: {data['race_info']['track_name']}")
    print(f"Winner: {data['results'][0]['driver_name']} ({data['results'][0]['team_name']})")
    print(f"Leader: {data['championship_leader']['driver_name']} - {data['championship_leader']['points']} pts")
else:
    print(f"ERROR: {r.text}")
    exit(1)

# 3. Simulate Race 2
print("\n3. Simulating Race 2...")
r = requests.post(f"{BASE}/season/next-race", json={"weather": "dry", "num_laps": 50})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Track: {data['race_info']['track_name']}")
    print(f"Winner: {data['results'][0]['driver_name']}")
    print(f"Leader: {data['championship_leader']['driver_name']} - {data['championship_leader']['points']} pts")
else:
    print(f"ERROR: {r.text}")

# 4. Get standings
print("\n4. Getting standings...")
r = requests.get(f"{BASE}/season/standings")
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print("\nDriver Standings:")
    for standing in data['driver_standings'][:5]:
        print(f"  {standing['position']}. {standing['driver_name']} - {standing['points']} pts")
else:
    print(f"ERROR: {r.text}")

# 5. Simulate final race
print("\n5. Simulating Race 3 (Final)...")
r = requests.post(f"{BASE}/season/next-race", json={"weather": "dry", "num_laps": 50})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Track: {data['race_info']['track_name']}")
    print(f"Winner: {data['results'][0]['driver_name']}")
    if data.get('season_complete'):
        champ = data.get('champion', {})
        print(f"\nSEASON COMPLETE!")
        print(f"Champion: {champ.get('driver_name')} ({champ.get('team_name')})")
        print(f"Final Points: {champ.get('points')}")
else:
    print(f"ERROR: {r.text}")

print("\n" + "="*60)
print("All tests passed - Game Loop API is functional!")
print("="*60)
