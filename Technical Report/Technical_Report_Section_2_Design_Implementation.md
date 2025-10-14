# Technical Report - Section 2.2 & 2.3: Design, Architecture & Implementation

## 2.2 Design & Architecture

### 2.2.1 System Architecture Overview

The Momentum system follows a **layered architecture** pattern with clear separation of concerns. The architecture is designed for modularity, testability, and future expansion.

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                            │
│  (Unity Frontend / Web Client / Mobile App / API Consumer)  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  /drivers   │  │   /teams    │  │ /simulate   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  Request Validation │ Response Formatting │ Error Handling  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              BUSINESS LOGIC LAYER                            │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Multi-Discipline Simulator               │       │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │       │
│  │  │Single│ │Touring│ │Rally │ │Street│ │ Drag │  │       │
│  │  │Seater│ │  Car │ │ Stage│ │ Race │ │ Race │  │       │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘  │       │
│  │  ┌──────┐ ┌──────┐                              │       │
│  │  │Rally │ │Endur-│                              │       │
│  │  │cross │ │ ance │                              │       │
│  │  └──────┘ └──────┘                              │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Staff     │  │  Currency   │  │     AI      │         │
│  │ Management  │  │   System    │  │   Engine    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              DATA ACCESS LAYER                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ DatabaseManager  │  │  DatabaseFactory │                │
│  └──────────────────┘  └──────────────────┘                │
│           ORM Mapping │ Query Builder │ Connection Pool     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER (SQLite)                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ Drivers │ │  Teams  │ │  Staff  │ │ Tracks  │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │  Races  │ │ Results │ │  Champ  │                      │
│  └─────────┘ └─────────┘ └─────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2.2 Component Design

#### **2.2.2.1 Multi-Discipline Simulation Engine**

The simulation engine is the core of the system. It uses a **Strategy Pattern** where each discipline implements the `BaseDisciplineEngine` interface with discipline-specific logic.

**Base Engine Interface:**
```python
class BaseDisciplineEngine(ABC):
    @abstractmethod
    def simulate_qualifying(self, context: DisciplineContext) -> List[RaceResult]
    
    @abstractmethod
    def simulate_race(self, context: DisciplineContext) -> List[RaceResult]
    
    @abstractmethod
    def calculate_performance_score(self, driver: Driver, team: Team) -> float
```

**Discipline Routing:**
The `MultiDisciplineSimulator` acts as a facade, routing requests to the appropriate engine:

```python
engines = {
    RacingDiscipline.SINGLE_SEATER: SingleSeaterEngine(),
    RacingDiscipline.RALLY_STAGE: RallyStageEngine(),
    # ... other engines
}

def simulate_race(self, race, drivers, teams):
    discipline = determine_discipline(race)
    engine = self.engines[discipline]
    return engine.simulate_race(context)
```

#### **2.2.2.2 Monte Carlo Simulation Algorithm**

The core simulation uses **Monte Carlo methods** to generate probabilistic race outcomes. The algorithm follows these steps:

**Algorithm: Monte Carlo Race Simulation**

```
INPUT: 
  - drivers: List of Driver objects with 50+ attributes
  - teams: Dictionary of Team objects
  - race: Race object with track and conditions
  - discipline: Racing discipline enum

OUTPUT:
  - results: Ordered list of RaceResult objects

ALGORITHM:

1. Calculate Base Performance Scores
   FOR EACH driver IN drivers:
     base_score = discipline_engine.calculate_performance_score(driver, team)
     // Uses weighted combination of relevant attributes
     // Example: single_seater_score = 0.3*raw_speed + 0.2*cornering + ...
   
2. Apply Team Modifiers
   FOR EACH driver IN drivers:
     team_multiplier = calculate_team_performance(team, staff)
     modified_score = base_score * team_multiplier
   
3. Apply Environmental Factors
   FOR EACH driver IN drivers:
     weather_mod = calculate_weather_impact(driver, conditions)
     track_mod = calculate_track_suitability(driver, track)
     final_base = modified_score * weather_mod * track_mod

4. Monte Carlo Sampling (N iterations)
   FOR iteration FROM 1 TO N:
     FOR EACH driver IN drivers:
       // Add random variance using normal distribution
       performance_sample = normal_distribution(
         mean = final_base,
         std_dev = consistency_factor(driver)
       )
       
       // Apply race incidents (mechanical failures, crashes)
       IF random() < incident_probability:
         performance_sample *= incident_penalty
       
       lap_times[driver][iteration] = calculate_lap_time(performance_sample)
     
     // Determine finishing order for this iteration
     results[iteration] = sort_by_total_time(lap_times)
   
5. Aggregate Results
   FOR EACH driver IN drivers:
     average_position = mean(positions_across_iterations)
     position_variance = std_dev(positions_across_iterations)
   
6. Apply Race Events (overtakes, pit stops, safety cars)
   final_results = apply_race_dynamics(aggregate_results)
   
7. Validate and Return Results
   VALIDATE finishing_order (no duplicates, all positions filled)
   RETURN final_results
```

