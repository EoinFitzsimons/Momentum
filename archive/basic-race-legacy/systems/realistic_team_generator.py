"""
Realistic Racing Team Name Generator

Generates authentic racing team names inspired by real motorsport structure:
- Original manufacturer names (multi-language, non-English influences)
- Title sponsor system (Base Team + Optional Sponsor)
- Cultural/geographic authenticity
- No real-world brand names

Examples: Invicta Racing, Campos Racing, Rodin Motorsport, DAMS Lucas Oil
"""

import random
from typing import Optional, Tuple

# ============================================================================
# FICTIONAL MANUFACTURER NAMES
# Based on real automotive naming patterns (see documentation)
# Patterns: Founder surnames, geographic+industry, meaningful translations,
#           acronyms, Latin wordplay, cultural meanings
# ============================================================================

ELITE_MANUFACTURERS = [
    # Pattern 1: Founder Surnames (like Ferrari, Ford, Honda, Renault)
    # Italian surnames
    "Bellini", "Moretti", "Ricci", "Fontana", "Barbieri", "Lombardi",
    "Marchetti", "Vitali", "Rossini", "Bianchi", "Conti", "Ferraro",
    
    # French surnames  
    "Beaumont", "Chevalier", "Dubois", "Garnier", "Mercier", "Rousseau",
    "Lefevre", "Girard", "Bonnet", "Clement", "Fournier", "Morel",
    
    # German surnames
    "Hartmann", "Kaufmann", "Becker", "Schröder", "Zimmermann", "Wagner",
    "Hoffmann", "Koch", "Richter", "Klein", "Wolf", "Neumann",
    
    # English surnames
    "Ashford", "Blackwell", "Carrington", "Fairfax", "Hartley", "Sterling",
    "Prescott", "Whitmore", "Langford", "Sutton", "Thornhill", "Weston",
    
    # Spanish/Portuguese surnames
    "Navarro", "Mendoza", "Cordero", "Vasconcelos", "Almeida", "Cardoso",
    "Ferreira", "Pereira", "Machado", "Carvalho", "Oliveira", "Monteiro",
    
    # Scandinavian surnames
    "Bergström", "Lindgren", "Svensson", "Nilsson", "Petersen", "Johannsen",
    "Andersen", "Hansen", "Olsen", "Larsen", "Eriksen", "Sørensen",
    
    # Japanese surnames (romanized, like Mazda from Matsuda)
    "Yamamoto", "Tanaka", "Watanabe", "Nakamura", "Kobayashi", "Sasaki",
    "Takahashi", "Fujimoto", "Hayashi", "Ishikawa", "Matsuda", "Yoshida",
    
    # Pattern 2: Geographic + Industry (like BMW = Bavarian Motor Works)
    # Format: [Region] [Industry term]
    "Alpenwerk",      # Alpine Works (German)
    "Nordmotor",      # North Motor (Nordic)
    "Süd Automobil",  # South Automobile (German)
    "Ostfabrik",      # East Factory (German)
    "Westwerk",       # West Works (German)
    
    # Pattern 3: Meaningful Words (like Volkswagen = people's car, Hyundai = modernity)
    # Latin-based
    "Velocitas",   # Speed (Latin)
    "Fortitudo",   # Strength (Latin)
    "Claritas",    # Clarity (Latin)
    "Veritas",     # Truth (Latin)
    "Aequitas",    # Equity (Latin)
    
    # Italian meaning
    "Rapido",      # Fast
    "Veloce",      # Swift
    "Forza",       # Force/Power
    "Legato",      # Connected
    
    # Pattern 4: Acronyms (like FIAT = Italian Auto Factory Turin)
    "AMTC",    # Automotive Manufacturing & Technology Corp
    "GEMA",    # Global Engineering & Motor Alliance
    "VECT",    # Vehicle Engineering & Construction Tech
    "APEX",    # Advanced Precision Engineering eXcellence
    "DYNX",    # Dynamic X-tech
    "VEXA",    # Vehicle EXcellence Alliance
    
    # Pattern 5: Cultural/Translated Names (like Audi = Latin for Horch)
    "Auscult",     # Latin: "to listen" (like Audi/Horch)
    "Stellarum",   # Latin: "of the stars"
    "Momentum",    # Latin: "movement"
    "Impetus",     # Latin: "driving force"
    "Cursus",      # Latin: "course/journey"
    
    # Pattern 6: Compound Names (descriptive)
    "Nordstahl",      # North Steel (German)
    "Südkraft",       # South Power (German)
    "Alpenmotor",     # Alpine Motor (German)
    "Eurotech",       # European Technology
    "Asiamotor",      # Asia Motor
    "Pacificworks",   # Pacific Works
]

# ============================================================================
# TITLE SPONSORS (GAMEPLAY MECHANIC - NOT USED IN BASE TEAM NAMES)
# These are available as optional sponsorship deals during gameplay
# Teams can sell naming rights for additional budget
# ============================================================================

# Note: Title sponsors are managed through the sponsorship system
# Base team names use only manufacturer names + suffix
# Example: "Invicta Racing" can become "Invicta TechCore Racing" with sponsor deal

