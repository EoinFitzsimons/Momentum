"""Career race-result persistence helpers.

These helpers move career-mode inserts out of the GUI layer and into the
service layer so UI code does not write to the database directly.
"""

from __future__ import annotations

from typing import Any, Optional

from momentum.services.race_settlement import UNCHANGED, settle_race


def persist_career_race_result(
    db: Any,
    player_id: str,
    career_race_id: int,
    driver_id: int,
    team_id: int,
    position: int,
    points: int,
    fastest_lap: bool,
    dnf_reason: Optional[str],
    grid_position: Optional[int],
) -> None:
    """Persist one career race-result row through the service layer."""
    if db is None:
        return

    with db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO career_race_results
                (player_id, career_race_id, driver_id, team_id, position, points, fastest_lap, dnf_reason, grid_position)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(career_race_id, driver_id) DO UPDATE SET
                team_id = excluded.team_id,
                position = excluded.position,
                points = excluded.points,
                fastest_lap = excluded.fastest_lap,
                dnf_reason = excluded.dnf_reason,
                grid_position = excluded.grid_position
            """,
            (
                player_id,
                career_race_id,
                driver_id,
                team_id,
                position,
                points,
                1 if fastest_lap else 0,
                dnf_reason,
                grid_position,
            ),
        )


def complete_career_race(db: Any, career_race_id: int) -> bool:
    """Mark a career race ``completed`` once its result rows exist.

    This is the single place the GUI uses to close a race, so the prize and
    sponsor payout (which only pays races in ``completed`` status) and the
    season rollover both see the same lifecycle state. Returns True when the
    status changed.
    """
    if db is None:
        return False
    with db.get_connection() as conn:
        has_results = conn.execute(
            "SELECT 1 FROM career_race_results WHERE career_race_id = ? LIMIT 1",
            (int(career_race_id),),
        ).fetchone()
        if not has_results:
            return False
        cursor = conn.execute(
            "UPDATE career_races SET status = 'completed' "
            "WHERE id = ? AND status != 'completed'",
            (int(career_race_id),),
        )
        conn.commit()
        return cursor.rowcount > 0


def settle_career_race(db: Any, career_race_id: int) -> str:
    """Settle a career race the player has left the race window for.

    Returns ``"completed"`` when its results close it, ``"reopened"`` when the
    race was abandoned mid-run (no results) and goes back to ``scheduled`` so
    it is raced again rather than silently skipped, else ``"unchanged"``.
    """
    if db is None or int(career_race_id or 0) <= 0:
        return UNCHANGED
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT status FROM career_races WHERE id = ?", (int(career_race_id),)
        ).fetchone()
        if row is None:
            return UNCHANGED
        has_results = conn.execute(
            "SELECT 1 FROM career_race_results WHERE career_race_id = ? LIMIT 1",
            (int(career_race_id),),
        ).fetchone()

    def _reopen() -> None:
        with db.get_connection() as conn:
            conn.execute(
                "UPDATE career_races SET status = 'scheduled' WHERE id = ?",
                (int(career_race_id),),
            )
            conn.commit()

    return settle_race(
        str(row[0]),
        bool(has_results),
        lambda: complete_career_race(db, career_race_id),
        _reopen,
    )
