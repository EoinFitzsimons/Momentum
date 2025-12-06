"""
Momentum Motorsport Simulation - Placeholder Names and Entities

This file contains all placeholder names, teams, drivers, and championships
to avoid copyright issues while maintaining authenticity and immersion.
All names are fictional and any resemblance to real entities is coincidental.

Now enhanced with hybrid name generation using:
- NameAPI for realistic, locale-specific names
- ParaNames dataset for massive bulk capacity
- Statistical frequency weighting for authenticity
- Graceful fallbacks for reliability

Authors: Final Year Project - Computer Science
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import random
import logging

# Import hybrid name generation system
try:
    from systems.name_generator import (
        HybridNameGenerator, NameGenerationConfig, Gender,
        generate_racing_driver_name, get_global_generator
    )
    HYBRID_NAMES_AVAILABLE = True
except ImportError:
    HYBRID_NAMES_AVAILABLE = False
    logging.warning(
        "Hybrid name generator not available. Using fallback names.")

# ============================================================================
# RACING CATEGORIES AND LEAGUES STRUCTURE
# ============================================================================

from enum import Enum
from typing import Dict, List, NamedTuple


class RaceFormat(Enum):
    SINGLE_SEATER = "single_seater"          # 20+ cars, 2 per team
    PRODUCTION_CIRCUIT = "production_circuit"  # 30+ cars, 2 per team
    TRAVERSE_STAGE = "traverse_stage"        # 50+ cars, 1 per team
    URBAN_SHOWCASE = "urban_showcase"        # 8 cars/teams per event
    LINEAR_ACCELERATION = "linear_acceleration"  # 64 cars, knockout format
    SPRINT_CIRCUIT = "sprint_circuit"        # 24 cars, heats format
    ENDURANCE = "endurance"                  # Variable grid sizes


class LeagueInfo(NamedTuple):
    code: str
    full_name: str
    race_format: RaceFormat
    tier: int  
    min_teams: int
    max_teams: int
    cars_per_team: int
    typical_grid_size: int


# 7 MAIN CATEGORIES WITH 5+ LEAGUES EACH
RACING_CATEGORIES = {
    "SINGLE_SEATER": {
        "name": "Single Seater Racing",
        "leagues": {
            "GPC1": LeagueInfo("GPC1", "Global Premier Championship", RaceFormat.SINGLE_SEATER, 1, 10, 12, 2, 24),
            "GPC2": LeagueInfo("GPC2", "Global Premier Series 2", RaceFormat.SINGLE_SEATER, 2, 11, 13, 2, 26),
            "GPC3": LeagueInfo("GPC3", "Global Premier Series 3", RaceFormat.SINGLE_SEATER, 3, 12, 14, 2, 28),
            "GPRC": LeagueInfo("GPRC", "Global Premier Regional Championship", RaceFormat.SINGLE_SEATER, 4, 10, 15, 2, 30),
            "GPNC": LeagueInfo("GPNC", "Global Premier National Championship", RaceFormat.SINGLE_SEATER, 5, 8, 12, 2, 24),
            "GPJC": LeagueInfo("GPJC", "Global Premier Junior Championship", RaceFormat.SINGLE_SEATER, 6, 10, 16, 2, 32)
        }
    },
    "PRODUCTION_TOURING": {
        "name": "Production & Touring Cars",
        "leagues": {
            "WTC1": LeagueInfo("WTC1", "World Touring Championship Premier", RaceFormat.PRODUCTION_CIRCUIT, 1, 15, 18, 2, 36),
            "WTC2": LeagueInfo("WTC2", "World Touring Championship Division 2", RaceFormat.PRODUCTION_CIRCUIT, 2, 16, 20, 2, 40),
            "RTC": LeagueInfo("RTC", "Regional Touring Championship", RaceFormat.PRODUCTION_CIRCUIT, 3, 12, 18, 2, 36),
            "NTC": LeagueInfo("NTC", "National Touring Championship", RaceFormat.PRODUCTION_CIRCUIT, 4, 10, 15, 2, 30),
            "STC": LeagueInfo("STC", "Super Touring Championship", RaceFormat.PRODUCTION_CIRCUIT, 2, 14, 16, 2, 32),
            "CTC": LeagueInfo("CTC", "Club Touring Championship", RaceFormat.PRODUCTION_CIRCUIT, 5, 8, 20, 2, 40)
        }
    },
    "RALLY_STAGE": {
        "name": "Rally & Stage Racing",
        "leagues": {
            "WRC1": LeagueInfo("WRC1", "World Rally Championship Premier", RaceFormat.TRAVERSE_STAGE, 1, 25, 30, 1, 30),
            "WRC2": LeagueInfo("WRC2", "World Rally Championship 2", RaceFormat.TRAVERSE_STAGE, 2, 30, 35, 1, 35),
            "WRC3": LeagueInfo("WRC3", "World Rally Championship 3", RaceFormat.TRAVERSE_STAGE, 3, 35, 40, 1, 40),
            "CWRC": LeagueInfo("CWRC", "Continental Rally Championship", RaceFormat.TRAVERSE_STAGE, 4, 40, 50, 1, 50),
            "NRC": LeagueInfo("NRC", "National Rally Championship", RaceFormat.TRAVERSE_STAGE, 5, 30, 60, 1, 60),
            "RRC": LeagueInfo("RRC", "Regional Rally Championship", RaceFormat.TRAVERSE_STAGE, 6, 25, 45, 1, 45)
        }
    },
    "URBAN_STREET": {
        "name": "Urban & Street Racing",
        "leagues": {
            "USC1": LeagueInfo("USC1", "Urban Street Championship Elite", RaceFormat.URBAN_SHOWCASE, 1, 8, 8, 1, 8),
            "USC2": LeagueInfo("USC2", "Urban Street Championship Pro", RaceFormat.URBAN_SHOWCASE, 2, 8, 8, 1, 8),
            "USC3": LeagueInfo("USC3", "Urban Street Championship Sport", RaceFormat.URBAN_SHOWCASE, 3, 8, 8, 1, 8),
            "CUSC": LeagueInfo("CUSC", "Continental Urban Series", RaceFormat.URBAN_SHOWCASE, 4, 8, 8, 1, 8),
            "NUSC": LeagueInfo("NUSC", "National Urban Series", RaceFormat.URBAN_SHOWCASE, 5, 8, 8, 1, 8)
        }
    },
    "DRAG_ACCELERATION": {
        "name": "Drag & Acceleration Racing",
        "leagues": {
            "WDC1": LeagueInfo("WDC1", "World Drag Championship Elite", RaceFormat.LINEAR_ACCELERATION, 1, 32, 32, 2, 64),
            "WDC2": LeagueInfo("WDC2", "World Drag Championship Pro", RaceFormat.LINEAR_ACCELERATION, 2, 32, 32, 2, 64),
            "WDC3": LeagueInfo("WDC3", "World Drag Championship Sport", RaceFormat.LINEAR_ACCELERATION, 3, 32, 32, 2, 64),
            "CWDC": LeagueInfo("CWDC", "Continental Drag Championship", RaceFormat.LINEAR_ACCELERATION, 4, 32, 32, 2, 64),
            "NWDC": LeagueInfo("NWDC", "National Drag Championship", RaceFormat.LINEAR_ACCELERATION, 5, 24, 24, 2, 48)
        }
    },
    "SPRINT_RALLYCROSS": {
        "name": "Sprint & Rallycross",
        "leagues": {
            "WSRC1": LeagueInfo("WSRC1", "World Sprint Rallycross Elite", RaceFormat.SPRINT_CIRCUIT, 1, 12, 12, 2, 24),
            "WSRC2": LeagueInfo("WSRC2", "World Sprint Rallycross Pro", RaceFormat.SPRINT_CIRCUIT, 2, 12, 12, 2, 24),
            "WSRC3": LeagueInfo("WSRC3", "World Sprint Rallycross Sport", RaceFormat.SPRINT_CIRCUIT, 3, 12, 12, 2, 24),
            "CSRC": LeagueInfo("CSRC", "Continental Sprint Championship", RaceFormat.SPRINT_CIRCUIT, 4, 10, 10, 2, 20),
            "NSRC": LeagueInfo("NSRC", "National Sprint Championship", RaceFormat.SPRINT_CIRCUIT, 5, 8, 8, 2, 16)
        }
    },
    "ENDURANCE": {
        "name": "Endurance Racing",
        "leagues": {
            "WEC1": LeagueInfo("WEC1", "World Endurance Championship", RaceFormat.ENDURANCE, 1, 20, 25, 2, 50),
            "WEC2": LeagueInfo("WEC2", "World Endurance Series", RaceFormat.ENDURANCE, 2, 18, 22, 2, 44),
            "CWEC": LeagueInfo("CWEC", "Continental Endurance Championship", RaceFormat.ENDURANCE, 3, 15, 20, 2, 40),
            "NWEC": LeagueInfo("NWEC", "National Endurance Championship", RaceFormat.ENDURANCE, 4, 12, 18, 2, 36),
            "RWEC": LeagueInfo("RWEC", "Regional Endurance Championship", RaceFormat.ENDURANCE, 5, 10, 15, 2, 30)
        }
    }
}

# ============================================================================
# TEAM NAME GENERATION SYSTEM
# ============================================================================

# Base components for generating thousands of unique team names
TEAM_NAME_PREFIXES = [
    "Apex", "Velocity", "Phoenix", "Thunder", "Crimson", "Azure", "Sterling", "Nexus",
    "Titan", "Eclipse", "Lightning", "Falcon", "Storm", "Vanguard", "Pinnacle", "Zenith",
    "Horizon", "Meridian", "Catalyst", "Summit", "Quantum", "Matrix", "Vector", "Fusion",
    "Prism", "Vertex", "Pulse", "Surge", "Blaze", "Vortex", "Nova", "Stellar",
    "Cosmic", "Plasma", "Turbo", "Nitro", "Boost", "Thrust", "Warp", "Hyper",
    "Ultra", "Mega", "Super", "Elite", "Prime", "Alpha", "Beta", "Gamma",
    "Delta", "Omega", "Sigma", "Zeta", "Phantom", "Shadow", "Stealth", "Ghost",
    "Viper", "Cobra", "Panther", "Tiger", "Lion", "Eagle", "Hawk", "Falcon",
    "Raven", "Wolf", "Bear", "Shark", "Dragon", "Serpent", "Stallion", "Mustang",
    "Jaguar", "Cheetah", "Leopard", "Lynx", "Puma", "Cougar", "Wildcat", "Bobcat",
    "Red", "Blue", "Green", "Black", "White", "Silver", "Gold", "Bronze",
    "Copper", "Steel", "Iron", "Chrome", "Platinum", "Diamond", "Crystal", "Jade",
    "Ruby", "Sapphire", "Emerald", "Topaz", "Onyx", "Marble", "Granite", "Obsidian",
    "Fire", "Ice", "Wind", "Earth", "Water", "Air", "Metal", "Wood",
    "Stone", "Rock", "Sand", "Clay", "Mud", "Dust", "Ash", "Ember"
]

TEAM_NAME_SUFFIXES = [
    "Racing", "Motorsport", "Motorsports", "Team", "Racing Team", "Grand Prix",
    "Speed", "Velocity", "Dynamics", "Performance", "Engineering", "Technology",
    "Systems", "Solutions", "Innovations", "Developments", "Enterprises", "Industries",
    "Corporation", "Group", "Alliance", "Syndicate", "Collective", "Union",
    "Federation", "Association", "Society", "Club", "Organization", "Institute",
    "Academy", "School", "University", "College", "Foundation", "Trust",
    "Holdings", "Ventures", "Capital", "Investments", "Partners", "Associates",
    "Consultants", "Specialists", "Experts", "Professionals", "Masters", "Champions",
    "Winners", "Victors", "Legends", "Heroes", "Warriors", "Fighters",
    "Gladiators", "Spartans", "Titans", "Giants", "Colossi", "Behemoths",
    "Leviathans", "Krakens", "Phoenixes", "Dragons", "Griffins", "Pegasi",
    "Unicorns", "Centaurs", "Minotaurs", "Cyclopes", "Hydras", "Chimeras",
    "Demons", "Angels", "Saints", "Spirits", "Ghosts", "Phantoms",
    "Shadows", "Wraiths", "Specters", "Apparitions", "Visions", "Dreams",
    "Nightmares", "Illusions", "Mirages", "Hallucinations", "Fantasies", "Chimeras"
]

# Sample generated teams (will be expanded programmatically)
SAMPLE_TEAM_NAMES = {

    "GPC1": ["Premier Racing", "Global Velocity", "Apex Motorsport", "Sterling GP", "Phoenix Racing", "Titan Racing", "Vanguard GP", "Quantum Racing", "Summit Motorsport", "Zenith Racing", "Nexus GP", "Elite Racing"],
    "GPC2": ["NextGen Racing", "Future Stars GP", "Pinnacle Motorsport", "Matrix Racing", "Vertex GP", "Pulse Racing", "Surge Motorsport", "Blaze GP", "Vortex Racing", "Nova Motorsport", "Stellar GP", "Cosmic Racing"],
    "GPC3": ["Rising Talent GP", "Prospect Racing", "Cadet Motorsport", "Junior Velocity", "Academy GP", "Star Racing", "Victory Cadets", "Premier Academy", "Racing Pathways", "Championship Futures", "Elite Juniors", "Victory Academy"],
    "WTC1": ["Touring Masters", "World Touring Elite", "Velocity Touring", "Apex Touring", "Thunder Touring", "Crimson Touring", "Azure Touring", "Sterling Touring", "Nexus Touring", "Titan Touring", "Eclipse Touring", "Lightning Touring"],
    "WTC2": ["Touring Pros", "Touring Champions", "Touring Performance", "Touring Dynamics", "Touring Engineering", "Touring Technology", "Touring Systems", "Touring Solutions", "Touring Innovations", "Touring Developments", "Touring Enterprises", "Touring Industries"],
    "WRC1": ["Rally Masters", "Off-Road Racing", "Stage Racing Team", "Terrain Masters", "All-Surface Racing", "Rally Champions", "Cross-Country Racing", "Surface Specialists", "Rally Elite", "Terrain Racing", "Stage Masters", "Rally Professionals"],
    "WRC2": ["Rally Pros", "Rally Champions", "Rally Performance", "Rally Dynamics", "Rally Engineering", "Rally Technology", "Rally Systems", "Rally Solutions", "Rally Innovations", "Rally Developments", "Rally Enterprises", "Rally Industries"],
    "WEC1": ["Endurance Masters", "Marathon Racing", "Persistence Motorsport", "Long Distance Racing", "Stamina Racing Team", "Durability Motors", "24 Hour Racing", "Ultra Distance Team", "Endurance Elite", "Distance Champions", "Marathon Masters", "Persistence Racing"],
    "WEC2": ["Endurance Pros", "Endurance Champions", "Endurance Performance", "Endurance Dynamics", "Endurance Engineering", "Endurance Technology", "Endurance Systems", "Endurance Solutions", "Endurance Innovations", "Endurance Developments", "Endurance Enterprises", "Endurance Industries"],
}

# ============================================================================
# DRIVER NAME GENERATION SYSTEM
# ============================================================================


@dataclass
class DriverProfile:
    first_name: str
    last_name: str
    nationality: str
    age: int
    discipline_specialization: str
    # "driver", "co_driver", "team_principal", "engineer", etc.
    role: str = "driver"


# Massive name pools for generating thousands of unique drivers
FIRST_NAMES = {
    "male": [
        "Alexander", "James", "Michael", "William", "Robert", "David", "John", "Daniel", "Matthew", "Christopher",
        "Andrew", "Joshua", "Paul", "Mark", "Donald", "Steven", "Kenneth", "Joseph", "Timothy", "Kevin",
        "Brian", "George", "Edward", "Ronald", "Thomas", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary",
        "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel",
        "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Jack", "Dennis", "Jerry", "Tyler", "Aaron",
        "Jose", "Henry", "Adam", "Douglas", "Nathan", "Peter", "Zachary", "Kyle", "Noah", "Alan",
        "Ethan", "Jeremy", "Lionel", "Mason", "Lucas", "Logan", "Isaac", "Elijah", "Wayne", "Ralph",
        # International names
        "Alessandro", "Giovanni", "Francesco", "Antonio", "Lorenzo", "Matteo", "Marco", "Andrea", "Stefano", "Luca",
        "Pierre", "Jean", "Michel", "Philippe", "Alain", "Claude", "Bernard", "Henri", "Marcel", "Andre",
        "Carlos", "Antonio", "Manuel", "Francisco", "Juan", "Luis", "Miguel", "Jose", "Rafael", "Diego",
        "Klaus", "Hans", "Wolfgang", "Jurgen", "Helmut", "Rolf", "Dieter", "Werner", "Gunter", "Horst",
        "Hiroshi", "Takeshi", "Kenji", "Yoshida", "Satoshi", "Masahiro", "Kazuki", "Ryouta", "Naoki", "Shinji"
    ],
    "female": [
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
        "Nancy", "Lisa", "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle",
        "Laura", "Sarah", "Kimberly", "Deborah", "Dorothy", "Lisa", "Nancy", "Karen", "Betty", "Helen",
        "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Sarah", "Kimberly", "Deborah",
        "Amy", "Angela", "Ashley", "Brenda", "Emma", "Olivia", "Cynthia", "Marie", "Janet", "Catherine",
        # International names
        "Giulia", "Francesca", "Chiara", "Valentina", "Alessandra", "Federica", "Silvia", "Paola", "Ilaria", "Serena",
        "Marie", "Nathalie", "Isabelle", "Sylvie", "Catherine", "Francoise", "Monique", "Nicole", "Brigitte", "Martine",
        "Carmen", "Maria", "Pilar", "Mercedes", "Rosa", "Ana", "Isabel", "Cristina", "Marta", "Patricia",
        "Ingrid", "Sabine", "Petra", "Andrea", "Claudia", "Stefanie", "Birgit", "Martina", "Christine", "Monika",
        "Yuki", "Sakura", "Akiko", "Miyuki", "Naomi", "Emi", "Rie", "Kumiko", "Mayumi", "Noriko"
    ]
}

LAST_NAMES = [
    # English/International surnames
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    # European surnames
    "Rossi", "Ferrari", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco", "Bruno", "Gallo",
    "Conti", "De Luca", "Costa", "Giordano", "Mancini", "Rizzo", "Lombardi", "Moretti", "Barbieri", "Fontana",
    "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand",
    "Morel", "Fournier", "Girard", "Bonnet", "Dupont", "Lambert", "Fontaine", "Rousseau", "Vincent", "Muller",
    "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann", "Schafer",
    "Koch", "Richter", "Klein", "Wolf", "Schroder", "Neumann", "Schwarz", "Zimmermann", "Braun", "Kruger",
    "Gonzalez", "Rodriguez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Gomez", "Martin", "Jimenez",
    "Ruiz", "Hernandez", "Diaz", "Moreno", "Munoz", "Alvarez", "Romero", "Alonso", "Gutierrez", "Navarro",
    # Asian surnames
    "Tanaka", "Suzuki", "Takahashi", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato", "Yoshida",
    "Yamada", "Sasaki", "Yamaguchi", "Matsumoto", "Inoue", "Kimura", "Hayashi", "Shimizu", "Yamazaki", "Mori",
    "Li", "Wang", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou",
    "Xu", "Sun", "Ma", "Zhu", "Hu", "Guo", "He", "Lin", "Luo", "Gao"
]

# Sample driver pool (will be expanded programmatically)
SAMPLE_DRIVER_POOL = [
    # Elite tier examples
    DriverProfile("Alexander", "Sterling", "GBR", 27, "GPC1"),
    DriverProfile("Marco", "Veloce", "ITA", 24, "GPC1"),
    DriverProfile("Lucas", "Phoenix", "FRA", 29, "GPC1"),
    DriverProfile("Kai", "Thunder", "JPN", 25, "GPC1"),
]


# ============================================================================
# COUNTRIES AND TERRITORIES (UN Members + Recognised Territories)
# ============================================================================

# Using real country codes and names
COUNTRIES = {
    # Major Racing Nations
    "GBR": "United Kingdom", "USA": "United States", "ITA": "Italy", "FRA": "France",
    "GER": "Germany", "ESP": "Spain", "JPN": "Japan", "AUS": "Australia",
    "NLD": "Netherlands", "BRA": "Brazil", "CAN": "Canada", "MEX": "Mexico",
    "SWE": "Sweden", "FIN": "Finland", "NOR": "Norway", "DEN": "Denmark",
    "BEL": "Belgium", "SUI": "Switzerland", "AUT": "Austria", "MON": "Monaco",

    # All UN Member States
    "AFG": "Afghanistan", "ALB": "Albania", "DZA": "Algeria", "AND": "Andorra",
    "AGO": "Angola", "ATG": "Antigua and Barbuda", "ARG": "Argentina", "ARM": "Armenia",
    "AZE": "Azerbaijan", "BHS": "Bahamas", "BHR": "Bahrain", "BGD": "Bangladesh",
    "BRB": "Barbados", "BLR": "Belarus", "BLZ": "Belize", "BEN": "Benin",
    "BTN": "Bhutan", "BOL": "Bolivia", "BIH": "Bosnia and Herzegovina", "BWA": "Botswana",
    "BRN": "Brunei", "BGR": "Bulgaria", "BFA": "Burkina Faso", "BDI": "Burundi",
    "CPV": "Cape Verde", "KHM": "Cambodia", "CMR": "Cameroon", "CAF": "Central African Republic",
    "TCD": "Chad", "CHL": "Chile", "CHN": "China", "COL": "Colombia",
    "COM": "Comoros", "COG": "Congo", "COD": "Democratic Republic of the Congo", "CRI": "Costa Rica",
    "CIV": "Ivory Coast", "HRV": "Croatia", "CUB": "Cuba", "CYP": "Cyprus",
    "CZE": "Czech Republic", "DJI": "Djibouti", "DMA": "Dominica", "DOM": "Dominican Republic",
    "ECU": "Ecuador", "EGY": "Egypt", "SLV": "El Salvador", "GNQ": "Equatorial Guinea",
    "ERI": "Eritrea", "EST": "Estonia", "SWZ": "Eswatini", "ETH": "Ethiopia",
    "FJI": "Fiji", "GAB": "Gabon", "GMB": "Gambia", "GEO": "Georgia",
    "GHA": "Ghana", "GRC": "Greece", "GRD": "Grenada", "GTM": "Guatemala",
    "GIN": "Guinea", "GNB": "Guinea-Bissau", "GUY": "Guyana", "HTI": "Haiti",
    "HND": "Honduras", "HUN": "Hungary", "ISL": "Iceland", "IND": "India",
    "IDN": "Indonesia", "IRN": "Iran", "IRQ": "Iraq", "IRL": "Ireland",
    "ISR": "Israel", "JAM": "Jamaica", "JOR": "Jordan", "KAZ": "Kazakhstan",
    "KEN": "Kenya", "KIR": "Kiribati", "PRK": "North Korea", "KOR": "South Korea",
    "KWT": "Kuwait", "KGZ": "Kyrgyzstan", "LAO": "Laos", "LVA": "Latvia",
    "LBN": "Lebanon", "LSO": "Lesotho", "LBR": "Liberia", "LBY": "Libya",
    "LIE": "Liechtenstein", "LTU": "Lithuania", "LUX": "Luxembourg", "MDG": "Madagascar",
    "MWI": "Malawi", "MYS": "Malaysia", "MDV": "Maldives", "MLI": "Mali",
    "MLT": "Malta", "MHL": "Marshall Islands", "MRT": "Mauritania", "MUS": "Mauritius",
    "FSM": "Micronesia", "MDA": "Moldova", "MNG": "Mongolia", "MNE": "Montenegro",
    "MAR": "Morocco", "MOZ": "Mozambique", "MMR": "Myanmar", "NAM": "Namibia",
    "NRU": "Nauru", "NPL": "Nepal", "NZL": "New Zealand", "NIC": "Nicaragua",
    "NER": "Niger", "NGA": "Nigeria", "MKD": "North Macedonia", "OMN": "Oman",
    "PAK": "Pakistan", "PLW": "Palau", "PAN": "Panama", "PNG": "Papua New Guinea",
    "PRY": "Paraguay", "PER": "Peru", "PHL": "Philippines", "POL": "Poland",
    "PRT": "Portugal", "QAT": "Qatar", "ROU": "Romania", "RUS": "Russia",
    "RWA": "Rwanda", "KNA": "Saint Kitts and Nevis", "LCA": "Saint Lucia", "VCT": "Saint Vincent and the Grenadines",
    "WSM": "Samoa", "SMR": "San Marino", "STP": "Sao Tome and Principe", "SAU": "Saudi Arabia",
    "SEN": "Senegal", "SRB": "Serbia", "SYC": "Seychelles", "SLE": "Sierra Leone",
    "SGP": "Singapore", "SVK": "Slovakia", "SVN": "Slovenia", "SLB": "Solomon Islands",
    "SOM": "Somalia", "ZAF": "South Africa", "SSD": "South Sudan", "LKA": "Sri Lanka",
    "SDN": "Sudan", "SUR": "Suriname", "SYR": "Syria", "TJK": "Tajikistan",
    "TZA": "Tanzania", "THA": "Thailand", "TLS": "Timor-Leste", "TGO": "Togo",
    "TON": "Tonga", "TTO": "Trinidad and Tobago", "TUN": "Tunisia", "TUR": "Turkey",
    "TKM": "Turkmenistan", "TUV": "Tuvalu", "UGA": "Uganda", "UKR": "Ukraine",
    "ARE": "United Arab Emirates", "URY": "Uruguay", "UZB": "Uzbekistan", "VUT": "Vanuatu",
    "VAT": "Vatican City", "VEN": "Venezuela", "VNM": "Vietnam", "YEM": "Yemen",
    "ZMB": "Zambia", "ZWE": "Zimbabwe",

    # Recognised Territories and Entities
    "GIB": "Gibraltar",
    "JEY": "Jersey",
    "GGY": "Guernsey",
    "FLK": "Falkland Islands",
    "BES": "Caribbean Netherlands (Bonaire, Sint Eustatius, Saba)",
    "CUW": "Curaçao",
    "SXM": "Sint Maarten",
    "MAF": "Saint Martin (French part)",
    "BLM": "Saint Barthélemy",
    "GLP": "Guadeloupe",
    "MTQ": "Martinique",
    "REU": "Réunion",
    "MYT": "Mayotte",
    "NCL": "New Caledonia",
    "PYF": "French Polynesia",
    "WLF": "Wallis and Futuna",
    "ASM": "American Samoa",
    "GUM": "Guam",
    "MNP": "Northern Mariana Islands",
    "PRI": "Puerto Rico",
    "VIR": "U.S. Virgin Islands",
    "VGB": "British Virgin Islands",
    "TCA": "Turks and Caicos Islands",
    "SHN": "Saint Helena, Ascension and Tristan da Cunha",
    "PCN": "Pitcairn Islands",
    "COK": "Cook Islands",
    "NIU": "Niue",
    "TKL": "Tokelau",
    "PSE": "Palestine", "TWN": "Taiwan", "XKX": "Kosovo", "PMR": "Transnistria",
    "ABK": "Abkhazia", "OSE": "South Ossetia", "ARK": "Artsakh", "DNR": "Donetsk People's Republic",
    "LNR": "Luhansk People's Republic", "NCY": "Northern Cyprus", "SOM2": "Somaliland",
    "WES": "Western Sahara", "HKG": "Hong Kong", "MAC": "Macau"
}

# ============================================================================
# MANUFACTURER/ENGINE SUPPLIER NAMES
# ============================================================================

ENGINE_SUPPLIERS: dict[str, str] = {

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
# STAFF ROLES AND PERSONNEL SYSTEM
# ============================================================================

STAFF_ROLES = {
    "management": [
        "Team Principal", "General Manager", "Operations Manager", "Commercial Manager",
        "Marketing Manager", "Communications Manager", "HR Manager", "Finance Manager"
    ],
    "technical": [
        "Technical Director", "Chief Engineer", "Aerodynamics Engineer", "Engine Engineer",
        "Data Engineer", "Performance Engineer", "Vehicle Dynamics Engineer", "Systems Engineer",
        "Electronics Engineer", "Materials Engineer", "Design Engineer", "CAD Designer"
    ],
    "race_operations": [
        "Race Engineer", "Strategy Engineer", "Pit Crew Chief", "Mechanic", "Tire Technician",
        "Fuel Systems Technician", "Electronics Technician", "Data Analyst", "Telemetry Engineer",
        "Race Strategist", "Performance Analyst", "Setup Engineer"
    ],
    "drivers": [
        "Lead Driver", "Reserve Driver", "Development Driver", "Test Driver", "Simulator Driver",
        "Co-Driver", "Instructor", "Driver Coach", "Driving Consultant"
    ],
    "support": [
        "Logistics Coordinator", "Transport Manager", "Equipment Manager", "Safety Officer",
        "Medical Officer", "Physiotherapist", "Sports Psychologist", "Nutritionist",
        "Fitness Trainer", "Media Relations", "Press Officer", "Photographer", "Videographer"
    ]
}

# Estimated staff sizes per team tier and league
STAFF_SIZE_ESTIMATES = {
    # Tier 1
    1: {"management": (8, 15), "technical": (25, 50), "race_operations": (20, 40), "drivers": (4, 8), "support": (15, 30)},
    # Tier 2
    2: {"management": (6, 12), "technical": (15, 35), "race_operations": (15, 30), "drivers": (3, 6), "support": (10, 20)},
    # Tier 3
    3: {"management": (4, 8), "technical": (10, 25), "race_operations": (10, 20), "drivers": (2, 4), "support": (5, 15)},
    # Tier 4
    4: {"management": (3, 6), "technical": (5, 15), "race_operations": (8, 15), "drivers": (2, 3), "support": (3, 10)},
    # Tier 5
    5: {"management": (2, 4), "technical": (3, 8), "race_operations": (5, 10), "drivers": (1, 2), "support": (2, 5)},
    # Tier 6
    6: {"management": (1, 3), "technical": (2, 5), "race_operations": (3, 6), "drivers": (1, 2), "support": (1, 3)}
}

# ============================================================================
# DATABASE GENERATION FUNCTIONS
# ============================================================================


def generate_team_name(
        category: Optional[str] = None, tier: Optional[int] = None) -> str:
    """Generate a unique team name using prefix + suffix combination"""
    import random
    prefix = random.choice(TEAM_NAME_PREFIXES)
    suffix = random.choice(TEAM_NAME_SUFFIXES)
    return f"{prefix} {suffix}"


def generate_driver_name(
        nationality: Optional[str] = None, gender: str = "ANY") -> Dict[str, str]:
    """Generate realistic driver name using hybrid system with fallback"""

    # Use hybrid name generator if available
    if HYBRID_NAMES_AVAILABLE and nationality:
        try:
            return generate_racing_driver_name(nationality, gender)
        except Exception as e:
            logging.warning(
                f"Hybrid name generation failed: {e}. Using fallback.")

    # Fallback to original system
    first_names = FIRST_NAMES.get('male', []) + FIRST_NAMES.get('female', [])
    last_names = LAST_NAMES

    # Select names based on nationality preference
    if nationality and nationality in COUNTRIES:
        # Weight towards more common names for major motorsport countries
        country_data: dict = COUNTRIES.get(nationality, {})  # type: ignore
        if isinstance(country_data, dict):
            weight_factor = country_data.get('motorsport_heritage', 0.5)
        else:
            weight_factor = 0.5
        if weight_factor > 0.7:
            # Use more traditional/common names for established racing nations
            first_name = random.choices(
                first_names, weights=[
                    1.2 if len(name) <= 6 else 0.8 for name in first_names], k=1)[0]
        else:
            first_name = random.choice(first_names)
    else:
        first_name = random.choice(first_names)

    last_name = random.choice(last_names)

    return {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "nationality": nationality or random.choice(list(COUNTRIES.keys())),
        "gender": gender,
        "source": "fallback",
        "confidence": "0.6"
    }


def calculate_total_entities():
    """Calculate total entities needed for full database"""
    totals = {
        "teams": 0,
        "drivers": 0,
        "staff": 0,
        "total_personnel": 0
    }

    for category_data in RACING_CATEGORIES.values():
        for league_info in category_data["leagues"].values():
            avg_teams = (league_info.min_teams + league_info.max_teams) // 2
            totals["teams"] += avg_teams
            totals["drivers"] += avg_teams * league_info.cars_per_team

            # Calculate staff per team based on tier
            tier_staff = STAFF_SIZE_ESTIMATES.get(
                league_info.tier, STAFF_SIZE_ESTIMATES.get(6, {}))
            if isinstance(tier_staff, dict):
                avg_staff_per_team = sum((min_staff + max_staff) // 2
                                         for min_staff, max_staff in tier_staff.values())
            else:
                avg_staff_per_team = 0
            totals["staff"] += avg_teams * avg_staff_per_team

    totals["total_personnel"] = totals["drivers"] + totals["staff"]
    return totals


def generate_league_structure(league_code: str) -> dict:
    """Generate complete team and driver structure for a specific league"""
    import random

    if league_code not in [code for cat in RACING_CATEGORIES.values()
                           for code in cat["leagues"].keys()]:  # type: ignore
        raise ValueError(f"Unknown league code: {league_code}")

    # Find league info
    league_info = None
    for category_data in RACING_CATEGORIES.values():
        if league_code in category_data["leagues"]:  # type: ignore
            league_info = category_data["leagues"][league_code]  # type: ignore
            break

    if not league_info:
        return {}

    # Generate teams for this league
    num_teams = random.randint(league_info.min_teams, league_info.max_teams)
    teams = []

    for i in range(num_teams):
        team = {
            "id": f"{league_code}_{i + 1:03d}",
            "name": generate_team_name(),
            "league": league_code,
            "tier": league_info.tier,
            "drivers": [],
            "staff": {}
        }

        # Generate drivers for this team
        for j in range(league_info.cars_per_team):
            nationality = random.choice(list(COUNTRIES.keys()))
            first_name, last_name = generate_driver_name(nationality)
            age = random.randint(18, 45)

            driver = {
                "id": f"{team['id']}_D{j + 1}",
                "first_name": first_name,
                "last_name": last_name,
                "nationality": nationality,
                "age": age,
                "role": "driver"
            }
            team["drivers"].append(driver)

        # Generate staff for this team based on tier
        tier_staff_ranges = STAFF_SIZE_ESTIMATES.get(
            league_info.tier, STAFF_SIZE_ESTIMATES[6])
        for role_category, (min_staff, max_staff) in tier_staff_ranges.items():
            if role_category == "drivers":
                continue  # Already handled

            num_staff = random.randint(min_staff, max_staff)
            team["staff"][role_category] = []

            for k in range(num_staff):
                nationality = random.choice(list(COUNTRIES.keys()))
                gender = random.choice(["male", "female"])
                first_name, last_name = generate_driver_name(
                    nationality, gender)
                age = random.randint(25, 65)
                role = random.choice(STAFF_ROLES[role_category])

                staff_member = {
                    "id": f"{team['id']}_S{role_category[0].upper()}{k + 1}",
                    "first_name": first_name,
                    "last_name": last_name,
                    "nationality": nationality,
                    "age": age,
                    "role": role,
                    "category": role_category
                }
                team["staff"][role_category].append(staff_member)

        teams.append(team)

    return {
        "league_code": league_code,
        "league_info": league_info,
        "teams": teams,
        "total_teams": len(teams),
        "total_drivers": sum(len(team["drivers"]) for team in teams),
        "total_staff": sum(sum(len(staff_list) for staff_list in team["staff"].values())
                           for team in teams)
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_random_driver_name(discipline: Optional[str] = None) -> DriverProfile:
    """Get a random driver name, optionally filtered by discipline"""
    import random

    if discipline:
        discipline_drivers = [
            d for d in SAMPLE_DRIVER_POOL if d.discipline_specialization == discipline]
        if discipline_drivers:
            return random.choice(discipline_drivers)

    return random.choice(SAMPLE_DRIVER_POOL)


def get_random_team_name(category: Optional[str] = None) -> str:
    """Generate a random team name"""
    return generate_team_name(category)


def get_random_track(discipline: str) -> Dict:
    """Get a random track for specified discipline"""
    import random
    # TODO: Implement TRACK_NAMES data structure
    return {}


def get_country_name(country_code: str) -> str:
    """Get country name from code"""
    return COUNTRIES.get(country_code, country_code)


def get_all_league_codes() -> List[str]:
    """Get all available league codes"""
    codes = []
    for category_data in RACING_CATEGORIES.values():
        codes.extend(category_data["leagues"].keys())  # type: ignore
    return codes


def get_leagues_by_category(category: str) -> Dict:
    """Get all leagues for a specific category"""
    return RACING_CATEGORIES.get(category, {}).get("leagues", {})  # type: ignore

# ============================================================================
# ENHANCED NAME GENERATION FUNCTIONS
# ============================================================================


def generate_bulk_drivers(
        count: int, country_distribution: Optional[Dict[str, float]] = None) -> List[Dict[str, str]]:
    """Generate bulk drivers using hybrid system for database seeding"""
    if HYBRID_NAMES_AVAILABLE:
        try:
            generator = get_global_generator()
            results = generator.generate_bulk_names(
                count, country_distribution)
            return [{
                "first_name": result.first_name,
                "last_name": result.last_name,
                "full_name": result.full_name,
                "nationality": result.nationality,
                "gender": result.gender.value,
                "source": result.source.value,
                "confidence": result.confidence
            } for result in results]
        except Exception as e:
            logging.warning(f"Bulk generation failed: {e}. Using fallback.")

    # Fallback to simple generation
    results = []
    countries = list(COUNTRIES.keys())
    for _ in range(count):
        nationality = random.choice(countries)
        gender = random.choice(["MALE", "FEMALE"])
        name = generate_driver_name(nationality, gender)
        results.append(name)
    return results


def get_name_generation_stats() -> Dict:
    """Get statistics about name generation performance"""
    if HYBRID_NAMES_AVAILABLE:
        try:
            generator = get_global_generator()
            return generator.get_generation_stats()
        except Exception:
            pass
    return {"hybrid_system": "unavailable", "fallback_only": True}


# Export main data structures
__all__ = [
    'RACING_CATEGORIES', 'COUNTRIES', 'SAMPLE_DRIVER_POOL', 'TRACK_NAMES',
    'CHAMPIONSHIP_NAMES', 'ENGINE_SUPPLIERS', 'TIRE_SUPPLIERS', 'FUEL_SUPPLIERS',
    'MEDIA_OUTLETS', 'SPONSOR_CATEGORIES', 'STAFF_ROLES', 'STAFF_SIZE_ESTIMATES',
    'RaceFormat', 'LeagueInfo', 'DriverProfile', 'FIRST_NAMES', 'LAST_NAMES',
    'TEAM_NAME_PREFIXES', 'TEAM_NAME_SUFFIXES', 'get_random_driver_name',
    'get_random_team_name', 'get_random_track', 'get_country_name',
    'generate_team_name', 'generate_driver_name', 'calculate_total_entities',
    'generate_league_structure', 'get_all_league_codes', 'get_leagues_by_category',
    'generate_bulk_drivers', 'get_name_generation_stats'
]

# ============================================================================
# SYSTEM SCALE DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    # Demonstrate the scale of the system
    print("=== MOMENTUM MOTORSPORT SIMULATION - SCALE ANALYSIS ===\\n")

    totals = calculate_total_entities()
    print(f"ESTIMATED TOTAL DATABASE SIZE:")
    print(f"- Teams: {totals['teams']:,}")
    print(f"- Drivers: {totals['drivers']:,}")
    print(f"- Staff: {totals['staff']:,}")
    print(f"- Total Personnel: {totals['total_personnel']:,}")

    print(f"\\nRACING CATEGORIES: {len(RACING_CATEGORIES)}")
    for category, data in RACING_CATEGORIES.items():
        print(f"\\n{category}: {data['name']}")
        print(f"  Leagues: {len(data['leagues'])}")
        for code, league in data['leagues'].items():  # type: ignore
            print(f"    {code}: {league.full_name} (Tier {league.tier})")
            print(
                f"      Grid: {
                    league.typical_grid_size} cars, {
                    league.min_teams}-{
                    league.max_teams} teams")

    print(f"\\nCOUNTRIES SUPPORTED: {len(COUNTRIES)}")
    print(f"NAME COMBINATIONS: {len(FIRST_NAMES['male']) +
                                len(FIRST_NAMES['female'])} × {len(LAST_NAMES)} = {(len(FIRST_NAMES['male']) +
                                                                                    len(FIRST_NAMES['female'])) *
                                                                                   len(LAST_NAMES):,} possible names")
    print(
        f"TEAM NAME COMBINATIONS: {
            len(TEAM_NAME_PREFIXES)} × {
            len(TEAM_NAME_SUFFIXES)} = {
                len(TEAM_NAME_PREFIXES) * len(TEAM_NAME_SUFFIXES):,} possible team names")

    print(f"\\n=== SAMPLE LEAGUE GENERATION ===")
    sample_league = generate_league_structure("GPC1")
    print(
        f"\\nGenerated {
            sample_league['league_code']} ({
            sample_league['league_info'].full_name}):")
    print(f"- Teams: {sample_league['total_teams']}")
    print(f"- Drivers: {sample_league['total_drivers']}")
    print(f"- Staff: {sample_league['total_staff']}")
    print(
        f"- Total Personnel: {sample_league['total_drivers'] + sample_league['total_staff']}")

    print("\\nThis system can generate THOUSANDS of unique entities while maintaining diversity and realism!")
