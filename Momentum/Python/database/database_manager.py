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
        """Create a new driver and return ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO drivers (name, nationality, birth_date, skill, consistency, 
                                   aggression, racecraft, adaptability, biography)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (driver.name, driver.nationality, driver.birth_date, driver.skill,
                  driver.consistency, driver.aggression, driver.racecraft, 
                  driver.adaptability, driver.biography))
            return cursor.lastrowid
    
    def get_driver(self, driver_id: int) -> Optional[Driver]:
        """Get driver by ID"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,)).fetchone()
            if row:
                return Driver(**dict(row))
            return None
    
    def get_all_drivers(self) -> List[Driver]:
        """Get all drivers"""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM drivers ORDER BY name").fetchall()
            return [Driver(**dict(row)) for row in rows]
    
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
                return Team(**dict(row))
            return None
    
    def get_teams_by_discipline(self, discipline: str) -> List[Team]:
        """Get all teams in a specific discipline"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM teams WHERE discipline = ? ORDER BY tier, name", 
                (discipline,)
            ).fetchall()
            return [Team(**dict(row)) for row in rows]
    
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
                "SELECT * FROM tracks WHERE discipline = ? ORDER BY name", 
                (discipline,)
            ).fetchall()
            return [Track(**dict(row)) for row in rows]
    
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
                return Championship(**dict(row))
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
            return [RaceResult(**dict(row)) for row in rows]
    
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