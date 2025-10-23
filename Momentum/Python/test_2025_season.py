"""
Test Game Loop with Season 2025
Following user guidance - start with 2025 and don't change years.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_game_loop_2025():
    print("=" * 60)
    print("TESTING GAME LOOP WITH SEASON 2025")
    print("=" * 60)
    
    # Test 1: Create Season
    print("\n1. Creating Season 2025...")
    create_response = requests.post(
        f"{BASE_URL}/season/create",
        json={
            "discipline": "SINGLE_SEATER",
            "num_races": 3,
            "season_year": 2025
        }
    )
    
    print(f"Status Code: {create_response.status_code}")
    if create_response.status_code == 200:
        season_data = create_response.json()
        print(f"✓ Season created successfully!")
        print(f"  Year: {season_data['year']}")
        print(f"  Discipline: {season_data['discipline']}")
        print(f"  Total Races: {season_data['total_races']}")
        print(f"  Completed: {season_data['completed_races']}")
        
        # Print race schedule
        print("\n  Race Schedule:")
        for race in season_data['races']:
            print(f"    Race {race['round']}: {race['track_name']} - {race['status']}")
    else:
        print(f"✗ Error: {create_response.text}")
        return
    
    # Test 2: Simulate Race 1
    print("\n2. Simulating Race 1...")
    race1_response = requests.post(
        f"{BASE_URL}/season/next-race",
        json={
            "weather": "dry",
            "num_laps": 50
        }
    )
    
    print(f"Status Code: {race1_response.status_code}")
    if race1_response.status_code == 200:
        race1_data = race1_response.json()
        print(f"✓ Race 1 completed!")
        print(f"  Winner: {race1_data['race_results']['winner']}")
        print(f"  Track: {race1_data['race_results']['track']}")
        
        # Print top 3
        print("\n  Top 3 Finishers:")
        for result in race1_data['race_results']['results'][:3]:
            print(f"    {result['position']}. {result['driver']} ({result['team']}) - {result['status']}")
        
        # Print standings
        print("\n  Championship Standings After Race 1:")
        for i, driver in enumerate(race1_data['standings']['drivers'][:5], 1):
            print(f"    {i}. {driver['driver_name']} - {driver['points']} pts")
    else:
        print(f"✗ Error: {race1_response.text}")
        return
    
    # Test 3: Simulate Race 2
    print("\n3. Simulating Race 2...")
    race2_response = requests.post(
        f"{BASE_URL}/season/next-race",
        json={
            "weather": "dry",
            "num_laps": 50
        }
    )
    
    print(f"Status Code: {race2_response.status_code}")
    if race2_response.status_code == 200:
        race2_data = race2_response.json()
        print(f"✓ Race 2 completed!")
        print(f"  Winner: {race2_data['race_results']['winner']}")
        
        print("\n  Championship Standings After Race 2:")
        for i, driver in enumerate(race2_data['standings']['drivers'][:5], 1):
            print(f"    {i}. {driver['driver_name']} - {driver['points']} pts")
    else:
        print(f"✗ Error: {race2_response.text}")
        return
    
    # Test 4: Simulate Race 3 (Final)
    print("\n4. Simulating Race 3 (FINAL RACE)...")
    race3_response = requests.post(
        f"{BASE_URL}/season/next-race",
        json={
            "weather": "dry",
            "num_laps": 50
        }
    )
    
    print(f"Status Code: {race3_response.status_code}")
    if race3_response.status_code == 200:
        race3_data = race3_response.json()
        print(f"✓ Race 3 completed!")
        print(f"  Winner: {race3_data['race_results']['winner']}")
        
        print("\n  FINAL CHAMPIONSHIP STANDINGS:")
        for i, driver in enumerate(race3_data['standings']['drivers'][:10], 1):
            print(f"    {i}. {driver['driver_name']} - {driver['points']} pts "
                  f"(Wins: {driver['wins']}, Podiums: {driver['podiums']})")
        
        # Check if season is complete
        if race3_data.get('season_complete'):
            print(f"\n🏆 CHAMPION: {race3_data['champion']['driver_name']}")
            print(f"   Team: {race3_data['champion']['team_name']}")
            print(f"   Points: {race3_data['champion']['points']}")
    else:
        print(f"✗ Error: {race3_response.text}")
        return
    
    print("\n" + "=" * 60)
    print("GAME LOOP TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    test_game_loop_2025()
