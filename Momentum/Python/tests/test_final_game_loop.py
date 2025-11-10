import requests

BASE = "http://127.0.0.1:8000"
SEASON_YEAR = 2035  # Use future year to avoid conflicts

print("\n=== GAME LOOP API TEST ===\n")

# Create season
print("1. Creating season 2030...")
r = requests.post(f"{BASE}/season/create", json={
    "discipline": "SINGLE_SEATER",
    "num_races": 3,
    "season_year": SEASON_YEAR
})

if r.status_code != 200:
    print(f"FAILED: {r.text}")
    exit(1)

data = r.json()
print(f"   SUCCESS: {data['championship']} with {data['total_rounds']} races\n")

# Simulate 3 races
for i in range(1, 4):
    print(f"{i+1}. Simulating Race {i}...")
    r = requests.post(f"{BASE}/season/next-race", json={
        "weather": "dry",
        "num_laps": 50
    })
    
    if r.status_code != 200:
        print(f"   FAILED: {r.text}")
        exit(1)
    
    result = r.json()
    print(f"   Track: {result['race_info']['track_name']}")
    print(f"   Winner: {result['results'][0]['driver_name']} ({result['results'][0]['team_name']})")
    print(f"   Points: {result['results'][0]['points']}")
    
    leader = result['championship_leader']
    print(f"   Championship Leader: {leader['driver_name']} - {leader['points']} pts")
    
    if result.get('season_complete'):
        print("\n   === SEASON COMPLETE ===")
        champ = result.get('champion', {})
        print(f"   CHAMPION: {champ['driver_name']} ({champ['team_name']})")
        print(f"   Final Points: {champ['points']}")
    
    print()

print("\n=== ALL TESTS PASSED ===\n")
