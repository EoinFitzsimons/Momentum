"""
Generate tracks for each racing discipline with appropriate parameters.

Creates tracks with correct layouts for:
- DRAG_ACCELERATION (straight quarter-mile)
- SPRINT_RALLYCROSS (short circuit with optional joker lap)
- RALLY_STAGE (point-to-point stage)
- SINGLE_SEATER, PRODUCTION_TOURING, URBAN_STREET, ENDURANCE (circuits)

Outputs PNG visualizations for each track.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.database_manager import DatabaseManager
from database.models import Track
import json
import random


def create_drag_strip_instructions():
    """Drag strip - single straight line, NO TURNS"""
    return [
        {'type': 'S', 'length_m': 402}  # Just a quarter mile straight, nothing else
    ]


def create_rallycross_instructions():
    """Rallycross - compact technical circuit with joker lap"""
    # Tight, technical circuit with 8-10 corners that properly closes
    main_circuit = [
        {'type': 'S', 'length_m': 200},
        {'type': 'C', 'angle_deg': 90, 'radius_m': 35, 'clothoid_len': 25, 'k': 0.00025},
        {'type': 'S', 'length_m': 150},
        {'type': 'C', 'angle_deg': -75, 'radius_m': 40, 'clothoid_len': 28, 'k': 0.0002},
        {'type': 'S', 'length_m': 180},
        {'type': 'C', 'angle_deg': 120, 'radius_m': 30, 'clothoid_len': 22, 'k': 0.0003},
        {'type': 'S', 'length_m': 160},
        {'type': 'C', 'angle_deg': -95, 'radius_m': 38, 'clothoid_len': 26, 'k': 0.00022},
        {'type': 'S', 'length_m': 140},
        {'type': 'C', 'angle_deg': 85, 'radius_m': 42, 'clothoid_len': 29, 'k': 0.00019},
        {'type': 'S', 'length_m': 200},
        {'type': 'C', 'angle_deg': -80, 'radius_m': 45, 'clothoid_len': 30, 'k': 0.00018},
        {'type': 'S', 'length_m': 170},
        {'type': 'C', 'angle_deg': 55, 'radius_m': 50, 'clothoid_len': 32, 'k': 0.00016},
    ]
    
    # Joker lap alternate route
    joker_instructions = [
        {'type': 'S', 'length_m': 100},
        {'type': 'C', 'angle_deg': 60, 'radius_m': 25, 'clothoid_len': 20, 'k': 0.0003},
        {'type': 'S', 'length_m': 80},
        {'type': 'C', 'angle_deg': 60, 'radius_m': 25, 'clothoid_len': 20, 'k': 0.0003},
        {'type': 'S', 'length_m': 100},
    ]
    
    main_circuit.append({'type': 'JOKER', 'instructions': joker_instructions})
    return main_circuit


def create_rally_stage_instructions():
    """Rally stage - long point-to-point with MANY varied corners, NO closure"""
    # 25-30 sections with random turns that DON'T try to balance
    random.seed(42)  # Consistent generation
    instructions = []
    
    for i in range(28):  # Many more sections than circuits
        # Add straight
        straight_length = random.randint(300, 1000)
        instructions.append({'type': 'S', 'length_m': straight_length})
        
        # Add corner - completely random, NO balancing
        angle = random.choice([30, 45, 60, 75, 90, 105, 120, -30, -45, -60, -75, -90, -105, -120])
        radius = random.randint(60, 180)
        clothoid = int(radius * 0.6)
        k = 1.0 / (radius * 10000)
        
        instructions.append({
            'type': 'C',
            'angle_deg': angle,
            'radius_m': radius,
            'clothoid_len': clothoid,
            'k': k
        })
    
    # Final straight
    instructions.append({'type': 'S', 'length_m': random.randint(500, 1500)})
    return instructions


def create_single_seater_circuit_instructions():
    """High-speed single seater circuit - VERY LONG straights, flowing fast corners"""
    # Emphasis: Long straights (800-1400m), large radius corners (120-220m), only 9 corners
    return [
        {'type': 'S', 'length_m': 1400},  # Main straight - massive
        {'type': 'C', 'angle_deg': 35, 'radius_m': 220, 'clothoid_len': 85, 'k': 0.00005},
        {'type': 'S', 'length_m': 900},
        {'type': 'C', 'angle_deg': 70, 'radius_m': 180, 'clothoid_len': 75, 'k': 0.00006},
        {'type': 'S', 'length_m': 600},
        {'type': 'C', 'angle_deg': -45, 'radius_m': 200, 'clothoid_len': 80, 'k': 0.000055},
        {'type': 'S', 'length_m': 800},
        {'type': 'C', 'angle_deg': 110, 'radius_m': 140, 'clothoid_len': 65, 'k': 0.00008},  # Slower corner
        {'type': 'S', 'length_m': 500},
        {'type': 'C', 'angle_deg': 80, 'radius_m': 170, 'clothoid_len': 72, 'k': 0.00007},
        {'type': 'S', 'length_m': 1100},
        {'type': 'C', 'angle_deg': -95, 'radius_m': 150, 'clothoid_len': 68, 'k': 0.00007},
        {'type': 'S', 'length_m': 700},
        {'type': 'C', 'angle_deg': 60, 'radius_m': 190, 'clothoid_len': 78, 'k': 0.00006},
        {'type': 'S', 'length_m': 450},
        {'type': 'C', 'angle_deg': -75, 'radius_m': 160, 'clothoid_len': 70, 'k': 0.00007},
    ]


def create_touring_circuit_instructions():
    """Technical touring car circuit - EXTREME variation: hairpins to fast sweepers"""
    # Emphasis: Mix of tight hairpins (35-45m radius) and fast sweepers (120-140m), 13 corners
    return [
        {'type': 'S', 'length_m': 550},
        {'type': 'C', 'angle_deg': 130, 'radius_m': 38, 'clothoid_len': 30, 'k': 0.0002},  # Tight hairpin
        {'type': 'S', 'length_m': 280},
        {'type': 'C', 'angle_deg': -50, 'radius_m': 135, 'clothoid_len': 65, 'k': 0.00008},  # Fast sweeper
        {'type': 'S', 'length_m': 420},
        {'type': 'C', 'angle_deg': 100, 'radius_m': 55, 'clothoid_len': 40, 'k': 0.00014},  # Medium corner
        {'type': 'S', 'length_m': 190},
        {'type': 'C', 'angle_deg': -145, 'radius_m': 35, 'clothoid_len': 28, 'k': 0.00024},  # Hairpin
        {'type': 'S', 'length_m': 350},
        {'type': 'C', 'angle_deg': 65, 'radius_m': 105, 'clothoid_len': 56, 'k': 0.0001},  
        {'type': 'S', 'length_m': 480},
        {'type': 'C', 'angle_deg': -40, 'radius_m': 140, 'clothoid_len': 68, 'k': 0.00007},  # Fast sweeper
        {'type': 'S', 'length_m': 220},
        {'type': 'C', 'angle_deg': 115, 'radius_m': 48, 'clothoid_len': 36, 'k': 0.00016},  # Tight
        {'type': 'S', 'length_m': 370},
        {'type': 'C', 'angle_deg': -85, 'radius_m': 72, 'clothoid_len': 46, 'k': 0.00012},
        {'type': 'S', 'length_m': 290},
        {'type': 'C', 'angle_deg': 70, 'radius_m': 95, 'clothoid_len': 52, 'k': 0.0001},
        {'type': 'S', 'length_m': 440},
        {'type': 'C', 'angle_deg': -55, 'radius_m': 125, 'clothoid_len': 62, 'k': 0.00008},
    ]


def create_urban_circuit_instructions():
    """Street circuit - ALL 90-degree corners, very short straights, chicanes"""
    # Emphasis: ONLY 90-degree turns, very tight radii (25-35m), short straights (120-350m), 16 corners
    return [
        {'type': 'S', 'length_m': 280},
        {'type': 'C', 'angle_deg': 90, 'radius_m': 28, 'clothoid_len': 22, 'k': 0.0003},
        {'type': 'S', 'length_m': 180},
        {'type': 'C', 'angle_deg': -90, 'radius_m': 30, 'clothoid_len': 23, 'k': 0.00028},
        {'type': 'S', 'length_m': 350},  # Longest straight
        {'type': 'C', 'angle_deg': 90, 'radius_m': 32, 'clothoid_len': 24, 'k': 0.00027},
        {'type': 'S', 'length_m': 220},
        {'type': 'C', 'angle_deg': -90, 'radius_m': 29, 'clothoid_len': 22, 'k': 0.00029},
        {'type': 'S', 'length_m': 160},  # Very short
        {'type': 'C', 'angle_deg': 90, 'radius_m': 26, 'clothoid_len': 21, 'k': 0.00031},
        {'type': 'S', 'length_m': 120},  # Shortest - chicane
        {'type': 'C', 'angle_deg': -90, 'radius_m': 25, 'clothoid_len': 20, 'k': 0.00032},
        {'type': 'S', 'length_m': 310},
        {'type': 'C', 'angle_deg': 90, 'radius_m': 33, 'clothoid_len': 25, 'k': 0.00026},
        {'type': 'S', 'length_m': 240},
        {'type': 'C', 'angle_deg': -90, 'radius_m': 31, 'clothoid_len': 24, 'k': 0.00028},
        {'type': 'S', 'length_m': 190},
        {'type': 'C', 'angle_deg': 90, 'radius_m': 27, 'clothoid_len': 21, 'k': 0.0003},
        {'type': 'S', 'length_m': 270},
        {'type': 'C', 'angle_deg': -90, 'radius_m': 34, 'clothoid_len': 26, 'k': 0.00025},
        {'type': 'S', 'length_m': 200},
        {'type': 'C', 'angle_deg': 90, 'radius_m': 30, 'clothoid_len': 23, 'k': 0.00028},
        {'type': 'S', 'length_m': 150},  # Short
        {'type': 'C', 'angle_deg': -90, 'radius_m': 28, 'clothoid_len': 22, 'k': 0.0003},
    ]


def create_endurance_circuit_instructions():
    """Endurance circuit - MASSIVE straights, huge speed variation, technical infield"""
    # Emphasis: Very long straights (800-2200m!), mix of fast (150-240m radius) and slow corners (40-60m), 14 corners
    return [
        {'type': 'S', 'length_m': 2200},  # Mulsanne-style straight - HUGE
        {'type': 'C', 'angle_deg': 120, 'radius_m': 42, 'clothoid_len': 32, 'k': 0.00018},  # Slow chicane after long straight
        {'type': 'S', 'length_m': 380},
        {'type': 'C', 'angle_deg': -135, 'radius_m': 38, 'clothoid_len': 30, 'k': 0.0002},  # Hairpin
        {'type': 'S', 'length_m': 580},
        {'type': 'C', 'angle_deg': 50, 'radius_m': 160, 'clothoid_len': 72, 'k': 0.00007},  # Fast
        {'type': 'S', 'length_m': 1800},  # Another very long straight
        {'type': 'C', 'angle_deg': -85, 'radius_m': 180, 'clothoid_len': 78, 'k': 0.00006},  # High-speed corner
        {'type': 'S', 'length_m': 1100},
        {'type': 'C', 'angle_deg': 110, 'radius_m': 55, 'clothoid_len': 40, 'k': 0.00014},  # Slow
        {'type': 'S', 'length_m': 420},
        {'type': 'C', 'angle_deg': -95, 'radius_m': 48, 'clothoid_len': 36, 'k': 0.00016},  # Technical section
        {'type': 'S', 'length_m': 310},
        {'type': 'C', 'angle_deg': 75, 'radius_m': 68, 'clothoid_len': 45, 'k': 0.00012},
        {'type': 'S', 'length_m': 800},
        {'type': 'C', 'angle_deg': -60, 'radius_m': 195, 'clothoid_len': 82, 'k': 0.00005},  # Very fast
        {'type': 'S', 'length_m': 1500},
        {'type': 'C', 'angle_deg': 90, 'radius_m': 120, 'clothoid_len': 62, 'k': 0.00009},
        {'type': 'S', 'length_m': 950},
        {'type': 'C', 'angle_deg': -70, 'radius_m': 155, 'clothoid_len': 70, 'k': 0.00007},
    ]


def generate_and_save_tracks():
    """Generate tracks for all disciplines and save to database and PNGs"""
    from PyQt6.QtGui import QPixmap, QPainter
    from GUI.gui_race_visual import CircuitGenerator, TrackWidget, VehicleAppearanceManager
    
    db = DatabaseManager()
    output_dir = Path(__file__).parent.parent / 'tools'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define tracks for each discipline
    tracks_to_create = [
        {
            'name': 'Momentum Drag Strip',
            'country': 'USA',
            'discipline': 'DRAG_ACCELERATION',
            'instructions': create_drag_strip_instructions(),
            'is_point_to_point': True,  # Drag strips are point-to-point (no closure)
            'joker_enabled': False,
            'length_km': 0.402,
        },
        {
            'name': 'Momentum Rallycross Circuit',
            'country': 'Sweden',
            'discipline': 'SPRINT_RALLYCROSS',
            'instructions': create_rallycross_instructions(),
            'is_point_to_point': False,
            'joker_enabled': True,
            'length_km': 1.2,
        },
        {
            'name': 'Momentum Rally Stage',
            'country': 'Finland',
            'discipline': 'RALLY_STAGE',
            'instructions': create_rally_stage_instructions(),
            'is_point_to_point': True,  # Rally stages are point-to-point (no closure)
            'joker_enabled': False,
            'length_km': 8.0,
        },
        {
            'name': 'Momentum Grand Prix Circuit',
            'country': 'Monaco',
            'discipline': 'SINGLE_SEATER',
            'instructions': create_single_seater_circuit_instructions(),
            'is_point_to_point': False,
            'joker_enabled': False,
            'length_km': 4.5,
        },
        {
            'name': 'Momentum Touring Circuit',
            'country': 'UK',
            'discipline': 'PRODUCTION_TOURING',
            'instructions': create_touring_circuit_instructions(),
            'is_point_to_point': False,
            'joker_enabled': False,
            'length_km': 3.8,
        },
        {
            'name': 'Momentum Street Circuit',
            'country': 'Singapore',
            'discipline': 'URBAN_STREET',
            'instructions': create_urban_circuit_instructions(),
            'is_point_to_point': False,
            'joker_enabled': False,
            'length_km': 3.2,
        },
        {
            'name': 'Momentum Endurance Circuit',
            'country': 'France',
            'discipline': 'ENDURANCE',
            'instructions': create_endurance_circuit_instructions(),
            'is_point_to_point': False,
            'joker_enabled': False,
            'length_km': 13.6,
        },
    ]
    
    with db.get_connection() as conn:
        for track_data in tracks_to_create:
            print(f"\nGenerating {track_data['name']} ({track_data['discipline']})...")
            
            # Convert instructions to JSON
            instructions_json = json.dumps(track_data['instructions'])
            
            # Insert track into database
            cursor = conn.execute("""
                INSERT INTO tracks (name, country, primary_discipline, is_point_to_point, 
                                  joker_enabled, instructions_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                track_data['name'],
                track_data['country'],
                track_data['discipline'],
                1 if track_data['is_point_to_point'] else 0,
                1 if track_data['joker_enabled'] else 0,
                instructions_json
            ))
            
            track_id = cursor.lastrowid
            print(f"  Created track with ID: {track_id}")
            
            # Generate visual track points
            options = {
                'is_point_to_point': track_data['is_point_to_point']
            }
            routes = CircuitGenerator.generate_with_routes(track_data['instructions'], options)
            track_points = routes['main']
            
            # Calculate actual track length from points
            if track_points:
                track_length = track_points[-1].s  # s is arc-length in meters
            else:
                track_length = track_data['length_km'] * 1000
            
            print(f"  Generated {len(track_points)} track points, length: {track_length/1000:.3f}km")
            
            # Create widget and render to PNG
            try:
                appearance = VehicleAppearanceManager()
                widget = TrackWidget(
                    track_points, 
                    track_length, 
                    appearance,
                    track_surface='asphalt',
                    surface_grip=None
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
    
    print("\n" + "="*70)
    print("Track generation complete!")
    print(f"Generated {len(tracks_to_create)} tracks")
    print(f"PNG files saved to: {output_dir}")
    print("="*70)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication([])
    print("QApplication created successfully")
    generate_and_save_tracks()
    app.quit()
