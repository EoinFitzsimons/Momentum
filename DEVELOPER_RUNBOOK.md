# Developer Runbook: Race Simulation SRS & Integration

---

## Quick Start

### **Prerequisites**
- Python 3.8+
- Dependencies from `Momentum/Python/requirements.txt` and `requirements-dev.txt`
- Access to `SRS/` folder (requirements, schemas, fixtures, event specs)

### **Setup**

```bash
cd Momentum/Python

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install jsonschema for SRS validation
pip install jsonschema
```

### **Verify SRS artifacts are in place**

```bash
# From repo root
ls SRS/
# Should list: requirements.yaml, determinism.md, perf_profiles.md, state_machine.md, failure_modes.md, event_contract.md
ls SRS/schemas/
# Should list: driver.schema.json, team.schema.json, track.schema.json, result.schema.json
ls SRS/event_schemas/
# Should list: lap_complete.schema.json, overtake.schema.json, incident.schema.json
ls SRS/fixtures/
# Should list: example_racecontext.json
```

---

## Running Tests

### **Reproducibility Tests (R-SIM-001)**

Tests that identical RaceContext + seed produce identical results.

```bash
cd Momentum/Python

# Run single reproducibility test
python -m pytest tests/test_simulation_reproducibility.py::test_reproducibility_with_seed -v

# Run all reproducibility tests
python -m pytest tests/test_simulation_reproducibility.py -v

# Run with determinism summary
python -m pytest tests/test_simulation_reproducibility.py::test_determinism_across_multiple_runs -v -s
```

**Expected output**: All tests pass; 5 consecutive runs with seed=42 produce identical hashes.

### **Integration Tests (R-SIM-002, R-DISC-001, R-EVT-001, R-FAIL-001)**

Tests for realtime mode, discipline adapters, event contracts, and failure recovery.

```bash
# Run all integration tests
python -m pytest tests/test_integration_srs.py -v

# Run discipline adapter tests only
python -m pytest tests/test_integration_srs.py::TestDisciplineAdapterContract -v

# Run event contract tests
python -m pytest tests/test_integration_srs.py::TestEventContract -v

# Run failure mode tests
python -m pytest tests/test_integration_srs.py::TestFailureModes -v
```

### **Full SRS Test Suite**

```bash
# From Momentum/Python folder
python -m pytest tests/test_simulation_reproducibility.py tests/test_integration_srs.py -v --tb=short
```

---

## Schema Validation

### **Validate domain objects**

Create a simple script to validate objects against SRS schemas:

```python
from tools.schema_validator import SchemaValidator

validator = SchemaValidator(schema_base_path="../../SRS")

# Validate a driver
driver_obj = {
    "id": 1,
    "name": "Test Driver",
    "status": "active",
    "attributes": {"raw_speed": 0.8}
}
valid, error = validator.validate_driver(driver_obj)
print(f"Driver valid: {valid}, error: {error}")

# Validate a result
result_obj = {
    "race_id": "race-001",
    "driver_id": 1,
    "finishing_position": 1,
    "seed": 42
}
valid, error = validator.validate_result(result_obj)
print(f"Result valid: {valid}, error: {error}")
```

---

## Running Simulations Directly

### **Simulate race with specific seed (for reproducibility validation)**

```python
from database.models import Driver, Track
from services.race_simulation_api import simulate_race

# Define drivers and track
drivers = [
    Driver(id=1, name="Driver A", preferred_discipline="formula"),
    Driver(id=2, name="Driver B", preferred_discipline="formula")
]

track = Track(
    id=1,
    name="Test Track",
    lap_time=78.0,
    length_km=5.0
)

# Run simulation
results = simulate_race(
    drivers=drivers,
    track=track,
    seed=42,  # Critical: fixed seed for reproducibility
    laps=5,
    verbose=True
)

# Print results
for r in results:
    print(f"Driver {r.driver_id}: Position {r.position}, Points {r.points}")
```

### **Run with event callback (for telemetry capture)**

```python
events = []

def capture_event(event: dict) -> None:
    events.append(event)
    if len(events) % 100 == 0:
        print(f"Captured {len(events)} events...")

results = simulate_race(
    drivers=drivers,
    track=track,
    seed=42,
    laps=5,
    event_callback=capture_event,
    verbose=False
)

print(f"Total events captured: {len(events)}")
```

---

## Key Development Workflows

### **1. Adding a new requirement**

When implementing a new feature:

1. **Add requirement to SRS**: Edit `SRS/requirements.yaml`
   - Assign unique ID (e.g., R-NEW-001)
   - Write acceptance criteria
   - Reference test file(s)

2. **Create schema if needed**: Add JSON Schema to `SRS/schemas/` or `SRS/event_schemas/`

3. **Write test first**: Create test in `tests/` that validates acceptance criteria

4. **Run test to confirm failure**: Verify baseline before implementation

5. **Implement feature**

6. **Validate test passes**: Run pytest on your new test

7. **Verify SRS artifacts**: Ensure schemas and docs are up-to-date

### **2. Modifying a discipline tuning**

To adjust race mechanics for a discipline (e.g., urban street):

1. **Locate tuning**: Edit `Momentum/Python/RaceLogic/disciplines/urban_street/urban_street_discipline.py`

