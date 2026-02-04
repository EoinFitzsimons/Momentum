"""
Comprehensive Career Mode Database Generator for Momentum

This script generates a complete career mode database with:
- 1,000+ drivers across all 6 disciplines with culturally-appropriate names
- 100+ teams per discipline (600+ total) with realistic team names
- 50+ staff members with appropriate roles and ratings
- All using Faker for authentic name generation

Usage:
    python scripts/seed_career_mode.py --drivers 1500 --teams-per-discipline 150 --staff 100

Features:
- Multi-locale name generation (24+ locales)
- Discipline-specific team naming patterns
- Role-appropriate staff generation
- Realistic attribute distributions
- Budget allocation by discipline tier
- Age and skill correlation modeling
"""

import argparse
import json
import random
import re
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

from faker import Faker

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database_manager import DatabaseManager
from config import DATABASE_PATH, DISCIPLINES, STAFF_ROLES_CONFIG
from tools.locale_mapping import get_all_country_codes, get_locale_for_country


# ============================================================================
# CONFIGURATION
# ============================================================================

# Team naming patterns by discipline
TEAM_NAME_PATTERNS = {
    "SINGLE_SEATER": [
        "{company} Racing",
        "{surname} Motorsport",
        "{company} Grand Prix",
        "Scuderia {surname}",
        "{company} GP",
        "{surname} Racing Team",
        "{adjective} {company} Racing",
        "{company} Performance",
        "{place} Grand Prix",
        "{company} Racing Group",
        "{surname} GP",
        "{company} Formula Team"
    ],
    "PRODUCTION_TOURING": [
        "{company} Motorsport",
        "{surname} Racing",
        "{company} GT Team",
        "{company} Touring",
        "{surname} Competition",
        "Team {company}",
        "{place} Touring",
        "{company} Racing Works",
        "{surname} Touring Team",
        "{company} Cup Team"
    ],
    "URBAN_STREET": [
        "{company} Drift",
        "{surname} Drift Team",
        "{city} Drift",
        "{company} Drift Squad",
        "Drift Team {surname}",
        "{city} Driftworks",
        "{adjective} Drift Crew",
        "{place} Drift",
        "{company} Slide Team",
        "{surname} Driftworks"
    ],
    "DRAG_ACCELERATION": [
        "{company} Drag Racing",
        "{surname} Speed Team",
        "{company} Acceleration",
        "Nitro {surname}",
        "{company} Performance",
        "{surname} Racing",
        "{place} Dragway",
        "{company} Launch Team",
        "{adjective} Drag",
        "{surname} Speedworks"
    ],
    "SPRINT_RALLYCROSS": [
        "{company} Rallycross",
        "{surname} RX Team",
        "{company} Sprint Racing",
        "RX Team {surname}",
        "{company} Motorsport",
        "{surname} Competition",
        "{place} Rallycross",
        "{adjective} RX",
        "{company} Cross Team",
        "{surname} Rallycross"
    ],
    "ENDURANCE": [
        "{company} Endurance",
        "{surname} Racing Team",
        "{company} Motorsport",
        "Team {company} Endurance",
        "{surname} Le Mans Team",
        "{company} Prototype Racing",
        "{place} Endurance",
        "{adjective} Endurance",
        "{company} 24H Team",
        "{surname} Endurance"
    ]
}

# Budget caps by discipline (2025 values in EUR)
BUDGET_CAPS = {
    "SINGLE_SEATER": 130_000_000,
    "PRODUCTION_TOURING": 50_000_000,
    "URBAN_STREET": 35_000_000,
    "DRAG_ACCELERATION": 25_000_000,
    "SPRINT_RALLYCROSS": 30_000_000,
    "ENDURANCE": 60_000_000
}

# Tier distribution percentages
TIER_DISTRIBUTION = {
    "tier1": 0.15,  # Top 15%
    "tier2": 0.30,  # Next 30%
    "tier3": 0.55   # Remaining 55%
}

