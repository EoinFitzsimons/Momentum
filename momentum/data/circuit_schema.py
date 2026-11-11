"""Typed schema for the circuit source data under ``momentum/data/circuits/``.

Every circuit shares ``CircuitBase``. Closed circuits add the lap geometry in
``LapCircuit``; each discipline then adds only what is specific to it, and drag
strips, which have no lap, extend the base directly. A record is checked
against exactly its own discipline's model (selected by
``primary_discipline``) and that discipline's profile of realistic ranges, so
a contradictory or misplaced figure is an error rather than something the
game has to work around. Figures that follow from others, such as the total
turn count, are derived and never stored.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, ClassVar, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError, model_validator

from momentum.data.circuit_profiles import PROFILES, DisciplineProfile

CIRCUITS_DIR = Path(__file__).resolve().parent / "circuits"

Climate = Literal["temperate", "mediterranean", "continental", "desert", "tropical", "alpine"]
Grade = Literal["Diamond", "Platinum", "Gold", "Silver", "Bronze", "Approved"]

QUARTER_MILE_M = 402.34


class CircuitError(ValueError):
    """Raised when the circuit source data breaks its schema or profile."""


class CircuitBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    discipline_key: ClassVar[str] = ""

    circuit_id: int = Field(gt=0)
    name: str = Field(min_length=1)
    country: str = Field(min_length=1)
    region: str = Field(min_length=1)
    circuit_type: Literal["permanent", "road_course", "street", "mixed"]
    ima_grade: Grade

    elevation_change_m: float = Field(ge=0)
    max_gradient_percent: float = Field(ge=0)
    min_gradient_percent: float = Field(le=0)
    track_width_avg_m: float = Field(gt=0)
    track_width_min_m: float = Field(gt=0)
    track_width_max_m: float = Field(gt=0)
    avg_speed_kmh: float = Field(gt=0)
    top_speed_kmh: float = Field(gt=0)

    climate: Climate
    avg_temp_summer_c: float
    avg_temp_winter_c: float
    rainfall_mm_annual: int = Field(ge=0)
    altitude_m: int

    pit_boxes: int = Field(gt=0)
    pit_lane_length_m: float = Field(gt=0)
    pit_speed_limit_kmh: int = Field(gt=0)
    paddock_capacity_teams: int = Field(gt=0)
    grandstand_capacity: int = Field(ge=0)
    safety_car_probability: float = Field(ge=0, le=1)
    night_racing_capable: bool
    wet_weather_racing: bool
    is_active: bool
    debut_year: int
    last_used_year: Optional[int] = None

    @property
    def profile(self) -> DisciplineProfile:
        return PROFILES[self.discipline_key]

    @property
    def length_m(self) -> float:
        raise NotImplementedError

    @model_validator(mode="after")
    def _consistent(self) -> "CircuitBase":
        problems = self._problems()
        if problems:
            raise ValueError("; ".join(problems))
        return self

    def _problems(self) -> List[str]:
        p: List[str] = []
        if not self.track_width_min_m <= self.track_width_avg_m <= self.track_width_max_m:
            p.append("track width must run min <= avg <= max")
        if self.avg_speed_kmh >= self.top_speed_kmh:
            p.append("average speed must be below top speed")
        if self.avg_temp_winter_c > self.avg_temp_summer_c:
            p.append("winter temperature above summer temperature")
        if self.last_used_year is not None and self.last_used_year < self.debut_year:
            p.append("last used before its debut")
        if self.pit_lane_length_m >= self.length_m:
            p.append("pit lane is not shorter than the circuit")
        for field, (lo, hi) in self.profile.ranges.items():
            value = getattr(self, field)
            if not lo <= value <= hi:
                p.append(f"{field} {value} outside {self.discipline_key} range {lo}-{hi}")
        return p

    def to_record(self) -> Dict[str, Any]:
        """Flat record for the seed importer, with the derived figures filled in."""
        record = self.model_dump()
        record["primary_discipline"] = self.discipline_key
        record["length_km"] = round(self.length_m / 1000.0, 3)
        return record


class LapCircuit(CircuitBase):
    length_km: float = Field(gt=0)
    left_turns: int = Field(ge=0)
    right_turns: int = Field(ge=0)
    longest_straight_m: float = Field(gt=0)
    shortest_straight_m: float = Field(gt=0)
    tightest_corner_radius_m: float = Field(gt=0)

    @property
    def length_m(self) -> float:
        return self.length_km * 1000.0

    @property
    def turns(self) -> int:
        return self.left_turns + self.right_turns

    def _problems(self) -> List[str]:
        p = super()._problems()
        if self.turns < 3 and not (self.turns == 2 and self.left_turns != self.right_turns):
            p.append("a lap needs two corners the same way, or three or more")
        if self.shortest_straight_m > self.longest_straight_m:
            p.append("shortest straight longer than the longest")
        share = self.longest_straight_m / self.length_m
        if share > self.profile.max_straight_share:
            p.append(
                f"longest straight is {share:.0%} of the lap, above the "
                f"{self.discipline_key} limit of {self.profile.max_straight_share:.0%}"
            )
        if not self.profile.turns[0] <= self.turns <= self.profile.turns[1]:
            p.append(f"{self.turns} turns outside {self.discipline_key} range {self.profile.turns}")
        return p

    def to_record(self) -> Dict[str, Any]:
        record = super().to_record()
        record["turns"] = self.turns
        record.setdefault("drs_zones", 0)  # only the disciplines with DRS store zones
        return record


class _Paved(BaseModel):
    surface: Literal["asphalt", "concrete"]


class _Drs(BaseModel):
    drs_zones: int = Field(ge=0)


class SingleSeaterCircuit(LapCircuit, _Paved, _Drs):
    discipline_key: ClassVar[str] = "SINGLE_SEATER"
    primary_discipline: Literal["SINGLE_SEATER"]


class EnduranceCircuit(LapCircuit, _Paved, _Drs):
    discipline_key: ClassVar[str] = "ENDURANCE"
    primary_discipline: Literal["ENDURANCE"]


class UrbanStreetCircuit(LapCircuit, _Paved):
    discipline_key: ClassVar[str] = "URBAN_STREET"
    primary_discipline: Literal["URBAN_STREET"]


class TouringCircuit(LapCircuit, _Paved):
    discipline_key: ClassVar[str] = "PRODUCTION_TOURING"
    primary_discipline: Literal["PRODUCTION_TOURING"]


class JokerRoute(BaseModel):
    """The alternative route each driver must take once per race."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    extra_length_m: float = Field(gt=0)
    branch_at_fraction: float = Field(gt=0, lt=1)


