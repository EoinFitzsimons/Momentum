"""
Intelligent Name Generation using Faker + Uniqueness Tracking

This system uses:
1. Faker library for culturally-appropriate name generation
2. SQLite database to track used names and prevent duplicates
3. Locale-specific generation based on nationality
4. Intelligent retry logic if duplicate detected

This solves the duplicate name problem without requiring massive datasets.
"""

import sqlite3
import logging
from faker import Faker
from typing import Optional, Set
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IntelligentNameGenerator:
    """
    Generate unique, culturally-appropriate names using Faker
    """
    
    def __init__(self, db_path: str = "data/used_names.db"):
        self.db_path = db_path
        self.conn = None
        self.used_names_cache: Set[str] = set()
        self._init_database()
        self._load_cache()
        
        # Initialize Faker instances for different locales
        self.faker_instances = {
            'en_US': Faker('en_US'),
            'en_GB': Faker('en_GB'),
            'de_DE': Faker('de_DE'),
            'fr_FR': Faker('fr_FR'),
            'it_IT': Faker('it_IT'),
            'es_ES': Faker('es_ES'),
            'pt_BR': Faker('pt_BR'),
            'ja_JP': Faker('ja_JP'),
            'zh_CN': Faker('zh_CN'),
            'ru_RU': Faker('ru_RU'),
            'nl_NL': Faker('nl_NL'),
            'sv_SE': Faker('sv_SE'),
            'fi_FI': Faker('fi_FI'),
            'no_NO': Faker('no_NO'),
            'da_DK': Faker('da_DK'),
            'pl_PL': Faker('pl_PL'),
            'cs_CZ': Faker('cs_CZ'),
            'hu_HU': Faker('hu_HU'),
            'tr_TR': Faker('tr_TR'),
            'ar_SA': Faker('ar_SA'),
            'ko_KR': Faker('ko_KR'),
            'hi_IN': Faker('hi_IN'),
            'es_MX': Faker('es_MX'),
            'pt_PT': Faker('pt_PT'),
        }
        
        # Comprehensive map of country codes to Faker locales with regional fallbacks
        self.country_to_locale = {
            # North America
            'USA': 'en_US', 'CAN': 'en_US', 'MEX': 'es_MX',
            
            # Western Europe
            'GBR': 'en_GB', 'IRL': 'en_GB', 'GER': 'de_DE', 'FRA': 'fr_FR',
            'ITA': 'it_IT', 'ESP': 'es_ES', 'NLD': 'nl_NL', 'BEL': 'nl_NL',
            'SWI': 'de_DE', 'AUT': 'de_DE', 'POR': 'pt_PT',
            
            # Scandinavia
            'SWE': 'sv_SE', 'FIN': 'fi_FI', 'NOR': 'no_NO', 'DEN': 'da_DK',
            
            # Eastern Europe
            'POL': 'pl_PL', 'CZE': 'cs_CZ', 'HUN': 'hu_HU', 'RUS': 'ru_RU',
            'UKR': 'ru_RU', 'BLR': 'ru_RU', 'SVK': 'cs_CZ', 'SVN': 'cs_CZ',
            'CRO': 'cs_CZ', 'SRB': 'cs_CZ', 'BUL': 'ru_RU', 'ROM': 'ru_RU',
            
            # Southern Europe
            'GRE': 'en_GB', 'TUR': 'tr_TR', 'CYP': 'en_GB', 'MLT': 'en_GB',
            
            # Asia Pacific
            'JPN': 'ja_JP', 'CHN': 'zh_CN', 'KOR': 'ko_KR', 'IND': 'hi_IN',
            'AUS': 'en_GB', 'NZL': 'en_GB', 'SGP': 'en_GB', 'HKG': 'zh_CN',
            'TWN': 'zh_CN', 'THA': 'en_GB', 'MYS': 'en_GB', 'IDN': 'en_GB',
            'PHL': 'en_US', 'VNM': 'en_GB',
            
            # Middle East
            'SAU': 'ar_SA', 'UAE': 'ar_SA', 'QAT': 'ar_SA', 'KWT': 'ar_SA',
            'BHR': 'ar_SA', 'OMN': 'ar_SA', 'JOR': 'ar_SA', 'LBN': 'ar_SA',
            'ISR': 'en_GB', 'IRN': 'ar_SA', 'IRQ': 'ar_SA', 'SYR': 'ar_SA',
            
            # South America
            'BRA': 'pt_BR', 'ARG': 'es_ES', 'CHI': 'es_ES', 'COL': 'es_ES',
            'PER': 'es_ES', 'VEN': 'es_ES', 'ECU': 'es_ES', 'URU': 'es_ES',
            'PRY': 'es_ES', 'BOL': 'es_ES',
            
            # Central America & Caribbean
            'CRC': 'es_ES', 'PAN': 'es_ES', 'GTM': 'es_ES', 'HND': 'es_ES',
            'SLV': 'es_ES', 'NIC': 'es_ES', 'DOM': 'es_ES', 'CUB': 'es_ES',
            'JAM': 'en_GB', 'TTO': 'en_GB', 'BRB': 'en_GB', 'PRI': 'es_ES',
            'MTQ': 'fr_FR', 'GLP': 'fr_FR', 'GUF': 'fr_FR',
            
            # Africa
            'RSA': 'en_GB', 'ZIM': 'en_GB', 'KEN': 'en_GB', 'NGA': 'en_GB',
            'GHA': 'en_GB', 'EGY': 'ar_SA', 'MAR': 'fr_FR', 'TUN': 'fr_FR',
            'ALG': 'fr_FR', 'SEN': 'fr_FR', 'CIV': 'fr_FR', 'CMR': 'fr_FR',
            'ETH': 'en_GB', 'TZA': 'en_GB', 'UGA': 'en_GB', 'ZMB': 'en_GB',
            
            # Other regions
            'BTN': 'hi_IN', 'NPL': 'hi_IN', 'LKA': 'hi_IN', 'BGD': 'hi_IN',
            'PAK': 'hi_IN', 'AFG': 'hi_IN', 'KHM': 'en_GB', 'LAO': 'en_GB',
            'MMR': 'en_GB', 'ARK': 'en_US',  # Arkansas (US state fallback)
        }
    
    def _init_database(self):
        """Initialize the used names database"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS used_names (
                full_name TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                nationality TEXT,
                gender TEXT,
                role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nationality ON used_names(nationality)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_gender ON used_names(gender)
        """)
        
        self.conn.commit()
        logging.info(f"Initialized name tracking database: {self.db_path}")
    
    def _load_cache(self):
        """Load all used names into memory cache for fast lookup"""
        cursor = self.conn.cursor()
        used = cursor.execute('SELECT full_name FROM used_names').fetchall()
        self.used_names_cache = {name[0] for name in used}
        logging.info(f"Loaded {len(self.used_names_cache):,} used names into cache")
    
    def generate_unique_name(self, 
                            nationality: str = 'USA',
                            gender: Optional[str] = None,
                            role: Optional[str] = None,
                            max_attempts: int = 100) -> dict:
        """
        Generate a unique name that hasn't been used before
        
        Args:
            nationality: Country code (e.g., 'USA', 'GBR', 'GER')
            gender: 'M' or 'F' or None for random
            role: Role type (e.g., 'driver', 'engineer', etc.)
            max_attempts: Maximum attempts to find unique name
            
        Returns:
            dict with first_name, last_name, full_name, nationality, gender
        """
        # Get appropriate Faker instance
        locale = self.country_to_locale.get(nationality, 'en_US')
        faker = self.faker_instances.get(locale, self.faker_instances['en_US'])
        
        for attempt in range(max_attempts):
            # Generate name based on gender
            if gender == 'M':
                first_name = faker.first_name_male()
                last_name = faker.last_name()
            elif gender == 'F':
                first_name = faker.first_name_female()
                last_name = faker.last_name()
            else:
                # Random gender
                if random.choice([True, False]):
                    first_name = faker.first_name_male()
                    gender_used = 'M'
                else:
                    first_name = faker.first_name_female()
                    gender_used = 'F'
                last_name = faker.last_name()
                gender = gender_used
            
            full_name = f"{first_name} {last_name}"
            
            # Check if name is unique
            if full_name not in self.used_names_cache:
                # Mark as used
                self._mark_name_used(first_name, last_name, full_name, nationality, gender, role)
                
                return {
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': full_name,
                    'nationality': nationality,
                    'gender': gender,
                    'role': role
                }
        
        # If we couldn't find unique name after max_attempts, append number
        first_name = faker.first_name()
        last_name = faker.last_name()
        full_name = f"{first_name} {last_name} {len(self.used_names_cache)}"
        self._mark_name_used(first_name, last_name, full_name, nationality, gender, role)
        
        logging.warning(f"Had to use numbered name: {full_name}")
        return {
            'first_name': first_name,
            'last_name': f"{last_name} {len(self.used_names_cache)}",
            'full_name': full_name,
            'nationality': nationality,
            'gender': gender,
            'role': role
        }
    
    def _mark_name_used(self, first_name: str, last_name: str, full_name: str,
                       nationality: str, gender: str, role: Optional[str]):
        """Mark a name as used in database and cache"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO used_names (full_name, first_name, last_name, nationality, gender, role)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_name, first_name, last_name, nationality, gender, role))
            self.conn.commit()
            self.used_names_cache.add(full_name)
        except sqlite3.IntegrityError:
            # Name already exists (race condition), try again
            logging.debug(f"Name already used: {full_name}")
    
    def clear_all_names(self):
        """Clear all used names (for testing or reset)"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM used_names')
        self.conn.commit()
        self.used_names_cache.clear()
        logging.info("Cleared all used names")
    
    def get_statistics(self):
        """Get statistics about generated names"""
        cursor = self.conn.cursor()
        total = cursor.execute('SELECT COUNT(*) FROM used_names').fetchone()[0]
        by_nationality = cursor.execute('''
            SELECT nationality, COUNT(*) as count 
            FROM used_names 
            GROUP BY nationality 
            ORDER BY count DESC 
            LIMIT 10
        ''').fetchall()
        by_gender = cursor.execute('''
            SELECT gender, COUNT(*) as count 
            FROM used_names 
            GROUP BY gender
        ''').fetchall()
        
        return {
            'total': total,
            'by_nationality': by_nationality,
            'by_gender': by_gender
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Convenience function for simple usage
def generate_driver_name(nationality: str = 'USA', gender: Optional[str] = None) -> dict:
    """Quick function to generate a unique driver name"""
    generator = IntelligentNameGenerator()
    name = generator.generate_unique_name(nationality, gender, role='driver')
    generator.close()
    return name


if __name__ == "__main__":
    # Test the generator
    print("=" * 80)
    print("Intelligent Name Generator Test")
    print("=" * 80)
    print()
    
    gen = IntelligentNameGenerator()
    
    # Generate some test names
    print("Generating 20 unique names from different nationalities:\n")
    
    nationalities = ['USA', 'GBR', 'GER', 'FRA', 'ITA', 'ESP', 'JPN', 'BRA', 'CHN', 'RUS']
    
    for i in range(20):
        nat = random.choice(nationalities)
        gender = random.choice(['M', 'F'])
        name = gen.generate_unique_name(nat, gender, 'driver')
        print(f"{i+1:2d}. {name['full_name']:30s} ({nat}, {gender})")
    
    print()
    print("=" * 80)
    stats = gen.get_statistics()
    print(f"Total names generated: {stats['total']}")
    print("\nBy nationality:")
    for nat, count in stats['by_nationality']:
        print(f"  {nat}: {count}")
    print("\nBy gender:")
    for gender, count in stats['by_gender']:
        print(f"  {gender}: {count}")
    print("=" * 80)
    
    gen.close()
