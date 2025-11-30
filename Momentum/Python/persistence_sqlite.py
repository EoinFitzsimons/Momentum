import sqlite3
from typing import List, Optional
from .persistence_iface import Driver, Track, RaceResult, PersistenceIface


class PersistenceSQLite(PersistenceIface):
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def ensure_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                raw_speed REAL NOT NULL
            )
        """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                length_km REAL NOT NULL
            )
        """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS race_results (
                race_id INTEGER,
                driver_id INTEGER,
                position INTEGER,
                time_seconds REAL
            )
        """
        )
        self.conn.commit()

    def seed_sample_data(self) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM drivers")
        cur.execute("DELETE FROM tracks")
        cur.execute("INSERT INTO drivers (id, name, raw_speed) VALUES (1, 'A. Driver', 85.0)")
        cur.execute("INSERT INTO drivers (id, name, raw_speed) VALUES (2, 'B. Driver', 78.0)")
        cur.execute("INSERT INTO drivers (id, name, raw_speed) VALUES (3, 'C. Driver', 72.0)")
        cur.execute("INSERT INTO tracks (id, name, length_km) VALUES (1, 'Short Circuit', 3.2)")
        self.conn.commit()

    def list_drivers(self) -> List[Driver]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, raw_speed FROM drivers ORDER BY id")
        rows = cur.fetchall()
        return [Driver(id=r["id"], name=r["name"], raw_speed=r["raw_speed"]) for r in rows]

    def get_driver(self, driver_id: int) -> Optional[Driver]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, raw_speed FROM drivers WHERE id = ?", (driver_id,))
        r = cur.fetchone()
        if not r:
            return None
        return Driver(id=r["id"], name=r["name"], raw_speed=r["raw_speed"])

    def get_track(self, track_id: int) -> Optional[Track]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, length_km FROM tracks WHERE id = ?", (track_id,))
        r = cur.fetchone()
        if not r:
            return None
        return Track(id=r["id"], name=r["name"], length_km=r["length_km"])

    def save_race_results(self, race_id: int, results: List[RaceResult]) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM race_results WHERE race_id = ?", (race_id,))
        for res in results:
            cur.execute(
                "INSERT INTO race_results (race_id, driver_id, position, time_seconds) VALUES (?, ?, ?, ?)",
                (race_id, res.driver_id, res.position, res.time_seconds),
            )
        self.conn.commit()
