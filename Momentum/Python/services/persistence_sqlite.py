import sqlite3
import dataclasses
from typing import List, Optional

# Use canonical DB models and schema
from database.models import Driver as DBDriver, Track as DBTrack, SCHEMA_SQL
from services.persistence_iface import PersistenceIface


class PersistenceSQLite(PersistenceIface):
    def __init__(self, db_path: str = "database/momentum.db"):
        self.db_path = db_path
        # Ensure the directory exists for file-backed DB
        if db_path != ":memory":
            import os

            dirpath = os.path.dirname(db_path)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def _migrate_team_id_column(self, cur) -> None:
        """Add current_team_id column if missing."""
        cur.execute("PRAGMA table_info(drivers)")
        existing = [r[1] for r in cur.fetchall()]
        if 'current_team_id' not in existing:
            cur.execute(
                "ALTER TABLE drivers ADD COLUMN current_team_id INTEGER;")
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_drivers_team ON drivers(current_team_id);")
            self.conn.commit()

    def _verify_and_recreate_drivers_table(self, cur) -> None:
        """Verify drivers table has required columns, recreate if incompatible."""
        try:
            cur.execute("PRAGMA table_info(drivers)")
            cols = [r[1] for r in cur.fetchall()]
            required = {'name', 'nationality', 'birth_date', 'raw_speed'}
            if not required.issubset(set(cols)):
                cur.execute("DROP TABLE IF EXISTS race_results")
                cur.execute("DROP TABLE IF EXISTS drivers")
                cur.execute("DROP TABLE IF EXISTS tracks")
                self.conn.commit()
                cur.executescript(SCHEMA_SQL)
                self.conn.commit()
        except Exception:
            pass

    def _ensure_time_seconds_column(self, cur) -> None:
        """Ensure race_results has time_seconds column."""
        try:
            cur.execute("PRAGMA table_info(race_results)")
            rcols = [r[1] for r in cur.fetchall()]
            if 'time_seconds' not in rcols:
                cur.execute(
                    "ALTER TABLE race_results ADD COLUMN time_seconds REAL DEFAULT 0.0;")
                self.conn.commit()
        except Exception:
            pass

    def ensure_schema(self) -> None:
        cur = self.conn.cursor()
        try:
            cur.executescript(SCHEMA_SQL)
            self.conn.commit()
        except sqlite3.OperationalError as oe:
            msg = str(oe).lower()
            if 'current_team_id' in msg or 'no such column: current_team_id' in msg:
                try:
                    self._migrate_team_id_column(cur)
                    cur.executescript(SCHEMA_SQL)
                    self.conn.commit()
                except Exception:
                    pass  # Silently fail migration; caller will handle missing data

        self._verify_and_recreate_drivers_table(cur)
        self._ensure_time_seconds_column(cur)

    def seed_sample_data(self, count: int = 20, force: bool = False) -> None:
        """Populate the DB with a small sample dataset for demos.

        By default this creates `count` drivers and one sample track. Using
        20 drivers gives a visibly interesting lap-by-lap leaderboard for the
        basic-race MVP.
        """
        cur = self.conn.cursor()
        # If the DB already has drivers and caller did not request force,
        # do not overwrite the user's data. This makes seeding safe by default.
        cur.execute("SELECT COUNT(1) as c FROM drivers")
        try:
            existing = cur.fetchone()[0]
        except Exception:
            existing = 0
        if existing > 0 and not force:
            # Do not clobber an existing database unless explicitly requested
            return

        # Remove existing demo data and create a fresh sample set
        cur.execute("DELETE FROM drivers")
        cur.execute("DELETE FROM tracks")

        # Insert `count` sample drivers with simple but varying attributes
        for i in range(1, max(3, count) + 1):
            name = f"Driver {i:02d}"
            # vary raw_speed and consistency across drivers for competitive
            # ordering
            raw_speed = 60.0 + (i % 10) * 4.0 + (i // 10) * 1.5
            consistency = 55.0 + ((10 - (i % 10)) * 2.0)
            if i % 3 == 0:
                nationality = 'GBR'
            elif i % 3 == 1:
                nationality = 'USA'
            else:
                nationality = 'IRL'
            birth = f"{1990 + (i % 20)}-01-01"
            cur.execute(
                "INSERT INTO drivers (id, name, nationality, birth_date, raw_speed, consistency, pit_entry_exit, tire_management, overtaking) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (i, name, nationality, birth, float(raw_speed), float(
                    consistency), 50 + (i % 10), 50 + ((i * 3) % 20), 40 + (i % 30)),
            )

        # Insert a sample track (provide required NOT NULL columns)
        cur.execute(
            """
            INSERT INTO tracks (
                id, name, country, region, circuit_type, ima_grade, primary_discipline,
                length_km, turns, left_turns, right_turns, elevation_change_m, max_gradient_percent, min_gradient_percent,
                surface, track_width_avg_m, track_width_min_m, track_width_max_m,
                avg_speed_kmh, top_speed_kmh, longest_straight_m, shortest_straight_m, tightest_corner_radius_m,
                climate, avg_temp_summer_c, avg_temp_winter_c, rainfall_mm_annual, altitude_m,
                pit_boxes, pit_lane_length_m, pit_speed_limit_kmh, paddock_capacity_teams, grandstand_capacity,
                drs_zones, safety_car_probability, night_racing_capable, wet_weather_racing, is_active, debut_year
            ) VALUES (
                1, 'Short Circuit', 'GBR', 'England', 'permanent', 'Silver', 'SINGLE_SEATER',
                3.2, 12, 6, 6, 40.0, 5.0, -3.0,
                'asphalt', 12.0, 10.0, 15.0,
                160.0, 300.0, 700, 200, 30.0,
                'temperate', 18.0, 6.0, 600, 45,
                20, 350.0, 60, 20, 15000,
                1, 0.02, 0, 1, 1, 1990
            )
        """
        )

        self.conn.commit()

    def _row_to_dataclass(self, row: sqlite3.Row, cls):
        if row is None:
            return None
        data = dict(row)
        # Filter keys to dataclass fields only
        field_names = {f.name for f in dataclasses.fields(cls)}
        filtered = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered)

    def list_drivers(self) -> List[DBDriver]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM drivers ORDER BY id")
        rows = cur.fetchall()
        return [self._row_to_dataclass(r, DBDriver) for r in rows]

    def get_driver(self, driver_id: int) -> Optional[DBDriver]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,))
        r = cur.fetchone()
        return self._row_to_dataclass(r, DBDriver)

    def get_track(self, track_id: int) -> Optional[DBTrack]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tracks WHERE id = ?", (track_id,))
        r = cur.fetchone()
        if not r:
            return None
        # import here to avoid circular import at module load
        from database.models import Track as _Track

        return self._row_to_dataclass(r, _Track)

    def _extract_result_field(self, res, field: str, default=None):
        """Extract field from result object or dict."""
        try:
            if hasattr(res, field):
                return getattr(res, field)
            return res.get(field, default) if isinstance(
                res, dict) else default
        except Exception:
            return default

    def _parse_team_id(self, res) -> int:
        """Parse and validate team_id, returning 0 if invalid."""
        team_id = self._extract_result_field(res, 'team_id', 0)
        if team_id is None:
            return 0
        try:
            return int(team_id)
        except Exception:
            return 0

    def save_race_results(self, race_id: int, results: List) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM race_results WHERE race_id = ?", (race_id,))

        for res in results:
            driver_id = self._extract_result_field(res, 'driver_id')
            position = self._extract_result_field(res, 'position')
            team_id = self._parse_team_id(res)
            time_sec = self._extract_result_field(res, 'time_seconds', 0.0)

            try:
                cur.execute(
                    "INSERT INTO race_results (race_id, driver_id, team_id, position, time_seconds) VALUES (?, ?, ?, ?, ?)",
                    (race_id, driver_id, team_id, position, time_sec),
                )
            except sqlite3.IntegrityError as ie:
                raise ValueError(
                    f"IntegrityError inserting race_result: {ie}; params=(race_id={race_id}, driver_id={driver_id}, team_id={team_id}, position={position}, time_seconds={time_sec})"
                )
        self.conn.commit()
