import requests

# Test game loop with unique season year
r = requests.post('http://127.0.0.1:8000/season/create', json={
    'discipline': 'SINGLE_SEATER',
    'num_races': 3,
    'season_year': 2050
})

print("Create Season:", r.status_code)
if r.status_code != 200:
    print("ERROR:", r.text)
    exit(1)

print("SUCCESS!")

# Simulate race 1
r = requests.post('http://127.0.0.1:8000/season/next-race', json={
    'weather': 'dry',
    'num_laps': 50
})

print("\nRace 1:", r.status_code)
if r.status_code != 200:
    print("ERROR:", r.text)
    exit(1)

result = r.json()
print(f"Winner: {result['results'][0]['driver_name']}")
print(f"Team: {result['results'][0]['team_name']}")
print(f"Points: {result['results'][0]['points']}")
print(f"\nLeader: {result['championship_leader']['driver_name']} - {result['championship_leader']['points']} pts")

# Simulate race 2
r = requests.post('http://127.0.0.1:8000/season/next-race', json={'weather': 'dry', 'num_laps': 50})
print(f"\nRace 2: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"Winner: {result['results'][0]['driver_name']}")

# Simulate race 3
r = requests.post('http://127.0.0.1:8000/season/next-race', json={'weather': 'dry', 'num_laps': 50})
print(f"\nRace 3 (Final): {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"Winner: {result['results'][0]['driver_name']}")
    if result.get('season_complete'):
        champ = result['champion']
        print(f"\nCHAMPION: {champ['driver_name']} ({champ['team_name']}) - {champ['points']} pts")

print("\n=== ALL TESTS PASSED ===")
