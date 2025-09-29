"""
Momentum Motorsport Simulation - Advanced Name Generation System

This module provides a hybrid name generation system that combines:
1. NameAPI external service for realistic, locale-specific names
2. ParaNames dataset for massive bulk generation capacity
3. Statistical frequency weighting for authenticity
4. Graceful fallbacks and error handling

The system ensures diverse, realistic names while maintaining performance
and avoiding copyright issues through fictional name generation.

Authors: Final Year Project - Computer Science
"""

import os
import sqlite3
import csv
import logging
import random
import time
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

# External dependencies (install via pip install nameapi-client)
try:
    from nameapi.client import NameApiClient, PersonNameGeneratorRequest
    NAMEAPI_AVAILABLE = True
except ImportError:
    NAMEAPI_AVAILABLE = False
    logging.warning("NameAPI client not available. Install with: pip install nameapi-client")

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

@dataclass
class NameGenerationConfig:
    """Configuration for name generation system"""
    nameapi_key: Optional[str] = None
    paranames_db_path: str = "data/paranames.db"
    use_api_primary: bool = True
    api_rate_limit: float = 1.0  # seconds between API calls
    max_api_retries: int = 3
    cache_size: int = 1000
    fallback_enabled: bool = True
    
class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    ANY = "ANY"

class NameSource(Enum):
    NAMEAPI = "nameapi"
    PARANAMES = "paranames"
    FALLBACK = "fallback"

@dataclass
class GeneratedName:
    """Structured name result with metadata"""
    first_name: str
    last_name: str
    full_name: str
    gender: Gender
    nationality: str
    locale: str
    source: NameSource
    confidence: float = 1.0
    
# ============================================================================
# COUNTRY/LOCALE MAPPING
# ============================================================================

# Map your racing countries to NameAPI locales and ParaNames languages
COUNTRY_LOCALE_MAP = {
    # Major motorsport countries with precise locale mapping
    "USA": {"nameapi": "en-US", "paranames": "en", "frequency_weight": 1.0},
    "GBR": {"nameapi": "en-GB", "paranames": "en", "frequency_weight": 0.9},
    "GER": {"nameapi": "de-DE", "paranames": "de", "frequency_weight": 0.8},
    "FRA": {"nameapi": "fr-FR", "paranames": "fr", "frequency_weight": 0.8},
    "ITA": {"nameapi": "it-IT", "paranames": "it", "frequency_weight": 0.7},
    "ESP": {"nameapi": "es-ES", "paranames": "es", "frequency_weight": 0.7},
    "JPN": {"nameapi": "ja-JP", "paranames": "ja", "frequency_weight": 0.6},
    "BRA": {"nameapi": "pt-BR", "paranames": "pt", "frequency_weight": 0.7},
    "AUS": {"nameapi": "en-AU", "paranames": "en", "frequency_weight": 0.6},
    "CAN": {"nameapi": "en-CA", "paranames": "en", "frequency_weight": 0.7},
    "MEX": {"nameapi": "es-MX", "paranames": "es", "frequency_weight": 0.6},
    "NLD": {"nameapi": "nl-NL", "paranames": "nl", "frequency_weight": 0.5},
    "BEL": {"nameapi": "nl-BE", "paranames": "nl", "frequency_weight": 0.4},
    "SWE": {"nameapi": "sv-SE", "paranames": "sv", "frequency_weight": 0.4},
    "FIN": {"nameapi": "fi-FI", "paranames": "fi", "frequency_weight": 0.3},
    "NOR": {"nameapi": "no-NO", "paranames": "no", "frequency_weight": 0.3},
    "DEN": {"nameapi": "da-DK", "paranames": "da", "frequency_weight": 0.3},
    "RUS": {"nameapi": "ru-RU", "paranames": "ru", "frequency_weight": 0.6},
    "CHN": {"nameapi": "zh-CN", "paranames": "zh", "frequency_weight": 0.8},
    "IND": {"nameapi": "hi-IN", "paranames": "hi", "frequency_weight": 0.7},
    "POL": {"nameapi": "pl-PL", "paranames": "pl", "frequency_weight": 0.4},
    "CZE": {"nameapi": "cs-CZ", "paranames": "cs", "frequency_weight": 0.3},
    "HUN": {"nameapi": "hu-HU", "paranames": "hu", "frequency_weight": 0.3},
    "GRC": {"nameapi": "el-GR", "paranames": "el", "frequency_weight": 0.3},
    "TUR": {"nameapi": "tr-TR", "paranames": "tr", "frequency_weight": 0.4},
    "ARG": {"nameapi": "es-AR", "paranames": "es", "frequency_weight": 0.4},
    "COL": {"nameapi": "es-CO", "paranames": "es", "frequency_weight": 0.3},
    "PER": {"nameapi": "es-PE", "paranames": "es", "frequency_weight": 0.3},
    "CHL": {"nameapi": "es-CL", "paranames": "es", "frequency_weight": 0.3},
    "ZAF": {"nameapi": "en-ZA", "paranames": "en", "frequency_weight": 0.3},
    "EGY": {"nameapi": "ar-EG", "paranames": "ar", "frequency_weight": 0.4},
    "MAR": {"nameapi": "ar-MA", "paranames": "ar", "frequency_weight": 0.3},
    "KOR": {"nameapi": "ko-KR", "paranames": "ko", "frequency_weight": 0.5},
    "THA": {"nameapi": "th-TH", "paranames": "th", "frequency_weight": 0.3},
    "SGP": {"nameapi": "en-SG", "paranames": "en", "frequency_weight": 0.3},
    "MYS": {"nameapi": "ms-MY", "paranames": "ms", "frequency_weight": 0.3},
    "IDN": {"nameapi": "id-ID", "paranames": "id", "frequency_weight": 0.4},
    "PHL": {"nameapi": "en-PH", "paranames": "en", "frequency_weight": 0.3},
    "VNM": {"nameapi": "vi-VN", "paranames": "vi", "frequency_weight": 0.4},
}

