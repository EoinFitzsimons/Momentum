# Momentum - Multi-Discipline Motorsport Management Simulator

Project Type: Final Year Computer Science Project
Primary Focus: Python backend simulation plus desktop GUI
Current Status: Active development (playable areas, incomplete game loop)

## Overview

Momentum is a motorsport management simulator built around six racing disciplines:

1. Single Seater
2. Production/Touring
3. Urban/Street (drifting-focused)
4. Drag/Acceleration
5. Sprint/Rallycross
6. Endurance

The project currently centers on a Python backend with FastAPI endpoints, SQLite persistence, race/championship logic, and a PyQt6 desktop GUI launcher.

## What Exists Today

- FastAPI app in `Momentum/Python/simulation.py`
- Core data layer in `Momentum/Python/database/`
- Service layer in `Momentum/Python/services/`
- API schemas in `Momentum/Python/api/schemas.py`
- Race logic in `Momentum/Python/RaceLogic/`
- Desktop GUI entrypoint in `Momentum/Python/GUI/launcher.py`
- Configuration and environment handling in `Momentum/Python/config.py`

## Repository Layout (Current)

```text
FinalProject/
|- README.md
|- Momentum/
|  |- Python/
|  |  |- simulation.py
|  |  |- config.py
|  |  |- requirements.txt
|  |  |- api/
|  |  |- database/
|  |  |- GUI/
|  |  |- RaceLogic/
|  |  |- services/
|  |  |- systems/
|  |  |- tests/
|  |  |- scripts/
|  |  |- docs/
|  |  |- mvp_tests/
|- Planning/
|- Branding/
|- Reflections/
|- scripts/
```

## Technology Stack

- Python
- FastAPI plus Uvicorn
- SQLite
- Pydantic
- NumPy, Pandas, SciPy
- PyQt6
- Faker
- python-dotenv

See `Momentum/Python/requirements.txt` for the active dependency list.

## Setup

### 1. Clone

```bash
git clone https://github.com/EoinFitzsimons/FinalProject.git
cd FinalProject/Momentum/Python
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Optional .env

Create `Momentum/Python/.env` if you want to override defaults from `config.py`.

Typical options:

```env
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true
DEFAULT_CURRENCY=EUR
DATABASE_PATH=database/momentum.db
```

## Running the Project

### Run API server

From `Momentum/Python`:

```bash
python simulation.py
```

Or explicitly with Uvicorn:

```bash
uvicorn simulation:app --reload --host 127.0.0.1 --port 8000
```

### Run desktop GUI

From `Momentum/Python`:

```bash
python GUI/launcher.py
```

## Testing

This repo contains multiple targeted test scripts under `Momentum/Python/tests/` and `Momentum/Python/mvp_tests/`.

Examples:

```bash
python tests/test_championship_management.py
python tests/test_hiring_system.py
python tests/test_progression_system.py
python mvp_tests/test_uc01_driver.py
```

Run tests from `Momentum/Python` so relative paths resolve correctly.

## API Highlights

The API includes endpoints for:

- Health and system checks
- Driver and team listing/details
- Team creation and budget operations
- Championship creation, schedule, standings, and recalculation
- Race event management and race result retrieval
- Hiring/contracts for drivers and staff
- Season progression operations

Interactive docs are available at `/docs` when the server is running.

## Known Gaps

- Some systems are still in progress or partially integrated.
- Not every folder has complete production-ready coverage.
- Documentation outside this README may be inconsistent while cleanup is ongoing.

## License and Contribution

Project work for academic submission. Contribution policy and licensing can be added as the repository is finalised.
