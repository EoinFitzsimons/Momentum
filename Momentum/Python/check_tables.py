import sqlite3
conn = sqlite3.connect('momentum.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables in database:', [t[0] for t in tables])
