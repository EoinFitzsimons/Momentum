# MOMENTUM - Multi-Discipline Motorsport Manager

## Game Design Document v1.0

---

## 1. EXECUTIVE SUMMARY

**Title:** MOMENTUM - Motorsport Management Simulation**Genre:** Multi-Discipline Racing Management Simulation**Platform:** PC (Python Backend + Optional Unity Frontend)**Target Audience:** Motorsport enthusiasts seeking deep, authentic management gameplay**Core Pillars:**

1. **Multi-Discipline Authenticity** - 7 distinct racing categories with unique mechanics
2. **Deep Career Progression** - Multi-season team building with long-term consequences
3. **Technical Depth** - Realistic vehicle component systems and development
4. **Strategic Management** - Financial, personnel, and technical resource optimization

---

## 2. GAME OVERVIEW

### 2.1 Concept Statement

MOMENTUM is a comprehensive motorsport management simulation spanning seven distinct racing disciplines. Players manage racing teams across multi-season careers, making strategic decisions about driver contracts, vehicle development, staff hiring, financial management, and race strategy. Each discipline features unique gameplay mechanics reflecting real-world differences between racing categories.

### 2.2 Core Gameplay Loop

```
Season Start → Team Assessment → Personnel Management → Vehicle Development → 
Race Weekends (10-20 per season) → Championship Resolution → Off-Season → Next Season
```

### 2.3 Key Differentiators

- **True Multi-Discipline System:** Not just different car types - fundamentally different racing formats
- **Component-Level Vehicle Simulation:** Deep car management beyond simple ratings
- **Persistent Career Progression:** Decisions have multi-season consequences
- **Data-Driven Realism:** 1,781 drivers with 56 attributes each, 175 authentic circuits

---

## 3. RACING DISCIPLINES

### 3.1 SINGLE_SEATER (Formula Racing)

**Real-World Inspiration:** Formula 1, Formula 2, IndyCar**Core Characteristics:**

- High-downforce open-wheel cars
- Precision engineering and aerodynamics critical
- Qualifying position highly influential
- Strategic pit stop windows

**Event Structure:**

- Practice Sessions (2x 60-90 minutes)
- Qualifying (Knockout format, 3 sessions)
- Race (50-70 laps, 1-2 pit stops)

**Vehicle Development Focus:**

- Aerodynamics (front wing, rear wing, floor, diffuser)
- Power unit (engine mapping, hybrid deployment)
- Chassis (weight distribution, rigidity)
- Electronics (traction control, DRS systems)

**Key Strategic Elements:**

- Tire compound selection (Soft/Medium/Hard)
- Fuel load optimization
- DRS (Drag Reduction System) deployment
- Pit stop timing vs track position

**Staff Specializations:**

- Chief Aerodynamicist
- Power Unit Engineer
- Race Strategist
- Data Analyst

---

### 3.2 PRODUCTION_TOURING (Sedan/Tin-Top Racing)

**Real-World Inspiration:** BTCC, V8 Supercars, DTM**Core Characteristics:**

- Contact racing encouraged
- Durability and reliability critical
- Door-to-door wheel-to-wheel battles
- High mechanical grip, moderate downforce

**Event Structure:**

- Practice (1x 45 minutes)
- Qualifying (Single lap shootout)
- Race 1 (20-30 laps)
- Race 2 (Reverse grid or separate quali)

**Vehicle Development Focus:**

- Suspension geometry (contact resistance)
- Body strength and panels (damage tolerance)
- Braking systems (repeated hard braking)
- Differential settings (traction out of corners)

**Key Strategic Elements:**

- Aggressive vs conservative driving styles
- Damage management (bent panels affect aero)
- Tire preservation on abrasive surfaces
- Success ballast management (weight penalties)

**Staff Specializations:**

- Suspension Engineer
- Body/Chassis Specialist
- Damage Assessment Crew
- Setup Engineer

---

### 3.3 RALLY_STAGE (Point-to-Point Rally)

**Real-World Inspiration:** WRC, Rally America, ERC**Core Characteristics:**

- **No wheel-to-wheel racing** - Time trials against the clock
- Co-driver pace notes system critical
- Vastly different surface types
- Multi-day events with service parks

**Event Structure (3-Day Rally):**

- **Day 1:** Shakedown (test stage) → 5 competitive stages → Service
- **Day 2:** 8 stages (mixed surfaces) → Midday service → Evening stages
- **Day 3:** 6 stages → Power Stage (bonus points for fastest 5 drivers)

**Vehicle Development Focus:**

- Suspension travel and damping (rough surfaces)
- Drivetrain durability (AWD systems)
- Ground clearance and underbody protection
- Weight distribution for different surfaces

**Key Strategic Elements:**

- Tire choice per stage (gravel/tarmac/snow/wet)
- Pace note accuracy and recce strategy
- Service park repair prioritization (limited time)
- Risk management (stage difficulty vs attack)
- Weather forecasting for tire strategy

**Staff Specializations:**

- Co-Driver (paired with driver - chemistry critical)
- Service Crew Chief
- Recce Specialist (stage scouting)
- Meteorologist
- Suspension Specialist

**Unique Mechanics:**

- **Stage Damage Persistence:** Damage carries through multiple stages until service
- **Recce System:** Pre-event stage scouting affects pace note quality
- **Service Park:** 15-45 minute windows to repair damage and setup changes
- **Road Position:** Running order affects grip levels on gravel stages

---

### 3.4 URBAN_STREET (Street Racing / Drift)

**Real-World Inspiration:** Fast & Furious, Need for Speed, Formula Drift**Core Characteristics:**

- Underground racing culture and reputation system
- Nitrous oxide systems (NOS)
- Contact and aggressive driving allowed
- Heavy visual customization emphasis
- Night racing predominant

