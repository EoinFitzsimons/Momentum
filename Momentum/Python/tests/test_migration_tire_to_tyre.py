import os
import sqlite3
import subprocess
import pytest

DB_TEMPLATE_SQL = """
CREATE TABLE drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    tire_management REAL DEFAULT 50.0,
    tire_strategy REAL DEFAULT 50.0
);

INSERT INTO drivers (name, tire_management, tire_strategy) VALUES ('Alice', 72.5, 60.0);
INSERT INTO drivers (name, tire_management, tire_strategy) VALUES ('Bob', 45.0, 40.0);
"""


@pytest.mark.integration
def test_migration_creates_tyre_columns(tmp_path):
    db_file = tmp_path / "test_mig.db"
    with open(db_file, "wb") as f:
        f.write(b"")

    # Initialize DB
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.executescript(DB_TEMPLATE_SQL)
    conn.commit()
    conn.close()

    # Run migration script
    script = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "scripts", "migrate_tire_to_tyre.py"
        )
    )
    res = subprocess.run(
        ["python", script, "--db", str(db_file)], capture_output=True, text=True
    )
    assert res.returncode == 0, f"Migration script failed: {res.stderr}"

    # Verify new columns exist and data preserved
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(drivers)")
    cols = [r[1] for r in cur.fetchall()]
    assert "tyre_management" in cols
    assert "tyre_strategy" in cols

    cur.execute(
        "SELECT name, tyre_management, tyre_strategy FROM drivers ORDER BY name"
    )
    rows = cur.fetchall()
    assert rows[0][0] == "Alice" and abs(rows[0][1] - 72.5) < 0.001
    assert rows[1][0] == "Bob" and abs(rows[1][1] - 45.0) < 0.001
    conn.close()
