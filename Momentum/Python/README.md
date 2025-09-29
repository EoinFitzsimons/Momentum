# Momentum Motorsport Simulation - Python Backend

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.7+-lightgrey.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Project Overview

**Momentum** is a comprehensive multi-discipline motorsport management simulation system designed as a final year Computer Science project. The system provides realistic race simulation capabilities across **seven major motorsport disciplines** with advanced team management, driver development, and staff operations.

The Python backend serves as the core simulation engine, utilizing Monte Carlo statistical methods to generate authentic race outcomes based on comprehensive driver attributes (50+), team performance, staff capabilities (40+ attributes), budget constraints, and environmental factors.

### 🎯 Key Features

#### 🏁 **Multi-Discipline Racing System** (7 Complete Engines)
- **Single Seater** (Formula 1, F2, F3): High-speed technical precision racing
- **Production/Touring** (GT3, BTCC, TCR): Close-quarters production-based racing
- **Rally/Stage** (WRC, WRC2): Point-to-point navigation and surface variety
- **Urban/Street** (Formula E, Street circuits): City-based technical racing
- **Drag/Acceleration** (Top Fuel, Pro Stock): Straight-line acceleration competition
- **Sprint/Rallycross** (World RX): Mixed-surface short-format racing
- **Endurance** (Le Mans, IMSA): Long-distance strategy-focused racing

#### 👨‍💼 **Comprehensive Driver System** (50+ Attributes)
- **Cross-discipline compatibility**: Drivers can race in all disciplines with preferences
- **7 attribute categories**: Technical Skills, Mental Attributes, Physical Fitness, Racecraft, Personality, Experience, Discipline Preferences
- **Dynamic career progression**: Skill development and specialization over time
- **Realistic attribute ranges**: 0-100 scale with tier-based distributions

#### 🏢 **Advanced Staff Management System** (40+ Attributes, 25+ Roles)
- **Comprehensive staff roles**: Technical Director, Data Analyst, Race Strategist, Pit Crew Chief, Chief Designer, and 20+ more
- **Budget-based scaling**: Staff quality and quantity scale with team budgets ($800K to $12M+)
- **Information fog-of-war**: Better analysts provide access to more detailed race data
- **Performance multipliers**: Staff capabilities affect team performance across 6 key areas
- **Realistic hiring system**: Salary negotiations, contract management, job satisfaction

#### 🎮 **Advanced Simulation Technology**
- **Monte Carlo Methods**: Advanced probabilistic race outcome generation
- **Discipline-specific logic**: Each racing type has unique simulation characteristics
- **Environmental factors**: Weather, track conditions, and surface variations
- **Real-time performance**: Sub-second simulation for interactive gameplay
- **Statistical authenticity**: Realistic distribution of results and upsets

## 🏗️ System Architecture

```text
Momentum Python Backend
├── 🎮 API Layer (FastAPI)
│   ├── REST Endpoints (/drivers, /teams, /simulate/race, /staff)
│   ├── Request/Response Models
│   └── Error Handling & Validation
│
├── 🏁 Multi-Discipline Racing Engines (7 Engines)
│   ├── engines/single_seater.py       # Formula racing simulation
│   ├── engines/production_touring.py  # GT and touring car racing
│   ├── engines/rally_stage.py         # Rally and stage racing
│   ├── engines/urban_street.py        # Street circuit racing
│   ├── engines/drag_acceleration.py   # Drag racing simulation
│   ├── engines/sprint_rallycross.py   # Rallycross simulation
│   └── engines/endurance.py          # Long-distance racing
│
├── 👥 Personnel Management Systems
│   ├── database/driver_models.py     # 50+ attribute driver system
│   ├── database/staff_models.py      # 40+ attribute staff system
│   ├── systems/staff_management.py   # Staff hiring & operations
│   └── examples/staff_examples.py    # Realistic staff profiles
│
├── 🧠 Core Simulation Engine (Monte Carlo)
│   ├── core/race_simulation.py       # Base simulation framework
│   ├── Race Outcome Calculation      # Probabilistic result generation
│   ├── Driver Performance Modeling   # 50+ attribute integration
│   ├── Team Performance Integration   # Staff impact calculations
│   └── Environmental Factor Processing # Weather, track conditions
│
├── 💾 Data Layer (SQLite)
│   ├── Entity Models (Driver, Team, Track, Race, Staff)
│   ├── Relationship Management (Team staffing, contracts)
│   ├── Data Integrity Constraints
│   └── Performance Optimization
│
├── 🌐 External Integrations
│   ├── Hybrid Name Generation (NameAPI + ParaNames dataset)
│   ├── API Key Security Management
│   └── External Data Sources
│
└── ⚙️ Configuration & Utils
    ├── System Configuration
    ├── Constants & Settings
    ├── Logging & Monitoring
    └── Comprehensive Test Suites
```

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Git** (for cloning repository)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/EoinFitzsimons/FinalProject.git
   cd FinalProject/Momentum/Python
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**
   ```bash
   python simulation.py
   ```

