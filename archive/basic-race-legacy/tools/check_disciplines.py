import sys
sys.path.insert(0, r'c:/Users/eoin0/Documents/FinalProject/Momentum/Python')
from config import DISCIPLINES, DATABASE_PATH
from database.database_manager import DatabaseManager
from collections import Counter

print('Using DB:', DATABASE_PATH)
manager = DatabaseManager()
for key in DISCIPLINES.keys():
    teams = manager.get_teams_by_discipline(key)
    counts = Counter([t.tier for t in teams])
    sample = [t.name for t in teams[:3]]
    print(f"{key}: {len(teams)} teams; tiers={dict(counts)}; sample={sample}")
