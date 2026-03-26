"""PersistenceSQLite - lightweight SQLite persistence implementation.

This module provides a small file-backed `PersistenceSQLite` class used by
tests and the simulation services for demo/demo-data persistence. It is a
local copy adapted from the repository archive so the `services` package
contains a runnable persistence implementation.
"""
import sqlite3
import dataclasses
from typing import List, Optional, Any
import os
import sys

# Ensure repository root is on sys.path so imports like `database.models`
# resolve when running tests from `Momentum/Python`.
_this_dir = os.path.dirname(__file__)
_momentum_python_dir = os.path.normpath(os.path.join(_this_dir, '..'))
if _momentum_python_dir not in sys.path:
    sys.path.insert(0, _momentum_python_dir)

_repo_root = os.path.normpath(os.path.join(_this_dir, '..', '..', '..'))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from database.models import Driver as DBDriver, Track as DBTrack, SCHEMA_SQL


class PersistenceSQLite:
    _PRAGMA_RACE_RESULTS_TABLE_INFO = "PRAGMA table_info(race_results)"

    def __init__(self, db_path: str = "database/momentum.db"):
        self.db_path = db_path
        # Ensure the directory exists for file-backed DB
        if db_path != ":memory":
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
            cur.execute("ALTER TABLE drivers ADD COLUMN current_team_id INTEGER;")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_drivers_team ON drivers(current_team_id);")
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
            cur.execute(self._PRAGMA_RACE_RESULTS_TABLE_INFO)
            rcols = [r[1] for r in cur.fetchall()]
            if 'time_seconds' not in rcols:
                cur.execute("ALTER TABLE race_results ADD COLUMN time_seconds REAL DEFAULT 0.0;")
                self.conn.commit()
        except Exception:
            pass

    def _ensure_race_result_columns(self, cur) -> None:
        """Ensure race_results contains the expanded set of columns.

        This is idempotent and will add any missing columns with safe defaults.
        """
        try:
            cur.execute(self._PRAGMA_RACE_RESULTS_TABLE_INFO)
            existing = {r[1] for r in cur.fetchall()}
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
                    pass

        self._verify_and_recreate_drivers_table(cur)
        self._ensure_time_seconds_column(cur)
        self._ensure_race_result_columns(cur)

    def seed_sample_data(self, count: int = 20, force: bool = False) -> None:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(1) as c FROM drivers")
        try:
            existing = cur.fetchone()[0]
        except Exception:
            existing = 0
        if existing > 0 and not force:
            return

        cur.execute("DELETE FROM drivers")
        cur.execute("DELETE FROM tracks")

        for i in range(1, max(3, count) + 1):
            name = f"Driver {i:02d}"
            speed_val = 60.0 + (i % 10) * 4.0 + (i // 10) * 1.5
            racecraft_val = 50.0 + (i % 10) * 1.2
            consistency = 55.0 + ((10 - (i % 10)) * 2.0)
            fitness = 50.0 + ((i * 2) % 20)
            reactions = 50.0 + (i % 10)
            if i % 3 == 0:
                nationality = 'GBR'
            elif i % 3 == 1:
                nationality = 'USA'
            else:
                nationality = 'IRL'
            birth = f"{1990 + (i % 20)}-01-01"
            cur.execute(
                "INSERT INTO drivers (id, name, nationality, birth_date, speed, racecraft, consistency, fitness, reactions) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    i,
                    name,
                    nationality,
                    birth,
                    float(speed_val),
                    float(racecraft_val),
                    float(consistency),
                    float(fitness),
                    float(reactions),
                ),
            )

        # Insert a minimal track record matching the `tracks` table in SCHEMA_SQL
        cur.execute(
            "INSERT INTO tracks (id, name, country, primary_discipline, is_point_to_point, joker_enabled, instructions_json, geometry_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                1,
                'Short Circuit',
                'GBR',
                'SINGLE_SEATER',
                0,
                0,
                None,
                None,
            ),
        )

        self.conn.commit()

    def _row_to_dataclass(self, row: sqlite3.Row, cls):
        if row is None:
            return None
        data = dict(row)
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
        from database.models import Track as _Track

        return self._row_to_dataclass(r, _Track)

    def _extract_result_field(self, res, field: str, default=None):
        try:
            if hasattr(res, field):
                return getattr(res, field)
            return res.get(field, default) if isinstance(res, dict) else default
        except Exception:
            return default

    def _parse_team_id(self, res) -> int:
        team_id = self._extract_result_field(res, 'team_id', 0)
        if team_id is None:
            return 0
        try:
            return int(team_id)
        except Exception:
            return 0

    def _try_direct_total_time(self, res_obj) -> Optional[float]:
        direct_names = ['time_seconds', 'total_time', 'total_seconds', 'race_time', 'time']
        for name in direct_names:
            t = self._extract_result_field(res_obj, name, None)
            if t is not None:
                try:
                    return float(t)
                except Exception:
                    pass
        return None

    def _safe_float(self, value) -> Optional[float]:
        try:
            return float(value)
        except Exception:
            return None

    def _safe_int(self, value) -> Optional[int]:
        try:
            return int(value)
        except Exception:
            return None

    def _is_total_time_key(self, lk: str) -> bool:
        return ('total' in lk or 'race_time' in lk or 'time_seconds' in lk) and ('time' in lk or 'seconds' in lk)

    def _is_avg_lap_key(self, lk: str) -> bool:
        return ('average' in lk or 'avg' in lk) and 'lap' in lk

    def _is_best_lap_key(self, lk: str) -> bool:
        return ('best' in lk or 'fastest' in lk) and 'lap' in lk

    def _is_laps_key(self, lk: str) -> bool:
        return lk in ('laps', 'laps_completed', 'lap_count', 'completed_laps', 'num_laps')

    def _extract_known_time_fields(self, res_obj) -> tuple:
        avg = self._safe_float(self._extract_result_field(res_obj, 'average_lap_time', None))
        best = self._safe_float(self._extract_result_field(res_obj, 'best_lap_time', None))
        laps_val = self._safe_int(self._extract_result_field(res_obj, 'laps_completed', None))
        return avg, best, laps_val

    def _estimate_total_from_laps(self, avg: Optional[float], best: Optional[float], laps_val: Optional[int]) -> Optional[float]:
        candidate_lap = avg if avg is not None else best
        if candidate_lap is None:
            return None
        if laps_val and laps_val > 0:
            return candidate_lap * float(laps_val)
        return candidate_lap

    def _update_time_components(self, lk: str, v, avg, best, laps_val, total_time) -> tuple:
        if total_time is None and self._is_total_time_key(lk):
            total_time = self._safe_float(v)
            if total_time is not None:
                return avg, best, laps_val, total_time

        if avg is None and self._is_avg_lap_key(lk):
            avg = self._safe_float(v)

        if best is None and self._is_best_lap_key(lk):
            best = self._safe_float(v)

        if laps_val is None and self._is_laps_key(lk):
            laps_val = self._safe_int(v)

        return avg, best, laps_val, total_time

    def _scan_dict_time_components(self, res_obj: dict) -> tuple:
        avg = None
        best = None
        laps_val = None
        total_time = None

        for k, v in res_obj.items():
            lk = str(k).lower()
            avg, best, laps_val, total_time = self._update_time_components(lk, v, avg, best, laps_val, total_time)

        return avg, best, laps_val, total_time

    def _compute_total_time(self, res_obj) -> Optional[float]:
        direct = self._try_direct_total_time(res_obj)
        if direct is not None:
            return direct

        avg, best, laps_val = (None, None, None)

        if isinstance(res_obj, dict):
            avg, best, laps_val, total_time = self._scan_dict_time_components(res_obj)
            if total_time is not None:
                return total_time

        field_avg, field_best, field_laps = self._extract_known_time_fields(res_obj)
        if avg is None:
            avg = field_avg
        if best is None:
            best = field_best
        if laps_val is None:
            laps_val = field_laps

        return self._estimate_total_from_laps(avg, best, laps_val)

    def _get_existing_result_columns(self, cur) -> List[str]:
        cur.execute(self._PRAGMA_RACE_RESULTS_TABLE_INFO)
        return [r[1] for r in cur.fetchall()]

    def _build_result_insert_statement(self, existing_cols: List[str]) -> tuple:
        preferred_cols = [
            'race_id', 'driver_id', 'team_id', 'position', 'fastest_lap', 'points', 'dnf_reason',
            'time_seconds', 'grid_position', 'laps_completed', 'best_lap_time', 'average_lap_time',
            'pitstops', 'tyre_strategy', 'penalties_seconds', 'penalty_reason', 'gap_to_winner_seconds',
            'status', 'recorded_at'
        ]
        insert_cols = [c for c in preferred_cols if c in existing_cols]
        insert_sql = f"INSERT INTO race_results ({', '.join(insert_cols)}) VALUES ({', '.join(['?'] * len(insert_cols))})"
        return insert_cols, insert_sql

    def _fallback_missing_column_value(self, res, col: str):
        if col == 'time_seconds':
            return self._compute_total_time(res)
        if col == 'best_lap_time':
            return self._extract_result_field(res, 'best_lap_time', None)
        if col == 'average_lap_time':
            return self._extract_result_field(res, 'average_lap_time', None)
        if col == 'grid_position':
            return self._extract_result_field(res, 'grid_position', None)
        if col == 'laps_completed':
            return self._extract_result_field(res, 'laps_completed', None)
        return None

    def _build_result_values(self, res, insert_cols: List[str], race_id: int) -> List[Any]:
        vals: List[Any] = []
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

            v = self._extract_result_field(res, col, None)
            if v is None:
                v = self._fallback_missing_column_value(res, col)
            vals.append(v)
        return vals

    def _insert_result_row(self, cur, insert_sql: str, vals: List[Any], race_id: int, res) -> None:
        try:
            cur.execute(insert_sql, tuple(vals))
        except sqlite3.IntegrityError as ie:
            raise ValueError(
                f"IntegrityError inserting race_result: {ie}; params=(race_id={race_id}, values={vals})"
            ) from ie
        except sqlite3.OperationalError as oe:
            try:
                driver_id = self._extract_result_field(res, 'driver_id')
                position = self._extract_result_field(res, 'position')
                time_sec = self._extract_result_field(res, 'time_seconds', 0.0)
                cur.execute(
                    "INSERT INTO race_results (race_id, driver_id, team_id, position, time_seconds) VALUES (?, ?, ?, ?, ?)",
                    (race_id, driver_id, self._parse_team_id(res), position, time_sec),
                )
            except Exception as e:
                raise oe from e

    def save_race_results(self, race_id: int, results: List) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM race_results WHERE race_id = ?", (race_id,))

        existing_cols = self._get_existing_result_columns(cur)
        insert_cols, insert_sql = self._build_result_insert_statement(existing_cols)

        for res in results:
            vals = self._build_result_values(res, insert_cols, race_id)
            self._insert_result_row(cur, insert_sql, vals, race_id, res)

        self.conn.commit()

__all__ = ['PersistenceSQLite']