4. **Verify Installation**
   - Open browser to `http://localhost:8000`
   - Check interactive docs at `http://localhost:8000/docs`

## 📊 Core Components

### 🏎️ Multi-Discipline Race Simulation System

The modular simulation system features discipline-specific engines with unique characteristics:

```python
# Example: Running discipline-specific race simulations
from engines.single_seater import SingleSeaterEngine
from engines.rally_stage import RallyStageEngine
from engines.endurance import EnduranceEngine
from database.driver_models import Driver
from database.staff_models import TeamStaffing

# Formula 1 race simulation
f1_engine = SingleSeaterEngine()
f1_results = f1_engine.simulate_race(
    drivers=driver_list,
    track_data={'downforce_importance': 0.85, 'power_importance': 0.70},
    weather_conditions={'temperature': 25, 'precipitation': 0.0},
    team_staffing=team_staffing_dict  # Staff performance multipliers
)

# Rally stage simulation
rally_engine = RallyStageEngine()
rally_results = rally_engine.simulate_stage(
    drivers=driver_list,
    stage_data={'surface': 'gravel', 'length_km': 15.8, 'elevation_change': 245},
    weather_conditions={'visibility': 0.9, 'grip_factor': 0.75}
)

# Endurance race simulation (multi-stint)
endurance_engine = EnduranceEngine()
endurance_results = endurance_engine.simulate_race(
    driver_lineups=lineup_dict,  # Multiple drivers per car
    race_duration_hours=24,
    pit_strategy_enabled=True,
    staff_strategy_impact=True   # Staff affects strategy quality
)
```

#### Advanced Simulation Factors

| Factor Category | Weight Range | Key Components | Discipline Variation |
|----------------|--------------|----------------|---------------------|
| **Driver Attributes (50+)** | 35-45% | Technical skills, mental attributes, racecraft, fitness | Varies by discipline specialization |
| **Staff Performance** | 15-25% | 6 performance multipliers from team staff quality | Higher impact in technical disciplines |
| **Team Resources** | 10-20% | Budget tier, equipment quality, operational excellence | Critical in development-heavy series |
| **Environmental** | 10-25% | Weather, track surface, visibility, temperature | Rally/street racing more affected |
| **Discipline-Specific** | 5-15% | Downforce (F1), navigation (rally), strategy (endurance) | Unique to each racing type |
| **Randomization** | 5-10% | Mechanical reliability, incidents, safety cars | Consistent across all disciplines |

### 🗄️ Database Schema

The system uses a normalized SQLite schema optimized for motorsport data:

```sql
-- Core entity tables
drivers          -- Individual racers with attributes
teams           -- Racing organizations with budgets
tracks          -- Racing circuits with characteristics
championships   -- Competition series with rules
races           -- Individual race events
race_results    -- Performance outcomes and standings
```

