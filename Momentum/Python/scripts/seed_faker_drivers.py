"""
Seed the Momentum SQLite DB with sample drivers using Faker.
This script ensures the database schema exists (via DatabaseManager) then
inserts several drivers using different name "types" to exercise name generation.

Run from repository root (PowerShell):
$env:PYTHONPATH='Momentum/Python'; python Momentum/Python/scripts/seed_faker_drivers.py
"""
from faker import Faker
import random
import json
from datetime import datetime, timedelta
from database.database_manager import DatabaseManager
from config import DISCIPLINES
import unicodedata
import runpy
from pathlib import Path
import re

# Try to use Unidecode for robust transliteration; fall back to NFKD
try:
    from unidecode import unidecode as _unidecode
except Exception:
    _unidecode = None

# Load ASCII-first/last name pools from archive for fallback when transliteration
# removes too much content (e.g., names entirely non-Latin). This gives stable
# Latin-script fallbacks.
archive_path = Path(__file__).resolve().parents[3] / 'archive' / 'placeholder_names.py'
if archive_path.exists():
    ns = runpy.run_path(str(archive_path))
    firsts = ns.get('FIRST_NAMES')
    if isinstance(firsts, dict):
        FIRST_NAME_POOL = list(firsts.get('male', [])) + list(firsts.get('female', []))
    elif isinstance(firsts, list):
        FIRST_NAME_POOL = list(firsts)
    else:
        FIRST_NAME_POOL = ['Alex', 'Sam', 'Chris']
    LAST_NAME_POOL = ns.get('LAST_NAMES', []) or ['Smith', 'Jones', 'Brown']
else:
    FIRST_NAME_POOL = ['Alex', 'Sam', 'Chris']
    LAST_NAME_POOL = ['Smith', 'Jones', 'Brown']


def to_latin(s: str) -> str:
    if not s:
        return s
    if _unidecode:
        out = _unidecode(s)
    else:
        out = unicodedata.normalize('NFKD', s)
        out = out.encode('ascii', 'ignore').decode('ascii')
    out = ' '.join(out.split())
    return out


_ascii_letter_re = re.compile(r'[A-Za-z]')

# strip common honorific prefixes and professional suffixes
HONORIFIC_PREFIX_RE = re.compile(r'^(Dr\.?|Mr\.?|Ms\.?|Mrs\.?|Miss\.?|Prof\.?|Sir\.?|Dame\.?|Lady\.?)\s+', flags=re.IGNORECASE)
HONORIFIC_SUFFIX_RE = re.compile(r'\b(MD|M\.D\.|DDS|D\.D\.S\.|PhD|Ph\.D\.|Jr\.|Sr\.|II|III|IV)\b', flags=re.IGNORECASE)

# Use the canonical country list from the project and map to locales.
from tools.locale_mapping import get_all_country_codes, get_locale_for_country
COUNTRY_CODES = get_all_country_codes()

# Use only full names for seeding so the GUI shows full driver names
NAME_TYPES = ['full']

# Number of drivers to create. Default to configured race grid size so GUI
# and quick-race scripts get a full grid by default. Can be overridden with
# the FAKER_NUM_DRIVERS env var if needed.
from config import RACE_GRID_SIZE
import os
NUM_DRIVERS = int(os.getenv('FAKER_NUM_DRIVERS', str(RACE_GRID_SIZE or 20)))


def random_birth_date(min_age=18, max_age=45):
    today = datetime.utcnow().date()
    age = random.randint(min_age, max_age)
    # approximate birthdate
    birth = today - timedelta(days=365 * age + random.randint(0, 365))
    return birth.strftime('%Y-%m-%d')


def format_name(fake: Faker, name_type: str) -> str:
    if name_type == 'full':
        nm = fake.name()
        # remove common honorific prefixes and suffixes
        nm = HONORIFIC_PREFIX_RE.sub('', nm)
        nm = HONORIFIC_SUFFIX_RE.sub('', nm).strip()
        nm = to_latin(nm)
        if not _ascii_letter_re.search(nm):
            # fallback to ASCII pool
            return f"{random.choice(FIRST_NAME_POOL)} {random.choice(LAST_NAME_POOL)}"
        return nm
    first = fake.first_name()
    last = fake.last_name()
    if name_type == 'initials':
        nm = f"{first[0]}. {last}"
        nm = HONORIFIC_PREFIX_RE.sub('', nm)
        nm = HONORIFIC_SUFFIX_RE.sub('', nm).strip()
        nm = to_latin(nm)
        if not _ascii_letter_re.search(nm):
            return f"{random.choice(FIRST_NAME_POOL)} {random.choice(LAST_NAME_POOL)}"
        return nm
    if name_type == 'mononym':
        nm = to_latin(first)
        if not _ascii_letter_re.search(nm):
            return random.choice(FIRST_NAME_POOL)
        return nm
    if name_type == 'nickname':
        nm = f"{first} '{last[:3]}' {last}"
        nm = to_latin(nm)
        if not _ascii_letter_re.search(nm):
            return f"{random.choice(FIRST_NAME_POOL)} {random.choice(LAST_NAME_POOL)}"
        return nm
    nm = f"{first} {last}"
    nm = to_latin(nm)
    if not _ascii_letter_re.search(nm):
        return f"{random.choice(FIRST_NAME_POOL)} {random.choice(LAST_NAME_POOL)}"
    return nm


