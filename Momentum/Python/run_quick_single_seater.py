"""
Quick headless test for Single Seater discipline adapter.
Creates minimal Driver and Track objects, builds RaceContext and runs
`services.simulate_race(context=...)` to verify the SingleSeaterEngine path.
"""

from database.models import Driver, Track
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline
from services.race_simulation_api import simulate_race

# Minimal drivers
drivers = [
    Driver(id=1, name='Alice Example', nationality='GBR', birth_date='1998-05-01', raw_speed=85.0, consistency=80.0),
    Driver(id=2, name='Bob Sample', nationality='FRA', birth_date='1997-03-12', raw_speed=78.0, consistency=78.0)
]

# Minimal track (fill required fields)
track = Track(
    id=1,
    name='Test Circuit',
    country='IRL',
    region='Leinster',
    circuit_type='permanent',
    ima_grade='Gold',
    primary_discipline='formula',
    length_km=5.2,
    turns=12,
    left_turns=6,
    right_turns=6,
    elevation_change_m=12.0,
    max_gradient_percent=5.0,
    min_gradient_percent=-4.0,
    surface='asphalt',
    track_width_avg_m=10.0,
    track_width_min_m=8.0,
    track_width_max_m=12.0,
    avg_speed_kmh=210.0,
    top_speed_kmh=320.0,
    longest_straight_m=1200,
    shortest_straight_m=80,
    tightest_corner_radius_m=45.0,
    climate='temperate',
    avg_temp_summer_c=18.0,
    avg_temp_winter_c=6.0,
    rainfall_mm_annual=800,
    altitude_m=50,
    pit_boxes=20,
    pit_lane_length_m=300.0,
    pit_speed_limit_kmh=60,
    paddock_capacity_teams=40,
    grandstand_capacity=15000,
    drs_zones=1,
    safety_car_probability=0.05,
    night_racing_capable=False,
    wet_weather_racing=True,
    is_active=True,
    debut_year=1998
)

# Build minimal teams dict (empty allowed)
teams = {}

# Create RaceContext
context = RaceContext(
    discipline=RacingDiscipline.SINGLE_SEATER,
    track=track,
    drivers=drivers,
    teams=teams,
    total_laps=3
)

# populate track_conditions expected by SingleSeaterEngine
context.track_conditions['player_driver_id'] = 1
context.track_conditions['player_overrides'] = {'attack': 0.8, 'defend': 0.6}
context.track_conditions['realtime_speed'] = 10.0

# Run simulation for multiple presets to validate tuning
for preset in ['balanced', 'aggressive', 'tyre_sensitive']:
    context.track_conditions['tuning_preset'] = preset
    print(f"\nRunning headless single-seater quick test (3 laps) with preset: {preset}...")
    results = simulate_race(context=context, verbose=True)
    print('Results:')
    for r in results:
        print(r)
