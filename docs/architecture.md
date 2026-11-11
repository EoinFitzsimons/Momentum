# Repository layout

Momentum is one Python package, `momentum/`, with the tests, tools, packaging
and documentation beside it. Everything is run from the repository root, so
imports are absolute (`from momentum.services.team_service import TeamService`)
and no module edits `sys.path`.

```
momentum/            the game
  gui/               PyQt6 screens; launcher.py is the entry point (python -m momentum)
    assets/          tiles and prop sprites drawn by the race view
  engine/            race simulation: base and realtime engines, race formats,
                     circuit layout, track physics, overtaking, disciplines/
  services/          game rules: teams, hiring, finance ledger, tiers, seasons,
                     championships, upgrades, progression, race engine factory
  database/          DatabaseManager, extensions, dataclass models and the
                     shipped seed world momentum.db
  data/              source data: circuits JSON, countries, nationality
                     weights, locale mapping and team naming
  vehicles/          vehicle appearance and liveries
  api/               FastAPI server (app.py) and Pydantic schemas, kept for
                     tests and modding rather than as a player route
  seed/              reproducible world build: python -m momentum.seed.build
  config.py          paths and tunables, read from the environment and .env
  race_settings.py   player-facing race view and speed settings
  logging_system.py  file logging and the exception hook
tests/               pytest suite (conftest puts the repository root on sys.path)
tools/               development scripts that earn their keep; tools/debug/ holds
                     one-off diagnostics, tools/assets/ regenerates placeholder
                     sprites, tools/lint/ the linter runner
packaging/           Momentum.spec, build_exe.ps1 and the dependency installer
docs/                technical notes, docs/srs/ (requirements, JSON schemas,
                     fixtures) and docs/branding/
```

## Conventions

- The seed database is the only binary tracked on purpose. Rebuild it with
  `python -m momentum.seed.build`; the build is deterministic and refuses to
  leave play state behind.
- Generated output (screenshots, previews, debug renders, PyInstaller output)
  goes under `build/`, `saves/` or `tools/**/*.png`, all ignored by git.
- Money only moves through `momentum.services.finance_service.FinanceService`,
  so every balance equals the sum of its ledger entries.
- Race formats are declared once per discipline engine in
  `momentum/engine/disciplines/` and inherited from `BaseDisciplineEngine`.
- Name data for manual review is exported on demand with
  `python tools/export_used_names.py` rather than committed.
