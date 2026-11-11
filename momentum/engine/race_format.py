"""How a race day is organised in each discipline.

A single-seater grand prix, a rallycross final of ten cars reached through
heats, a sixteen-car drag bracket and a three-driver endurance entry are not
the same event, so grid size, cars per team and drivers per car live here
rather than in one global number. Each discipline engine carries its
``race_format`` as a class attribute and overrides it by inheritance;
``race_format_for()`` is how the rest of the game looks it up.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from momentum.services.tier_service import TIERS, TOP_TIER, normalise_tier

GRAND_PRIX = "grand_prix"  # one race, everyone on the grid
HEATS_AND_FINAL = "heats_and_final"  # heats and semi-finals decide who reaches the final
KNOCKOUT_BRACKET = "knockout_bracket"  # paired eliminations down to a winner
BATTLES = "battles"  # judged head-to-head runs (placeholder for urban street)


@dataclass(frozen=True)
class RaceFormat:
    """The shape of a race day for one discipline."""

    name: str
    race_day: str = GRAND_PRIX
    cars_per_team: int = 2
    drivers_per_car: int = 1
    reserve_drivers: int = 0
    team_based: bool = True
    max_entries: int = 40
    # Smaller fields in the top league, where regulations cap the entry list.
    max_entries_by_tier: Dict[str, int] = field(default_factory=dict)
    # Track-length cap: roughly one car per this many metres of lap.
    metres_per_car: float = 100.0
    min_entries: int = 6
    # Leagues whose cars carry a drag-reduction system. A circuit records where
    # its DRS zones are; whether the cars may open the wing is a rule of the tier.
    drs_tiers: Tuple[str, ...] = ()

    @property
    def driver_slots(self) -> int:
        """Drivers a team contracts for this format."""
        return self.cars_per_team * self.drivers_per_car + self.reserve_drivers

    def allows_drs(self, tier: Optional[str]) -> bool:
        return normalise_tier(tier) in self.drs_tiers

    def entry_cap(self, tier: Optional[str] = None) -> int:
        if tier is None:
            return self.max_entries
        return int(self.max_entries_by_tier.get(normalise_tier(tier), self.max_entries))

    def grid_size(
        self,
        track_length_m: Optional[float] = None,
        tier: Optional[str] = None,
        available: Optional[int] = None,
    ) -> int:
        """Cars that start the race, given the league and the track."""
        cap = self.entry_cap(tier)
        if track_length_m and track_length_m > 0:
            cap = min(cap, int(track_length_m // self.metres_per_car))
        cap = max(self.min_entries, cap)
        if available is not None:
            cap = min(cap, int(available))
        return max(0, cap)


SINGLE_SEATER_FORMAT = RaceFormat(
    name="Single-seater grand prix",
    cars_per_team=2,
    max_entries=40,
    max_entries_by_tier={TOP_TIER: 30},
    metres_per_car=110.0,
    drs_tiers=TIERS,
)
PRODUCTION_TOURING_FORMAT = RaceFormat(
    name="Touring car race",
    cars_per_team=2,
    max_entries=40,
    metres_per_car=90.0,
)
ENDURANCE_FORMAT = RaceFormat(
    name="Endurance race",
    cars_per_team=1,
    drivers_per_car=3,
    reserve_drivers=1,
    max_entries=20,
    metres_per_car=250.0,
    # Only the purpose-built top-tier prototypes; the GT-style lower tiers are
    # homologated road cars without it.
    drs_tiers=(TOP_TIER,),
)
SPRINT_RALLYCROSS_FORMAT = RaceFormat(
    name="Rallycross heats and final",
    race_day=HEATS_AND_FINAL,
    cars_per_team=2,
    team_based=False,
    max_entries=10,
    metres_per_car=120.0,
    min_entries=4,
)
DRAG_ACCELERATION_FORMAT = RaceFormat(
    name="Drag elimination bracket",
    race_day=KNOCKOUT_BRACKET,
    cars_per_team=2,
    team_based=False,
    max_entries=16,
    metres_per_car=1.0,
    min_entries=4,
)
URBAN_STREET_FORMAT = RaceFormat(
    name="Street battles",
    race_day=BATTLES,
    cars_per_team=2,
    team_based=False,
    max_entries=16,
    metres_per_car=80.0,
    min_entries=4,
)

DISCIPLINE_FORMATS: Dict[str, RaceFormat] = {
    "SINGLE_SEATER": SINGLE_SEATER_FORMAT,
    "PRODUCTION_TOURING": PRODUCTION_TOURING_FORMAT,
    "URBAN_STREET": URBAN_STREET_FORMAT,
    "DRAG_ACCELERATION": DRAG_ACCELERATION_FORMAT,
    "SPRINT_RALLYCROSS": SPRINT_RALLYCROSS_FORMAT,
    "ENDURANCE": ENDURANCE_FORMAT,
}


def normalise_discipline(value) -> str:
    raw = getattr(value, "value", value)
    return str(raw or "").strip().upper().replace(" ", "_").replace("-", "_")


def race_format_for(discipline) -> RaceFormat:
    """The format the discipline's engine declares; the table above otherwise."""
    key = normalise_discipline(discipline)
    try:
        from momentum.services.race_engine_factory import discipline_engine_class

        engine_cls = discipline_engine_class(key)
    except Exception:
        engine_cls = None
    declared = getattr(engine_cls, "race_format", None) if engine_cls else None
    if isinstance(declared, RaceFormat):
        return declared
    return DISCIPLINE_FORMATS.get(key, SINGLE_SEATER_FORMAT)


def driver_slots_for(discipline) -> int:
    return race_format_for(discipline).driver_slots


__all__ = [
    "BATTLES",
    "DISCIPLINE_FORMATS",
    "GRAND_PRIX",
    "HEATS_AND_FINAL",
    "KNOCKOUT_BRACKET",
    "RaceFormat",
    "driver_slots_for",
    "normalise_discipline",
    "race_format_for",
]
