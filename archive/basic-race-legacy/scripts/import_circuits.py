"""
Import Circuits from JSON Database

Imports the 175 pre-generated circuits from circuits_database.json into the
SQLite database with full specifications including IMA grading, facilities,
environmental factors, and racing characteristics.

This script:
1. Reads circuits_database.json (175 circuits)
2. Maps JSON fields to database Track model fields
3. Inserts circuits using raw SQL for full control
4. Handles backward compatibility fields
5. Reports success/failure for each circuit

Usage:
    python scripts/import_circuits.py
"""

import json
import sqlite3
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATABASE_PATH

def map_circuit_to_db_fields(circuit: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map circuit JSON fields to database fields.
    
    Handles:
    - Field name mapping (circuit_id -> id)
    - Boolean conversion (Python bool -> SQLite INTEGER)
    - NULL handling for optional fields
    - Backward compatibility field calculation
    """
    # Calculate backward compatibility fields
    # difficulty based on corners and elevation
    difficulty = min(1.0, (circuit['turns'] / 20.0 * 0.5) + (abs(circuit['elevation_change_m']) / 100.0 * 0.5))
    
    # weather_impact based on climate and rainfall
    weather_impact = 0.3 if circuit['rainfall_mm_annual'] < 500 else 0.7
    
    # overtaking_difficulty based on track width and straights
    overtaking_difficulty = 1.0 - (circuit['track_width_avg_m'] / 20.0 * 0.5 + circuit['longest_straight_m'] / 1500.0 * 0.5)
    overtaking_difficulty = max(0.0, min(1.0, overtaking_difficulty))
    
    # Map surface types to match database enum (if needed)
    surface_type_map = {
        'asphalt': 'tarmac',
        'concrete': 'tarmac',
        'gravel': 'gravel',
        'mixed': 'mixed'
    }
    
    # Map circuit types to valid database values
    circuit_type_map = {
        'permanent': 'permanent',
        'street': 'street',
        'semi_permanent': 'semi_permanent',
        'rally_stage': 'rally_stage',
        'road_course': 'rally_stage',  # Road courses are rally stages
        'temporary': 'semi_permanent',  # Temporary circuits are semi-permanent
        'oval': 'permanent',  # Ovals are permanent circuits
        'mixed_surface': 'rally_stage'  # Mixed surface are rally stages
    }
    
    return {
        'id': circuit['circuit_id'],
        'name': circuit['name'],
        'country': circuit['country'],
        'region': circuit['region'],
        
        # Classification
        'circuit_type': circuit_type_map.get(circuit['circuit_type'], 'permanent'),
        'ima_grade': circuit['ima_grade'],
        'primary_discipline': circuit['primary_discipline'],
        
        # Track layout and geometry
        'length_km': circuit['length_km'],
        'turns': circuit['turns'],
        'left_turns': circuit['left_turns'],
        'right_turns': circuit['right_turns'],
        'elevation_change_m': circuit['elevation_change_m'],
        'max_gradient_percent': circuit['max_gradient_percent'],
        'min_gradient_percent': circuit['min_gradient_percent'],
        
        # Surface and dimensions
        'surface': circuit['surface'],
        'track_width_avg_m': circuit['track_width_avg_m'],
        'track_width_min_m': circuit['track_width_min_m'],
        'track_width_max_m': circuit['track_width_max_m'],
        
        # Speed and corners
        'avg_speed_kmh': circuit['avg_speed_kmh'],
        'top_speed_kmh': circuit['top_speed_kmh'],
        'longest_straight_m': circuit['longest_straight_m'],
        'shortest_straight_m': circuit['shortest_straight_m'],
        'tightest_corner_radius_m': circuit['tightest_corner_radius_m'],
        
        # Environmental factors
        'climate': circuit['climate'],
        'avg_temp_summer_c': circuit['avg_temp_summer_c'],
        'avg_temp_winter_c': circuit['avg_temp_winter_c'],
        'rainfall_mm_annual': circuit['rainfall_mm_annual'],
        'altitude_m': circuit['altitude_m'],
        
        # Facilities
        'pit_boxes': circuit['pit_boxes'],
        'pit_lane_length_m': circuit['pit_lane_length_m'],
        'pit_speed_limit_kmh': circuit['pit_speed_limit_kmh'],
        'paddock_capacity_teams': circuit['paddock_capacity_teams'],
        'grandstand_capacity': circuit['grandstand_capacity'],
        
        # Racing features (convert bool to int for SQLite)
        'drs_zones': circuit['drs_zones'],
        'safety_car_probability': circuit['safety_car_probability'],
        'night_racing_capable': 1 if circuit['night_racing_capable'] else 0,
        'wet_weather_racing': 1 if circuit['wet_weather_racing'] else 0,
        
        # Status and history
        'is_active': 1 if circuit['is_active'] else 0,
        'debut_year': circuit['debut_year'],
        'last_used_year': circuit['last_used_year'],
        
        # Backward compatibility fields
        'surface_type': surface_type_map.get(circuit['surface'], 'tarmac'),
        'difficulty': difficulty,
        'weather_impact': weather_impact,
        'overtaking_difficulty': overtaking_difficulty,
        'discipline': circuit['primary_discipline'],
        'lap_record_time': None,
        'description': f"{circuit['ima_grade']} grade {circuit['circuit_type']} circuit in {circuit['region']}, {circuit['country']}"
    }

def import_circuits():
    """
    Import all circuits from JSON file into database.
    """
    print("=" * 80)
    print("CIRCUIT IMPORT UTILITY")
    print("=" * 80)
    
    # Load circuits from JSON (now in data/ folder)
    parent_dir = Path(__file__).parent.parent
    circuits_file = parent_dir / 'data' / 'circuits_database.json'
    print("\n1. Loading circuits from:", circuits_file)
    
    if not circuits_file.exists():
        print("   ❌ ERROR: circuits_database.json not found!")
        print("   Expected location:", circuits_file)
        return
    
    with open(circuits_file, 'r', encoding='utf-8') as f:
        circuits = json.load(f)
    
    print("   ✅ Loaded", len(circuits), "circuits from JSON")
    
    # Connect to database
    db_path = Path(DATABASE_PATH)
    print("\n2. Connecting to database:", db_path)
    
    if not db_path.exists():
        print("   ❌ ERROR: Database not found at", db_path)
        print("   Run generate_initial_database.py first!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("   ✅ Connected to database")
    
    # Check current track count
    cursor.execute("SELECT COUNT(*) FROM tracks")
    existing_count = cursor.fetchone()[0]
    print("   📊 Current tracks in database:", existing_count)
    
    if existing_count > 0:
        print(f"\n   ⚠️  WARNING: Database already has {existing_count} tracks!")
        response = input("   Delete existing tracks and import fresh? (yes/no): ").strip().lower()
        if response == 'yes':
            cursor.execute("DELETE FROM tracks")
            conn.commit()
            print("   ✅ Deleted", existing_count, "existing tracks")
        else:
            print("   ℹ️  Skipping import (database unchanged)")
            conn.close()
            return
    
    # Prepare SQL statement with ALL fields
    insert_sql = """
        INSERT INTO tracks (
            id, name, country, region,
            circuit_type, ima_grade, primary_discipline,
            length_km, turns, left_turns, right_turns,
            elevation_change_m, max_gradient_percent, min_gradient_percent,
            surface, track_width_avg_m, track_width_min_m, track_width_max_m,
            avg_speed_kmh, top_speed_kmh, longest_straight_m, shortest_straight_m,
            tightest_corner_radius_m,
            climate, avg_temp_summer_c, avg_temp_winter_c, rainfall_mm_annual, altitude_m,
            pit_boxes, pit_lane_length_m, pit_speed_limit_kmh,
            paddock_capacity_teams, grandstand_capacity,
            drs_zones, safety_car_probability, night_racing_capable, wet_weather_racing,
            is_active, debut_year, last_used_year,
            surface_type, difficulty, weather_impact, overtaking_difficulty,
            discipline, lap_record_time, description
        ) VALUES (
            :id, :name, :country, :region,
            :circuit_type, :ima_grade, :primary_discipline,
            :length_km, :turns, :left_turns, :right_turns,
            :elevation_change_m, :max_gradient_percent, :min_gradient_percent,
            :surface, :track_width_avg_m, :track_width_min_m, :track_width_max_m,
            :avg_speed_kmh, :top_speed_kmh, :longest_straight_m, :shortest_straight_m,
            :tightest_corner_radius_m,
            :climate, :avg_temp_summer_c, :avg_temp_winter_c, :rainfall_mm_annual, :altitude_m,
            :pit_boxes, :pit_lane_length_m, :pit_speed_limit_kmh,
            :paddock_capacity_teams, :grandstand_capacity,
            :drs_zones, :safety_car_probability, :night_racing_capable, :wet_weather_racing,
            :is_active, :debut_year, :last_used_year,
            :surface_type, :difficulty, :weather_impact, :overtaking_difficulty,
            :discipline, :lap_record_time, :description
        )
    """
    
    # Import circuits
    print("\n3. Importing", len(circuits), "circuits...")
    success_count = 0
    error_count = 0
    errors = []
    
    for i, circuit in enumerate(circuits, 1):
        try:
            db_fields = map_circuit_to_db_fields(circuit)
            cursor.execute(insert_sql, db_fields)
            success_count += 1
            
            # Progress indicator
            if i % 25 == 0:
                print("   Progress:", i, "/", len(circuits), "circuits processed...")
        
        except Exception as e:
            error_count += 1
            errors.append({
                'circuit': circuit['name'],
                'error': str(e)
            })
            print("   ❌ Error importing", circuit.get('name'), ":", e)
    
    # Commit transaction
    conn.commit()
    
    # Verify import
    cursor.execute("SELECT COUNT(*) FROM tracks")
    final_count = cursor.fetchone()[0]
    
    # Print summary
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print("✅ Successfully imported:", success_count, "circuits")
    print("❌ Failed imports:", error_count, "circuits")
    print("📊 Total tracks in database:", final_count)
    
    if errors:
        print(f"\n⚠️  ERRORS ENCOUNTERED:")
        for err in errors[:10]:  # Show first 10 errors
            print(f"   - {err['circuit']}: {err['error']}")
        if len(errors) > 10:
            print("   ... and", (len(errors) - 10), "more errors")
    
    # Show sample circuits by discipline
    print("\n📋 CIRCUITS BY DISCIPLINE:")
    disciplines = [
        'SINGLE_SEATER', 'PRODUCTION_TOURING', 'RALLY_STAGE',
        'URBAN_STREET', 'DRAG_ACCELERATION', 'SPRINT_RALLYCROSS', 'ENDURANCE'
    ]
    
    for discipline in disciplines:
        cursor.execute(
            "SELECT COUNT(*), COUNT(CASE WHEN is_active = 1 THEN 1 END) FROM tracks WHERE primary_discipline = ?",
            (discipline,)
        )
        total, active = cursor.fetchone()
        print(f"   {discipline:20s}: {total:3d} circuits ({active:3d} active)")
    
    # Show sample circuits
    print("\n🏁 SAMPLE CIRCUITS:")
    cursor.execute("""
        SELECT name, country, ima_grade, circuit_type, length_km, primary_discipline
        FROM tracks
        WHERE is_active = 1
        ORDER BY RANDOM()
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        name, country, grade, _ctype, length, disc = row
        print(f"   {name:30s} | {country:15s} | {grade:8s} | {length:.2f}km | {disc}")
    
    conn.close()
    print("\n" + "=" * 80)
    print("✅ Circuit import complete!")
    print("=" * 80)

if __name__ == "__main__":
    import_circuits()
