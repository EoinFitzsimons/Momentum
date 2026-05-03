"""
Generate tracks for each racing discipline with PROCEDURAL generation.

Features:
- Random corner counts, angles, radii within discipline constraints
- Self-intersection detection and retry logic
- Discipline-specific parameter ranges
- PNG visualizations

Outputs to: data/track_previews/
"""

import sys
import random
import math
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.database_manager import DatabaseManager


def check_line_intersection(p1, p2, p3, p4):
    """Check if line segments (p1,p2) and (p3,p4) intersect"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return False  # Parallel

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0 < t < 1 and 0 < u < 1:
        return True
    return False


def simulate_track_path(instructions, max_instructions=20):
    """Simulate track path to get approximate points for intersection checking"""
    x, y, theta = 0, 0, 0
    points = [(x, y)]

    for instruction in instructions[:max_instructions]:
        if instruction["type"] == "S":
            length = instruction["length_m"]
            steps = max(3, int(length / 50))
            for _ in range(steps):
                x += math.cos(theta) * (length / steps)
                y += math.sin(theta) * (length / steps)
                points.append((x, y))

        elif instruction["type"] == "C":
            angle_rad = math.radians(instruction["angle_deg"])
            radius = instruction["radius_m"]
            steps = max(3, int(abs(instruction["angle_deg"]) / 10))

            for i in range(steps):
                theta += angle_rad / steps
                arc_len = radius * abs(angle_rad / steps * math.pi / 180)
                x += math.cos(theta) * arc_len
                y += math.sin(theta) * arc_len
                points.append((x, y))

    return points


def check_self_intersection(points, skip_distance=8):
    """Check if track intersects itself (excluding nearby segments)"""
    n = len(points)
    if n < skip_distance * 2:
        return False

    # Check segments against non-adjacent segments
    for i in range(n - 1):
        for j in range(i + skip_distance, n - 1):
            if check_line_intersection(
                points[i], points[i + 1], points[j], points[j + 1]
            ):
                return True
    return False


def generate_procedural_track(discipline_params, seed=None):
    """
    Generate random track with discipline-specific parameters.
    Retries if self-intersection detected.
    """
    if seed is not None:
        random.seed(seed)

    corner_range = discipline_params["corner_range"]
    straight_range = discipline_params["straight_range"]
    radius_range = discipline_params["radius_range"]
    angle_options = discipline_params["angle_options"]
    max_attempts = discipline_params.get("max_attempts", 25)

    for attempt in range(max_attempts):
        instructions = []
        num_corners = random.randint(*corner_range)

        # Generate angles that roughly balance to 360 degrees
        angles = []
        remaining_angle = 360

        for i in range(num_corners):
            if i == num_corners - 1:
                # Last corner compensates for drift
                angle = remaining_angle
                # Clamp to reasonable values
                angle = max(-150, min(150, angle))
            else:
                angle = random.choice(angle_options)
                remaining_angle -= angle

            angles.append(angle)

        # Build track instructions
        for angle in angles:
            straight = random.randint(*straight_range)
            instructions.append({"type": "S", "length_m": straight})

            radius = random.randint(*radius_range)
            clothoid = int(radius * 0.55)
            k = 1.0 / (radius * 10000)

            instructions.append(
                {
                    "type": "C",
                    "angle_deg": angle,
                    "radius_m": radius,
                    "clothoid_len": clothoid,
                    "k": k,
                }
            )

        # Test for self-intersection
        path_points = simulate_track_path(instructions)
        if not check_self_intersection(path_points):
            print(
                f"  Procedural generation succeeded (attempt {attempt + 1}, {num_corners} corners)"
            )
            return instructions

    # Use fallback if all attempts fail
    print(f"  WARNING: Using fallback after {max_attempts} attempts")
    return discipline_params["fallback"]


def create_drag_strip_instructions():
    """Drag strip - simple straight line (no randomness needed)"""
    return [{"type": "S", "length_m": 402}]


def create_rallycross_instructions():
    """Rallycross - tight technical circuit with joker lap"""
    params = {
        "corner_range": (7, 10),
        "straight_range": (120, 350),
        "radius_range": (35, 75),
        "angle_options": [-105, -90, -75, -60, 60, 75, 90, 105],
        "max_attempts": 30,
        "fallback": [  # Safe fallback if generation fails
            {"type": "S", "length_m": 200},
            {
                "type": "C",
                "angle_deg": 90,
                "radius_m": 50,
                "clothoid_len": 30,
                "k": 0.0001,
            },
            {"type": "S", "length_m": 180},
            {
                "type": "C",
                "angle_deg": -90,
                "radius_m": 55,
                "clothoid_len": 33,
                "k": 0.00009,
            },
            {"type": "S", "length_m": 220},
            {
                "type": "C",
                "angle_deg": 90,
                "radius_m": 48,
                "clothoid_len": 29,
                "k": 0.00011,
            },
            {"type": "S", "length_m": 190},
            {
                "type": "C",
                "angle_deg": -90,
                "radius_m": 52,
                "clothoid_len": 31,
                "k": 0.0001,
            },
        ],
    }

    main_circuit = generate_procedural_track(params, seed=42)

    # Add joker lap (simpler alternate route)
    joker_instructions = [
        {"type": "S", "length_m": 120},
        {
            "type": "C",
            "angle_deg": -75,
            "radius_m": 40,
            "clothoid_len": 25,
            "k": 0.00013,
        },
        {"type": "S", "length_m": 100},
        {
            "type": "C",
            "angle_deg": 75,
            "radius_m": 40,
            "clothoid_len": 25,
            "k": 0.00013,
        },
    ]

    main_circuit.append({"type": "JOKER", "instructions": joker_instructions})
    return main_circuit


def create_single_seater_circuit_instructions():
    """Single seater - high-speed with long straights and flowing corners"""
    params = {
        "corner_range": (8, 11),
        "straight_range": (500, 1300),
        "radius_range": (120, 210),
        "angle_options": [-80, -70, -60, -45, 45, 60, 70, 80],
        "max_attempts": 30,
        "fallback": [
            {"type": "S", "length_m": 1000},
            {
                "type": "C",
                "angle_deg": 60,
                "radius_m": 180,
                "clothoid_len": 100,
                "k": 0.00006,
            },
            {"type": "S", "length_m": 800},
            {
                "type": "C",
                "angle_deg": -90,
                "radius_m": 150,
                "clothoid_len": 85,
                "k": 0.00007,
            },
            {"type": "S", "length_m": 700},
            {
                "type": "C",
                "angle_deg": 120,
                "radius_m": 130,
                "clothoid_len": 75,
                "k": 0.00008,
            },
            {"type": "S", "length_m": 600},
            {
                "type": "C",
                "angle_deg": -90,
                "radius_m": 160,
                "clothoid_len": 90,
                "k": 0.00007,
            },
        ],
    }
    return generate_procedural_track(params, seed=43)


def create_touring_circuit_instructions():
    """Touring - mix of tight hairpins and fast corners"""
    params = {
        "corner_range": (11, 15),
        "straight_range": (180, 500),
        "radius_range": (30, 140),
        "angle_options": [-130, -105, -90, -75, -50, 50, 75, 90, 105, 130],
        "max_attempts": 30,
        "fallback": [
            {"type": "S", "length_m": 400},
            {
                "type": "C",
                "angle_deg": 90,
                "radius_m": 70,
                "clothoid_len": 40,
                "k": 0.0001,
            },
            {"type": "S", "length_m": 300},
            {
                "type": "C",
                "angle_deg": -120,
                "radius_m": 40,
                "clothoid_len": 25,
                "k": 0.00015,
            },
            {"type": "S", "length_m": 350},
            {
                "type": "C",
                "angle_deg": 75,
                "radius_m": 90,
                "clothoid_len": 50,
                "k": 0.0001,
            },
            {"type": "S", "length_m": 280},
            {
                "type": "C",
                "angle_deg": -75,
                "radius_m": 100,
                "clothoid_len": 55,
                "k": 0.00009,
            },
        ],
    }
    return generate_procedural_track(params, seed=44)


def create_urban_circuit_instructions():
    """Urban street - tight corners, chicanes, varied angles"""
    params = {
        "corner_range": (12, 16),
        "straight_range": (110, 380),
        "radius_range": (20, 50),
        "angle_options": [-110, -95, -90, -75, -65, 65, 75, 90, 95, 110],
        "max_attempts": 35,
        "fallback": [
            {"type": "S", "length_m": 300},
            {
                "type": "C",
                "angle_deg": 90,
                "radius_m": 30,
                "clothoid_len": 20,
                "k": 0.00025,
            },
            {"type": "S", "length_m": 200},
            {
                "type": "C",
                "angle_deg": -90,
                "radius_m": 32,
                "clothoid_len": 22,
                "k": 0.00024,
            },
            {"type": "S", "length_m": 250},
            {
                "type": "C",
                "angle_deg": 90,
                "radius_m": 28,
                "clothoid_len": 19,
                "k": 0.00027,
            },
            {"type": "S", "length_m": 180},
            {
                "type": "C",
                "angle_deg": -90,
                "radius_m": 35,
                "clothoid_len": 23,
                "k": 0.00023,
            },
        ],
    }
    return generate_procedural_track(params, seed=45)


def create_endurance_circuit_instructions():
    """Endurance - very long straights with mix of fast and slow corners"""
    params = {
        "corner_range": (10, 14),
        "straight_range": (600, 2000),
        "radius_range": (40, 190),
        "angle_options": [-120, -90, -70, -50, 50, 70, 90, 120],
        "max_attempts": 30,
        "fallback": [
            {"type": "S", "length_m": 1800},
            {
                "type": "C",
                "angle_deg": 90,
                "radius_m": 160,
                "clothoid_len": 90,
                "k": 0.00007,
            },
            {"type": "S", "length_m": 1500},
            {
                "type": "C",
                "angle_deg": -110,
                "radius_m": 50,
                "clothoid_len": 30,
                "k": 0.00015,
            },
            {"type": "S", "length_m": 1200},
            {
                "type": "C",
                "angle_deg": 70,
                "radius_m": 180,
                "clothoid_len": 100,
                "k": 0.00006,
            },
            {"type": "S", "length_m": 1000},
            {
                "type": "C",
                "angle_deg": -110,
                "radius_m": 60,
                "clothoid_len": 35,
                "k": 0.00012,
            },
        ],
    }
    return generate_procedural_track(params, seed=46)


def generate_and_save_tracks():
    """Generate tracks for all disciplines and save to database and PNGs"""
    from PyQt6.QtGui import QPixmap, QPainter
    from GUI.gui_race_visual import (
        CircuitGenerator,
        TrackWidget,
        VehicleAppearanceManager,
    )

    db = DatabaseManager()
    output_dir = Path(__file__).parent.parent / "data" / "track_previews"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define tracks for each discipline
    tracks_to_create = [
        {
            "name": "Momentum Drag Strip",
            "country": "USA",
            "discipline": "DRAG_ACCELERATION",
            "instructions": create_drag_strip_instructions(),
            "is_point_to_point": True,  # Drag strips are point-to-point (no closure)
            "joker_enabled": False,
            "length_km": 0.402,
        },
        {
            "name": "Momentum Rallycross Circuit",
            "country": "Sweden",
            "discipline": "SPRINT_RALLYCROSS",
            "instructions": create_rallycross_instructions(),
            "is_point_to_point": False,
            "joker_enabled": True,
            "length_km": 1.2,
        },
        # Rally stages removed - too long/complex for current system (rallycross covers rally cars)
        {
            "name": "Momentum Grand Prix Circuit",
            "country": "Monaco",
            "discipline": "SINGLE_SEATER",
            "instructions": create_single_seater_circuit_instructions(),
            "is_point_to_point": False,
            "joker_enabled": False,
            "length_km": 4.5,
        },
        {
            "name": "Momentum Touring Circuit",
            "country": "UK",
            "discipline": "PRODUCTION_TOURING",
            "instructions": create_touring_circuit_instructions(),
            "is_point_to_point": False,
            "joker_enabled": False,
            "length_km": 3.8,
        },
        {
            "name": "Momentum Street Circuit",
            "country": "Singapore",
            "discipline": "URBAN_STREET",
            "instructions": create_urban_circuit_instructions(),
            "is_point_to_point": False,
            "joker_enabled": False,
            "length_km": 3.2,
        },
        {
            "name": "Momentum Endurance Circuit",
            "country": "France",
            "discipline": "ENDURANCE",
            "instructions": create_endurance_circuit_instructions(),
            "is_point_to_point": False,
            "joker_enabled": False,
            "length_km": 13.6,
        },
    ]

    with db.get_connection() as conn:
        for track_data in tracks_to_create:
            print(f"\nGenerating {track_data['name']} ({track_data['discipline']})...")

            # Convert instructions to JSON
            instructions_json = json.dumps(track_data["instructions"])

            # Insert track into database
            cursor = conn.execute(
                """
                INSERT INTO tracks (name, country, primary_discipline, is_point_to_point,
                                  joker_enabled, instructions_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    track_data["name"],
                    track_data["country"],
                    track_data["discipline"],
                    1 if track_data["is_point_to_point"] else 0,
                    1 if track_data["joker_enabled"] else 0,
                    instructions_json,
                ),
            )

            track_id = cursor.lastrowid
            print(f"  Created track with ID: {track_id}")

            # Generate visual track points
            options = {"is_point_to_point": track_data["is_point_to_point"]}
            routes = CircuitGenerator.generate_with_routes(
                track_data["instructions"], options
            )
            track_points = routes["main"]

            # Calculate actual track length from points
            if track_points:
                track_length = track_points[-1].s  # s is arc-length in meters
            else:
                track_length = track_data["length_km"] * 1000

            print(
                f"  Generated {len(track_points)} track points, length: {track_length/1000:.3f}km"
            )

            # Create widget and render to PNG
            try:
                appearance = VehicleAppearanceManager()
                widget = TrackWidget(
                    track_points,
                    track_length,
                    appearance,
                    track_surface="asphalt",
                    surface_grip=None,
                )
                widget.resize(widget.minimumSize())

                w = widget.width()
                h = widget.height()

                pix = QPixmap(w, h)
                pix.fill()
                painter = QPainter(pix)
                widget.render(painter)
                painter.end()

                # Save PNG
                filename = f"{track_data['discipline']}_{track_data['name'].replace(' ', '_')}.png"
                output_path = output_dir / filename
                pix.save(str(output_path))
                print(f"  Saved PNG: {output_path}")

            except Exception as e:
                print(f"  ERROR rendering PNG: {e}")
                import traceback

                traceback.print_exc()

        conn.commit()

    print("\n" + "=" * 70)
    print("Track generation complete!")
    print(f"Generated {len(tracks_to_create)} tracks")
    print(f"PNG files saved to: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    print("QApplication created successfully")
    generate_and_save_tracks()
    app.quit()