**Event Structure:**

- **Sprint Races:** Point-to-point (1-3 miles)
- **Circuit Battles:** Multi-lap closed street courses
- **Drift Exhibitions:** Judged on style, angle, proximity
- **Touge Runs:** Mountain pass battles (uphill vs downhill)

**Vehicle Development Focus:**

- Turbo/Supercharger tuning
- Nitrous bottle capacity and jet sizing
- Weight reduction (stripped interiors)
- Suspension (drift setup vs grip racing)
- Visual customization (liveries, body kits, underglow)

**Key Strategic Elements:**

- NOS deployment timing (short bursts at critical moments)
- Contact risk vs speed advantage
- Reputation management (winning builds respect)
- Police heat level (if illegal events)
- Drift scoring optimization (angle + speed + proximity)

**Staff Specializations:**

- Tuner (dyno specialist)
- NOS System Technician
- Drift Coach
- Visual Customization Designer

**Unique Mechanics:**

- **Reputation System:** Wins increase respect, unlock better opponents
- **NOS Management:** Limited shots per race, refill between events
- **Drift Scoring:** Angle, speed, line, smoke, proximity to walls
- **Police Interference:** Heat level affects event risk/rewards
- **Illegal Parts:** High-risk high-reward modifications

---

### 3.5 DRAG_ACCELERATION (Quarter Mile)

**Real-World Inspiration:** NHRA, IHRA, Drag racing**Core Characteristics:**

- **4-8 second races** - pure acceleration
- Reaction time at Christmas Tree critical
- Bracket racing and dial-in strategy
- Extreme mechanical stress and failures
- Elimination tournament format

**Event Structure:**

- **Qualifying:** 2-3 runs to determine seeding
- **Eliminations:** Bracket racing (Round 1 → Round 2 → Semis → Finals)
- **Match Racing:** Head-to-head against single opponent

**Vehicle Development Focus:**

- Launch system (clutch, trans brake, wheelie bars)
- Engine power output (superchargers, nitrous)
- Weight reduction to extreme levels
- Tire compound for launch grip
- Chassis rigidity and weight transfer

**Key Strategic Elements:**

- **Dial-In Times:** Setting target time for bracket racing
- **Reaction Time:** 0.000-0.500s window at start
- **Consistency:** Repeating times more important than raw speed
- **Weather Compensation:** Temperature/humidity massively affect times
- **Engine Tuning:** Pushing power vs reliability risk

**Staff Specializations:**

- Launch Specialist
- Engine Tuner
- Track Prep Specialist
- Data Acquisition Engineer

**Unique Mechanics:**

- **Christmas Tree Start:** Staged/Pre-staged lights, reaction time measurement
- **Bracket Racing:** Slower car can win by hitting dial-in time
- **Breakout System:** Going faster than dial-in = disqualification
- **60-Foot Times:** First 60 feet determines entire race outcome
- **Track Prep:** Track conditions vary throughout day (temperature)

---

### 3.6 SPRINT_RALLYCROSS (Mixed Surface Racing)

**Real-World Inspiration:** World RX, Americas Rallycross**Core Characteristics:**

- Short sprint races (4-6 laps, ~600m per lap)
- Mixed tarmac and gravel sections per lap
- Standing starts with massive launch forces
- Mandatory "Joker Lap" (longer alternate route)

**Event Structure:**

- **Heat Races:** 3-4 heats (4-6 cars each, 4 laps)
- **Semi-Finals:** Top qualifiers (6 laps)
- **Final:** Top 6 drivers (6 laps + Joker)

**Vehicle Development Focus:**

- Launch control systems (standing starts)
- AWD torque distribution
- Suspension for tarmac/gravel transitions
- Brake cooling (repeated hard braking)

**Key Strategic Elements:**

- **Joker Lap Timing:** When to take slower alternate route (tactical)
- **Launch Technique:** Starting grid position critical
- **Surface Transitions:** Tarmac → gravel setup compromise
- **Overtaking Zones:** Limited passing opportunities

**Staff Specializations:**

- Launch Systems Engineer
- AWD Specialist
- Race Strategist (Joker timing)

**Unique Mechanics:**

- **Mandatory Joker:** Must take alternate route once per race (1-3 seconds slower)
- **Standing Starts:** Every race starts from standstill (launch critical)
- **Progression Format:** Heat results determine semi/final grids
- **Contact Allowed:** Aggressive racing encouraged

---

### 3.7 ENDURANCE (Multi-Hour Racing)

**Real-World Inspiration:** Le Mans 24h, Daytona 24h, Spa 24h**Core Characteristics:**

- 6-24 hour race duration
- Multiple drivers per car (2-3 drivers)
- Reliability and consistency over speed
- Night racing sections
- Multi-class racing (LMP1, LMP2, GTE)

**Event Structure:**

- **Practice/Qualifying:** Multiple sessions over 2 days
- **Race:** 6/12/24 hour duration
  - Hour 0-6: Daylight, aggressive pace
  - Hour 6-12: Sunset transition, strategy phase
  - Hour 12-18: Night racing, cautious pace
  - Hour 18-24: Sunrise push, final strategy

**Vehicle Development Focus:**

- Mechanical reliability above all
- Fuel efficiency (longer stints)
- Brake cooling systems
- Driver comfort (long stints)
- Night lighting systems

**Key Strategic Elements:**

- **Driver Rotation:** Managing 2-3 drivers (fatigue, pace, traffic skills)
- **Fuel Strategy:** Double/triple stinting to gain positions
- **Traffic Management:** Lapping slower classes cleanly
- **Night Driving:** Reduced pace, higher accident risk
- **Mechanical Preservation:** Component wear over 24 hours

**Staff Specializations:**

