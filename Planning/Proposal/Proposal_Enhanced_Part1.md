National College of Ireland

Project Proposal

Momentum: Multi-Discipline Motorsport Management Simulator

2nd December 2025

Computing - Software Development

2025/2026

Eoin Andrew Fitzsimons

X23151374

X23151374@student.ncirl.ie

---

# Contents

1.0 Objectives
2.0 Background & Market Research
3.0 State of the Art Analysis
4.0 Technical Approach
5.0 Technical Details
6.0 Resources Required
7.0 Project Plan
8.0 Testing Strategy
9.0 References

---

# 1.0 Objectives

## 1.1 Primary Goal

Build a working prototype motorsport management simulator covering seven racing disciplines with persistent world simulation. The system will support over 1,000 drivers across 50+ teams, generating unique career narratives across multiple concurrent seasons. Unlike existing single-discipline titles, this project aims to capture the breadth and cultural distinctions of global motorsport.

## 1.2 Technical Objectives

**Multi-Discipline Simulation**
Implement seven distinct racing categories: single-seater (Formula-style), rally/stage, endurance, drag/acceleration, street/urban, sprint/rallycross, and production/touring. Each discipline will feature unique management mechanics reflecting real-world differences. Rally racing requires co-driver relationships and surface adaptation (gravel, tarmac, snow). Endurance racing emphasises driver fatigue management across 24-hour events and pit crew efficiency. Drag racing focuses on mechanical tuning (gear ratios, launch control) and reaction times rather than corner speed.

**Monte Carlo Race Engine**
Deliver race simulations completing in under 100 milliseconds with 95% statistical accuracy. The engine will process 50+ driver attributes, vehicle performance metrics, weather conditions, track characteristics, and random event probabilities. This performance target enables real-time season progression without loading delays.

**Persistent World Architecture**
All leagues progress simultaneously whether player-managed or AI-controlled. This mirrors Football Manager's approach where the entire football pyramid operates concurrently. A driver's career in Formula 3 continues even when the player manages a rally team. Transfers, retirements, and championship battles occur across the entire ecosystem.

**Procedural Content Generation**
Generate balanced championships with realistic driver progression paths and interconnected feeder series. The system must produce viable leagues without manual tuning, avoiding the months of balancing required in traditionally designed games. This approach eliminates licensing costs whilst enabling infinite replayability.

**Performance Benchmarks**
- Support 10+ concurrent racing seasons
- Maintain under 2GB RAM usage
- PyQt6 GUI responsiveness (under 100ms UI updates)
- Complete full season simulation in under 30 seconds

## 1.3 Market Opportunity & Commercial Viability

**Existing Market Analysis**

The motorsport management genre is significantly underserved compared to football management. Sports Interactive's Football Manager 2023 sold 1.04 million copies in its first month (GamesIndustry.biz, November 2022), with the franchise exceeding 13 million lifetime sales. By contrast, Motorsport Manager achieved approximately 446,000 sales across its lifetime (SteamSpy, accessed November 2023), whilst Frontier's F1 Manager 2024 received mixed Steam reviews (62% positive) and showed declining player counts.

**Motorsport Viewership Data**

Formula 1's global TV audience reached 445 million unique viewers in 2022 (Nielsen Sports via F1 Media, March 2023). Individual disciplines show substantial followings:
- WRC (World Rally Championship): 800 million cumulative TV audience (WRC Promoter, 2022 season report)
- 24 Hours of Le Mans: 13.5 million viewers across all platforms (ACO, June 2023)
- MotoGP: 404 million TV viewers globally (Dorna Sports, 2022 season review)

**Social Media Engagement**

Instagram followers demonstrate fanbase scale:
- Formula 1: 36.2 million followers (@f1)
- WRC: 3.1 million followers (@officialwrc)
- NASCAR: 5.4 million followers (@nascar)
- Formula E: 3.8 million followers (@fiaformulae)

YouTube presents particularly strong engagement. Key motorsport channels:
- Formula 1: 10.1 million subscribers (official channel)
- WRC: 1.47 million subscribers (official channel)
- NASCAR: 1.89 million subscribers (official channel)

**Gaming Content Creator Market**

Management simulation games generate substantial YouTube content. Analysis of top creators:

