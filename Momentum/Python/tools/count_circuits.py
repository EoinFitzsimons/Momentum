import json
p='Momentum/Python/data/circuits_database.json'
with open(p,'r',encoding='utf-8') as f:
    data=json.load(f)
print('circuits_json_count=', len(data))