**Statistical Properties:**
- Uses **Normal Distribution** for performance variance: μ = base_performance, σ = (100 - consistency) / 10
- **Incident probability** scales with discipline risk: Rally = 0.15, Single Seater = 0.05
- **Sample size** N = 100 iterations for balance of accuracy vs. performance

#### **2.2.2.3 Driver Performance Calculation**

Each discipline weights driver attributes differently. The calculation uses a **weighted sum** of relevant attributes:

**Example: Single Seater Performance Score**

$$
\text{Score}_{\text{single-seater}} = \sum_{i=1}^{n} w_i \cdot a_i
$$

Where:
- $w_i$ = weight for attribute $i$
- $a_i$ = driver's attribute value (0-100)
- Weights sum to 1.0: $\sum w_i = 1.0$

**Single Seater Weights:**
```python
weights = {
    'raw_speed': 0.25,           # Critical for qualifying
    'cornering_skill': 0.20,     # High-speed corners
    'racecraft': 0.15,           # Strategic positioning
    'consistency': 0.12,         # Maintaining pace
    'physical_fitness': 0.10,    # G-force tolerance
    'setup_knowledge': 0.08,     # Car optimization
    'tire_management': 0.10      # Stint performance
}
```

**Rally Stage Weights** (different emphasis):
```python
weights = {
    'vehicle_control': 0.30,     # Essential for gravel/snow
    'adaptability': 0.20,        # Changing surfaces
    'bravery': 0.15,            # Commitment to pace notes
    'spatial_awareness': 0.12,   # Narrow roads
    'consistency': 0.08,         # Less important in rally
    'setup_knowledge': 0.15      # Surface-specific setup
}
```

This creates **discipline-specific performance profiles** where drivers excel differently based on their attribute distribution.

### 2.2.3 Database Design

#### **Entity-Relationship Diagram**

```
┌─────────────────┐         ┌─────────────────┐
│     Driver      │         │      Team       │
├─────────────────┤         ├─────────────────┤
│ PK driver_id    │         │ PK team_id      │
│    name         │         │    name         │
│    nationality  │         │    budget       │
│    50+ attrs    │         │    discipline   │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │                           │
         │  ┌─────────────────┐     │
         └──┤   RaceResult    ├─────┘
            ├─────────────────┤
            │ PK result_id    │
            │ FK race_id      │───┐
            │ FK driver_id    │   │
            │ FK team_id      │   │
            │    position     │   │
            │    points       │   │
            │    fastest_lap  │   │
            └─────────────────┘   │
                                  │
            ┌─────────────────┐   │
            │      Race       │   │
            ├─────────────────┤   │
            │ PK race_id      │◄──┘
            │ FK champ_id     │───┐
            │ FK track_id     │─┐ │
            │    date         │ │ │
            │    weather      │ │ │
            └─────────────────┘ │ │
                                │ │
┌─────────────────┐             │ │    ┌─────────────────┐
│      Track      │◄────────────┘ │    │  Championship   │
├─────────────────┤               │    ├─────────────────┤
│ PK track_id     │               └────┤ PK champ_id     │
│    name         │                    │    name         │
│    length       │                    │    season       │
│    corners      │                    │    discipline   │
│    surface      │                    │    points_sys   │
└─────────────────┘                    └─────────────────┘

┌─────────────────┐         ┌─────────────────┐
│  StaffMember    │         │  TeamStaffing   │
├─────────────────┤         ├─────────────────┤
│ PK staff_id     │         │ FK team_id      │───┐
│    name         │         │ FK staff_id     │   │
│    role         │         │    hire_date    │   │
│    40+ attrs    │         │    salary       │   │
│    salary_req   │         └─────────────────┘   │
└─────────────────┘                               │
                                                  │
                            ┌─────────────────┐   │
                            │      Team       │◄──┘
                            └─────────────────┘
```

**Key Design Decisions:**

1. **Normalization**: Database is in **3rd Normal Form (3NF)** to eliminate redundancy
2. **Foreign Keys**: All relationships enforced with FK constraints
3. **Indexes**: Created on frequently queried fields (driver_id, team_id, race_id)
4. **Check Constraints**: Attribute values validated at database level (0-100 range)

