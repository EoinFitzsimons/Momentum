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
from datetime import datetime, timedelta, timezone
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

COMPANY_MOTORSPORT = "{company} Motorsport"

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
        "{company} Formula Team",
    ],
    "PRODUCTION_TOURING": [
        COMPANY_MOTORSPORT,
        "{surname} Racing",
        "{company} GT Team",
        "{company} Touring",
        "{surname} Competition",
        "Team {company}",
        "{place} Touring",
        "{company} Racing Works",
        "{surname} Touring Team",
        "{company} Cup Team",
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
        "{surname} Driftworks",
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
        "{surname} Speedworks",
    ],
    "SPRINT_RALLYCROSS": [
        "{company} Rallycross",
        "{surname} RX Team",
        "{company} Sprint Racing",
        "RX Team {surname}",
        COMPANY_MOTORSPORT,
        "{surname} Competition",
        "{place} Rallycross",
        "{adjective} RX",
        "{company} Cross Team",
        "{surname} Rallycross",
    ],
    "ENDURANCE": [
        "{company} Endurance",
        "{surname} Racing Team",
        COMPANY_MOTORSPORT,
        "Team {company} Endurance",
        "{surname} Le Mans Team",
        "{company} Prototype Racing",
        "{place} Endurance",
        "{adjective} Endurance",
        "{company} 24H Team",
        "{surname} Endurance",
    ],
}

# Budget caps by discipline (2025 values in EUR)
BUDGET_CAPS = {
    "SINGLE_SEATER": 130_000_000,
    "PRODUCTION_TOURING": 50_000_000,
    "URBAN_STREET": 35_000_000,
    "DRAG_ACCELERATION": 25_000_000,
    "SPRINT_RALLYCROSS": 30_000_000,
    "ENDURANCE": 60_000_000,
}

# Tier distribution percentages
TIER_DISTRIBUTION = {
    "tier1": 0.15,  # Top 15%
    "tier2": 0.30,  # Next 30%
    "tier3": 0.55,  # Remaining 55%
}

# Common Faker locales for staff name generation
COMMON_LOCALES = [
    "en_US",
    "en_GB",
    "de_DE",
    "fr_FR",
    "it_IT",
    "es_ES",
    "pt_BR",
    "ja_JP",
    "zh_CN",
    "ru_RU",
    "ko_KR",
    "nl_NL",
]

HONORIFIC_PREFIXES = {"dr", "mr", "ms", "mrs", "miss", "prof", "sir", "dame", "lady"}

HONORIFIC_SUFFIXES = {"md", "dds", "phd", "jr", "sr", "ii", "iii", "iv"}

DRIVER_SLOTS_PER_DISCIPLINE = {
    "SINGLE_SEATER": 2,
    "PRODUCTION_TOURING": 2,
    "URBAN_STREET": 2,
    "DRAG_ACCELERATION": 2,
    "SPRINT_RALLYCROSS": 2,
    "ENDURANCE": 4,
}

STAFF_SLOTS_PER_TEAM = 3
MIN_STAFF_PER_TEAM = 1

# Locale mapping is provided by tools.locale_mapping (best-effort per country)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def _load_unidecode():
    """Best-effort dynamic import of unidecode to avoid hard dependency."""
    try:
        module = __import__("unidecode")
        return getattr(module, "unidecode", None)
    except Exception:
        return None


_unidecode = _load_unidecode()


def to_latin(s: str) -> str:
    """Convert string to Latin script"""
    if not s:
        return s
    if _unidecode:
        out = _unidecode(s)
    else:
        out = unicodedata.normalize("NFKD", s)
        out = out.encode("ascii", "ignore").decode("ascii")
    return " ".join(out.split())


def clean_name(name: str) -> str:
    """Remove honorifics and clean name"""
    if not name:
        return ""
    tokens = [t for t in name.strip().split() if t]
    if not tokens:
        return ""

    while tokens and tokens[0].lower().rstrip(".") in HONORIFIC_PREFIXES:
        tokens.pop(0)
    while tokens and tokens[-1].lower().rstrip(".") in HONORIFIC_SUFFIXES:
        tokens.pop()

    cleaned = to_latin(" ".join(tokens)).strip()
    if not re.search(r"[A-Za-z]", cleaned):
        return ""
    return cleaned