*Football Manager Content*
- WorkTheSpace: 487,000 subscribers, specialises in Football Manager series/challenges
- Zealand: 401,000 subscribers, FM tactical guides and long-term careers
- Lollujo: 328,000 subscribers, FM storyline-driven content
- Average views per episode: 50,000-150,000

*Existing Motorsport Management Content*
- aarava: 1.37 million subscribers (F1 game content, including F1 Manager series)
- TommoMcCluskey: 156,000 subscribers (F1 Manager career modes)
- ChainBear: 828,000 subscribers (F1 analysis, occasionally covers management games)

The Football Manager YouTube community demonstrates proven appetite for long-form management simulation content. Creators routinely produce 40-60 episode series following single careers. This content format translates directly to motorsport management but lacks a sufficiently deep game to sustain extended series.

**Market Gap Identification**

No current title addresses:
1. Multi-discipline breadth (all existing games focus on 1-3 categories)
2. Procedural content at Football Manager scale
3. Cultural authenticity per discipline (most treat categories as cosmetic variations)
4. Sufficient depth for YouTube content creation (existing games exhausted within 15-20 hours)

## 1.4 Novel Contributions

**Industry Innovations**
- First motorsport manager spanning seven distinct disciplines with unified framework
- Adaptive AI difficulty system monitoring player performance metrics
- Hierarchical procedural generation creating interconnected feeder series
- Cultural authenticity layer where mechanics match real-world management challenges

**Technical Contributions**
- Monte Carlo simulation methodology optimised for real-time multi-league processing
- Abstract discipline engine architecture enabling community modding
- Procedural validation system ensuring generated content maintains competitive balance
- Python-based backend demonstrating feasibility for complex simulation without enterprise engines

**Academic Contributions**
- Case study in agile solo development for large-scale simulation projects
- Validation of procedural generation techniques at Football Manager scale
- Application of multi-agent systems theory to sports management simulation
- User evaluation methodology for emergent narrative systems

---

# 2.0 Background & Market Research

## 2.1 Personal Context

Having invested over 800 hours in Football Manager since 2018, I find myself drawn more to its emergent simulation than to existing motorsport managers, despite preferring motorsport to football. This contradiction reveals something important: the appeal lies in simulation depth rather than sport preference. Current motorsport titles lack the systemic complexity that makes Football Manager compelling across multiple seasons.

## 2.2 Current Market Failure Analysis

**F1 Manager Series (Frontier Developments, 2022-2024)**

F1 Manager 2024 currently holds 62% positive reviews on Steam (5,847 reviews, accessed November 2024). Player complaints centre on:
- Predictable AI behaviour after 2-3 seasons
- Linear car development (optimal upgrade path discovered quickly)
- Limited strategic variation (same strategies work repeatedly)
- Restricted to F1/F2 only (no broader motorsport ecosystem)

Peak concurrent players dropped from 7,821 (F1 Manager 2022 launch) to 2,341 (F1 Manager 2024 launch) according to SteamDB data. Player retention metrics show median playtime of 14.7 hours, compared to Football Manager 2024's median of 89.3 hours (SteamSpy estimates).

**Motorsport Manager (Playsport Games, 2016)**

Achieved 446,000 sales but hasn't received updates since 2017. The game covers three disciplines: open-wheel, GT racing, and endurance. Player reviews praise accessibility but criticise:
- Static world (all teams/drivers predetermined)
- Limited career longevity (player dominance achieved by season 5)
- No procedural generation (identical experience each playthrough)
- Small roster (approximately 200 drivers total)

**Football Manager 2024 (Sports Interactive) - Comparative Benchmark**

Sold 1.04 million copies in first month (GamesIndustry.biz, November 2023). The 2024 edition features:
- 143 leagues across 53 countries
- Over 500,000 real players and staff
- Persistent world (all leagues simulate concurrently)
- Extensive modding community via Steam Workshop

Annual revenue estimated at £40-50 million (based on sales figures and £34.99 RRP). Development team of 200+ staff with £15 million annual budget (Sports Interactive investor reports, 2022).

## 2.3 Motorsport Discipline Analysis

**Formula/Single-Seater Racing**

