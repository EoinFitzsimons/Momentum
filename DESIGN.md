# Momentum: Game Design

Momentum is a motorsport management game played across six racing disciplines. The
player takes the role of a team manager: building a squad of drivers and staff, deciding
how the team's money is invested, and guiding the team through live races from the pit
wall. The game is single-player and runs offline on the player's own computer.

This document describes how the game is meant to work. It is written for anyone working
on Momentum, so that design decisions live in one place and the code can be checked
against them. Sections marked **[open]** are questions that still need an answer.

---

## 1. Design principles

**Performance comes from preparation.** A team's pace on track is the product of the
people it employs, the car it has developed and the decisions made during the race. Money
matters because it funds all of these, and a well-run team on a modest budget should be
able to outperform a richer team that invests poorly.

**Leagues reflect history.** Each discipline is organised into three leagues, called
tiers. A team's tier records how it has performed in previous seasons and determines who
it races against, how much it can earn and how attractive it is to drivers, staff and
sponsors. The tier itself has no bearing on how the car behaves on track.

**Races are lived, not reported.** Every race the player enters is simulated in real
time, with the player able to watch, intervene and react as it unfolds. The sense that a
result was shaped by the player's own calls is central to the experience.

**Outcomes are reproducible.** Given the same grid, settings and seed, a race plays out
identically. Variation comes from driver attributes and the player's decisions rather
than from chance that differs between runs, which keeps results explainable and makes
problems in the simulation easy to investigate.

**Disciplines have character.** The six disciplines differ in what wins races, how long
seasons are, how risky the racing is and what a team needs to invest in. A manager who
has mastered one discipline should find a different challenge in another.

---

## 2. The world

### 2.1 Disciplines and leagues

Momentum features six disciplines, each with its own calendar, points system and racing
style:

| Discipline | Rounds per season | Character |
|---|---|---|
| Single Seater | 24 | Precision, aerodynamics, politics |
| Production Touring | 12 | Close packs, contact, budgets |
| Urban Street | 10 | Style, risk, city circuits |
| Drag Acceleration | 14 | Launches, power, pressure |
| Sprint Rallycross | 12 | Mixed surfaces, short shocks |
| Endurance | 8 | Stints, reliability, patience |

Each discipline has three leagues: Tier 1 at the top, then Tier 2 and Tier 3. When a new
world is created, roughly 15% of a discipline's teams are placed in Tier 1, 30% in Tier 2
and the remaining 55% in Tier 3.

### 2.2 How the world moves on

Every league runs a full season. Races in the league the player is competing in are
simulated live. Races in all other leagues are resolved by the game at the end of the
season, so the whole world advances together: promotions and relegations happen
everywhere, every team earns and spends money, and the state of the sport changes from one
season to the next whether or not the player was watching.

---

## 3. Tiers

### 3.1 Starting placement

When a world is created, the teams in each discipline are ranked by overall strength,
taking into account their operations rating, how developed their car is and the quality
of their best two drivers. The strongest teams are placed in Tier 1 and the weakest in
Tier 3, so the top league starts with the teams that deserve to be there.

A team created later, after the world already exists, joins Tier 3 and earns its way up
through results like any other.

### 3.2 Promotion and relegation

At the end of each season, teams move between leagues based on the points their drivers
scored. Currently the bottom two teams in a league are relegated and the top two in the
league below are promoted. **[open]** Whether two places is the right number for leagues
of this size, and whether larger leagues should move more teams.

### 3.3 What a team's tier influences

- Which championship the team enters and which teams it races against.
- The prize money paid for each finishing position; Tier 1 pays the most.
- The sponsor income the team receives for each race it enters.
- **[open]** How attractive the team is to drivers, staff and managers on the market.

Tier is not used by the race simulation. Two cars with the same drivers, development and
staff will perform the same whichever league they are in.

---

## 4. Money

A team's budget is the money its owners make available to the manager. It is earned
through racing and sponsorship, and spent on developing the car, employing people and
improving the headquarters. The race simulation never reads the budget directly; its
effect on results is entirely through what it has been spent on.

### 4.1 Income

- **Prize money** is paid after every race according to finishing position. The amounts
  are scaled by the league (Tier 1 pays more than Tier 2, which pays more than Tier 3)
  and by the discipline, since the money in Single Seater racing is of a different order
  to that in Drag Acceleration.
- **Sponsor income** is paid for each race the team enters, with a larger amount in
  higher leagues.
