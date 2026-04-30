Failure modes and recovery policies
==================================

Failure classes
- ValidationError: malformed RaceContext or missing required fields.
- RuntimeError: unhandled exception in simulation loop.
- PersistenceError: failure writing to DB or storage.

Policies
- ValidationError: reject run, return explicit error with code and message,
  no side-effects.
- RuntimeError: mark race as `ABORTED`, persist partial results where
  possible, capture exception trace, and surface error to caller.
- PersistenceError: retry writes with exponential backoff; on sustained
  failure, fallback to durable local file writes and mark record for
  reconciliation.

Compensation and rollback
- There is no cross-system distributed transaction. Instead, define
  compensation actions for downstream systems (e.g., purge partial
  leaderboard entries and re-ingest after reconciliation).

Testing
- Add fault-injection tests under `Momentum/Python/tests/` to assert
  expected persisted state on injected failures.
