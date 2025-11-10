import sqlite3

conn = sqlite3.connect('database/momentum.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("Tables:", tables)

if 'staff_members' in tables:
    print("\nStaff_members table - last 10 columns:")
    cursor = conn.execute('PRAGMA table_info(staff_members)')
    cols = cursor.fetchall()
    print(f"Total columns: {len(cols)}")
    for c in cols[-10:]:  # Last 10 columns
        print(f"  {c[1]} ({c[2]})")
