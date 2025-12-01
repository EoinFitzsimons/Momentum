 



National College of Ireland

Project Proposal
Momentum
17/11/25

Computing
Software Development
2025/2026
Eoin Andrew Fitzsimons
X23151374
X23151374@student.ncirl.ie
 
Contents
1.0	Objectives	2
2.0	Background	2
3.0	State of the Art	3
4.0	Technical Approach	3
4.1.	Simulation Engine	3
4.2.	Database Management	4
4.3.	Front-End Interface	4
4.4.	Iteration, Feedback, and Scalability	4
5.0	Technical Details	4
5.1.	Race Outcome Simulation	4
5.2.	Driver Progression	5
5.3.	Data Management	5
5.4.	Performance Optimisation & Integration	5
6.0	Special Resources Required	5
6.1.	Hardware Requirements	5
6.2.	Software and Libraries	6
6.3.	Optional Resources	6
6.4.	Summary	6
7.0	Project Plan	6
7.1.	Project Overview	6
7.2.	Requirements and Design	6
7.3.	Core Simulation Engine Development	6
7.4.	Database Management	6
7.5.	Front-End Integration	7
7.6.	Iterative Testing and Refinement	7
7.7.	Final Evaluation and Documentation	7
Gantt Chart	8
8.0	Testing	8
8.1.	Testing Strategy	8
8.2.	Unit Testing	8
8.3.	Integration Testing	8
8.4.	System Testing	9
8.5.	User Evaluation	9

