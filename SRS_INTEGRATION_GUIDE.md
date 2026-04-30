# SRS INTEGRATION GUIDE: End-to-End Implementation

---

## Overview

This guide provides a **complete pathway** to implement and validate the **FinalProject SRS** across all lifecycle phases (Requirements → Design → Implementation → Testing → Operations).

**Status**: SRS Phase Complete. Ready for team implementation.

---

## SRS DOCUMENTS COMPLETED

| ID | Title | Document | Status |
|----|-------|----------|--------|
| R-SIM-001 | Deterministic simulation execution | `SRS/determinism.md` |  Specs + tests |
| R-SIM-002 | Realtime mode and event streaming | `SRS/requirements.yaml` |  Tests wired |
| R-DISC-001 | Discipline adapter contract | `SRS/requirements.yaml` |  Tests wired |
| R-DB-001 | Domain object schemas and persistence | `SRS/schemas/` |  Schemas defined |
| R-EVT-001 | Event contract and ordering guarantees | `SRS/event_schemas/` |  Schemas + tests |
| R-PERF-001 | Performance profiles and SLAs | `SRS/perf_profiles.md` |  Documented |
| R-STATE-001 | Race state machine | `SRS/state_machine.md` |  Documented |
| R-FAIL-001 | Failure modes and recovery | `SRS/failure_modes.md` |  Tests wired |

---

## COMPONENT INTEGRATION CHECKLIST

### **Phase 1: Validation & Verification (NOW)**

-  SRS requirements formally documented with acceptance criteria
-  JSON schemas created for all domain objects (Driver, Team, Track, Result)
-  Event schemas defined (lap_complete, overtake, incident)
-  Reproducibility test (`test_simulation_reproducibility.py`) wired to actual engine
-  Integration tests created (`test_integration_srs.py`) covering adapters, events, failures
-  Schema validator utility (`tools/schema_validator.py`) implemented
-  CI/CD workflow (`.github/workflows/srs_validation.yml`) configured
-  Developer runbook (`DEVELOPER_RUNBOOK.md`) written
-  Employment analysis document (`EMPLOYMENT_ANALYSIS.md`) completed

### **Phase 2: Enhancement (Team Implementation)**

-  Implement schema validation at persistence boundaries (DB layer)
-  Add schema validation to API request/response handlers
-  Implement event validation in engine event emission
-  Wire discipline adapter registry to load tuning from external config (YAML)
-  Add performance benchmarking harness (`perf/bench_single_sim.py`)
-  Implement state machine enforcement in engine (assert valid transitions)
-  Add failure-mode fault-injection tests (chaos testing)
-  Create migration guide for tuning from code → config

### **Phase 3: Scaling (Post-MVP)**

-  Containerize simulation engine
-  Implement message queue (RabbitMQ/Kafka) for work distribution
-  Add async persistence layer
-  Create worker autoscaling policy
-  Implement observability (metrics, logging, traces)
-  Benchmark against perf SLAs

---

## WORKING WITH SRS ARTIFACTS

### **1. Understanding Requirements**

Read `SRS/requirements.yaml` for all traced requirements:

```bash
cat SRS/requirements.yaml | grep -A 10 "id: R-SIM-001"
```

Each requirement has:
- **id**: Unique identifier (R-SYS-NNN)
- **title**: Human-readable title
- **description**: Detailed spec
- **acceptance_criteria**: Pass/fail definition
- **tests**: Test files that validate this requirement
- **owner**: Team responsible
- **priority**: high/medium/low
- **verification**: How acceptance is verified

### **2. Validating Domain Objects**

Use schema validator to check object conformance:

```python
from tools.schema_validator import SchemaValidator

validator = SchemaValidator()

# Validate a driver before persisting
driver = {"id": 1, "name": "Test", "status": "active", "attributes": {}}
valid, error = validator.validate_driver(driver)
if not valid:
    raise ValueError(f"Invalid driver: {error}")

# Validate batch of results
results = [...]
valid, errors = validator.validate_batch(results, "result")
if not valid:
    for error in errors:
        log.warning(f"Result validation issue: {error}")
```

### **3. Ensuring Reproducibility**

When modifying simulation logic:

1. **Before change**: Commit current state to ensure reproducibility test passes:
   ```bash
   python -m pytest tests/test_simulation_reproducibility.py::test_reproducibility_with_seed -v
   ```

