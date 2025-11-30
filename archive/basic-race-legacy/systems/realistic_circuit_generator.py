"""
Realistic Racing Circuit Generator

Generates original racing circuits with detailed properties:
- Original circuit names (no real-world tracks)
- Geographic location and climate data
- Technical specifications (turns, elevation, length)
- Racing discipline suitability
- Surface and layout characteristics

Based on real motorsport venues but with fictional names.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class CircuitType(Enum):
    """Types of circuit layouts"""
    PERMANENT = "permanent"  # Purpose-built racing circuit
    STREET = "street"        # Temporary street circuit
    ROAD = "road"           # Public roads converted for racing
    OVAL = "oval"           # Oval/speedway
    MIXED = "mixed"         # Combination of permanent + street


class SurfaceType(Enum):
    """Racing surface types"""
    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    GRAVEL = "gravel"
    DIRT = "dirt"
    MIXED = "mixed"


class Climate(Enum):
    """Climate zones"""
    TEMPERATE = "temperate"
    TROPICAL = "tropical"
    DESERT = "desert"
    MEDITERRANEAN = "mediterranean"
    CONTINENTAL = "continental"
    POLAR = "polar"


@dataclass
class CircuitData:
    """Complete circuit specification"""
    name: str
    country: str
    city: str
    circuit_type: CircuitType
    
    # Technical specifications
    length_km: float
    turns: int
    elevation_change_m: float
    max_gradient_percent: float
    
    # Track characteristics
    surface: SurfaceType
    average_speed_kmh: float
    longest_straight_m: float
    narrowest_point_m: float
    widest_point_m: float
    
    # Environmental
    climate: Climate
    average_temp_c: float
    rainfall_days_per_year: int
    altitude_m: int
    
    # Racing suitability (0.0 to 1.0)
    single_seater_suitability: float
    rally_suitability: float
    endurance_suitability: float
    sprint_suitability: float
    
    # Additional info
    pit_lane_length_m: float
    paddock_capacity: int
    night_racing_capable: bool
    fia_grade: str  # Grade 1, 2, 3, or "Not Graded"


# ============================================================================
# CIRCUIT NAME COMPONENTS
# Multi-language influenced, original names
# ============================================================================

# Base names (geographic/cultural influences)
CIRCUIT_BASE_NAMES = [
    # European-inspired
    "Aldoria", "Belmont", "Cascara", "Delvaux", "Estavon",
    "Fontaine", "Glenmont", "Haverton", "Ironbridge", "Jarville",
    "Kingsford", "Lansbury", "Montrose", "Norcastle", "Oakridge",
    "Pemberton", "Queensbury", "Riverside", "Stonehaven", "Thornbury",
    
    # Latin-inspired
    "Valestra", "Portavia", "Meridia", "Costanza", "Ravenna",
    "Silvano", "Montalvo", "Bellavista", "Carrera", "Estrella",
    
    # Asian-inspired (Romanized)
    "Sakura", "Mizuno", "Hayashi", "Takumi", "Hikari",
    "Kaze", "Nami", "Yama", "Hoshi", "Tsuki",
    
    # Middle Eastern-inspired
    "Almara", "Bahrain", "Calida", "Dakhla", "Emara",
    "Falaj", "Ghazi", "Hafar", "Jabal", "Karim",
    
    # Abstract/Modern
    "Apex", "Zenith", "Nexus", "Vortex", "Catalyst",
    "Meridian", "Horizon", "Eclipse", "Aether", "Quantum"
]

# Circuit type descriptors
CIRCUIT_DESCRIPTORS = [
    "International Circuit", "Grand Prix Circuit", "Racing Circuit",
    "Motorsport Complex", "Speed Circuit", "Racing Park",
    "Autodrome", "Motor Speedway", "Racing Arena",
    "Circuit de", "Circuito", "Autodromo", "Rennstrecke"
]

# Regional modifiers
REGIONAL_MODIFIERS = [
    "North", "South", "East", "West", "Central",
    "Royal", "National", "International", "Grand",
    "New", "Old", "Greater"
]

# ============================================================================
# LOCATION DATA
# Fictional but geographically plausible
# ============================================================================

CIRCUIT_LOCATIONS = [
    # Europe
    {"country": "Italy", "cities": ["Aldoria", "Bellavista", "Montalvo"], "climate": Climate.MEDITERRANEAN},
    {"country": "France", "cities": ["Fontaine", "Delvaux", "Estavon"], "climate": Climate.TEMPERATE},
    {"country": "Spain", "cities": ["Costanza", "Estrella", "Valestra"], "climate": Climate.MEDITERRANEAN},
    {"country": "Germany", "cities": ["Ironbridge", "Thornbury", "Norcastle"], "climate": Climate.CONTINENTAL},
    {"country": "United Kingdom", "cities": ["Pemberton", "Kingsford", "Haverton"], "climate": Climate.TEMPERATE},
    {"country": "Belgium", "cities": ["Cascara", "Lansbury", "Riverside"], "climate": Climate.TEMPERATE},
    {"country": "Netherlands", "cities": ["Glenmont", "Oakridge", "Queensbury"], "climate": Climate.TEMPERATE},
    
    # Americas
    {"country": "United States", "cities": ["Phoenix Heights", "Silver Springs", "Crystal Bay"], "climate": Climate.CONTINENTAL},
    {"country": "Brazil", "cities": ["Portavia", "Meridia", "Ravenna"], "climate": Climate.TROPICAL},
    {"country": "Mexico", "cities": ["Carrera", "Silvano", "Montrose"], "climate": Climate.DESERT},
    {"country": "Canada", "cities": ["Stonehaven", "Montrose", "Belmont"], "climate": Climate.CONTINENTAL},
    
    # Asia
    {"country": "Japan", "cities": ["Sakura", "Mizuno", "Takumi"], "climate": Climate.TEMPERATE},
    {"country": "Singapore", "cities": ["Meridian", "Nexus", "Horizon"], "climate": Climate.TROPICAL},
    {"country": "South Korea", "cities": ["Hayashi", "Hikari", "Nami"], "climate": Climate.CONTINENTAL},
    
    # Middle East
    {"country": "United Arab Emirates", "cities": ["Emara", "Almara", "Calida"], "climate": Climate.DESERT},
    {"country": "Bahrain", "cities": ["Dakhla", "Hafar", "Ghazi"], "climate": Climate.DESERT},
    
    # Oceania
    {"country": "Australia", "cities": ["Zenith", "Eclipse", "Catalyst"], "climate": Climate.MEDITERRANEAN},
]

# ============================================================================
# CIRCUIT GENERATOR
# ============================================================================

class RealisticCircuitGenerator:
    """Generates detailed, realistic racing circuits with original names"""
    
    def __init__(self):
        self.used_names = set()
        self.circuits = []
    
    def _generate_circuit_name(self, city: str, country: str) -> str:
        """Generate a unique circuit name"""
        
        patterns = [
            f"{city} {random.choice(CIRCUIT_DESCRIPTORS)}",
            f"{random.choice(REGIONAL_MODIFIERS)} {city} Circuit",
            f"Circuit de {city}",
            f"Autodromo {city}",
            f"{city} Grand Prix Circuit",
            f"{city} International Raceway",
            f"{city} Motor Speedway"
        ]
        
        for _ in range(20):
            name = random.choice(patterns)
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        
        # Fallback
        fallback = f"{city} Circuit {random.randint(1, 99)}"
        self.used_names.add(fallback)
        return fallback
    
    def _generate_technical_specs(self, circuit_type: CircuitType) -> Dict:
        """Generate realistic technical specifications"""
        
        if circuit_type == CircuitType.STREET:
            return {
                "length_km": round(random.uniform(3.2, 6.5), 2),
                "turns": random.randint(14, 23),
                "elevation_change_m": round(random.uniform(15, 85), 1),
                "max_gradient_percent": round(random.uniform(6, 18), 1),
                "average_speed_kmh": round(random.uniform(180, 220), 1),
                "longest_straight_m": random.randint(600, 1200),
                "narrowest_point_m": round(random.uniform(8, 11), 1),
                "widest_point_m": round(random.uniform(14, 18), 1),
                "pit_lane_length_m": random.randint(250, 450)
            }
        elif circuit_type == CircuitType.PERMANENT:
            return {
                "length_km": round(random.uniform(4.0, 7.0), 2),
                "turns": random.randint(12, 20),
                "elevation_change_m": round(random.uniform(20, 120), 1),
                "max_gradient_percent": round(random.uniform(8, 22), 1),
                "average_speed_kmh": round(random.uniform(200, 240), 1),
                "longest_straight_m": random.randint(800, 1800),
                "narrowest_point_m": round(random.uniform(10, 13), 1),
                "widest_point_m": round(random.uniform(15, 22), 1),
                "pit_lane_length_m": random.randint(300, 550)
            }
        elif circuit_type == CircuitType.OVAL:
            return {
                "length_km": round(random.uniform(2.0, 4.5), 2),
                "turns": random.choice([4, 8]),  # Oval configurations
                "elevation_change_m": round(random.uniform(5, 35), 1),
                "max_gradient_percent": round(random.uniform(2, 12), 1),
                "average_speed_kmh": round(random.uniform(260, 320), 1),
                "longest_straight_m": random.randint(1200, 2000),
                "narrowest_point_m": round(random.uniform(12, 15), 1),
                "widest_point_m": round(random.uniform(18, 25), 1),
                "pit_lane_length_m": random.randint(400, 700)
            }
        else:  # ROAD or MIXED
            return {
                "length_km": round(random.uniform(5.0, 12.0), 2),
                "turns": random.randint(18, 35),
                "elevation_change_m": round(random.uniform(80, 250), 1),
                "max_gradient_percent": round(random.uniform(12, 28), 1),
                "average_speed_kmh": round(random.uniform(160, 200), 1),
                "longest_straight_m": random.randint(500, 1000),
                "narrowest_point_m": round(random.uniform(7, 10), 1),
                "widest_point_m": round(random.uniform(12, 16), 1),
                "pit_lane_length_m": random.randint(200, 400)
            }
    
    def _generate_environmental_data(self, climate: Climate) -> Dict:
        """Generate climate and environmental data"""
        
        climate_data = {
            Climate.MEDITERRANEAN: {
                "temp_range": (18, 28),
                "rainfall_range": (40, 90),
                "altitude_range": (0, 300)
            },
            Climate.TROPICAL: {
                "temp_range": (25, 32),
                "rainfall_range": (120, 200),
                "altitude_range": (0, 200)
            },
            Climate.DESERT: {
                "temp_range": (28, 40),
                "rainfall_range": (5, 30),
                "altitude_range": (0, 500)
            },
            Climate.TEMPERATE: {
                "temp_range": (12, 22),
                "rainfall_range": (80, 140),
                "altitude_range": (0, 400)
            },
            Climate.CONTINENTAL: {
                "temp_range": (8, 24),
                "rainfall_range": (60, 110),
                "altitude_range": (100, 800)
            }
        }
        
        data = climate_data.get(climate, climate_data[Climate.TEMPERATE])
        
        return {
            "average_temp_c": round(random.uniform(*data["temp_range"]), 1),
            "rainfall_days_per_year": random.randint(*data["rainfall_range"]),
            "altitude_m": random.randint(*data["altitude_range"])
        }
    
    def generate_circuit(
        self,
        discipline: Optional[str] = None,
        circuit_type: Optional[CircuitType] = None
    ) -> CircuitData:
        """
        Generate a complete realistic circuit.
        
        Args:
            discipline: Target discipline (SINGLE_SEATER, RALLY_STAGE, etc.)
            circuit_type: Specific circuit type to generate
            
        Returns:
            CircuitData with all specifications
        """
        
        # Select location
        location = random.choice(CIRCUIT_LOCATIONS)
        city = random.choice(location["cities"])
        country = location["country"]
        climate = location["climate"]
        
        # Determine circuit type
        if circuit_type is None:
            if discipline == "RALLY_STAGE":
                circuit_type = random.choice([CircuitType.ROAD, CircuitType.MIXED])
            elif discipline == "DRAG_ACCELERATION":
                circuit_type = CircuitType.PERMANENT
            else:
                circuit_type = random.choice([
                    CircuitType.PERMANENT, CircuitType.PERMANENT, CircuitType.PERMANENT,  # Most common
                    CircuitType.STREET, CircuitType.MIXED
                ])
        
        # Generate name
        name = self._generate_circuit_name(city, country)
        
        # Generate technical specs
        tech_specs = self._generate_technical_specs(circuit_type)
        
        # Generate environmental data
        env_data = self._generate_environmental_data(climate)
        
        # Determine surface
        if discipline == "RALLY_STAGE":
            surface = random.choice([SurfaceType.GRAVEL, SurfaceType.DIRT, SurfaceType.MIXED])
        else:
            surface = random.choice([SurfaceType.ASPHALT, SurfaceType.ASPHALT, SurfaceType.ASPHALT, SurfaceType.CONCRETE])
        
        # Generate discipline suitability
        suitability = self._generate_discipline_suitability(circuit_type, discipline)
        
        # FIA Grade (for single seater circuits)
        fia_grade = self._determine_fia_grade(tech_specs["length_km"], tech_specs["widest_point_m"])
        
        # Create circuit data
        circuit = CircuitData(
            name=name,
            country=country,
            city=city,
            circuit_type=circuit_type,
            length_km=tech_specs["length_km"],
            turns=tech_specs["turns"],
            elevation_change_m=tech_specs["elevation_change_m"],
            max_gradient_percent=tech_specs["max_gradient_percent"],
            surface=surface,
            average_speed_kmh=tech_specs["average_speed_kmh"],
            longest_straight_m=tech_specs["longest_straight_m"],
            narrowest_point_m=tech_specs["narrowest_point_m"],
            widest_point_m=tech_specs["widest_point_m"],
            climate=climate,
            average_temp_c=env_data["average_temp_c"],
            rainfall_days_per_year=env_data["rainfall_days_per_year"],
            altitude_m=env_data["altitude_m"],
            single_seater_suitability=suitability["single_seater"],
            rally_suitability=suitability["rally"],
            endurance_suitability=suitability["endurance"],
            sprint_suitability=suitability["sprint"],
            pit_lane_length_m=tech_specs["pit_lane_length_m"],
            paddock_capacity=random.randint(20, 50),
            night_racing_capable=random.choice([True, False]),
            fia_grade=fia_grade
        )
        
        self.circuits.append(circuit)
        return circuit
    
    def _generate_discipline_suitability(self, circuit_type: CircuitType, target_discipline: Optional[str]) -> Dict[str, float]:
        """Calculate how suitable the circuit is for each discipline"""
        
        base_suitability = {
            "single_seater": 0.5,
            "rally": 0.3,
            "endurance": 0.5,
            "sprint": 0.6
        }
        
        # Adjust based on circuit type
        if circuit_type == CircuitType.PERMANENT:
            base_suitability["single_seater"] += 0.3
            base_suitability["endurance"] += 0.3
        elif circuit_type == CircuitType.STREET:
            base_suitability["single_seater"] += 0.2
            base_suitability["sprint"] += 0.2
        elif circuit_type == CircuitType.ROAD:
            base_suitability["rally"] += 0.5
            base_suitability["endurance"] += 0.2
        
        # Boost target discipline
        if target_discipline:
            if "SINGLE_SEATER" in target_discipline:
                base_suitability["single_seater"] = min(1.0, base_suitability["single_seater"] + 0.3)
            elif "RALLY" in target_discipline:
                base_suitability["rally"] = min(1.0, base_suitability["rally"] + 0.4)
            elif "ENDURANCE" in target_discipline:
                base_suitability["endurance"] = min(1.0, base_suitability["endurance"] + 0.3)
            elif "SPRINT" in target_discipline or "DRAG" in target_discipline:
                base_suitability["sprint"] = min(1.0, base_suitability["sprint"] + 0.3)
        
        # Clamp values
        return {k: round(max(0.0, min(1.0, v)), 2) for k, v in base_suitability.items()}
    
    def _determine_fia_grade(self, length_km: float, width_m: float) -> str:
        """Determine FIA circuit grade"""
        
        if length_km >= 4.5 and width_m >= 15:
            return random.choice(["Grade 1", "Grade 1", "Grade 2"])
        elif length_km >= 3.5 and width_m >= 12:
            return random.choice(["Grade 2", "Grade 2", "Grade 3"])
        elif length_km >= 2.5:
            return random.choice(["Grade 3", "Not Graded"])
        else:
            return "Not Graded"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_circuit_generator = RealisticCircuitGenerator()

def generate_realistic_circuit(discipline: Optional[str] = None) -> CircuitData:
    """Generate a realistic circuit for the given discipline"""
    return _circuit_generator.generate_circuit(discipline=discipline)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("Realistic Circuit Generator - Examples")
    print("=" * 80)
    
    # Generate single seater circuits
    print("\nSingle Seater Circuits:")
    for i in range(5):
        circuit = generate_realistic_circuit("SINGLE_SEATER")
        print(f"\n{i+1}. {circuit.name}")
        print(f"   Location: {circuit.city}, {circuit.country}")
        print(f"   Type: {circuit.circuit_type.value} | Surface: {circuit.surface.value}")
        print(f"   Length: {circuit.length_km}km | Turns: {circuit.turns}")
        print(f"   Elevation: {circuit.elevation_change_m}m | Max Gradient: {circuit.max_gradient_percent}%")
        print(f"   Climate: {circuit.climate.value} | Avg Temp: {circuit.average_temp_c}°C")
        print(f"   FIA Grade: {circuit.fia_grade}")
    
    # Generate rally circuits
    print("\n" + "=" * 80)
    print("\nRally Stage Circuits:")
    for i in range(3):
        circuit = generate_realistic_circuit("RALLY_STAGE")
        print(f"\n{i+1}. {circuit.name}")
        print(f"   Location: {circuit.city}, {circuit.country}")
        print(f"   Type: {circuit.circuit_type.value} | Surface: {circuit.surface.value}")
        print(f"   Length: {circuit.length_km}km | Elevation: {circuit.elevation_change_m}m")
        print(f"   Rally Suitability: {circuit.rally_suitability:.2f}")