class RallycrossCircuit(LapCircuit):
    discipline_key: ClassVar[str] = "SPRINT_RALLYCROSS"
    primary_discipline: Literal["SPRINT_RALLYCROSS"]
    surfaces: Dict[Literal["asphalt", "gravel", "dirt"], float]
    joker: JokerRoute

    def _problems(self) -> List[str]:
        p = super()._problems()
        if abs(sum(self.surfaces.values()) - 1.0) > 1e-6:
            p.append("surface shares must add up to 1")
        if len(self.surfaces) < 2 or min(self.surfaces.values()) <= 0:
            p.append("rallycross runs on at least two surfaces")
        if self.joker.extra_length_m > 0.25 * self.length_m:
            p.append("joker route adds more than a quarter of the lap")
        return p

    def to_record(self) -> Dict[str, Any]:
        record = super().to_record()
        record["surface"] = "mixed"
        record["joker_enabled"] = True
        return record


class DragStrip(CircuitBase, _Paved):
    discipline_key: ClassVar[str] = "DRAG_ACCELERATION"
    primary_discipline: Literal["DRAG_ACCELERATION"]
    race_distance_m: Literal[402.34] = QUARTER_MILE_M
    shutdown_m: float = Field(gt=0)

    @property
    def length_m(self) -> float:
        return self.race_distance_m + self.shutdown_m

    def to_record(self) -> Dict[str, Any]:
        record = super().to_record()
        record.update(
            turns=0, left_turns=0, right_turns=0, is_point_to_point=True,
            longest_straight_m=self.length_m, tightest_corner_radius_m=0.0, drs_zones=0,
        )
        return record


_MODEL_TYPES = (
    SingleSeaterCircuit,
    EnduranceCircuit,
    UrbanStreetCircuit,
    TouringCircuit,
    RallycrossCircuit,
    DragStrip,
)
Circuit = Annotated[Union[_MODEL_TYPES], Field(discriminator="primary_discipline")]
MODELS = {m.discipline_key: m for m in _MODEL_TYPES}
_ADAPTER: TypeAdapter = TypeAdapter(Circuit)

FILES = {
    "SINGLE_SEATER": "single_seater.json",
    "ENDURANCE": "endurance.json",
    "URBAN_STREET": "urban_street.json",
    "PRODUCTION_TOURING": "production_touring.json",
    "SPRINT_RALLYCROSS": "sprint_rallycross.json",
    "DRAG_ACCELERATION": "drag_acceleration.json",
}


def parse_circuit(raw: Dict[str, Any]) -> CircuitBase:
    return _ADAPTER.validate_python(raw)


def validate_records(records: List[Tuple[str, Dict[str, Any]]]) -> Tuple[List[CircuitBase], List[str]]:
    """Validate (source, record) pairs; return the circuits and every problem found."""
    circuits: List[CircuitBase] = []
    errors: List[str] = []
    for source, raw in records:
        label = f"{source}: {raw.get('name', '?')}"
        try:
            circuits.append(parse_circuit(raw))
        except ValidationError as exc:
            for err in exc.errors():
                where = ".".join(str(x) for x in err["loc"][1:]) or "record"
                errors.append(f"{label}: {where}: {err['msg']}")
    seen: Dict[Any, str] = {}
    for c in circuits:
        for key in (("id", c.circuit_id), ("name", c.name.casefold())):
            if key in seen:
                errors.append(f"duplicate circuit {key[0]} {key[1]!r} ({seen[key]} and {c.name})")
            seen[key] = c.name
    return circuits, errors


def read_sources(directory: Path = CIRCUITS_DIR) -> List[Tuple[str, Dict[str, Any]]]:
    records: List[Tuple[str, Dict[str, Any]]] = []
    for discipline, filename in FILES.items():
        path = directory / filename
        for raw in json.loads(path.read_text(encoding="utf-8")):
            if raw.get("primary_discipline") != discipline:
                raise CircuitError(f"{filename}: {raw.get('name', '?')} is not a {discipline} circuit")
            records.append((filename, raw))
    return records


def load_circuits(directory: Path = CIRCUITS_DIR) -> List[CircuitBase]:
    """Load and validate every shipped circuit, refusing the set if any is wrong."""
    circuits, errors = validate_records(read_sources(directory))
    if errors:
        raise CircuitError(
            f"{len(errors)} problem(s) in the circuit data:\n  " + "\n  ".join(errors)
        )
    return sorted(circuits, key=lambda c: c.circuit_id)


def json_schema() -> Dict[str, Any]:
    return _ADAPTER.json_schema()
