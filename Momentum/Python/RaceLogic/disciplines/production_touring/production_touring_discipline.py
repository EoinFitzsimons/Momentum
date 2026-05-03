"""
Production Touring discipline adapter.

Provides a dedicated adapter for production/touring racing, preserving the
abstraction contract while using the shared realtime simulation core.
"""

from typing import Any, Dict, List, Optional

from RaceLogic.base_race_engine import (
    BaseDisciplineEngine,
    RaceContext,
    RacingDiscipline,
)
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from database.models import Driver, Team
from services.race_engine_factory import create_realtime_engine


class ProductionTouringEngine(BaseDisciplineEngine):
    """Production/touring adapter with balanced pace and racecraft weighting."""

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed if seed is not None else 0)
        self.discipline = RacingDiscipline.PRODUCTION_TOURING

    def get_attribute_weights(self) -> Dict[str, float]:
        return {
            "consistency": 0.16,
            "racecraft": 0.14,
            "cornering_skill": 0.12,
            "braking_technique": 0.10,
            "overtaking": 0.08,
            "defensive_driving": 0.08,
            "tyre_management": 0.10,
            "fuel_management": 0.08,
            "raw_speed": 0.08,
            "concentration": 0.06,
        }

    def calculate_lap_time(
        self,
        driver: Driver,
        team: Team,
        context: RaceContext,
        lap_number: int,
        current_position: int,
    ) -> float:
        base_lap = float(getattr(context.track, "lap_time", 84.0) or 84.0)
        performance = self.calculate_base_performance(driver, team, context)
        perf_factor = 1.11 - (0.23 * performance)
        degradation = 1.0 + (max(1, lap_number) * 0.0008)
        traffic = 1.0 + (0.008 if current_position > 10 else 0.0)
        return base_lap * perf_factor * degradation * traffic

    def _apply_tuning(self, engine: RealtimeRaceEngine) -> None:
        engine.BASE_SPEED_MPS = 64.0
        engine.MAX_SPEED_MPS = 85.0
        engine.MIN_SPEED_MPS = 24.0
        engine.TYRE_DEGRADATION_RATE = 0.000013
        engine.FUEL_BURN_RATE = 0.000019
        engine.ATTACK_THRESHOLD_GAP = 2.4
        engine.DEFEND_THRESHOLD_GAP = 1.4
        engine.DIRTY_AIR_PENALTY = 0.12
        engine.SLIPSTREAM_BONUS = 0.06
        engine.OVERTAKE_INCIDENT_MULTIPLIER = 2.2

    def _track_conditions(self, context: RaceContext) -> Dict[str, Any]:
        return (
            context.track_conditions
            if isinstance(context.track_conditions, dict)
            else {}
        )

    def _as_int(self, value: Any) -> Optional[int]:
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return None

    def _as_int_list(self, value: Any) -> Optional[List[int]]:
        if not isinstance(value, list):
            return None
        out: List[int] = []
        for item in value:
            try:
                out.append(int(item))
            except Exception:
                continue
        return out

    def _as_dict(self, value: Any) -> Optional[Dict[str, float]]:
        return value if isinstance(value, dict) else None

    def _as_float(self, value: Any, default: float) -> float:
        if value is None:
            return default
        try:
            return float(value)
        except Exception:
            return default

    def simulate_race(self, context: RaceContext) -> List[Dict[str, Any]]:
        # Prefer a module-level RealtimeRaceEngine (tests may monkeypatch this),
        # otherwise use the canonical factory.
        engine = None
        engine_cls = globals().get("RealtimeRaceEngine")
        if engine_cls is not None:
            engine = engine_cls(seed=getattr(self, "seed", None))
        else:
            engine = create_realtime_engine(seed=getattr(self, "seed", None))
        self._apply_tuning(engine)

        tc = self._track_conditions(context)
        teams = getattr(context, "teams", {}) or {}

        return engine.simulate_race(
            drivers=context.drivers,
            teams=teams,
            track=context.track,
            total_laps=context.total_laps,
            event_callback=context.event_callback,
            stop_event=tc.get("stop_event"),
            realtime_speed=self._as_float(tc.get("realtime_speed"), 5.0),
            track_points=tc.get("track_points"),
            player_driver_id=self._as_int(tc.get("player_driver_id")),
            player_team_driver_ids=self._as_int_list(tc.get("player_team_driver_ids")),
            player_overrides=self._as_dict(tc.get("player_overrides")),
        )
