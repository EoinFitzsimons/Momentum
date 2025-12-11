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

    def _ensure_race_result_columns(self, cur) -> None:
        """Ensure race_results contains the expanded set of columns.

        This is idempotent and will add any missing columns with safe defaults.
        """
        try:
            cur.execute("PRAGMA table_info(race_results)")
            existing = {r[1] for r in cur.fetchall()}
            # Map of column -> SQL to add it
            extras = {
                'time_seconds': "ALTER TABLE race_results ADD COLUMN time_seconds REAL DEFAULT NULL;",
                'grid_position': "ALTER TABLE race_results ADD COLUMN grid_position INTEGER DEFAULT NULL;",
                'laps_completed': "ALTER TABLE race_results ADD COLUMN laps_completed INTEGER DEFAULT 0;",
                'best_lap_time': "ALTER TABLE race_results ADD COLUMN best_lap_time REAL DEFAULT NULL;",
                'average_lap_time': "ALTER TABLE race_results ADD COLUMN average_lap_time REAL DEFAULT NULL;",
                'pitstops': "ALTER TABLE race_results ADD COLUMN pitstops INTEGER DEFAULT 0;",
                'tyre_strategy': "ALTER TABLE race_results ADD COLUMN tyre_strategy TEXT DEFAULT NULL;",
                'penalties_seconds': "ALTER TABLE race_results ADD COLUMN penalties_seconds REAL DEFAULT 0.0;",
                'penalty_reason': "ALTER TABLE race_results ADD COLUMN penalty_reason TEXT DEFAULT NULL;",
                'gap_to_winner_seconds': "ALTER TABLE race_results ADD COLUMN gap_to_winner_seconds REAL DEFAULT NULL;",
                'status': "ALTER TABLE race_results ADD COLUMN status TEXT DEFAULT 'FINISHED';",
                'recorded_at': "ALTER TABLE race_results ADD COLUMN recorded_at TEXT DEFAULT NULL;",
            }
            for col, sql in extras.items():
                if col not in existing:
                    try:
                        cur.execute(sql)
                        self.conn.commit()
                    except Exception:
                        # Best-effort: do not raise during migration
                        pass
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
        # Ensure legacy and expanded race_results columns exist
        self._ensure_time_seconds_column(cur)
        self._ensure_race_result_columns(cur)

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

        # Detect available columns and insert only those present (backwards compatible)
        cur.execute("PRAGMA table_info(race_results)")
        existing_cols = [r[1] for r in cur.fetchall()]

        preferred_cols = [
            'race_id', 'driver_id', 'team_id', 'position', 'fastest_lap', 'points', 'dnf_reason',
            'time_seconds', 'grid_position', 'laps_completed', 'best_lap_time', 'average_lap_time',
            'pitstops', 'tyre_strategy', 'penalties_seconds', 'penalty_reason', 'gap_to_winner_seconds',
            'status', 'recorded_at'
        ]

        insert_cols = [c for c in preferred_cols if c in existing_cols]
        insert_sql = f"INSERT INTO race_results ({', '.join(insert_cols)}) VALUES ({', '.join(['?'] * len(insert_cols))})"

        for res in results:
            vals = []
            # Helper to get attribute/dict key
            for col in insert_cols:
                if col == 'race_id':
                    vals.append(race_id)
                    continue
                if col == 'team_id':
                    vals.append(self._parse_team_id(res))
                    continue
                if col == 'fastest_lap':
                    v = self._extract_result_field(res, 'fastest_lap', False)
                    vals.append(1 if v else 0)
                    continue
                # standard fields
                v = self._extract_result_field(res, col, None)
                # Some runtime attributes are named slightly differently
                if v is None:
                    if col == 'time_seconds':
                        v = self._extract_result_field(res, 'time_seconds', None)
                    elif col == 'best_lap_time':
                        v = self._extract_result_field(res, 'best_lap_time', None)
                    elif col == 'average_lap_time':
                        v = self._extract_result_field(res, 'average_lap_time', None)
                    elif col == 'grid_position':
                        v = self._extract_result_field(res, 'grid_position', None)
                    elif col == 'laps_completed':
                        v = self._extract_result_field(res, 'laps_completed', None)
                vals.append(v)

            try:
                cur.execute(insert_sql, tuple(vals))
            except sqlite3.IntegrityError as ie:
                raise ValueError(
                    f"IntegrityError inserting race_result: {ie}; params=(race_id={race_id}, values={vals})"
                )
            except sqlite3.OperationalError:
                # Best-effort fallback: try older minimal insert
                try:
                    driver_id = self._extract_result_field(res, 'driver_id')
                    position = self._extract_result_field(res, 'position')
                    time_sec = self._extract_result_field(res, 'time_seconds', 0.0)
                    cur.execute(
                        "INSERT INTO race_results (race_id, driver_id, team_id, position, time_seconds) VALUES (?, ?, ?, ?, ?)",
                        (race_id, driver_id, self._parse_team_id(res), position, time_sec),
                    )
                except Exception:
                    raise

        self.conn.commit()