- **[open]** An end-of-season bonus for the leading teams in each championship.
- **[open]** Named sponsors with their own goals, such as a certain number of top-five
  finishes, whose payments depend on those goals being met. This would give the money
  side of the game its own storylines.

### 4.2 Spending

- **Car development**, described in section 5. This is expected to be the largest and
  most important outlay.
- **Contracts** for drivers and staff: salaries, signing bonuses and the cost of buying
  out a contract early.
- **Headquarters actions**: marketing campaigns, driver development programmes, staff
  training, and facility upgrades (driver academy, simulation lab, data centre and
  marketing suite).
- **[open]** Running costs per race, such as logistics, tyres and accident damage, so that
  a budget is always under some pressure and an incident has a financial cost.

### 4.3 AI teams

AI teams earn income in exactly the same way as the player's team, from the same prize
table and sponsor rates. In the off-season each AI team invests around a third of its
budget in car development, prioritising its weakest areas while keeping a reserve of
about a tenth of its budget untouched.

**[open]** Whether AI teams should also invest during the season, and whether a team's
strategy profile (conservative, standard or aggressive) should influence how freely it
spends.

---

## 5. Car development

Each team develops its car in five areas, each with ten levels:

- **Power Unit**: straight-line speed and acceleration.
- **Aerodynamics**: cornering speed and efficiency.
- **Chassis and Handling**: balance, braking and change of direction.
- **Reliability**: resistance to mechanical failure.
- **Race Operations**: pit work, strategy execution and general organisation.

Each level costs more than the one before it, rising by about 35% per step, and the
prices are scaled to the discipline so that a Single Seater upgrade costs considerably
more than the equivalent in Drag Acceleration. The early levels deliver the biggest
improvements; the later ones bring diminishing returns, so a fully developed car is hard
to beat but not untouchable.

Power, Aerodynamics, Handling and Race Operations together determine the car's
development rating, which the simulation uses alongside the team's operations rating and
staff to set the team's pace. Reliability determines how likely the car is to suffer a
mechanical failure over a race distance.

**[open]** Whether development should reset or partially carry over between seasons, in
the manner of a regulation change, so that the development race restarts and a dominant
team can be caught.

**[open]** Whether the areas should be weighted differently per discipline, for example
Power in Drag Acceleration, Reliability in Endurance and Handling in Rallycross, so that
the disciplines feel different in the garage as well as on the track.

---

## 6. People

### 6.1 Drivers

Drivers are rated from 0 to 100 across speed, racecraft, consistency, fitness, reactions,
performance under pressure, setup knowledge, fuel management, tyre management, feedback
and adaptability. Teams field two drivers, or four in Endurance where cars are shared.

Drivers develop over a career: they tend to peak between about 28 and 32, decline from
their mid-thirties and retire around 45 or earlier if results fall away. Young drivers
improve through racing. Each driver has a contract with a length, a salary and a signing
bonus, and ending a contract early requires a buyout.

### 6.2 Staff

Staff fill roles such as engineers, strategists, pit crew and aerodynamicists. Each role
contributes a modest bonus to a particular part of the car or the race operation. These
bonuses saturate, so the first capable hire in a role makes the most difference and a
team cannot buy its way to dominance by stacking elite staff.

**[open]** Staff limits are currently tied to tier (60, 40 and 25 for Tiers 1 to 3).
It may be better for budget alone to limit the size of the team.

### 6.3 Managers and the manager market

Every team, including the player's, is run by a manager, and managers are employed by
the team's owners. Managers have a reputation built from their results, the leagues they
have worked in and how long they have stayed in a job.

Managers move between teams through a market that operates throughout the career:

- Team owners review their manager at the end of each season, and sometimes during one.
  A manager who has fallen well short of the owners' expectations may be dismissed, and a
  team without a manager will look to appoint one.
- A team seeking a manager considers the available candidates, weighing reputation,
  recent results and experience in the discipline. Strong candidates may be approached
  directly.
- Managers may also apply for vacancies at other teams. An application can be accepted or
  declined, and a team in a higher league will usually expect a stronger record.
- AI managers take part in the same market, so the grid of managers changes over time
  and a well-known rival may turn up at a different team.

The player experiences this market exactly as the AI managers do. They may be approached
by another team, apply for a vacancy and be turned down, or be dismissed by their own
owners after a poor run. Changing teams is therefore possible during a career, but it
happens through offers and appointments rather than at the player's discretion, and
leaving a team means leaving its drivers, staff and development behind.

