"""Career race-result persistence helpers.

These helpers move career-mode inserts out of the GUI layer and into the
service layer so UI code does not write to the database directly.
"""

from __future__ import annotations

from typing import Any, Optional


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
