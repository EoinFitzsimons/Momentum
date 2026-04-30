# SRS ↔ Test Case Mapping

This document maps SRS requirement IDs to test files and test names, with pass/fail criteria for traceability and audits.

| SRS ID | Test File | Test Name | Pass Criteria |
|---|---|---|---|
| R-SIM-001 | Momentum/Python/tests/test_simulation_reproducibility.py | test_reproducibility_with_seed | Identical seed runs produce identical serialized results (hash equal) |
| R-SIM-001 | Momentum/Python/tests/test_simulation_reproducibility.py | test_determinism_across_multiple_runs | Multiple runs with same seed produce same output; sampled seeds produce multiple distinct outputs |
| R-SIM-002 | Momentum/Python/tests/test_integration_srs.py | TestRealtimeModeAndStreaming::test_event_callback_is_invoked | Event callback is wired and invoked during simulation (list populated) |
| R-DISC-001 | Momentum/Python/tests/test_integration_srs.py | TestDisciplineAdapterContract::test_adapter_instantiation_with_seed | Adapter instantiates with seed and exposes required methods |
| R-DISC-001 | Momentum/Python/tests/test_integration_srs.py | TestDisciplineAdapterContract::test_adapter_get_attribute_weights | Weights dict returned with floats in 0..1 range |
| R-EVT-001 | Momentum/Python/tests/test_integration_srs.py | TestEventContract::test_event_schema_load | Event schemas load from SRS/event_schemas/ |
| R-EVT-001 | Momentum/Python/tests/test_event_schema_emission.py | test_emitted_events_validate_against_schema | Events emitted during a short realtime run validate against corresponding JSON schemas |
| R-FAIL-001 | Momentum/Python/tests/test_integration_srs.py | TestFailureModes::test_missing_drivers_raises_error | simulate_race raises ValueError for missing drivers |
| R-DB-001 | Momentum/Python/tests/test_integration_srs.py | TestSchemaValidation::* | Domain objects validate against JSON schemas when schemas are present |
| R-DISC-EDGE-001 | Momentum/Python/tests/test_discipline_edge_cases.py | test_discipline_extreme_attributes_and_weather | Lap times remain finite, non-negative, and within expected numeric bounds under extreme attributes & weather |
| R-HYP-001 | Momentum/Python/tests/test_property_based_randomness.py | test_base_performance_property | `calculate_base_performance` returns value in [0.0, 1.0] for arbitrarily generated driver attributes (Hypothesis)

Notes:
- If JSON schemas are absent, schema validation tests will skip with informative messages.
- Edge-case tests focus on numeric stability (no NaN/inf, reasonable bounds) and will report specific failing inputs for debugging.
