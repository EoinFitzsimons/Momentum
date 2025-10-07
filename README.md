
# Momentum - Multi-discipline Motorsport Management Simulator

**Project Type:** Multi-discipline Motorsport Management Simulator  
**Development Scope:** Python back-end simulation engine (primary focus)  
**Status:** Active Development - Backend Systems Implementation Phase

## Project Overview

Momentum is a comprehensive motorsport management simulation that spans **seven distinct racing disciplines**, featuring detailed team operations, driver development, and strategic management. The system emphasizes realistic simulation depth, emergent narratives, and authentic motorsport operations without any licensed content.

Players act as team principals, making managerial, financial, and strategic decisions across multiple racing categories—from single-seater championships to rally stages, endurance racing to drag competitions.

## Core Philosophy

- **Management-Focused Simulation:** Strategic decision-making drives success, not driving mechanics
- **Multi-Discipline Racing:** Seven complete racing disciplines with unique characteristics and challenges
- **Authentic Operations:** Realistic budgets, staff management, driver development, and team dynamics
- **Generic Content:** All teams, drivers, series, and personnel are fictional to avoid licensing issues
- **Emergent Narratives:** Dynamic career progression, rivalries, and historical depth through simulation
- **Data-Driven Decisions:** Advanced analytics and staff systems provide strategic information layers

## Racing Disciplines

Momentum features **seven complete racing disciplines**, each with distinct simulation characteristics:

### 1. **Single Seater** (Open-Wheel Racing)
- **Format:** Technical precision racing with open wheels and aerodynamic focus
- **Grid Size:** 20-32 cars, 2 per team
- **Leagues:** GPC1 (Premier), GPC2, GPC3, GPRC (Regional), GPNC (National), GPJC (Junior)
- **Key Factors:** Aerodynamics, cornering speed, qualifying precision

### 2. **Production/Touring Cars** (Circuit Racing)
- **Format:** Close-quarters racing with modified production vehicles
- **Grid Size:** 30-40 cars, 2 per team
- **Leagues:** WTC1 (Premier), WTC2, RTC (Regional), NTC (National), STC (Super), CTC (Club)
- **Key Factors:** Durability, contact management, overtaking ability

### 3. **Rally/Stage Racing** (Off-Road Navigation)
- **Format:** Point-to-point time trials across varied terrain
- **Grid Size:** 30-60 entries, 1 car per team
- **Leagues:** WRC1 (Premier), WRC2, WRC3, CWRC (Continental), NRC (National), RRC (Regional)
- **Key Factors:** Co-driver communication, surface adaptability, pace notes

### 4. **Urban/Street Racing** (City Circuits)
- **Format:** Technical street circuit racing in urban environments
- **Grid Size:** 8 cars per event
- **Leagues:** USC1 (Elite), USC2 (Pro), USC3 (Sport), CUSC (Continental), NUSC (National)
- **Key Factors:** Precision, barrier proximity, street surface grip

### 5. **Drag/Acceleration Racing** (Quarter Mile)
- **Format:** Straight-line acceleration in knockout tournament format
- **Grid Size:** 64 cars, knockout elimination
- **Leagues:** WDC1 (Elite), WDC2 (Pro), WDC3 (Sport), CWDC (Continental), NWDC (National)
- **Key Factors:** Launch technique, power delivery, reaction time

### 6. **Sprint/Rallycross** (Mixed Surface)
- **Format:** Short circuit races mixing tarmac and gravel with jumps
- **Grid Size:** 16-24 cars in heat format
- **Leagues:** WSRC1 (Elite), WSRC2 (Pro), WSRC3 (Sport), CSRC (Continental), NSRC (National)
- **Key Factors:** Surface transitions, jump navigation, heat consistency

### 7. **Endurance Racing** (Long Distance)
- **Format:** Extended multi-hour races emphasizing reliability and strategy
- **Grid Size:** 30-50 cars, 2 per team
- **Leagues:** WEC1 (Premier), WEC2, CWEC (Continental), NWEC (National), RWEC (Regional)
- **Key Factors:** Fuel strategy, tire management, driver rotation, reliability

## System Architecture

### Python Simulation Engine (`Momentum/Python/`)

