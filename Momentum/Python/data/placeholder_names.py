"""
Momentum Motorsport Simulation - Placeholder Names and Entities

This file contains all placeholder names, teams, drivers, and championships
to avoid copyright issues while maintaining authenticity and immersion.
All names are fictional and any resemblance to real entities is coincidental.

Authors: Final Year Project - Computer Science
"""

from typing import Dict, List
from dataclasses import dataclass

# ============================================================================
# RACING DISCIPLINES (Placeholder Names)
# ============================================================================

DISCIPLINES = {
    "GPC": "Grand Prix Championship",           # Formula 1 equivalent
    "GPDC": "Grand Prix Development Championship",  # Formula 2 equivalent  
    "GPAC": "Grand Prix Academy Championship",      # Formula 3 equivalent
    "WEC": "World Endurance Championship",         # Keep generic name
    "WRC": "World Rally Championship",             # Keep generic name
    "MPG": "Motorcycle Premier Grand Prix",       # MotoGP equivalent
    "EGP": "Electric Grand Prix"                   # Formula E equivalent
}

DISCIPLINE_CODES = {
    "GPC": "gpc",
    "GPDC": "gpdc", 
    "GPAC": "gpac",
    "WEC": "wec",
    "WRC": "wrc",
    "MPG": "mpg",
    "EGP": "egp"
}

# ============================================================================
# FICTIONAL TEAM NAMES
# ============================================================================

TEAM_NAMES = {
    "GPC": [
        # Elite Tier (Top Teams)
        "Apex Racing", "Velocity Motorsports", "Phoenix Grand Prix", 
        "Thunder Racing Team", "Crimson Motorsport", "Azure Racing",
        "Sterling Grand Prix", "Nexus Racing", "Titan Motorsports",
        "Eclipse Racing Team",
        
        # Mid Tier
        "Lightning Racing", "Falcon Motorsport", "Storm Racing",
        "Vanguard Racing", "Pinnacle Motorsports", "Zenith Racing",
        
        # Lower Tier
        "Horizon Racing", "Meridian Motorsport", "Catalyst Racing",
        "Summit Racing Team"
    ],
    
    "GPDC": [
        "Academy Racing", "Future Stars Racing", "Rising Phoenix",
        "Next Gen Motorsport", "Talent Development Team", "Prospect Racing",
        "Elite Academy", "Championship Futures", "Star Racing Academy",
        "Premier Development", "Racing Pathways", "Victory Academy"
    ],
    
    "GPAC": [
        "Junior Stars", "Rookie Racing", "Academy Motorsport",
        "Youth Racing Team", "Development Stars", "Future Champions",
        "Cadet Racing", "Premier Academy", "Rising Talent",
        "Championship Academy", "Elite Juniors", "Victory Cadets"
    ],
    
    "WEC": [
        "Endurance Masters", "Marathon Racing", "Persistence Motorsport",
        "Long Distance Racing", "Stamina Racing Team", "Durability Motors",
        "24 Hour Racing", "Ultra Distance Team", "Endurance Elite",
        "Distance Champions", "Marathon Masters", "Persistence Racing"
    ],
    
    "WRC": [
        "Rally Masters", "Off-Road Racing", "Stage Racing Team",
        "Terrain Masters", "All-Surface Racing", "Rally Champions",
        "Cross-Country Racing", "Surface Specialists", "Rally Elite",
        "Terrain Racing", "Stage Masters", "Rally Professionals"
    ],
    
    "MPG": [
        "Motorcycle Masters", "Bike Racing Elite", "Two-Wheel Champions",
        "Speed Demons Racing", "Lean Angle Racing", "Motorcycle Legends",
        "Bike Masters Team", "Racing Motorcycles", "Elite Bike Racing",
        "Motorcycle Champions", "Two-Wheel Masters", "Speed Racing Team"
    ],
    
    "EGP": [
        "Electric Racing", "Voltage Motorsport", "E-Power Racing",
        "Clean Energy Racing", "Electric Elite", "Sustainable Racing",
        "Green Racing Team", "Electric Champions", "Eco Racing",
        "Zero Emission Racing", "Electric Masters", "Green Speed Team"
    ]
}

