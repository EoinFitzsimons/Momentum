# Momentum

Momentum is a multi-discipline motorsport management simulator. Build a team,
develop drivers and staff, and compete across six disciplines: single-seater,
production/touring, urban/street, drag, sprint/rallycross, and endurance.

The project is currently in active development. Release builds, supported
platforms, and a first public version will be documented here as they become
available.

## Development setup

Momentum currently uses Python, PyQt6, FastAPI, SQLite, NumPy, SciPy,
Matplotlib, Pydantic, and Uvicorn.

```powershell
Set-Location Momentum/Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python GUI/launcher.py
```

Copy `.env.example` to `.env` when local configuration overrides are needed.
The API can be started with `python simulation.py` or with Uvicorn as described
in the source documentation.

## Tests

Run the test suite from `Momentum/Python`:

```powershell
python -m pytest
```

The PyInstaller build configuration is in `Momentum/Python/Momentum.spec` and
the Windows build helper is in `Momentum/Python/scripts/build_exe.ps1`.

## Repository layout

- `Momentum/Python/GUI/` - desktop interface and bundled visual assets
- `Momentum/Python/RaceLogic/` - simulation and discipline engines
- `Momentum/Python/services/` - game services and persistence orchestration
- `Momentum/Python/database/` - SQLite models and database access
- `Momentum/Python/tests/` - automated tests
- `Momentum/Python/docs/` - technical game documentation
- `SRS/` - runtime schemas and simulation contracts used by the application

## Licensing

Momentum is proprietary software. Copyright and distribution terms are in
[`LICENSE`](LICENSE). Third-party software and assets remain subject to their
own licenses; see [`NOTICE.md`](NOTICE.md).

Do not redistribute a build or its assets until the dependency and asset
licenses have been reviewed for that release.

## Reporting security issues

Please follow [`SECURITY.md`](SECURITY.md) rather than publishing sensitive
details in a public issue.