**Core Components:**

- **Multi-Discipline Simulator:** Seven complete discipline-specific racing engines with unique simulation logic
- **Driver System:** 50+ attributes across 7 categories (technical, mental, physical, racecraft, personality, experience, discipline preferences)
- **Staff Management:** 40+ attributes, 25+ roles (Technical Director, Race Strategist, Data Analyst, Pit Crew Chief, etc.)
- **Currency System:** Multi-currency support (EUR, USD, GBP, JPY, CHF) with real-time exchange rates
- **Financial Management:** Realistic budget caps, salary negotiations, operational costs scaled by discipline
- **Name Generation:** Intelligent system using Faker library with 24 locales for authentic, culturally-appropriate international names
- **Supplier System:** Engine, tire, and fuel suppliers with performance characteristics
- **Monte Carlo Simulation:** Advanced probabilistic race outcome generation
- **Database Layer:** SQLite persistence for teams, drivers, staff, races, championships

**Key Features:**

- Cross-discipline driver compatibility with specialization preferences
- Budget-scaled staff requirements (€800K to €12M+ budgets)
- Information fog-of-war based on staff quality (better analysts = more data access)
- Realistic attribute distributions and career progression
- Generic placeholder content (no licensed series, teams, or drivers)

## Technical Stack

- **Backend:** Python 3.11+
- **Database:** SQLite 3.7+ with SQLAlchemy ORM
- **Web Framework:** FastAPI (optional, for future API exposure)
- **Libraries:** NumPy, Pandas, SciPy (Monte Carlo simulation)
- **Name Generation:** Faker library with comprehensive locale support (80+ countries, 24 locales)
- **Currency:** Live exchange rate support via currency API
- **Tools:** VS Code, GitHub Desktop, SQLite browser

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for version control)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EoinFitzsimons/FinalProject.git
   cd FinalProject/Momentum/Python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional):
   Create a `.env` file in the Python directory:
   ```env
   # Name Generation API (optional)
      ```bash
   # No API keys required - fully offline name generation
   ```
   
   # Currency System
   DEFAULT_CURRENCY=EUR
   USE_LIVE_EXCHANGE_RATES=true
   
   # Database
   DATABASE_PATH=database/momentum.db
   ```

4. **Initialize the database:**
   ```bash
   python -m database.database_manager
   ```

5. **Run tests:**
   ```bash
   python tests/simple_driver_test.py
   python tests/test_staff_system.py
   ```

## Project Structure

```
Momentum/Python/
├── config.py                    # Configuration settings
├── simulation.py               # Legacy simulation entry point
├── enhanced_simulation.py      # Enhanced multi-discipline simulation
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
│
├── disciplines/                # Racing discipline engines
│   ├── multi_discipline_simulator.py  # Main coordinator
│   ├── base_engine.py          # Base engine interface
│   ├── single_seater/          # Single seater racing
│   ├── production_touring/     # Touring car racing
│   ├── rally_stage/            # Rally racing
│   ├── urban_street/           # Street racing
│   ├── drag_acceleration/      # Drag racing
│   ├── sprint_rallycross/      # Rallycross
│   └── endurance/              # Endurance racing
│
├── database/                   # Data persistence layer
│   ├── database_manager.py     # Database operations
│   ├── models.py               # Core entity models
│   └── models/
│       ├── multi_discipline_models.py  # Discipline-specific models
│       ├── staff_models.py     # Staff system models
│       └── supplier_models.py  # Supplier system models
│
├── systems/                    # Core simulation systems
│   ├── staff_management.py     # Staff hiring & operations
│   ├── currency_system.py      # Multi-currency support
│   ├── name_generator.py       # Hybrid name generation
│   ├── supplier_management.py  # Supplier relationships
│   ├── championship_manager.py # Championship tracking
│   └── vehicle_development.py  # R&D systems
│
├── data/                       # Static data and generators
│   ├── placeholder_names.py    # Generic names, teams, leagues
│   └── used_names.db           # Name uniqueness tracking database
│
├── vehicles/                   # Vehicle component systems
│   ├── vehicle.py              # Vehicle class
│   └── components/             # Vehicle components
│
├── tests/                      # Test suite
│   ├── simple_driver_test.py   # Basic driver system tests
│   ├── test_driver_system.py   # Comprehensive driver tests
│   └── test_staff_system.py    # Staff system tests
│
└── docs/                       # Documentation
    └── driver_system_summary.md
```

