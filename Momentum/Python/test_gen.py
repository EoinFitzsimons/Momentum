from systems.name_generator import generate_racing_driver_name

for i in range(5):
    result = generate_racing_driver_name('GBR', 'MALE')
    print('{0}. {1} - Source: {2}'.format(i+1, result['full_name'], result['source']))
