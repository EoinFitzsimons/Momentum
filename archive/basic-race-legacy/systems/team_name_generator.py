"""
Improved Team Name Generation System

Generates realistic racing team names with proper variety and authenticity.
Uses component-based generation with location, sponsor, and technical elements.
"""

import random
from typing import Optional

# Location-based prefixes (cities, regions, countries)
TEAM_LOCATIONS = [
    "Monaco", "Silverstone", "Monza", "Spa", "Nürburgring", "Le Mans", "Daytona",
    "Indianapolis", "Sebring", "Laguna Seca", "Brands Hatch", "Suzuka", "Shanghai",
    "Melbourne", "São Paulo", "Mexico City", "Austin", "Miami", "Las Vegas",
    "Monte Carlo", "Barcelona", "Zandvoort", "Budapest", "Singapore", "Baku",
    "Montreal", "Imola", "Portimão", "Hockenheim", "Paul Ricard", "Estoril",
    "Jerez", "Magny-Cours", "Yas Marina", "Sochi", "Istanbul", "Valencia",
    "European", "American", "Asian", "Global", "International", "WorldWide",
    "Atlantic", "Pacific", "Nordic", "Alpine", "Mediterranean", "Adriatic"
]

# Sponsor/company style prefixes
TEAM_SPONSORS = [
    "Velocity", "Apex", "Phoenix", "Thunder", "Lightning", "Storm", "Tempest",
    "Viper", "Cobra", "Falcon", "Eagle", "Hawk", "Panther", "Jaguar", "Lion",
    "Titan", "Atlas", "Olympus", "Zenith", "Summit", "Pinnacle", "Prime",
    "Elite", "Ultimate", "Supreme", "Imperial", "Royal", "Sovereign", "Majestic",
    "Turbo", "Nitro", "Boost", "Thrust", "Power", "Force", "Energy", "Momentum",
    "Quantum", "Fusion", "Plasma", "Vector", "Matrix", "Nexus", "Helix",
    "Carbon", "Titanium", "Platinum", "Diamond", "Crystal", "Steel", "Chrome",
    "Crimson", "Azure", "Emerald", "Golden", "Silver", "Scarlet", "Cobalt",
    "Revolution", "Evolution", "Innovation", "Precision", "Performance", "Dynamics",
    "Alpha", "Beta", "Gamma", "Delta", "Sigma", "Omega", "Nova", "Stella",
    "Red Bull", "Ferrari", "Mercedes", "McLaren", "Aston Martin", "Alpine", "Williams"
]

# Technical/racing suffixes
TEAM_SUFFIXES = [
    "Racing", "Motorsport", "Motorsports", "Racing Team", "Competition",
    "GP", "Grand Prix", "F1 Team", "Racing Division", "Autosport",
    "Performance", "Engineering", "Technologies", "Dynamics", "Systems",
    "Speed", "Velocity", "Racing Squad", "Racing Stable", "Garage",
    "Team", "Crew", "Squad", "Collective", "Division", "Unit",
    "Racing Club", "Motor Club", "Automobile Club", "Sports Club",
    "Legends", "Champions", "Warriors", "Challengers", "Contenders",
    "Racing Alliance", "Racing Federation", "Racing Association",
    "Speedway", "Circuit", "Track Racing", "Formula Racing",
    "Rally Team", "Rally Sport", "Off-Road Racing", "Street Racing"
]

# Adjective modifiers for variety
TEAM_ADJECTIVES = [
    "Advanced", "Aggressive", "Ambitious", "Bold", "Brave", "Brilliant",
    "Classic", "Competitive", "Dominant", "Dynamic", "Efficient", "Elite",
    "Epic", "Extreme", "Fast", "Fearless", "Fierce", "Flying", "Legendary",
    "Mighty", "Modern", "Powerful", "Premium", "Professional", "Proven",
    "Quick", "Rapid", "Relentless", "Revolutionary", "Roaring", "Serious",
    "Sleek", "Smooth", "Sonic", "Spectacular", "Spirited", "Strategic",
    "Superior", "Swift", "Ultimate", "Unstoppable", "Victorious", "Wild"
]

# Color-based team names
TEAM_COLORS = [
    "Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Black", "White",
    "Silver", "Gold", "Crimson", "Azure", "Emerald", "Scarlet", "Cobalt",
    "Violet", "Amber", "Ruby", "Sapphire", "Jade", "Onyx", "Pearl"
]

# Country-specific team name patterns
COUNTRY_PATTERNS = {
    'ITA': ['Scuderia', 'Squadra Corse', 'Racing'],
    'GER': ['Rennstall', 'Motorsport', 'Racing'],
    'FRA': ['Équipe', 'Racing', 'Motorsport'],
    'ESP': ['Escudería', 'Racing', 'Motorsport'],
    'JPN': ['Racing', 'Team', 'Motorsport'],
    'GBR': ['Racing', 'Motorsport', 'GP'],
    'USA': ['Racing', 'Motorsport', 'Team'],
}


