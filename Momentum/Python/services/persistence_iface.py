from typing import List, Optional, Protocol

# Use the canonical DB models as types so the persistence implementation
# returns the full driver/track dataclasses defined in `database/models.py`.
from database.models import Driver as DBDriver
from database.models import Track as DBTrack
from database.models import RaceResult as DBRaceResult


class PersistenceIface(Protocol):
    def ensure_schema(self) -> None:
        """Create tables if needed."""

    def seed_sample_data(self) -> None:
        """Insert a few drivers and a track for local testing."""

    def list_drivers(self) -> List[DBDriver]:
        raise NotImplementedError

    def get_driver(self, driver_id: int) -> Optional[DBDriver]:
        raise NotImplementedError

    def get_track(self, track_id: int) -> Optional[DBTrack]:
        raise NotImplementedError

    def save_race_results(self, race_id: int,
                          results: List[DBRaceResult]) -> None:
        raise NotImplementedError