# ============================================================================
# PARANAMES DATABASE MANAGER
# ============================================================================

class ParaNamesDB:
    """Manages local ParaNames dataset for bulk name generation"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize ParaNames database structure"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                language TEXT NOT NULL,
                gender TEXT,
                frequency_score REAL DEFAULT 1.0,
                source TEXT DEFAULT 'paranames',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_language ON names(language);
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_gender ON names(gender);
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_frequency ON names(frequency_score DESC);
        """)
        
        self.conn.commit()
        
        # Check if we need to populate
        count = self.conn.execute("SELECT COUNT(*) FROM names").fetchone()[0]
        if count == 0:
            logging.info("ParaNames database empty. You may want to import data.")
    
    def import_paranames_tsv(self, tsv_path: str):
        """Import ParaNames dataset from TSV file"""
        if not Path(tsv_path).exists():
            logging.error(f"ParaNames TSV file not found: {tsv_path}")
            return False
        
        try:
            with open(tsv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                
                # Skip header if present
                header = next(reader, None)
                
                batch_size = 1000
                batch_data = []
                
                for row_num, row in enumerate(reader):
                    if len(row) < 3:
                        continue
                    
                    # Assuming TSV format: name_original, language, romanized_name, ...
                    name_original = row[0].strip()
                    language = row[1].strip()
                    romanized = row[2].strip() if len(row) > 2 else name_original
                    
                    # Parse name into first/last components
                    name_parts = romanized.split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = ' '.join(name_parts[1:])
                    else:
                        first_name = name_parts[0] if name_parts else romanized
                        last_name = "Unknown"
                    
                    # Assign gender (you might improve this with ML)
                    gender = self._guess_gender(first_name, language)
                    
                    batch_data.append((first_name, last_name, language, gender, 1.0, 'paranames'))
                    
                    if len(batch_data) >= batch_size:
                        self._insert_batch(batch_data)
                        batch_data = []
                        
                        if row_num % 10000 == 0:
                            logging.info(f"Imported {row_num} names...")
                
                # Insert remaining batch
                if batch_data:
                    self._insert_batch(batch_data)
                
                self.conn.commit()
                logging.info(f"Successfully imported ParaNames data from {tsv_path}")
                return True
                
        except Exception as e:
            logging.error(f"Failed to import ParaNames data: {e}")
            return False
    
    def _insert_batch(self, batch_data: List[Tuple]):
        """Insert batch of names efficiently"""
        self.conn.executemany("""
            INSERT INTO names (first_name, last_name, language, gender, frequency_score, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, batch_data)
    
    def _guess_gender(self, first_name: str, language: str) -> str:
        """Basic gender guessing - can be improved with ML models"""
        # This is a simplified approach - you might want to use actual gender prediction
        name_lower = first_name.lower()
        
        # Some basic heuristics for common languages
        if language in ['en', 'de', 'fr', 'es', 'it']:
            if name_lower.endswith(('a', 'e', 'ina', 'ette', 'elle')):
                return 'FEMALE'
            elif name_lower.endswith(('o', 'er', 'son', 'ton')):
                return 'MALE'
        
        # Default to random for unknown
        return random.choice(['MALE', 'FEMALE'])
    
    def get_random_name(self, language: str = None, gender: Gender = Gender.ANY) -> Optional[Tuple[str, str]]:
        """Get random name from ParaNames database"""
        if not self.conn:
            return None
        
        query = "SELECT first_name, last_name FROM names WHERE 1=1"
        params = []
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        if gender != Gender.ANY:
            query += " AND gender = ?"
            params.append(gender.value)
        
        query += " ORDER BY RANDOM() LIMIT 1"
        
        try:
            result = self.conn.execute(query, params).fetchone()
            return (result[0], result[1]) if result else None
        except Exception as e:
            logging.error(f"Error querying ParaNames database: {e}")
            return None
    
    def get_weighted_name(self, language: str = None, gender: Gender = Gender.ANY) -> Optional[Tuple[str, str]]:
        """Get weighted random name based on frequency scores"""
        if not self.conn:
            return None
        
        query = """
            SELECT first_name, last_name, frequency_score FROM names 
            WHERE 1=1
        """
        params = []
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        if gender != Gender.ANY:
            query += " AND gender = ?"
            params.append(gender.value)
        
        query += " ORDER BY frequency_score DESC LIMIT 100"
        
        try:
            results = self.conn.execute(query, params).fetchall()
            if not results:
                return None
            
            # Weighted random selection
            weights = [row[2] for row in results]
            selected = random.choices(results, weights=weights, k=1)[0]
            return (selected[0], selected[1])
            
        except Exception as e:
            logging.error(f"Error getting weighted name: {e}")
            return None

# ============================================================================
# NAMEAPI CLIENT WRAPPER
# ============================================================================

class NameAPIWrapper:
    """Wrapper for NameAPI service with rate limiting and caching"""
    
    def __init__(self, api_key: str, rate_limit: float = 1.0):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_call_time = 0
        self.call_count = 0
        self.cache: Dict[str, GeneratedName] = {}
        
        if not NAMEAPI_AVAILABLE:
            raise ImportError("NameAPI client not available. Install with: pip install nameapi-client")
        
        self.client = NameApiClient(api_key=api_key)
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        
        if time_since_last < self.rate_limit:
            wait_time = self.rate_limit - time_since_last
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def generate_name(self, country_code: str, gender: Gender = Gender.ANY, max_retries: int = 3) -> Optional[GeneratedName]:
        """Generate name using NameAPI service"""
        
        # Check cache first
        cache_key = f"{country_code}_{gender.value}"
        if cache_key in self.cache and random.random() < 0.1:  # 10% cache hit rate for variety
            return self.cache[cache_key]
        
        # Get locale mapping
        locale_info = COUNTRY_LOCALE_MAP.get(country_code)
        if not locale_info:
            return None
        
        nameapi_locale = locale_info["nameapi"]
        
        for attempt in range(max_retries):
            try:
                self._rate_limit_wait()
                
                # Create request
                req = PersonNameGeneratorRequest(
                    locale=nameapi_locale,
                    gender=gender.value if gender != Gender.ANY else None
                )
                
                # Make API call
                result = self.client.person_name_generator(req)
                self.call_count += 1
                
                if result and hasattr(result, 'firstName') and hasattr(result, 'lastName'):
                    generated_name = GeneratedName(
                        first_name=result.firstName,
                        last_name=result.lastName,
                        full_name=f"{result.firstName} {result.lastName}",
                        gender=gender,
                        nationality=country_code,
                        locale=nameapi_locale,
                        source=NameSource.NAMEAPI,
                        confidence=0.95
                    )
                    
                    # Cache result
                    self.cache[cache_key] = generated_name
                    return generated_name
                    
            except Exception as e:
                logging.warning(f"NameAPI call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(1.0 * (attempt + 1))  # Exponential backoff
        
        return None

# ============================================================================
# MAIN HYBRID NAME GENERATOR
# ============================================================================

class HybridNameGenerator:
    """Main name generation system combining all sources"""
    
    def __init__(self, config: NameGenerationConfig):
        self.config = config
        self.nameapi_client = None
        self.paranames_db = None
        self.generation_stats = {
            "total_generated": 0,
            "nameapi_success": 0,
            "paranames_used": 0,
            "fallback_used": 0
        }
        
        # Initialize NameAPI if configured
        if config.nameapi_key and NAMEAPI_AVAILABLE and config.use_api_primary:
            try:
                self.nameapi_client = NameAPIWrapper(config.nameapi_key, config.api_rate_limit)
                logging.info("NameAPI client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize NameAPI client: {e}")
        
        # Initialize ParaNames database
        try:
            self.paranames_db = ParaNamesDB(config.paranames_db_path)
            logging.info("ParaNames database initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize ParaNames database: {e}")
        
        # Fallback names for emergencies
        self.fallback_names = self._load_fallback_names()
    
    def _load_fallback_names(self) -> Dict[str, List[Tuple[str, str]]]:
        """Load basic fallback names for emergency use"""
        return {
            "MALE": [
                ("Alex", "Johnson"), ("Michael", "Smith"), ("David", "Wilson"),
                ("Chris", "Brown"), ("Mark", "Davis"), ("Paul", "Miller"),
                ("John", "Taylor"), ("James", "Anderson"), ("Robert", "Thomas"),
                ("Daniel", "Jackson"), ("Matthew", "White"), ("Andrew", "Martin")
            ],
            "FEMALE": [
                ("Sarah", "Johnson"), ("Emma", "Smith"), ("Lisa", "Wilson"),
                ("Anna", "Brown"), ("Maria", "Davis"), ("Jessica", "Miller"),
                ("Laura", "Taylor"), ("Michelle", "Anderson"), ("Rachel", "Thomas"),
                ("Nicole", "Jackson"), ("Amanda", "White"), ("Jennifer", "Martin")
            ]
        }
    
    def generate_driver_name(
        self, 
        country_code: str, 
        gender: Gender = Gender.ANY,
        prefer_api: bool = None
    ) -> GeneratedName:
        """Generate a single driver name using the hybrid system"""
        
        self.generation_stats["total_generated"] += 1
        
        # Determine generation strategy
        use_api = (prefer_api if prefer_api is not None else self.config.use_api_primary)
        
        # Try NameAPI first if enabled
        if use_api and self.nameapi_client:
            try:
                api_result = self.nameapi_client.generate_name(country_code, gender)
                if api_result:
                    self.generation_stats["nameapi_success"] += 1
                    return api_result
            except Exception as e:
                logging.warning(f"NameAPI generation failed: {e}")
        
        # Try ParaNames database
        if self.paranames_db and self.config.fallback_enabled:
            locale_info = COUNTRY_LOCALE_MAP.get(country_code)
            if locale_info:
                paranames_lang = locale_info["paranames"]
                
                # Try weighted selection first
                para_result = self.paranames_db.get_weighted_name(paranames_lang, gender)
                if not para_result:
                    # Fall back to random selection
                    para_result = self.paranames_db.get_random_name(paranames_lang, gender)
                
                if para_result:
                    self.generation_stats["paranames_used"] += 1
                    return GeneratedName(
                        first_name=para_result[0],
                        last_name=para_result[1],
                        full_name=f"{para_result[0]} {para_result[1]}",
                        gender=gender,
                        nationality=country_code,
                        locale=locale_info["nameapi"],
                        source=NameSource.PARANAMES,
                        confidence=0.8
                    )
        
        # Ultimate fallback to hardcoded names
        self.generation_stats["fallback_used"] += 1
        gender_key = gender.value if gender != Gender.ANY else random.choice(["MALE", "FEMALE"])
        fallback_name = random.choice(self.fallback_names[gender_key])
        
        return GeneratedName(
            first_name=fallback_name[0],
            last_name=fallback_name[1],
            full_name=f"{fallback_name[0]} {fallback_name[1]}",
            gender=Gender(gender_key),
            nationality=country_code,
            locale=COUNTRY_LOCALE_MAP.get(country_code, {}).get("nameapi", "en-US"),
            source=NameSource.FALLBACK,
            confidence=0.5
        )
    
    def generate_bulk_names(
        self, 
        count: int, 
        country_distribution: Dict[str, float] = None,
        gender_distribution: Dict[Gender, float] = None
    ) -> List[GeneratedName]:
        """Generate bulk names efficiently for database seeding"""
        
        if not country_distribution:
            # Default motorsport country distribution
            country_distribution = {
                "GBR": 0.15, "USA": 0.12, "GER": 0.10, "FRA": 0.08, "ITA": 0.08,
                "ESP": 0.06, "BRA": 0.05, "AUS": 0.04, "JPN": 0.04, "CAN": 0.03,
                "NLD": 0.03, "BEL": 0.02, "SWE": 0.02, "FIN": 0.02, "NOR": 0.02,
                "Other": 0.14
            }
        
        if not gender_distribution:
            # Motorsport is still male-dominated but improving
            gender_distribution = {Gender.MALE: 0.85, Gender.FEMALE: 0.15}
        
        results = []
        
        for i in range(count):
            # Select country based on distribution
            country = random.choices(
                list(country_distribution.keys()),
                weights=list(country_distribution.values()),
                k=1
            )[0]
            
            # Handle "Other" countries
            if country == "Other":
                country = random.choice(list(COUNTRY_LOCALE_MAP.keys()))
            
            # Select gender based on distribution
            gender = random.choices(
                list(gender_distribution.keys()),
                weights=list(gender_distribution.values()),
                k=1
            )[0]
            
            # Generate name with preference for database over API for bulk
            name = self.generate_driver_name(country, gender, prefer_api=False)
            results.append(name)
            
            # Progress logging for large batches
            if i > 0 and i % 100 == 0:
                logging.info(f"Generated {i}/{count} bulk names...")
        
        return results
    
    def get_generation_stats(self) -> Dict:
        """Get statistics about name generation performance"""
        total = self.generation_stats["total_generated"]
        if total == 0:
            return self.generation_stats
        
        return {
            **self.generation_stats,
            "nameapi_success_rate": self.generation_stats["nameapi_success"] / total,
            "paranames_usage_rate": self.generation_stats["paranames_used"] / total,
            "fallback_usage_rate": self.generation_stats["fallback_used"] / total
        }

# ============================================================================
# CONVENIENCE FUNCTIONS AND INTEGRATION
# ============================================================================

def setup_name_generator(api_key: str = None, paranames_tsv_path: str = None) -> HybridNameGenerator:
    """Set up the name generator with proper configuration"""
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv("NAMEAPI_KEY")
    
    config = NameGenerationConfig(
        nameapi_key=api_key,
        paranames_db_path="data/paranames.db",
        use_api_primary=bool(api_key),
        api_rate_limit=1.0,
        fallback_enabled=True
    )
    
    generator = HybridNameGenerator(config)
    
    # Import ParaNames data if provided
    if paranames_tsv_path and Path(paranames_tsv_path).exists():
        logging.info("Importing ParaNames dataset...")
        generator.paranames_db.import_paranames_tsv(paranames_tsv_path)
    
    return generator

# Global generator instance (initialized when needed)
_global_generator = None

def get_global_generator() -> HybridNameGenerator:
    """Get or create global name generator instance"""
    global _global_generator
    if _global_generator is None:
        _global_generator = setup_name_generator()
    return _global_generator

def generate_racing_driver_name(country_code: str, gender: str = "ANY") -> Dict[str, str]:
    """
    Convenience function for generating racing driver names
    Compatible with existing placeholder_names.py interface
    """
    generator = get_global_generator()
    
    # Convert string gender to enum
    gender_enum = Gender.ANY
    if gender.upper() == "MALE":
        gender_enum = Gender.MALE
    elif gender.upper() == "FEMALE":
        gender_enum = Gender.FEMALE
    
    result = generator.generate_driver_name(country_code, gender_enum)
    
    return {
        "first_name": result.first_name,
        "last_name": result.last_name,
        "full_name": result.full_name,
        "nationality": result.nationality,
        "gender": result.gender.value,
        "source": result.source.value,
        "confidence": result.confidence
    }

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

__all__ = [
    "HybridNameGenerator", "NameGenerationConfig", "ParaNamesDB",
    "NameAPIWrapper", "GeneratedName", "Gender", "NameSource",
    "setup_name_generator", "get_global_generator", "generate_racing_driver_name",
    "COUNTRY_LOCALE_MAP"
]

# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

if __name__ == "__main__":
    # Demonstration of the hybrid system
    print("=== MOMENTUM HYBRID NAME GENERATION SYSTEM ===\n")
    
    # Set up generator (you would set your API key here)
    # generator = setup_name_generator(api_key="your-api-key-here")
    generator = setup_name_generator()  # Will use fallback mode without API key
    
    print("Generating sample driver names for major motorsport countries:")
    countries = ["GBR", "USA", "GER", "FRA", "ITA", "ESP", "BRA", "JPN"]
    
    for country in countries:
        name = generate_racing_driver_name(country, "MALE")
        print(f"{country}: {name['full_name']} (Source: {name['source']}, Confidence: {name['confidence']:.2f})")
    
    print("\nGenerating bulk names for database seeding:")
    bulk_names = generator.generate_bulk_names(20)
    for i, name in enumerate(bulk_names[:10]):  # Show first 10
        print(f"{i+1:2d}. {name.full_name} ({name.nationality}, {name.gender.value}, {name.source.value})")
    
    print(f"\nGeneration Statistics:")
    stats = generator.get_generation_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nSystem ready for integration with Momentum simulation!")