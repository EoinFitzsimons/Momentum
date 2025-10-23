"""
Comprehensive Racing Circuit Generator - Momentum Motorsport

Generates 100+ unique, original racing circuits with:
- No real-world track names (completely fictional)
- Detailed technical specifications per discipline
- Climate and environmental factors
- Active/inactive calendar system for year-to-year variety
- Custom governing body grading system (IMA - International Motorsport Authority)

Each discipline gets 20-30 circuits to rotate through seasons.
"""

import random
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum

# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class CircuitType(Enum):
    """Types of circuit layouts"""
    PERMANENT = "permanent"
    STREET = "street"
    ROAD_COURSE = "road_course"
    OVAL = "oval"
    MIXED = "mixed"


class SurfaceType(Enum):
    """Racing surface types"""
    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    GRAVEL = "gravel"
    DIRT = "dirt"
    TARMAC = "tarmac"
    MIXED_SURFACE = "mixed"


class Climate(Enum):
    """Climate zones"""
    TEMPERATE = "temperate"
    TROPICAL = "tropical"
    DESERT = "desert"
    MEDITERRANEAN = "mediterranean"
    CONTINENTAL = "continental"
    ALPINE = "alpine"
    COASTAL = "coastal"


@dataclass
class CircuitSpecification:
    """Complete circuit data for the simulation"""
    # Identity
    circuit_id: int
    name: str
    country: str
    region: str
    
    # Classification
    circuit_type: str
    ima_grade: str  # IMA = International Motorsport Authority (fictional)
    primary_discipline: str
    
    # Technical specs
    length_km: float
    turns: int
    left_turns: int
    right_turns: int
    elevation_change_m: float
    max_gradient_percent: float
    min_gradient_percent: float
    
    # Track characteristics
    surface: str
    avg_speed_kmh: float
    top_speed_kmh: float
    longest_straight_m: float
    shortest_straight_m: float
    tightest_corner_radius_m: float
    track_width_avg_m: float
    track_width_min_m: float
    track_width_max_m: float
    
    # Environmental
    climate: str
    avg_temp_summer_c: float
    avg_temp_winter_c: float
    rainfall_mm_annual: int
    altitude_m: int
    
    # Facilities
    pit_boxes: int
    pit_lane_length_m: float
    pit_speed_limit_kmh: int
    paddock_capacity_teams: int
    grandstand_capacity: int
    
    # Racing features
    drs_zones: int  # Overtaking zones
    safety_car_probability: float
    night_racing_capable: bool
    wet_weather_racing: bool
    
    # Calendar system
    is_active: bool
    debut_year: int
    last_used_year: Optional[int]
    

# ============================================================================
# CIRCUIT NAME GENERATION COMPONENTS
# Massive variety - no repetition
# ============================================================================