1.0	Objectives
Momentum aims to design and implement a prototype motorsport management simulator that captures the scale, depth, and unpredictability of real-world racing ecosystems. Unlike existing titles, which currently focus on a limited range of disciplines (e.g., Formula 1 and limited feeder systems), it will model a wide variety of racing disciplines, each with its own unique challenges and culture. For example, rally racing will feature dynamic terrain and weather, requiring teams to adapt strategies for gravel, tarmac, or snow. Endurance racing will simulate human factors such as driver fatigue, teamwork, and mechanical reliability over long events. Street racing will emphasise customisation, driver personality, and the underground culture that shapes rivalries and alliances. By capturing these distinctions, the simulator will aim to represent a more varied and context-sensitive motorsport environment, where each series presents different management challenges.
The objective is to simulate a persistent game world where events unfold across all leagues, regardless of whether the player is directly involved. By doing so, the system mirrors the emergent qualities of Football Manager, supporting diverse career trajectories that may differ across playthroughs.
A further objective is to offer a high degree of customisation. Players will be able to modify or generate new teams, drivers, and competitions. Procedural generation will be a cornerstone, enabling large-scale fictional ecosystems that feel authentic while avoiding licensing restrictions.
The project will demonstrate implementation across key areas including simulation design and AI-driven decision-making. The intended prototype will model core systems such as driver progression, economic management, league standings, and race outcomes, with a focus on achieving computational efficiency.
The project’s objective is to produce a management simulator that can serve as a foundation for future extension. It seeks to address an identified gap in current games by emphasising simulation depth and customisation, rather than prioritising graphical fidelity.
2.0	Background
My passion for motorsport spans a wide range of disciplines, from open-wheel racing to rally, endurance, and street racing. While some recent games, such as The Crew Motorfest, successfully capture the unique feel and culture of different racing series, they focus on driving experiences rather than management. Existing management games, on the other hand, tend to concentrate on a single discipline or lack the depth and variety needed to authentically represent the full spectrum of motorsport. No current title combines the breadth of racing types, the distinctiveness of each discipline, and the emergent, persistent world of a management simulation. This project seeks to address that gap by integrating the unique characteristics of multiple racing series into a single, dynamic management experience.
Having spent extensive hours in Football Manager, I have experienced the appeal of large, complex simulations that generate emergent stories. Despite having a stronger interest in Formula 1 and motorsport generally than in football, I find myself drawn more to Football Manager than to existing motorsport management titles. This reveals an important insight: the attraction lies not in the sport itself, but in the richness of the simulated world.
By comparison, current motorsport titles such as F1 Manager and Motorsport Manager are limited. Their focus is on presentation and visuals rather than world depth. The lack of customisation and the narrow scope of simulated leagues lead to repetitive experiences over time.
This project seeks to address this gap by exploring how the thematic appeal of motorsport can be combined with the systemic depth characteristic of Football Manager. The objectives outlined in Section 1.0 will be met by designing algorithms that support persistent multi-league simulation, driver development models, and financial/strategic systems. Procedural content generation will be used to overcome licensing limitations and create a fictional but believable motorsport ecosystem.
3.0	State of the Art
Current motorsport management titles include Motorsport Manager (2016) and F1 Manager (2022–2024). These games present detailed races and authentic visuals, but their simulation depth is fundamentally limited. Driver development is linear and predetermined, making long-term play predictable. Once a player has learned the optimal strategies, the outcomes become repetitive. In contrast, Football Manager maintains replayability by simulating an immense global ecosystem of leagues, players, and staff, where no two careers are the same. This difference highlights the gap between motorsport management games and the broader standard of emergent sports simulations.
Another limitation of existing motorsport titles is their lack of customisation. Players cannot easily expand leagues, create fictional scenarios, or reshape the competitive environment. The games are tightly constrained by licensing agreements and static structures, which prevents the freedom that makes Football Manager engaging. Furthermore, the game worlds are small in scale, restricted to a handful of categories such as Formula 1 or Formula 2, with little simulation occurring outside the top tiers. By comparison, Football Manager tracks hundreds of leagues and thousands of clubs across multiple nations, with events unfolding regardless of direct player involvement.
This project aims to distinguish itself by adopting that philosophy. The simulation will extend beyond open-wheel racing, with multiple tiers within each discipline. Every league will progress whether the player manages there or not, creating a sense of a living world. Because official licensing is not available, all teams, drivers, and championships will be procedurally created, which also allows experimentation with unique structures, rivalries, and narratives. By prioritising breadth, depth, customisation, and emergent systems, this project will investigate how principles seen in Football Manager’s large-scale simulation might be adapted to a motorsport context.
It is worth noting that some recent non-management racing games, such as The Crew Motorfest, have made significant strides in capturing the unique feel, culture, and challenges of different racing disciplines. These titles demonstrate that it is possible to authentically represent the diversity of motorsport, from rally to endurance to street racing. However, they focus on the driving experience and do not offer the persistent, emergent management simulation that is central to this project. No current management title integrates the breadth of racing types, the distinctiveness of each discipline, and a persistent simulation world. This project aims to explore how these elements can be combined within a prototype, developing a management simulator that reflects both the variety and complexity of motorsport ecosystems.
4.0	Technical Approach
Momentum is being built using agile software principles. The system is organised into three main parts: the Simulation Engine, Database Management, and the Front-End Interface. Each part works together to create a realistic and engaging motorsport management experience.
4.1.	Simulation Engine
The simulation engine is the heart of the system. Its design is inspired by popular motorsport management games and research into multi-agent systems. The engine handles things like how drivers improve over time, how teams manage their finances, how races are decided, and how multiple leagues can run at once. Race results are calculated using Monte Carlo simulations, which take into account driver skills, car performance, track details, weather, and random events. The financial side uses probability-based models to reflect real-world unpredictability, such as changes in sponsorship or unexpected costs. This means, for example, that a team with less money might have to take more risks with their strategy, which can change how the whole league plays out.
4.2.	Database Management
The database management system is responsible for creating and storing all the teams, drivers, tracks, and championships. It uses algorithms to generate these elements based on certain rules and probabilities, ensuring that each league is balanced and diverse. Driver traits like skill, temperament, and fatigue are set according to the needs of the league. Tracks are created with different weather, locations, and surfaces, which all affect how races play out. Team budgets and resources are also assigned by the database, helping to create a dynamic and evolving competition. The system keeps an eye on things like driver diversity and league balance, making automatic adjustments to keep the game fair and interesting. All aspects of content creation and generation are managed here, so references to procedural generation are now part of database management.
4.3.	Front-End Interface
The front-end interface, built in Python, displays race data, standings, driver stats, and financial dashboards. It shows the results of simulations and AI decisions, and updates in real time as the game progresses. When users make decisions or change strategies, these are sent to the back end, which updates the league data. The interface provides instant feedback on how the league is evolving and how the AI and database management systems are affecting the game.
4.4.	Iteration, Feedback, and Scalability
The development plan is broken into clear phases, with regular feedback and review. Progress is measured by tracking things like driver development, AI improvements, financial stability, and the diversity of the database-generated content. The system is designed to be modular, so new features or motorsport types can be added without having to rebuild everything. Data is stored efficiently to allow for long-term, multi-league play, making Momentum a robust and replayable motorsport management simulator.
5.0	Technical Details
Momentum uses Python for both the front-end dashboards and the back-end simulation logic and database management. The system relies on NumPy for fast calculations, Pandas for handling data, and SciPy for advanced statistics. The database uses SQLite to store all the information about drivers, teams, tracks, and championships, making it easy to save and load multi-season histories. All content creation and generation is handled by the database management system.
5.1.	Race Outcome Simulation
Race results are calculated using Monte Carlo simulations, which combine factors like driver skill, car performance, track features, weather, and random events. Each race is simulated thousands of times to get realistic results. Rare events, like crashes or mechanical failures, are included as low-probability outcomes to keep things unpredictable but fair. Frequently used results are cached to make the game run smoothly and keep leaderboards up to date.
5.2.	Driver Progression
Driver attributes like speed, consistency, aggression, adaptability, and fatigue are tracked as numbers that can change over time. How a driver develops depends on their past results, which are stored in the database. Growth and decline are modelled using probability-based functions, so each driver's career is unique. Fatigue and injuries are also tracked, with recovery periods built in, making each season different and challenging.
5.3.	Data Management
All teams, drivers, tracks, and championships are created and managed by the database management system. It uses algorithms to ensure that everything is balanced and diverse, with different locations and themes for tracks and championships. Before anything is saved, the system checks that the league will be fair and interesting. This approach makes every playthrough unique and replayable, and all content generation is now part of database management.
5.4.	Performance Optimisation & Integration
The Python backend uses fast, vectorised calculations and keeps frequently used data in memory for speed. League states are saved at the end of each season, so progress is never lost. The system uses JSON to keep everything in sync between the front end and database management. The design makes it easy to add new features or motorsport types in the future, without having to change the core of the game.
6.0	Special Resources Required
6.1.	Hardware Requirements
Momentum's Python GUI and simulation backend have modest hardware requirements. For typical development and use:
- Minimum Requirements:
-	CPU: Dual-core processor (e.g., Intel i3 or AMD equivalent)
-	RAM: 4 GB
-	Storage: 500 MB free disk space
-	GPU: Integrated graphics (no dedicated GPU required)
-	Display: 1366x768 resolution
- Recommended Requirements:
-	CPU: Quad-core processor (e.g., Intel i5 or AMD Rysen 3)
-	RAM: 8 GB
-	Storage: 1 GB free disk space
-	GPU: Integrated or basic dedicated GPU (optional)
-	Display: 1920x1080 resolution
These specifications are sufficient for running and developing the Python GUI, simulation, and database management systems. Higher-end hardware is only needed if running very large-scale simulations.
6.2.	Software and Libraries
The front end is built in Python, which handles all the graphics, user interface, and telemetry displays. The back end also runs on Python 3.11, using NumPy, Pandas, and SciPy for calculations and data handling. All persistent data is stored in SQLite, which is lightweight and works across platforms. This setup is enough for multi-season and multi-league play, and can be upgraded to a bigger database if needed for very large simulations. SQLite also allows safe rollbacks during testing.
6.3.	Optional Resources
Cloud-based virtual machines (like AWS, Azure, or GCP) can be used for large-scale testing of multi-league simulations, helping to optimise performance. Git version control is used for safe, collaborative development. Automated testing is handled by tools like GitHub Actions or GitLab CI. Since all content is generated by the database management system, there is no need for licensed assets. Optional plugins can improve telemetry displays for advanced analysis.
6.4.	Summary
Together, these resources provide all the computing power, software, and support needed to run a persistent, scalable motorsport management simulator, without needing expensive enterprise solutions.
7.0	Project Plan
7.1.	Project Overview
Momentum will be developed in clear, manageable phases, using agile methods. Each phase builds on the last, with milestones to track progress. The plan ensures that the core systems are working before expanding the database management system. Regular feedback and testing help refine the algorithms and keep the simulation balanced and realistic.
7.2.	Requirements and Design
The first phase is about defining what the project will do, how it will be structured, and how the database management system will work. The main goals are to have realistic driver progression, dynamic race results, and persistent multi-league play, with all teams, drivers, tracks, and championships created and managed by the database system. The database will be created before the game and packaged with it, so that every player has the same starting point. Non-functional goals include making sure the system is efficient, scalable, and easy to maintain. Design documents, diagrams, and flowcharts will be created to clarify and organise the project plan. This phase also sets performance targets and database designs and defines how the Python components will communicate.
7.3.	Core Simulation Engine Development
The next phase is building the simulation engine, which is the core of the project. This includes setting up league structures, how drivers improve, how finances work, and how races are decided. Driver skills, fatigue, and personality are modelled using probability-based systems. Team finances, including budgets and sponsorships, are also handled with realistic randomness. Race results are calculated using Monte Carlo simulations, considering all the important factors. Data is managed efficiently to keep the game running smoothly, even with many leagues and seasons.
7.4.	Database Management
Once the simulation engine is working, the focus shifts to the database management system. This part is responsible for creating and storing all teams, drivers, tracks, and championship schedules. It uses algorithms to make sure everything is diverse and balanced, with different locations and themes. Before anything is saved, the system checks that the league will be fair and interesting. This phase also adds tools for batch creation and automatic checking of content, making sure every playthrough is unique and replayable.
7.5.	Front-End Integration
The Python front end is connected to the backend to show race data, leaderboards, team dashboards, and driver stats. Updates are sent smoothly to keep the interface responsive. The user interface is tested for clarity and ease of use. Integration ensures that all changes from the simulation and database management systems are shown accurately in the game.
7.6.	Iterative Testing and Refinement
Testing happens in cycles, with milestones for things like driver development, financial stability, AI variety, realistic race results, and multi-league play. Feedback from each cycle is used to improve the algorithms and keep the simulation balanced. The system is monitored to make sure rivalries, race outcomes, and league progression all feel realistic. Performance is checked and improved as needed to keep everything running smoothly.
7.7.	Final Evaluation and Documentation
The final phase reviews how the system behaves, the user experience, stability, and overall performance. All code is documented, and detailed reports are created on simulation accuracy and database management. This phase makes sure that Momentum works as a complete, persistent, and scalable motorsport management simulator, meeting all the goals set out at the start.

