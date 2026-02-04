import sqlite3
from database.database_manager import DatabaseManager

db = DatabaseManager()
conn = sqlite3.connect(db.db_path)
cursor = conn.execute("PRAGMA table_info(teams)")
columns = [row[1] for row in cursor.fetchall()]
print('Teams table columns:', columns)
conn.close()
