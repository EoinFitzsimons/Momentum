"""
Circuit Data Import Script

Imports 175 circuits from data/circuits_database.json into SQLite database.
Creates tracks table if missing, validates circuit data, and reports import status.

Usage:
    python scripts/import_circuits.py
"""

from config import DATABASE_PATH
from database.database_manager import DatabaseManager
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_circuit_json(json_path: str) -> list[dict]:
    """Load circuit data from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_tracks_table_if_missing(db: DatabaseManager):
    """Create tracks table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        region TEXT,
        circuit_type TEXT NOT NULL,
        ima_grade TEXT NOT NULL,
        primary_discipline TEXT NOT NULL,
        length_km REAL NOT NULL,
        turns INTEGER NOT NULL,
        left_turns INTEGER,
        right_turns INTEGER,
        elevation_change_m REAL,
        max_gradient_percent REAL,
        min_gradient_percent REAL,
        surface TEXT NOT NULL,
        avg_speed_kmh REAL,
        top_speed_kmh REAL,
        longest_straight_m INTEGER,
        shortest_straight_m INTEGER,
        tightest_corner_radius_m REAL,
        track_width_avg_m REAL,
        track_width_min_m REAL,
        track_width_max_m REAL,
        climate TEXT,
        avg_temp_summer_c REAL,
        avg_temp_winter_c REAL,
        rainfall_mm_annual INTEGER,
        altitude_m INTEGER,
        pit_boxes INTEGER,
        pit_lane_length_m REAL,
        pit_speed_limit_kmh INTEGER,
        paddock_capacity_teams INTEGER,
        grandstand_capacity INTEGER,
        drs_zones INTEGER,
        safety_car_probability REAL,
        night_racing_capable INTEGER,
        wet_weather_racing INTEGER,
        is_active INTEGER,
        debut_year INTEGER,
        last_used_year INTEGER
    );
    """

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()
    print("✓ Tracks table created/verified")


def import_circuit(conn, circuit: dict) -> bool:
    """Import a single circuit into the database using shared connection."""
    try:
        # Map circuit_type from JSON to schema values
        circuit_type_map = {
            'permanent': 'permanent',
            'street': 'street',
            'semi_permanent': 'semi_permanent',
            'rally_stage': 'rally_stage',
            'road_course': 'permanent',  # Map road_course to permanent
            'temporary': 'semi_permanent'  # Map temporary to semi_permanent
        }

        mapped_type = circuit_type_map.get(
            circuit['circuit_type'], 'permanent')

        insert_sql = """
        INSERT OR REPLACE INTO tracks (
            id, name, country, region, circuit_type, ima_grade, primary_discipline,
            length_km, turns, left_turns, right_turns, elevation_change_m,
            max_gradient_percent, min_gradient_percent, surface, avg_speed_kmh,
            top_speed_kmh, longest_straight_m, shortest_straight_m,
            tightest_corner_radius_m, track_width_avg_m, track_width_min_m,
            track_width_max_m, climate, avg_temp_summer_c, avg_temp_winter_c,
            rainfall_mm_annual, altitude_m, pit_boxes, pit_lane_length_m,
            pit_speed_limit_kmh, paddock_capacity_teams, grandstand_capacity,
            drs_zones, safety_car_probability, night_racing_capable,
            wet_weather_racing, is_active, debut_year, last_used_year
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor = conn.cursor()
        cursor.execute(insert_sql, (
            circuit['circuit_id'],
            circuit['name'],
            circuit['country'],
            circuit['region'],
            mapped_type,
            circuit['ima_grade'],
            circuit['primary_discipline'],
            circuit['length_km'],
            circuit['turns'],
            circuit['left_turns'],
            circuit['right_turns'],
            circuit['elevation_change_m'],
            circuit['max_gradient_percent'],
            circuit['min_gradient_percent'],
            circuit['surface'],
            circuit['avg_speed_kmh'],
            circuit['top_speed_kmh'],
            circuit['longest_straight_m'],
            circuit['shortest_straight_m'],
            circuit['tightest_corner_radius_m'],
            circuit['track_width_avg_m'],
            circuit['track_width_min_m'],
            circuit['track_width_max_m'],
            circuit['climate'],
            circuit['avg_temp_summer_c'],
            circuit['avg_temp_winter_c'],
            circuit['rainfall_mm_annual'],
            circuit['altitude_m'],
            circuit['pit_boxes'],
            circuit['pit_lane_length_m'],
            circuit['pit_speed_limit_kmh'],
            circuit['paddock_capacity_teams'],
            circuit['grandstand_capacity'],
            circuit['drs_zones'],
            circuit['safety_car_probability'],
            1 if circuit['night_racing_capable'] else 0,
            1 if circuit['wet_weather_racing'] else 0,
            1 if circuit['is_active'] else 0,
            circuit['debut_year'],
            circuit.get('last_used_year')
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"✗ Failed to import {circuit['name']}: {e}")
        return False


def main():
    print("\n" + "=" * 70)
    print("CIRCUIT IMPORT SCRIPT")
    print("=" * 70)
    print(f"Database: {DATABASE_PATH}")

    # Load circuit JSON
    json_path = Path(__file__).parent.parent / \
        "data" / "circuits_database.json"
    print(f"Source: {json_path}")

    if not json_path.exists():
        print(f"✗ Circuit JSON not found at {json_path}")
        return 1

    circuits = load_circuit_json(str(json_path))
    print(f"✓ Loaded {len(circuits)} circuits from JSON\n")

    # Connect to database
    db = DatabaseManager()
    print("✓ Connected to database")

    # Create table if missing
    create_tracks_table_if_missing(db)

    # Import circuits using single shared connection
    print("\nImporting circuits...")
    success_count = 0
    fail_count = 0

    # Track discipline distribution
    discipline_counts = {}

    conn = db.get_connection()
    for circuit in circuits:
        if import_circuit(conn, circuit):
            success_count += 1
            disc = circuit['primary_discipline']
            discipline_counts[disc] = discipline_counts.get(disc, 0) + 1
        else:
            fail_count += 1
    conn.close()

    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"✓ Successfully imported: {success_count}")
    print(f"✗ Failed: {fail_count}")
    print(f"Total circuits in database: {success_count}")

    # Discipline breakdown
    print("\nDiscipline Distribution:")
    for disc, count in sorted(discipline_counts.items()):
        print(f"  {disc}: {count} circuits")

    # Verify Single Seater circuits for MVP
    single_seater_count = discipline_counts.get('SINGLE_SEATER', 0)
    print(
        f"\n✓ Single Seater circuits available for MVP: {single_seater_count}")

    # Sample query to verify data
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, country, length_km, turns, ima_grade
        FROM tracks
        WHERE primary_discipline = 'SINGLE_SEATER'
        ORDER BY ima_grade DESC, length_km DESC
        LIMIT 5
    """)

    print("\nTop 5 Single Seater circuits (by grade & length):")
    for row in cursor.fetchall():
        print(
            f"  • {
                row[0]} ({
                row[1]}) - {
                row[2]}km, {
                    row[3]} turns, Grade {
                        row[4]}")

    conn.close()

    print("\n" + "=" * 70)
    print("Import complete!")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