- Chief Strategist (multi-hour planning)
- Reliability Engineer
- Driver Coach (managing 3 drivers)
- Night Racing Specialist

**Unique Mechanics:**

- **Driver Changes:** Mandatory pit stops with driver swaps
- **Driver Fatigue:** Performance degrades during stints
- **Night Vision:** Reduced visibility affects pace and safety
- **Multi-Class Racing:** Navigating traffic from 3-4 different car classes
- **Safety Cars:** Frequent due to long duration, strategy reset moments
- **Mechanical Failures:** Higher probability over 24 hours

---

## 4. CAREER MODE STRUCTURE

### 4.1 Career Initialization

**Player Setup:**

- Manager name
- Starting year (2025 ONLY)
- **Choose team** (existing team at any tier level AT ANY DISCIPLINE)

**Team Selection Options:**

**Tier 1 (Elite Teams):**

- Budget: €8-12M annually
- Immediate championship pressure
- Existing driver contracts (1-2 star drivers)
- Fully staffed (20-30 personnel)
- Advanced facilities
- **Challenge:** Win-now mentality, high expectations

**Tier 2 (Midfield Teams):**

- Budget: €5-8M annually
- Build competitive car over 2-3 seasons
- Mix of talent (1 veteran, 1 young driver)
- Basic staff (10-15 personnel)
- Standard facilities
- **Challenge:** Balanced approach, podiums expected

**Tier 3 (Backmarker Teams):**

- Budget: €2-5M annually
- Long-term project (3-5 seasons to compete)
- Young/unproven drivers
- Skeleton staff (5-10 personnel)
- Minimal facilities
- **Challenge:** Survive financially, develop slowly

### 4.2 Season Structure

**Pre-Season (Off-Season Phase - 3 Months)**

**Month 1: Personnel Changes**

- **Driver Market Opens**

  - Review current driver contracts (expiring vs remaining years)
  - Negotiate with free agents
  - Buy out contracts from other teams
  - Renew existing drivers or let go
  - Considerations:
    - Salary demands vs budget
    - Discipline aptitude ratings
    - Driver chemistry (for endurance/rally co-driver pairs)
    - Age and development potential
- **Staff Hiring/Firing**

  - Assess current staff performance ratings
  - Hire specialists based on budget
  - Promote from within or recruit externally
  - Staff salary negotiations
  - Each role has different costs:
    - Team Principal: €500k-2M
    - Chief Engineer: €300k-1M
    - Aerodynamicist: €200k-800k
    - Mechanics: €40k-100k each

**Month 2: Technical Development**

- **Vehicle Development Allocation**

  - Set budget distribution across components:
    - Engine: €X million (power, reliability)
    - Chassis: €X million (rigidity, weight)
    - Aerodynamics: €X million (downforce, drag)
    - Suspension: €X million (handling, durability)
    - Electronics: €X million (control systems)
    - Drivetrain: €X million (gearbox, differential)
- **Research & Development Projects**

  - Choose development path (aggressive vs reliable)
  - Allocate wind tunnel hours (regulated limit)
  - CFD simulation budget
  - Physical testing days
- **Facility Upgrades** (Long-term investments)

  - Factory expansion: €5-20M (increases development speed)
  - Wind tunnel: €10-50M (improves aero development)
  - Simulator: €2-10M (driver training, setup testing)
  - Upgrades take 1-3 seasons to complete

**Month 3: Pre-Season Testing**

- **Testing Sessions** (3-5 days at multiple circuits)

  - Discover car strengths/weaknesses
  - Test different setups
  - Driver feedback loop
  - Component reliability testing
  - Set development priorities based on data
- **Championship Preparation**

  - Finalize driver line-ups
  - Set season objectives (based on budget/tier)
  - Sponsor agreement reviews
  - Media commitments

**Race Season (10-20 Events Depending on Discipline)**

Each race weekend follows discipline-specific format (see Section 3), but general structure:

**Pre-Event (Week Before Race):**

- Review circuit characteristics
- Historical performance at this track
- Weather forecasting
- Preliminary car setup recommendations
- Driver/staff travel logistics

**Event Execution:**

- **Practice Sessions**

  - Setup experimentation
  - Data gathering
  - Component testing
- **Qualifying** (Format varies by discipline)

  - Grid position determination
  - Strategy implications
- **Race**

  - Real-time or simulated
  - Strategic decisions during race
  - Component wear management
  - Driver performance evaluation
- **Post-Race**

  - Championship points allocation
  - Prize money awarded
  - Component damage assessment
  - Media reactions
  - Sponsor satisfaction tracking

**Post-Season (End of Championship)**

**Championship Resolution:**

- Final standings (Drivers' + Constructors')
- Prize money distribution (position-based)
- Sponsor bonus/penalty payments
- Achievement unlocks
- Historical records updated

**Team Performance Review:**

- Did team meet objectives?
- Job security assessment (can be fired for poor results)
- Driver satisfaction (affects contract negotiations)
- Staff morale (affects next season performance)

**Regulation Changes:**

- New technical regulations announced
- Budget cap adjustments
- Calendar changes (circuits added/removed)
- Points system changes

### 4.3 Multi-Season Progression

**Season-to-Season Evolution:**

**Years 1-3: Establishment Phase**

- Learn team strengths/weaknesses
- Build staff infrastructure
- Initial facility investments
- Establish driver partnerships
- Climb from Tier 3 → Tier 2 (if starting low)

**Years 4-7: Competitive Phase**

- Consistent podium challenges
- First race wins
- Driver talent poaching from rivals
- Advanced facility completion
- Tier 2 → Tier 1 progression

**Years 8-15: Dynasty Building**

- Championship contention
- Multiple titles possible
- Driver academies developed
- Technical dominance periods
- Legacy building

