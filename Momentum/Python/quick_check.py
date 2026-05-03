import os
import sqlite3

os.remove("momentum.db") if os.path.exists("momentum.db") else None
from database.database_manager import DatabaseManager

db = DatabaseManager()
conn = sqlite3.connect(db.db_path)
cursor = conn.execute("PRAGMA table_info(teams)")
cols = [r[1] for r in cursor.fetchall()]
print("Teams columns:", cols)
print("Has headquarters:", "headquarters" in cols)
print("Has biography:", "biography" in cols)
conn.close()
