"""Archived: DB schema checker (legacy)"""
import sqlite3

conn = sqlite3.connect('database/momentum.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("Tables:", tables)