**Career Longevity Features:**

- **Driver Aging:**

  - Rookies (18-22): High potential, low consistency
  - Prime (25-32): Peak performance years
  - Veterans (33-40): Declining speed, high experience
  - Retirement: Must replace legends
- **Staff Development:**

  - Junior staff improve with experience
  - Loyalty system (poaching risk from rivals)
  - Retirement and replacement
- **Team Reputation:**

  - Poor results → drivers leave, sponsors pull out
  - Good results → attract better talent
  - Historic records (first win, championships)
- **AI Team Evolution:**

  - Other teams hire/fire drivers and staff
  - Teams rise and fall in competitiveness
  - Regulation changes shuffle competitive order

---

## 5. VEHICLE DEVELOPMENT SYSTEM

### 5.1 Component Architecture

**Existing Component Models** (from codebase analysis):

**Engine Component:**

- Displacement (liters)
- Cylinder configuration (V8, Inline-4, Flat-6, etc.)
- Aspiration (Naturally Aspirated, Turbocharged, Supercharged, Twin-charged)
- Fuel system and fuel type
- Power output (BHP) and torque (Nm)
- RPM characteristics (redline, power band)
- **Component Wear System:**
  - Crankshaft condition (0.0-1.0)
  - Pistons condition
  - Connecting rods condition
  - Valvetrain condition
  - Camshaft condition
  - Turbo/Supercharger condition
  - Cooling efficiency
  - Oil/Coolant condition
- Reliability rating
- Fuel consumption rate
- Total mileage tracking

**Hybrid Power Unit** (for applicable disciplines):

- Battery capacity (kWh)
- Electric motor power (kW)
- Energy recovery systems (MGU-K, MGU-H)
- Deployment modes (Attack, Conserve, Charge)
- Regeneration efficiency

**Drivetrain:**

- Gearbox type (Manual, Sequential, Dual-Clutch)
- Number of gears
- Gear ratios (customizable per track)
- Differential type (Open, Limited-Slip, Electronic)
- Clutch system
- Component wear tracking

**Chassis:**

- Material (Carbon fiber, Aluminum, Steel tube frame)
- Weight (kg)
- Rigidity/Torsional stiffness
- Safety cell rating
- Crash structure integrity
- Repair/Rebuild requirements

**Aerodynamics Package:**

- Front wing configuration
- Rear wing angle/configuration
- Floor design
- Diffuser efficiency
- Drag coefficient (Cd)
- Downforce levels (front/rear balance)
- DRS system (if applicable)

**Suspension:**

- Type (Double wishbone, MacPherson, etc.)
- Spring rates (front/rear)
- Damper settings
- Anti-roll bar stiffness
- Ride height
- Camber/Toe settings

**Electronics:**

- ECU (Engine Control Unit) sophistication
- Traction control systems
- ABS systems
- Telemetry capability
- Data logging
- Driver aids (Launch control, pit limiter)

**Tires:**

- Compound types (Soft/Medium/Hard or discipline-specific)
- Wear rate
- Temperature operating window
- Grip levels
- Degradation curves

### 5.2 Development Mechanics

**Budget Allocation:**
Player distributes annual development budget across component categories:

```
Example Tier 2 Team (€6M budget):
- Engine: €1.5M (25%)
- Aerodynamics: €1.2M (20%)
- Chassis: €1.0M (17%)
- Suspension: €0.8M (13%)
- Electronics: €0.6M (10%)
- Drivetrain: €0.5M (8%)
- Testing: €0.4M (7%)
Total: €6.0M
```

**Development Impact:**

- Higher spending = faster improvement rate
- Diminishing returns above certain thresholds
- Staff quality affects efficiency of spending
- Testing budget validates improvements

**Component Performance Ratings:**
Each component has performance rating (0-100):

- **0-30:** Uncompetitive (backmarker performance)
- **31-50:** Midfield performance
- **51-70:** Competitive (podium capable)
- **71-85:** Championship contender
- **86-100:** Dominant performance

**Development Paths:**

**Aggressive Development:**

- Faster performance gains
- Higher reliability risk
- More expensive
- Rapid improvement but potential failures

**Conservative Development:**

- Slower performance gains
- Better reliability
- Cost-effective
- Steady improvement without risks

**Balanced Development:**

- Moderate gains and risk
- Standard approach
- Middle ground

### 5.3 Component Wear and Maintenance

**Session-Based Degradation:**

- Every practice/quali/race session degrades components
- Wear rate based on:
  - Session intensity (practice < qualifying < race)
  - Track characteristics (high-speed vs tight corners)
  - Weather conditions (rain increases wear)
  - Driver aggression

**Component Lifecycle:**

```
New (100%) → Good (75-99%) → Worn (50-74%) → 
Critical (25-49%) → Failure Risk (<25%)
```

**Replacement Decisions:**

- Replace components = cost + performance restoration
- Run degraded components = save money but performance loss
- Strategic replacement timing (before critical weekends)

**Component Pool System:**

- Regulations limit number of engines/gearboxes per season
- Exceeding allocation = grid penalties
- Strategic management across 10-20 races

### 5.4 Setup Optimization

**Track-Specific Setup:**
Each circuit requires different setup approach:

**High-Speed Circuits:**

- Low downforce (reduce drag)
- Stiff suspension
- Low ride height
- Long gear ratios

**Technical Circuits:**

- High downforce (maximize cornering)
- Softer suspension
- Higher ride height (curbs)
- Short gear ratios

**Mixed Circuits:**

- Balanced downforce
- Compromise suspension
- Medium ride height
- Optimized ratios

**Setup Process:**

1. Engineer recommendations based on track data
2. Driver testing in practice
3. Telemetry analysis
4. Setup adjustments
5. Qualifying/Race setup locked in