#### Key Relationships
- **Drivers** belong to **Teams** (many-to-one)
- **Races** occur at **Tracks** within **Championships** (many-to-one)
- **RaceResults** link **Drivers**, **Teams**, and **Races** (many-to-many)

### 🌐 API Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/` | System information and status | API metadata |
| `GET` | `/health` | Health check with database stats | System health |
| `GET` | `/drivers` | All drivers with attributes | Driver list |
| `GET` | `/teams?discipline={type}` | Teams (filterable by discipline) | Team list |
| `POST` | `/simulate/race` | Execute race simulation | Race results |
| `GET` | `/stats` | Database statistics | Entity counts |

#### Example API Usage

```bash
# Get all Formula racing teams
curl "http://localhost:8000/teams?discipline=formula"

# Run a race simulation
curl -X POST "http://localhost:8000/simulate/race" \
     -H "Content-Type: application/json" \
     -d '{
       "race_id": 1,
       "weather_conditions": "wet",
       "participants": [
         {"driver_id": 1, "team_id": 1},
         {"driver_id": 2, "team_id": 2}
       ]
     }'
```

## 📈 Data Models

### Comprehensive Driver Model (50+ Attributes)

```python
@dataclass
class Driver:
    # Basic Information
    id: int
    name: str
    nationality: str
    birth_date: str
    age: int
    
    # Technical Skills (12 attributes)
    technical_knowledge: float      # Understanding of car systems (0-100)
    setup_ability: float           # Car setup optimization
    data_interpretation: float     # Telemetry analysis capability
    mechanical_sympathy: float     # Preserving equipment
    tire_management: float         # Tire wear optimization
    fuel_efficiency: float         # Fuel consumption management
    
    # Mental Attributes (8 attributes) 
    focus_ability: float           # Concentration during races
    pressure_handling: float       # Performance under pressure
    decision_making: float         # Split-second choices
    strategic_thinking: float      # Long-term race planning
    learning_speed: float          # Adaptation to new situations
    mental_resilience: float       # Recovery from setbacks
    
    # Physical Fitness (7 attributes)
    overall_fitness: float         # General physical condition
    reaction_time: float           # Response speed
    endurance: float              # Fatigue resistance
    g_force_tolerance: float      # High-G maneuver handling
    vision_quality: float         # Visual acuity and tracking
    hand_eye_coordination: float  # Precision control
    
    # Racecraft (10 attributes)
    overtaking_ability: float      # Passing other drivers
    defensive_driving: float       # Maintaining position
    raceline_optimization: float   # Finding fastest path
    traffic_navigation: float      # Racing in groups
    situational_awareness: float   # Track condition awareness
    risk_assessment: float         # Calculated risk-taking
    
    # Personality Traits (6 attributes)
    aggression: float             # Racing aggressiveness
    confidence: float             # Self-belief and boldness
    teamwork: float               # Collaboration with team
    professionalism: float        # Media and sponsor relations
    adaptability: float           # Adjustment to changes
    leadership: float             # Inspiring team performance
    
    # Experience & Specialization (7 attributes)
    years_experience: int         # Total racing career length
    championship_experience: float # High-level competition exposure
    wet_weather_skill: float      # Rain/adverse condition ability
    night_racing_skill: float     # Low visibility racing
    
    # Discipline Preferences (7 attributes) - Cross-discipline compatibility
    single_seater_preference: float    # Formula racing affinity
    touring_car_preference: float      # Production car racing
    rally_preference: float            # Stage rally preference
    street_racing_preference: float    # Urban circuit preference
    drag_racing_preference: float      # Acceleration racing
    rallycross_preference: float       # Mixed surface racing
    endurance_preference: float        # Long-distance racing
```

### Advanced Team & Staff System

