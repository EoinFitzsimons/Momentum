# Technical Report - Section 2.1: Requirements

## 2.1 Requirements

### 2.1.2 Data Requirements

**Database Schema:**

The system requires persistent storage for the following entities:

The repository includes a seeded dataset for drivers, teams, staff, tracks, championships, races and race results. These data are generated and validated during project setup and are included with the project distribution to enable offline, deterministic simulations and repeatable testing. The canonical seeded SQLite database file is available at `Momentum/Python/database/momentum.db` and reference JSON input files (for example `circuits_database.json`) are located in `Momentum/Python/data/`.

Data generation and import scripts are provided in `Momentum/Python/scripts/` for development purposes (re-seeding or regenerating sample data). Regeneration of seeded data is intended for development workflows and is not required for standard use of the packaged distribution.

1. **Drivers Table**

  - Primary Key: `id` (INTEGER) (commonly exposed as `driver_id` in API responses)
   - 50+ attribute columns (REAL, 0.0-100.0 range)
   - Biographical data: name, nationality, birth_date, age
   - Career statistics: races, wins, podiums, championships
   - Constraints: CHECK constraints on attribute ranges
2. **Teams Table**

  - Primary Key: `id` (INTEGER) (commonly exposed as `team_id` in API responses)
   - Budget (REAL), discipline (TEXT), tier (INTEGER)
   - Performance attributes: innovation, risk_appetite, management_quality
   - Career statistics: championships, total_wins
3. **Staff Table**

  - Primary Key: `id` (INTEGER) (commonly exposed as `staff_id` in API responses)
   - Foreign Key: `team_id` references Teams
   - 40+ attribute columns for role-specific skills
   - Contract data: salary, contract_end_date, job_satisfaction
4. **Tracks Table**

  - Primary Key: `id` (INTEGER) (commonly exposed as `track_id` in API responses)
   - Physical characteristics: length, corners, elevation_change
   - Surface data: surface_type, grip_level
   - Challenge ratings: technical_challenge, overtaking_difficulty
5. **Championships Table**

  - Primary Key: `id` (INTEGER) (commonly exposed as `championship_id` in API responses)
   - Series configuration: discipline, points_system, race_count
6. **Races Table**

  - Primary Key: `id` (INTEGER) (commonly exposed as `race_id` in API responses)
   - Foreign Keys: championship_id, track_id
   - Conditions: weather, temperature, track_condition
7. **RaceResults Table**

  - Primary Key: `id` (INTEGER) (commonly exposed as `result_id` in API responses)
   - Foreign Keys: race_id, driver_id, team_id
   - Performance data: position, fastest_lap, points_earned

**Data Integrity:**

- Foreign key constraints enforce referential integrity
- CHECK constraints validate attribute ranges
- UNIQUE constraints prevent duplicate entries
- NOT NULL constraints on critical fields

**Performance Optimisation:**

- Indexes on frequently queried fields (driver_id, team_id)
- Composite indexes on race lookups (championship_id, race_id)
- Query optimisation for large result sets

### Entity Relationship Diagram

### 2.1.3 User Requirements and Usability Targets

Target Users:

- **Motorsport Enthusiasts**: Players with domain knowledge of racing who seek narrative and an interactive world simulation.
- **Data Driven Gamers**: Players who prefer management depth, analytical systems, and data-driven decision making.

The following pairs each User Requirement with explicit, measurable Usability Requirements. Each usability item includes an acceptance criterion and a suggested test method. This in‑file pairing provides immediate traceability from feature to quality target.

Mapping policy:

- Usability requirements are classified as non‑functional requirements under usability / quality‑in‑use (see ISO 9126, ISO 9241‑11 and ISO/IEC 25010). Validation of usability targets is achieved through standard usability testing and quality assurance practices.
- The document provides a mapping between usability requirements and User Requirements to support traceability and measurable acceptance criteria. The mapping is an implementation aid and does not imply a subset or one‑to‑one relationship. A single User Requirement may relate to multiple usability targets (for example: performance, learnability, accessibility), and a single usability rule (for example: WCAG AA) may apply to multiple User Requirements.
- The pairings in this section document traceability links and suggested test plans; they do not alter the classification of usability requirements as non‑functional.

R1: Driver & Team Statistics

- User requirement: Provide detailed driver and team statistics retrievable via UI and API.
- Usability targets:
  - U-R1-1 (API latency): Median `GET /drivers/{id}` and `GET /teams/{id}` ≤150 ms; 95th‑percentile ≤800 ms (10 concurrent clients). Test: automated performance benchmark (k6/locust).
  - U-R1-2 (UI visibility): Primary stats (top 6 attributes + 5 recent races) visible without scrolling on 1080p. Test: UI snapshot checks + moderated test (n≥10), 90% findability within 5s.

R2: Race Simulation

- User requirement: Produce race simulation results that reflect driver, team, vehicle, track, weather and race-condition parameters.
- Usability targets:
  - U-R2-1 (simulation latency): 90th‑percentile end‑to‑end completion time for single‑race quick race ≤5 s on recommended hardware. Test: 100 automated headless runs; compute percentiles.
  - U-R2-2 (result delivery): Top summary available ≤300 ms after completion; full payload ≤2 s. Test: API composition timing checks.

- R3: Customisation & Strategy Controls

