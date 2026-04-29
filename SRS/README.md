SRS artifacts for FinalProject (Race Simulation)

This folder contains starter SRS artifacts produced by analysis:
- `requirements.yaml`: numbered requirements with acceptance criteria and test mappings
- `determinism.md`: formal determinism acceptance and test fixtures
- `perf_profiles.md`: hardware/workload baselines and SLAs
- `state_machine.md`: race lifecycle and transitions
- `failure_modes.md`: failure classes and recovery policies
- `event_contract.md` and `event_schemas/`: event schemas and contract guidance
- `schemas/`: JSON Schemas for domain objects (`Driver`, `Team`, `Track`, `Result`)

Use these as the authoritative source for implementing verification tests and CI checks.
