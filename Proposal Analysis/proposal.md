National College of Ireland

Project Proposal

Momentum

12/10/25

Computing

Software Development

2025/2026

Eoin Andrew Fitzsimons

X23151374

X23151374@student.ncirl.ie

 Contents

 [1.0        Objectives. 2](#_Toc211173428)

 [2.0        Background. 2](#_Toc211173429)

 [3.0        State of the Art. 3](#_Toc211173430)

 [4.0        Technical Approach. 3](#_Toc211173431)

 [4.1.       Simulation Engine. 4](#_Toc211173432)

 [4.2.       Procedural Content Generation. 4](#_Toc211173433)

 [4.3.       AI Decision-Making. 4](#_Toc211173434)

 [4.4.       Unity Front-End Interface. 4](#_Toc211173435)

 [4.5.       Iteration, Feedback, and Scalability. 4](#_Toc211173436)

 [5.0        Technical Details. 5](#_Toc211173437)

 [5.1.       Race Outcome Simulation. 5](#_Toc211173438)

 [5.2.       Driver Progression. 5](#_Toc211173439)

 [5.3.       AI Decision-Making. 5](#_Toc211173440)

 [5.4.       Procedural Content Generation. 5](#_Toc211173441)

 [5.5.       Performance Optimisation &amp; Integration. 6](#_Toc211173442)

 [6.0        Special Resources Required. 6](#_Toc211173443)

 [6.1.       Hardware Requirements. 6](#_Toc211173444)

 [6.2.       Software and Libraries. 6](#_Toc211173445)

 [6.3.       Optional Resources. 6](#_Toc211173446)

 [6.4.       Summary. 6](#_Toc211173447)

 [7.0        Project Plan. 7](#_Toc211173448)

 [7.1.       Project Overview.. 7](#_Toc211173449)

 [7.2.       Requirements and Design. 7](#_Toc211173450)

 [7.3.       Core Simulation Engine Development. 7](#_Toc211173451)

 [7.4.       Procedural Content Generation. 7](#_Toc211173452)

 [7.5.       AI Systems Development. 7](#_Toc211173453)

 [7.6.       Front-End Integration. 8](#_Toc211173454)

 [7.7.       Iterative Testing and Refinement. 8](#_Toc211173455)

 [7.8.       Final Evaluation and Documentation. 8](#_Toc211173456)

 [7.9.       Gantt Chart. 9](#_Toc211173457)

 [8.0        Testing. 9](#_Toc211173458)

 [8.1.       Testing Strategy. 9](#_Toc211173459)

 [8.2.       Unit Testing. 9](#_Toc211173460)

 [8.3.       Integration Testing. 9](#_Toc211173461)

 [8.4.       System Testing. 10](#_Toc211173462)

 [8.5.       User Evaluation. 10](#_Toc211173463)

# [1.0

Objectives]()

Momentum aims to design and implement a prototype motorsport
management simulator that captures the scale, depth, and unpredictability of
real-world racing ecosystems. Unlike existing titles, which currently focus on
a limited range of disciplines (e.g., Formula 1 and limited feeder systems), it
will model a wide variety of racing disciplines, each with its own unique
challenges and culture. For example, rally racing will feature dynamic terrain
and weather, requiring teams to adapt strategies for gravel, tarmac, or snow.
Endurance racing will simulate human factors such as driver fatigue, teamwork,
and mechanical reliability over long events. Street racing will emphasise
customisation, driver personality, and the underground culture that shapes
rivalries and alliances. By capturing these distinctions, the simulator will
aim to represent a more varied and context-sensitive motorsport environment,
where each series presents different management challenges.

The objective is to simulate a persistent game world where
events unfold across all leagues, regardless of whether the player is directly
involved. By doing so, the system mirrors the emergent qualities of Football
Manager, supporting diverse career trajectories that may differ across
playthroughs.

A further objective is to offer a high degree of
customisation. Players will be able to modify or generate new teams, drivers,
and competitions. Procedural generation will be a cornerstone, enabling
large-scale fictional ecosystems that feel authentic while avoiding licensing
restrictions.

The project will demonstrate implementation across key areas
including simulation design and AI-driven decision-making. The intended
prototype will model core systems such as driver progression, financial
management, league standings, and race outcomes, with a focus on achieving
computational efficiency.

The project’s objective is to produce a management simulator
that can serve as a foundation for future extension. It seeks to address an
identified gap in current games by emphasising simulation depth and
customisation, rather than prioritising graphical fidelity.

# [2.0

Background]()

My passion for motorsport spans a wide range of disciplines,
from open-wheel racing to rally, endurance, and street racing. While some
recent games, such as The Crew Motorfest, successfully capture the unique feel
and culture of different racing series, they focus on driving experiences
rather than management. Existing management games, on the other hand, tend to
concentrate on a single discipline or lack the depth and variety needed to
authentically represent the full spectrum of motorsport. No current title
combines the breadth of racing types, the distinctiveness of each discipline,
and the emergent, persistent world of a management simulation. This project
seeks to address that gap by integrating the unique characteristics of multiple
racing series into a single, dynamic management experience.

Having spent extensive hours in Football Manager, I have
experienced the appeal of large, complex simulations that generate emergent
stories. Despite having a stronger interest in Formula 1 and motorsport
generally than in football, I find myself drawn more to Football Manager than
to existing motorsport management titles. This reveals an important insight:
the attraction lies not in the sport itself, but in the richness of the
simulated world.

By comparison, current motorsport titles such as F1 Manager
and Motorsport Manager are limited. Their focus is on presentation and visuals
rather than world depth. The lack of customisation and the narrow scope of
simulated leagues lead to repetitive experiences over time.

This project seeks to address this gap by exploring how the
thematic appeal of motorsport can be combined with the systemic depth
characteristic of Football Manager. The objectives outlined in Section 1.0 will
be met by designing algorithms that support persistent multi-league simulation,
driver development models, and financial/strategic systems. Procedural content
generation will be used to overcome licensing limitations and create a
fictional but believable motorsport ecosystem.

# [3.0

State of the Art]()

Current motorsport management titles include Motorsport
Manager (2016) and F1 Manager (2022–2024). These games present detailed races
and authentic visuals, but their simulation depth is fundamentally limited.
Driver development is linear and predetermined, making long-term play
predictable. Once a player has learned the optimal strategies, the outcomes
become repetitive. In contrast, Football Manager maintains replayability by
simulating an immense global ecosystem of leagues, players, and staff, where no
two careers are the same. This difference highlights the gap between motorsport
management games and the broader standard of emergent sports simulations.

Another limitation of existing motorsport titles is their
lack of customisation. Players cannot easily expand leagues, create fictional
scenarios, or reshape the competitive environment. The games are tightly
constrained by licensing agreements and static structures, which prevents the
freedom that makes Football Manager engaging. Furthermore, the game worlds are
small in scale, restricted to a handful of categories such as Formula 1 or
Formula 2, with little simulation occurring outside the top tiers. By comparison,
Football Manager tracks hundreds of leagues and thousands of clubs across
multiple nations, with events unfolding regardless of direct player
involvement.

This project aims to distinguish itself by adopting that
philosophy. The simulation will extend beyond open-wheel racing, with multiple
tiers within each discipline. Every league will progress whether the player
manages there or not, creating a sense of a living world. Because official
licensing is not available, all teams, drivers, and championships will be
procedurally created, which also allows experimentation with unique structures,
rivalries, and narratives. By prioritising breadth, depth, customisation, and
emergent systems, this project will investigate how principles seen in Football
Manager’s large-scale simulation might be adapted to a motorsport context.

It is worth noting that some recent non-management racing
games, such as The Crew Motorfest, have made significant strides in capturing
the unique feel, culture, and challenges of different racing disciplines. These
titles demonstrate that it is possible to authentically represent the diversity
of motorsport, from rally to endurance to street racing. However, they focus on
the driving experience and do not offer the persistent, emergent management
simulation that is central to this project. No current management title
integrates the breadth of racing types, the distinctiveness of each discipline,
and a persistent simulation world. This project aims to explore how these
elements can be combined within a prototype, developing a management simulator
that reflects both the variety and complexity of motorsport ecosystems.

# [4.0

Technical Approach]()

Momentum is developed using a modular, iterative methodology
that combines agile software principles with a technically rigorous framework
for multi-discipline motorsport simulation. The system architecture is divided
into four interdependent subsystems:  **Simulation Engine** ,  **Procedural
Content Generation** ,  **AI Decision-Making** , and  **Unity Front-End
Interface** . Each module is engineered to operate independently while
remaining fully interoperable, allowing isolated development, testing, and
optimisation without disrupting overall system functionality. Data exchange
between Unity and the Python back-end occurs via structured JSON messages, and
persistent data is maintained using SQLite, providing a durable foundation for
multi-season and multi-league simulations.

## [4.1.  Simulation

Engine]()

The simulation engine forms the core computational
framework. Requirements were identified by analysing existing motorsport
management games, reviewing multi-agent systems research, and evaluating
emergent gameplay mechanics. Key functions include driver skill progression,
team financial management, dynamic race outcome modelling, and concurrent
league support. Race outcomes are computed using Monte Carlo simulations,
integrating driver attributes, car performance metrics, track-specific
parameters, weather conditions, and probabilistic random events. Financial
models employ stochastic methods to simulate operational budgets, sponsorship
volatility, and unexpected expenditures, producing realistic emergent league
economics. For example, an underfunded team may be forced to adopt aggressive
pit strategies, affecting competitor behaviour and league standings.

## [4.2.  Procedural

Content Generation]()

Procedural generation algorithmically produces teams,
drivers, tracks, and championships using constraint-based and probabilistic
rules. Driver traits, including skill, temperament, and fatigue progression,
are assigned according to league difficulty and balance requirements. Tracks
are generated with variable weather, geographic diversity, and surface types,
influencing race strategy and outcome. Team budgets and resources are
procedurally allocated, generating dynamic competitive hierarchies that evolve
over seasons. Metrics such as driver attribute diversity and competitive
balance are monitored, and automated adjustments ensure ecosystem stability,
enabling a replayable and unique motorsport environment for each simulation.

## [4.3.  AI

Decision-Making]()

AI agents integrate deterministic rule sets, probabilistic
heuristics, and reinforcement learning to manage pit stops, driver rotations,
race tactics, and financial decisions. Emergent behaviours arise when AI teams
respond dynamically to competitor actions. For instance, a fatigued AI driver
may miscalculate braking in wet conditions, causing chain reactions that affect
pit timing and rival team strategies. Reinforcement learning allows agents to
optimise long-term league performance, producing unpredictable yet balanced
outcomes. Real-time monitoring ensures AI decisions remain consistent with
procedural constraints and league regulations.

## [4.4.  Unity

Front-End Interface]()

Unity renders race telemetry, standings, driver statistics,
financial dashboards, and optional 3D track previews. Iterative integration
ensures simulation outputs, AI decisions, and procedural updates are reflected
accurately. User interactions, including strategy adjustments and managerial
decisions, are transmitted to the Python back-end, which updates persistent
league data. Visualisation metrics provide immediate feedback on emergent
behaviour, AI impact, and procedural ecosystem balance.

## [4.5.  Iteration,

Feedback, and Scalability]()

The development plan divides tasks into measurable phases
with continuous feedback loops. Milestones track driver progression, AI
adaptability, financial consistency, and procedural diversity. Modular
isolation enables future expansion, including additional motorsport
disciplines, extended driver attributes, or enhanced AI complexity without
redesigning the core engine. Persistent storage and optimised computational
methods sustain emergent, multi-league behaviour across multiple seasons,
ensuring Momentum remains a robust, scalable, and highly replayable motorsport
management simulator.

# [5.0

Technical Details]()

Momentum is implemented using a **Unity 2023 front-end**
for real-time visualisation and dashboard interfaces, paired with a **Python
3.11 back-end** for simulation logic, AI decision-making, procedural content
generation, and persistent data management. Python leverages **NumPy** for
high-performance numerical computations, **Pandas** for structured data
manipulation, and **SciPy** for advanced statistical operations. AI modules
additionally employ **PyTorch** for reinforcement learning and neural
network modelling, while procedural generation routines rely on
constraint-solving libraries to maintain balanced ecosystems. **SQLite**
provides a lightweight, cross-platform database for persistent storage of
drivers, teams, tracks, championship states, and multi-season histories.

## [5.1.  Race

Outcome Simulation]()

Race results are computed using  **Monte Carlo simulations** ,
integrating multiple weighted factors including driver skill, vehicle
performance parameters, track-specific attributes, dynamic weather, and
stochastic random events. Each simulated race consists of thousands of
iterations to generate probabilistic distributions of finishing positions. Edge
cases, such as mechanical failure or accidents, are represented as
low-probability events, introducing realistic uncertainty while maintaining
competitive balance. Cached results for commonly accessed league states reduce
redundant computation and ensure real-time responsiveness when updating
leaderboards and race summaries.

## [5.2.  Driver

Progression]()

Driver attributes—speed, consistency, aggression,
adaptability, and fatigue resilience—are represented as **multi-dimensional
vectors** with probabilistic evolution based on historical performance. Past
performance is stored in SQLite and influences future development trajectories
using weighted stochastic growth functions. Fatigue and injury are modelled
using decay algorithms combined with recovery cycles, producing emergent career
progression patterns that differ for each driver. This ensures that each season
presents novel strategic challenges and realistic driver dynamics.

## [5.3.  AI

Decision-Making]()

AI agents use a  **hybrid approach** , combining
deterministic rule-based behaviour with probabilistic decision heuristics and
reinforcement learning. Rule sets govern fundamental decisions, such as pit
stop eligibility and safety car reactions, while probabilistic heuristics allow
for variable strategies under uncertainty. Reinforcement learning optimises
long-term league objectives, such as championship points accumulation, resource
allocation, and rivalry management. AI outputs are transmitted in real time to Unity
via JSON, enabling coherent front-end visualisation of emergent behaviours and
adaptive strategy execution.

## [5.4.  Procedural

Content Generation]()

Procedural algorithms generate teams, drivers, tracks, and
championships based on constraint satisfaction models. Attribute ranges are
normalised to maintain competitive balance, and geographic or thematic
variations are algorithmically assigned to tracks and championships. Procedural
generation pipelines iterate over candidate entities, validating diversity and
ecosystem stability before committing data to SQLite. This ensures that each
simulated league is unique, replayable, and emergent.

## [5.5.  Performance

Optimisation &amp; Integration]()

Python back-end modules leverage **vectorised computations
and in-memory caching** for computational efficiency, while Unity employs
asynchronous data polling to avoid frame drops. Multi-league persistence is
maintained by serialising league states at season checkpoints. JSON-based
communication guarantees synchronised updates between front-end visualisation,
AI agents, and procedural generators. The architecture allows future expansion
of AI sophistication, additional motorsport disciplines, and enhanced procedural
attributes without disrupting core functionality.

# [6.0

Special Resources Required]()

## [6.1.  Hardware

Requirements]()

Development and execution of Momentum require a
high-performance workstation with a minimum of a 6-core CPU (Intel i7-12700 or
AMD Ryzen 7 5800X) to handle concurrent back-end simulations and AI
computations, 16 GB of RAM for caching simulation states, and a dedicated GPU
(NVIDIA RTX 3060 or equivalent) to render real-time Unity dashboards and
optional 3D track previews. For testing multi-league persistence and large
procedural ecosystems, additional cores or cloud-based virtual machines (VMs)
are recommended to parallelise race simulations across multiple seasons without
performance degradation. SSD storage is necessary for fast SQLite read/write
operations, particularly when managing hundreds of driver and team records
across concurrent leagues.

## [6.2.  Software

and Libraries]()

The front-end is built in Unity 2023, providing 2D/3D
rendering, UI management, and telemetry visualisation. The back end is
implemented in Python 3.11, utilising NumPy and Pandas for numerical and data
processing, SciPy for statistical modelling, and PyTorch for AI reinforcement
learning. Persistent storage is managed via SQLite, offering a lightweight,
cross-platform relational database sufficient for multi-season and multi-league
state persistence without requiring enterprise-level database infrastructure.
SQLite supports ACID compliance, enabling safe rollback during iterative
simulation testing, though for extremely large-scale simulations, optional
migration to PostgreSQL or MySQL can be considered.

## [6.3.  Optional

Resources]()

Cloud-based VMs (AWS, Azure, or GCP) allow large-scale
stress testing of AI agents, procedural content generation, and multi-league
simulations, enabling automated benchmarking for performance optimisation. Git
version control with branching ensures collaborative development and rollback
safety. Continuous integration tools (GitHub Actions or GitLab CI) automate
unit and integration testing pipelines. Procedural generation eliminates the
need for licensed assets, while optional telemetry visualisation plugins
enhance dashboard clarity for advanced performance analysis.

## [6.4.  Summary]()

These resources collectively provide sufficient
computational capacity, software infrastructure, and development support to
enable persistent, emergent, and scalable motorsport management simulation
without reliance on high-cost enterprise solutions.

# [7.0

Project Plan]()

## [7.1.  Project

Overview]()

The development of Momentum will follow a phased, iterative
methodology, combining agile principles with the requirements of a
multi-discipline motorsport management simulation. The project is divided into
seven primary phases, each building on the previous phase and enabling
measurable milestones. Dependencies between phases ensure that core systems are
functional before advanced AI and procedural content systems are integrated.
Feedback loops are implemented at each stage to refine algorithms, validate simulation
balance, and confirm emergent behaviours.

## [7.2.  Requirements

and Design]()

The initial phase focuses on defining the full scope of the
project, architecture of the system, and algorithmic approaches for AI and
procedural generation. Functional requirements include realistic driver
progression, dynamic race outcomes, persistent multi-league simulation, and
procedurally generated teams, drivers, tracks, and championships.
Non-functional requirements focus on computational efficiency, scalability, and
maintainability. Design documentation, UML diagrams, and flowcharts will be produced
to ensure all team members have a collective understanding of the system
architecture. This phase establishes clear performance targets and constraints,
including database schema designs for SQLite and communication protocols
between Unity and Python back-end modules.

## [7.3.  Core

Simulation Engine Development]()

The next phase implements the simulation engine, which forms
the backbone of the project. League structures, driver progression mechanics,
financial systems, and race resolution algorithms are developed and unit
tested. Driver attributes such as skill, fatigue, consistency, and personality
traits are modelled using probabilistic weighted systems. Financial operations
for teams, including budgets, sponsorships, and operational costs, are
represented using stochastic models to reflect real-world variability. Race
outcomes are calculated using Monte Carlo simulations, factoring in driver
skill, car performance, weather conditions, and track characteristics. Data
structures and in-memory caching strategies are optimised to maintain high
performance during multi-league, multi-season simulations.

## [7.4.  Procedural

Content Generation]()

Once the simulation engine is operational, procedural
content generation routines are integrated. Teams, drivers, tracks, and
championship schedules are algorithmically generated based on constraint
satisfaction models to ensure diversity and balance. Geographic, thematic, and
competitive variations are embedded to create a believable motorsport
ecosystem. Generated entities are validated for ecosystem stability before
being committed to the SQLite database. This phase also implements pipelines to
allow batch generation and automated verification of content, supporting
replayability and emergent behaviours across multiple simulated seasons.

## [7.5.  AI

Systems Development]()

AI modules are implemented concurrently with procedural
generation. Teams and drivers utilise hybrid decision-making models combining
rule-based heuristics, probabilistic strategies, and reinforcement learning. AI
agents determine pit stop timing, race tactics, driver rotations, and long-term
strategic decisions to maximise championship points while responding
dynamically to rival behaviour. Reinforcement learning models are trained on
historical simulation data to optimise performance over multiple seasons. AI
outputs are communicated to Unity in real time via JSON, ensuring coherent
visualisation of strategies, standings, and emergent rivalries.

## [7.6.  Front-End

Integration]()

The Unity front-end is connected to the Python back-end to
visualise race telemetry, leaderboards, team dashboards, and driver statistics.
Asynchronous data polling is implemented to prevent frame drops and maintain
smooth user interactions. User interface components are tested for usability,
clarity, and responsiveness. Integration ensures that procedural generation and
AI decisions are reflected accurately in the visualised simulation state.

## [7.7.  Iterative

Testing and Refinement]()

Unit, integration, and system testing occur in iterative
cycles, with milestones for driver progression accuracy, financial consistency,
AI diversity, race outcome realism, and persistent multi-league simulation.
Iterative feedback informs adjustments to algorithms and simulation parameters.
Emergent behaviours are monitored to ensure realistic rivalries, variable race
outcomes, and balanced progression across multiple leagues and seasons.
Performance profiling and optimisation are performed to maintain efficiency
under high computational loads.

## [7.8.  Final

Evaluation and Documentation]()

The final phase evaluates the emergent behaviour, user
experience, system stability, and overall performance. All code is documented,
and comprehensive reports on simulation accuracy, AI performance, procedural
generation stability, and database integrity are produced. This phase confirms
that Momentum operates as a coherent, persistent, and scalable motorsport
management simulator, meeting all functional and non-functional requirements.

The structured project plan ensures clear progression from
design through deployment, with measurable milestones and dependencies at each
stage. Iterative feedback and testing cycles guarantee that Momentum achieves
realistic, emergent, and persistent gameplay while remaining maintainable and
extensible for future development.

## [7.9.  ]()

Gantt Chart

# [8.0

Testing]()

## [8.1.  Testing

Strategy]()

Testing for Momentum is structured across multiple levels to
ensure system stability, performance, and fidelity of simulation outcomes.
Unit, integration, system, and user testing are all incorporated to validate
both functional and non-functional requirements. Each level of testing is
designed to produce measurable results and inform iterative refinement cycles
throughout development. Ethical considerations, including data privacy,
informed consent, and participant anonymity, are integrated into all user evaluation
procedures.

## [8.2.  Unit

Testing]()

Unit testing validates individual modules of the simulation.
Driver progression, financial systems, race outcome calculations, and AI
decision-making routines are tested against expected behaviours and edge cases.
Probabilistic models for driver skill development, fatigue, and personality
traits are verified for correct statistical distribution and consistency.
Financial operations are checked for accuracy, ensuring budgets, sponsorships,
and costs are correctly computed under stochastic conditions. Race outcome
algorithms, including Monte Carlo simulations, are validated to maintain
realistic variability while ensuring balance between drivers and teams.

## [8.3.  Integration

Testing]()

Integration testing ensures proper communication between the
Python back-end, Unity front-end, AI modules, and procedural content generation
systems. JSON-based data exchanges are verified for accuracy and latency, and
SQLite storage operations are tested for integrity across multi-season and
multi-league scenarios. Metrics include data consistency, transaction success
rates, and persistence reliability. Integration tests also verify that AI
decisions, procedural generation outputs, and race telemetry are correctly
reflected in the user interface, maintaining coherent emergent behaviours
across the simulation.

## [8.4.  System

Testing]()

System-level testing evaluates Momentum under full
operational conditions. Multi-league, multi-season simulations are run to
assess emergent behaviour, computational performance, and scalability. Metrics
include league variability, AI decision diversity, race outcome distribution,
system load, and memory usage. Stress testing is performed to evaluate
performance under high concurrency and extended simulation periods. Any
bottlenecks in AI computation, procedural content generation, or database
operations are identified and addressed to maintain real-time responsiveness
and persistent state accuracy.

## [8.5.  User

Evaluation]()

User testing measures interface usability, engagement, and
comprehension of the management systems. Participants interact with the full
Unity front-end, reviewing dashboards, race summaries, and team management
tools. Quantitative metrics include task completion time, accuracy of actions,
and interaction frequency. Qualitative metrics are gathered via structured
surveys, focusing on perceived realism, clarity, and enjoyment. Ethical
safeguards are enforced, including informed consent, voluntary participation,
and secure handling of collected data. Feedback informs both interface
improvements and algorithmic refinements to maintain realistic, emergent
gameplay.

Overall, the testing framework ensures that Momentum
achieves persistent, scalable, and believable motorsport simulation. Iterative
results from unit, integration, system, and user testing directly guide
algorithm adjustments, AI behaviour tuning, procedural content balancing, and
front-end enhancements, guaranteeing a coherent, high-quality, and engaging
management experience.