2. **After change**: Re-run reproducibility tests to confirm determinism preserved:
   ```bash
   python -m pytest tests/test_simulation_reproducibility.py -v
   ```

3. **If test fails**: Audit your changes for non-deterministic code:
   - RNG seeding issues
   - Unordered collections (set iteration)
   - Threading / async code
   - Floating-point precision differences

### **4. Adding a New Event Type**

When engine needs to emit a new event:

1. **Create schema** in `SRS/event_schemas/my_event.schema.json`:
   ```json
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "title": "my_event",
     "type": "object",
     "required": ["event_id", "schema_version", "event_type", "race_id", "timestamp", "payload"],
     "properties": {
       ...
     }
   }
   ```

2. **Update event_contract.md** to document the new event

3. **Wire validation** in test:
   ```python
   from tools.schema_validator import SchemaValidator
   validator = SchemaValidator()
   valid, error = validator.validate_event(my_event_obj, "my_event")
   assert valid, error
   ```

4. **Update requirements.yaml** if changing R-EVT-001 scope

---

## CI/CD INTEGRATION

### **Triggering SRS Validation**

CI job (`.github/workflows/srs_validation.yml`) runs automatically on:
- `push` to `main`, `report-work`, `develop`
- `pull_request` to `main`, `develop`

**Validation steps**:
1. Verify all SRS markdown files exist
2. Verify all JSON schemas exist and are valid JSON
3. Run reproducibility tests (R-SIM-001)
4. Run integration tests (R-SIM-002, R-DISC-001, R-EVT-001, R-FAIL-001)
5. Generate coverage report
6. Run linting

### **Checking CI Status**

```bash
# View workflow runs
gh run list --workflow srs_validation.yml

# View latest run
gh run view --repo EoinFitzsimons/FinalProject [run-id]

# View logs
gh run view --repo EoinFitzsimons/FinalProject [run-id] --log
```

### **Local Pre-commit Checks**

Before committing:

```bash
# Run all SRS tests
cd Momentum/Python
python -m pytest tests/test_simulation_reproducibility.py tests/test_integration_srs.py -v

# If any fail, check logs and fix before committing
```

---

## TEST COVERAGE & EXPANSION

### **Current Coverage**

| Component | Test | Coverage |
|-----------|------|----------|
| Deterministic engine | `test_simulation_reproducibility.py` | High |
| Discipline adapters | `test_integration_srs.py::TestDisciplineAdapterContract` | Medium |
| Event schemas | `test_integration_srs.py::TestEventContract` | Medium |
| Domain objects | `test_integration_srs.py::TestSchemaValidation` | Medium |
| Failure handling | `test_integration_srs.py::TestFailureModes` | Medium |

### **Recommended Expansion**

1. **Performance benchmarking** (`perf/bench_single_sim.py`)
   - Latency tests for single simulation
   - Throughput tests for batch runs
   - Measure against SLAs in `SRS/perf_profiles.md`

2. **State machine tests** (add to `test_integration_srs.py`)
   - Verify valid state transitions
   - Test guards and timeout policies
   - Verify abort behavior

3. **Fault injection** (add to `test_integration_srs.py`)
   - Inject DB write failures
   - Verify partial persistence semantics
   - Test retry/fallback behavior

4. **Data pipeline tests**
   - Verify events flow through persistence layer
   - Validate aggregation and reporting

---

## DOCUMENTING CHANGES

When making changes that affect SRS:

### **Change Summary Format**

```
[TITLE]

[DESCRIPTION]

Affected Requirements: R-ABC-001, R-XYZ-002

Changes:
- Specific change 1
- Specific change 2

Test results: [pass/fail]

Breaking changes: [none / description]
```

### **Examples**

**Example 1: Discipline tuning change**
```
tuning(urban_street): increase overtake multiplier for more dynamic racing

ACCEPTED CHANGE:
- Modified OVERTAKE_INCIDENT_MULTIPLIER from 2.5 → 2.9 in UrbanStreetEngine._apply_tuning()
- Rationale: Players reported too few overtakes; increase multiplier to create more passing opportunities

Affected Requirements: None (tuning is within R-DISC-001 scope)

Test Results: Reproducibility tests pass (determinism verified with new tuning constant)

Breaking Changes: None (purely gameplay tuning)
```

