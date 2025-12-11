import sqlite3

DB='database/momentum.db'
conn=sqlite3.connect(DB)
cur=conn.cursor()
print('Before update:')
for row in cur.execute("SELECT id,driver_id,position,laps_completed,time_seconds,dnf_reason,status FROM race_results ORDER BY position").fetchall():
    print(row)

# Update existing rows where dnf_reason is not null to set status='DNF'
cur.execute("UPDATE race_results SET status='DNF' WHERE dnf_reason IS NOT NULL AND (status IS NULL OR status!='DNF')")
conn.commit()
print('\nAfter update:')
for row in cur.execute("SELECT id,driver_id,position,laps_completed,time_seconds,dnf_reason,status FROM race_results ORDER BY position").fetchall():
    print(row)

conn.close()