# Locale mapping is provided by tools.locale_mapping (best-effort per country)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Try to use unidecode for robust transliteration
try:
    from unidecode import unidecode as _unidecode
except ImportError:
    _unidecode = None


def to_latin(s: str) -> str:
    """Convert string to Latin script"""
    if not s:
        return s
    if _unidecode:
        out = _unidecode(s)
    else:
        out = unicodedata.normalize('NFKD', s)
        out = out.encode('ascii', 'ignore').decode('ascii')
    return ' '.join(out.split())


def clean_name(name: str) -> str:
    """Remove honorifics and clean name"""
    # Remove common honorifics
    honorific_prefix = re.compile(r'^(Dr\.?|Mr\.?|Ms\.?|Mrs\.?|Miss\.?|Prof\.?|Sir\.?|Dame\.?|Lady\.?)\s+', re.IGNORECASE)
    honorific_suffix = re.compile(r'\b(MD|M\.D\.|DDS|D\.D\.S\.|PhD|Ph\.D\.|Jr\.|Sr\.|II|III|IV)\b', re.IGNORECASE)
    
    name = honorific_prefix.sub('', name)
    name = honorific_suffix.sub('', name).strip()
    name = to_latin(name)
    
    # Fallback if name is empty or only non-Latin characters
    if not re.search(r'[A-Za-z]', name):
        return None
    
    return name


def random_birth_date(min_age: int = 18, max_age: int = 45) -> str:
    """Generate random birth date for given age range"""
    today = datetime.now().date()
    age = random.randint(min_age, max_age)
    birth = today - timedelta(days=365 * age + random.randint(0, 365))
    return birth.strftime('%Y-%m-%d')


def get_locale_for_nationality(nationality: str) -> str:
    """Get appropriate Faker locale for nationality"""
    return get_locale_for_country(nationality)


def skill_distribution(mean: float = 60.0, std: float = 15.0, min_val: float = 30.0, max_val: float = 95.0) -> float:
    """Generate skill value with normal distribution"""
    value = random.gauss(mean, std)
    return round(max(min_val, min(max_val, value)), 2)


# ============================================================================
# DRIVER GENERATION
# ============================================================================

def generate_driver(fake: Faker, nationality: str, discipline: str, locale: str) -> Optional[dict]:
    """Generate a single driver with all attributes"""
    name = clean_name(fake.name())
    if not name:
        return None
    
    # Age affects skill distribution
    age = random.randint(18, 45)
    
    # Peak performance ages (28-32) have higher mean skills
    if 28 <= age <= 32:
        skill_mean = 65.0
    elif 22 <= age <= 27:
        skill_mean = 62.0
    elif 33 <= age <= 37:
        skill_mean = 63.0
    elif age >= 38:
        skill_mean = 58.0
    else:
        skill_mean = 55.0  # Rookies
    
    birth_date = (datetime.utcnow().date() - timedelta(days=365 * age)).strftime('%Y-%m-%d')
    
    # Generate all skill attributes
    driver_data = {
        'name': name,
        'nationality': nationality,
        'birth_date': birth_date,
        'speed': skill_distribution(skill_mean, 12.0),
        'racecraft': skill_distribution(skill_mean, 12.0),
        'consistency': skill_distribution(skill_mean - 5, 10.0),
        'fitness': skill_distribution(60.0, 10.0),
        'reactions': skill_distribution(skill_mean, 10.0),
        'pressure': skill_distribution(skill_mean - 5, 12.0),
        'setup_knowledge': skill_distribution(skill_mean - 10, 15.0),
        'fuel_management': skill_distribution(55.0, 12.0),
        'tyre_management': skill_distribution(55.0, 12.0),
        'feedback': skill_distribution(55.0, 10.0),
        'adaptability': skill_distribution(55.0, 12.0),
        'preferred_discipline': discipline,
        'learning_rate': round(random.uniform(0.8, 1.5), 2),
        'name_locale': locale,
        'previous_teams': json.dumps([])
    }
    
    return driver_data