# Unique location prefixes (200+ unique combinations)
CIRCUIT_PREFIXES_A = [
    # European-inspired (50)
    "Aldermoor", "Blackstone", "Clearwater", "Deepford", "Eastmarch",
    "Fairhaven", "Goldcrest", "Highbridge", "Ironspire", "Kingsgate",
    "Lionheart", "Moorfield", "Northvale", "Oakenshield", "Pinecrest",
    "Queenshold", "Redstone", "Silverwind", "Thornhill", "Westbrook",
    "Ashford", "Bellcrest", "Crosswell", "Dawnshire", "Elmwood",
    "Frostpeak", "Greendale", "Havenport", "Ivywood", "Jadecliff",
    "Kelvin", "Larkspur", "Millbrook", "Newbridge", "Oldgate",
    "Palmhurst", "Quarryhill", "Ravenwood", "Stormhold", "Tidehaven",
    "Underhill", "Valleyford", "Whitestone", "Yarmouth", "Zenwick",
    "Bramford", "Crestmere", "Duskwood", "Eagleton", "Fallcrest",
    
    # Latin-inspired (30)
    "Altavista", "Bellaverde", "Castellano", "Dolorosa", "Esperanza",
    "Fontanella", "Girasole", "Hermosa", "Isola", "Luminara",
    "Maravilla", "Novara", "Oriente", "Portofino", "Quieta",
    "Rosario", "Salvatore", "Terranova", "Ultimare", "Valentia",
    "Azurra", "Bonita", "Carmina", "Divina", "Encanto",
    "Fortezza", "Grandeza", "Horizonte", "Infinita", "Joya",
    
    # Asian-inspired romanized (30)
    "Akatsuki", "Bokuden", "Chikara", "Daichi", "Eikou",
    "Fujimura", "Genki", "Haruka", "Ikari", "Jinrai",
    "Kokoro", "Lumina", "Midori", "Noboru", "Okari",
    "Raijin", "Sakurada", "Takara", "Uzumaki", "Wakaba",
    "Yamato", "Zenkou", "Ashura", "Byakko", "Crimson",
    "Doragon", "Enma", "Fubuki", "Gekko", "Heiwa",
    
    # Middle Eastern-inspired (25)
    "Alamein", "Bahrami", "Caspar", "Daleel", "Elysara",
    "Fahreed", "Ghazali", "Hadara", "Ishkar", "Jazirah",
    "Kashan", "Lazuli", "Marakesh", "Nazari", "Omarr",
    "Pasha", "Qatara", "Rasheed", "Sahir", "Talaal",
    "Umara", "Vazir", "Waseem", "Xerxes", "Zahir",
    
    # Modern/Abstract (30)
    "Apex", "Beacon", "Catalyst", "Dynamo", "Eclipse",
    "Fusion", "Genesis", "Helios", "Ignition", "Kinetic",
    "Luminos", "Matrix", "Nexus", "Orbital", "Polaris",
    "Quantum", "Radiance", "Sector", "Thrust", "Unity",
    "Vertex", "Waveform", "Xenon", "Yonder", "Zenith",
    "Aether", "Blaze", "Cipher", "Dynex", "Ember",
    
    # Nordic-inspired (25)
    "Bjornstad", "Dalvik", "Eriksund", "Fjordheim", "Grindval",
    "Hafnir", "Isvik", "Jarvik", "Kaldfjord", "Lindholm",
    "Mjolnir", "Nordvast", "Odinstal", "Polarcrest", "Roarvik",
    "Skulstad", "Thorsheim", "Ustvold", "Vatnborg", "Winterpeak",
    "Ylvinge", "Zornak", "Aldric", "Bergstrom", "Carlsen"
]

CIRCUIT_SUFFIXES = [
    # Traditional
    "Circuit", "Raceway", "Speedway", "Park", "Arena",
    "Track", "Complex", "Ring", "Course", "Loop",
    
    # International variants
    "Autodrome", "Autodromo", "Circuito", "Piste",
    "Rennstrecke", "Autobahn", "Velocita", "Corso",
    
    # Modern
    "Motorsports", "Racing Center", "Grand Prix Circuit",
    "International Circuit", "Motor Stadium", "Racing Arena",
    
    # Descriptive
    "Street Circuit", "Road Course", "Sprint Track",
    "Endurance Circuit", "Rally Stage", "Mountain Pass"
]

# Regional descriptors for variety
REGIONAL_DESCRIPTORS = [
    "", "North", "South", "East", "West", "Central", "Greater",
    "Royal", "International", "Grand", "Imperial", "National"
]

# ============================================================================
# LOCATION DATABASE (100+ unique locations)
# ============================================================================