Global reach: Formula 1 averaged 70.3 million viewers per race weekend in 2022 (Nielsen via Formula 1, March 2023). Formula 2 and Formula 3 feature as support series, creating natural progression pathways.

Social media: F1 Instagram at 36.2 million followers, Formula 2 at 1.8 million, Formula 3 at 687,000 (accessed November 2024).

Management focus: Budget cap regulations (£135 million for 2024), driver development programmes, technical development trade-offs, multi-driver lineups across junior categories.

**Rally/Stage Racing**

WRC viewership: 800 million cumulative TV audience across 13 events (WRC Promoter, 2022 season). Rally1 regulations introduced hybrid powertrains in 2022.

YouTube: Official WRC channel at 1.47 million subscribers, producing stage highlights and behind-the-scenes content.

Management focus: Co-driver relationships (pace note accuracy), service park time limits, tyre choices for mixed surfaces, recce strategy, stage times variability.

**Endurance Racing**

Le Mans 24 Hours: 13.5 million viewers across TV and streaming (ACO, June 2023). World Endurance Championship (WEC) features Hypercars, LMP2, and GTE categories.

Unique factors: Multi-driver lineups (Bronze/Silver/Gold ratings), 24-hour race strategy, pit crew fatigue, mechanical reliability over distance, fuel/tyre strategy over triple stints.

Management focus: Driver rotation schedules, night driving specialists, mechanical sympathy traits, team endurance across multiple classes simultaneously.

**Drag Racing**

NHRA (National Hot Rod Association): Reaches 65 million viewers annually across US broadcasts (NHRA media kit, 2023). Top Fuel dragsters accelerate 0-100mph in 0.8 seconds.

YouTube presence: NHRA official channel at 654,000 subscribers, featuring full race coverage and technical breakdowns.

Management focus: Reaction time specialists, mechanical tuning (gear ratios, launch control, clutch management), single-elimination brackets, crash damage affecting subsequent rounds.

**Street/Urban Racing**

Formula E: 316 million TV viewers globally (Formula E, 2022-23 season report). Races in city centres including Monaco, Rome, Berlin.

Instagram: 3.8 million followers. Younger demographic than traditional motorsport (61% under 35, Formula E audience survey 2023).

Management focus: Energy management strategy, Attack Mode timing, street circuit characteristics (limited overtaking), manufacturer politics in electric series.

**Rallycross**

World Rallycross Championship: 185 million TV viewers (WRX Promoter, 2022). Combines circuit racing with rally car specifications.

Format: Short 5-6 lap races, compulsory joker lap, knockout qualifying structure, mixed surface (tarmac/gravel).

Management focus: Joker lap strategy, start position importance (first corner advantage), car setup compromises for mixed surfaces.

**Touring Cars**

British Touring Car Championship: 4.2 million viewers per event (ITV Sport, 2023 averages). Three races per weekend with success ballast system.

Multiple categories globally: DTM (Germany), V8 Supercars (Australia), WTCR (worldwide).

Management focus: Success ballast mitigation, reverse grid races, mixed weather strategy, production-based regulations limiting development freedom.

## 2.4 YouTube Content Creator Economy

**Football Manager Content Analysis**

Top creators demonstrate substantial engagement with management simulation content:

*WorkTheSpace* (487K subscribers)
- Format: Long-term save series (40-80 episodes)
- Average views: 60,000-120,000 per episode
- Content style: Narrative-driven, focuses on building clubs from lower leagues
- Upload frequency: 3-4 videos weekly

*Zealand* (401K subscribers)
- Format: Tactical experiments, challenge runs, "Road to Glory" series
- Average views: 80,000-150,000 per episode
- Content style: Educational with entertainment elements
- Community engagement: Active Discord (15,000+ members)

*Lollujo* (328K subscribers)
- Format: Story-driven career modes, "Pentagon Challenge" style content
- Average views: 50,000-100,000 per episode
- Series length: 30-50 episodes typical
- Appeal: Emergent narratives from simulation

These creators monetise through:
- AdSense revenue (estimated £3-8k monthly based on view counts)
- Sponsorships (NordVPN, GFuel appear regularly)
- Membership systems (YouTube/Patreon, £3-10k monthly for top creators)

**Existing Motorsport Management Content**