**Example 2: Schema change**
```
schema(result): add 'dnf_reason' optional field

ACCEPTED CHANGE:
- Added optional 'dnf_reason' field to result.schema.json
- Rationale: Store Did-Not-Finish reason for analytics

Affected Requirements: R-DB-001 (Domain object schemas)

Test Results: Schema validation tests updated and passing

Breaking Changes: None (backward compatible; field is optional)
```

---

## TROUBLESHOOTING INTEGRATION

### **Problem: Reproducibility test fails**

**Diagnosis**:
```bash
cd Momentum/Python
python -m pytest mvp_tests/test_simulation_reproducibility.py::test_reproducibility_with_seed -v -s
```

**Common causes**:
1. RNG seed not propagated end-to-end
2. Unordered collection iteration
3. Floating-point math differences across runs

**Fix**:
- Audit engine's seed usage: `grep -r "seed" RaceLogic/`
- Ensure all RNG calls use the provided seed
- Sort dictionaries/lists before comparison

### **Problem: Integration test fails**

**Diagnosis**:
```bash
python -m pytest mvp_tests/test_integration_srs.py::TestDisciplineAdapterContract -v -s
```

**Fix depends on test**:
- **Adapter contract**: Verify `BaseDisciplineEngine` interface is implemented
- **Event validation**: Ensure event JSON matches schema
- **Schema validation**: Check schema file exists and is valid JSON

### **Problem: CI workflow fails**

**Diagnosis**:
1. Check GitHub Actions logs: repo → Actions → SRS Validation workflow
2. Look for specific step failure
3. Review logs for error message

**Common fixes**:
- Missing SRS artifact: add file and commit
- Invalid JSON schema: fix syntax error
- Test import error: check Python path and dependencies

---

## TEAM RESPONSIBILITIES

### **Requirements Analysis**
- **Owner**: Product / Requirements team
- **Tasks**: Review SRS, propose changes, validate business alignment
- **Artifact**: `SRS/requirements.yaml`

### **Design & Architecture**
- **Owner**: Systems architects / Tech leads
- **Tasks**: Review SRS specs, design implementation, propose scaling strategies
- **Artifacts**: `SRS/state_machine.md`, `SRS/perf_profiles.md`, architecture docs

### **Implementation**
- **Owner**: Software engineers
- **Tasks**: Code features per acceptance criteria, wire tests, update schema if needed
- **Artifacts**: `Momentum/Python/services/`, `Momentum/Python/RaceLogic/`

### **Testing & QA**
- **Owner**: QA engineers / Tech leads
- **Tasks**: Run tests, validate against acceptance criteria, file bugs
- **Artifacts**: `mvp_tests/`, coverage reports

### **DevOps / Platform**
- **Owner**: DevOps / SRE team
- **Tasks**: Wire CI/CD, monitor performance, scale infrastructure
- **Artifacts**: `.github/workflows/`, infrastructure-as-code

### **Product / Game Design**
- **Owner**: Product/design team
- **Tasks**: Define discipline tuning, run A/B experiments, iterate balance
- **Artifacts**: Discipline configs, experiment reports

---

## SUCCESS CRITERIA

SRS integration is successful when:

1.  All 8 requirements formalized with acceptance criteria
2.  Reproducibility tests pass consistently (R-SIM-001)
3.  Integration tests pass (R-SIM-002, R-DISC-001, R-EVT-001, R-FAIL-001)
4.  Schema validation wired to persistence layer
5.  CI/CD pipeline runs on every commit and PR
6.  Team follows change documentation format
7.  Coverage report shows >80% on critical paths
8.  Performance SLAs met (Phase 2)

---

## NEXT STEPS

1. **Week 1**: Review SRS with product/design teams; confirm alignment
2. **Week 2**: Implement Phase 2 enhancements (schema validation, external config)
3. **Week 3**: Performance benchmarking and optimization
4. **Week 4**: Scaling design review; prepare Phase 3 roadmap

---

## REFERENCE DOCUMENTS

- [SRS Requirements](SRS/requirements.yaml)
- [Determinism Spec](SRS/determinism.md)
- [Performance Profiles](SRS/perf_profiles.md)
- [State Machine](SRS/state_machine.md)
- [Failure Modes](SRS/failure_modes.md)
- [Event Contract](SRS/event_contract.md)
- [Developer Runbook](DEVELOPER_RUNBOOK.md)
- [Employment Analysis](EMPLOYMENT_ANALYSIS.md)

---

Generated by Copilot SRS Integration | April 2026
