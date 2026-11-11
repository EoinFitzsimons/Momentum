Race state machine
===================

States
- INITIALIZED: race context created, not yet started
- STARTING: pre-race setup (grid formation, checks)
- RUNNING: race in progress, lap progression
- PAUSED: temporary halt (external stop_event or pause)
- RESOLVING_INCIDENT: handling incident (penalties, retirements)
- COMPLETED: normal finish
- ABORTED: unexpected termination or unrecoverable error

Transitions (examples)
- INITIALIZED -> STARTING: on `start()` command and preflight ok
- STARTING -> RUNNING: on race clock start
- RUNNING -> RESOLVING_INCIDENT: on `incident` occurrence
- RESOLVING_INCIDENT -> RUNNING: when incident resolved or timeout
- RUNNING -> PAUSED: on `stop_event` signal (graceful pause)
- PAUSED -> RUNNING: on resume
- RUNNING -> COMPLETED: when all laps complete
- Any -> ABORTED: on unrecoverable runtime failure

Guards and policies
- Incident resolution has a configurable timeout (e.g., 10s simulated
  wall-time) after which mitigation policies apply (e.g., apply default
  penalty and resume).
- `stop_event` must allow the engine to persist last consistent snapshot.

Testing
- `Momentum/Python/tests/test_simulation_reproducibility.py` should feed events and
  assert the observed state sequence equals expected sequence.