# ============================================================================
# TEAM TYPE SUFFIXES
# Based on real motorsport team naming conventions
# ============================================================================

TEAM_SUFFIXES = [
    "Racing", "Motorsport", "Team", "Racing Team",
    "Motorsports", "Competition", "Squad", "Crew"
]

# ============================================================================
# GEOGRAPHIC MODIFIERS
# To add regional flavor (optional use)
# ============================================================================

GEOGRAPHIC_MODIFIERS = {
    "Europe": ["European", "Euro", "Continental"],
    "Asia": ["Asian", "Pan-Asian", "Eastern"],
    "America": ["American", "Trans-Atlantic", "Western"],
    "Global": ["International", "Global", "Worldwide", "Universal"]
}

# ============================================================================
# TEAM NAME GENERATOR CLASS
# ============================================================================

class RealisticTeamGenerator:
    """
    Generates realistic racing team names with title sponsor system.
    
    Structure options:
    1. Base only: "Invicta Racing"
    2. With sponsor: "Campos TechCore Racing"
    3. With modifier: "Euro Campos Racing"
    """
    
    def __init__(self):
        self.used_base_names = set()
        self.used_full_names = set()
    
    def generate_team_name(
        self, 
        category: str = "SINGLE_SEATER",
        tier: int = 1,
        use_modifier_probability: float = 0.15
    ) -> str:
        """
        Generate a realistic BASE team name (no title sponsors).
        
        Title sponsors are added via gameplay sponsorship system, not at generation.
        
        Args:
            category: Racing category (affects naming style)
            tier: Tier level (1-5, for future use)
            use_modifier_probability: Chance of adding geographic modifier
            
        Returns:
            Generated team name (e.g., "Invicta Racing", "Campos Motorsport")
        """
        max_attempts = 50
        
        for _ in range(max_attempts):
            # Step 1: Select base manufacturer name
            base_name = random.choice(ELITE_MANUFACTURERS)
            
            # Step 2: Select suffix
            suffix = random.choice(TEAM_SUFFIXES)
            
            # Step 3: Decide on geographic modifier (rare, adds prestige)
            has_modifier = random.random() < use_modifier_probability
            
            # Build name
            parts = []
            
            # Add modifier (rare - e.g., "Euro Campos Racing")
            if has_modifier:
                region = random.choice(list(GEOGRAPHIC_MODIFIERS.keys()))
                modifier = random.choice(GEOGRAPHIC_MODIFIERS[region])
                parts.append(modifier)
            
            # Add base name
            parts.append(base_name)
            
            # Add suffix
            parts.append(suffix)
            
            # Construct full name
            full_name = " ".join(parts)
            
            # Check uniqueness
            if full_name not in self.used_full_names:
                self.used_full_names.add(full_name)
                self.used_base_names.add(base_name)
                return full_name
        
        # Fallback: append number
        fallback_name = f"{random.choice(ELITE_MANUFACTURERS)} Racing {random.randint(1, 999)}"
        self.used_full_names.add(fallback_name)
        return fallback_name
    
    def reset(self):
        """Clear used names cache."""
        self.used_base_names.clear()
        self.used_full_names.clear()


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

_generator = RealisticTeamGenerator()

def generate_realistic_team_name(category: str = "SINGLE_SEATER", tier: int = 1) -> str:
    """
    Convenience function for generating realistic team names.
    
    Args:
        category: Racing category
        tier: Tier level (1-5)
        
    Returns:
        Realistic team name
    """
    return _generator.generate_team_name(category=category, tier=tier)


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

if __name__ == "__main__":
    print("Realistic Racing Team Name Generator - Examples")
    print("=" * 60)
    print("\nNOTE: Base team names only. Title sponsors added via gameplay!")
    print("=" * 60)
    
    # Test Tier 1 teams
    print("\nTier 1 Elite Teams (Single Seater):")
    for i in range(15):
        name = generate_realistic_team_name(category="SINGLE_SEATER", tier=1)
        print(f"  {i+1}. {name}")
    
    # Test Tier 3 teams
    print("\nTier 3 Mid-Field Teams:")
    _generator.reset()
    for i in range(10):
        name = generate_realistic_team_name(category="SINGLE_SEATER", tier=3)
        print(f"  {i+1}. {name}")
    
    # Test variety
    print("\nVariety Test (50 teams):")
    _generator.reset()
    names = [generate_realistic_team_name(tier=random.randint(1, 5)) for _ in range(50)]
    unique_bases = len(set(n.split()[0] if not n.split()[0] in GEOGRAPHIC_MODIFIERS.get("Global", []) + GEOGRAPHIC_MODIFIERS.get("Europe", []) + GEOGRAPHIC_MODIFIERS.get("Asia", []) + GEOGRAPHIC_MODIFIERS.get("America", []) else n.split()[1] for n in names))
    print(f"  Generated: {len(names)} teams")
    print(f"  Unique base names: {unique_bases}")
    print(f"  Sample: {names[:5]}")