def random_birth_date(min_age: int = 18, max_age: int = 45) -> str:
    """Generate random birth date for given age range"""
    today = datetime.now().date()
    age = random.randint(min_age, max_age)
    birth = today - timedelta(days=365 * age + random.randint(0, 365))
    return birth.strftime("%Y-%m-%d")


def get_locale_for_nationality(nationality: str) -> str:
    """Get appropriate Faker locale for nationality"""
    return get_locale_for_country(nationality)


def _build_fake_for_nationality(nationality: str) -> Faker:
    """Create Faker instance for nationality locale with safe fallback."""
    locale = get_locale_for_nationality(nationality)
    try:
        return Faker(locale)
    except Exception:
        return Faker("en_US")


def _pick_tier_from_distribution() -> str:
    """Sample a team tier using configured distribution weights."""
    rand = random.random()
    if rand < TIER_DISTRIBUTION["tier1"]:
        return "tier1"
    if rand < TIER_DISTRIBUTION["tier1"] + TIER_DISTRIBUTION["tier2"]:
        return "tier2"
    return "tier3"


def _tier_age_skill_profile(tier: str) -> Tuple[int, float, float]:
    """Return (age, skill_mean, skill_std) profile by normalized team tier."""
    t = (tier or "").lower()
    if t in ("tier1", "tier_1", "1"):
        age = (
            random.randint(28, 45) if random.random() < 0.80 else random.randint(22, 27)
        )
        return age, 78.0, 10.0
    if t in ("tier2", "tier_2", "2"):
        age = random.choice([random.randint(22, 30)] * 6 + [random.randint(30, 38)] * 4)
        return age, 62.0, 12.0
    age = random.randint(18, 32) if random.random() < 0.85 else random.randint(35, 45)
    return age, 55.0, 13.0


def skill_distribution(
    mean: float = 60.0, std: float = 15.0, min_val: float = 30.0, max_val: float = 95.0
) -> float:
    """Generate skill value with normal distribution"""
    value = random.gauss(mean, std)
    return round(max(min_val, min(max_val, value)), 2)


# ============================================================================
# DRIVER GENERATION
# ============================================================================


def generate_driver(
    fake: Faker, nationality: str, discipline: str, locale: str
) -> Optional[dict]:
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

    birth_date = (
        datetime.now(timezone.utc).date() - timedelta(days=365 * age)
    ).strftime("%Y-%m-%d")

    # Generate all skill attributes
    driver_data = {
        "name": name,
        "nationality": nationality,
        "birth_date": birth_date,
        "speed": skill_distribution(skill_mean, 12.0),
        "racecraft": skill_distribution(skill_mean, 12.0),
        "consistency": skill_distribution(skill_mean - 5, 10.0),
        "fitness": skill_distribution(60.0, 10.0),
        "reactions": skill_distribution(skill_mean, 10.0),
        "pressure": skill_distribution(skill_mean - 5, 12.0),
        "setup_knowledge": skill_distribution(skill_mean - 10, 15.0),
        "fuel_management": skill_distribution(55.0, 12.0),
        "tyre_management": skill_distribution(55.0, 12.0),
        "feedback": skill_distribution(55.0, 10.0),
        "adaptability": skill_distribution(55.0, 12.0),
        "preferred_discipline": discipline,
        "learning_rate": round(random.uniform(0.8, 1.5), 2),
        "name_locale": locale,
        "previous_teams": json.dumps([]),
    }

    return driver_data


def _get_table_columns(conn, table_name: str) -> list:
    """Return column names for a table (lowercase)"""
    return [
        row["name"]
        for row in conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    ]


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
                    f"INSERT INTO drivers ({columns}) VALUES ({placeholders})", values
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