- User requirement: Provide deep customisation and strategy controls for advanced users.
- Usability targets:
  - U-R3-1 (learnability/help): Inline help and "learn more" links present; expert users (n≥8) complete full team setup ≤5 minutes with ≤2 recoverable errors in ≥80% sessions. Test: moderated sessions.
  - U-R3-2 (discoverability): Key strategy controls discoverable within two clicks. Test: UI walkthroughs and automated path checks.

R4: Historical Career Progression

- User requirement: Record and present historical career progression for drivers and teams.
- Usability targets:
  - U-R4-1 (navigation depth): Reach driver's season history within ≤3 clicks. Test: moderated tasks + automated checks.
  - U-R4-2 (load performance): Season history (≤30 races) median server response ≤300 ms; UI render ≤500 ms. Test: backend + frontend timing tests.

R5: Simplified Guided Interface

- User requirement: Provide a simplified, guided interface mode for casual players.
- Usability targets:
  - U-R5-1 (onboarding completion): New users complete core onboarding (create basic team) ≤120 s with ≤1 navigation error in ≥80% moderated sessions (n≥10). Test: moderated onboarding sessions.
  - U-R5-2 (step budget): Simplified flow ≤4 screens/steps from dashboard to simulation. Test: UI flow verification.

R6: Quick Race

- User requirement: Support a "quick race" feature with minimal input and acceptable response times.
- Usability targets:
  - U-R6-1 (task time): First‑time user starts and views quick‑race results ≤90 s with ≤1 recoverable navigation error (moderated test n≥10). Test: moderated sessions.
  - U-R6-2 (service SLA): Follow U-R2-1 and U-R2-2 for server and delivery thresholds.

R7: Immediate Feedback for Decisions

- User requirement: Provide clear, immediate feedback in the UI for player decisions.
- Usability targets:
  - U-R7-1 (visual feedback latency): State change visual updates ≤200 ms. Test: automated UI timing.
  - U-R7-2 (activity trace): Activity feed includes timestamped entry within 2 s. Test: integration tests.

R8: Emergent Narrative & Highlights

- User requirement: Surface emergent narrative events and digestible story highlights.
- Usability targets:
  - U-R8-1 (highlight visibility): Highlights appear in the activity feed and are visible without extra navigation; acceptance: 80% of moderated users recall top highlight after 1 minute (n≥10). Test: moderated recall.

R9: Documented RESTful API

- User requirement: Provide a documented RESTful API with examples and versioning.
- Usability targets:
  - U-R9-1 (docs coverage): Documentation includes example request/response and schema for ≥95% public endpoints. Test: automated doc coverage checker.
  - U-R9-2 (API latency): Median response ≤200 ms for common endpoints; 95th‑percentile ≤800 ms under nominal load. Test: performance benchmarks.

R10: Clear Error Messages

- User requirement: Return clear, actionable error messages and standard HTTP status codes.
- Usability targets:
  - U-R10-1 (error schema): Errors include `code`, `message`, and `field` (where applicable) and validate against the documented error schema. Test: contract tests.
  - U-R10-2 (actionable guidance): Error messages include remediation where possible; acceptance: UX review with ≥90% pass on clarity checks.

R11: Efficient Querying for Large Data Sets

- User requirement: Support efficient querying for large data sets with pagination, filtering and sorting.
- Usability targets:
  - U-R11-1 (page performance): Paginated lists (page size 50) median server response ≤1 s; 95th‑percentile ≤2 s. Test: API performance tests.
  - U-R11-2 (functional APIs): Endpoints support documented pagination, filtering and sorting. Test: API contract tests.

R12: Programmatic Creation & Game‑Loop Automation

- User requirement: Enable programmatic creation and retrieval of championships, schedules, races and standings via the API.
- Usability targets:
  - U-R12-1 (creation success): Creation endpoints return ≥99% success for valid inputs; invalid inputs return structured errors. Test: integration tests.
  - U-R12-2 (automation latency): Scheduled game‑loop rollover for medium championships completes ≤10 s. Test: scheduled job timing checks.

R13: Role‑Based Controls & Audit

- User requirement: Provide role‑based controls for privileged operations with authentication and audit logging.
- Usability targets:
  - U-R13-1 (confirmation & discoverability): Privileged ops require explicit confirmation and be discoverable within ≤3 clicks. Test: admin UI walkthroughs.
  - U-R13-2 (audit completeness): Every privileged op generates an audit record with actor, action, timestamp and entity. Test: audit log validation.

R14: Meet Documented Usability & Performance Targets

- User requirement: Meet documented usability and performance targets for response times and simulation durations.
- Usability targets:
  - U-R14-1 (release gating): Releases are expected to pass automated performance checks, accessibility (WCAG AA) audit, and a small moderated usability smoke test for key flows. Test: CI gates and moderated checks.

R15: Exportable Data

- User requirement: Offer exportable data (JSON) for key entities to facilitate integration and analysis.
- Usability targets:
  - U-R15-1 (export latency): Export (≤10k rows) generates downloadable JSON ≤10 s in ≥95% runs. Test: automated export timing.
  - U-R15-2 (schema validity): Exported JSON validates against documented schema. Test: automated schema validation.

Notes: Accessibility, global UI scaling, and logging are cross‑cutting concerns and are enforced via the per‑requirement usability targets in Section 2.1.3 and the release‑gating checks described in U-R14-1 (automated performance, accessibility audits and moderated smoke tests).

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
