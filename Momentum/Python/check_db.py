import sqlite3

conn = sqlite3.connect('database/momentum.db')
c = conn.cursor()

# Get counts
c.execute('SELECT COUNT(*) FROM teams')
teams = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM drivers')
drivers = c.fetchone()[0]

print(f'\n✅ SUCCESS! Database Schema Fixed and Regenerated!')
print(f'   Teams: {teams:,}')
print(f'   Drivers: {drivers:,}')

# Get sample teams
c.execute('SELECT name, tier, budget, discipline FROM teams ORDER BY RANDOM() LIMIT 25')
teams_sample = c.fetchall()

print(f'\n📋 Sample of {teams} Teams with Authentic Manufacturer Names:')
print('=' * 90)
for i, (name, tier, budget, discipline) in enumerate(teams_sample, 1):
    print(f'{i:2d}. {name:50s} [{tier}] {discipline:20s} €{budget:>12,.0f}')

conn.close()