GLOBAL_LOCATIONS = [
    # Europe (30)
    {"country": "Italy", "regions": ["Lombardia", "Tuscana", "Sicilia", "Veneto"]},
    {"country": "France", "regions": ["Provence", "Aquitaine", "Brittany", "Alsace"]},
    {"country": "Spain", "regions": ["Catalonia", "Andalusia", "Valencia", "Galicia"]},
    {"country": "Germany", "regions": ["Bavaria", "Saxony", "Rhineland", "Brandenburg"]},
    {"country": "United Kingdom", "regions": ["Yorkshire", "Cornwall", "Highlands", "Midlands"]},
    {"country": "Belgium", "regions": ["Flanders", "Wallonia", "Ardennes", "Brabant"]},
    {"country": "Netherlands", "regions": ["Zeeland", "Friesland", "Gelderland", "Utrecht"]},
    {"country": "Austria", "regions": ["Tyrol", "Salzburg", "Styria", "Carinthia"]},
    {"country": "Switzerland", "regions": ["Valais", "Graubünden", "Ticino", "Bern"]},
    {"country": "Portugal", "regions": ["Algarve", "Douro", "Lisbon", "Madeira"]},
    
    # Americas (25)
    {"country": "United States", "regions": ["California", "Texas", "Florida", "Nevada", "Arizona"]},
    {"country": "Canada", "regions": ["Quebec", "Ontario", "British Columbia", "Alberta"]},
    {"country": "Mexico", "regions": ["Baja", "Yucatan", "Jalisco", "Veracruz"]},
    {"country": "Brazil", "regions": ["São Paulo", "Rio", "Bahia", "Minas Gerais"]},
    {"country": "Argentina", "regions": ["Buenos Aires", "Patagonia", "Mendoza", "Córdoba"]},
    {"country": "Chile", "regions": ["Atacama", "Santiago", "Valparaíso", "Araucanía"]},
    
    # Asia (25)
    {"country": "Japan", "regions": ["Kanto", "Kansai", "Hokkaido", "Kyushu"]},
    {"country": "South Korea", "regions": ["Gyeonggi", "Jeolla", "Gangwon", "Jeju"]},
    {"country": "China", "regions": ["Guangdong", "Zhejiang", "Sichuan", "Yunnan"]},
    {"country": "Singapore", "regions": ["Central", "Marina Bay", "Sentosa", "Changi"]},
    {"country": "Malaysia", "regions": ["Selangor", "Penang", "Sabah", "Johor"]},
    {"country": "Thailand", "regions": ["Bangkok", "Phuket", "Chiang Mai", "Pattaya"]},
    {"country": "India", "regions": ["Maharashtra", "Karnataka", "Tamil Nadu", "Rajasthan"]},
    
    # Middle East (15)
    {"country": "United Arab Emirates", "regions": ["Abu Dhabi", "Dubai", "Sharjah", "Fujairah"]},
    {"country": "Bahrain", "regions": ["Manama", "Riffa", "Muharraq", "Sakhir"]},
    {"country": "Saudi Arabia", "regions": ["Riyadh", "Jeddah", "Eastern", "Mecca"]},
    {"country": "Qatar", "regions": ["Doha", "Al Wakrah", "Al Khor", "Lusail"]},
    
    # Oceania (10)
    {"country": "Australia", "regions": ["Victoria", "New South Wales", "Queensland", "Tasmania"]},
    {"country": "New Zealand", "regions": ["Auckland", "Canterbury", "Otago", "Waikato"]},
    
    # Africa (10)
    {"country": "South Africa", "regions": ["Western Cape", "Gauteng", "KwaZulu-Natal", "Eastern Cape"]},
    {"country": "Morocco", "regions": ["Casablanca", "Marrakech", "Tangier", "Fes"]},
]

# ============================================================================
# IMA GRADING SYSTEM (International Motorsport Authority)
# Our fictional governing body for motorsport safety and standards
# ============================================================================

IMA_GRADES = {
    "Diamond": "Highest grade - suitable for world championship events",
    "Platinum": "Premium grade - international competition standard",
    "Gold": "High grade - national championship level",
    "Silver": "Standard grade - professional racing",
    "Bronze": "Entry grade - regional competition",
    "Approved": "Basic certification - grassroots racing"
}

# ============================================================================
# CIRCUIT GENERATOR
# ============================================================================

