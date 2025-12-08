import os
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parent
    project_root = repo_root.parent
    py_pkg = project_root / "Momentum" / "Python"
    # Ensure package imports work (database package expects to be imported from Momentum/Python)
    sys.path.insert(0, str(py_pkg))

    # Target DB path inside Momentum/Python/database
    db_dir = py_pkg / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "momentum_generated.db"

    # Export DATABASE_PATH env var so config picks it up if imported
    os.environ["DATABASE_PATH"] = str(db_path)

    # Import database manager after env var and sys.path adjustments
    from database.database_manager import DatabaseManager

    print(f"Initializing database at: {db_path}")
    mgr = DatabaseManager(db_path=str(db_path))

    # Seed a minimal team
    with mgr.get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO teams (name, nationality, founded_year, discipline, tier, budget, headquarters, team_principal, biography) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("Seed Team", "IRL", 2000, "SINGLE_SEATER", "tier3", 5.0, "Dublin", "Seed Principal", "Seeded team for testing")
        )

        # Minimal driver insert - rely on defaults for the many attributes
        conn.execute(
            "INSERT OR IGNORE INTO drivers (name, nationality, birth_date) VALUES (?, ?, ?)",
            ("Seed Driver", "IRL", "1995-01-01")
        )

        # Minimal track insert - provide required NOT NULL columns
        track_vals = (
            "Seed Circuit",
            "Ireland",
            "Leinster",
            "permanent",
            "Bronze",
            "SINGLE_SEATER",
            3.2, 12, 6, 6, 15.0, 6.0, -4.0, "asphalt",
            12.0, 9.5, 15.0, 160.0, 300.0, 800, 60, 30.0,
            "temperate", 18.0, 6.0, 800, 150, 20, 350.0, 80, 20, 15000, 2, 0.05, 1, 1, 1, 1998
        )
        print("DEBUG: track_vals length=", len(track_vals))
        print("DEBUG: track_vals sample=", track_vals[:6], "...", track_vals[-6:])
        conn.execute(
            "INSERT OR IGNORE INTO tracks (name, country, region, circuit_type, ima_grade, primary_discipline, length_km, turns, left_turns, right_turns, elevation_change_m, max_gradient_percent, min_gradient_percent, surface, track_width_avg_m, track_width_min_m, track_width_max_m, avg_speed_kmh, top_speed_kmh, longest_straight_m, shortest_straight_m, tightest_corner_radius_m, climate, avg_temp_summer_c, avg_temp_winter_c, rainfall_mm_annual, altitude_m, pit_boxes, pit_lane_length_m, pit_speed_limit_kmh, paddock_capacity_teams, grandstand_capacity, drs_zones, safety_car_probability, night_racing_capable, wet_weather_racing, is_active, debut_year) VALUES (%s)" % (', '.join(['?'] * 38)),
            track_vals
        )

        conn.commit()

    stats = mgr.get_database_stats()
    print("Database stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("Seeding complete. DB path:", db_path)


if __name__ == "__main__":
    main()
