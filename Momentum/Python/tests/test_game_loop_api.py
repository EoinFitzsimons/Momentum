"""
Test script for Game Loop API endpoints

This script tests the new championship season and race simulation endpoints.
Run this while the simulation.py server is running on http://127.0.0.1:8000
"""

import requests
import json
from time import sleep

BASE_URL = "http://127.0.0.1:8000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    print(f"{'='*80}\n")

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("HEALTH CHECK", response)
    return response.status_code == 200

def test_create_season():
    """Test season creation"""
    print("Testing season creation...")
    data = {
        "discipline": "SINGLE_SEATER",
        "num_races": 5,
        "season_year": 2025
    }
    response = requests.post(f"{BASE_URL}/season/create", json=data)
    print_response("CREATE SEASON", response)
    return response.status_code == 200

def test_get_season_state():
    """Test get season state"""
    print("Testing get season state...")
    response = requests.get(f"{BASE_URL}/season/state")
    print_response("SEASON STATE", response)
    return response.status_code == 200

def test_simulate_race(race_num):
    """Test race simulation"""
    print(f"Testing race simulation (Race {race_num})...")
    data = {
        "weather": "dry",
        "num_laps": 50
    }
    response = requests.post(f"{BASE_URL}/season/next-race", json=data)
    print_response(f"SIMULATE RACE {race_num}", response)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nRace Summary:")
        print(f"  Track: {result.get('race_info', {}).get('track_name', 'Unknown')}")
        print(f"  Round: {result.get('race_info', {}).get('round_number', '?')}")
        print(f"\nTop 3 Finishers:")
        for i, res in enumerate(result.get('results', [])[:3], 1):
            print(f"  {i}. {res.get('driver_name', 'Unknown')} ({res.get('team_name', 'Unknown')}) - {res.get('points', 0)} pts")
        
        leader = result.get('championship_leader', {})
        if leader:
            print(f"\nChampionship Leader:")
            print(f"  {leader.get('driver_name', 'Unknown')} ({leader.get('team_name', 'Unknown')}) - {leader.get('points', 0)} pts")
        
        if result.get('season_complete'):
            print(f"\n🏆 SEASON COMPLETE! 🏆")
            champion = result.get('champion', {})
            if champion:
                print(f"  Champion: {champion.get('driver_name', 'Unknown')}")
                print(f"  Team: {champion.get('team_name', 'Unknown')}")
                print(f"  Total Points: {champion.get('points', 0)}")
    
    return response.status_code == 200

def test_get_standings():
    """Test get standings"""
    print("Testing get standings...")
    response = requests.get(f"{BASE_URL}/season/standings")
    print_response("CHAMPIONSHIP STANDINGS", response)
    
    if response.status_code == 200:
        data = response.json()
        print("\nDriver Standings (Top 5):")
        for standing in data.get('driver_standings', [])[:5]:
            print(f"  {standing.get('position', '?')}. {standing.get('driver_name', 'Unknown')} "
                  f"({standing.get('team_name', 'Unknown')}) - "
                  f"{standing.get('points', 0)} pts, "
                  f"{standing.get('wins', 0)} wins")
    
    return response.status_code == 200

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("GAME LOOP API TEST SUITE")
    print("="*80)
    
    # Test health first
    if not test_health():
        print("❌ Server is not responding. Make sure simulation.py is running.")
        return
    
    print("\n✅ Server is healthy!\n")
    sleep(1)
    
    # Test season creation
    if not test_create_season():
        print("❌ Failed to create season")
        return
    
    print("\n✅ Season created successfully!\n")
    sleep(1)
    
    # Test getting season state
    if not test_get_season_state():
        print("❌ Failed to get season state")
        return
    
    print("\n✅ Season state retrieved!\n")
    sleep(1)
    
    # Simulate all 5 races
    for race_num in range(1, 6):
        if not test_simulate_race(race_num):
            print(f"❌ Failed to simulate race {race_num}")
            return
        print(f"\n✅ Race {race_num} completed!\n")
        sleep(1)
    
    # Get final standings
    if not test_get_standings():
        print("❌ Failed to get standings")
        return
    
    print("\n✅ All tests passed!\n")
    print("="*80)
    print("GAME LOOP API IS FULLY FUNCTIONAL!")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Make sure simulation.py is running on http://127.0.0.1:8000")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
