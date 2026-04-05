"""
Momentum Motorsport Simulation - Database Manager

Comprehensive database abstraction layer providing CRUD operations, data integrity
enforcement, and query optimization for the Momentum simulation system. Manages
all persistent storage operations for drivers, teams, tracks, championships, and
race results using SQLite as the backend database.

Key Features:
- Automatic schema initialisation and validation
- Transaction management with rollback support
- Optimized queries with proper indexing
- Data integrity through foreign key constraints
- Connection pooling and resource management
- Comprehensive error handling and logging

Database Architecture:
- SQLite file-based storage for portability
- Normalized relational schema
- Performance-optimized with strategic indexes
- Multi-discipline support (Formula, Rally, Endurance, Street)
- Historical data preservation for career tracking

Usage Patterns:
    db = DatabaseManager()
    drivers = db.get_all_drivers()
    team = db.get_team(team_id)
    standings = db.get_championship_standings(championship_id, season)

Compatibility: SQLite 3.7+, Python 3.8+
Authors: Eoin Fitzsimons
"""

import sqlite3
import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
from database.models import Driver, Team, Track, Championship, Race, RaceResult, SCHEMA_SQL
from config import DATABASE_PATH


INTEGER_DEFAULT_NULL = 'INTEGER DEFAULT NULL'


@dataclass
class SimpleTrack:
    name: str
    length_km: float = 3.2
    turns: int = 12
    left_turns: int = 6
    right_turns: int = 6
    elevation_change_m: float = 0.0
    avg_corner_radius_m: float = 40.0
    min_corner_radius_m: float = 20.0
    max_corner_radius_m: float = 80.0
    tightest_corner_radius_m: float = 20.0
    longest_straight_m: float = 700.0
    shortest_straight_m: float = 150.0
    avg_speed_kmh: float = 160.0
    top_speed_kmh: float = 300.0
    surface: str = "asphalt"
    surface_type: str = "asphalt"
    surface_grip: float = 12.0
    surface_abrasiveness: float = 8.0
    climate: str = "temperate"
    drs_zones: int = 1