**[open]** How owners' expectations should be set (for example, a target finishing
position based on the team's budget relative to the league), how much a reputation
should rise or fall per season, and whether a dismissed player manager should have a
spell without a team before new offers arrive.

---

## 7. The race

### 7.1 What determines pace

A car's pace during a race depends, in roughly descending order of influence, on:

1. how hard the driver is pushing, which the player controls;
2. the driver's attributes;
3. the team's contribution: operations rating, car development and staff;
4. track position, including slipstream on the straights and disturbed air in corners;
5. tyre wear, fuel load and weather.

### 7.2 Decisions available to the player

During a race the player can:

- set the **push intensity**, trading outright speed against tyre wear and the risk of
  mistakes;
- set the **overtaking aggression**, which governs how readily the drivers attempt
  passes;
- make **pit calls**, choosing when to stop and which tyre compound to fit;
- in Rallycross, choose when to take the mandatory **joker lap**;
- choose a **tuning preset** before the start;
- adjust the **simulation speed** and frame rate, so that a long race can be watched
  closely or moved through quickly.

**[open]** Further pit-wall tools under consideration: team orders between the two cars,
weather-based tyre gambles and reactions to safety-car periods.

### 7.3 Risk and reliability

Pushing hard with high aggression while attacking carries a genuine chance of an
incident. Mechanical failures follow a wear-out curve, becoming more likely late in a
race and in extreme heat, cold or rain, and less likely as the car's Reliability
development improves. Lap-to-lap variation comes from each driver's consistency rating.

### 7.4 Points

Each discipline has its own points table. Single Seater uses 25, 18, 15, 12, 10, 8, 6, 4,
2 and 1 for the top ten, with a bonus point for the fastest lap if the driver finishes in
the top ten; Urban Street uses the same fastest-lap bonus. Endurance awards points down to
fifteenth place and Production Touring pays deep into the field, reflecting their larger
grids.

**[open]** Drag Acceleration is run as a knockout bracket; the mapping from bracket
results to championship points needs defining.

### 7.5 Reproducibility

A race run with the same grid, settings and seed produces the same result every time.
This currently holds within a given simulation mode. The faster, coarser mode used to
resolve AI leagues at the end of a season does not reproduce a live race frame for frame.
**[open]** Whether this is acceptable, or whether AI leagues should be resolved by the
same engine running at full speed.

---

## 8. The season

A season proceeds as follows.

1. **Pre-season.** The manager reviews contracts, invests in the car and makes use of
   headquarters actions.
2. **Rounds.** For each round the team prepares (tuning preset and tyre choice), races
   live, collects prize and sponsor money and reviews the standings.
3. **Season end.** The remaining AI leagues are resolved; income is paid to every team;
   AI teams invest in their cars; promotion and relegation are applied; drivers age,
   develop and in some cases retire, with new drivers arriving to replace them; owners
   review their managers and the manager market opens; and the next season's calendar is
   generated.

**[open]** A transfer window in which expiring contracts are renewed or not and drivers
move between teams, including between AI teams, so that grids evolve from year to year.

---

## 9. Platform and presentation

Momentum is a desktop application, with Windows as the first target platform, built with
PyQt6 and storing each player's world in a single local database. The race view should
maintain its target frame rate with a full grid on an ordinary laptop; this is the
performance requirement that matters for the game. The interface uses a dark theme with
accessibility options (alternative colour themes and visible focus indicators) treated as
part of the core design.

**[open]** Multiple career saves and the ability to export a career.

---

## 10. Outside the current scope

- Multiplayer, online leaderboards and cloud synchronisation.
- Motorcycles or any non-car category.
- A hosted service: the FastAPI server is retained for tooling and tests rather than for
  players.
- Service-level concerns from the earlier SRS, such as throughput targets for batch
  simulation, worker pools and retry policies.

---

## Appendix: relationship to the earlier SRS

The earlier `SRS/` folder described a hosted simulation service. Its requirement for
deterministic simulation (R-SIM-001) and the accompanying test,
`tests/test_simulation_reproducibility.py`, remain relevant and are kept. The remaining
material, covering hosted performance profiles, failure and retry policies, a race state
machine that was never implemented and an event contract for external consumers, is
retired in favour of this document. The JSON schemas and fixtures under `SRS/` stay only
because the existing tests read them; they are test data rather than a specification.