*aarava* (1.37M subscribers)
- Primary focus: F1 codemasters games (racing not management)
- Management content: F1 Manager series achieved 100K-200K views per episode (2023)
- Series length: 15-20 episodes before apparent content exhaustion
- Audience demand: Comments consistently request longer series

*TommoMcCluskey* (156K subscribers)
- Specialises in F1 Manager career modes
- Average views: 15,000-30,000 per episode
- Issue: Runs out of compelling content after season 3-4
- Direct quote from video (Episode 18, November 2023): "The game becomes too easy once you understand the systems"

**Content Gap Analysis**

Football Manager supports 40-80 episode series because:
1. Emergent narratives (unexpected transfers, relegation battles, wonderkids)
2. Multiple career paths (different leagues, different management styles)
3. Sufficient depth preventing "solved" gameplay

Motorsport managers fail to sustain series because:
1. Predictable progression (same drivers peak at same times)
2. Limited scope (single discipline becomes repetitive)
3. Shallow systems (optimal strategy discovered quickly)

**Potential Content Creator Market**

If Momentum matches Football Manager's replayability, potential YouTube audience:
- Motorsport interest + management sim interest (overlap demographic)
- Formula 1 YouTube (10.1M subscribers) + WRC (1.47M) + NASCAR (1.89M) = 13.46M potential
- Football Manager creators (combined 2M+ subscribers) demonstrate content format viability
- Estimated addressable creator market: 50-100 channels could build audiences around deep motorsport manager

Conservative projection: 20 active content creators with average 50K subscribers = 1M reach. Content drives discovery and sales (Football Manager sees 15-20% purchase attribution to YouTube content, per Sports Interactive GDC talk 2019).

---

# 3.0 State of the Art Analysis

## 3.1 Competitive Landscape

**Football Manager 2024** (Sports Interactive/SEGA)

*Technical Architecture*
- Match engine: 3D real-time simulation, 100+ on-pitch calculations per second
- Database: Over 800,000 individuals across 143 leagues
- AI: Role-based tactical AI, personality-driven player behaviour
- Development: 12-month cycle, team of 200+ developers

*Commercial Performance*
- Launch sales: 1.04 million (first month, November 2023)
- Lifetime franchise: 13 million+ copies
- Revenue model: Annual release (£34.99) + in-game editor DLC (£3.99)
- Platform: PC (Steam), Xbox, PlayStation, Nintendo Switch, Mobile

*Community Engagement*
- Steam Workshop: 25,000+ user-created databases and graphics packs
- Official forum: 350,000+ registered users
- Modding tools: Official editor enabling league creation and player editing

*Why It Works*
- Emergent narratives (wonderkids, shock relegations, underdog cup runs)
- Depth preventing "solved" gameplay (1,000+ hours common playtime)
- Persistent world simulation (background events create dynamic environment)
- Annual improvements maintain player investment

*Limitations for Motorsport Adaptation*
- Team-based sport structure (11v11 vs individual driver + constructor battle)
- Match events fundamentally different from race events
- Database of real players (licensing model unsuitable for motorsport)

**F1 Manager 2024** (Frontier Developments)

*Technical Architecture*
- 3D race visualisation with real-time strategy decisions
- Official F1 license (all 2024 teams, drivers, circuits)
- Real-time telemetry simulation (tyre deg, fuel, ERS management)
- Development: 18-month initial development, annual updates

*Commercial Performance*
- Launch concurrent players: 2,341 (SteamDB, August 2024)
- Decline from F1 Manager 2022: 7,821 launch players (68% drop)
- Steam reviews: Mixed (62% positive from 5,847 reviews)
- Player retention: Median playtime 14.7 hours (SteamSpy estimate)

*Strengths*
- Authentic F1 presentation (licensed teams, accurate calendar)
- Strong tutorial systems (accessible to newcomers)
- Detailed car development mechanics (aero/chassis/powertrain)
- Real-time race strategy decisions create tension

*Critical Weaknesses*
- Predictable AI driver performance (Hamilton always peaks 95+, Stroll always 75-80)
- Linear car development (optimal upgrade path discovered by season 2)
- Limited scope (F1/F2 only, no broader motorsport career paths)
- Static driver potential (no emergent wonderkids or unexpected declines)

