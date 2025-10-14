# Technical Report - Section 2.1: Requirements

## 2.1 Requirements

All requirements in the Momentum system are designed to be **verifiable and testable**. For example: "The system shall simulate a complete race with 20 drivers in under 1 second on standard hardware" or "Driver attributes shall influence race outcomes with measurable statistical correlation of at least 0.7."

### 2.1.1 Functional Requirements

The following functional requirements are listed in priority order:

---

#### **Requirement 1: Multi-Discipline Race Simulation**

**Priority:** CRITICAL

**Description:**  
The system must be capable of simulating realistic races across seven different motorsport disciplines (Single Seater, Production/Touring, Rally/Stage, Urban/Street, Drag/Acceleration, Sprint/Rallycross, Endurance). Each discipline must have unique simulation logic reflecting real-world racing characteristics.

**Verification Criteria:**
- Each discipline engine produces distinct result patterns
- Simulation completes within 1 second for 20-driver races
- Results show statistical correlation (r > 0.7) with driver attributes
- Upset victories occur at realistic frequencies (5-15% depending on discipline)

---

#### **Use Case 1.1: Simulate Single Race Event**

**Scope:**  
This use case covers the execution of a single race simulation from initialization to result generation.

**Description:**  
This use case describes how the system processes a race simulation request, applies discipline-specific logic, calculates driver performance based on 50+ attributes, and generates realistic race results.

**Actors:**
- **Primary Actor:** Game Client (Unity/Web Frontend)
- **Secondary Actors:** Database System, Simulation Engine

**Preconditions:**
- Race configuration is valid (discipline, track, participants)
- All participating drivers exist in database with complete attribute sets
- Track data is available for selected circuit
- Simulation engine is initialized and ready

**Main Flow:**

1. Client sends POST request to `/simulate/race` with race configuration
2. API validates request parameters and checks data integrity
3. System loads driver data from database (See A1: Driver Not Found)
4. System loads team data and associates drivers with teams
5. System determines discipline type from race configuration
6. System routes request to appropriate discipline engine (SingleSeaterEngine, RallyStageEngine, etc.)
7. Discipline engine creates simulation context with all relevant data
8. Engine calculates base performance scores for each driver using attribute formulas
9. Engine applies team modifiers based on staff capabilities and budget
10. Engine applies environmental factors (weather, track conditions)
11. Monte Carlo simulation generates race outcome using probabilistic methods
12. System records race results to database (See E1: Database Write Failure)
13. System returns formatted race results to client

**Alternate Flows:**

**A1: Driver Not Found**
1. System detects missing driver in database
2. System returns HTTP 404 error with driver ID
3. Client displays error message to user
4. Use case terminates

**A2: Invalid Discipline**
1. System detects unsupported discipline type
2. System returns HTTP 400 error with supported disciplines list
3. Client prompts user to select valid discipline
4. Use case returns to step 6 of main flow

**Exceptional Flows:**

**E1: Database Write Failure**
1. System fails to write race results to database
2. System logs error with full stack trace
3. System returns HTTP 500 error to client
4. Race results are held in memory for retry
5. System attempts automatic retry (max 3 attempts)
6. If all retries fail, use case terminates with error

**E2: Simulation Timeout**
1. Simulation exceeds 5-second timeout threshold
2. System terminates simulation thread
3. System logs performance warning with race parameters
4. System returns HTTP 503 error (Service Temporarily Unavailable)
5. Use case terminates

**Postconditions:**
- Race results are persisted in database
- Championship standings are updated (if applicable)
- Driver statistics are incremented
- System returns to idle state ready for next request

---

#### **Requirement 2: Driver Management System**

**Priority:** CRITICAL

**Description:**  
The system must maintain comprehensive driver profiles with 50+ attributes across 7 categories. Drivers must be capable of competing in any discipline with performance modifiers based on their specialization preferences.

**Verification Criteria:**
- All 50+ driver attributes are stored and retrievable
- Driver performance varies measurably across disciplines
- Attribute ranges are validated (0-100 scale)
- Driver specializations affect race outcomes

**Use Case 2.1: Retrieve Driver Information**

**Scope:** Accessing complete driver data including all attributes and statistics

**Main Flow:**
1. Client requests driver list via GET `/drivers`
2. System queries database for all driver records
3. System applies optional filters (nationality, discipline preference, age range)
4. System formats driver data as JSON response
5. Client receives driver list with all attributes

**Postconditions:** Driver data is returned without database modifications

---

#### **Requirement 3: Team and Staff Management**

**Priority:** HIGH

**Description:**  
The system must support comprehensive team management with 40+ staff attributes across 25+ roles. Staff quality and quantity must scale with team budget, affecting performance multipliers and information access.

**Verification Criteria:**
- Staff members have complete attribute sets
- Budget constraints are enforced during hiring
- Staff performance multipliers affect race outcomes
- Information fog-of-war works correctly based on analyst quality

**Use Case 3.1: Hire Staff Member**

**Scope:** Team recruitment and staff onboarding process

**Main Flow:**
1. Team queries available staff market
2. System generates staff candidates based on budget tier
3. User selects candidate and initiates negotiation
4. System calculates salary requirements based on staff attributes
5. User offers contract terms (salary, duration, bonuses)
6. System evaluates offer against staff expectations
7. If accepted, staff member joins team roster
8. Team budget is reduced by salary commitment
9. Performance multipliers are recalculated

**Alternate Flows:**
**A1: Insufficient Budget**
- System rejects hire attempt
- Returns error indicating budget shortfall

**A2: Offer Rejected**
- Staff counter-offers with higher salary
- User can accept, negotiate, or decline

---

#### **Requirement 4: Multi-Currency Financial System**

**Priority:** MEDIUM