def generate_team_name(
    fake: Faker, discipline: str, existing_names: set
) -> Optional[str]:
    """Generate unique team name for discipline"""
    patterns = TEAM_NAME_PATTERNS.get(discipline, TEAM_NAME_PATTERNS["SINGLE_SEATER"])

    max_attempts = 50
    for _ in range(max_attempts):
        pattern = random.choice(patterns)

        # Generate name components
        company = fake.company().split()[0]  # Take first word only
        surname = fake.last_name()
        city = fake.city()
        place = fake.city()
        adjective = random.choice(
            ["Velocity", "Titan", "Apex", "Rapid", "Vanguard", "Prime", "Vertex"]
        )

        # Clean company name (remove Inc, Ltd, etc.)
        company = re.sub(
            r"\b(Inc|Ltd|LLC|Corp|Group|Holdings)\b\.?",
            "",
            company,
            flags=re.IGNORECASE,
        ).strip()
        company = to_latin(company).strip()
        surname = to_latin(surname).strip()
        city = to_latin(city).strip()
        place = to_latin(place).strip()
        adjective = to_latin(adjective).strip()

        # Reject if any critical component became empty (non-Latin locale artifact)
        if not company or not surname or not city or not place:
            continue

        values = {
            "company": company,
            "surname": surname,
            "city": city,
            "place": place,
            "adjective": adjective,
        }
        name = pattern.format_map(values)
        name = clean_name(name)

        # Verify name has content and is unique
        if (
            name
            and len(name) > 3
            and re.search(r"[A-Za-z]", name)
            and name not in existing_names
        ):
            return name

    return None


def _get_country_codes_for_team_seed() -> list:
    """Return all country codes used for team nationality sampling."""
    try:
        from data.countries import COUNTRIES

        return list(COUNTRIES.keys())
    except ImportError:
        return ["USA", "GBR", "DEU", "ITA", "FRA", "ESP", "JPN", "BRA"]


def _safe_locales_for_team_names() -> list:
    """Locales that reliably produce Latin-script company/place strings."""
    return [
        "en_US",
        "en_GB",
        "de_DE",
        "fr_FR",
        "it_IT",
        "es_ES",
        "pt_BR",
        "nl_NL",
        "sv_SE",
        "da_DK",
        "en_AU",
        "en_CA",
    ]


def _calculate_team_budget_and_ops(discipline: str, tier: str) -> Tuple[float, float]:
    """Return generated (budget, operations_rating) for team tier/discipline."""
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
    return round(budget, 2), operations_rating


def _build_seed_team_data(
    discipline: str,
    country_codes: list,
    safe_locales_for_names: list,
    existing_names: set,
) -> Optional[dict]:
    """Generate one team payload suitable for insertion, or None if invalid."""
    nationality = random.choice(country_codes)

    safe_locale = random.choice(safe_locales_for_names)
    fake_for_names = Faker(safe_locale)
    fake_for_principal = _build_fake_for_nationality(nationality)

    tier = _pick_tier_from_distribution()
    team_name = generate_team_name(fake_for_names, discipline, existing_names)
    if not team_name:
        return None

    budget, operations_rating = _calculate_team_budget_and_ops(discipline, tier)

    team_data = {
        "name": team_name,
        "nationality": nationality,
        "discipline": discipline,
        "tier": tier,
        "budget": budget,
        "founded_year": random.randint(1950, 2024),
        "team_principal": clean_name(fake_for_principal.name()),
        "headquarters": fake_for_principal.city(),
        "operations_rating": operations_rating,
        "strategy_profile": random.choice(["conservative", "standard", "aggressive"]),
    }

    if not team_data["team_principal"]:
        return None

    return team_data