def _get_table_columns(conn, table_name: str) -> list:
    """Return column names for a table (lowercase)"""
    return [row["name"] for row in conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()]


def seed_drivers(db: DatabaseManager, count: int, disciplines: list) -> int:
    """Seed database with drivers"""
    print(f"\n=== Generating {count} Drivers ===")
    
    # Use every country code at least once
    country_codes = get_all_country_codes()
    random.shuffle(country_codes)
    
    drivers_created = 0
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        driver_columns = _get_table_columns(conn, "drivers")
        
        for i in range(count):
            # Select discipline and nationality
            discipline = random.choice(disciplines)
            if i < len(country_codes):
                nationality = country_codes[i]
            else:
                nationality = random.choice(country_codes)
            
            locale = get_locale_for_nationality(nationality)
            try:
                fake = Faker(locale)
            except Exception:
                fake = Faker("en_US")
                locale = "en_US"
            
            driver_data = generate_driver(fake, nationality, discipline, locale)
            if not driver_data:
                continue
            
            # Filter to columns that actually exist in the DB schema
            filtered = {k: v for k, v in driver_data.items() if k in driver_columns}
            if not filtered:
                continue
            
            columns = ", ".join(filtered.keys())
            placeholders = ", ".join(["?"] * len(filtered))
            values = list(filtered.values())
            
            try:
                cursor.execute(
                    f"INSERT INTO drivers ({columns}) VALUES ({placeholders})",
                    values
                )
                drivers_created += 1
                
                if (drivers_created % 100) == 0:
                    print(f"  Created {drivers_created} drivers...")
                    
            except Exception as e:
                print(f"  ⚠ Failed to create driver: {e}")
                continue
        
        conn.commit()
    
    print(f"✓ Created {drivers_created} drivers")
    return drivers_created


# ============================================================================
# TEAM GENERATION
# ============================================================================

def generate_team_name(fake: Faker, discipline: str, existing_names: set) -> Optional[str]:
    """Generate unique team name for discipline"""
    patterns = TEAM_NAME_PATTERNS.get(discipline, TEAM_NAME_PATTERNS["SINGLE_SEATER"])
    
    max_attempts = 50
    for _ in range(max_attempts):
        pattern = random.choice(patterns)
        
        # Generate name components
        company = fake.company().split()[0]  # Take first word only
        surname = fake.last_name()
        city = fake.city()
        
        # Clean company name (remove Inc, Ltd, etc.)
        company = re.sub(r'\b(Inc|Ltd|LLC|Corp|Group|Holdings)\b\.?', '', company, flags=re.IGNORECASE).strip()
        company = to_latin(company)
        surname = to_latin(surname)
        city = to_latin(city)
        
        name = pattern.format(company=company, surname=surname, city=city)
        name = clean_name(name)
        
        if name and re.search(r'[A-Za-z]', name) and name not in existing_names:
            return name
    
    return None


def generate_team(fake: Faker, discipline: str, nationality: str, tier: str, existing_names: set) -> Optional[dict]:
    """Generate a single team"""
    name = generate_team_name(fake, discipline, existing_names)
    if not name:
        return None
    
    # Budget based on tier and discipline
    base_budget = BUDGET_CAPS.get(discipline, 50_000_000)
    
    if tier == "tier1":
        budget = base_budget * random.uniform(0.85, 1.0)
        operations_rating = round(random.uniform(75.0, 95.0), 2)
    elif tier == "tier2":
        budget = base_budget * random.uniform(0.60, 0.85)
        operations_rating = round(random.uniform(60.0, 80.0), 2)
    else:  # tier3
        budget = base_budget * random.uniform(0.35, 0.65)
        operations_rating = round(random.uniform(45.0, 70.0), 2)
    
    team_data = {
        'name': name,
        'nationality': nationality,
        'discipline': discipline,
        'tier': tier,
        'budget': round(budget, 2),
        'founded_year': random.randint(1950, 2024),
        'team_principal': clean_name(fake.name()),
        'headquarters': fake.city(),
        'operations_rating': operations_rating,
        'strategy_profile': random.choice(['conservative', 'standard', 'aggressive'])
    }
    
    return team_data