class ComprehensiveCircuitGenerator:
    """Generates large variety of unique circuits for all disciplines"""
    
    def __init__(self):
        self.used_names = set()
        self.circuits_by_discipline = {
            "SINGLE_SEATER": [],
            "RALLY_STAGE": [],
            "ENDURANCE": [],
            "PRODUCTION_TOURING": [],
            "URBAN_STREET": [],
            "DRAG_ACCELERATION": [],
            "SPRINT_RALLYCROSS": []
        }
        self.next_id = 1
    
    def _generate_unique_name(self) -> str:
        """Generate a completely unique circuit name"""
        max_attempts = 200
        
        for _ in range(max_attempts):
            # Select components
            prefix = random.choice(CIRCUIT_PREFIXES_A)
            suffix = random.choice(CIRCUIT_SUFFIXES)
            descriptor = random.choice(REGIONAL_DESCRIPTORS)
            
            # Construct name (various patterns)
            patterns = [
                f"{prefix} {suffix}",
                f"{descriptor} {prefix} {suffix}" if descriptor else f"{prefix} {suffix}",
                f"{prefix} {suffix}" if random.random() < 0.7 else f"{prefix} International {suffix}",
            ]
            
            name = random.choice(patterns).strip()
            
            # Clean up double spaces
            name = " ".join(name.split())
            
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        
        # Ultimate fallback
        fallback = f"{random.choice(CIRCUIT_PREFIXES_A)} Circuit {random.randint(100, 999)}"
        self.used_names.add(fallback)
        return fallback
    
    def _select_location(self) -> Dict:
        """Select a random location"""
        loc = random.choice(GLOBAL_LOCATIONS)
        return {
            "country": loc["country"],
            "region": random.choice(loc["regions"])
        }
    
    def _determine_climate(self, country: str, region: str) -> Climate:
        """Determine climate based on location"""
        # Simplified climate mapping
        tropical_countries = ["Brazil", "Singapore", "Malaysia", "Thailand"]
        desert_countries = ["United Arab Emirates", "Saudi Arabia", "Qatar", "Bahrain"]
        mediterranean_countries = ["Italy", "Spain", "Portugal", "Morocco"]
        alpine_regions = ["Tyrol", "Bavaria", "Graubünden"]
        
        if country in tropical_countries:
            return Climate.TROPICAL
        elif country in desert_countries:
            return Climate.DESERT
        elif country in mediterranean_countries:
            return Climate.MEDITERRANEAN
        elif region in alpine_regions:
            return Climate.ALPINE
        elif "coast" in region.lower() or "bay" in region.lower():
            return Climate.COASTAL
        elif country in ["Canada", "Germany", "Austria"]:
            return Climate.CONTINENTAL
        else:
            return Climate.TEMPERATE
    
    def generate_circuit_for_discipline(
        self,
        discipline: str,
        is_active: bool = True,
        debut_year: int = 2020
    ) -> CircuitSpecification:
        """Generate a circuit optimized for a specific discipline"""
        
        # Get location
        location = self._select_location()
        country = location["country"]
        region = location["region"]
        climate = self._determine_climate(country, region)
        
        # Generate name
        name = self._generate_unique_name()
        
        # Discipline-specific specs
        if discipline == "SINGLE_SEATER":
            specs = self._generate_single_seater_specs()
        elif discipline == "RALLY_STAGE":
            specs = self._generate_rally_specs()
        elif discipline == "ENDURANCE":
            specs = self._generate_endurance_specs()
        elif discipline == "PRODUCTION_TOURING":
            specs = self._generate_touring_specs()
        elif discipline == "URBAN_STREET":
            specs = self._generate_street_specs()
        elif discipline == "DRAG_ACCELERATION":
            specs = self._generate_drag_specs()
        elif discipline == "SPRINT_RALLYCROSS":
            specs = self._generate_rallycross_specs()
        else:
            specs = self._generate_default_specs()
        
        # Environmental data
        env_data = self._generate_environmental_data(climate)
        
        # Create circuit
        circuit = CircuitSpecification(
            circuit_id=self.next_id,
            name=name,
            country=country,
            region=region,
            circuit_type=specs["circuit_type"],
            ima_grade=specs["ima_grade"],
            primary_discipline=discipline,
            length_km=specs["length_km"],
            turns=specs["turns"],
            left_turns=specs["left_turns"],
            right_turns=specs["right_turns"],
            elevation_change_m=specs["elevation_change_m"],
            max_gradient_percent=specs["max_gradient_percent"],
            min_gradient_percent=specs["min_gradient_percent"],
            surface=specs["surface"],
            avg_speed_kmh=specs["avg_speed_kmh"],
            top_speed_kmh=specs["top_speed_kmh"],
            longest_straight_m=specs["longest_straight_m"],
            shortest_straight_m=specs["shortest_straight_m"],
            tightest_corner_radius_m=specs["tightest_corner_radius_m"],
            track_width_avg_m=specs["track_width_avg_m"],
            track_width_min_m=specs["track_width_min_m"],
            track_width_max_m=specs["track_width_max_m"],
            climate=climate.value,
            avg_temp_summer_c=env_data["summer_temp"],
            avg_temp_winter_c=env_data["winter_temp"],
            rainfall_mm_annual=env_data["rainfall"],
            altitude_m=env_data["altitude"],
            pit_boxes=specs["pit_boxes"],
            pit_lane_length_m=specs["pit_lane_length_m"],
            pit_speed_limit_kmh=specs["pit_speed_limit_kmh"],
            paddock_capacity_teams=specs["paddock_capacity"],
            grandstand_capacity=specs["grandstand_capacity"],
            drs_zones=specs["drs_zones"],
            safety_car_probability=specs["safety_car_probability"],
            night_racing_capable=specs["night_racing_capable"],
            wet_weather_racing=specs["wet_weather_racing"],
            is_active=is_active,
            debut_year=debut_year,
            last_used_year=None if is_active else random.randint(2018, 2023)
        )
        
        self.circuits_by_discipline[discipline].append(circuit)
        self.next_id += 1
        return circuit
    
    def _generate_single_seater_specs(self) -> Dict:
        """Generate specs for single seater racing"""
        circuit_type = random.choice([CircuitType.PERMANENT, CircuitType.STREET, CircuitType.PERMANENT, CircuitType.PERMANENT])
        
        if circuit_type == CircuitType.STREET:
            length = round(random.uniform(3.8, 6.2), 2)
            turns = random.randint(16, 23)
        else:
            length = round(random.uniform(4.5, 7.0), 2)
            turns = random.randint(12, 20)
        
        left = random.randint(int(turns * 0.35), int(turns * 0.65))
        right = turns - left
        
        return {
            "circuit_type": circuit_type.value,
            "ima_grade": random.choice(["Diamond", "Diamond", "Platinum", "Gold"]),
            "length_km": length,
            "turns": turns,
            "left_turns": left,
            "right_turns": right,
            "elevation_change_m": round(random.uniform(25, 110), 1),
            "max_gradient_percent": round(random.uniform(8, 18), 1),
            "min_gradient_percent": round(random.uniform(-12, -3), 1),
            "surface": SurfaceType.ASPHALT.value,
            "avg_speed_kmh": round(random.uniform(195, 235), 1),
            "top_speed_kmh": round(random.uniform(310, 360), 1),
            "longest_straight_m": random.randint(850, 1800),
            "shortest_straight_m": random.randint(120, 250),
            "tightest_corner_radius_m": round(random.uniform(35, 85), 1),
            "track_width_avg_m": round(random.uniform(12, 16), 1),
            "track_width_min_m": round(random.uniform(9, 12), 1),
            "track_width_max_m": round(random.uniform(18, 25), 1),
            "pit_boxes": random.randint(24, 40),
            "pit_lane_length_m": round(random.uniform(350, 550), 1),
            "pit_speed_limit_kmh": random.choice([60, 80, 100]),
            "paddock_capacity": random.randint(28, 45),
            "grandstand_capacity": random.randint(45000, 150000),
            "drs_zones": random.randint(2, 3),
            "safety_car_probability": round(random.uniform(0.15, 0.35), 2),
            "night_racing_capable": random.choice([True, False]),
            "wet_weather_racing": True
        }
    
    def _generate_rally_specs(self) -> Dict:
        """Generate specs for rally racing"""
        return {
            "circuit_type": CircuitType.ROAD_COURSE.value,
            "ima_grade": random.choice(["Gold", "Silver", "Approved"]),
            "length_km": round(random.uniform(8.0, 35.0), 2),
            "turns": random.randint(45, 120),
            "left_turns": random.randint(20, 60),
            "right_turns": random.randint(25, 60),
            "elevation_change_m": round(random.uniform(180, 650), 1),
            "max_gradient_percent": round(random.uniform(15, 35), 1),
            "min_gradient_percent": round(random.uniform(-18, -8), 1),
            "surface": random.choice([SurfaceType.GRAVEL.value, SurfaceType.DIRT.value, SurfaceType.MIXED_SURFACE.value]),
            "avg_speed_kmh": round(random.uniform(85, 140), 1),
            "top_speed_kmh": round(random.uniform(180, 220), 1),
            "longest_straight_m": random.randint(650, 1200),
            "shortest_straight_m": random.randint(40, 90),
            "tightest_corner_radius_m": round(random.uniform(12, 35), 1),
            "track_width_avg_m": round(random.uniform(6, 9), 1),
            "track_width_min_m": round(random.uniform(4.5, 6.5), 1),
            "track_width_max_m": round(random.uniform(10, 14), 1),
            "pit_boxes": random.randint(8, 16),
            "pit_lane_length_m": round(random.uniform(150, 300), 1),
            "pit_speed_limit_kmh": 40,
            "paddock_capacity": random.randint(12, 24),
            "grandstand_capacity": random.randint(8000, 35000),
            "drs_zones": 0,
            "safety_car_probability": round(random.uniform(0.05, 0.15), 2),
            "night_racing_capable": False,
            "wet_weather_racing": True
        }
    
    def _generate_endurance_specs(self) -> Dict:
        """Generate specs for endurance racing"""
        return {
            "circuit_type": random.choice([CircuitType.PERMANENT.value, CircuitType.ROAD_COURSE.value]),
            "ima_grade": random.choice(["Diamond", "Platinum", "Gold"]),
            "length_km": round(random.uniform(5.5, 13.5), 2),
            "turns": random.randint(18, 42),
            "left_turns": random.randint(8, 22),
            "right_turns": random.randint(10, 20),
            "elevation_change_m": round(random.uniform(45, 180), 1),
            "max_gradient_percent": round(random.uniform(10, 20), 1),
            "min_gradient_percent": round(random.uniform(-14, -5), 1),
            "surface": SurfaceType.ASPHALT.value,
            "avg_speed_kmh": round(random.uniform(180, 220), 1),
            "top_speed_kmh": round(random.uniform(300, 345), 1),
            "longest_straight_m": random.randint(1200, 2500),
            "shortest_straight_m": random.randint(100, 220),
            "tightest_corner_radius_m": round(random.uniform(25, 70), 1),
            "track_width_avg_m": round(random.uniform(13, 18), 1),
            "track_width_min_m": round(random.uniform(10, 13), 1),
            "track_width_max_m": round(random.uniform(20, 28), 1),
            "pit_boxes": random.randint(40, 65),
            "pit_lane_length_m": round(random.uniform(450, 750), 1),
            "pit_speed_limit_kmh": 60,
            "paddock_capacity": random.randint(50, 80),
            "grandstand_capacity": random.randint(60000, 180000),
            "drs_zones": random.randint(3, 5),
            "safety_car_probability": round(random.uniform(0.25, 0.45), 2),
            "night_racing_capable": random.choice([True, True, False]),
            "wet_weather_racing": True
        }
    
    def _generate_touring_specs(self) -> Dict:
        """Generate specs for touring car racing"""
        return {
            "circuit_type": CircuitType.PERMANENT.value,
            "ima_grade": random.choice(["Platinum", "Gold", "Silver"]),
            "length_km": round(random.uniform(3.2, 5.5), 2),
            "turns": random.randint(10, 18),
            "left_turns": random.randint(4, 10),
            "right_turns": random.randint(6, 10),
            "elevation_change_m": round(random.uniform(20, 75), 1),
            "max_gradient_percent": round(random.uniform(6, 14), 1),
            "min_gradient_percent": round(random.uniform(-10, -4), 1),
            "surface": SurfaceType.ASPHALT.value,
            "avg_speed_kmh": round(random.uniform(160, 195), 1),
            "top_speed_kmh": round(random.uniform(260, 295), 1),
            "longest_straight_m": random.randint(700, 1300),
            "shortest_straight_m": random.randint(90, 180),
            "tightest_corner_radius_m": round(random.uniform(30, 65), 1),
            "track_width_avg_m": round(random.uniform(11, 14), 1),
            "track_width_min_m": round(random.uniform(9, 11), 1),
            "track_width_max_m": round(random.uniform(16, 22), 1),
            "pit_boxes": random.randint(28, 42),
            "pit_lane_length_m": round(random.uniform(300, 450), 1),
            "pit_speed_limit_kmh": 60,
            "paddock_capacity": random.randint(32, 50),
            "grandstand_capacity": random.randint(35000, 80000),
            "drs_zones": 0,
            "safety_car_probability": round(random.uniform(0.20, 0.40), 2),
            "night_racing_capable": random.choice([True, False]),
            "wet_weather_racing": True
        }
    
    def _generate_street_specs(self) -> Dict:
        """Generate specs for urban street racing"""
        return {
            "circuit_type": CircuitType.STREET.value,
            "ima_grade": random.choice(["Gold", "Silver"]),
            "length_km": round(random.uniform(2.8, 5.8), 2),
            "turns": random.randint(14, 26),
            "left_turns": random.randint(6, 14),
            "right_turns": random.randint(8, 14),
            "elevation_change_m": round(random.uniform(12, 68), 1),
            "max_gradient_percent": round(random.uniform(5, 15), 1),
            "min_gradient_percent": round(random.uniform(-12, -4), 1),
            "surface": SurfaceType.ASPHALT.value,
            "avg_speed_kmh": round(random.uniform(165, 205), 1),
            "top_speed_kmh": round(random.uniform(280, 320), 1),
            "longest_straight_m": random.randint(600, 1100),
            "shortest_straight_m": random.randint(70, 140),
            "tightest_corner_radius_m": round(random.uniform(20, 50), 1),
            "track_width_avg_m": round(random.uniform(10, 13), 1),
            "track_width_min_m": round(random.uniform(7.5, 10), 1),
            "track_width_max_m": round(random.uniform(15, 19), 1),
            "pit_boxes": random.randint(18, 28),
            "pit_lane_length_m": round(random.uniform(250, 400), 1),
            "pit_speed_limit_kmh": 60,
            "paddock_capacity": random.randint(20, 32),
            "grandstand_capacity": random.randint(25000, 75000),
            "drs_zones": random.randint(1, 2),
            "safety_car_probability": round(random.uniform(0.30, 0.55), 2),
            "night_racing_capable": random.choice([True, True, True, False]),
            "wet_weather_racing": True
        }
    
    def _generate_drag_specs(self) -> Dict:
        """Generate specs for drag/acceleration racing"""
        return {
            "circuit_type": CircuitType.PERMANENT.value,
            "ima_grade": random.choice(["Gold", "Silver", "Bronze"]),
            "length_km": round(random.uniform(0.4, 2.0), 2),
            "turns": random.choice([0, 2, 4]),
            "left_turns": 0,
            "right_turns": 0,
            "elevation_change_m": round(random.uniform(2, 15), 1),
            "max_gradient_percent": round(random.uniform(0.5, 3), 1),
            "min_gradient_percent": round(random.uniform(-2, -0.2), 1),
            "surface": random.choice([SurfaceType.ASPHALT.value, SurfaceType.CONCRETE.value]),
            "avg_speed_kmh": round(random.uniform(250, 320), 1),
            "top_speed_kmh": round(random.uniform(380, 450), 1),
            "longest_straight_m": random.randint(400, 2000),
            "shortest_straight_m": random.randint(400, 1200),
            "tightest_corner_radius_m": 0.0,
            "track_width_avg_m": round(random.uniform(14, 20), 1),
            "track_width_min_m": round(random.uniform(12, 16), 1),
            "track_width_max_m": round(random.uniform(18, 24), 1),
            "pit_boxes": random.randint(16, 32),
            "pit_lane_length_m": round(random.uniform(200, 350), 1),
            "pit_speed_limit_kmh": 40,
            "paddock_capacity": random.randint(24, 40),
            "grandstand_capacity": random.randint(15000, 50000),
            "drs_zones": 0,
            "safety_car_probability": round(random.uniform(0.05, 0.15), 2),
            "night_racing_capable": random.choice([True, False]),
            "wet_weather_racing": False
        }
    
    def _generate_rallycross_specs(self) -> Dict:
        """Generate specs for sprint rallycross"""
        return {
            "circuit_type": CircuitType.MIXED.value,
            "ima_grade": random.choice(["Silver", "Bronze", "Approved"]),
            "length_km": round(random.uniform(0.8, 1.6), 2),
            "turns": random.randint(8, 16),
            "left_turns": random.randint(3, 8),
            "right_turns": random.randint(5, 10),
            "elevation_change_m": round(random.uniform(15, 45), 1),
            "max_gradient_percent": round(random.uniform(8, 18), 1),
            "min_gradient_percent": round(random.uniform(-12, -5), 1),
            "surface": SurfaceType.MIXED_SURFACE.value,
            "avg_speed_kmh": round(random.uniform(95, 145), 1),
            "top_speed_kmh": round(random.uniform(180, 230), 1),
            "longest_straight_m": random.randint(300, 650),
            "shortest_straight_m": random.randint(50, 120),
            "tightest_corner_radius_m": round(random.uniform(18, 40), 1),
            "track_width_avg_m": round(random.uniform(9, 12), 1),
            "track_width_min_m": round(random.uniform(7, 9), 1),
            "track_width_max_m": round(random.uniform(13, 17), 1),
            "pit_boxes": random.randint(12, 20),
            "pit_lane_length_m": round(random.uniform(120, 250), 1),
            "pit_speed_limit_kmh": 40,
            "paddock_capacity": random.randint(16, 28),
            "grandstand_capacity": random.randint(12000, 40000),
            "drs_zones": 0,
            "safety_car_probability": round(random.uniform(0.10, 0.25), 2),
            "night_racing_capable": random.choice([True, False]),
            "wet_weather_racing": True
        }
    
    def _generate_default_specs(self) -> Dict:
        """Fallback specs"""
        return self._generate_touring_specs()
    
    def _generate_environmental_data(self, climate: Climate) -> Dict:
        """Generate realistic environmental data based on climate"""
        climate_ranges = {
            Climate.MEDITERRANEAN: {"summer": (22, 32), "winter": (8, 16), "rain": (400, 800), "altitude": (0, 400)},
            Climate.TROPICAL: {"summer": (28, 35), "winter": (24, 30), "rain": (1500, 3000), "altitude": (0, 300)},
            Climate.DESERT: {"summer": (35, 48), "winter": (15, 25), "rain": (50, 200), "altitude": (0, 600)},
            Climate.TEMPERATE: {"summer": (18, 26), "winter": (2, 12), "rain": (600, 1100), "altitude": (0, 500)},
            Climate.CONTINENTAL: {"summer": (20, 30), "winter": (-5, 8), "rain": (500, 900), "altitude": (100, 700)},
            Climate.ALPINE: {"summer": (12, 22), "winter": (-8, 4), "rain": (800, 1600), "altitude": (800, 2200)},
            Climate.COASTAL: {"summer": (20, 28), "winter": (8, 16), "rain": (700, 1300), "altitude": (0, 200)},
        }
        
        ranges = climate_ranges.get(climate, climate_ranges[Climate.TEMPERATE])
        
        return {
            "summer_temp": round(random.uniform(*ranges["summer"]), 1),
            "winter_temp": round(random.uniform(*ranges["winter"]), 1),
            "rainfall": random.randint(*ranges["rain"]),
            "altitude": random.randint(*ranges["altitude"])
        }
    
    def generate_full_calendar(
        self,
        circuits_per_discipline: int = 25,
        active_percentage: float = 0.70
    ):
        """
        Generate complete circuit database for all disciplines.
        
        Args:
            circuits_per_discipline: Number of circuits to generate per discipline
            active_percentage: Percentage of circuits that are currently active
        """
        print(f"\nGenerating comprehensive circuit database...")
        print(f"  {circuits_per_discipline} circuits per discipline")
        print(f"  {active_percentage * 100}% active, {(1 - active_percentage) * 100}% inactive\n")
        
        for discipline in self.circuits_by_discipline.keys():
            print(f"Generating {discipline} circuits...")
            
            for i in range(circuits_per_discipline):
                # Determine if active
                is_active = random.random() < active_percentage
                
                # Debut year (spread across years)
                if is_active:
                    debut_year = random.randint(2010, 2024)
                else:
                    debut_year = random.randint(2005, 2020)
                
                circuit = self.generate_circuit_for_discipline(
                    discipline=discipline,
                    is_active=is_active,
                    debut_year=debut_year
                )
            
            active_count = sum(1 for c in self.circuits_by_discipline[discipline] if c.is_active)
            print(f"  ✓ {circuits_per_discipline} circuits ({active_count} active, {circuits_per_discipline - active_count} inactive)")
        
        print(f"\n✓ Total circuits generated: {self.next_id - 1}")
        print(f"  Unique names: {len(self.used_names)}")
    
    def export_to_json(self, filename: str = "circuits_database.json"):
        """Export all circuits to JSON"""
        all_circuits = []
        for circuits in self.circuits_by_discipline.values():
            all_circuits.extend([asdict(c) for c in circuits])
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_circuits, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Exported to {filename}")


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def generate_comprehensive_circuit_database(
    circuits_per_discipline: int = 25,
    output_file: str = "circuits_database.json"
):
    """Generate and export complete circuit database"""
    generator = ComprehensiveCircuitGenerator()
    generator.generate_full_calendar(circuits_per_discipline=circuits_per_discipline)
    generator.export_to_json(output_file)
    return generator


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE CIRCUIT GENERATOR - Momentum Motorsport")
    print("=" * 80)
    
    # Generate full database
    generator = generate_comprehensive_circuit_database(
        circuits_per_discipline=25,
        output_file="circuits_database.json"
    )
    
    # Show samples
    print("\n" + "=" * 80)
    print("SAMPLE CIRCUITS")
    print("=" * 80)
    
    for discipline, circuits in generator.circuits_by_discipline.items():
        print(f"\n{discipline} (showing first 3):")
        for circuit in circuits[:3]:
            print(f"  • {circuit.name}")
            print(f"    {circuit.region}, {circuit.country} | {circuit.ima_grade}")
            print(f"    {circuit.length_km}km, {circuit.turns} turns | {circuit.surface}")
            status = "🟢 ACTIVE" if circuit.is_active else "🔴 INACTIVE"
            print(f"    {status} | Debut: {circuit.debut_year}")
