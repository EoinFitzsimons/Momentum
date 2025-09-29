# Momentum Motorsport Simulation - Python Backend

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.7+-lightgrey.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Project Overview

**Momentum** is a comprehensive multi-discipline motorsport management simulation system designed as a final year Computer Science project. The system provides realistic race simulation capabilities across four major motorsport categories: Formula Racing, Rally, Endurance, and Street Racing.

The Python backend serves as the core simulation engine, utilizing Monte Carlo statistical methods to generate authentic race outcomes based on driver attributes, team performance, track characteristics, and environmental factors.

### 🎯 Key Features

- **Multi-Discipline Racing**: Support for Formula, Rally, Endurance, and Street racing
- **Monte Carlo Simulation**: Advanced probabilistic race outcome generation
- **Comprehensive Data Model**: Detailed driver, team, track, and championship entities
- **RESTful API**: FastAPI-based backend for frontend integration
- **Real-time Results**: Sub-second simulation performance for interactive use
- **Statistical Authenticity**: Realistic distribution of race results and upsets
- **Career Progression**: Long-term driver and team development tracking
- **Championship Management**: Multi-season competition tracking with standings

## 🏗️ System Architecture

```
Momentum Python Backend
├── 🎮 API Layer (FastAPI)
│   ├── REST Endpoints (/drivers, /teams, /simulate/race)
│   ├── Request/Response Models
│   └── Error Handling & Validation
│
├── 🧠 Simulation Engine (Monte Carlo)
│   ├── Race Outcome Calculation
│   ├── Driver Performance Modeling
│   ├── Team Performance Integration
│   └── Environmental Factor Processing
│
├── 💾 Data Layer (SQLite)
│   ├── Entity Models (Driver, Team, Track, Race)
│   ├── Relationship Management
│   ├── Data Integrity Constraints
│   └── Performance Optimization
│
└── ⚙️ Configuration & Utils
    ├── System Configuration
    ├── Constants & Settings
    └── Logging & Monitoring
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

### 🏎️ Race Simulation Engine

The Monte Carlo simulation engine is the heart of the system:

```python
# Example: Running a race simulation
from core.race_simulation import RaceSimulator, SimulationContext
from database.models import Race, Track, Driver, Team

# Initialize simulator
simulator = RaceSimulator(seed=12345)

# Create simulation context
context = SimulationContext(
    race=race_object,
    track=track_object,
    drivers=driver_list,
    teams=team_dict,
    weather_factor=0.8  # Light rain conditions
)

# Run simulation
results = simulator.simulate_race(context)
```

#### Simulation Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| **Driver Attributes** | 40% | skill, consistency, racecraft, adaptability, aggression |
| **Team Performance** | 30% | Budget, tier, operational excellence |
| **Environmental** | 20% | Track characteristics, weather conditions |
| **Randomization** | 10% | Mechanical reliability, incidents, luck |

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

### Driver Model
```python
@dataclass
class Driver:
    id: int                    # Unique identifier
    name: str                  # Full name
    nationality: str           # ISO country code
    skill: float              # Raw talent (0.0-1.0)
    consistency: float        # Reliability (0.0-1.0)
    racecraft: float          # Strategic intelligence (0.0-1.0)
    adaptability: float       # Environmental adaptation (0.0-1.0)
    aggression: float         # Risk-taking tendency (0.0-1.0)
    career_wins: int          # Total victories
    career_points: int        # Championship points earned
```

### Team Model
```python
@dataclass
class Team:
    id: int                   # Unique identifier
    name: str                 # Team name
    discipline: str           # formula/rally/endurance/street
    tier: str                 # tier1/tier2/tier3
    budget: float             # Annual budget (millions USD)
    total_wins: int           # Career victories
    championships: int        # Championship titles
```

## 🎮 Racing Disciplines

### Formula Racing
- **Categories**: F1, F2, F3
- **Characteristics**: High speed, technical precision
- **Key Attributes**: skill, racecraft, consistency

### Rally Racing
- **Categories**: WRC, WRC2, WRC3
- **Characteristics**: Varied surfaces, navigation challenges
- **Key Attributes**: adaptability, skill, aggression

### Endurance Racing
- **Categories**: LMP1, LMP2, GTE
- **Characteristics**: Long-distance, strategy-focused
- **Key Attributes**: consistency, racecraft, adaptability

### Street Racing
- **Categories**: GT3, GT4, Touring
- **Characteristics**: Close competition, production-based
- **Key Attributes**: racecraft, aggression, skill

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

### Simulation Performance
- **Monte Carlo Iterations**: 1000 (configurable)
- **Simulation Time**: <1 second for 20-car grid
- **Memory Usage**: <50MB for typical datasets
- **Scalability**: Supports up to 50 participants per race

### Database Performance
- **SQLite Optimization**: Strategic indexing on key queries
- **Connection Management**: Efficient connection pooling
- **Query Performance**: Sub-millisecond for typical operations
- **Storage**: <10MB for comprehensive season data

## 🚀 Future Enhancements

### Planned Features
- [ ] **Multi-threaded Simulations** - Parallel race processing
- [ ] **Advanced AI Strategies** - Machine learning-based team decisions
- [ ] **Weather System Expansion** - Dynamic weather changes during races
- [ ] **Driver Development** - Skill progression over career
- [ ] **Economic Simulation** - Team budget management and sponsorship

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributors

- **Primary Developer**: Final Year Computer Science Student
- **Project Supervisor**: [Supervisor Name]
- **Institution**: [University Name]

---

*This project is submitted as part of a Final Year Computer Science degree program, demonstrating advanced software development skills, system architecture design, and statistical modeling capabilities.*