def seed_teams(db: DatabaseManager, teams_per_discipline: int, disciplines: list) -> int:
    """Seed database with teams"""
    print(f"\n=== Generating {teams_per_discipline} Teams per Discipline ===")
    
    try:
        from data.countries import COUNTRIES
        country_codes = list(COUNTRIES.keys())
    except ImportError:
        country_codes = ['USA', 'GBR', 'DEU', 'ITA', 'FRA', 'ESP', 'JPN', 'BRA']
    
    teams_created = 0
    existing_names = set()
    
    # Get existing team names to avoid duplicates
    with db.get_connection() as conn:
        existing = conn.execute("SELECT name FROM teams").fetchall()
        existing_names = {row[0] for row in existing}
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for discipline in disciplines:
            print(f"\n  Creating teams for {discipline}...")
            discipline_teams = 0
            
            for i in range(teams_per_discipline):
                nationality = random.choice(country_codes)
                locale = get_locale_for_nationality(nationality)
                fake = Faker(locale)
                
                # Determine tier based on distribution
                rand = random.random()
                if rand < TIER_DISTRIBUTION['tier1']:
                    tier = 'tier1'
                elif rand < TIER_DISTRIBUTION['tier1'] + TIER_DISTRIBUTION['tier2']:
                    tier = 'tier2'
                else:
                    tier = 'tier3'
                
                team_data = generate_team(fake, discipline, nationality, tier, existing_names)
                
                if not team_data:
                    continue
                
                try:
                    cursor.execute('''
                        INSERT INTO teams (
                            name, nationality, discipline, tier, budget, founded_year,
                            team_principal, headquarters, operations_rating, strategy_profile
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        team_data['name'], team_data['nationality'], team_data['discipline'],
                        team_data['tier'], team_data['budget'], team_data['founded_year'],
                        team_data['team_principal'], team_data['headquarters'],
                        team_data['operations_rating'], team_data['strategy_profile']
                    ))
                    
                    existing_names.add(team_data['name'])
                    teams_created += 1
                    discipline_teams += 1
                    
                except Exception as e:
                    print(f"  ⚠ Failed to create team: {e}")
                    continue
            
            print(f"    ✓ Created {discipline_teams} {discipline} teams")
        
        conn.commit()
    
    print(f"\n✓ Created {teams_created} total teams")
    return teams_created


# ============================================================================
# STAFF GENERATION
# ============================================================================

def generate_staff_member(fake: Faker, role: str) -> Optional[dict]:
    """Generate a single staff member"""
    name = clean_name(fake.name())
    if not name:
        return None
    
    role_config = STAFF_ROLES_CONFIG.get(role, {"rating_range": (50.0, 80.0)})
    min_rating, max_rating = role_config["rating_range"]
    rating = round(random.uniform(min_rating, max_rating), 2)
    
    return {
        'name': name,
        'role': role,
        'rating': rating
    }


def seed_staff(db: DatabaseManager, count: int) -> int:
    """Seed database with staff members"""
    print(f"\n=== Generating {count} Staff Members ===")
    
    # Create weighted role list
    role_pool = []
    for role, config in STAFF_ROLES_CONFIG.items():
        role_pool.extend([role] * config['weight'])
    
    staff_created = 0
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for i in range(count):
            # Random locale for name
            locale = random.choice(LOCALES)
            fake = Faker(locale)
            
            # Select role based on weights
            role = random.choice(role_pool)
            
            staff_data = generate_staff_member(fake, role)
            if not staff_data:
                continue
            
            try:
                cursor.execute('''
                    INSERT INTO staff_members (name, role, rating)
                    VALUES (?, ?, ?)
                ''', (staff_data['name'], staff_data['role'], staff_data['rating']))
                
                staff_created += 1
                
                if (staff_created % 50) == 0:
                    print(f"  Created {staff_created} staff members...")
                    
            except Exception as e:
                print(f"  ⚠ Failed to create staff member: {e}")
                continue
        
        conn.commit()
    
    print(f"✓ Created {staff_created} staff members")
    return staff_created


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate comprehensive career mode database')
    parser.add_argument('--drivers', type=int, default=1500, help='Number of drivers to generate (default: 1500)')
    parser.add_argument('--teams-per-discipline', type=int, default=100, help='Teams per discipline (default: 100)')
    parser.add_argument('--staff', type=int, default=100, help='Number of staff members (default: 100)')
    parser.add_argument('--clear-existing', action='store_true', help='Clear existing data before seeding')
    args = parser.parse_args()
    
    print("=" * 70)
    print("MOMENTUM CAREER MODE DATABASE GENERATOR")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Database: {DATABASE_PATH}")
    print(f"  Drivers: {args.drivers}")
    print(f"  Teams per discipline: {args.teams_per_discipline}")
    print(f"  Staff: {args.staff}")
    print(f"  Total teams: ~{args.teams_per_discipline * 6}")
    print(f"  Clear existing data: {args.clear_existing}")
    
    # Initialize database
    db = DatabaseManager()
    
    # Get discipline list
    disciplines = list(DISCIPLINES.keys())
    
    # Optionally clear existing data
    if args.clear_existing:
        print("\n⚠ Clearing existing data...")
        with db.get_connection() as conn:
            conn.execute("DELETE FROM drivers WHERE id > 0")
            conn.execute("DELETE FROM teams WHERE id > 0")
            conn.execute("DELETE FROM staff_members WHERE id > 0")
            conn.commit()
        print("✓ Existing data cleared")
    
    # Show current stats
    stats = db.get_database_stats()
    print("\nCurrent Database Contents:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    # Generate data
    try:
        drivers_created = seed_drivers(db, args.drivers, disciplines)
        teams_created = seed_teams(db, args.teams_per_discipline, disciplines)
        staff_created = seed_staff(db, args.staff)
        
        # Show final stats
        final_stats = db.get_database_stats()
        print("\n" + "=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print("\nFinal Database Contents:")
        for k, v in final_stats.items():
            print(f"  {k}: {v}")
        
        print(f"\nNew entries created:")
        print(f"  Drivers: {drivers_created}")
        print(f"  Teams: {teams_created}")
        print(f"  Staff: {staff_created}")
        
        # Sample some entries
        print("\n" + "=" * 70)
        print("Sample Entries:")
        print("=" * 70)
        
        with db.get_connection() as conn:
            # Sample drivers
            print("\nSample Drivers:")
            drivers = conn.execute("SELECT name, nationality, speed, racecraft, preferred_discipline FROM drivers ORDER BY RANDOM() LIMIT 5").fetchall()
            for d in drivers:
                print(f"  • {d[0]} ({d[1]}) - Speed: {d[2]:.1f}, Racecraft: {d[3]:.1f} - {d[4]}")
            
            # Sample teams
            print("\nSample Teams:")
            teams = conn.execute("SELECT name, discipline, tier, budget FROM teams ORDER BY RANDOM() LIMIT 5").fetchall()
            for t in teams:
                print(f"  • {t[0]} - {t[1]} ({t[2]}) - Budget: €{t[3]:,.0f}")
            
            # Sample staff
            print("\nSample Staff:")
            staff = conn.execute("SELECT name, role, rating FROM staff_members ORDER BY RANDOM() LIMIT 5").fetchall()
            for s in staff:
                print(f"  • {s[0]} - {s[1]} (Rating: {s[2]:.1f})")
        
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n✓ Career mode database generation complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