**Setup Parameters:**

- Front wing angle (0-15 degrees)
- Rear wing angle (0-20 degrees)
- Suspension stiffness (soft/medium/stiff)
- Ride height (mm)
- Brake bias (front/rear %)
- Differential settings
- Gear ratios per gear
- Tire pressures

---

## 6. PERSONNEL MANAGEMENT

### 6.1 Driver System

**Driver Attributes** (56 attributes - from codebase):

**Core Driving Skills (10):**

- Raw Speed, Consistency, Racecraft, Overtaking, Defensive Driving
- Cornering Skill, Braking Technique, Acceleration Control
- Spatial Awareness, Vehicle Control

**Physical & Mental (10):**

- Physical Fitness, Reaction Time, Concentration, Pressure Handling
- Pain Tolerance, G-Force Tolerance, Coordination, Multitasking
- Mental Resilience, Adrenaline Management

**Technical Knowledge (8):**

- Setup Knowledge, Mechanical Sympathy, Tire Management, Fuel Management
- Aerodynamics Understanding, Suspension Feel, Engine Management, Data Analysis

**Discipline Aptitudes (7):**

- Single Seater Aptitude
- Touring Car Aptitude
- Rally Aptitude
- Street Racing Aptitude
- Drag Racing Aptitude
- Rallycross Aptitude
- Endurance Aptitude

**Race Craft & Strategy (8):**

- Race Strategy, Pit Entry/Exit, Traffic Management, Qualifying Pace
- Race Pace, Starting Skill, Tire Warming, Energy Management

**Environmental Adaptation (7):**

- Wet Weather Skill, Night Driving, Heat Tolerance, Cold Tolerance
- Altitude Adaptation, Visibility Adaptation, Surface Adaptation

**Personal & Social (6):**

- Media Handling, Sponsorship Appeal, Fan Engagement
- Team Player, Leadership, Professionalism

**Driver Contracts:**

- Contract length (1-5 years)
- Annual salary (€100k - €15M depending on talent)
- Performance bonuses (podiums, wins, championship)
- Buyout clauses (cost to release early)
- Driver demands:
  - Number 1 status guarantee
  - Car development priority
  - Veto rights on teammates
  - Personal sponsor integration

**Driver Development:**

- Young drivers (18-22) improve rapidly
- Peak years (25-32) stable high performance
- Decline phase (33+) gradual skill reduction
- Retirement (typically 35-42 depending on discipline)

**Driver Morale System:**

- Affected by:
  - Car performance vs expectations
  - Team treatment (favoritism)
  - Contract satisfaction
  - Media pressure
  - Crash incidents
- Low morale = underperformance
- High morale = overperformance

### 6.2 Staff System

**Staff Roles** (from codebase - 25+ roles):

**Core Technical:**

- Technical Director: Overall car development direction
- Chief Engineer: Component integration and optimization
- Aerodynamics Engineer: Aero package development
- Engine Engineer: Power unit optimization
- Suspension Engineer: Handling characteristics
- Setup Engineer: Track-specific configurations
- Data Analyst: Telemetry interpretation

**Operational:**

- Team Manager: Day-to-day operations
- Race Strategist: In-race decision making
- Pit Crew Chief: Pit stop coordination
- Pit Crew Members (multiple): Pit stop execution
- Mechanics: Car preparation and maintenance

**Development:**

- Chief Designer: New car concepts
- Car Designer: Component design
- Simulator Engineer: Virtual testing
- Test Engineer: Physical testing programs

**Business:**

- Team Principal: Overall leadership
- Financial Director: Budget management
- Commercial Director: Sponsorship deals
- Marketing Manager: Brand building

**Support:**

- Driver Coach: Driver skill development
- Fitness Trainer: Driver physical conditioning
- Psychologist: Mental performance

**Staff Attributes:**

- Technical Skill (0-100)
- Experience Level (Intern → Legendary)
- Specialization areas
- Salary requirements
- Loyalty rating
- Team chemistry

**Staff Impact on Performance:**

- Better staff = faster development
- Higher salaries for top talent
- Staff chemistry affects morale
- Poaching risk from rival teams
- Retirement and succession planning

### 6.3 Team Chemistry

**Internal Dynamics:**

- Driver-Driver relationships (teammates)
- Driver-Engineer relationships
- Staff-Staff chemistry
- Leadership effectiveness

**Chemistry Effects:**

- High chemistry = better car development
- Low chemistry = infighting, slow progress
- Personality conflicts = performance loss

---

## 7. FINANCIAL MANAGEMENT

### 7.1 Revenue Streams

**Championship Prize Money:**

- Position-based payments (1st highest, decreasing down grid)
- Tier 1 teams: €20-50M for championship win
- Tier 2 teams: €5-15M for mid-table
- Tier 3 teams: €1-3M for participation

**Sponsorship Income:**

- Primary Sponsor: €2-20M annually (based on team tier)
- Secondary Sponsors: €500k-5M each
- Personal Driver Sponsors: €100k-2M
- Performance bonuses in contracts (win = bonus)

**Merchandise and Licensing:**

- Team merchandise sales
- Licensing deals
- Broadcast revenue share

### 7.2 Expenditures

**Personnel Costs:**

- Driver salaries: €100k-15M per driver
- Staff salaries: €40k-2M per person
- Total team payroll: €5-50M annually

**Development Costs:**

- Car development budget: €2-30M
- Testing programs: €500k-5M
- Facility maintenance: €200k-2M

**Operational Costs:**

- Race attendance: €50k-200k per event
- Transportation and logistics
- Hospitality and catering
- Travel expenses

**Component Costs:**

