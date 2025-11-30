"""
Archived: Game loop API tests (legacy)
"""
import requests
import json
from time import sleep

BASE_URL = "http://127.0.0.1:8000"

def print_response(title, response):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

if __name__ == '__main__':
    try:
        r = requests.get(f"{BASE_URL}/health")
        print_response('HEALTH CHECK', r)
    except Exception:
        print('Cannot contact server')
