"""Central factory for race simulation engines.

The Momentum architecture routes all discipline-engine construction through
this module so callers never instantiate engines directly.
"""

from __future__ import annotations

import importlib
from typing import Any, Dict, Optional, Tuple, Type

from RaceLogic.base_race_engine import (
    BaseDisciplineEngine,
    RaceContext,
    RacingDiscipline,
)
from RaceLogic.realtime_race_engine import RealtimeRaceEngine


DiscRegistryEntry = Tuple[str, str, str]


CANONICAL_DISCIPLINE_REGISTRY: Dict[RacingDiscipline, DiscRegistryEntry] = {
    RacingDiscipline.SINGLE_SEATER: (
        "RaceLogic.disciplines.single_seater.single_seater_discipline",
        "SingleSeaterEngine",
        "realtime_wrapper",
    ),
    RacingDiscipline.PRODUCTION_TOURING: (
        "RaceLogic.disciplines.production_touring.production_touring_discipline",
        "ProductionTouringEngine",
        "realtime_wrapper",
    ),
    RacingDiscipline.URBAN_STREET: (
        "RaceLogic.disciplines.urban_street.urban_street_discipline",
        "UrbanStreetEngine",
        "realtime_wrapper",
    ),
    RacingDiscipline.DRAG_ACCELERATION: (
        "RaceLogic.disciplines.drag_acceleration.drag_acceleration_discipline",
        "DragAccelerationEngine",
        "isolated_engine",
    ),
    RacingDiscipline.SPRINT_RALLYCROSS: (
        "RaceLogic.disciplines.sprint_rallycross.sprint_rallycross_discipline",
        "SprintRallycrossEngine",
        "realtime_wrapper",
    ),
    RacingDiscipline.ENDURANCE: (
        "RaceLogic.disciplines.endurance.endurance_discipline",
        "EnduranceEngine",
        "realtime_wrapper",
    ),
}


def create_realtime_engine(
    seed: Optional[int] = None, db: Optional[Any] = None, debug_logging: bool = False
) -> RealtimeRaceEngine:
    """Build the shared realtime engine through the canonical factory."""
    engine = RealtimeRaceEngine(seed=seed)
    engine.debug_logging = bool(debug_logging)
    if db is not None:
        engine.db = db
    return engine


def _resolve_discipline_engine_class(
    context: RaceContext,
) -> Optional[Type[BaseDisciplineEngine]]:
    if not context or not getattr(context, "discipline", None):
        return None

    registry_entry = CANONICAL_DISCIPLINE_REGISTRY.get(context.discipline)
    if registry_entry is None:
        return None

    module_path, class_name, _ = registry_entry
    module = importlib.import_module(module_path)
    engine_class = getattr(module, class_name, None)
    if isinstance(engine_class, type) and issubclass(
        engine_class, BaseDisciplineEngine
    ):
        return engine_class
    return None


def create_discipline_engine(
    context: RaceContext, seed: Optional[int] = None
) -> Optional[BaseDisciplineEngine]:
    """Create the canonical engine adapter for a race context."""
    engine_class = _resolve_discipline_engine_class(context)
    if engine_class is None:
        return None
    return engine_class(seed=seed if seed is not None else 0)


def discipline_engine_class(discipline) -> Optional[Type[BaseDisciplineEngine]]:
    """Import and return the engine class registered for ``discipline``."""
    try:
        key = RacingDiscipline(str(getattr(discipline, "value", discipline)).upper())
    except ValueError:
        return None
    entry = CANONICAL_DISCIPLINE_REGISTRY.get(key)
    if not entry:
        return None
    module = importlib.import_module(entry[0])
    return getattr(module, entry[1], None)


def get_canonical_discipline_registry() -> Dict[RacingDiscipline, DiscRegistryEntry]:
    """Expose the canonical registry for validation and diagnostics."""
    return dict(CANONICAL_DISCIPLINE_REGISTRY)