- Engine rebuilds: €100k-500k
- Gearbox replacement: €50k-200k
- Chassis repairs: €20k-500k
- Aero damage: €10k-100k
- Tire allocation: €5k-20k per race

**Facilities Investment:**

- Factory expansion: €5-20M
- Wind tunnel: €10-50M
- Simulator: €2-10M

### 7.3 Budget Balancing

**Financial Health States:**

- **Profitable:** Revenue > Expenses, can invest in growth
- **Break-Even:** Stable but no growth capacity
- **Deficit:** Burning through reserves
- **Bankruptcy Risk:** Insolvency threatens team survival

**Budget Management Decisions:**

- Aggressive spending for performance
- Conservative approach for stability
- Risk/reward calculations
- Sponsor negotiation leverage

---

## 8. RACE WEEKEND EXECUTION

### 8.1 Pre-Race Planning

**Circuit Analysis:**

- Track characteristics (high-speed, technical, mixed)
- Historical performance data at this circuit
- Weather forecast (7-day outlook)
- Tire allocation strategy

**Car Setup Direction:**

- Engineer recommendations based on simulation
- Driver preferences
- Compromise between drivers (if conflicting)

**Strategic Objectives:**

- Target finishing position
- Points scoring goals
- Risk tolerance level

### 8.2 Practice Sessions

**Data Gathering:**

- Long run pace analysis
- Tire degradation rates
- Fuel consumption mapping
- Component temperatures

**Setup Refinement:**

- Aerodynamic balance adjustments
- Suspension tuning
- Brake bias optimization
- Gear ratio validation

**Driver Feedback:**

- Handling characteristics
- Problem areas identification
- Confidence level assessment

### 8.3 Qualifying

**Discipline-Specific Formats:**

- Single Seater: Knockout qualifying (Q1, Q2, Q3)
- Touring: Single flying lap
- Rally: Shakedown stage time
- Street: Reputation-based or time trial
- Drag: Elimination qualifying runs
- Rallycross: Heat races determine grid
- Endurance: Multiple qualifying sessions

**Strategic Decisions:**

- Tire compound choice
- Fuel load (light for speed vs heavy for race start)
- Engine mode (aggressive vs conservative)
- Number of attempts vs tire preservation

### 8.4 Race Execution

**Pre-Race Final Decisions:**

- Starting tire compound
- Fuel load calculation
- Pit stop strategy (1-stop, 2-stop, 3-stop)
- Driver instructions (aggressive/conservative)

**Real-Time Decision Points:**

- Pit stop trigger moments
- Safety car responses
- Weather changes (switch to wet tires?)
- Competitor moves (undercut/overcut)
- Component damage assessment
- Team orders (if both drivers fighting)

**Post-Race:**

- Championship points updated
- Prize money allocation
- Component wear assessment
- Driver/staff morale updates
- Media obligations
- Sponsor satisfaction tracking

---

## 9. PROGRESSION AND REWARDS

### 9.1 Championship Systems

**Drivers' Championship:**

- Individual driver points across season
- Points allocation based on finishing position
- Fastest lap bonus (if applicable to discipline)
- Champion crowned at season end

**Constructors' Championship:**

- Combined team points (both drivers)
- Determines prize money distribution
- Team prestige and reputation

**Discipline-Specific Variations:**

- Rally: Stage wins and overall rally victories
- Drag: Elimination bracket winners
- Endurance: Class championships (LMP1, LMP2, GTE)

### 9.2 Achievement System

**Career Milestones:**

- First race start
- First points finish
- First podium
- First win
- First pole position
- First championship
- 10/25/50/100 wins
- 5/10/20 championships
- Perfect season (win every race)

**Team Achievements:**

- Constructor championship
- 1-2 finish (both drivers podium)
- Dominant season (>80% wins)
- Dynasty (3+ consecutive championships)

**Technical Achievements:**

- Develop championship-winning car
- Create dominant engine
- Perfect reliability season (no DNFs)

### 9.3 Unlockables

**Historical Content:**

- Legendary drivers from past eras
- Classic cars and liveries
- Historic circuits

**Advanced Features:**

- Multi-discipline career (compete in 2+ disciplines)
- Team creation mode
- Custom championship builder

### 9.4 Legacy System

**Hall of Fame:**

- Greatest drivers in game history
- Championship-winning teams
- Record holders (most wins, titles, etc.)

**Historical Records:**

- Lap records per circuit
- Season records (most wins, points, etc.)
- Career records across 15+ seasons
- Dynasty periods documented

---

## 10. TECHNICAL IMPLEMENTATION

### 10.1 Existing Systems (From Codebase)

**Database Layer:**

- SQLite database with comprehensive schema
- 1,781 drivers with 56 attributes each
- 1,095 teams across 7 disciplines
- 175 circuits with full specifications
- 57,936 staff members
- Championship, Race, RaceResult tables

**Vehicle System:**

- Complete component architecture (Engine, Drivetrain, Chassis, Aero, Electronics)
- Component wear simulation
- Power output calculations
- Condition tracking per component

**Simulation Engine:**

- Monte Carlo race simulation
- Multi-discipline support
- Weather impact modeling
- Driver skill evaluation
- Track characteristic integration

**Staff Management:**

- 25+ staff roles with specializations
- Skill ratings and experience levels
- Salary systems with currency support
- Budget-based hiring constraints

### 10.2 Required New Systems

**Career Persistence:**

- Save/Load game state
- Multi-season data storage
- Historical record tracking
- Player profile management

**Contract System:**

- Driver contract negotiation AI
- Staff hiring negotiations
- Sponsor agreement management
- Multi-year contract tracking

**Financial Simulation:**

- Revenue calculation engine
- Expense tracking per category
- Budget allocation interface
- Bankruptcy detection

**AI Team Behavior:**