# ============================================================================
# FICTIONAL DRIVER NAMES
# ============================================================================

@dataclass
class DriverProfile:
    first_name: str
    last_name: str
    nationality: str
    age: int
    discipline_specialization: str

DRIVER_POOL = [
    # Elite GPC Drivers (F1 Level)
    DriverProfile("Alex", "Sterling", "GBR", 27, "GPC"),
    DriverProfile("Marco", "Veloce", "ITA", 24, "GPC"), 
    DriverProfile("Lucas", "Phoenix", "FRA", 29, "GPC"),
    DriverProfile("Kai", "Thunder", "JPN", 25, "GPC"),
    DriverProfile("Sebastian", "Crimson", "GER", 31, "GPC"),
    DriverProfile("Oscar", "Azure", "AUS", 23, "GPC"),
    DriverProfile("Carlos", "Nexus", "ESP", 28, "GPC"),
    DriverProfile("Max", "Titan", "NLD", 26, "GPC"),
    DriverProfile("Lewis", "Eclipse", "GBR", 32, "GPC"),
    DriverProfile("Charles", "Apex", "MON", 25, "GPC"),
    
    # Development Series Drivers (F2/F3 Level)
    DriverProfile("Oliver", "Rising", "GBR", 21, "GPDC"),
    DriverProfile("Theo", "Future", "FRA", 20, "GPDC"),
    DriverProfile("Felipe", "Academy", "BRA", 22, "GPDC"),
    DriverProfile("Jack", "Prospect", "AUS", 19, "GPDC"),
    DriverProfile("Dennis", "Elite", "NLD", 21, "GPDC"),
    DriverProfile("Victor", "Champion", "DEN", 20, "GPDC"),
    DriverProfile("Arthur", "Victory", "FRA", 18, "GPAC"),
    DriverProfile("Zane", "Cadet", "USA", 17, "GPAC"),
    DriverProfile("Ryan", "Junior", "IRL", 18, "GPAC"),
    DriverProfile("Leo", "Rookie", "FIN", 19, "GPAC"),
    
    # Endurance Specialists
    DriverProfile("Andre", "Marathon", "FRA", 34, "WEC"),
    DriverProfile("Tom", "Endurance", "GBR", 29, "WEC"),
    DriverProfile("Pierre", "Distance", "FRA", 31, "WEC"),
    DriverProfile("Mike", "Stamina", "USA", 33, "WEC"),
    
    # Rally Drivers
    DriverProfile("Erik", "Terrain", "SWE", 28, "WRC"),
    DriverProfile("Henri", "Surface", "FIN", 30, "WRC"),
    DriverProfile("Diego", "Cross", "ESP", 26, "WRC"),
    DriverProfile("Petter", "Rally", "NOR", 32, "WRC"),
    
    # Motorcycle Racers
    DriverProfile("Valentino", "Speed", "ITA", 28, "MPG"),
    DriverProfile("Marc", "Lean", "ESP", 25, "MPG"),
    DriverProfile("Casey", "Angle", "AUS", 29, "MPG"),
    DriverProfile("Jorge", "Bike", "ESP", 27, "MPG"),
    
    # Electric Racing Drivers
    DriverProfile("Sam", "Voltage", "GBR", 26, "EGP"),
    DriverProfile("Nick", "Electric", "USA", 24, "EGP"),
    DriverProfile("Jean", "Green", "FRA", 27, "EGP"),
    DriverProfile("Antonio", "Eco", "ITA", 25, "EGP")
]

# ============================================================================
# FICTIONAL TRACK NAMES AND LOCATIONS
# ============================================================================

