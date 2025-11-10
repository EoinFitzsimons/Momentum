#!/usr/bin/env python3
"""Test culturally-appropriate name generation"""

from systems.intelligent_name_generator import IntelligentNameGenerator
import random

def main():
    gen = IntelligentNameGenerator()

    print('Testing culturally-appropriate name generation:')
    print()
    print(f"{'Country':<8} | {'Name':<40} | Gender")
    print("-" * 65)

    test_countries = [
        ('UKR', 'Ukraine'),
        ('MTQ', 'Martinique'), 
        ('ECU', 'Ecuador'),
        ('FIN', 'Finland'),
        ('BRA', 'Brazil'),
        ('ESP', 'Spain'),
        ('JPN', 'Japan'),
        ('GER', 'Germany'),
        ('ITA', 'Italy'),
        ('RUS', 'Russia'),
        ('CHN', 'China'),
        ('AUS', 'Australia'),
        ('MEX', 'Mexico'),
        ('FRA', 'France'),
        ('GBR', 'Great Britain'),
        ('USA', 'United States'),
        ('POL', 'Poland'),
        ('CZE', 'Czech Republic'),
        ('NLD', 'Netherlands'),
        ('SWE', 'Sweden')
    ]

    for code, name in test_countries:
        gender = random.choice(["M", "F"])
        name_data = gen.generate_unique_name(code, gender, "test")
        print(f"{code:<8} | {name_data['full_name']:<40} | {gender}")

    print()
    print("=" * 65)
    stats = gen.get_statistics()
    print(f"Total unique names generated: {stats['total']}")
    gen.close()

if __name__ == "__main__":
    main()