- Rival teams making hiring decisions
- AI development spending patterns
- AI race strategy
- Driver market AI

**Development Progression:**

- Component improvement over time
- Research tree implementation
- Testing impact on development
- Facility upgrade effects

**Championship Manager:**

- Multi-race season orchestration
- Points calculation
- Standings tracking
- Regulation management

**World State Manager:**

- Time progression (days/weeks/months)
- Event scheduling
- Dynamic calendar generation
- Season transitions

### 10.3 Interface Requirements

**Core Screens Needed:**

1. **Main Menu**

   - New Career
   - Load Career
   - Options
   - Exit
2. **Career Hub**

   - Current season status
   - Next event countdown
   - Quick navigation to all systems
   - News feed
3. **Team Overview**

   - Current drivers
   - Staff roster
   - Car performance ratings
   - Financial summary
   - Championship standings
4. **Driver Management**

   - Current contracts
   - Driver market
   - Contract negotiations
   - Driver comparison tools
   - Performance statistics
5. **Staff Management**

   - Current staff roster
   - Available staff market
   - Hiring interface
   - Salary negotiations
   - Staff performance reviews
6. **Car Development**

   - Component ratings display
   - Budget allocation sliders
   - Development path selection
   - Testing schedule
   - Facility upgrades
7. **Financial Overview**

   - Income sources breakdown
   - Expense categories
   - Budget planning
   - Sponsor contracts
   - Cash flow projection
8. **Race Weekend**

   - Event schedule
   - Practice session results
   - Qualifying interface
   - Race strategy planning
   - Live race view (or simulation)
   - Post-race analysis
9. **Championship Calendar**

   - Full season schedule
   - Past results
   - Upcoming events
   - Weather forecasts
   - Circuit information
10. **Season Review**

    - Final standings
    - Season highlights
    - Financial summary
    - Contract situations
    - Regulation changes preview

---

## 11. DEVELOPMENT ROADMAP

### Phase 1: Core Foundation (Weeks 1-2)

**Goal:** Playable single-season career

- [ ] World State Manager implementation
- [ ] Championship season generation
- [ ] Basic race weekend flow
- [ ] Simple points tracking
- [ ] Save/Load game state
- [ ] Team selection interface

**Deliverable:** Can select team, run through 10-race season, see standings

### Phase 2: Personnel Systems (Weeks 3-4)

**Goal:** Driver and staff management functional

- [ ] Driver contract system
- [ ] Contract negotiation mechanics
- [ ] Staff hiring/firing
- [ ] Salary management
- [ ] Driver/staff attribute display
- [ ] Free agent market

**Deliverable:** Can hire/fire drivers and staff, manage contracts

### Phase 3: Financial System (Week 5)

**Goal:** Complete economic simulation

- [ ] Revenue calculation (prize money, sponsors)
- [ ] Expense tracking (salaries, operations, development)
- [ ] Budget allocation interface
- [ ] Financial health monitoring
- [ ] Sponsor contract management

**Deliverable:** Full financial simulation affecting team decisions

### Phase 4: Development System (Week 6)

**Goal:** Car development and progression

- [ ] Budget allocation to components
- [ ] Performance improvement over time
- [ ] Testing impact implementation
- [ ] Facility upgrade system
- [ ] Development path choices

**Deliverable:** Car improves throughout season based on spending

### Phase 5: Multi-Season Progression (Week 7)

**Goal:** Career longevity and evolution

- [ ] Season transition mechanics
- [ ] Driver aging and retirement
- [ ] Staff development over time
- [ ] AI team evolution
- [ ] Regulation changes
- [ ] Historical records

**Deliverable:** Can play 5+ season career with evolving world

### Phase 6: Race Weekend Depth (Week 8)

**Goal:** Detailed race weekend experience

- [ ] Practice session simulation
- [ ] Setup optimization interface
- [ ] Qualifying strategies
- [ ] In-race decision making
- [ ] Component wear integration
- [ ] Post-race analysis

**Deliverable:** Deep race weekend gameplay

### Phase 7: Discipline Specialization (Weeks 9-10)

**Goal:** Unique mechanics per discipline

- [ ] Rally stage-by-stage system
- [ ] Drag elimination brackets
- [ ] Endurance driver rotation
- [ ] Street racing reputation
- [ ] Rallycross joker lap
- [ ] Discipline-specific staff

**Deliverable:** Each discipline feels unique

### Phase 8: Polish and Balance (Weeks 11-12)

**Goal:** Refined, balanced experience

- [ ] AI difficulty tuning
- [ ] Economic balance testing
- [ ] Performance curve adjustments
- [ ] UI/UX improvements
- [ ] Bug fixing
- [ ] Testing and iteration

**Deliverable:** Polished, playable full career mode

### Phase 9: GUI Implementation (Weeks 13-15)

**Goal:** Professional desktop application

- [ ] ttkbootstrap UI framework
- [ ] All core screens implemented
- [ ] Data visualization (graphs, charts)
- [ ] Visual polish
- [ ] User experience refinement

**Deliverable:** Beautiful desktop application

### Phase 10: Optional Unity Integration (Weeks 16+)

**Goal:** 3D visualization layer

- [ ] Python backend API
- [ ] Unity frontend connection
- [ ] 3D car models
- [ ] Circuit visualization
- [ ] Race replay system

**Deliverable:** Premium 3D experience

---

## 12. SUCCESS METRICS

### 12.1 Core Gameplay Goals

**Depth of Engagement:**

- Average career length: 10+ seasons
- Player retention per session: 2+ hours
- Decisions per race weekend: 20+ meaningful choices

**Strategic Complexity:**

- Multiple viable team building paths
- No single dominant strategy
- Meaningful trade-offs in all decisions

**Replayability:**

