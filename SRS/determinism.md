Determinism specification
=========================

Purpose
-------
Provide a formal definition and validation approach for the deterministic
behaviour requirement (R-SIM-001).

Definition
----------
- Input equality: Two runs are considered input-equal when the serialized
  `RaceContext` JSON and integer `seed` are byte-for-byte identical.
- Output equivalence: Two runs are equivalent when the serialized event list
  and final results JSON are byte-for-byte identical.

Tolerance rules
---------------
- Default: exact equality for all fields.
- If a numeric field is allowed tolerance, that must be documented per-field
  in `SRS/schemas/` with `tolerance` metadata.

Validation method
-----------------
1. Store canonical fixtures under `SRS/fixtures/`.
2. Create CI job that runs each fixture N=5 times with the same `seed` and
   compares serialized outputs.
3. On mismatch, the job records a canonical diff and fails the build.

Example invocation (developer):

```bash
# from repo root
python -m tools.run_sim --fixture SRS/fixtures/example_racecontext.json --seed 42 --out out1.json
python -m tools.run_sim --fixture SRS/fixtures/example_racecontext.json --seed 42 --out out2.json
cmp out1.json out2.json  # must be identical
```

Test mapping
------------
- Momentum/Python/mvp_tests/test_simulation_reproducibility.py (CI)