### 2.2.4 API Design

**RESTful Endpoint Structure:**

```
GET    /                      # API information
GET    /health                # System status
GET    /stats                 # Database statistics

GET    /drivers               # List all drivers
GET    /drivers/{id}          # Get specific driver
POST   /drivers               # Create new driver
PUT    /drivers/{id}          # Update driver
DELETE /drivers/{id}          # Remove driver

GET    /teams                 # List all teams
GET    /teams?discipline=X    # Filter by discipline
POST   /teams                 # Create team

POST   /simulate/race         # Run race simulation
POST   /simulate/qualifying   # Run qualifying session
POST   /simulate/championship # Simulate full championship

GET    /staff                 # List available staff
POST   /staff/hire            # Hire staff member

GET    /championships         # List championships
GET    /championships/{id}/standings  # Current standings
```

**Request/Response Format:**

```json
// POST /simulate/race
{
  "race_id": 1,
  "discipline": "single_seater",
  "track_id": 5,
  "driver_ids": [1, 2, 3, 4, 5],
  "weather": "dry",
  "temperature": 25
}

// Response
{
  "race_id": 1,
  "results": [
    {
      "position": 1,
      "driver_id": 3,
      "driver_name": "Lewis Hamilton",
      "team_id": 2,
      "fastest_lap": "1:23.456",
      "points": 25
    },
    // ... more results
  ],
  "simulation_time": "0.234s",
  "incidents": []
}
```

---

## 2.3 Implementation

### 2.3.1 Key Modules and Classes

#### **2.3.1.1 Multi-Discipline Simulator**

**File:** `disciplines/multi_discipline_simulator.py`

This module coordinates all racing simulations:

```python
class MultiDisciplineSimulator:
    """Main coordinator for multi-discipline racing"""
    
    def __init__(self, seed: int = None):
        self.seed = seed
        self._engines: Dict[RacingDiscipline, BaseDisciplineEngine] = {}
        self._initialize_engines()
    
    def simulate_race(self, race: Race, drivers: List[Driver], 
                     teams: Dict[int, Team]) -> List[RaceResult]:
        """
        Main entry point for race simulation
        
        Routes to appropriate discipline engine and handles
        result aggregation and error handling.
        """
        # Determine racing discipline
        discipline = self._determine_discipline(race)
        
        # Get appropriate engine
        engine = self._get_engine(discipline)
        
        # Create context with all race data
        context = DisciplineContext(
            race=race,
            drivers=drivers,
            teams=teams,
            weather=race.weather,
            track=race.track
        )
        
        # Run simulation
        results = engine.simulate_race(context)
        
        return results
```

**Key Implementation Details:**
- Uses **Factory Pattern** to instantiate correct engine
- **Context Object** encapsulates all race data
- **Dependency Injection** allows engine swapping for testing

#### **2.3.1.2 Single Seater Engine**

**File:** `disciplines/single_seater/single_seater_engine.py`

Implements Formula-style racing simulation:

```python
class SingleSeaterEngine(BaseDisciplineEngine):
    """
    Single Seater racing simulation (Formula-style)
    
    Emphasizes: Raw speed, aerodynamics, tire management
    Low variance, high skill expression
    """
    
    def calculate_performance_score(self, driver: Driver, 
                                    team: Team) -> float:
        """
        Calculate performance score for single seater racing
        
        Formula uses weighted attributes emphasizing technical
        precision and consistency.
        """
        score = (
            driver.raw_speed * 0.25 +
            driver.cornering_skill * 0.20 +
            driver.racecraft * 0.15 +
            driver.consistency * 0.12 +
            driver.tire_management * 0.10 +
            driver.setup_knowledge * 0.08 +
            driver.physical_fitness * 0.10
        )
        
        # Apply team performance multiplier
        team_factor = self._calculate_team_impact(team)
        
        return score * team_factor
    
    def simulate_race(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate full race distance
        
        Implements:
        - Grid formation from qualifying
        - Lap-by-lap simulation with overtaking
        - Pit stop strategy
        - Safety car periods (probabilistic)
        - Tire degradation modeling
        """
        # Initialize race state
        race_state = self._initialize_race_state(context)
        
        # Simulate each lap
        for lap in range(1, context.race.total_laps + 1):
            # Update tire wear
            self._update_tire_degradation(race_state, lap)
            
            # Calculate lap times with degradation
            lap_times = self._calculate_lap_times(race_state)
            
            # Process overtakes
            self._process_overtakes(race_state, lap_times)
            
            # Check for pit stops
            self._process_pit_stops(race_state, lap)
            
            # Random incidents (low probability)
            self._process_incidents(race_state, lap)
        
        # Convert final state to RaceResults
        return self._generate_results(race_state)
```