## Development Status

### ✅ Completed Systems

- **Multi-Discipline Racing Framework:** Seven complete discipline engines with unique simulation characteristics
- **Driver System:** 50+ attributes, cross-discipline compatibility, career progression modeling
- **Staff Management:** 40+ attributes, 25+ roles, budget-scaled hiring, performance multipliers
- **Currency System:** Multi-currency support with live exchange rates (EUR, USD, GBP, JPY, CHF)
- **Name Generation:** Intelligent system with Faker (guaranteed unique, culturally-appropriate names)
- **Supplier Management:** Engine, tire, and fuel suppliers with performance characteristics
- **Database Layer:** SQLite persistence with comprehensive models for all entities
- **Generic Content:** All placeholder names, teams, leagues, and personnel (no licensed content)

### 🚧 In Progress

- **Championship Management:** Season progression, points systems, standings
- **Vehicle Development:** R&D systems, component upgrades, performance progression
- **Financial Simulation:** Detailed budget allocation, sponsorship management, cost modeling
- **AI Decision Making:** Team strategy, driver selection, pit stop decisions

### 📋 Planned Features

- **API Layer:** FastAPI REST endpoints for external integrations
- **Advanced Analytics:** Telemetry analysis, performance prediction, strategy optimization
- **Historical Tracking:** Multi-season statistics, career records, team histories
- **Unity Frontend:** Visualization layer for race outcomes and team management UI

## Key Design Decisions

### No Licensed Content

All teams, drivers, series, tracks, and personnel are fictional and generated using:
- **Generic League Codes:** GPC1, WTC1, WRC1, etc. (not F1, NASCAR, WRC, etc.)
- **Placeholder Names:** Randomly generated from international name databases
- **Generic Team Names:** Procedurally generated from prefix + suffix combinations
- **Fictional Suppliers:** PowerTech, VelocityMotors, TurboMax, etc.

This approach avoids licensing costs and legal complications while maintaining authenticity.

### Backend-First Development

The Python simulation engine is being developed first to ensure:
- Realistic statistical modeling and simulation accuracy
- Comprehensive data structures and relationships
- Solid foundation for any frontend implementation
- Flexibility to add Unity, web, or other frontends later

### Cross-Discipline Driver System

Drivers can compete in all seven disciplines with varying effectiveness:
- **Discipline Preferences:** Each driver has aptitudes for different racing types
- **Attribute-Based Performance:** 50+ attributes determine capability across disciplines
- **Specialization vs. Versatility:** Trade-offs between mastery and flexibility
- **Realistic Transitions:** Drivers can move between disciplines with appropriate skill adjustments

## Testing

The project includes comprehensive test suites:

- **`tests/simple_driver_test.py`:** Basic driver system validation (50+ attributes, 7 disciplines)
- **`tests/test_driver_system.py`:** Advanced driver testing (career progression, specialization)
- **`tests/test_staff_system.py`:** Staff management validation (hiring, budgets, performance impact)

Run all tests:
```bash
cd Momentum/Python
python tests/simple_driver_test.py
python tests/test_driver_system.py
python tests/test_staff_system.py
```

## Documentation

Additional documentation available in the repository:

- **`Momentum/Python/README.md`:** Detailed Python backend documentation
- **`Momentum/Python/API_DOCUMENTATION.md`:** API specifications (when implemented)
- **`Momentum/Python/HYBRID_NAMES_SETUP.md`:** Name generation system guide
- **`Momentum/Python/SUPPLIER_SYSTEM_OVERVIEW.md`:** Supplier management details
- **`Momentum/Python/docs/driver_system_summary.md`:** Driver attribute breakdown

## Contributing

This is a final year Computer Science project. Contributions, suggestions, and feedback are welcome!

## Requirements

- **Python:** 3.11+
- **Database:** SQLite (included with Python)
- **No API Keys Required:** Fully offline operation with Faker-based name generation