class DatabaseManager:
    """
    Database Manager - Core Data Access Layer

    Provides comprehensive database management for the Momentum simulation system.
    Handles all CRUD operations, schema management, and data integrity enforcement
    across the complete motorsport simulation data model.

    Architecture:
        - SQLite backend for portability and simplicity
        - Connection pooling for performance
        - Automatic transaction management
        - Schema validation and migration support
        - Comprehensive error handling

    Key Responsibilities:
        - Database schema initialisation and updates
        - CRUD operations for all entity types
        - Complex queries for standings and statistics
        - Data validation and constraint enforcement
        - Connection lifecycle management

    Usage:
        manager = DatabaseManager()  # Uses default database path
        manager = DatabaseManager("/custom/path/db.sqlite")  # Custom path
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Initialise Database Manager

        Sets up the database connection and ensures proper schema initialisation.
        Creates the database file and directory structure if they don't exist.

        Args:
            db_path (str): Path to SQLite database file. Defaults to configured path
                          from config.DATABASE_PATH

        Raises:
            sqlite3.Error: If database initialisation fails
            OSError: If database directory cannot be created
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """
        Initialise Database Schema

        Creates the complete database schema including all tables, indexes,
        constraints, and triggers. Safe to call multiple times - only creates
        objects that don't already exist.

        Schema Components:
            - Core entity tables (drivers, teams, tracks, championships, races)
            - Result tracking tables (race_results)
            - Performance indexes for query optimization
            - Foreign key constraints for data integrity
            - Check constraints for data validation

        Raises:
            sqlite3.Error: If schema creation fails
            OSError: If database directory creation fails
        """
        # Ensure database directory exists (create parent directories as
        # needed)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Execute complete schema creation script
        # Uses transaction to ensure atomicity of schema operations
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign key constraint enforcement
            conn.execute("PRAGMA foreign_keys = ON")

            # Execute the complete schema creation script
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        
        # Apply any schema migrations for existing databases
        self._apply_schema_migrations()
    
    def _apply_schema_migrations(self):
        """
        Apply schema migrations to existing databases
        
        Adds missing columns that may not exist in older databases,
        ensuring backward compatibility with existing data.
        """
        with self.get_connection() as conn:
            self._run_schema_migration_step(
                conn,
                lambda c: self._ensure_table_columns(
                    c,
                    "teams",
                    {
                        'headquarters': "TEXT DEFAULT ''",
                        'biography': "TEXT DEFAULT ''",
                        'version': 'INTEGER NOT NULL DEFAULT 1',
                        'updated_at': 'TEXT DEFAULT CURRENT_TIMESTAMP'
                    },
                ),
            )

            self._run_schema_migration_step(
                conn,
                lambda c: self._ensure_table_columns(
                    c,
                    "drivers",
                    {
                        'contract_start_season': INTEGER_DEFAULT_NULL,
                        'contract_end_season': INTEGER_DEFAULT_NULL,
                        'performance_bonus': 'REAL DEFAULT 0.0'
                    },
                ),
            )

            self._run_schema_migration_step(
                conn,
                lambda c: self._ensure_table_columns(
                    c,
                    "staff_members",
                    {
                        'annual_salary': 'REAL DEFAULT NULL',
                        'contract_length': INTEGER_DEFAULT_NULL,
                        'contract_start_season': INTEGER_DEFAULT_NULL,
                        'contract_end_season': INTEGER_DEFAULT_NULL
                    },
                ),
            )

            self._run_schema_migration_step(conn, self._ensure_team_management_tables)

            self._run_schema_migration_step(
                conn,
                lambda c: self._ensure_table_columns(
                    c,
                    "tracks",
                    {
                        'length_km': 'REAL DEFAULT 3.2',
                        'turns': 'INTEGER DEFAULT 12',
                        'avg_speed_kmh': 'REAL DEFAULT 160.0',
                        'longest_straight_m': 'REAL DEFAULT 700.0',
                        'tightest_corner_radius_m': 'REAL DEFAULT 30.0',
                        'left_turns': 'INTEGER DEFAULT 6',
                        'right_turns': 'INTEGER DEFAULT 6',
                        'drs_zones': 'INTEGER DEFAULT 1',
                        'surface': "TEXT DEFAULT 'asphalt'",
                        'surface_type': "TEXT DEFAULT 'asphalt'",
                        'surface_grip': 'REAL DEFAULT 1.0',
                        'surface_abrasiveness': 'REAL DEFAULT 8.0',
                        'climate': "TEXT DEFAULT 'temperate'"
                    },
                ),
            )

    def _run_schema_migration_step(self, conn: sqlite3.Connection, migration_fn) -> None:
        """Run one migration step and ignore compatibility errors."""
        try:
            migration_fn(conn)
        except Exception:
            pass

    def _ensure_table_columns(self, conn: sqlite3.Connection, table_name: str, required_columns: Dict[str, str]) -> None:
        """Ensure required columns exist on a table."""
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {row[1] for row in cursor.fetchall()}

        for column_name, column_def in required_columns.items():
            if column_name in existing_columns:
                continue
            try:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            except sqlite3.OperationalError:
                pass

        conn.commit()

    def _ensure_team_management_tables(self, conn: sqlite3.Connection) -> None:
        """Ensure supporting team management tables/indexes exist."""
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS team_ownership (
            team_id INTEGER PRIMARY KEY,
            player_id TEXT NOT NULL UNIQUE,
            is_active INTEGER NOT NULL DEFAULT 1,
            acquired_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );

        CREATE TABLE IF NOT EXISTS team_budget_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );

        CREATE TABLE IF NOT EXISTS team_facility_upgrades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            facility_name TEXT NOT NULL,
            level INTEGER NOT NULL DEFAULT 1,
            invested_amount REAL NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team_id, facility_name),
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );

        CREATE TABLE IF NOT EXISTS team_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            actor_id TEXT,
            action TEXT NOT NULL,
            changes_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        );

        CREATE INDEX IF NOT EXISTS idx_team_budget_transactions_team_id ON team_budget_transactions(team_id);
        CREATE INDEX IF NOT EXISTS idx_team_audit_log_team_id ON team_audit_log(team_id);
        """)
        conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """
        Get Database Connection with Configuration

        Creates a new database connection with optimal settings for the simulation
        system including row factory for easier data access and foreign key
        constraint enforcement.

        Returns:
            sqlite3.Connection: Configured database connection with:
                - Row factory for dict-like row access
                - Foreign key constraints enabled
                - Optimal pragma settings

        Usage:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM drivers")
                rows = cursor.fetchall()
        """
        conn = sqlite3.connect(self.db_path)

        # Set row factory for easier data access (allows dict-like access to
        # columns)
        conn.row_factory = sqlite3.Row

        # Enable foreign key constraint enforcement
        conn.execute("PRAGMA foreign_keys = ON")

        return conn

    def _hydrate_driver(self, row: sqlite3.Row) -> Optional[Driver]:
        """Internal: convert a DB row into a `Driver` instance and attach
        legacy attributes from `attributes_extra` (JSON) and sensible defaults.

        This keeps the DB schema slim while providing backward compatibility
        to code that expects legacy attributes like `raw_speed`,
        `cornering_skill`, etc. No schema changes are made.
        """
        if not row:
            return None
        row_dict = dict(row)
        # Remove DB-only columns
        row_dict.pop('created_at', None)
        row_dict.pop('updated_at', None)

        # Build kwargs only for fields present in the compact Driver dataclass
        driver_fields = dict.fromkeys(Driver.__dataclass_fields__.keys(), None)
        driver_kwargs = {k: v for k, v in row_dict.items() if k in driver_fields}

        try:
            driver = Driver(**driver_kwargs)
        except TypeError:
            return None

        # NOTE: legacy alias/fallback attributes (e.g. `raw_speed`,
        # `vehicle_control`, `cornering_skill`, `defensive_driving`,
        # `professionalism`) were previously synthesized here for
        # backwards-compatibility. The project now favors the canonical
        # persisted attributes (e.g. `speed`, `racecraft`, `consistency`,
        # `setup_knowledge`, `tyre_management`, `feedback`, `adaptability`).
        # Engines and services should compute any derived signals from these
        # official attributes. Avoid creating legacy aliases here to prevent
        # accidental reliance on synthesized values.

        # Ensure driver.name is usable in the UI (strip whitespace and provide
        # a fallback if name is empty). This is a UI hygiene step only.
        try:
            nm = getattr(driver, 'name', '') or ''
            nm = str(nm).strip()
            if not nm:
                nat = getattr(driver, 'nationality', None)
                if nat:
                    nm = f"{nat} #{getattr(driver, 'id', '')}"
                else:
                    nm = f"Driver #{getattr(driver, 'id', '')}"
            setattr(driver, 'name', nm)
        except Exception:
            setattr(driver, 'name', f"Driver #{getattr(driver, 'id', '')}")

        # Backward-compatible aliases used by older tests and services.
        def _safe_float(value: Any, default: float) -> float:
            try:
                return float(value)
            except Exception:
                return float(default)

        setattr(driver, 'raw_speed', _safe_float(getattr(driver, 'speed', 50.0), 50.0))
        setattr(driver, 'cornering_skill', _safe_float(getattr(driver, 'racecraft', 50.0), 50.0))
        setattr(driver, 'qualifying_pace', _safe_float(getattr(driver, 'speed', 50.0), 50.0))
        setattr(driver, 'reaction_time', _safe_float(getattr(driver, 'reactions', 50.0), 50.0))
        setattr(driver, 'mental_fortitude', _safe_float(getattr(driver, 'pressure', 50.0), 50.0))
        setattr(driver, 'wet_weather_skill', _safe_float(getattr(driver, 'adaptability', 50.0), 50.0))
        setattr(driver, 'tire_management', _safe_float(getattr(driver, 'tyre_management', 50.0), 50.0))
        setattr(driver, 'age', int(getattr(driver, 'computed_age', 0) or 0))
        setattr(driver, 'decision_making', _safe_float(getattr(driver, 'racecraft', 50.0), 50.0))
        setattr(driver, 'physical_fitness', _safe_float(getattr(driver, 'fitness', 50.0), 50.0))
        setattr(driver, 'discipline', str(getattr(driver, 'preferred_discipline', 'SINGLE_SEATER')))

        return driver

    def _hydrate_team(self, row_dict: Dict[str, Any]) -> Team:
        """Internal: convert a DB row dict into a Team with legacy aliases."""
        team_fields = set(Team.__dataclass_fields__.keys())
        team_kwargs = {k: v for k, v in row_dict.items() if k in team_fields}
        team = Team(**team_kwargs)
        try:
            setattr(team, 'budget_eur', float(getattr(team, 'budget', 0.0)))
        except Exception:
            pass
        try:
            setattr(team, 'version', int(row_dict.get('version', 1) or 1))
            setattr(team, 'updated_at', str(row_dict.get('updated_at') or ''))
        except Exception:
            pass
        return team

    # Driver operations
    def create_driver(self, driver: Driver) -> Optional[int]:
        """Create a new driver with all 50+ attributes and return ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                INSERT INTO drivers (
                    name, nationality, birth_date, age,
                    -- Core Driving Skills
                    raw_speed, consistency, racecraft, overtaking, defensive_driving,
                    cornering_skill, braking_technique, acceleration_control, spatial_awareness, vehicle_control,
                    -- Physical & Mental Traits
                    physical_fitness, reaction_time, concentration, pressure_handling, pain_tolerance,
                    g_force_tolerance, coordination, multitasking, mental_resilience, adrenaline_management,
                    -- Technical Knowledge
                    setup_knowledge, mechanical_sympathy, tire_management, fuel_management,
                    aerodynamics_understanding, suspension_feel, engine_management, data_analysis,
                    -- Discipline Specializations
                    single_seater_aptitude, touring_car_aptitude, rally_aptitude, street_racing_aptitude,
                    drag_racing_aptitude, rallycross_aptitude, endurance_aptitude,
                    -- Race Craft & Strategy
                    race_strategy, pit_entry_exit, traffic_management, qualifying_pace, race_pace,
                    starting_skill, tyre_warming, energy_management,
                    -- Environmental Adaptation
                    wet_weather_skill, night_driving, heat_tolerance, cold_tolerance,
                    altitude_adaptation, visibility_adaptation, surface_adaptation,
                    -- Personal & Social Traits
                    media_handling, sponsorship_appeal, fan_engagement, team_player, leadership, professionalism,
                    -- Career Stats
                    career_wins, career_podiums, career_points, biography, current_team_id
                )
                VALUES (?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?)
                """, (
                driver.name, driver.nationality, driver.birth_date, driver.age,
                # Core Driving Skills
                driver.raw_speed, driver.consistency, driver.racecraft, driver.overtaking, driver.defensive_driving,
                driver.cornering_skill, driver.braking_technique, driver.acceleration_control, driver.spatial_awareness, driver.vehicle_control,
                # Physical & Mental Traits
                driver.physical_fitness, driver.reaction_time, driver.concentration, driver.pressure_handling, driver.pain_tolerance,
                driver.g_force_tolerance, driver.coordination, driver.multitasking, driver.mental_resilience, driver.adrenaline_management,
                # Technical Knowledge
                driver.setup_knowledge, driver.mechanical_sympathy, driver.tire_management, driver.fuel_management,
                driver.aerodynamics_understanding, driver.suspension_feel, driver.engine_management, driver.data_analysis,
                # Discipline Specializations
                driver.single_seater_aptitude, driver.touring_car_aptitude, driver.rally_aptitude, driver.street_racing_aptitude,
                driver.drag_racing_aptitude, driver.rallycross_aptitude, driver.endurance_aptitude,
                # Race Craft & Strategy
                driver.race_strategy, driver.pit_entry_exit, driver.traffic_management, driver.qualifying_pace, driver.race_pace,
                driver.starting_skill, driver.tyre_warming, driver.energy_management,
                # Environmental Adaptation
                driver.wet_weather_skill, driver.night_driving, driver.heat_tolerance, driver.cold_tolerance,
                driver.altitude_adaptation, driver.visibility_adaptation, driver.surface_adaptation,
                # Personal & Social Traits
                driver.media_handling, driver.sponsorship_appeal, driver.fan_engagement, driver.team_player, driver.leadership, driver.professionalism,
                # Career Stats
                driver.career_wins, driver.career_podiums, driver.career_points, driver.biography, driver.current_team_id
                ))
                return cursor.lastrowid
        except Exception:
            # Fallback path for compact Driver objects used in newer code/tests.
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO drivers (name, nationality, birth_date, speed, racecraft, consistency, preferred_discipline)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        getattr(driver, 'name', 'Unknown Driver'),
                        getattr(driver, 'nationality', 'Unknown'),
                        getattr(driver, 'birth_date', '1995-01-01'),
                        float(getattr(driver, 'speed', getattr(driver, 'raw_speed', 50.0))),
                        float(getattr(driver, 'racecraft', 50.0)),
                        float(getattr(driver, 'consistency', 50.0)),
                        str(getattr(driver, 'preferred_discipline', getattr(driver, 'discipline', 'SINGLE_SEATER'))),
                    ),
                )
                return cursor.lastrowid

    def update_driver(self, driver: Driver) -> bool:
        """Update core driver fields used by tests and API flows."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE drivers
                SET name = ?, nationality = ?, birth_date = ?, speed = ?, racecraft = ?, consistency = ?, preferred_discipline = ?
                WHERE id = ?
                """,
                (
                    getattr(driver, 'name', 'Unknown Driver'),
                    getattr(driver, 'nationality', 'Unknown'),
                    getattr(driver, 'birth_date', '1995-01-01'),
                    float(getattr(driver, 'speed', getattr(driver, 'raw_speed', 50.0))),
                    float(getattr(driver, 'racecraft', 50.0)),
                    float(getattr(driver, 'consistency', 50.0)),
                    str(getattr(driver, 'preferred_discipline', getattr(driver, 'discipline', 'SINGLE_SEATER'))),
                    int(getattr(driver, 'id', 0)),
                ),
            )
            return cursor.rowcount > 0

    def get_driver(self, driver_id: int) -> Optional[Driver]:
        """Get driver by ID (returns compact Driver with legacy attrs attached)."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,)).fetchone()
            return self._hydrate_driver(row)

    def get_all_drivers(self, order_by: str = 'id') -> List[Driver]:
        """Get all drivers and hydrate them for compatibility.

        Args:
            order_by: Column name to order results by. For safety this value is
                validated against the `Driver` dataclass fields and a small
                trusted set (e.g. 'id', 'name'). If an unknown column is
                provided the method falls back to ordering by 'id'.
        """
        # Build a small whitelist of allowed ordering columns to avoid SQL
        # injection via the `order_by` parameter. Prefer fields defined on
        # the compact `Driver` dataclass plus a couple of well-known DB
        # columns.
        allowed = set(Driver.__dataclass_fields__.keys()) if hasattr(Driver, '__dataclass_fields__') else set()
        allowed.update({'id', 'name'})
        if not isinstance(order_by, str) or order_by not in allowed:
            order_by = 'id'

        with self.get_connection() as conn:
            sql = f"SELECT * FROM drivers ORDER BY {order_by}"
            rows = conn.execute(sql).fetchall()
            drivers = []
            for row in rows:
                d = self._hydrate_driver(row)
                if d:
                    drivers.append(d)
            return drivers

    def get_drivers_by_team(self, team_id: int) -> List[Driver]:
        """Get all drivers for a specific team"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM drivers WHERE current_team_id = ? ORDER BY speed DESC",
                (team_id,)
            ).fetchall()
            drivers = []
            for row in rows:
                d = self._hydrate_driver(row)
                if d:
                    drivers.append(d)
            return drivers

    def update_driver_stats(self, driver_id: int,
                            wins: int = 0, podiums: int = 0, points: int = 0):
        """Update driver career statistics"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE drivers
                SET career_wins = career_wins + ?,
                    career_podiums = career_podiums + ?,
                    career_points = career_points + ?
                WHERE id = ?
            """, (wins, podiums, points, driver_id))

    # Staff operations - NOT NEEDED FOR MVP - COMMENTED OUT
    # All staff-related methods removed for MVP focus

    # Team operations
    def create_team(self, team: Team) -> Optional[int]:
        """Create a new team and return ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO teams (name, nationality, founded_year, discipline, tier,
                                 budget, headquarters, team_principal, biography, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (team.name, team.nationality, team.founded_year, team.discipline,
                  team.tier, team.budget, team.headquarters, team.team_principal, team.biography))
            return cursor.lastrowid

    def get_staff_by_team(self, team_id: int):
        """Get all staff members for a specific team."""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM staff_members WHERE current_team_id = ? ORDER BY rating DESC, name ASC",
                (team_id,)
            ).fetchall()
            from database.models import StaffMember
            return [StaffMember(**dict(row)) for row in rows]

    def get_team(self, team_id: int) -> Optional[Team]:
        """Get team by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
            if row:
                return self._hydrate_team(dict(row))
            return None

    def get_teams_by_discipline(self, discipline: str) -> List[Team]:
        """Get all teams in a specific discipline"""
        with self.get_connection() as conn:
            # Accept flexible discipline identifiers: case-insensitive, spaces vs underscores
            # Normalize input to lowercase with underscores and compare against a normalized
            # discipline column (replace spaces with underscores and lower-case
            # it).
            norm = discipline.lower().replace(' ', '_')
            rows = conn.execute(
                "SELECT * FROM teams WHERE LOWER(REPLACE(discipline, ' ', '_')) = ? ORDER BY tier, name",
                (norm,)
            ).fetchall()
            return [self._hydrate_team(dict(row)) for row in rows]

    def get_teams_by_discipline_and_tier(
            self, discipline: str, tier: str) -> List[Team]:
        """Get all teams in a specific discipline and tier (for championship-specific races)"""
        with self.get_connection() as conn:
            # Normalize discipline input (case-insensitive, spaces vs
            # underscores)
            norm_discipline = discipline.lower().replace(' ', '_')
            rows = conn.execute(
                """SELECT * FROM teams
                   WHERE LOWER(REPLACE(discipline, ' ', '_')) = ?
                   AND tier = ?
                   ORDER BY name""",
                (norm_discipline, tier)
            ).fetchall()
            return [self._hydrate_team(dict(row)) for row in rows]

    def get_all_teams(self) -> List[Team]:
        """Get all teams."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()
            return [self._hydrate_team(dict(row)) for row in rows]

    def update_team(self, team_id: int, team: Team, expected_version: Optional[int] = None) -> bool:
        """Update an existing team's attributes with optional optimistic locking."""
        with self.get_connection() as conn:
            if expected_version is None:
                cursor = conn.execute("""
                    UPDATE teams
                    SET name = ?, nationality = ?, discipline = ?, tier = ?,
                        budget = ?, headquarters = ?, team_principal = ?, biography = ?,
                        strategy_profile = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (team.name, team.nationality, team.discipline, team.tier,
                      team.budget, team.headquarters, team.team_principal, team.biography,
                      team.strategy_profile, team_id))
            else:
                cursor = conn.execute("""
                    UPDATE teams
                    SET name = ?, nationality = ?, discipline = ?, tier = ?,
                        budget = ?, headquarters = ?, team_principal = ?, biography = ?,
                        strategy_profile = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND version = ?
                """, (team.name, team.nationality, team.discipline, team.tier,
                      team.budget, team.headquarters, team.team_principal, team.biography,
                      team.strategy_profile, team_id, expected_version))
            return cursor.rowcount > 0

    def assign_team_owner(self, team_id: int, player_id: str) -> bool:
        """Assign or replace the owner of a team."""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE team_ownership SET is_active = 0 WHERE team_id = ?",
                (team_id,)
            )
            conn.execute(
                """
                INSERT INTO team_ownership (team_id, player_id, is_active)
                VALUES (?, ?, 1)
                ON CONFLICT(player_id) DO UPDATE SET
                    team_id = excluded.team_id,
                    is_active = 1,
                    acquired_at = CURRENT_TIMESTAMP
                """,
                (team_id, player_id)
            )
            return True

    def get_player_team_id(self, player_id: str) -> Optional[int]:
        """Return active owned team id for a player, if any."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT team_id FROM team_ownership WHERE player_id = ? AND is_active = 1",
                (player_id,)
            ).fetchone()
            return int(row[0]) if row else None

    def get_team_owner(self, team_id: int) -> Optional[str]:
        """Return active owner player id for team, if assigned."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT player_id FROM team_ownership WHERE team_id = ? AND is_active = 1",
                (team_id,)
            ).fetchone()
            return str(row[0]) if row else None

    def add_budget_transaction(self, team_id: int, category: str, amount: float, description: str = "") -> int:
        """Persist a budget transaction entry and return transaction id."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO team_budget_transactions (team_id, category, amount, description)
                VALUES (?, ?, ?, ?)
                """,
                (team_id, category, amount, description)
            )
            return int(cursor.lastrowid or 0)

    def get_budget_transactions(self, team_id: int) -> List[Dict[str, Any]]:
        """Get all persisted budget transactions for a team."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, team_id, category, amount, description, created_at
                FROM team_budget_transactions
                WHERE team_id = ?
                ORDER BY id DESC
                """,
                (team_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    def upsert_facility_upgrade(self, team_id: int, facility_name: str, invested_amount: float) -> bool:
        """Track facility upgrades and accumulated investment for the team."""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO team_facility_upgrades (team_id, facility_name, level, invested_amount, updated_at)
                VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(team_id, facility_name)
                DO UPDATE SET
                    invested_amount = team_facility_upgrades.invested_amount + excluded.invested_amount,
                    level = team_facility_upgrades.level + 1,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (team_id, facility_name, invested_amount)
            )
            return True

    def get_facility_upgrades(self, team_id: int) -> List[Dict[str, Any]]:
        """Get facility upgrade records for the team."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT facility_name, level, invested_amount, updated_at
                FROM team_facility_upgrades
                WHERE team_id = ?
                ORDER BY facility_name
                """,
                (team_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    def add_team_audit_log(self, team_id: int, action: str, changes: Dict[str, Any], actor_id: Optional[str] = None) -> int:
        """Persist an audit log entry for team changes."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO team_audit_log (team_id, actor_id, action, changes_json)
                VALUES (?, ?, ?, ?)
                """,
                (team_id, actor_id, action, json.dumps(changes, ensure_ascii=True))
            )
            return int(cursor.lastrowid or 0)

    def get_team_audit_logs(self, team_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent team audit logs."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, team_id, actor_id, action, changes_json, created_at
                FROM team_audit_log
                WHERE team_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (team_id, max(1, int(limit)))
            ).fetchall()
            parsed = []
            for row in rows:
                item = dict(row)
                try:
                    item["changes"] = json.loads(item.get("changes_json") or "{}")
                except Exception:
                    item["changes"] = {}
                parsed.append(item)
            return parsed

    # Track operations
    def create_track(self, track: Track) -> Optional[int]:
        """Create a new track and return ID"""
        with self.get_connection() as conn:
            table_info = conn.execute("PRAGMA table_info(tracks)").fetchall()
            existing_cols = {row[1] for row in table_info}

            # Build a safe geometry payload for schemas that lack physical columns
            geometry_payload = getattr(track, "geometry_json", None)
            if geometry_payload is None:
                phys_fields = [
                    "length_km", "turns", "avg_speed_kmh", "top_speed_kmh",
                    "longest_straight_m", "shortest_straight_m", "tightest_corner_radius_m",
                    "left_turns", "right_turns", "drs_zones", "surface", "surface_type",
                    "surface_grip", "surface_abrasiveness", "climate"
                ]
                payload = {k: getattr(track, k) for k in phys_fields if getattr(track, k, None) is not None}
                geometry_payload = json.dumps(payload) if payload else None

            preferred = {
                "name": track.name,
                "country": track.country,
                "primary_discipline": getattr(track, "primary_discipline", None),
                "is_point_to_point": int(getattr(track, "is_point_to_point", False)),
                "joker_enabled": int(getattr(track, "joker_enabled", False)),
                "instructions_json": getattr(track, "instructions_json", None),
                "geometry_json": geometry_payload,
                "pit_entry_index": getattr(track, "pit_entry_index", None),
                "pit_exit_index": getattr(track, "pit_exit_index", None),
            }

            columns = [c for c in preferred.keys() if c in existing_cols]
            if not columns:
                return None

            values = [preferred[c] for c in columns]
            placeholders = ", ".join(["?" for _ in columns])
            col_clause = ", ".join(columns)

            cursor = conn.execute(
                f"INSERT INTO tracks ({col_clause}) VALUES ({placeholders})",
                values,
            )
            return cursor.lastrowid

    def _track_from_row(self, row_dict: dict) -> Track:
        """Convert database row to Track object with proper defaults"""
        from services.track_surface_service import TrackSurfaceService
        from dataclasses import fields
        
        row_dict.pop('created_at', None)
        
        # Only keep fields that exist in Track model
        track_field_names = {f.name for f in fields(Track)}
        row_dict = {k: v for k, v in row_dict.items() if k in track_field_names}
        
        # Set defaults for missing physical attributes that are used in race logic
        physical_attrs = {
            'length_km': 3.2,
            'turns': 12,
            'avg_speed_kmh': 160.0,
            'longest_straight_m': 700.0,
            'tightest_corner_radius_m': 30.0,
            'left_turns': 6,
            'right_turns': 6,
            'drs_zones': 1,
            'surface': 'asphalt'  # Default to asphalt
        }
        # Only set defaults for missing fields
        for attr, default_val in physical_attrs.items():
            if attr not in row_dict:
                row_dict[attr] = default_val
        
        # Calculate grip level from surface if not provided
        surface = row_dict.get('surface', 'asphalt')
        if 'surface_grip' not in row_dict or row_dict['surface_grip'] is None:
            row_dict['surface_grip'] = TrackSurfaceService.get_grip_level(surface)
        
        track = Track(**row_dict)
        # Backward-compatible aliases for legacy tests.
        try:
            setattr(track, 'discipline', getattr(track, 'primary_discipline', 'SINGLE_SEATER'))
            setattr(track, 'top_speed_kmh', max(float(getattr(track, 'avg_speed_kmh', 160.0)) * 1.6, 250.0))
            setattr(track, 'elevation_change_m', 0.0)
        except Exception:
            pass
        return track

    def get_tracks_by_discipline(self, discipline: str) -> List[Track]:
        """Get all tracks for a specific discipline"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tracks WHERE primary_discipline = ? ORDER BY name",
                (discipline,)
            ).fetchall()
            return [self._track_from_row(dict(row)) for row in rows]


    def get_track_instructions(self, track_id: int) -> Optional[Dict]:
        """Return parsed instructions JSON for a track, or None."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT instructions_json, geometry_json, is_point_to_point, joker_enabled FROM tracks WHERE id = ?",
                               (track_id,)).fetchone()
            if not row:
                return None
            rowd = dict(row)
            instr = rowd.get('instructions_json')
            geom = rowd.get('geometry_json')
            is_ptp = bool(rowd.get('is_point_to_point'))
            joker = bool(rowd.get('joker_enabled'))
            parsed = None
            if instr:
                try:
                    parsed = json.loads(instr)
                except Exception:
                    parsed = None
            return {
                'instructions': parsed,
                'geometry_json': geom,
                'is_point_to_point': is_ptp,
                'joker_enabled': joker
            }

    def save_track_geometry(self, track_id: int, geometry_json: str):
        """Persist generated geometry JSON for a track (cache)."""
        with self.get_connection() as conn:
            conn.execute("UPDATE tracks SET geometry_json = ? WHERE id = ?", (geometry_json, track_id))

    def save_track_instructions(self, track_id: int, instructions_json: str):
        """Persist canonical instructions JSON for a track."""
        with self.get_connection() as conn:
            conn.execute("UPDATE tracks SET instructions_json = ? WHERE id = ?", (instructions_json, track_id))

    def get_simple_track(self, track_id: Optional[int] = None) -> "SimpleTrack":
        """Return a simple track object suitable for the GUI and simulation.

        If `track_id` is provided the specific track is returned. If no tracks
        exist in the database a default "Test Circuit" will be created with the
        same hard-coded values previously used by the GUI so behaviour is
        identical.
        """
        with self.get_connection() as conn:
            row = self._fetch_simple_track_row(conn, track_id)
            rowd = dict(row)
            geom = self._parse_track_geometry(rowd.get('geometry_json'))
            attrs = self._build_simple_track_attrs(rowd, geom)
            return SimpleTrack(**attrs)

    def _default_track_geometry_attrs(self) -> Dict[str, Any]:
        """Default geometry payload used for seeded fallback test track."""
        return {
            "length_km": 4.5,
            "turns": 12,
            "left_turns": 6,
            "right_turns": 6,
            "elevation_change_m": 15.0,
            "avg_corner_radius_m": 40.0,
            "min_corner_radius_m": 20.0,
            "max_corner_radius_m": 80.0,
            "tightest_corner_radius_m": 20.0,
            "longest_straight_m": 800.0,
            "shortest_straight_m": 150.0,
            "avg_speed_kmh": 180.0,
            "top_speed_kmh": 280.0,
            "surface": "asphalt",
            "surface_type": "asphalt",
            "surface_grip": 12.0,
            "surface_abrasiveness": 8.0,
            "climate": "temperate",
            "drs_zones": 2,
        }

    def _fetch_simple_track_row(self, conn: sqlite3.Connection, track_id: Optional[int]):
        """Fetch requested track row, seeding a fallback track when needed."""
        if track_id is not None:
            row = conn.execute(
                "SELECT id, name, country, primary_discipline, geometry_json FROM tracks WHERE id = ?",
                (track_id,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id, name, country, primary_discipline, geometry_json FROM tracks ORDER BY id LIMIT 1"
            ).fetchone()

        if row:
            return row

        default_attrs = self._default_track_geometry_attrs()
        cursor = conn.execute(
            "INSERT INTO tracks (name, country, primary_discipline, geometry_json) VALUES (?, ?, ?, ?)",
            ("Test Circuit", "Nowhere", "SINGLE_SEATER", json.dumps(default_attrs)),
        )
        new_id = cursor.lastrowid
        return conn.execute(
            "SELECT id, name, country, primary_discipline, geometry_json FROM tracks WHERE id = ?",
            (new_id,),
        ).fetchone()

    def _parse_track_geometry(self, raw_geom: Any) -> Optional[Dict[str, Any]]:
        """Parse geometry payload and return dict data when valid."""
        try:
            if not raw_geom:
                return None
            if isinstance(raw_geom, str):
                parsed = json.loads(raw_geom)
            elif isinstance(raw_geom, dict):
                parsed = raw_geom
            else:
                return None
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    def _pick_float(self, geom: Optional[Dict[str, Any]], key: str, fallback: Any) -> float:
        """Read float from geometry with fallback."""
        if geom:
            val = geom.get(key)
            if val is not None:
                return float(val)
        return float(fallback)

    def _pick_int(self, geom: Optional[Dict[str, Any]], key: str, fallback: Any) -> int:
        """Read int from geometry with fallback."""
        if geom:
            val = geom.get(key)
            if val is not None:
                return int(val)
        return int(fallback)

    def _pick_str(self, geom: Optional[Dict[str, Any]], key: str, fallback: Any) -> str:
        """Read string from geometry with fallback."""
        if geom and geom.get(key):
            return str(geom.get(key))
        return str(fallback)

    def _build_simple_track_attrs(self, rowd: Dict[str, Any], geom: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build `SimpleTrack` init attrs from DB row and optional geometry payload."""
        return {
            'name': rowd.get('name') or 'Unnamed Circuit',
            'length_km': self._pick_float(geom, 'length_km', rowd.get('length_km') or 3.2),
            'turns': self._pick_int(geom, 'turns', rowd.get('turns') or 12),
            'left_turns': self._pick_int(geom, 'left_turns', rowd.get('left_turns') or 6),
            'right_turns': self._pick_int(geom, 'right_turns', rowd.get('right_turns') or 6),
            'elevation_change_m': self._pick_float(geom, 'elevation_change_m', 0.0),
            'avg_corner_radius_m': self._pick_float(geom, 'avg_corner_radius_m', 40.0),
            'min_corner_radius_m': self._pick_float(geom, 'min_corner_radius_m', 20.0),
            'max_corner_radius_m': self._pick_float(geom, 'max_corner_radius_m', 80.0),
            'tightest_corner_radius_m': self._pick_float(geom, 'tightest_corner_radius_m', 20.0),
            'longest_straight_m': self._pick_float(geom, 'longest_straight_m', 800.0),
            'shortest_straight_m': self._pick_float(geom, 'shortest_straight_m', 150.0),
            'avg_speed_kmh': self._pick_float(geom, 'avg_speed_kmh', 180.0),
            'top_speed_kmh': self._pick_float(geom, 'top_speed_kmh', 280.0),
            'surface': self._pick_str(geom, 'surface', rowd.get('surface') or 'asphalt'),
            'surface_type': self._pick_str(geom, 'surface_type', rowd.get('surface_type') or 'asphalt'),
            'surface_grip': self._pick_float(geom, 'surface_grip', 12.0),
            'surface_abrasiveness': self._pick_float(geom, 'surface_abrasiveness', 8.0),
            'climate': self._pick_str(geom, 'climate', 'temperate'),
            'drs_zones': self._pick_int(geom, 'drs_zones', 1),
        }

    def synthesize_instructions_from_fields(self, track: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a simple instruction list from compact track fields as fallback.

        Produces a reasonable mix of straights and corners based on `length_km` and `turns`.
        This is approximate and intended as a fallback when `instructions_json` is absent.
        """
        length_m = int(float(track.get('length_km', 3.0)) * 1000)
        turns = int(track.get('turns', max(3, length_m // 800)))
        straight_len = max(50, length_m // (turns + 1))
        instr = []
        for i in range(turns):
            instr.append({'type': 'S', 'length_m': straight_len})
            # alternate left/right corners with moderate radius and angle
            angle = 40 if i % 2 == 0 else -45
            instr.append({'type': 'C', 'radius_m': 80, 'angle_deg': angle})
        # final straight to complete distance
        remainder = length_m - straight_len * turns
        if remainder > 0:
            instr.append({'type': 'S', 'length_m': remainder})
        return instr

    def get_track(self, track_id: int) -> Optional[Track]:
        """Get track by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tracks WHERE id = ?", (track_id,)).fetchone()
            if row:
                return self._track_from_row(dict(row))
            return None
    
    def update_track_surface(self, track_id: int, surface: str) -> bool:
        """
        Update track surface type
        
        Args:
            track_id: Track ID to update
            surface: Surface type (asphalt, concrete, gravel, mixed, dirt, grassy)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE tracks SET surface = ?, surface_type = ? WHERE id = ?",
                    (surface, surface, track_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            # Error updating surface, but continue gracefully
            return False
    
    # Alias for consistency
    def get_track_by_id(self, track_id: int) -> Optional[Track]:
        """Get track by ID (alias for get_track)"""
        return self.get_track(track_id)

    # Championship operations
    def create_championship(self, championship: Championship) -> Optional[int]:
        """Create a new championship and return ID"""
        with self.get_connection() as conn:
            # Align insert columns with whatever exists in the current schema to
            # avoid failures on older databases without newer fields.
            table_info = conn.execute("PRAGMA table_info(championships)").fetchall()
            existing_cols = {row[1] for row in table_info}

            preferred_columns = [
                ("name", championship.name),
                ("discipline", championship.discipline),
                ("tier", championship.tier),
                ("season_length", championship.season_length),
                ("points_system", championship.points_system),
                ("current_season", championship.current_season),
                ("founded_year", championship.founded_year),
                ("description", championship.description),
                ("archived", getattr(championship, "archived", False)),
            ]

            columns, values = zip(*[(col, val) for col, val in preferred_columns if col in existing_cols])
            placeholders = ", ".join(["?" for _ in columns])
            col_clause = ", ".join(columns)

            cursor = conn.execute(
                f"INSERT INTO championships ({col_clause}) VALUES ({placeholders})",
                values,
            )
            return cursor.lastrowid

    def get_championship(self, championship_id: int) -> Optional[Championship]:
        """Get championship by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM championships WHERE id = ?",
                (championship_id,
                 )).fetchone()
            if row:
                # Filter out created_at field which isn't in the Championship
                # model
                return Championship(
                    **{k: v for k, v in dict(row).items() if k != 'created_at'})
            return None

    def delete_championship(self, championship_id: int) -> bool:
        """Delete a championship and all race/result rows under it."""
        with self.get_connection() as conn:
            race_rows = conn.execute(
                "SELECT id FROM races WHERE championship_id = ?",
                (championship_id,),
            ).fetchall()
            race_ids = [int(row[0]) for row in race_rows]

            for race_id in race_ids:
                conn.execute(
                    "DELETE FROM race_results WHERE race_id = ?",
                    (race_id,),
                )

            conn.execute(
                "DELETE FROM races WHERE championship_id = ?",
                (championship_id,),
            )

            cursor = conn.execute(
                "DELETE FROM championships WHERE id = ?",
                (championship_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    # Race operations
    def create_race(self, race: Race) -> Optional[int]:
        """Create a new race and return ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO races (championship_id, track_id, season, round_number,
                                     race_date, weather_conditions, race_duration_minutes, laps, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (race.championship_id, race.track_id, race.season, race.round_number,
                      race.race_date, race.weather_conditions, race.race_duration_minutes, race.laps, race.status))
                return cursor.lastrowid
        except Exception as e:
            # Fallback for databases without race_duration_minutes column
            if "race_duration_minutes" in str(e):
                with self.get_connection() as conn:
                    cursor = conn.execute("""
                        INSERT INTO races (championship_id, track_id, season, round_number,
                                         race_date, weather_conditions, laps, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (race.championship_id, race.track_id, race.season, race.round_number,
                          race.race_date, race.weather_conditions, race.laps, race.status))
                    return cursor.lastrowid
            raise

    def get_race_results(self, race_id: int) -> List[RaceResult]:
        """Get all results for a specific race"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM race_results
                WHERE race_id = ?
                ORDER BY position
            """, (race_id,)).fetchall()
            # Filter out created_at field which isn't in the RaceResult model
            return [RaceResult(
                **{k: v for k, v in dict(row).items() if k != 'created_at'}) for row in rows]

    def get_race(self, race_id: int) -> Optional[Race]:
        """Get race by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM races WHERE id = ?", (race_id,)).fetchone()
            if row:
                row_dict = {k: v for k, v in dict(row).items() if k != 'created_at'}
                # Provide default for race_duration_minutes if missing
                if 'race_duration_minutes' not in row_dict:
                    row_dict['race_duration_minutes'] = 90
                return Race(**row_dict)
            return None

    def update_race_status(self, race_id: int, status: str):
        """Update race status"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE races SET status = ? WHERE id = ?",
                (status, race_id)
            )

    def save_race_result(self, result: RaceResult) -> Optional[int]:
        """Save race result and return ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO race_results
                (race_id, driver_id, team_id, position, points, fastest_lap, dnf_reason, grid_position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (result.race_id, result.driver_id, result.team_id, result.position,
                  result.points, result.fastest_lap, result.dnf_reason, result.grid_position))
            return cursor.lastrowid

    # Alias for consistency with game loop
    def create_race_result(self, result: RaceResult) -> Optional[int]:
        """Create race result (alias for save_race_result)"""
        return self.save_race_result(result)

    def get_all_championships(self) -> List[Championship]:
        """Get all championships"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM championships ORDER BY name").fetchall()
            # Filter out created_at field which isn't in the Championship model
            return [Championship(
                **{k: v for k, v in dict(row).items() if k != 'created_at'}) for row in rows]

    # Statistics and queries
    def get_championship_standings(
            self, championship_id: int, season: int) -> List[Dict[str, Any]]:
        """Get current championship standings for a season"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT d.name as driver_name, t.name as team_name,
                       SUM(rr.points) as total_points,
                       COUNT(CASE WHEN rr.position = 1 THEN 1 END) as wins,
                       COUNT(CASE WHEN rr.position <= 3 THEN 1 END) as podiums
                FROM race_results rr
                JOIN races r ON rr.race_id = r.id
                JOIN drivers d ON rr.driver_id = d.id
                JOIN teams t ON rr.team_id = t.id
                WHERE r.championship_id = ? AND r.season = ?
                GROUP BY rr.driver_id, rr.team_id
                ORDER BY total_points DESC, wins DESC
            """, (championship_id, season)).fetchall()

            return [dict(row) for row in rows]

    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        with self.get_connection() as conn:
            stats = {}
            for table in ['drivers', 'teams', 'tracks',
                          'championships', 'races', 'race_results']:
                count = conn.execute(
                    f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                stats[table] = count
            return stats

    # Legacy aliases expected by older test suites.
    def list_drivers(self) -> List[Driver]:
        return self.get_all_drivers()

    def list_teams(self) -> List[Team]:
        return self.get_all_teams()

    def list_tracks(self) -> List[Track]:
        return self.get_all_tracks()

    # Convenience aliases for consistency
    def add_track(self, track: Track) -> Optional[int]:
        """Alias for create_track"""
        return self.create_track(track)

    def get_all_tracks(self) -> List[Track]:
        """Get all tracks in the database"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tracks ORDER BY name").fetchall()
            return [self._track_from_row(dict(row)) for row in rows]

    def get_circuits_by_discipline(self, discipline: str) -> List[Any]:
        """
        Get all circuits for a specific discipline

        Args:
            discipline: Racing discipline (e.g., "SINGLE_SEATER")

        Returns:
            List of Track objects matching the discipline
        """
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tracks
                WHERE primary_discipline = ?
                ORDER BY name
            """, (discipline,)).fetchall()

            return [Track(**dict(row)) for row in rows]

    def get_circuit_by_id(self, circuit_id: int) -> Optional[Any]:
        """
        Get circuit by ID as a full Track object

        Args:
            circuit_id: Circuit database ID

        Returns:
            Track object or None
        """
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tracks WHERE id = ?", (circuit_id,)).fetchone()

            if not row:
                return None

            from database.models import Track
            return Track(**dict(row))

    def get_race_by_id(self, race_id: int) -> Optional[Any]:
        """
        Get race by ID

        For now, returns a simple object with race attributes.
        In future, this would query a races table.

        Args:
            race_id: Race ID

        Returns:
            Race-like object or None
        """
        # For now, we don't have a races table, so create a temporary race-like
        # object using a best available track id from the tracks table.

        championship_id = race_id // 1000
        round_number = race_id % 1000
        circuit_id = None

        with self.get_connection() as conn:
            row = conn.execute("SELECT id FROM tracks ORDER BY id LIMIT 1").fetchone()
            if row is not None:
                circuit_id = int(row[0])

        if circuit_id is None:
            return None

        class TempRace:
            def __init__(self):
                self.id = race_id
                self.championship_id = championship_id
                self.circuit_id = circuit_id
                self.discipline = "SINGLE_SEATER"  # Will be set by caller
                self.round_number = round_number
                self.total_laps = 50

        return TempRace()
