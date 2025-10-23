import sqlite3

# Connect to the correct database
conn = sqlite3.connect('database/momentum.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

print(f"Tables in database/momentum.db: {tables}")

# Get counts for each table
if tables:
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")

conn.close()
