"""
Archived: Test Game Loop with Season 2025
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
    else:
        print(f"✗ Error: {create_response.text}")
        return

if __name__ == "__main__":
    test_game_loop_2025()