def _insert_seed_team(cursor, team_data: dict) -> None:
    """Insert a generated team payload into teams table."""
    cursor.execute(
        """
        INSERT INTO teams (
            name, nationality, discipline, tier, budget, founded_year,
            team_principal, headquarters, operations_rating, strategy_profile
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            team_data["name"],
            team_data["nationality"],
            team_data["discipline"],
            team_data["tier"],
            team_data["budget"],
            team_data["founded_year"],
            team_data["team_principal"],
            team_data["headquarters"],
            team_data["operations_rating"],
            team_data["strategy_profile"],
        ),
    )


def seed_teams(
    db: DatabaseManager, teams_per_discipline: int, disciplines: list
) -> int:
    """Seed database with teams"""
    print(f"\n=== Generating {teams_per_discipline} Teams per Discipline ===")

    country_codes = _get_country_codes_for_team_seed()
    safe_locales_for_names = _safe_locales_for_team_names()

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

            for _ in range(teams_per_discipline):
                team_data = _build_seed_team_data(
                    discipline,
                    country_codes,
                    safe_locales_for_names,
                    existing_names,
                )
                if not team_data:
                    continue

                try:
                    _insert_seed_team(cursor, team_data)

                    existing_names.add(team_data["name"])
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

    return {"name": name, "role": role, "rating": rating}


def seed_staff(db: DatabaseManager, count: int) -> int:
    """Seed database with staff members"""
    print(f"\n=== Generating {count} Staff Members ===")

    # Create weighted role list
    role_pool = []
    for role, config in STAFF_ROLES_CONFIG.items():
        role_pool.extend([role] * config["weight"])

    staff_created = 0

    with db.get_connection() as conn:
        cursor = conn.cursor()

        for _ in range(count):
            # Random locale for name
            locale = random.choice(COMMON_LOCALES)
            try:
                fake = Faker(locale)
            except Exception:
                fake = Faker("en_US")

            # Select role based on weights
            role = random.choice(role_pool)

            staff_data = generate_staff_member(fake, role)
            if not staff_data:
                continue

            try:
                cursor.execute(
                    """
                    INSERT INTO staff_members (name, role, rating)
                    VALUES (?, ?, ?)
                """,
                    (staff_data["name"], staff_data["role"], staff_data["rating"]),
                )

                staff_created += 1

                if (staff_created % 50) == 0:
                    print(f"  Created {staff_created} staff members...")

            except Exception as e:
                print(f"  ⚠ Failed to create staff member: {e}")
                continue

        conn.commit()

    print(f"✓ Created {staff_created} staff members")
    return staff_created


def assign_staff_contracts(db: DatabaseManager, disciplines: list) -> int:  # NOSONAR
    """Assign available staff to teams and guarantee minimum staffing coverage."""
    print("\n=== Assigning Staff Contracts to Teams ===")
    assignments = 0
    generated_staff = 0

    with db.get_connection() as conn:
        cursor = conn.cursor()

        team_ids: list[int] = []
        for discipline in disciplines:
            rows = cursor.execute(
                """
                SELECT id
                FROM teams
                WHERE discipline = ?
                ORDER BY operations_rating DESC, id ASC
                """,
                (discipline,),
            ).fetchall()
            team_ids.extend(int(row[0]) for row in rows)

        if not team_ids:
            print("  ! No teams found for staff assignment")
            return 0

        staff_counts = {
            int(row[0]): int(row[1])
            for row in cursor.execute(
                """
                SELECT t.id, COUNT(s.id) AS staff_count
                FROM teams t
                LEFT JOIN staff_members s ON s.current_team_id = t.id
                WHERE t.discipline IN ({})
                GROUP BY t.id
                """.format(
                    ",".join(["?"] * len(disciplines))
                ),
                tuple(disciplines),
            ).fetchall()
        }

        team_ids_needing_minimum = [
            team_id
            for team_id in team_ids
            if staff_counts.get(team_id, 0) < MIN_STAFF_PER_TEAM
        ]

        staff_rows = cursor.execute(
            """
            SELECT id, rating
            FROM staff_members
            WHERE current_team_id IS NULL
            ORDER BY rating DESC, id ASC
            """
        ).fetchall()

        role_pool = []
        for role, config in STAFF_ROLES_CONFIG.items():
            role_pool.extend([role] * int(config.get("weight", 1)))
        if not role_pool:
            role_pool = ["MECHANIC"]

        missing_minimum = max(0, len(team_ids_needing_minimum) - len(staff_rows))
        if missing_minimum > 0:
            print(
                f"  ! Creating {missing_minimum} extra staff to satisfy minimum team coverage"
            )
            created_for_minimum = 0
            attempts = 0
            max_attempts = max(10, missing_minimum * 8)

            while created_for_minimum < missing_minimum and attempts < max_attempts:
                attempts += 1
                locale = random.choice(COMMON_LOCALES)
                try:
                    fake = Faker(locale)
                except Exception:
                    fake = Faker("en_US")
                role = random.choice(role_pool)
                staff_data = generate_staff_member(fake, role)
                if not staff_data:
                    role_cfg = STAFF_ROLES_CONFIG.get(
                        role, {"rating_range": (50.0, 80.0)}
                    )
                    min_rating, max_rating = role_cfg["rating_range"]
                    staff_data = {
                        "name": f"Generated Staff {random.randint(100000, 999999)}",
                        "role": role,
                        "rating": round(random.uniform(min_rating, max_rating), 2),
                    }
                cursor.execute(
                    """
                    INSERT INTO staff_members (name, role, rating)
                    VALUES (?, ?, ?)
                    """,
                    (staff_data["name"], staff_data["role"], staff_data["rating"]),
                )
                generated_staff += 1
                created_for_minimum += 1

            if created_for_minimum < missing_minimum:
                print(
                    "  ! Warning: could not generate enough minimum-coverage staff "
                    f"({created_for_minimum}/{missing_minimum})"
                )

            staff_rows = cursor.execute(
                """
                SELECT id, rating
                FROM staff_members
                WHERE current_team_id IS NULL
                ORDER BY rating DESC, id ASC
                """
            ).fetchall()

        if not staff_rows:
            print("  ! No unassigned staff available to contract")
            return 0

        mandatory_targets = list(team_ids_needing_minimum)
        pair_count = min(len(staff_rows), len(mandatory_targets))
        start_season = datetime.now().year

        for idx in range(pair_count):
            team_id = mandatory_targets[idx]
            staff_id = int(staff_rows[idx][0])
            rating = float(staff_rows[idx][1] or 50.0)
            annual_salary = round(45_000 + (rating * 2_750), 2)
            contract_length = random.randint(1, 3)

            cursor.execute(
                """
                UPDATE staff_members
                SET current_team_id = ?,
                    annual_salary = ?,
                    contract_length = ?,
                    contract_start_season = ?,
                    contract_end_season = ?
                WHERE id = ?
                """,
                (
                    team_id,
                    annual_salary,
                    contract_length,
                    start_season,
                    start_season + contract_length - 1,
                    staff_id,
                ),
            )
            assignments += 1
            staff_counts[team_id] = staff_counts.get(team_id, 0) + 1

        remaining_staff = staff_rows[pair_count:]

        extra_targets = []
        for _ in range(STAFF_SLOTS_PER_TEAM):
            for team_id in team_ids:
                if staff_counts.get(team_id, 0) < STAFF_SLOTS_PER_TEAM:
                    extra_targets.append(team_id)

        extra_pair_count = min(len(remaining_staff), len(extra_targets))
        for idx in range(extra_pair_count):
            team_id = extra_targets[idx]
            staff_id = int(remaining_staff[idx][0])
            rating = float(remaining_staff[idx][1] or 50.0)
            annual_salary = round(45_000 + (rating * 2_750), 2)
            contract_length = random.randint(1, 3)

            cursor.execute(
                """
                UPDATE staff_members
                SET current_team_id = ?,
                    annual_salary = ?,
                    contract_length = ?,
                    contract_start_season = ?,
                    contract_end_season = ?
                WHERE id = ?
                """,
                (
                    team_id,
                    annual_salary,
                    contract_length,
                    start_season,
                    start_season + contract_length - 1,
                    staff_id,
                ),
            )
            assignments += 1
            staff_counts[team_id] = staff_counts.get(team_id, 0) + 1

        conn.commit()

        teams_without_staff = sum(
            1 for team_id in team_ids if staff_counts.get(team_id, 0) <= 0
        )

    print(
        f"✓ Total staff contracts assigned: {assignments} "
        f"(generated {generated_staff} extra staff, target {STAFF_SLOTS_PER_TEAM} per team where possible, "
        f"teams with zero staff after assignment: {teams_without_staff})"
    )
    return assignments


def assign_driver_contracts(db: DatabaseManager, disciplines: list) -> int:
    """Assign drivers to teams by discipline to create playable rosters."""
    print("\n=== Assigning Driver Contracts to Teams ===")
    assignments = 0

    with db.get_connection() as conn:
        cursor = conn.cursor()

        for discipline in disciplines:
            slots = DRIVER_SLOTS_PER_DISCIPLINE.get(discipline, 2)

            team_rows = cursor.execute(
                """
                SELECT id
                FROM teams
                WHERE discipline = ?
                ORDER BY operations_rating DESC, id ASC
                """,
                (discipline,),
            ).fetchall()
            team_ids = [row[0] for row in team_rows]
            if not team_ids:
                continue

            driver_rows = cursor.execute(
                """
                SELECT id
                FROM drivers
                WHERE current_team_id IS NULL
                  AND preferred_discipline = ?
                ORDER BY speed DESC, racecraft DESC, consistency DESC, id ASC
                """,
                (discipline,),
            ).fetchall()
            driver_ids = [row[0] for row in driver_rows]

            if not driver_ids:
                continue

            # Fill rosters in round-robin slot order (slot 1 for all teams,
            # then slot 2, etc.) so limited driver pools still spread fairly.
            team_slot_targets = [
                (team_id, slot) for slot in range(slots) for team_id in team_ids
            ]
            pair_count = min(len(driver_ids), len(team_slot_targets))

            for idx in range(pair_count):
                team_id = team_slot_targets[idx][0]
                driver_id = driver_ids[idx]
                contract_length = random.randint(1, 3)
                salary = round(random.uniform(600_000, 4_000_000), 2)
                cursor.execute(
                    """
                    UPDATE drivers
                    SET current_team_id = ?,
                        contract_length = ?,
                        salary = ?
                    WHERE id = ?
                    """,
                    (team_id, contract_length, salary, driver_id),
                )
                assignments += 1

            print(
                f"  ✓ {discipline}: assigned {pair_count} drivers across "
                f"{len(team_ids)} teams ({slots} slots/team target)"
            )

        conn.commit()

    print(f"✓ Total driver contracts assigned: {assignments}")
    return assignments


def adjust_drivers_by_tier(db: DatabaseManager) -> int:
    """Adjust driver attributes and ages based on their team's tier.

    Tier weighting:
    - TIER_1: High skill (70-95+), experienced drivers (28-45 mostly)
    - TIER_2: Mid skill (55-80), mixed ages (20-40)
    - TIER_3: Lower skill (40-70 mostly), young drivers (18-32) with occasional veterans
    """
    print("\n=== Adjusting Driver Attributes by Team Tier ===")

    adjusted_count = 0
    tier_adjustments = {}

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Get all drivers who are assigned to teams (current_team_id IS NOT NULL)
        driver_rows = cursor.execute(
            """
            SELECT d.id, d.birth_date, d.speed, d.racecraft, d.consistency,
                   d.fitness, d.reactions, d.pressure, d.setup_knowledge,
                   d.fuel_management, d.tyre_management, d.feedback, d.adaptability,
                   t.tier
            FROM drivers d
            JOIN teams t ON d.current_team_id = t.id
            ORDER BY t.tier, d.id
        """
        ).fetchall()

        for row in driver_rows:
            driver_id = row[0]
            birth_date_str = row[1]
            tier = row[13]

            if tier not in tier_adjustments:
                tier_adjustments[tier] = 0

            try:
                datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except Exception:
                pass

            new_age, skill_mean, skill_std = _tier_age_skill_profile(tier)

            # Calculate new birth date from age
            new_birth_date = (
                datetime.now(timezone.utc).date() - timedelta(days=365 * new_age)
            ).strftime("%Y-%m-%d")

            # Generate tier-appropriate skill attributes
            speed = skill_distribution(skill_mean, skill_std)
            racecraft = skill_distribution(skill_mean - 3, skill_std)
            consistency = skill_distribution(skill_mean - 5, skill_std)
            fitness = skill_distribution(
                60.0, 10.0
            )  # Relatively consistent across tiers
            reactions = skill_distribution(skill_mean, skill_std)
            pressure = skill_distribution(skill_mean - 5, skill_std)
            setup_knowledge = skill_distribution(skill_mean - 10, skill_std)
            fuel_management = skill_distribution(55.0, 12.0)  # Less tier-dependent
            tyre_management = skill_distribution(55.0, 12.0)  # Less tier-dependent
            feedback = skill_distribution(55.0, 10.0)
            adaptability = skill_distribution(55.0, 12.0)

            # Update driver with new attributes
            cursor.execute(
                """
                UPDATE drivers
                SET birth_date = ?,
                    speed = ?,
                    racecraft = ?,
                    consistency = ?,
                    fitness = ?,
                    reactions = ?,
                    pressure = ?,
                    setup_knowledge = ?,
                    fuel_management = ?,
                    tyre_management = ?,
                    feedback = ?,
                    adaptability = ?
                WHERE id = ?
            """,
                (
                    new_birth_date,
                    speed,
                    racecraft,
                    consistency,
                    fitness,
                    reactions,
                    pressure,
                    setup_knowledge,
                    fuel_management,
                    tyre_management,
                    feedback,
                    adaptability,
                    driver_id,
                ),
            )

            adjusted_count += 1
            tier_adjustments[tier] += 1

        conn.commit()

    # Print summary
    for tier in sorted(tier_adjustments.keys()):
        count = tier_adjustments[tier]
        tier_label = tier.replace("_", " ").title()
        print(f"  ✓ {tier_label}: Adjusted {count} drivers")

    print(f"✓ Total drivers adjusted: {adjusted_count}")
    return adjusted_count


def refresh_unsupported_disciplines(db: DatabaseManager, disciplines: list) -> dict:
    """Purge records for disciplines no longer supported by config."""
    print("\n=== Refreshing Unsupported Disciplines ===")
    supported = set(disciplines)
    placeholders = ",".join(["?"] * len(supported))

    result = {
        "teams_deleted": 0,
        "tracks_deleted": 0,
        "championships_deleted": 0,
        "races_deleted": 0,
        "race_results_deleted": 0,
        "drivers_detached": 0,
        "staff_detached": 0,
    }

    with db.get_connection() as conn:
        cursor = conn.cursor()

        unsupported_team_ids = [
            row[0]
            for row in cursor.execute(
                f"SELECT id FROM teams WHERE discipline NOT IN ({placeholders})",
                tuple(supported),
            ).fetchall()
        ]

        unsupported_champ_ids = [
            row[0]
            for row in cursor.execute(
                f"SELECT id FROM championships WHERE discipline NOT IN ({placeholders})",
                tuple(supported),
            ).fetchall()
        ]

        if unsupported_team_ids:
            team_q = ",".join(["?"] * len(unsupported_team_ids))

            result["drivers_detached"] = cursor.execute(
                f"UPDATE drivers SET current_team_id = NULL WHERE current_team_id IN ({team_q})",
                tuple(unsupported_team_ids),
            ).rowcount
            result["staff_detached"] = cursor.execute(
                f"UPDATE staff_members SET current_team_id = NULL WHERE current_team_id IN ({team_q})",
                tuple(unsupported_team_ids),
            ).rowcount

            result["race_results_deleted"] += cursor.execute(
                f"DELETE FROM race_results WHERE team_id IN ({team_q})",
                tuple(unsupported_team_ids),
            ).rowcount

            for table_name in [
                "team_ownership",
                "team_budget_transactions",
                "team_facility_upgrades",
                "team_audit_log",
            ]:
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE team_id IN ({team_q})",
                    tuple(unsupported_team_ids),
                )

            result["teams_deleted"] = cursor.execute(
                f"DELETE FROM teams WHERE id IN ({team_q})",
                tuple(unsupported_team_ids),
            ).rowcount

        if unsupported_champ_ids:
            champ_q = ",".join(["?"] * len(unsupported_champ_ids))
            race_ids = [
                row[0]
                for row in cursor.execute(
                    f"SELECT id FROM races WHERE championship_id IN ({champ_q})",
                    tuple(unsupported_champ_ids),
                ).fetchall()
            ]

            if race_ids:
                race_q = ",".join(["?"] * len(race_ids))
                result["race_results_deleted"] += cursor.execute(
                    f"DELETE FROM race_results WHERE race_id IN ({race_q})",
                    tuple(race_ids),
                ).rowcount
                result["races_deleted"] = cursor.execute(
                    f"DELETE FROM races WHERE id IN ({race_q})",
                    tuple(race_ids),
                ).rowcount

            result["championships_deleted"] = cursor.execute(
                f"DELETE FROM championships WHERE id IN ({champ_q})",
                tuple(unsupported_champ_ids),
            ).rowcount

        result["tracks_deleted"] = cursor.execute(
            f"""
            DELETE FROM tracks
            WHERE primary_discipline NOT IN ({placeholders})
              AND id NOT IN (SELECT DISTINCT track_id FROM races)
            """,
            tuple(supported),
        ).rowcount

        conn.commit()

    print(
        f"✓ Refresh complete: teams={result['teams_deleted']}, "
        f"tracks={result['tracks_deleted']}, championships={result['championships_deleted']}"
    )
    return result


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive career mode database"
    )
    parser.add_argument(
        "--drivers",
        type=int,
        default=1500,
        help="Number of drivers to generate (default: 1500)",
    )
    parser.add_argument(
        "--teams-per-discipline",
        type=int,
        default=100,
        help="Teams per discipline (default: 100)",
    )
    parser.add_argument(
        "--staff", type=int, default=100, help="Number of staff members (default: 100)"
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing data before seeding",
    )
    parser.add_argument(
        "--hard-refresh",
        action="store_true",
        help="Purge unsupported discipline records before seeding",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("MOMENTUM CAREER MODE DATABASE GENERATOR")
    print("=" * 70)
    print("\nConfiguration:")
    print(f"  Database: {DATABASE_PATH}")
    print(f"  Drivers: {args.drivers}")
    print(f"  Teams per discipline: {args.teams_per_discipline}")
    print(f"  Staff: {args.staff}")
    print(f"  Total teams: ~{args.teams_per_discipline * 6}")
    print(f"  Clear existing data: {args.clear_existing}")
    print(f"  Hard refresh unsupported disciplines: {args.hard_refresh}")

    # Initialize database
    db = DatabaseManager()

    # Get discipline list
    disciplines = list(DISCIPLINES.keys())

    # Optional purge of legacy/unsupported disciplines
    if args.hard_refresh:
        refresh_unsupported_disciplines(db, disciplines)

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
        staff_contracts_assigned = assign_staff_contracts(db, disciplines)
        contracts_assigned = assign_driver_contracts(db, disciplines)
        drivers_adjusted = adjust_drivers_by_tier(db)

        # Show final stats
        final_stats = db.get_database_stats()
        print("\n" + "=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print("\nFinal Database Contents:")
        for k, v in final_stats.items():
            print(f"  {k}: {v}")

        print("\nNew entries created:")
        print(f"  Drivers: {drivers_created}")
        print(f"  Teams: {teams_created}")
        print(f"  Staff: {staff_created}")
        print(f"  Staff contracts: {staff_contracts_assigned}")
        print(f"  Driver contracts: {contracts_assigned}")
        print(f"  Drivers adjusted by tier: {drivers_adjusted}")

        # Sample some entries
        print("\n" + "=" * 70)
        print("Sample Entries:")
        print("=" * 70)

        with db.get_connection() as conn:
            # Sample drivers
            print("\nSample Drivers:")
            drivers = conn.execute(
                "SELECT name, nationality, speed, racecraft, preferred_discipline FROM drivers ORDER BY RANDOM() LIMIT 5"
            ).fetchall()
            for d in drivers:
                print(
                    f"  • {d[0]} ({d[1]}) - Speed: {d[2]:.1f}, Racecraft: {d[3]:.1f} - {d[4]}"
                )

            # Sample teams
            print("\nSample Teams:")
            teams = conn.execute(
                "SELECT name, discipline, tier, budget FROM teams ORDER BY RANDOM() LIMIT 5"
            ).fetchall()
            for t in teams:
                print(f"  • {t[0]} - {t[1]} ({t[2]}) - Budget: €{t[3]:,.0f}")

            # Sample staff
            print("\nSample Staff:")
            staff = conn.execute(
                "SELECT name, role, rating FROM staff_members ORDER BY RANDOM() LIMIT 5"
            ).fetchall()
            for s in staff:
                print(f"  • {s[0]} - {s[1]} (Rating: {s[2]:.1f})")

    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n✓ Career mode database generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