**Interesting Implementation: Tire Degradation Model**

```python
def _calculate_tire_degradation(self, laps_on_tires: int, 
                                driver_skill: float) -> float:
    """
    Models tire performance degradation over stint
    
    Uses exponential decay modified by driver tire management skill.
    High skill = slower degradation
    
    Formula: grip = e^(-k * laps) where k depends on driver skill
    """
    # Base degradation rate
    k = 0.02  # 2% per lap baseline
    
    # Adjust for driver skill (0-100 scale)
    # Better drivers conserve tires: skill 100 = 0.5x degradation
    skill_factor = 1.0 - (driver_skill / 200.0)
    adjusted_k = k * skill_factor
    
    # Exponential decay
    grip_level = math.exp(-adjusted_k * laps_on_tires)
    
    # Cliff effect at lap 30+ (sudden dropoff)
    if laps_on_tires > 30:
        cliff_penalty = 0.95 ** (laps_on_tires - 30)
        grip_level *= cliff_penalty
    
    return grip_level
```

This creates realistic tire strategy where skilled drivers can extend stints while less skilled drivers must pit earlier.

#### **2.3.1.3 Staff Management System**

**File:** `systems/staff_management.py`

Handles team personnel and performance impact:

```python
class StaffManagementSystem:
    """
    Manages staff hiring, contracts, and performance impact
    """
    
    def calculate_performance_multiplier(self, team_staff: List[StaffMember],
                                        discipline: str) -> Dict[str, float]:
        """
        Calculate how staff capabilities affect team performance
        
        Returns multipliers for different performance areas:
        - technical: Car development speed
        - strategy: Race strategy quality
        - operations: Pit stop speed, reliability
        - information: Data quality and detail
        """
        multipliers = {
            'technical': 1.0,
            'strategy': 1.0,
            'operations': 1.0,
            'information': 1.0
        }
        
        # Group staff by role
        role_groups = self._group_by_role(team_staff)
        
        # Chief Engineer affects technical
        if StaffRole.CHIEF_ENGINEER in role_groups:
            chief = role_groups[StaffRole.CHIEF_ENGINEER][0]
            multipliers['technical'] = 1.0 + (chief.technical_knowledge / 100.0) * 0.3
        
        # Data Analysts affect information access
        if StaffRole.DATA_ANALYST in role_groups:
            analysts = role_groups[StaffRole.DATA_ANALYST]
            avg_skill = sum(a.data_analysis for a in analysts) / len(analysts)
            multipliers['information'] = 1.0 + (avg_skill / 100.0) * 0.5
        
        # Race Strategist affects strategy
        if StaffRole.RACE_STRATEGIST in role_groups:
            strategist = role_groups[StaffRole.RACE_STRATEGIST][0]
            multipliers['strategy'] = 1.0 + (strategist.tactical_thinking / 100.0) * 0.4
        
        return multipliers
```

**Information Fog-of-War Implementation:**

```python
def get_visible_race_data(self, team: Team, race_data: Dict) -> Dict:
    """
    Filter race data based on team's analyst quality
    
    Poor analysts = basic positions only
    Good analysts = lap times, gaps
    Excellent analysts = detailed telemetry, predictions
    """
    staff_quality = self._get_analyst_quality(team)
    
    visible_data = {'positions': race_data['positions']}  # Always visible
    
    if staff_quality > 30:
        visible_data['lap_times'] = race_data['lap_times']
    
    if staff_quality > 60:
        visible_data['gaps'] = race_data['gaps']
        visible_data['tire_wear'] = race_data['tire_wear']
    
    if staff_quality > 85:
        visible_data['predicted_pit_stops'] = self._predict_pit_windows(race_data)
        visible_data['competitor_fuel_levels'] = race_data['fuel_levels']
    
    return visible_data
```

This creates strategic depth where investing in better analysts provides competitive advantage through better information.

#### **2.3.1.4 Currency System**

**File:** `systems/currency_system.py`

Handles multi-currency financial operations:

```python
class CurrencySystem:
    """
    Multi-currency support with live exchange rates
    """
    
    def __init__(self):
        self.base_currency = Currency.EUR
        self.exchange_rates = {}
        self.cache_file = 'currency_cache.json'
        self._load_exchange_rates()
    
    def convert(self, amount: float, from_currency: Currency, 
                to_currency: Currency) -> float:
        """Convert amount between currencies"""
        if from_currency == to_currency:
            return amount
        
        # Convert through EUR base
        eur_amount = amount / self.exchange_rates[from_currency]
        target_amount = eur_amount * self.exchange_rates[to_currency]
        
        return round(target_amount, 2)
    
    def format_currency(self, amount: float, currency: Currency, 
                       locale: str = 'en_US') -> str:
        """
        Format currency with proper symbols and thousands separators
        
        Examples:
          EUR: "€1,234,567.89"
          USD: "$1,234,567.89"
          GBP: "£1,234,567.89"
          JPY: "¥1,234,568" (no decimals)
        """
        symbols = {
            Currency.EUR: '€',
            Currency.USD: '$',
            Currency.GBP: '£',
            Currency.JPY: '¥',
            Currency.CHF: 'CHF'
        }
        
        symbol = symbols[currency]
        
        # JPY doesn't use decimals
        if currency == Currency.JPY:
            formatted = f"{symbol}{amount:,.0f}"
        else:
            formatted = f"{symbol}{amount:,.2f}"
        
        return formatted
```

### 2.3.2 Database Implementation

**File:** `database/database_manager.py`

```python
class DatabaseManager:
    """
    Handles all database operations with connection pooling
    and transaction management
    """
    
    def __init__(self, db_path: str = "momentum.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def create_driver(self, driver: Driver) -> int:
        """Insert new driver with all attributes"""
        query = """
        INSERT INTO drivers (
            name, nationality, birth_date, age,
            raw_speed, consistency, racecraft,
            -- ... all 50+ attributes ...
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ...)
        """
        
        cursor = self.connection.cursor()
        cursor.execute(query, driver.to_tuple())
        self.connection.commit()
        
        return cursor.lastrowid
    
    def get_drivers_by_discipline_preference(self, 
                                            discipline: str,
                                            min_aptitude: float = 70.0) -> List[Driver]:
        """
        Find drivers suited for specific discipline
        
        Uses discipline-specific aptitude attributes
        """
        query = f"""
        SELECT * FROM drivers 
        WHERE {discipline}_aptitude >= ?
        ORDER BY {discipline}_aptitude DESC
        """
        
        cursor = self.connection.cursor()
        cursor.execute(query, (min_aptitude,))
        
        return [Driver.from_row(row) for row in cursor.fetchall()]
```

### 2.3.3 AI Decision Engine

**File:** `ai/decision_engine.py`

```python
class TeamAI:
    """
    AI agent making strategic decisions for teams
    """
    
    def decide_driver_signing(self, team: Team, 
                             available_drivers: List[Driver]) -> Optional[Driver]:
        """
        Decide which driver to sign based on:
        - Budget constraints
        - Team personality
        - Current driver quality
        - Championship position
        """
        # Calculate team needs
        current_driver_quality = self._assess_current_drivers(team)
        
        # Filter affordable drivers
        affordable = [d for d in available_drivers 
                     if self._can_afford(team, d)]
        
        if not affordable:
            return None
        
        # Rank by fit
        ranked = self._rank_drivers_by_fit(team, affordable)
        
        # Apply personality-based decision
        personality = TeamPersonality(team)
        
        if personality.risk_appetite > 0.7:
            # High risk = sign young talent
            return self._select_young_talent(ranked)
        else:
            # Low risk = sign experienced driver
            return self._select_experienced(ranked)
```

### 2.3.4 Code Quality Practices

**Docstrings:**
All functions include comprehensive docstrings:

```python
def calculate_lap_time(base_performance: float, track: Track, 
                      conditions: WeatherConditions) -> float:
    """
    Calculate lap time from performance score and conditions
    
    Args:
        base_performance: Driver performance score (0-100)
        track: Track object with length and characteristics
        conditions: Current weather and track conditions
    
    Returns:
        Lap time in seconds
    
    Raises:
        ValueError: If base_performance is outside valid range
    
    Example:
        >>> track = Track(name="Monaco", length=3.337)
        >>> conditions = WeatherConditions(temp=25, weather="dry")
        >>> calculate_lap_time(85.0, track, conditions)
        72.456
    """
```

**Type Hints:**
Python 3.8+ type hints used throughout:

```python
from typing import List, Dict, Optional, Tuple

def simulate_race(drivers: List[Driver], 
                 teams: Dict[int, Team]) -> List[RaceResult]:
    # Implementation
```

**Error Handling:**
Comprehensive exception handling:

```python
try:
    results = simulator.simulate_race(race, drivers, teams)
except DatabaseError as e:
    logger.error(f"Database error during simulation: {e}")
    raise HTTPException(status_code=500, detail="Database error")
except ValidationError as e:
    logger.warning(f"Invalid race configuration: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

**End of Section 2.2 & 2.3**

