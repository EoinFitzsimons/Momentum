"""
Team Name Generation - Faker-based authentic team naming

Generates realistic, unique team names across multiple disciplines using Faker.
Supports automotive, corporate, and regional naming patterns for authenticity.

Features:
- Multi-locale support for international teams
- Discipline-specific naming patterns
- Avoidance of real-world F1/F2 team conflicts
- Fallback ASCII translation for non-Latin scripts
- Customizable name patterns and prefixes
"""

from faker import Faker
import random
import re
import unicodedata
import importlib
from typing import List, Set, Optional, Callable, cast

# Try to use Unidecode for robust transliteration
try:
    _unidecode_module = importlib.import_module("unidecode")
    _unidecode = cast(Callable[[str], str], getattr(_unidecode_module, "unidecode"))
except Exception:
    _unidecode = None  # type: ignore[assignment]


class TeamNameGenerator:
    """Generate authentic team names using Faker"""

    # Real-world teams to avoid conflicts
    RESERVED_NAMES = {
        # Formula 1 teams
        "Mercedes",
        "Red Bull",
        "Ferrari",
        "McLaren",
        "Alpine",
        "Aston Martin",
        "Haas",
        "AlphaTauri",
        "Alfa Romeo",
        "Williams",
        "Sauber",
        "Lotus",
        "Force India",
        "Manor",
        "Caterham",
        # Other major racing teams
        "Porsche",
        "BMW",
        "Audi",
        "Lamborghini",
        "Jaguar",
        "Bentley",
        "Rolls Royce",
        "Tesla",
        "Bugatti",
        # Generic/overused names
        "Speedway Racing",
        "Fast Lane",
        "Thunder",
        "Lightning",
        "Victory",
        "Championship",
        "Racing Team",
        "Motorsports",
    }

    # Team name patterns by discipline
    PATTERNS = {
        "SINGLE_SEATER": [
            "{company} Racing",
            "{company} Motorsport",
            "{company} Grand Prix",
            "{place} Racing",
            "{adjective} {company}",
            "{company} Elite",
            "{place} {adjective}",
            "{prefix} {company} {suffix}",
            "{company} {suffix}",
            "{color} {company} Racing",
        ],
        "PRODUCTION_TOURING": [
            "{company} Touring",
            "{company} Cup Team",
            "{place} Touring",
            "{adjective} {car_brand}",
            "{company} Motorsport",
            "{car_brand} Specialists",
            "{prefix} {place} {suffix}",
            "{company} Works",
            "{adjective} {company} Touring",
        ],
        "URBAN_STREET": [
            "{place} Drift Team",
            "{company} Drift",
            "{place} Drift Racing",
            "{adjective} Drift",
            "{company} Drift Squad",
            "{color} Drift {crew}",
            "{animal} Drift Team",
            "{company} Slide Works",
        ],
        "DRAG_ACCELERATION": [
            "{company} Drag",
            "{place} Drag Racing",
            "{company} Speed",
            "{adjective} Acceleration",
            "{place} Dragway",
            "{animal} Drag",
            "{company} Launch {crew}",
            "{color} Speedworks",
        ],
        "SPRINT_RALLYCROSS": [
            "{company} Sprint",
            "{place} Rallycross",
            "{company} Cross",
            "{adjective} Sprint",
            "{place} Sprint Team",
            "{company} RX",
            "{animal} Rallycross",
        ],
        "ENDURANCE": [
            "{company} Endurance",
            "{place} 24H Team",
            "{company} Endurance Racing",
            "{place} Long Distance",
            "{adjective} Endurance",
            "{company} Marathon",
            "{company} {suffix}",
            "{color} Endurance {crew}",
        ],
    }

    # Adjectives for team names
    ADJECTIVES = [
        "Apex",
        "Precision",
        "Thunder",
        "Storm",
        "Velocity",
        "Nitro",
        "Blaze",
        "Arctic",
        "Crimson",
        "Azure",
        "Elite",
        "Prime",
        "Peak",
        "Dynamic",
        "Phoenix",
        "Quantum",
        "Sonic",
        "Titan",
        "Vortex",
        "Steel",
        "Iron",
        "Bolt",
        "Arrow",
        "Surge",
        "Vector",
        "Pulse",
        "Rapid",
        "Frontier",
        "Neon",
        "Shadow",
        "Glacier",
        "Turbo",
        "Forge",
        "Catalyst",
    ]

    # Prefixes and suffixes to enrich naming variety
    PREFIXES = [
        "Team",
        "Racing",
        "Motorsport",
        "Auto",
        "Performance",
        "Speed",
        "Works",
        "Engineering",
        "Dynamics",
        "Competition",
    ]
    SUFFIXES = [
        "Racing",
        "Motorsport",
        "Works",
        "GP",
        "Performance",
        "Engineering",
        "Competition",
        "Factory",
        "Dynamics",
        "Crew",
    ]

    # Additional theme pools
    COLORS = ["Red", "Blue", "Black", "White", "Silver", "Gold", "Crimson", "Azure"]
    ANIMALS = [
        "Falcon",
        "Viper",
        "Wolf",
        "Panther",
        "Eagle",
        "Stallion",
        "Lynx",
        "Raven",
    ]
    CREW_TERMS = ["Squad", "Crew", "Unit", "Collective", "Garage"]

    # Car brands for authenticity
    CAR_BRANDS = [
        "BMW",
        "Audi",
        "Porsche",
        "Lotus",
        "McLaren",
        "Nissan",
        "Subaru",
        "Toyota",
        "Mitsubishi",
        "Honda",
        "Renault",
        "Peugeot",
        "Citroen",
        "Alfa Romeo",
        "Lancia",
        "Chevrolet",
        "Dodge",
        "Ford",
        "Cadillac",
        "GMC",
        "Volvo",
        "Saab",
        "Jaguar",
        "Land Rover",
        "Bentley",
    ]

    # Locales for diverse naming
    LOCALES = [
        "en_GB",
        "en_US",
        "it_IT",
        "fr_FR",
        "de_DE",
        "es_ES",
        "pt_BR",
        "nl_NL",
        "sv_SE",
        "da_DK",
        "en_AU",
        "en_CA",
        "no_NO",
        "pl_PL",
        "fi_FI",
    ]

    def __init__(self):
        """Initialize team name generator with Faker instances"""
        self.fakers = {locale: Faker(locale) for locale in self.LOCALES}
        self.generated_names: Set[str] = set()

    def _to_latin(self, s: str) -> str:
        """Convert string to Latin characters"""
        if not s:
            return s

        if _unidecode:
            out = _unidecode(s)
        else:
            out = unicodedata.normalize("NFKD", s)
            out = out.encode("ascii", "ignore").decode("ascii")

        out = " ".join(out.split())
        return out

    def _sanitize_name(self, name: str) -> str:
        """Clean and sanitize team name"""
        # Remove common honorifics
        name = re.sub(r"^(The|A|An)\s+", "", name, flags=re.IGNORECASE)
        name = re.sub(
            r"\s+(Inc|Ltd|LLC|GmbH|AG|SpA|SPA|SA)\s*$", "", name, flags=re.IGNORECASE
        )

        # Convert to Latin
        name = self._to_latin(name)

        # Clean up spacing
        name = " ".join(name.split())
        name = name.strip()

        return name

    def _get_company_name(self, locale: Optional[str] = None) -> str:
        """Get a company name from Faker"""
        selected_locale = locale or random.choice(self.LOCALES)

        faker = self.fakers[selected_locale]
        company = faker.company()
        return self._sanitize_name(company)

    def _get_place_name(self, locale: Optional[str] = None) -> str:
        """Get a place name from Faker"""
        selected_locale = locale or random.choice(self.LOCALES)

        faker = self.fakers[selected_locale]
        # Use city names (most reliable across all locales)
        place = faker.city()
        return self._sanitize_name(place)

    def generate_name(self, discipline: Optional[str] = None) -> str:
        """
        Generate a unique team name

        Args:
            discipline: Racing discipline (e.g., 'SINGLE_SEATER', 'URBAN_STREET')
                       If None, chooses random discipline

        Returns:
            Unique team name string
        """
        if not discipline:
            discipline = random.choice(list(self.PATTERNS.keys()))

        # Get patterns for this discipline
        patterns = self.PATTERNS.get(discipline, self.PATTERNS["SINGLE_SEATER"])

        # Try to generate a unique name
        max_attempts = 50
        for _ in range(max_attempts):
            pattern = random.choice(patterns)

            # Generate substitutions
            company = self._get_company_name()
            place = self._get_place_name()
            adjective = random.choice(self.ADJECTIVES)
            car_brand = random.choice(self.CAR_BRANDS)
            prefix = random.choice(self.PREFIXES)
            suffix = random.choice(self.SUFFIXES)
            color = random.choice(self.COLORS)
            animal = random.choice(self.ANIMALS)
            crew = random.choice(self.CREW_TERMS)

            # Fill in pattern
            name = pattern.format(
                company=company,
                place=place,
                adjective=adjective,
                car_brand=car_brand,
                prefix=prefix,
                suffix=suffix,
                color=color,
                animal=animal,
                crew=crew,
            )

            # Check if name is unique and not reserved
            if (
                name not in self.generated_names
                and name not in self.RESERVED_NAMES
                and len(name) > 5
            ):
                self.generated_names.add(name)
                return name

        # Fallback: create distinctive name
        company = self._get_company_name()
        adjective = random.choice(self.ADJECTIVES)
        return f"{adjective} {company}".strip()

    def generate_names(self, count: int, discipline: Optional[str] = None) -> List[str]:
        """
        Generate multiple unique team names

        Args:
            count: Number of names to generate
            discipline: Racing discipline (optional)

        Returns:
            List of unique team names
        """
        names = []
        for _ in range(count):
            name = self.generate_name(discipline)
            names.append(name)
        return names

    def get_nationality_for_team(self, team_name: str) -> str:
        """
        Estimate nationality from generated team name

        Returns:
            Country code (e.g., 'GB', 'DE', 'IT')
        """
        # This is a heuristic - in reality, could track during generation
        country_hints = {
            "Audi": "DE",
            "BMW": "DE",
            "Porsche": "DE",
            "Mercedes": "DE",
            "Ferrari": "IT",
            "Alfa Romeo": "IT",
            "Lamborghini": "IT",
            "Renault": "FR",
            "Peugeot": "FR",
            "Citroën": "FR",
            "Lotus": "GB",
            "McLaren": "GB",
            "Jaguar": "GB",
            "Nissan": "JP",
            "Honda": "JP",
            "Toyota": "JP",
            "Mitsubishi": "JP",
            "Volvo": "SE",
            "Saab": "SE",
        }

        for brand, country in country_hints.items():
            if brand in team_name:
                return country

        # Default: use random from team name generation
        return random.choice(["GB", "DE", "FR", "IT", "US", "JP", "SE"])


# Global instance for convenience
_generator = None


def get_generator() -> TeamNameGenerator:
    """Get or create global team name generator"""
    global _generator
    if _generator is None:
        _generator = TeamNameGenerator()
    return _generator


def generate_team_name(discipline: Optional[str] = None) -> str:
    """Generate a unique team name (convenience function)"""
    return get_generator().generate_name(discipline)


def generate_team_names(count: int, discipline: Optional[str] = None) -> List[str]:
    """Generate multiple unique team names (convenience function)"""
    return get_generator().generate_names(count, discipline)


__all__ = [
    "TeamNameGenerator",
    "generate_team_name",
    "generate_team_names",
    "get_generator",
]
