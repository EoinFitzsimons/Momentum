"""Quick database verification script."""
import sqlite3

conn = sqlite3.connect('database/momentum.db')
cursor = conn.cursor()

# Count records
cursor.execute('SELECT COUNT(*) FROM teams')
teams_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM drivers')
drivers_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM tracks')
tracks_count = cursor.fetchone()[0]

print("=" * 80)
print("DATABASE VERIFICATION")
print("=" * 80)
print(f"\n✅ Teams: {teams_count}")
print(f"✅ Drivers: {drivers_count}")
print(f"✅ Tracks: {tracks_count}")

# Sample tracks
print("\n🏁 SAMPLE TRACKS:")
cursor.execute('''
    SELECT name, country, ima_grade, primary_discipline, length_km 
    FROM tracks 
    LIMIT 10
''')
for row in cursor.fetchall():
    name, country, grade, discipline, length = row
    print(f"  - {name:<40} | {country:<15} | {grade:<8} | {discipline:<20} | {length:.2f}km")

# Tracks by discipline
print("\n📊 TRACKS BY DISCIPLINE:")
cursor.execute('''
    SELECT primary_discipline, COUNT(*) as count
    FROM tracks
    GROUP BY primary_discipline
    ORDER BY primary_discipline
''')
for row in cursor.fetchall():
    discipline, count = row
    print(f"  {discipline:<25} : {count:>3} tracks")

conn.close()
print("\n" + "=" * 80)
print("✅ Database verification complete!")
print("=" * 80)
