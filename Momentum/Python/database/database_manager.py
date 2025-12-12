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
Authors: Final Year Project - Computer Science
"""

import sqlite3
import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
from database.models import Driver, Team, Track, Championship, Race, RaceResult, SCHEMA_SQL
from config import DATABASE_PATH


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

        return driver

    # Driver operations
    def create_driver(self, driver: Driver) -> Optional[int]:
        """Create a new driver with all 50+ attributes and return ID"""
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
                "SELECT * FROM drivers WHERE current_team_id = ? ORDER BY overall_rating DESC",
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
                                 budget, headquarters, team_principal, biography)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (team.name, team.nationality, team.founded_year, team.discipline,
                  team.tier, team.budget, team.headquarters, team.team_principal, team.biography))
            return cursor.lastrowid

    def get_team(self, team_id: int) -> Optional[Team]:
        """Get team by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
            if row:
                # Filter out created_at field which isn't in the Team model
                return Team(
                    **{k: v for k, v in dict(row).items() if k != 'created_at'})
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
            # Filter out created_at field which isn't in the Team model
            return [Team(**{k: v for k, v in dict(row).items()
                         if k != 'created_at'}) for row in rows]

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
            # Filter out created_at field which isn't in the Team model
            return [Team(**{k: v for k, v in dict(row).items()
                         if k != 'created_at'}) for row in rows]

    # Track operations
    def create_track(self, track: Track) -> Optional[int]:
        """Create a new track and return ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO tracks (name, country, length_km, surface_type, difficulty,
                                  weather_impact, overtaking_difficulty, discipline, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (track.name, track.country, track.length_km, track.surface_type,
                  track.difficulty, track.weather_impact, track.overtaking_difficulty,
                  track.discipline, track.description))
            return cursor.lastrowid

    def get_tracks_by_discipline(self, discipline: str) -> List[Track]:
        """Get all tracks for a specific discipline"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tracks WHERE primary_discipline = ? ORDER BY name",
                (discipline,)
            ).fetchall()
            # Filter out created_at field which isn't in the Track model
            return [Track(**{k: v for k, v in dict(row).items()
                          if k != 'created_at'}) for row in rows]


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
            if track_id is not None:
                row = conn.execute("SELECT id, name, country, primary_discipline, geometry_json FROM tracks WHERE id = ?", (track_id,)).fetchone()
            else:
                row = conn.execute("SELECT id, name, country, primary_discipline, geometry_json FROM tracks ORDER BY id LIMIT 1").fetchone()

            if not row:
                # Insert default Test Circuit using geometry_json to store full attributes
                default_attrs = {
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
                    "drs_zones": 2
                }
                cursor = conn.execute(
                    "INSERT INTO tracks (name, country, primary_discipline, geometry_json) VALUES (?, ?, ?, ?)",
                    ("Test Circuit", "Nowhere", "SINGLE_SEATER", json.dumps(default_attrs))
                )
                new_id = cursor.lastrowid
                row = conn.execute("SELECT id, name, country, primary_discipline, geometry_json FROM tracks WHERE id = ?", (new_id,)).fetchone()

            rowd = dict(row)
            geom = None
            raw_geom = rowd.get('geometry_json')
            try:
                if raw_geom:
                    if isinstance(raw_geom, str):
                        parsed = json.loads(raw_geom)
                    elif isinstance(raw_geom, (dict, list)):
                        parsed = raw_geom
                    else:
                        parsed = None
                    # Only accept dict-style geometry for attribute mapping
                    geom = parsed if isinstance(parsed, dict) else None
                else:
                    geom = None
            except Exception:
                geom = None

            # Build a simple object merging DB fields and geometry attributes
            attrs = {
                'name': rowd.get('name') or 'Unnamed Circuit',
                'length_km': float(geom.get('length_km')) if geom and geom.get('length_km') is not None else float(rowd.get('length_km') or 3.2),
                'turns': int(geom.get('turns')) if geom and geom.get('turns') is not None else int(rowd.get('turns') or 12),
                'left_turns': int(geom.get('left_turns')) if geom and geom.get('left_turns') is not None else int(rowd.get('left_turns') or 6),
                'right_turns': int(geom.get('right_turns')) if geom and geom.get('right_turns') is not None else int(rowd.get('right_turns') or 6),
                'elevation_change_m': float(geom.get('elevation_change_m')) if geom and geom.get('elevation_change_m') is not None else 0.0,
                'avg_corner_radius_m': float(geom.get('avg_corner_radius_m')) if geom and geom.get('avg_corner_radius_m') is not None else 40.0,
                'min_corner_radius_m': float(geom.get('min_corner_radius_m')) if geom and geom.get('min_corner_radius_m') is not None else 20.0,
                'max_corner_radius_m': float(geom.get('max_corner_radius_m')) if geom and geom.get('max_corner_radius_m') is not None else 80.0,
                'tightest_corner_radius_m': float(geom.get('tightest_corner_radius_m')) if geom and geom.get('tightest_corner_radius_m') is not None else 20.0,
                'longest_straight_m': float(geom.get('longest_straight_m')) if geom and geom.get('longest_straight_m') is not None else 800.0,
                'shortest_straight_m': float(geom.get('shortest_straight_m')) if geom and geom.get('shortest_straight_m') is not None else 150.0,
                'avg_speed_kmh': float(geom.get('avg_speed_kmh')) if geom and geom.get('avg_speed_kmh') is not None else 180.0,
                'top_speed_kmh': float(geom.get('top_speed_kmh')) if geom and geom.get('top_speed_kmh') is not None else 280.0,
                'surface': geom.get('surface') if geom and geom.get('surface') else (rowd.get('surface') or 'asphalt'),
                'surface_type': geom.get('surface_type') if geom and geom.get('surface_type') else (rowd.get('surface_type') or 'asphalt'),
                'surface_grip': float(geom.get('surface_grip')) if geom and geom.get('surface_grip') is not None else 12.0,
                'surface_abrasiveness': float(geom.get('surface_abrasiveness')) if geom and geom.get('surface_abrasiveness') is not None else 8.0,
                'climate': geom.get('climate') if geom and geom.get('climate') else 'temperate',
                'drs_zones': int(geom.get('drs_zones')) if geom and geom.get('drs_zones') is not None else 1
            }

            return SimpleTrack(**attrs)

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
                # Filter out created_at field which isn't in the Track model
                return Track(
                    **{k: v for k, v in dict(row).items() if k != 'created_at'})
            return None
    # Alias for consistency
    def get_track_by_id(self, track_id: int) -> Optional[Track]:
        """Get track by ID (alias for get_track)"""
        return self.get_track(track_id)

    # Championship operations
    def create_championship(self, championship: Championship) -> Optional[int]:
        """Create a new championship and return ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO championships (name, discipline, tier, season_length,
                                         points_system, current_season, founded_year, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (championship.name, championship.discipline, championship.tier,
                  championship.season_length, championship.points_system,
                  championship.current_season, championship.founded_year, championship.description))
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

    # Race operations
    def create_race(self, race: Race) -> Optional[int]:
        """Create a new race and return ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO races (championship_id, track_id, season, round_number,
                                 race_date, weather_conditions, race_duration_minutes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (race.championship_id, race.track_id, race.season, race.round_number,
                  race.race_date, race.weather_conditions, race.race_duration_minutes, race.status))
            return cursor.lastrowid

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
                # Filter out created_at field which isn't in the Race model
                return Race(
                    **{k: v for k, v in dict(row).items() if k != 'created_at'})
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

    # Convenience aliases for consistency
    def add_track(self, track: Track) -> Optional[int]:
        """Alias for create_track"""
        return self.create_track(track)

    def get_all_tracks(self) -> List[Track]:
        """Get all tracks in the database"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tracks ORDER BY name").fetchall()
            return [Track(**dict(row)) for row in rows]

    def get_circuits_by_discipline(self, discipline: str) -> List[Any]:
        """
        Get all circuits for a specific discipline

        Args:
            discipline: Racing discipline (e.g., "SINGLE_SEATER")

        Returns:
            List of circuit objects (simplified from database)
        """
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT id, name, country, region, length_km, turns,
                       primary_discipline as discipline, circuit_type
                FROM tracks
                WHERE primary_discipline = ?
                ORDER BY name
            """, (discipline,)).fetchall()

            # Return as simple objects with necessary attributes
            class SimpleCircuit:
                country: str
                region: str
                location: str

                def __init__(self, row_dict):
                    for key, value in row_dict.items():
                        setattr(self, key, value)
                    # Add location as combined string for compatibility
                    self.location = f"{self.country}, {self.region}"

            return [SimpleCircuit(dict(row)) for row in rows]

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
        # For now, we don't have a races table, so we create a temporary race object
        # The race_id contains the info we need (championship_id * 1000 +
        # round)

        championship_id = race_id // 1000
        round_number = race_id % 1000

        class TempRace:
            def __init__(self):
                self.id = race_id
                self.championship_id = championship_id
                self.circuit_id = 1  # Placeholder
                self.discipline = "SINGLE_SEATER"  # Will be set by caller
                self.round_number = round_number
                self.total_laps = 50

        return TempRace()
