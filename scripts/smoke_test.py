import sys
sys.path.insert(0, 'Momentum/Python')
from database.database_manager import DatabaseManager
from GUI.gui_race_visual import CircuitGenerator
print('Imported OK')
# Instantiate DB manager (will init DB)
db = DatabaseManager(db_path='momentum_smoke_test.db')
print('DB init OK')
# Call get_track_instructions for an id that probably doesn't exist
print('track_instructions:', db.get_track_instructions(1))
# Call generator with simple dict-style instructions
instr = [
    {'type':'S','length_m':100},
    {'type':'C','radius_m':60,'angle_deg':90,'clothoid_len':20,'k':0.0001},
    {'type':'JOKER','instructions':[{'type':'S','length_m':30},{'type':'C','radius_m':30,'angle_deg':60}]},
    {'type':'PIT','instructions':[{'type':'S','length_m':40}]}
]
routes = CircuitGenerator.generate_with_routes(instr, {'is_point_to_point': True})
print('routes keys:', list(routes.keys()))
print('main len:', len(routes['main']))
print('joker len:', len(routes['joker']) if routes['joker'] else None)
print('pit len:', len(routes['pit']) if routes['pit'] else None)