class TeamNameGenerator:
    """Generate realistic racing team names with variety"""
    
    def __init__(self):
        self.used_names = set()
    
    def generate_team_name(
        self, 
        category: str = None,
        tier: int = None,
        nationality: Optional[str] = None,
        style: Optional[str] = None
    ) -> str:
        """
        Generate a unique team name
        
        Args:
            category: Racing category (SINGLE_SEATER, RALLY, etc.)
            tier: Team tier (1=top, 2=mid, 3+=lower)
            nationality: Team nationality for cultural naming
            style: Naming style ('location', 'sponsor', 'color', 'technical', 'mixed')
        
        Returns:
            Unique team name string
        """
        
        # Choose generation style
        if style is None:
            style = random.choice(['location', 'sponsor', 'color', 'technical', 'mixed', 'simple'])
        
        for attempt in range(100):
            if style == 'location':
                name = self._generate_location_based()
            elif style == 'sponsor':
                name = self._generate_sponsor_based()
            elif style == 'color':
                name = self._generate_color_based()
            elif style == 'technical':
                name = self._generate_technical_based()
            elif style == 'mixed':
                name = self._generate_mixed()
            else:  # simple
                name = self._generate_simple()
            
            # Check uniqueness
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        
        # Fallback with number
        base_name = self._generate_simple()
        return f"{base_name} {len(self.used_names)}"
    
    def _generate_location_based(self) -> str:
        """Location + suffix pattern"""
        location = random.choice(TEAM_LOCATIONS)
        suffix = random.choice(TEAM_SUFFIXES)
        
        # Sometimes add adjective
        if random.random() < 0.3:
            adj = random.choice(TEAM_ADJECTIVES)
            return f"{location} {adj} {suffix}"
        
        return f"{location} {suffix}"
    
    def _generate_sponsor_based(self) -> str:
        """Sponsor + suffix pattern"""
        sponsor = random.choice(TEAM_SPONSORS)
        suffix = random.choice(TEAM_SUFFIXES)
        return f"{sponsor} {suffix}"
    
    def _generate_color_based(self) -> str:
        """Color + animal/object + suffix"""
        color = random.choice(TEAM_COLORS)
        element = random.choice(["Bull", "Arrow", "Star", "Lightning", "Thunder", "Storm"])
        suffix = random.choice(TEAM_SUFFIXES)
        
        patterns = [
            f"{color} {element}",
            f"{color} {element} {suffix}",
            f"{element} {color} {suffix}"
        ]
        
        return random.choice(patterns)
    
    def _generate_technical_based(self) -> str:
        """Technical/engineering focused names"""
        tech = random.choice(["Aero", "Turbo", "Hybrid", "Electric", "Velocity", "Precision"])
        suffix = random.choice(["Dynamics", "Engineering", "Technologies", "Systems", "Racing"])
        return f"{tech} {suffix}"
    
    def _generate_mixed(self) -> str:
        """Mix different patterns"""
        patterns = [
            lambda: f"{random.choice(TEAM_ADJECTIVES)} {random.choice(TEAM_SPONSORS)} {random.choice(TEAM_SUFFIXES)}",
            lambda: f"{random.choice(TEAM_LOCATIONS)} {random.choice(TEAM_COLORS)} {random.choice(TEAM_SUFFIXES)}",
            lambda: f"{random.choice(TEAM_SPONSORS)} {random.choice(TEAM_LOCATIONS)} {random.choice(TEAM_SUFFIXES)}"
        ]
        
        return random.choice(patterns)()
    
    def _generate_simple(self) -> str:
        """Simple two-word names"""
        word1 = random.choice(TEAM_SPONSORS)
        word2 = random.choice(["Racing", "Motorsport", "Team", "GP"])
        return f"{word1} {word2}"
    
    def clear_cache(self):
        """Clear used names cache"""
        self.used_names.clear()


# Global instance for easy import
_global_generator = TeamNameGenerator()


def generate_improved_team_name(
    category: str = None,
    tier: int = None, 
    nationality: Optional[str] = None
) -> str:
    """
    Generate a team name using the global generator
    
    This is a drop-in replacement for the old generate_team_name()
    """
    return _global_generator.generate_team_name(
        category=category,
        tier=tier,
        nationality=nationality
    )


# Alias for backward compatibility
generate_team_name = generate_improved_team_name


if __name__ == "__main__":
    # Test generation
    print("Testing Team Name Generator\n")
    print("=" * 60)
    
    for i in range(20):
        name = generate_improved_team_name()
        print(f"{i+1:2d}. {name}")
    
    print("\n" + "=" * 60)
    print(f"Total unique names generated: {len(_global_generator.used_names)}")