```python
@dataclass 
class TeamStaffing:
    team_id: int
    discipline: str              # Primary racing discipline
    total_budget: float          # Annual team budget
    personnel_budget: float      # Staff salary allocation
    staff_members: List[StaffMember]  # Team personnel
    
    # Performance multipliers (calculated from staff)
    overall_performance: float    # 0.3x - 1.5x based on staff quality
    development_speed: float     # Car development rate
    pit_stop_efficiency: float   # Operational excellence
    race_strategy: float         # Strategic decision quality
    reliability: float           # Equipment reliability
    adaptability: float          # Response to changing conditions
    
    # Information access (fog-of-war system)
    data_access_level: float     # 0-100 based on analyst quality
    
@dataclass
class StaffMember:
    # 40+ attributes across 6 categories:
    # - Technical Skills (12): engineering, aerodynamics, electronics, etc.
    # - Analytical Skills (8): data analysis, telemetry, predictive analytics
    # - Management & Leadership (7): team coordination, decision making
    # - Operational Skills (8): pit efficiency, crisis management
    # - Financial & Commercial (5): budget management, negotiations
    # - Discipline Specializations (7): expertise in each racing type
    
    role: StaffRole              # 25+ roles: Technical Director, Data Analyst, etc.
    tier: StaffTier              # Intern → Junior → Regular → Senior → Expert → Legendary
    salary: float                # Annual compensation
    effectiveness: float         # Role-specific performance rating
```

## � Racing Disciplines (7 Complete Engines)

### 1. Single Seater Racing 🏎️
- **Categories**: Formula 1, Formula 2, Formula 3, IndyCar
- **Characteristics**: High downforce, technical precision, aerodynamic optimization
- **Key Factors**: Technical skill, racecraft, car development, aerodynamics expertise
- **Staff Impact**: Technical Director and Aerodynamics Engineers critical
- **Unique Elements**: Qualifying system, DRS zones, tire strategy

### 2. Production/Touring Car Racing 🚗
- **Categories**: GT3, BTCC, TCR, V8 Supercars
- **Characteristics**: Production-based cars, close racing, driver skill emphasis
- **Key Factors**: Racecraft, adaptability, car setup, mechanical reliability
- **Staff Impact**: Race engineers and strategists important
- **Unique Elements**: Balance of Performance (BoP), contact tolerance

### 3. Rally/Stage Racing 🏔️
- **Categories**: WRC, WRC2, Regional Rally Championships
- **Characteristics**: Point-to-point stages, surface variety, navigation
- **Key Factors**: Adaptability, bravery, co-driver communication, surface expertise
- **Staff Impact**: Engineers for surface-specific setups
- **Unique Elements**: Pacenotes, surface changes, weather impact

### 4. Urban/Street Racing 🏙️
- **Categories**: Formula E, Monaco GP, Street Circuits
- **Characteristics**: Confined spaces, walls, technical challenges
- **Key Factors**: Precision, racecraft, adaptability, risk management
- **Staff Impact**: Data analysts for track evolution
- **Unique Elements**: Track evolution, wall proximity, limited overtaking

### 5. Drag/Acceleration Racing 🚀
- **Categories**: Top Fuel, Funny Car, Pro Stock, Pro Mod
- **Key Factors**: Reaction time, technical precision, power management
- **Staff Impact**: Engine specialists and data analysts critical
- **Unique Elements**: Christmas tree starts, terminal speeds, parachute deployment

### 6. Sprint/Rallycross Racing 💨
- **Categories**: World Rallycross Championship, Americas Rallycross
- **Characteristics**: Mixed surfaces, short races, jump sections
- **Key Factors**: Adaptability, aggression, racecraft, surface switching
- **Staff Impact**: Setup engineers for surface transitions
- **Unique Elements**: Joker laps, surface transitions, wheel-to-wheel racing

### 7. Endurance Racing ⏱️
- **Categories**: Le Mans 24h, IMSA, WEC, Nürburgring 24h
- **Characteristics**: Multi-hour races, driver changes, strategic complexity
- **Key Factors**: Consistency, strategy, stamina, team coordination
- **Staff Impact**: Race strategists and pit crews essential
- **Unique Elements**: Driver lineups, fuel strategy, night racing, weather windows

