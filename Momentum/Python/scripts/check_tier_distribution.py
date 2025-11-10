"""Check tier distribution across all disciplines"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager

db = DatabaseManager()

disciplines = [
    'SINGLE_SEATER',
    'PRODUCTION_TOURING', 
    'RALLY_STAGE',
    'URBAN_STREET',
    'DRAG_ACCELERATION',
    'SPRINT_RALLYCROSS',
    'ENDURANCE'
]

print("\n" + "=" * 80)
print("TIER DISTRIBUTION PER DISCIPLINE")
print("=" * 80 + "\n")

for discipline in disciplines:
    teams = db.get_teams_by_discipline(discipline)
    
    tier_count = {}
    for team in teams:
        tier_count[team.tier] = tier_count.get(team.tier, 0) + 1
    
    print(f"{discipline}:")
    for tier in sorted(tier_count.keys()):
        print(f"  {tier}: {tier_count[tier]} teams")
    print(f"  TOTAL: {len(teams)} teams\n")