def main():
    print('Initializing DB and schema...')
    dbm = DatabaseManager()  # ensure schema exists
    conn = dbm.get_connection()
    # Ensure any new columns added to SCHEMA_SQL are present in existing DB
    # If the DB was created earlier with an older schema, add missing columns.
    existing_cols = {r['name'] for r in conn.execute("PRAGMA table_info('drivers')").fetchall()}
    needed = {
        'speed': "speed REAL NOT NULL DEFAULT 50.0",
        'racecraft': "racecraft REAL NOT NULL DEFAULT 50.0",
        'consistency': "consistency REAL NOT NULL DEFAULT 50.0",
        'fitness': "fitness REAL NOT NULL DEFAULT 50.0",
        'reactions': "reactions REAL NOT NULL DEFAULT 50.0",
        'pressure': "pressure REAL NOT NULL DEFAULT 50.0",
        'setup_knowledge': "setup_knowledge REAL NOT NULL DEFAULT 50.0",
        'fuel_management': "fuel_management REAL NOT NULL DEFAULT 50.0",
        'tyre_management': "tyre_management REAL NOT NULL DEFAULT 50.0",
        'feedback': "feedback REAL NOT NULL DEFAULT 50.0",
        'adaptability': "adaptability REAL NOT NULL DEFAULT 50.0",
        'previous_teams': "previous_teams TEXT DEFAULT '[]'",
    }
    to_add = [k for k in needed.keys() if k not in existing_cols]
    if to_add:
        print('Migrating drivers table; adding columns:', to_add)
        with conn:
            for col in to_add:
                sql = f"ALTER TABLE drivers ADD COLUMN {needed[col]}"
                conn.execute(sql)
    # ensure name_locale column exists
    if 'name_locale' not in existing_cols:
        print('Adding name_locale column to drivers table')
        with conn:
            conn.execute("ALTER TABLE drivers ADD COLUMN name_locale TEXT DEFAULT NULL")
    drivers_created = []
    with conn:
        cur = conn.cursor()

        for i in range(NUM_DRIVERS):
            nationality = random.choice(COUNTRY_CODES)
            locale = get_locale_for_country(nationality)
            try:
                fake = Faker(locale)
            except Exception:
                locale = "en_US"
                fake = Faker(locale)
            name_type = random.choice(NAME_TYPES)
            name = format_name(fake, name_type)
            birth_date = random_birth_date()
            speed = round(random.uniform(30.0, 90.0), 2)
            racecraft = round(random.uniform(30.0, 90.0), 2)
            consistency = round(random.uniform(30.0, 90.0), 2)
            fitness = round(random.uniform(30.0, 90.0), 2)
            reactions = round(random.uniform(30.0, 90.0), 2)
            pressure = round(random.uniform(30.0, 90.0), 2)
            setup_knowledge = round(random.uniform(30.0, 90.0), 2)
            fuel_management = round(random.uniform(30.0, 90.0), 2)
            tyre_management = round(random.uniform(30.0, 90.0), 2)
            feedback = round(random.uniform(30.0, 90.0), 2)
            adaptability = round(random.uniform(30.0, 90.0), 2)
            previous_teams = json.dumps([])

            cur.execute('''
                INSERT INTO drivers (
                    name, nationality, birth_date, speed, racecraft, consistency,
                    fitness, reactions, pressure, setup_knowledge, fuel_management,
                    tyre_management, feedback, adaptability, previous_teams, name_locale
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, nationality, birth_date, speed, racecraft, consistency,
                fitness, reactions, pressure, setup_knowledge, fuel_management,
                tyre_management, feedback, adaptability, previous_teams, locale
            ))
            drivers_created.append((cur.lastrowid, name, nationality, name_type))

    print(f'Inserted {len(drivers_created)} drivers into DB at: {dbm.db_path}')
    print('Sample drivers:')
    for did, nm, nat, nt in drivers_created[:6]:
        print(f' - [{did}] {nm} ({nat}) type={nt}')


if __name__ == '__main__':
    main()
