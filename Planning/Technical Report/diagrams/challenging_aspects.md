# Challenging Aspects, Options, and Resolutions

## 1) Visual race loop (from Monte Carlo to live)

- **Challenge:** Monte Carlo races finished instantly and there was no live feedback for the GUI or for on-the-fly management.
- **Resolution:** Switched to a frame-by-frame race engine (target approximately 30 FPS) with driving modes (ATTACK, DEFEND, MANAGE, CRUISE) updated each tick, and the GUI now reflects the live state.
- **Alternatives weighed:**
  - Artificial delay on Monte Carlo (rejected because it produced fake time and did not enable true interactivity)
  - Coarse lap or sector stepping (rejected because it was too blunt and provided weak strategic feedback)
- **Evidence and links:** INFORMATION_ARCHITECTURE.drawio (Race Setup to Race Live), WIREFRAMES.drawio (race screen), ACTIVITY_DIAGRAM.drawio or SEQUENCE_DIAGRAM.drawio for the tick loop if present.
- **What next:** Add a sim speed control, light telemetry sampling (every N ticks), and readable per-tick decision logging.

## 2) Broad synthetic data without IP risk (names, teams, circuits)

- **Challenge:** 1,000+ drivers/teams/circuits without real-world IP or costly licences.
  **Resolution:** Procedural generation via Faker (24 locales), discipline-tuned templates, circuits in JSON to SQLite. All names are synthetic.
- **Alternatives weighed:**
  - Real-world datasets (rejected: copyright/licensing risk).
  - Single-locale random names (rejected: low authenticity/diversity).
- **Evidence/links:** data/circuits_database.json, config.py (Faker settings), DATABASE_ER_DIAGRAM.drawio (schema), CRUD_MATRIX.drawio (entity touchpoints).
- **What next:** Validation script to catch listed words/real-name collisions; locale weighting per discipline.

## 3) Extensible base engine with discipline overlays

- **Challenge:** One simulation core that permits discipline-specific rules (rally co-driver/surface checks; endurance reliability; drag launch) without duplicate code.
  -- **Resolution:** BaseDisciplineEngine plus DisciplineContext. Derived engines override weightings and event hooks and shared Monte Carlo and statistics utilities are used where appropriate.
- **Alternatives weighed:**
  - Per-discipline bespoke engines (rejected: duplication, maintenance risk).
  - Single monolith with if/else by discipline (rejected: brittle and hard to test).
- **Evidence/links:** ARCHITECTURE_DIAGRAM.drawio (engine structure), ACTIVITY_DIAGRAM.drawio (discipline flow), WIREFRAMES.drawio/INFORMATION_ARCHITECTURE.drawio (how strategy/results are reached).
- **What next:** Publish an extension checklist (steps to add a discipline), contract tests against the base, and a tiny exemplar (e.g., drag) showing override points.