*Player Feedback Analysis* (Steam reviews, November 2024)
- "Becomes repetitive after winning first championship" (recurring complaint)
- "AI makes same mistakes every race" (strategy predictability issue)
- "Career mode too easy by season 3" (difficulty curve problem)
- "Wish there were lower formulas to build from" (scope limitation)

**Motorsport Manager** (Playsport Games, 2016)

*Technical Architecture*
- 2D race visualisation with strategic overlays
- Custom fictional universe (no licensed content)
- Three disciplines: Open-wheel, GT, Endurance
- Unity engine, released for PC/Mac/Linux

*Commercial Performance*
- Lifetime sales: 446,000 copies (SteamSpy, accessed November 2024)
- No updates since 2017 (7-year abandonment)
- Steam reviews: Very Positive (86% from 7,134 reviews)
- Player retention: Median 11.2 hours (SteamSpy estimate)

*Innovative Elements*
- Multi-discipline structure (precursor to this project's approach)
- Accessible price point (£11.99 vs F1 Manager's £34.99)
- Chairman objectives system (varied career challenges)
- Modular race simulation (adjustable speed/detail)

*Fatal Flaws*
- Static universe (predetermined drivers, no procedural generation)
- Small scale (approximately 200 drivers across all categories)
- Limited longevity (player dominance inevitable by season 5-6)
- Abandoned development (no community modding support)

*Why It Matters*
- Proves market appetite for multi-discipline motorsport management
- Demonstrates fictional universe avoids licensing costs
- Shows accessible pricing can succeed (outsold F1 Manager 2024 lifetime)
- Abandonment creates market gap this project addresses

## 3.2 Adjacent Markets

**iRacing** (Simulation Racing Platform)

Not a management game but demonstrates motorsport engagement patterns:
- Membership: 200,000+ active subscribers (iRacing metrics, 2023)
- Subscription: £10.50/month base + content purchases
- Annual revenue: Estimated £25-30 million
- User-created content: Paints, setups, race series

Relevance: Proves £10+ monthly spend willingness for motorsport simulation depth.

**Gran Turismo 7** (Polyphony Digital, 2022)

- Sales: 5.45 million copies (PlayStation, January 2024)
- Career mode: Single-player progression through licenses and championships
- Vehicle count: 424 cars spanning motorsport history
- Player engagement: Average playtime 42 hours (PSN trophies data)

Relevance: Shows appetite for varied motorsport disciplines within single title.

**Assetto Corsa Competizione** (Kunos Simulazioni, 2019)

- Sales: 800,000+ copies (SteamSpy + console estimates)
- Focus: GT World Challenge official license
- Community: Active modding scene despite official single-series focus
- Career mode: Basic progression system, primarily multiplayer-focused

Relevance: Demonstrates niche disciplines (GT3 racing) support dedicated fanbases.

## 3.3 Academic & Technical References

**Multi-Agent Systems**
- Wooldridge, M. (2009). *An Introduction to MultiAgent Systems* (2nd ed.). Wiley.
  - Foundation for AI-driven team/driver decision-making
  - Agent autonomy principles applied to persistent world simulation

**Monte Carlo Methods in Sports**
- Silver, N. (2012). *The Signal and the Noise: The Art and Science of Prediction*. Penguin.
  - Statistical forecasting methods adapted for race outcome simulation
  - Probability distribution modelling for performance variability

**Procedural Content Generation**
- Shaker, N., Togelius, J., & Nelson, M. J. (2016). *Procedural Content Generation in Games*. Springer.
  - PCG techniques for championship generation and balance
  - Validation methodologies ensuring generated content quality

**Emergent Narrative Systems**
- Mateas, M., & Stern, A. (2003). "Façade: An Experiment in Building a Fully-Realized Interactive Drama." *Game Developers Conference*.
  - Systems generating stories through simulation rather than scripting
  - Player agency in narrative development

**Sports Simulation Design**
- Sweetser, P., & Wyeth, P. (2005). "GameFlow: A model for evaluating player enjoyment in games." *Computers in Entertainment, 3*(3).
  - Player engagement metrics applicable to management simulation
  - Flow state maintenance through balanced challenge

