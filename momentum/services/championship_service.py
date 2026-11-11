"""
Championship Service - Business Logic for Championship Management

Provides comprehensive championship management including:
- Points system calculations (discipline-specific)
- Standings recalculation with tie-breaking
- Season rollover automation
- Championship lifecycle management
- Event scheduling and validation

Points Systems:
- SINGLE_SEATER: Pinnacle open-wheel format (25, 18, 15, 12, 10, 8, 6, 4, 2, 1)
- ENDURANCE: Long-distance format (25, 20, 16, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)
- PRODUCTION_TOURING: Production car racing (32, 28, 25, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 1)
- URBAN_STREET: Street circuit drifting (28, 23, 19, 16, 13, 11, 9, 7, 5, 3, 2, 1)
- DRAG_ACCELERATION: Straight-line acceleration racing (20, 17, 14, 11, 8, 5, 2, 1)
- SPRINT_RALLYCROSS: Mixed-surface sprint series (30, 25, 22, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1)
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from momentum.database.database_manager import DatabaseManager
from momentum.database.models import Championship, Race, RaceResult
from momentum.services.track_surface_service import TrackSurfaceService


# Points systems by discipline
POINTS_SYSTEMS = {
    "SINGLE_SEATER": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],  # Pinnacle open-wheel
    "ENDURANCE": [
        25,
        20,
        16,
        13,
        11,
        10,
        9,
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1,
    ],  # Long-distance racing
    "PRODUCTION_TOURING": [
        32,
        28,
        25,
        22,
        20,
        18,
        16,
        14,
        12,
        10,
        8,
        6,
        4,
        2,
        1,
    ],  # Production car racing
    "URBAN_STREET": [28, 23, 19, 16, 13, 11, 9, 7, 5, 3, 2, 1],  # Drifting-focused
    "DRAG_ACCELERATION": [20, 17, 14, 11, 8, 5, 2, 1],  # Straight-line acceleration
    "SPRINT_RALLYCROSS": [
        30,
        25,
        22,
        19,
        17,
        15,
        13,
        11,
        9,
        7,
        5,
        3,
        1,
    ],  # Mixed-surface sprint
}


@dataclass
class StandingEntry:
    """Championship standing entry for a driver"""

    driver_id: int
    driver_name: str
    team_id: int
    team_name: str
    total_points: int
    wins: int
    podiums: int
    races_started: int
    dnf_count: int
    fastest_laps: int
    position: int = 0  # Set after sorting


class ChampionshipService:
    """
    Championship Service - Business Logic Layer

    Handles all championship-related business logic including points calculations,
    standings management, season rollover, and event scheduling.
    """

    def __init__(self, db_manager: DatabaseManager):
        """Initialise with database manager"""
        self.db = db_manager

    @staticmethod
    def default_laps_for_discipline(discipline: str) -> int:
        """Return default race laps for each discipline."""
        key = str(discipline or "").upper()
        if key == "ENDURANCE":
            return 24
        if key == "SPRINT_RALLYCROSS":
            return 6
        if key == "DRAG_ACCELERATION":
            return 3
        return 3

    def calculate_points(
        self, position: int, discipline: str, fastest_lap: bool = False
    ) -> int:
        """
        Calculate points for a finishing position

        Args:
            position: Finishing position (1-indexed)
            discipline: Racing discipline
            fastest_lap: Whether driver achieved fastest lap

        Returns:
            Points awarded
        """
        points_table = POINTS_SYSTEMS.get(discipline, POINTS_SYSTEMS["SINGLE_SEATER"])

        # Get base points for position
        if position <= 0 or position > len(points_table):
            base_points = 0
        else:
            base_points = points_table[position - 1]

        # Add fastest lap bonus (selected disciplines - only if finished in top 10)
        fastest_lap_bonus = 0
        if (
            fastest_lap
            and position <= 10
            and discipline in ["SINGLE_SEATER", "URBAN_STREET"]
        ):
            fastest_lap_bonus = 1

        return base_points + fastest_lap_bonus

    def recalculate_standings(
        self, championship_id: int, season: int
    ) -> List[StandingEntry]:
        """
        Recalculate championship standings with tie-breaking

        Tie-breaking rules:
        1. Total wins
        2. Total podiums
        3. Fastest laps
        4. Races started (consistency)

        Args:
            championship_id: Championship ID
            season: Season number

        Returns:
            List of standings entries, ordered by position
        """
        # Get championship to determine discipline
        championship = self.db.get_championship(championship_id)
        if not championship:
            return []

        # Get all races for this championship and season
        races = self._get_championship_races(championship_id, season)

        if not races:
            return []

        driver_stats = self._aggregate_driver_stats(races)
        standings = self._build_standing_entries(driver_stats)
        return self._rank_standings(standings)

    def _aggregate_driver_stats(self, races: List[Race]) -> Dict[int, Dict[str, Any]]:
        """Aggregate per-driver stats across completed races."""
        driver_stats: Dict[int, Dict[str, Any]] = {}

        for race in races:
            if race.status != "completed":
                continue
            results = self.db.get_race_results(race.id)
            for result in results:
                stats = self._ensure_driver_stats(
                    driver_stats, result.driver_id, result.team_id
                )
                self._accumulate_result_stats(stats, result)

        return driver_stats

    def _ensure_driver_stats(
        self,
        driver_stats: Dict[int, Dict[str, Any]],
        driver_id: int,
        team_id: Optional[int],
    ) -> Dict[str, Any]:
        """Initialise driver stats entry when missing and return it."""
        if driver_id not in driver_stats:
            driver_stats[driver_id] = {
                "driver_id": driver_id,
                "team_id": team_id,
                "total_points": 0,
                "wins": 0,
                "podiums": 0,
                "races_started": 0,
                "dnf_count": 0,
                "fastest_laps": 0,
            }
        return driver_stats[driver_id]

    def _accumulate_result_stats(
        self, stats: Dict[str, Any], result: RaceResult
    ) -> None:
        """Update running driver stats from one race result row."""
        stats["races_started"] += 1

        if result.dnf_reason is not None:
            stats["dnf_count"] += 1
            return

        stats["total_points"] += result.points
        if result.position == 1:
            stats["wins"] += 1
        if result.position <= 3:
            stats["podiums"] += 1
        if result.fastest_lap:
            stats["fastest_laps"] += 1

    def _build_standing_entries(
        self, driver_stats: Dict[int, Dict[str, Any]]
    ) -> List[StandingEntry]:
        """Convert aggregated driver stats into standings entries."""
        standings: List[StandingEntry] = []

        for driver_id, stats in driver_stats.items():
            driver = self.db.get_driver(driver_id)
            team = self.db.get_team(stats["team_id"]) if stats["team_id"] else None

            standings.append(
                StandingEntry(
                    driver_id=driver_id,
                    driver_name=driver.name if driver else f"Driver {driver_id}",
                    team_id=stats["team_id"],
                    team_name=team.name if team else f"Team {stats['team_id']}",
                    total_points=stats["total_points"],
                    wins=stats["wins"],
                    podiums=stats["podiums"],
                    races_started=stats["races_started"],
                    dnf_count=stats["dnf_count"],
                    fastest_laps=stats["fastest_laps"],
                )
            )

        return standings

    def _rank_standings(self, standings: List[StandingEntry]) -> List[StandingEntry]:
        """Sort standings and assign position values."""
        standings.sort(
            key=lambda x: (
                -x.total_points,
                -x.wins,
                -x.podiums,
                -x.fastest_laps,
                -x.races_started,
            )
        )

        for position, entry in enumerate(standings, start=1):
            entry.position = position

        return standings

    def create_championship_season(
        self, championship: Championship, tracks: List[int], start_date: datetime
    ) -> Tuple[int, List[int]]:
        """
        Create a new championship season with race calendar

        Assigns discipline-appropriate surfaces to all tracks in the championship.

        Args:
            championship: Championship object
            tracks: List of track IDs for the season
            start_date: Season start date

        Returns:
            Tuple of (championship_id, list of race_ids)
        """
        # Create championship
        champ_id = self.db.create_championship(championship)

        if not champ_id:
            raise ValueError("Failed to create championship")

        # Create race calendar with surface assignment
        race_ids = []
        current_date = start_date

        for round_num, track_id in enumerate(tracks, start=1):
            # Get track and assign surface for this discipline
            track = self.db.get_track(track_id)
            if track:
                track = TrackSurfaceService.assign_surface_to_track(
                    track, championship.discipline
                )
                # Update track with assigned surface
                self.db.update_track_surface(track.id, track.surface)

            race = Race(
                id=0,  # Will be assigned by database
                championship_id=champ_id,
                track_id=track_id,
                season=championship.current_season,
                round_number=round_num,
                race_date=current_date.strftime("%Y-%m-%d"),
                weather_conditions="clear",
                laps=self.default_laps_for_discipline(championship.discipline),
                status="scheduled",
            )

            race_id = self.db.create_race(race)
            if race_id:
                race_ids.append(race_id)

            # Space races 2 weeks apart
            current_date += timedelta(days=14)

        return champ_id, race_ids

    def validate_race_event(
        self, championship_id: int, track_id: int, race_date: str, season: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a new race event for conflicts

        Args:
            championship_id: Championship ID
            track_id: Track ID
            race_date: Proposed race date (YYYY-MM-DD)
            season: Season number

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check track exists
        track = self.db.get_track(track_id)
        if not track:
            return False, f"Track {track_id} not found"

        # Check for date conflicts in same championship
        existing_races = self._get_championship_races(championship_id, season)

        for race in existing_races:
            if race.race_date == race_date:
                return False, f"Date conflict: Race already scheduled on {race_date}"

        # Check if track is already used on this date (across all championships)
        # This is a simplification - real validation would check time windows

        return True, None

    def update_race_lifecycle_status(
        self, race_id: int, new_status: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Update race status with lifecycle validation

        Valid transitions:
        - scheduled -> in-progress
        - in-progress -> completed
        - scheduled -> cancelled

        Args:
            race_id: Race ID
            new_status: New status value

        Returns:
            Tuple of (success, error_message)
        """
        valid_statuses = ["scheduled", "in-progress", "completed", "cancelled"]

        if new_status not in valid_statuses:
            return False, f"Invalid status: {new_status}"

        race = self.db.get_race(race_id)
        if not race:
            return False, f"Race {race_id} not found"

        current_status = race.status

        # Define valid transitions
        valid_transitions = {
            "scheduled": ["in-progress", "cancelled"],
            "in-progress": ["completed"],
            "completed": [],  # No transitions from completed
            "cancelled": [],  # No transitions from cancelled
        }

        if new_status not in valid_transitions.get(current_status, []):
            return False, f"Invalid transition: {current_status} -> {new_status}"

        # Update status
        self.db.update_race_status(race_id, new_status)

        return True, None

    def get_championship_calendar(
        self, championship_id: int, season: int
    ) -> List[Dict[str, Any]]:
        """
        Get full championship calendar with race details

        Args:
            championship_id: Championship ID
            season: Season number

        Returns:
            List of race details with track information
        """
        races = self._get_championship_races(championship_id, season)

        calendar = []
        for race in races:
            track = self.db.get_track(race.track_id)

            calendar.append(
                {
                    "race_id": race.id,
                    "round_number": race.round_number,
                    "race_date": race.race_date,
                    "track_id": race.track_id,
                    "track_name": track.name if track else "Unknown",
                    "track_country": track.country if track else "Unknown",
                    "status": race.status,
                    "weather_conditions": race.weather_conditions,
                    "laps": race.laps,
                }
            )

        return calendar

    def _get_championship_races(self, championship_id: int, season: int) -> List[Race]:
        """Get all races for a championship season"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM races
                WHERE championship_id = ? AND season = ?
                ORDER BY round_number
            """,
                (championship_id, season),
            ).fetchall()

            races = []
            for row in rows:
                row_dict = {k: v for k, v in dict(row).items() if k != "created_at"}
                # Provide default for race_duration_minutes if missing
                if "race_duration_minutes" not in row_dict:
                    row_dict["race_duration_minutes"] = 90
                races.append(Race(**row_dict))
            return races
