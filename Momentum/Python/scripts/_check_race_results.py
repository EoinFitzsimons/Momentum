import sqlite3

DB='database/momentum.db'
conn=sqlite3.connect(DB)
cur=conn.cursor()
try:
    total = cur.execute("SELECT COUNT(1) FROM race_results").fetchone()[0]
except Exception as e:
    print('ERROR reading race_results table:', e)
    conn.close()
    raise SystemExit(1)
max_rid = cur.execute("SELECT MAX(race_id) FROM race_results").fetchone()[0]
distinct = cur.execute("SELECT COUNT(DISTINCT race_id) FROM race_results").fetchone()[0]
print(f"total_rows={total}, distinct_race_ids={distinct}, max_race_id={max_rid}")
if max_rid is not None:
    rows = cur.execute(
        "SELECT race_id, driver_id, position, status, dnf_reason, time_seconds FROM race_results WHERE race_id=? ORDER BY position",
        (max_rid,)
    ).fetchall()
    print('\nSample rows for latest race_id=', max_rid)
    for r in rows[:40]:
        print(r)
else:
    print('No race_results rows found')
conn.close()