TRACK_NAMES = {
    "GPC": [
        # Circuit Tracks
        {"name": "Apex International Circuit", "location": "Silverton", "country": "Britannia"},
        {"name": "Phoenix Grand Prix Circuit", "location": "Monaco Bay", "country": "Riviera"},
        {"name": "Thunder Valley Circuit", "location": "Speedway City", "country": "Americana"},
        {"name": "Azure Coast Circuit", "location": "Blue Harbor", "country": "Mediterra"},
        {"name": "Crimson Hills Circuit", "location": "Red Valley", "country": "Germania"},
        {"name": "Velocity Park Circuit", "location": "Motor City", "country": "Italia"},
        {"name": "Sterling Ring", "location": "Crown City", "country": "Britannia"},
        {"name": "Nexus Speedway", "location": "Tech Valley", "country": "Futura"},
        {"name": "Eclipse Circuit", "location": "Shadow Hills", "country": "Nordica"},
        {"name": "Titan Raceway", "location": "Steel City", "country": "Industria"}
    ],
    
    "WEC": [
        # Endurance Tracks
        {"name": "Marathon International Circuit", "location": "Le Circuit", "country": "Gallia"},
        {"name": "Endurance Valley", "location": "Long Beach", "country": "Americana"},
        {"name": "24 Hour Circuit", "location": "Daylight City", "country": "Germania"},
        {"name": "Distance Masters Track", "location": "Far Valley", "country": "Nordica"}
    ],
    
    "WRC": [
        # Rally Stages
        {"name": "Forest Masters Stage", "location": "Pine Valley", "country": "Nordica"},
        {"name": "Mountain Rally Stage", "location": "High Peaks", "country": "Alpina"},
        {"name": "Desert Cross Stage", "location": "Sand Dunes", "country": "Saharia"},
        {"name": "Coastal Rally Stage", "location": "Sea Cliffs", "country": "Oceanica"}
    ],
    
    "MPG": [
        # Motorcycle Circuits
        {"name": "Speed Demon Circuit", "location": "Fast City", "country": "Velocia"},
        {"name": "Lean Angle Track", "location": "Curve Valley", "country": "Bendica"},
        {"name": "Two-Wheel Speedway", "location": "Bike Town", "country": "Motorcity"},
        {"name": "Racing Thunder Circuit", "location": "Sound Valley", "country": "Acoustica"}
    ],
    
    "EGP": [
        # Electric Racing Circuits
        {"name": "Voltage Street Circuit", "location": "Electric City", "country": "Futura"},
        {"name": "Green Energy Track", "location": "Eco Valley", "country": "Sustainia"},
        {"name": "Zero Emission Circuit", "location": "Clean City", "country": "Purica"},
        {"name": "E-Power Speedway", "location": "Battery Bay", "country": "Electronia"}
    ]
}

# ============================================================================
# FICTIONAL COUNTRIES AND NATIONALITIES
# ============================================================================

FICTIONAL_COUNTRIES = {
    "GBR": "Britannia",      # UK equivalent
    "USA": "Americana",      # USA equivalent
    "ITA": "Italia",         # Italy equivalent
    "FRA": "Gallia",         # France equivalent
    "GER": "Germania",       # Germany equivalent
    "ESP": "Hispania",       # Spain equivalent
    "JPN": "Nippon",         # Japan equivalent
    "AUS": "Australis",      # Australia equivalent
    "NLD": "Hollandia",      # Netherlands equivalent
    "BRA": "Brasilia",       # Brazil equivalent
    "CAN": "Canadia",        # Canada equivalent
    "MEX": "Mexicana",       # Mexico equivalent
    "SWE": "Nordica",        # Sweden/Nordic equivalent
    "FIN": "Finlandia",      # Finland equivalent
    "NOR": "Norvegia",       # Norway equivalent
    "DEN": "Dania",          # Denmark equivalent
    "BEL": "Belgica",        # Belgium equivalent
    "SUI": "Helvetia",       # Switzerland equivalent
    "AUT": "Austria",        # Austria equivalent
    "MON": "Riviera"         # Monaco equivalent
}

# ============================================================================
# CHAMPIONSHIP NAMES
# ============================================================================

CHAMPIONSHIP_NAMES = {
    "GPC": "Global Premier Championship",
    "GPDC": "Global Premier Development Series", 
    "GPAC": "Global Premier Academy Series",
    "WEC": "World Endurance Series",
    "WRC": "World Rally Series",
    "MPG": "Motorcycle Premier Global Series",
    "EGP": "Electric Grand Prix Series"
}