The project plan is designed to move smoothly from design to deployment, with clear milestones and dependencies. Regular feedback and testing ensure that Momentum delivers a realistic and engaging experience, while staying easy to maintain and expand in the future.
Gantt Chart 
8.0	Testing
8.1.	Testing Strategy
Testing for Momentum is structured across multiple levels to ensure system stability, performance, and fidelity of simulation outcomes. Unit, integration, system, and user testing are all incorporated to validate both functional and non-functional requirements. Each level of testing is designed to produce measurable results and inform iterative refinement cycles throughout development. Ethical considerations, including data privacy, informed consent, and participant anonymity, are integrated into all user evaluation procedures.
8.2.	Unit Testing
Unit testing validates individual modules of the simulation. Driver progression, financial systems, race outcome calculations, and AI decision-making routines are tested against expected behaviours and edge cases. Probabilistic models for driver skill development, fatigue, and personality traits are verified for correct statistical distribution and consistency. Financial operations are checked for accuracy, ensuring budgets, sponsorships, and costs are correctly computed under stochastic conditions. Race outcome algorithms, including Monte Carlo simulations, are validated to maintain realistic variability while ensuring balance between drivers and teams.
8.3.	Integration Testing
Integration testing ensures proper communication between the Python back-end, Unity front-end, AI modules, and procedural content generation systems. JSON-based data exchanges are verified for accuracy and latency, and SQLite storage operations are tested for integrity across multi-season and multi-league scenarios. Metrics include data consistency, transaction success rates, and persistence reliability. Integration tests also verify that AI decisions, procedural generation outputs, and race telemetry are correctly reflected in the user interface, maintaining coherent emergent behaviours across the simulation.
8.4.	System Testing
System-level testing evaluates Momentum under full operational conditions. Multi-league, multi-season simulations are run to assess emergent behaviour, computational performance, and scalability. Metrics include league variability, AI decision diversity, race outcome distribution, system load, and memory usage. Stress testing is performed to evaluate performance under high concurrency and extended simulation periods. Any bottlenecks in AI computation, procedural content generation, or database operations are identified and addressed to maintain real-time responsiveness and persistent state accuracy.
8.5.	User Evaluation
User testing measures interface usability, engagement, and comprehension of the management systems. Participants interact with the full Unity front-end, reviewing dashboards, race summaries, and team management tools. Quantitative metrics include task completion time, accuracy of actions, and interaction frequency. Qualitative metrics are gathered via structured surveys, focusing on perceived realism, clarity, and enjoyment. Ethical safeguards are enforced, including informed consent, voluntary participation, and secure handling of collected data. Feedback informs both interface improvements and algorithmic refinements to maintain realistic, emergent gameplay.
Overall, the testing framework ensures that Momentum achieves persistent, scalable, and believable motorsport simulation. Iterative results from unit, integration, system, and user testing directly guide algorithm adjustments, AI behaviour tuning, procedural content balancing, and front-end enhancements, guaranteeing a coherent, high-quality, and engaging management experience.