2. **Update `_apply_tuning()` method**: Modify constants like:
   ```python
   engine.BASE_SPEED_MPS = 60.0
   engine.OVERTAKE_INCIDENT_MULTIPLIER = 2.9
   ```

3. **Document change**: Add comments explaining why (e.g., "Increased to encourage more overtakes")

4. **Run reproducibility tests** to ensure determinism is preserved:
   ```bash
   python -m pytest tests/test_simulation_reproducibility.py -v
   ```

5. **Test in UI** or run an experiment with known seed to observe behavior

6. **Commit with message**: `"tuning(urban_street): increase overtake multiplier to 2.9"`

### **3. Adding a new event type**

To add a new event that engines can emit:

1. **Create JSON Schema**: Add `SRS/event_schemas/new_event.schema.json`
   ```json
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "title": "new_event",
     "type": "object",
     "required": ["event_id", "schema_version", "event_type", "race_id", "timestamp", "payload"],
     "properties": { ... }
   }
   ```

2. **Add validator support**: Update `tools/schema_validator.py` if needed

3. **Update engine to emit**: Wire event emission in `RaceLogic/realtime_race_engine.py`

4. **Add test**: Create test that verifies event schema compliance

5. **Update SRS**: Document event in `SRS/event_contract.md`

### **4. Scaling performance (Phase 2)**

When throughput requirements demand scaling:

1. **Baseline current performance**:
   ```bash
   python -m pytest perf/bench_single_sim.py -v
   ```

2. **Follow SRS/perf_profiles.md** for target SLAs

3. **Implement worker pool**: Container + queue design per architecture docs

4. **Add async persistence**: Queue events to separate writer process

5. **Benchmark again**: Verify SLA achieved

6. **Document in runbook**: Add scaling section

---

## Troubleshooting

### **Determinism tests failing**

**Symptoms**: `test_reproducibility_with_seed` or `test_determinism_across_multiple_runs` fail with hash mismatch.

**Diagnosis**:
- Check seed is propagated end-to-end: `grep -r "seed" Momentum/Python/RaceLogic/realtime_race_engine.py`
- Look for floating-point math that may be nondeterministic (e.g., dict iteration order pre-Python 3.7, unordered sets)
- Check for threading/async code that reorders events

**Fix**:
- Ensure all RNG instances use the same seed
- Use stable iteration order (sorted dicts/lists)
- Run in single-threaded mode for determinism tests

### **Event callback not being called**

**Symptoms**: `events_captured` list is empty.

**Diagnosis**:
- Check engine implementation emits events: `grep "event_callback" Momentum/Python/RaceLogic/realtime_race_engine.py`
- Verify callback is not None: `assert event_callback is not None`

**Fix**:
- Ensure engine's event emission code is reachable (not commented out)
- Check for exceptions swallowing the callback invocation

### **Schema validation failing**

**Symptoms**: `validator.validate_driver()` returns False.

**Diagnosis**:
- Confirm schema is loaded: `print(validator.schemas.keys())`
- Check object conforms to schema (print both schema and object)

**Fix**:
- Verify `SRS/schemas/driver.schema.json` exists and is valid JSON
- Add missing required fields to object
- Update schema if intentionally allowing new fields

---

## CI/CD Integration

### **Pre-commit checks**

Run before committing:

```bash
# Reproducibility + integration tests
python -m pytest tests/test_simulation_reproducibility.py tests/test_integration_srs.py --tb=short

# Linting (if configured)
python -m pylint Momentum/Python/services/race_simulation_api.py
```

### **CI Job (GitHub Actions, GitLab CI, etc.)**

See `.github/workflows/srs_validation.yml` or equivalent.

Key steps:
1. Install dependencies
2. Run SRS tests (reproducibility + integration)
3. Generate coverage report
4. Validate SRS artifacts (schemas, fixtures exist)
5. Upload results

---

## Documentation Map

| Document | Purpose |
|----------|---------|
| `SRS/requirements.yaml` | Traced requirements with acceptance criteria |
| `SRS/determinism.md` | Formal determinism definition and validation |
| `SRS/perf_profiles.md` | Hardware baselines and SLAs |
| `SRS/state_machine.md` | Race lifecycle and state transitions |
| `SRS/failure_modes.md` | Failure classes and recovery policies |
| `SRS/event_contract.md` | Event schema versioning and delivery guarantees |
| `SRS/schemas/` | Domain object JSON Schemas |
| `SRS/event_schemas/` | Event type JSON Schemas |
| `SRS/fixtures/` | Example RaceContext for testing |
| `EMPLOYMENT_ANALYSIS.md` | Full employability & skills report |
| This runbook | Developer workflow and commands |

---

## Contact & Questions

For questions on:
- **SRS & requirements**: See `SRS/requirements.yaml` and `SRS/README.md`
- **Test failures**: Check `tests/` and run with `-v -s` for verbose output
- **Schema validation**: Review `tools/schema_validator.py` and JSON schemas
- **Architecture**: See `Planning/Design and Architecture/` and `SRS/state_machine.md`
- **Employment positioning**: Review `EMPLOYMENT_ANALYSIS.md`

---

Generated by Copilot SRS Integration | April 2026
