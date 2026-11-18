"""Settle a race the player has left the race window for.

Shared by the career and championship paths so both close a round the same
way: a race with results is ``completed``; a race abandoned mid-run (no
results) returns to ``scheduled`` so it is raced again rather than skipped.
"""

from __future__ import annotations

from typing import Callable

COMPLETED = "completed"
REOPENED = "reopened"
UNCHANGED = "unchanged"


def settle_race(
    status: str | None,
    has_results: bool,
    mark_completed: Callable[[], None],
    mark_scheduled: Callable[[], None],
) -> str:
    """Return ``completed``, ``reopened`` or ``unchanged`` after applying the change."""
    current = str(status or "")
    if not current or current == "completed":
        return UNCHANGED
    if has_results:
        mark_completed()
        return COMPLETED
    if current == "scheduled":
        return UNCHANGED
    mark_scheduled()
    return REOPENED


def settle_championship_race(db, championship_service, race_id: int) -> str:
    """Settle a championship round through the race lifecycle service."""
    if db is None or int(race_id or 0) <= 0:
        return UNCHANGED
    race = db.get_race(int(race_id))
    if race is None:
        return UNCHANGED
    has_results = bool(db.get_race_results(int(race_id)))

    def _transition(new_status: str) -> None:
        ok, error = championship_service.update_race_lifecycle_status(
            int(race_id), new_status
        )
        if not ok:
            raise RuntimeError(error or f"could not mark race {race_id} {new_status}")

    return settle_race(
        getattr(race, "status", None),
        has_results,
        lambda: _transition("completed"),
        lambda: _transition("scheduled"),
    )
