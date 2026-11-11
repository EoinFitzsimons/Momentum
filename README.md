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
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m momentum
```

Everything runs from the repository root; `python -m momentum` starts the game
and `python -m momentum.api.app` the FastAPI server used by tests and modding.
A checkout plays straight from the tracked seed database. A packaged or
`pip`-installed game copies that seed on first launch into a per-user folder
(`MOMENTUM_DATA_DIR`, else `%LOCALAPPDATA%\\Momentum`, `~/Library/Application
Support/Momentum` or `~/.local/share/momentum`) and saves there.

Copy `.env.example` to `.env` when local configuration overrides are needed.

The game starts from the seed database `momentum/database/momentum.db`:
six disciplines, five leagues of 20 teams each, 1,500 drivers and their staff,
plus every circuit in `momentum/data/circuits/` (one file per discipline, validated by `momentum/data/circuit_schema.py`). It is built from
source by `python -m momentum.seed.build`, which always produces the same file
for the same seed. Nationalities follow each discipline's real-world heartlands
(see `momentum/data/nationality_weights.py`), with smaller nations kept well
represented.

## Tests

Run the test suite from the repository root:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

The PyInstaller build configuration is in `packaging/Momentum.spec` and
the Windows build helper is in `packaging/build_exe.ps1`.

## Repository layout

- `momentum/` - the game package: `gui/`, `engine/`, `services/`, `database/`,
  `data/`, `vehicles/`, `api/` and `seed/` (see `docs/architecture.md`)
- `tests/` - automated tests, run from the repository root
- `tools/` - development scripts (seed world, circuits, previews, accessibility
  captures); one-off diagnostics live in `tools/debug/`
- `packaging/` - PyInstaller spec and Windows build scripts
- `docs/` - technical documentation, `docs/srs/` (determinism requirement, JSON
  schemas and fixtures used by the tests) and `docs/branding/`
- `DESIGN.md` - the game design: leagues, money, upgrades, people, races and seasons

## Licensing

Momentum is proprietary software. Copyright and distribution terms are in
[`LICENSE`](LICENSE). Third-party software and assets remain subject to their
own licenses; see [`NOTICE.md`](NOTICE.md).

Do not redistribute a build or its assets until the dependency and asset
licenses have been reviewed for that release.

## Reporting security issues

Please follow [`SECURITY.md`](SECURITY.md) rather than publishing sensitive
details in a public issue.
