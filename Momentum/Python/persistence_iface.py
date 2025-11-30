from dataclasses import dataclass
from typing import List, Optional, Protocol


@dataclass
class Driver:
    id: int
    name: str
    raw_speed: float  # 0-100


@dataclass
class Track:
    id: int
    name: str
    length_km: float


@dataclass
class RaceResult:
    driver_id: int
    position: int
    time_seconds: float


class PersistenceIface(Protocol):
    def ensure_schema(self) -> None:
        """Create tables if needed."""

    def seed_sample_data(self) -> None:
        """Insert a few drivers and a track for local testing."""

    def list_drivers(self) -> List[Driver]:
        raise NotImplementedError

    def get_driver(self, driver_id: int) -> Optional[Driver]:
        raise NotImplementedError

    def get_track(self, track_id: int) -> Optional[Track]:
        raise NotImplementedError

    def save_race_results(self, race_id: int, results: List[RaceResult]) -> None:
        raise NotImplementedError
