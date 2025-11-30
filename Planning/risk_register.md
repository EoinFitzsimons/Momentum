**Risk Register — Momentum (Planning-first Final Year Project)**

Scope: technical risks for the Python backend (`Momentum/Python/`) and repository hygiene that could impact deliverables, timeline, or evaluation criteria.

Format: each entry lists Description, Probability, Impact (High/Med/Low), Mitigation, Acceptance Criteria.

1. Schema drift / lack of migrations
- Description: The project uses raw `SCHEMA_SQL` applied directly via `sqlite3`. Without migrations, schema changes are hard to evolve and can break saved data.
- Probability: High
- Impact: High
- Mitigation:
  - Generate typed ORM models from `SCHEMA_SQL` (SQLModel/SQLAlchemy) as a canonical model layer.
  - Add Alembic (or simple migration scripts) and a documented migration process.
  - Create automated tests that assert expected schema and run in CI against an in-memory DB.
- Acceptance criteria: ORM models exist for core tables (`drivers`, `teams`, `tracks`), Alembic initialized, and a passing migration smoke test in CI.

2. Large/binary artifacts in repository history
- Description: Committed DB files, caches, and large media inflate repository size and complicate cloning and CI.
- Probability: High
- Impact: Medium (storage/performance) -> High (if left unaddressed for marking / hand-in)
- Mitigation:
  - Remove runtime DBs from index (backed up) and add `.gitignore` entries (done).
  - Move large design/media to external archive or Git LFS and keep placeholders in repo.
  - Document regeneration steps for DB and caches in `docs/DB_POLICY.md`.
- Acceptance criteria: No tracked `.db` or large binary files in working index; archive location documented.

3. High coupling between systems and persistence
- Description: Many modules import `DatabaseManager` and dataclasses directly. This couples business logic tightly to sqlite3 implementation and file paths.
- Probability: High
- Impact: High (refactor cost, testability)
- Mitigation:
  - Introduce a small persistence facade / repository interface and adapt a single subsystem to use it as a prototype.
  - Add dependency-injection-friendly patterns so core systems accept a `Persistence` object in constructors.
  - Write unit tests for the facade and one calling subsystem before wider refactor.
- Acceptance criteria: At least one subsystem (e.g., `scripts/generate_initial_database.py` or `systems/world_state.py`) uses the facade and passes unit tests.

4. Missing or insufficient unit tests / no CI
- Description: Tests exist but are not enforced by CI; lack of coverage around `DatabaseManager`, `GameLoop`, and `race_simulation` increases regression risk.
- Probability: High
- Impact: High (grading risk, regressions)
- Mitigation:
  - Add a minimal GitHub Actions workflow to run lint + pytest smoke tests on PRs and pushes to `main`.
  - Prioritise unit tests for `DatabaseManager` init, `race_simulation` deterministic runs (seeded RNG), and `GameLoop` step.
- Acceptance criteria: CI workflow runs on PRs and `pytest` suite (core tests) passes on main branch.

5. Heavy or platform-specific dependencies (PyQt6, torch)
- Description: GUI (PyQt6) and ML (torch) dependencies complicate CI and local setup (heavy, platform-specific wheels). They also increase cognitive load for examiners running the project.
- Probability: Medium
- Impact: Medium
- Mitigation:
  - Separate heavy dependencies into extras in `requirements.txt` or `pyproject.toml` (e.g., `requirements-dev.txt` vs `requirements-core.txt`).
  - Ensure core CI installs only lightweight core deps; mark GUI and ML tests optional / manual.
- Acceptance criteria: CI runs only with core test deps; README documents how to install extras for local full-run.

6. Accidental secrets or `.env` leakage
- Description: `.env` files or API keys accidentally included in history are a security and evaluation risk.
- Probability: Low–Medium
- Impact: High (security + marking issues)
- Mitigation:
  - Run a repository scan for secrets (heuristic checks for `API_KEY`, `SECRET`, `TOKEN`, or `.env` files) and remove/rotate any found.
  - Add `pre-commit` hooks or a GitHub Action to scan for secrets on PRs.
- Acceptance criteria: No committed secrets; a pre-commit secret scan configured for new commits.

7. Data loss / backup practices
- Description: Deleting or untracking DBs without reliable backups risks losing curated databases used for demos or marking.
- Probability: Low (we backed up) 
- Impact: High
- Mitigation:
  - Keep offline backups and document regeneration steps (`scripts/generate_initial_database.py`).
  - Preserve at least one dated backup in `FinalProject_db_backups` outside the repo (confirmed present).
- Acceptance criteria: Backup folder exists and contains expected DB files; regeneration script can produce a seed DB in a fresh environment.

8. Performance / scaling assumptions in simulation
- Description: Monte Carlo simulation and large-scale in-memory operations may not scale and can cause long runtime on limited hardware.
- Probability: Medium
- Impact: Medium
- Mitigation:
  - Add configuration for Monte Carlo iteration count (lower defaults) and document recommended hardware or sample scaling values for tests.
  - Add a deterministic, low-iteration mode used by CI/tests.
- Acceptance criteria: CI tests use deterministic, low-cost simulation parameters and complete within the CI time limit.

9. Incomplete or coupled game loop and state management
- Description: `systems/game_loop.py` and related systems are partially implemented and tightly integrated with UI and DB access.
- Probability: High
- Impact: High
- Mitigation:
  - Refactor game loop to a small, testable core with clear inputs/outputs and minimal side-effects.
  - Add integration tests that exercise one loop tick with in-memory DB.
- Acceptance criteria: `game_loop` core has a small, tested function that runs a single tick with injected dependencies.

Next actions
- Finalise this register by linking each mitigation to an actionable todo (e.g., "Generate SQLModel drivers/teams" => prototype PR).
- Start the ORM prototype for `drivers` and `teams` (recommended next step).

Owners: Project lead (you) for decisions and the codebase; I can implement prototypes and CI scaffolds on request.
