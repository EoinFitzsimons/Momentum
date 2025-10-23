import sqlite3

conn = sqlite3.connect('momentum.db')
cursor = conn.execute('PRAGMA table_info(drivers)')
columns = cursor.fetchall()

print("\nDriver Table Columns:")
print("-" * 40)
for col in columns[:30]:
    print(f"{col[1]:30} {col[2]}")
