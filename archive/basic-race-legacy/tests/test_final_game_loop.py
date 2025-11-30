"""Archived: final game loop integration test"""
import requests

BASE = "http://127.0.0.1:8000"
SEASON_YEAR = 2035

print("\n=== GAME LOOP API TEST ===\n")

print("1. Creating season 2030...")
try:
    r = requests.post(f"{BASE}/season/create", json={
        "discipline": "SINGLE_SEATER",
        "num_races": 3,
        "season_year": SEASON_YEAR
    })
    print(f"   Status: {r.status_code}")
except Exception:
    print("Failed to contact server")
