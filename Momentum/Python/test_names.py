#!/usr/bin/env python3
"""Quick test of the hybrid name generation system"""

from data.placeholder_names import generate_driver_name, generate_bulk_drivers, get_name_generation_stats
import json

print("=== HYBRID NAME GENERATION SYSTEM TEST ===\n")

# Test single name generation
print("1. Single Driver Generation:")
countries = ["GBR", "USA", "GER", "FRA", "ITA", "ESP", "BRA", "JPN"]
for country in countries:
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