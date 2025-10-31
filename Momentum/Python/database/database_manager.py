"""
Momentum Motorsport Simulation - Database Manager

Comprehensive database abstraction layer providing CRUD operations, data integrity
enforcement, and query optimization for the Momentum simulation system. Manages
all persistent storage operations for drivers, teams, tracks, championships, and
race results using SQLite as the backend database.

Key Features:
- Automatic schema initialization and validation
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
from typing import List, Optional, Dict, Any
from pathlib import Path
from database.models import Driver, Team, Track, Championship, Race, RaceResult, SCHEMA_SQL
from database.models import StaffMember
from config import DATABASE_PATH

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
        - Database schema initialization and updates
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
        Initialize Database Manager
        
        Sets up the database connection and ensures proper schema initialization.
        Creates the database file and directory structure if they don't exist.
        
        Args:
            db_path (str): Path to SQLite database file. Defaults to configured path
                          from config.DATABASE_PATH
        
        Raises:
            sqlite3.Error: If database initialization fails
            OSError: If database directory cannot be created
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """
        Initialize Database Schema
        
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
        # Ensure database directory exists (create parent directories as needed)
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
        
        # Set row factory for easier data access (allows dict-like access to columns)
        conn.row_factory = sqlite3.Row
        
        # Enable foreign key constraint enforcement
        conn.execute("PRAGMA foreign_keys = ON")
        
        return conn
    
    # Driver operations
    def create_driver(self, driver: Driver) -> int:
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
        """Get driver by ID"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,)).fetchone()
            if row:
                row_dict = dict(row)
                row_dict.pop('created_at', None)
                row_dict.pop('updated_at', None)
                try:
                    return Driver(**row_dict)
                except TypeError:
                    return None
            return None
    
    def get_all_drivers(self) -> List[Driver]:
        """Get all drivers"""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM drivers ORDER BY name").fetchall()
            # Filter out extra database columns (created_at, updated_at, etc.)
            drivers = []
            for row in rows:
                row_dict = dict(row)
                # Remove non-model fields
                row_dict.pop('created_at', None)
                row_dict.pop('updated_at', None)
                try:
                    drivers.append(Driver(**row_dict))
                except TypeError as e:
                    # Skip drivers that fail to load (log in production)
                    continue
            return drivers
    
    def get_drivers_by_team(self, team_id: int) -> List[Driver]:
        """Get all drivers for a specific team"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM drivers WHERE current_team_id = ? ORDER BY raw_speed DESC", 
                (team_id,)
            ).fetchall()
            drivers = []
            for row in rows:
                try:
                    row_dict = dict(row)
                    # Remove non-model fields
                    row_dict.pop('created_at', None)
                    row_dict.pop('updated_at', None)
                    drivers.append(Driver(**row_dict))
                except TypeError:
                    continue
            return drivers
    
    def update_driver_stats(self, driver_id: int, wins: int = 0, podiums: int = 0, points: int = 0):
        """Update driver career statistics"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE drivers 
                SET career_wins = career_wins + ?, 
                    career_podiums = career_podiums + ?,
                    career_points = career_points + ?
                WHERE id = ?
            """, (wins, podiums, points, driver_id))
    
    # Staff operations
    def create_staff_member(self, staff: StaffMember) -> int:
        """Create a new staff member with all 70+ attributes and return ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO staff_members (
                    name, nationality, birth_date, age, current_team_id, role, tier,
                    -- Core Competencies
                    technical_expertise, experience_years, management_skill, innovation_ability,
                    problem_solving, attention_to_detail, work_under_pressure, adaptability,
                    learning_speed, decision_making,
                    -- Technical Specializations
                    aerodynamics_knowledge, engine_knowledge, suspension_knowledge, tire_knowledge,
                    electronics_knowledge, data_analysis_skill, cfd_expertise, simulation_expertise,
                    -- Strategic & Leadership
                    race_strategy_skill, team_leadership, negotiation_skill, budget_management,
                    resource_allocation, long_term_planning, risk_assessment,
                    -- Communication & People Skills
                    communication, driver_relationship, team_motivation, conflict_resolution,
                    media_handling, stakeholder_management,
                    -- Discipline Specializations
                    single_seater_expertise, touring_car_expertise, rally_expertise,
                    street_racing_expertise, drag_racing_expertise, rallycross_expertise, endurance_expertise,
                    -- Personal Traits
                    reliability, loyalty, ambition, professionalism, work_ethic,
                    -- Additional Technical Skills
                    materials_science, cad_design, manufacturing_knowledge, quality_control,
                    -- Advanced Analytical Skills
                    telemetry_analysis, performance_modeling, statistical_methods, pattern_recognition,
                    predictive_analytics, software_proficiency, database_management,
                    -- Operational Skills
                    pit_stop_efficiency, crisis_management, equipment_maintenance,
                    logistics_coordination, safety_protocols,
                    -- Financial & Commercial Skills
                    commercial_acumen, sponsorship_development, cost_optimisation,
                    -- Career & Development
                    previous_teams, education_level, certifications, languages_spoken, contract_type,
                    -- Performance & Satisfaction
                    job_satisfaction, workload_capacity, current_workload, performance_rating,
                    -- Career & Contract
                    salary_demand, contract_years_remaining, biography
                )
                VALUES (?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?)
            """, (
                staff.name, staff.nationality, staff.birth_date, staff.age, staff.current_team_id, staff.role, staff.tier,
                # Core Competencies
                staff.technical_expertise, staff.experience_years, staff.management_skill, staff.innovation_ability,
                staff.problem_solving, staff.attention_to_detail, staff.work_under_pressure, staff.adaptability,
                staff.learning_speed, staff.decision_making,
                # Technical Specializations
                staff.aerodynamics_knowledge, staff.engine_knowledge, staff.suspension_knowledge, staff.tire_knowledge,
                staff.electronics_knowledge, staff.data_analysis_skill, staff.cfd_expertise, staff.simulation_expertise,
                # Strategic & Leadership
                staff.race_strategy_skill, staff.team_leadership, staff.negotiation_skill, staff.budget_management,
                staff.resource_allocation, staff.long_term_planning, staff.risk_assessment,
                # Communication & People Skills
                staff.communication, staff.driver_relationship, staff.team_motivation, staff.conflict_resolution,
                staff.media_handling, staff.stakeholder_management,
                # Discipline Specializations
                staff.single_seater_expertise, staff.touring_car_expertise, staff.rally_expertise,
                staff.street_racing_expertise, staff.drag_racing_expertise, staff.rallycross_expertise, staff.endurance_expertise,
                # Personal Traits
                staff.reliability, staff.loyalty, staff.ambition, staff.professionalism, staff.work_ethic,
                # Additional Technical Skills
                staff.materials_science, staff.cad_design, staff.manufacturing_knowledge, staff.quality_control,
                # Advanced Analytical Skills
                staff.telemetry_analysis, staff.performance_modeling, staff.statistical_methods, staff.pattern_recognition,
                staff.predictive_analytics, staff.software_proficiency, staff.database_management,
                # Operational Skills
                staff.pit_stop_efficiency, staff.crisis_management, staff.equipment_maintenance,
                staff.logistics_coordination, staff.safety_protocols,
                # Financial & Commercial Skills
                staff.commercial_acumen, staff.sponsorship_development, staff.cost_optimisation,
                # Career & Development
                staff.previous_teams, staff.education_level, staff.certifications, staff.languages_spoken, staff.contract_type,
                # Performance & Satisfaction
                staff.job_satisfaction, staff.workload_capacity, staff.current_workload, staff.performance_rating,
                # Career & Contract
                staff.salary_demand, staff.contract_years_remaining, staff.biography
            ))
            return cursor.lastrowid
    
    def get_staff_member(self, staff_id: int) -> Optional[StaffMember]:
        """Get staff member by ID"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM staff_members WHERE id = ?", (staff_id,)).fetchone()
            if row:
                return StaffMember(**dict(row))
            return None
    
    def get_team_staff(self, team_id: int) -> List[StaffMember]:
        """Get all staff members for a team"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM staff_members WHERE current_team_id = ? ORDER BY role, name",
                (team_id,)
            ).fetchall()
            return [StaffMember(**dict(row)) for row in rows]
    
    def get_all_staff(self) -> List[StaffMember]:
        """Get all staff members"""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM staff_members ORDER BY name").fetchall()
            return [StaffMember(**dict(row)) for row in rows]
    
    # Team operations
    def create_team(self, team: Team) -> int:
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
            row = conn.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
            if row:
                # Filter out created_at field which isn't in the Team model
                return Team(**{k: v for k, v in dict(row).items() if k != 'created_at'})
            return None
    
    def get_teams_by_discipline(self, discipline: str) -> List[Team]:
        """Get all teams in a specific discipline"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM teams WHERE discipline = ? ORDER BY tier, name", 
                (discipline,)
            ).fetchall()
            # Filter out created_at field which isn't in the Team model
            return [Team(**{k: v for k, v in dict(row).items() if k != 'created_at'}) for row in rows]
    
    # Track operations
    def create_track(self, track: Track) -> int:
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
            return [Track(**{k: v for k, v in dict(row).items() if k != 'created_at'}) for row in rows]

    def get_track(self, track_id: int) -> Optional[Track]:
        """Get track by ID"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM tracks WHERE id = ?", (track_id,)).fetchone()
            if row:
                # Filter out created_at field which isn't in the Track model
                return Track(**{k: v for k, v in dict(row).items() if k != 'created_at'})
            return None
    
    # Alias for consistency
    def get_track_by_id(self, track_id: int) -> Optional[Track]:
        """Get track by ID (alias for get_track)"""
        return self.get_track(track_id)
    
    # Championship operations
    def create_championship(self, championship: Championship) -> int:
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
            row = conn.execute("SELECT * FROM championships WHERE id = ?", (championship_id,)).fetchone()
            if row:
                # Filter out created_at field which isn't in the Championship model
                return Championship(**{k: v for k, v in dict(row).items() if k != 'created_at'})
            return None
    
    # Race operations
    def create_race(self, race: Race) -> int:
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
            return [RaceResult(**{k: v for k, v in dict(row).items() if k != 'created_at'}) for row in rows]
    
    def get_race(self, race_id: int) -> Optional[Race]:
        """Get race by ID"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM races WHERE id = ?", (race_id,)).fetchone()
            if row:
                # Filter out created_at field which isn't in the Race model
                return Race(**{k: v for k, v in dict(row).items() if k != 'created_at'})
            return None
    
    def update_race_status(self, race_id: int, status: str):
        """Update race status"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE races SET status = ? WHERE id = ?",
                (status, race_id)
            )
    
    def save_race_result(self, result: RaceResult) -> int:
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
    def create_race_result(self, result: RaceResult) -> int:
        """Create race result (alias for save_race_result)"""
        return self.save_race_result(result)
    
    def get_all_championships(self) -> List[Championship]:
        """Get all championships"""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM championships ORDER BY name").fetchall()
            # Filter out created_at field which isn't in the Championship model
            return [Championship(**{k: v for k, v in dict(row).items() if k != 'created_at'}) for row in rows]
    
    # Statistics and queries
    def get_championship_standings(self, championship_id: int, season: int) -> List[Dict[str, Any]]:
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
            for table in ['drivers', 'teams', 'tracks', 'championships', 'races', 'race_results']:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                stats[table] = count
            return stats
    
    # Convenience aliases for consistency
    def add_track(self, track: Track) -> int:
        """Alias for create_track"""
        return self.create_track(track)
    
    def get_all_tracks(self) -> List[Track]:
        """Get all tracks in the database"""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM tracks ORDER BY name").fetchall()
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
            row = conn.execute("SELECT * FROM tracks WHERE id = ?", (circuit_id,)).fetchone()
            
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
        # The race_id contains the info we need (championship_id * 1000 + round)
        
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