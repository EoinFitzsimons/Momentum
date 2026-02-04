import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "database" / "momentum.db"
if not DB.exists():
    print(f"DB not found at: {DB}")
    raise SystemExit(1)

con = sqlite3.connect(str(DB))
cur = con.cursor()
cur.execute("PRAGMA table_info('race_results')")
cols = cur.fetchall()
if not cols:
    print("Table 'race_results' not found or has no columns.")
else:
    print(f"Found {len(cols)} columns in 'race_results':")
    for cid, name, ctype, notnull, dflt_value, pk in cols:
        print(f"- {name} : {ctype}  (pk={pk}, notnull={notnull}, default={dflt_value})")
con.close()