**Description:**  
The system must support financial transactions in multiple currencies (EUR, USD, GBP, JPY, CHF) with real-time exchange rates. All budget caps and salary calculations must respect currency conversions.

**Verification Criteria:**
- Exchange rates update within 24 hours
- Currency conversions are mathematically accurate
- Budget caps are enforced in all supported currencies
- Locale-specific formatting displays correctly

---

#### **Requirement 5: Championship Management**

**Priority:** MEDIUM

**Description:**  
The system must track championships across multiple seasons with points systems, standings, and historical records.

**Verification Criteria:**
- Points are calculated correctly per discipline rules
- Standings update after each race
- Historical data is preserved across seasons
- Tie-breaking rules apply correctly

---

#### **Requirement 6: AI Decision Making**

**Priority:** LOW (Future Enhancement)

**Description:**  
AI-controlled teams must make autonomous strategic decisions including driver signings, budget allocation, and race strategy based on team personality traits.

**Verification Criteria:**
- AI decisions reflect team personality
- Decisions are explainable with reasoning
- AI competitive balance is maintained
- Decision variety prevents predictable patterns

---

### 2.1.2 Data Requirements

**Database Schema:**

The system requires persistent storage for the following entities:

1. **Drivers Table**
   - Primary Key: `driver_id` (INTEGER)
   - 50+ attribute columns (REAL, 0.0-100.0 range)
   - Biographical data: name, nationality, birth_date, age
   - Career statistics: races, wins, podiums, championships
   - Constraints: CHECK constraints on attribute ranges

2. **Teams Table**
   - Primary Key: `team_id` (INTEGER)
   - Budget (REAL), discipline (TEXT), tier (INTEGER)
   - Performance attributes: innovation, risk_appetite, management_quality
   - Career statistics: championships, total_wins

3. **Staff Table**
   - Primary Key: `staff_id` (INTEGER)
   - Foreign Key: `team_id` references Teams
   - 40+ attribute columns for role-specific skills
   - Contract data: salary, contract_end_date, job_satisfaction

4. **Tracks Table**
   - Primary Key: `track_id` (INTEGER)
   - Physical characteristics: length, corners, elevation_change
   - Surface data: surface_type, grip_level
   - Challenge ratings: technical_challenge, overtaking_difficulty

5. **Championships Table**
   - Primary Key: `championship_id` (INTEGER)
   - Series configuration: discipline, points_system, race_count

6. **Races Table**
   - Primary Key: `race_id` (INTEGER)
   - Foreign Keys: championship_id, track_id
   - Conditions: weather, temperature, track_condition

7. **RaceResults Table**
   - Primary Key: `result_id` (INTEGER)
   - Foreign Keys: race_id, driver_id, team_id
   - Performance data: position, fastest_lap, points_earned

**Data Integrity:**
- Foreign key constraints enforce referential integrity
- CHECK constraints validate attribute ranges
- UNIQUE constraints prevent duplicate entries
- NOT NULL constraints on critical fields

**Performance Optimization:**
- Indexes on frequently queried fields (driver_id, team_id)
- Composite indexes on race lookups (championship_id, race_id)
- Query optimization for large result sets

---

### 2.1.3 User Requirements

**Target Users:**
1. **Motorsport Enthusiasts**: Players with deep knowledge of racing who want realistic simulation
2. **Casual Gamers**: Players seeking accessible motorsport management without overwhelming complexity
3. **Developers**: API consumers building frontend applications

**User Needs:**

**For Motorsport Enthusiasts:**
- Detailed driver and team statistics
- Realistic race outcomes reflecting real-world physics
- Deep customization and strategy options
- Historical data and career progression tracking

**For Casual Gamers:**
- Simplified interfaces with sensible defaults
- Quick race simulations without excessive configuration
- Clear feedback on decision impacts
- Engaging narratives and emergent storylines

**For Developers:**
- Clear API documentation with examples
- Consistent data formats (JSON)
- Error messages with actionable information
- Rate limiting and authentication (future)

---

### 2.1.4 Environmental Requirements

**Hardware Requirements:**
- **Minimum:** 2GB RAM, 500MB disk space, 1GHz dual-core CPU
- **Recommended:** 4GB RAM, 1GB disk space, 2GHz quad-core CPU

**Software Requirements:**
- **Operating System:** Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)
- **Python:** Version 3.8 or higher
- **Database:** SQLite 3.7+
- **Network:** Internet connection for currency exchange rates (optional)

**Deployment Requirements:**
- **Development:** Local uvicorn server on localhost:8000
- **Production:** ASGI-compatible server (uvicorn, gunicorn)
- **Database:** File-based SQLite (momentum.db)
- **API Keys:** Optional for external services (currency rates)

**Scalability Considerations:**
- API can run multiple worker processes
- Database can migrate to PostgreSQL/MySQL for multi-user scenarios
- Stateless design enables horizontal scaling

---

### 2.1.5 Usability Requirements

**Response Time:**
- API endpoints must respond within 200ms for data retrieval
- Race simulations must complete within 1 second
- Database queries must return results within 100ms

**Accessibility:**
- API documentation must be auto-generated and browsable
- Error messages must be human-readable with clear guidance
- JSON responses must follow consistent naming conventions

**Reliability:**
- System uptime target: 99% during operation
- Graceful error handling with no data corruption
- Automatic database backup capabilities

**Learnability:**
- API endpoint naming must be intuitive and RESTful
- Code examples provided for common use cases
- Comprehensive README documentation

**API Design Standards:**
- RESTful principles (GET, POST, PUT, DELETE)
- Proper HTTP status codes (200, 201, 400, 404, 500)
- Consistent JSON structure with standardized field names
- Versioned endpoints for future compatibility

---

**End of Section 2.1**