# ============================================================================
# MANUFACTURER/ENGINE SUPPLIER NAMES
# ============================================================================

ENGINE_SUPPLIERS = {
    "GPC": ["PowerTech", "VelocityMotors", "TurboMax", "SpeedForce", "RacingPower"],
    "GPDC": ["DevelopmentPower", "AcademyMotors", "RisingForce", "FutureTech"],
    "GPAC": ["JuniorPower", "CadetMotors", "AcademyTech", "RookieForce"],
    "WEC": ["EnduranceTech", "MarathonPower", "DistanceMotors", "StaminaForce"],
    "WRC": ["RallyTech", "TerrainPower", "OffRoadMotors", "StageForce"],
    "MPG": ["BikeMax", "TwoWheelPower", "MotorcycleTech", "SpeedBike"],
    "EGP": ["ElectricMax", "VoltageMotors", "GreenTech", "EcoPower"]
}

TIRE_SUPPLIERS = [
    "GripMax", "TractionTech", "SpeedGrip", "RacingRubber", 
    "PerformanceTire", "UltraGrip", "RaceTech", "SpeedCompound"
]

FUEL_SUPPLIERS = [
    "RacingFuel", "PerformanceOil", "SpeedEnergy", "TurboFuel",
    "RaceMax", "VelocityFuel", "PowerPlus", "UltraFuel"
]

# ============================================================================
# MEDIA AND SPONSOR NAMES
# ============================================================================

MEDIA_OUTLETS = [
    "Racing Today", "Motorsport Weekly", "Speed Central", "Racing News Network",
    "Grand Prix Times", "Racing World", "Motorsport Central", "Speed Report",
    "Racing Tribune", "Championship News", "Velocity Media", "Racing Channel"
]

SPONSOR_CATEGORIES = {
    "technology": ["TechMax", "DataForce", "CyberSpeed", "DigitalRacing"],
    "energy": ["PowerMax", "EnergyPlus", "FuelTech", "SpeedEnergy"],
    "automotive": ["MotorTech", "AutoMax", "CarForce", "VehiclePlus"],
    "finance": ["RacingBank", "SpeedFinance", "VelocityCapital", "TurboCredit"],
    "apparel": ["RacingWear", "SpeedGear", "VelocityApparel", "TurboClothing"],
    "electronics": ["RacingTech", "SpeedElectronics", "VelocityGadgets", "TurboDevices"]
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_random_driver_name(discipline: str = None) -> DriverProfile:
    """Get a random driver name, optionally filtered by discipline"""
    import random
    
    if discipline:
        discipline_drivers = [d for d in DRIVER_POOL if d.discipline_specialization == discipline]
        if discipline_drivers:
            return random.choice(discipline_drivers)
    
    return random.choice(DRIVER_POOL)

def get_random_team_name(discipline: str) -> str:
    """Get a random team name for specified discipline"""
    import random
    return random.choice(TEAM_NAMES.get(discipline, TEAM_NAMES["GPC"]))

def get_random_track(discipline: str) -> Dict:
    """Get a random track for specified discipline"""
    import random
    return random.choice(TRACK_NAMES.get(discipline, TRACK_NAMES["GPC"]))

def get_country_name(country_code: str) -> str:
    """Convert country code to fictional country name"""
    return FICTIONAL_COUNTRIES.get(country_code, country_code)

# Export main data structures
__all__ = [
    'DISCIPLINES', 'DISCIPLINE_CODES', 'TEAM_NAMES', 'DRIVER_POOL',
    'TRACK_NAMES', 'FICTIONAL_COUNTRIES', 'CHAMPIONSHIP_NAMES',
    'ENGINE_SUPPLIERS', 'TIRE_SUPPLIERS', 'FUEL_SUPPLIERS',
    'MEDIA_OUTLETS', 'SPONSOR_CATEGORIES', 'get_random_driver_name',
    'get_random_team_name', 'get_random_track', 'get_country_name'
]