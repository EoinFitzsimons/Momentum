"""Check what's actually in the database"""
import sqlite3

conn = sqlite3.connect('momentum.db')

# Check championships
print("\n=== CHAMPIONSHIPS ===")
champs = conn.execute("SELECT id, name, discipline, current_season FROM championships").fetchall()
for c in champs:
    print(f"ID {c[0]}: {c[1]} ({c[2]}) - Current Season: {c[3]}")

# Check races
print("\n=== RACES ===")
races = conn.execute("SELECT id, championship_id, season, round_number, status FROM races ORDER BY championship_id, season, round_number").fetchall()
print(f"Total races: {len(races)}")
if races:
    print("\nFirst 10 races:")
    for r in races[:10]:
        print(f"  Race ID {r[0]}: Championship {r[1]}, Season {r[2]}, Round {r[3]}, Status: {r[4]}")
    
    # Group by championship and season
    print("\n=== RACES BY CHAMPIONSHIP/SEASON ===")
    seasons = conn.execute("""
        SELECT championship_id, season, COUNT(*) as race_count
        FROM races
        GROUP BY championship_id, season
        ORDER BY championship_id, season
    """).fetchall()
    for s in seasons:
        print(f"  Championship {s[0]}, Season {s[1]}: {s[2]} races")

# Check race results
print("\n=== RACE RESULTS ===")
result_count = conn.execute("SELECT COUNT(*) FROM race_results").fetchone()[0]
print(f"Total race results: {result_count}")

conn.close()
