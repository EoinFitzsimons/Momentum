"""
Component State Persistence

Handles saving and loading component states to/from database.
Stores serialized component data for persistent race car state across sessions.

Authors: Final Year Project - Computer Science
"""

import sqlite3
import pickle
import json
from typing import Optional, Dict, List
from pathlib import Path

from vehicles.vehicle import RaceCar


class ComponentPersistence:
    """
    Handles database persistence for component states
    
    Stores:
    - Serialized RaceCar instances
    - Component health history
    - Damage events
    - Repair history
    """
    
    def __init__(self, db_path: str = "momentum.db"):
        self.db_path = db_path
        self.ensure_schema()
    
    def ensure_schema(self):
        """Create component tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Component states table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS component_states (
                vehicle_id INTEGER PRIMARY KEY,
                race_car_data BLOB NOT NULL,
                last_updated TEXT NOT NULL,
                season_year INTEGER NOT NULL,
                total_km REAL DEFAULT 0.0
            )
        """)
        
        # Component health history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS component_health_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                recorded_date TEXT NOT NULL,
                component_name TEXT NOT NULL,
                health_percentage REAL NOT NULL,
                FOREIGN KEY (vehicle_id) REFERENCES component_states(vehicle_id)
            )
        """)
        
        # Damage events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS damage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                event_date TEXT NOT NULL,
                session_type TEXT NOT NULL,
                lap_number INTEGER NOT NULL,
                component_name TEXT NOT NULL,
                severity REAL NOT NULL,
                cause TEXT NOT NULL,
                FOREIGN KEY (vehicle_id) REFERENCES component_states(vehicle_id)
            )
        """)
        
        # Repair history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                repair_date TEXT NOT NULL,
                components_repaired TEXT NOT NULL,
                cost_millions REAL NOT NULL,
                time_hours REAL NOT NULL,
                success INTEGER NOT NULL,
                FOREIGN KEY (vehicle_id) REFERENCES component_states(vehicle_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_race_car(self, vehicle_id: int, race_car: RaceCar, season_year: int) -> bool:
        """
        Save a RaceCar instance to database
        
        Args:
            vehicle_id: Vehicle ID
            race_car: RaceCar instance to save
            season_year: Current season year
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Serialize RaceCar using pickle
            race_car_blob = pickle.dumps(race_car)
            
            # Get current date/time
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            
            # Calculate total km (would come from race tracking)
            total_km = 0.0
            if race_car.engine:
                total_km = race_car.engine.total_km
            
            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO component_states
                (vehicle_id, race_car_data, last_updated, season_year, total_km)
                VALUES (?, ?, ?, ?, ?)
            """, (vehicle_id, race_car_blob, timestamp, season_year, total_km))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving race car: {e}")
            return False
    
    def load_race_car(self, vehicle_id: int) -> Optional[RaceCar]:
        """
        Load a RaceCar instance from database
        
        Args:
            vehicle_id: Vehicle ID
            
        Returns:
            RaceCar instance or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT race_car_data FROM component_states
                WHERE vehicle_id = ?
            """, (vehicle_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                race_car = pickle.loads(row[0])
                return race_car
            
            return None
            
        except Exception as e:
            print(f"Error loading race car: {e}")
            return None
    
    def record_component_health(self, vehicle_id: int, component_health: Dict[str, float]) -> bool:
        """
        Record component health snapshot
        
        Args:
            vehicle_id: Vehicle ID
            component_health: Dict of component -> health percentage
            
        Returns:
            True if successful
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for component, health in component_health.items():
                cursor.execute("""
                    INSERT INTO component_health_history
                    (vehicle_id, recorded_date, component_name, health_percentage)
                    VALUES (?, ?, ?, ?)
                """, (vehicle_id, timestamp, component, health * 100))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error recording component health: {e}")
            return False
    
    def record_damage_event(self, vehicle_id: int, component_name: str, 
                           severity: float, cause: str, session_type: str,
                           lap_number: int) -> bool:
        """
        Record a damage event
        
        Args:
            vehicle_id: Vehicle ID
            component_name: Component that was damaged
            severity: Damage severity (0.0-1.0)
            cause: Cause of damage
            session_type: Session type
            lap_number: Lap when damage occurred
            
        Returns:
            True if successful
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO damage_events
                (vehicle_id, event_date, session_type, lap_number, 
                 component_name, severity, cause)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (vehicle_id, timestamp, session_type, lap_number,
                  component_name, severity, cause))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error recording damage event: {e}")
            return False
    
    def record_repair(self, vehicle_id: int, components: List[str],
                     cost: float, time_hours: float, success: bool) -> bool:
        """
        Record a repair event
        
        Args:
            vehicle_id: Vehicle ID
            components: List of components repaired
            cost: Cost in millions
            time_hours: Time taken in hours
            success: Whether repair was successful
            
        Returns:
            True if successful
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            components_str = ", ".join(components)
            
            cursor.execute("""
                INSERT INTO repair_history
                (vehicle_id, repair_date, components_repaired, 
                 cost_millions, time_hours, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (vehicle_id, timestamp, components_str,
                  cost, time_hours, 1 if success else 0))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error recording repair: {e}")
            return False
    
    def get_damage_history(self, vehicle_id: int, limit: int = 50) -> List[Dict]:
        """
        Get damage history for vehicle
        
        Args:
            vehicle_id: Vehicle ID
            limit: Max number of events to return
            
        Returns:
            List of damage event dicts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT event_date, session_type, lap_number, 
                       component_name, severity, cause
                FROM damage_events
                WHERE vehicle_id = ?
                ORDER BY event_date DESC
                LIMIT ?
            """, (vehicle_id, limit))
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    "date": row[0],
                    "session": row[1],
                    "lap": row[2],
                    "component": row[3],
                    "severity": row[4],
                    "cause": row[5]
                })
            
            conn.close()
            return events
            
        except Exception as e:
            print(f"Error getting damage history: {e}")
            return []
    
    def get_repair_history(self, vehicle_id: int, limit: int = 50) -> List[Dict]:
        """
        Get repair history for vehicle
        
        Args:
            vehicle_id: Vehicle ID
            limit: Max number of repairs to return
            
        Returns:
            List of repair event dicts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT repair_date, components_repaired, 
                       cost_millions, time_hours, success
                FROM repair_history
                WHERE vehicle_id = ?
                ORDER BY repair_date DESC
                LIMIT ?
            """, (vehicle_id, limit))
            
            repairs = []
            for row in cursor.fetchall():
                repairs.append({
                    "date": row[0],
                    "components": row[1],
                    "cost": row[2],
                    "time_hours": row[3],
                    "success": bool(row[4])
                })
            
            conn.close()
            return repairs
            
        except Exception as e:
            print(f"Error getting repair history: {e}")
            return []
    
    def get_component_health_trend(self, vehicle_id: int, 
                                   component_name: str,
                                   limit: int = 100) -> List[Dict]:
        """
        Get health trend for a specific component
        
        Args:
            vehicle_id: Vehicle ID
            component_name: Component to track
            limit: Max data points
            
        Returns:
            List of health data points
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT recorded_date, health_percentage
                FROM component_health_history
                WHERE vehicle_id = ? AND component_name = ?
                ORDER BY recorded_date DESC
                LIMIT ?
            """, (vehicle_id, component_name, limit))
            
            data_points = []
            for row in cursor.fetchall():
                data_points.append({
                    "date": row[0],
                    "health": row[1]
                })
            
            conn.close()
            return data_points
            
        except Exception as e:
            print(f"Error getting health trend: {e}")
            return []
    
    def delete_vehicle_data(self, vehicle_id: int) -> bool:
        """
        Delete all component data for a vehicle
        
        Args:
            vehicle_id: Vehicle ID
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM component_states WHERE vehicle_id = ?", (vehicle_id,))
            cursor.execute("DELETE FROM component_health_history WHERE vehicle_id = ?", (vehicle_id,))
            cursor.execute("DELETE FROM damage_events WHERE vehicle_id = ?", (vehicle_id,))
            cursor.execute("DELETE FROM repair_history WHERE vehicle_id = ?", (vehicle_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting vehicle data: {e}")
            return False


__all__ = ['ComponentPersistence']
