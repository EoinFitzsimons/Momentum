#!/usr/bin/env python3
"""Initialise database with proper schema"""

import os
import sqlite3
import sys
import shutil

# Delete all Python caches
for root, dirs, files in os.walk("."):
    if "__pycache__" in dirs:
        shutil.rmtree(os.path.join(root, "__pycache__"))
        print(f"Cleared {os.path.join(root, '__pycache__')}")

# Delete database file
if os.path.exists("momentum.db"):
    os.remove("momentum.db")
    print("✓ Deleted momentum.db")

# Clear all cached modules
for module in tuple(sys.modules):
    if "database" in module or "config" in module:
        del sys.modules[module]

# Fresh import
from database.database_manager import DatabaseManager

db = DatabaseManager()
print("✓ Database initialised")

# Verify schema
conn = sqlite3.connect(db.db_path)
cursor = conn.execute("PRAGMA table_info(teams)")
columns = {row[1]: row[2] for row in cursor.fetchall()}
print(f"\nTeams columns ({len(columns)}): {list(columns.keys())}")

if "headquarters" in columns and "biography" in columns:
    print("\n✓ SUCCESS: headquarters and biography columns exist!")
else:
    print("\n✗ FAIL: Missing columns")
    if "headquarters" not in columns:
        print("  ✗ headquarters missing")
    if "biography" not in columns:
        print("  ✗ biography missing")

conn.close()