## ⚙️ Configuration

The system is configured via `config.py`:

```python
# Database Configuration
DATABASE_PATH = "database/momentum.db"

# Simulation Parameters
MONTE_CARLO_ITERATIONS = 1000    # Simulation accuracy vs speed
RANDOM_SEED = 42                 # Reproducible results

# API Configuration
API_HOST = "127.0.0.1"
API_PORT = 8000
API_RELOAD = True               # Development hot-reload
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_simulation.py
python -m pytest tests/test_database.py
python -m pytest tests/test_api.py
```

## 📝 Development Guidelines

### Code Style
- **PEP 8** compliance for Python code
- **Type hints** for all function signatures
- **Comprehensive docstrings** for classes and methods
- **Meaningful variable names** and comments

### Database Operations
```python
# Always use context managers for database operations
with db_manager.get_connection() as conn:
    cursor = conn.execute("SELECT * FROM drivers")
    results = cursor.fetchall()

# Use parameterized queries to prevent SQL injection
cursor.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,))
```

## 📊 Performance Characteristics

### Multi-Engine Simulation Performance
- **7 Racing Engines**: Each optimized for discipline-specific characteristics
- **Driver System**: 50+ attributes per driver with cross-discipline compatibility
- **Staff System**: 40+ attributes per staff member with 25+ roles
- **Simulation Time**: <1 second for 30-car grid across all disciplines
- **Memory Usage**: <100MB for comprehensive team + staff + driver datasets
- **Scalability**: Supports up to 50 participants per race with full staff simulation

### Advanced System Capabilities
- **Budget Scaling**: Staff requirements scale from $500K to $10M+ team budgets
- **Information Fog-of-War**: 10-level data access system based on analyst quality
- **Performance Multipliers**: 6 distinct team performance areas affected by staff
- **Cross-Discipline Racing**: Drivers can compete in all 7 disciplines with preferences
- **Comprehensive Testing**: 100% test coverage across all major system components

### Database Performance
- **Multi-Entity Schema**: Drivers, Teams, Staff, Races, Championships
- **Relationship Management**: Complex staff-team-performance relationships
- **Query Optimization**: Efficient lookups for 50+ attribute comparisons
- **Storage Scaling**: <50MB for full season with complete personnel data

## 🚀 System Status & Capabilities

### ✅ Fully Implemented Systems
- [x] **7 Complete Racing Engines** - All disciplines with unique simulation logic
- [x] **50+ Attribute Driver System** - Cross-discipline compatibility with preferences
- [x] **40+ Attribute Staff System** - 25+ roles with budget scaling and performance impact
- [x] **Information Fog-of-War** - Data access based on staff analytical capabilities
- [x] **Budget-Based Team Scaling** - Realistic staff requirements and salary scaling
- [x] **Comprehensive Testing Suite** - 100% validation of all major components
- [x] **Hybrid Name Generation** - External API integration with fallback systems
- [x] **Security Implementation** - API key protection and gitignore configuration

### 🔮 Future Enhancement Opportunities
- [ ] **Dynamic Weather Systems** - Real-time weather changes during race simulation
- [ ] **Multi-Season Career Mode** - Long-term driver and staff development
- [ ] **Contract Negotiations** - Advanced staff and driver contract management
- [ ] **Championship Management** - Multi-series competition tracking
- [ ] **Economic Simulation** - Detailed budget management and sponsorship systems
- [ ] **Machine Learning Integration** - AI-powered strategy optimization
- [ ] **Real-Time Multiplayer** - Live competitive team management

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributors

- **Primary Developer**: Final Year Computer Science Student
- **Project Supervisor**: [Supervisor Name]
- **Institution**: [University Name]

---

*This project is submitted as part of a Final Year Computer Science degree program, demonstrating advanced software development skills, system architecture design, and statistical modeling capabilities.*