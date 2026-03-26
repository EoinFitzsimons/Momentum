#!/usr/bin/env python3
"""Check the newest teams created"""

from database.database_manager import DatabaseManager

db = DatabaseManager()

# Get the newest teams (assuming they were just created with highest IDs)
with db.get_connection() as conn:
    new_teams = conn.execute(
        "SELECT id, name, discipline, tier FROM teams ORDER BY id DESC LIMIT 50"
    ).fetchall()
    
    print("50 Most recent teams:\n")
    bad_count = 0
    for row in new_teams:
        team_id, name, discipline, tier = row
        is_bad = '()' in name or ( ' ' + name).startswith(' (')
        marker = " ⚠️ BAD" if is_bad else ""
        print(f"ID {team_id}: '{name}'{marker}")
        if is_bad:
            bad_count += 1
    
    print(f"\nBad teams in recent 50: {bad_count}")