- 7 disciplines offer different experiences
- 3 tiers provide different challenge levels
- Emergent narratives through driver/team evolution

### 12.2 Quality Benchmarks

**Authenticity:**

- Realistic driver attributes and progression
- Accurate circuit characteristics
- Believable financial simulation
- Component wear matches real-world patterns

**Balance:**

- No overpowered teams/drivers
- Budget constraints create meaningful choices
- Tier progression feels earned (3-5 seasons from Tier 3 to Tier 1)

**Performance:**

- Save/Load under 5 seconds
- Race simulation under 30 seconds
- UI responsiveness (no lag)

---

## 13. APPENDICES

### Appendix A: Database Schema Extensions Needed

**New Tables:**

```sql
-- Driver Contracts
CREATE TABLE driver_contracts (
    id INTEGER PRIMARY KEY,
    driver_id INTEGER,
    team_id INTEGER,
    start_year INTEGER,
    end_year INTEGER,
    annual_salary REAL,
    performance_bonuses TEXT, -- JSON
    buyout_clause REAL,
    clauses TEXT, -- JSON
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Staff Contracts
CREATE TABLE staff_contracts (
    id INTEGER PRIMARY KEY,
    staff_id INTEGER,
    team_id INTEGER,
    role TEXT,
    start_year INTEGER,
    end_year INTEGER,
    annual_salary REAL,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Sponsor Agreements
CREATE TABLE sponsor_agreements (
    id INTEGER PRIMARY KEY,
    team_id INTEGER,
    sponsor_name TEXT,
    annual_amount REAL,
    start_year INTEGER,
    end_year INTEGER,
    performance_requirements TEXT, -- JSON
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Component Development
CREATE TABLE component_development (
    id INTEGER PRIMARY KEY,
    team_id INTEGER,
    season_year INTEGER,
    engine_rating REAL,
    chassis_rating REAL,
    aero_rating REAL,
    suspension_rating REAL,
    electronics_rating REAL,
    drivetrain_rating REAL,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Facility Upgrades
CREATE TABLE facility_upgrades (
    id INTEGER PRIMARY KEY,
    team_id INTEGER,
    facility_type TEXT,
    level INTEGER,
    completion_year INTEGER,
    cost REAL,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Season Objectives
CREATE TABLE season_objectives (
    id INTEGER PRIMARY KEY,
    team_id INTEGER,
    season_year INTEGER,
    objective_type TEXT,
    target_value INTEGER,
    met BOOLEAN,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Historical Records
CREATE TABLE historical_records (
    id INTEGER PRIMARY KEY,
    record_type TEXT,
    holder_id INTEGER,
    holder_type TEXT, -- 'driver' or 'team'
    value REAL,
    season_year INTEGER,
    discipline TEXT
);

-- Career Save Data
CREATE TABLE career_saves (
    id INTEGER PRIMARY KEY,
    save_name TEXT,
    player_name TEXT,
    current_date TEXT,
    current_season INTEGER,
    team_id INTEGER,
    world_state TEXT, -- JSON blob
    created_at TIMESTAMP,
    last_played TIMESTAMP
);
```

### Appendix B: Key Formulas

**Driver Performance Calculation:**

```python
def calculate_race_performance(driver, car, track, weather):
    # Base performance from driver skill
    base = driver.get_discipline_rating(track.discipline)
  
    # Car performance impact (±30%)
    car_factor = (car.overall_rating / 100) * 0.3
  
    # Track suitability (±10%)
    track_factor = calculate_track_suitability(driver, track) * 0.1
  
    # Weather adaptation (±10%)
    weather_factor = (driver.wet_weather_skill / 100) * weather.severity * 0.1
  
    # Form and morale (±5%)
    morale_factor = (driver.morale / 100) * 0.05
  
    # Component condition (±15%)
    component_factor = car.get_overall_condition() * 0.15
  
    final_performance = base * (1 + car_factor + track_factor + 
                                weather_factor + morale_factor + 
                                component_factor)
  
    return clamp(final_performance, 0, 100)
```

**Development Progress:**

```python
def calculate_component_improvement(budget_allocated, staff_quality, testing_hours):
    # Base improvement from budget
    base_improvement = (budget_allocated / 1000000) * 2.0  # €1M = +2 rating
  
    # Staff efficiency multiplier (0.5x - 2.0x)
    staff_multiplier = 0.5 + (staff_quality / 100) * 1.5
  
    # Testing validation bonus (up to +20%)
    testing_bonus = min(testing_hours / 100, 0.2)
  
    # Diminishing returns above 85 rating
    current_rating = component.current_rating
    if current_rating > 85:
        diminishing = 1.0 - ((current_rating - 85) / 30)
    else:
        diminishing = 1.0
  
    improvement = base_improvement * staff_multiplier * (1 + testing_bonus) * diminishing
  
    return improvement
```

**Financial Health:**

```python
def calculate_financial_health(team):
    annual_revenue = (
        team.prize_money +
        sum(sponsor.annual_amount for sponsor in team.sponsors) +
        team.merchandise_income
    )
  
    annual_expenses = (
        sum(driver.salary for driver in team.drivers) +
        sum(staff.salary for staff in team.staff) +
        team.development_budget +
        team.operational_costs +
        team.facility_maintenance
    )
  
    cash_flow = annual_revenue - annual_expenses
  
    if cash_flow > 0:
        return "PROFITABLE"
    elif team.cash_reserves > abs(cash_flow):
        return "STABLE"
    elif team.cash_reserves > 0:
        return "WARNING"
    else:
        return "BANKRUPTCY_RISK"
```

---

## END OF DOCUMENT

**Document Version:** 1.0
**Last Updated:** 2025-10-31
**Authors:** Momentum Development Team
**Status:** Foundation Document - Implementation in Progress
