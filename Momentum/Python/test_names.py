"""Test culturally-appropriate name generation"""from systems.name_generator import generate_racing_driver_name"""Test the hybrid name generation system"""#!/usr/bin/env python3

from systems.intelligent_name_generator import IntelligentNameGenerator

import random



gen = IntelligentNameGenerator()# Test generating a few namesfrom systems.name_generator import generate_racing_driver_name"""Quick test of the hybrid name generation system"""



print('Testing culturally-appropriate name generation:\n')for i in range(5):

print(f"{'Country':<8} | {'Name':<35} | Gender")

print("-" * 60)    result = generate_racing_driver_name('GBR', 'MALE')



test_countries = [    print(f"{i+1}. {result['full_name']} - Source: {result['source']}, Confidence: {result['confidence']}")

    'UKR', 'MTQ', 'ECU', 'FIN', 'BRA', 'ESP', 'JPN', 

    'GER', 'ITA', 'RUS', 'CHN', 'AUS', 'MEX', 'FRA',# Test generating a few namesfrom data.placeholder_names import generate_driver_name, generate_bulk_drivers, get_name_generation_stats

    'GBR', 'USA', 'POL', 'CZE', 'NLD', 'SWE'

]print("\n--- Different Countries ---")



for country in test_countries:for country in ['USA', 'GER', 'JPN', 'BRA', 'ITA']:for i in range(5):import json

    gender = random.choice(["M", "F"])

    name_data = gen.generate_unique_name(country, gender, "test")    result = generate_racing_driver_name(country, 'MALE')

    print(f"{country:<8} | {name_data['full_name']:<35} | {gender}")

    print(f"{country}: {result['full_name']} - Source: {result['source']}")    result = generate_racing_driver_name('GBR', 'MALE')

print("\n" + "=" * 60)

stats = gen.get_statistics()

print(f"Total unique names: {stats['total']}")    print(f"{i+1}. {result['full_name']} - Source: {result['source']}, Confidence: {result['confidence']}")print("=== HYBRID NAME GENERATION SYSTEM TEST ===\n")

gen.close()



print("\n--- Different Countries ---")# Test single name generation

for country in ['USA', 'GER', 'JPN', 'BRA', 'ITA']:print("1. Single Driver Generation:")

    result = generate_racing_driver_name(country, 'MALE')countries = ["GBR", "USA", "GER", "FRA", "ITA", "ESP", "BRA", "JPN"]

    print(f"{country}: {result['full_name']} - Source: {result['source']}")for country in countries:

    name = generate_driver_name(country, "MALE")
    print(f"   {country}: {name['full_name']} (Source: {name['source']}, Confidence: {name['confidence']:.1f})")

print("\n2. Bulk Driver Generation (10 drivers):")
bulk_drivers = generate_bulk_drivers(10)
for i, driver in enumerate(bulk_drivers, 1):
    print(f"   {i:2d}. {driver['full_name']:20} ({driver['nationality']}) - {driver['source']}")

print("\n3. System Statistics:")
stats = get_name_generation_stats()
for key, value in stats.items():
    if isinstance(value, float):
        print(f"   {key}: {value:.2%}")
    else:
        print(f"   {key}: {value}")

print("\n✅ Hybrid name generation system is working!")
print("📊 Ready to generate thousands of unique drivers for your simulation!")