"""
Endurance discipline adapter.

Provides a dedicated engine class so the discipline loader can resolve an
Endurance-specific adapter while still reusing the realtime simulation core.
"""

from typing import Any, Dict, List, Optional

from RaceLogic.base_race_engine import (
    BaseDisciplineEngine,
    RaceContext,
    RacingDiscipline,
)
from RaceLogic.race_format import ENDURANCE_FORMAT
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from database.models import Driver, Team
from services.race_engine_factory import create_realtime_engine


class EnduranceEngine(BaseDisciplineEngine):
    """Endurance racing adapter with reliability and tyre-management emphasis."""

    race_format = ENDURANCE_FORMAT

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed if seed is not None else 0)
        self.discipline = RacingDiscipline.ENDURANCE

    def get_attribute_weights(self) -> Dict[str, float]:
        return {
            "consistency": 0.18,
            "racecraft": 0.08,
            "raw_speed": 0.08,
            "tyre_management": 0.18,
            "fuel_management": 0.16,
            "mechanical_sympathy": 0.12,
            "concentration": 0.08,
            "pressure_handling": 0.06,
            "physical_fitness": 0.04,
            "wet_weather_skill": 0.02,
        }

    def calculate_lap_time(
        self,
        driver: Driver,
        team: Team,
        context: RaceContext,
        lap_number: int,
        current_position: int,
    ) -> float:
        base_lap = float(getattr(context.track, "lap_time", 95.0) or 95.0)
        performance = self.calculate_base_performance(driver, team, context)
        perf_factor = 1.10 - (0.24 * performance)
        stint_wear = 1.0 + (max(1, lap_number) * 0.0009)
        traffic = 1.0 + (0.01 if current_position > 8 else 0.0)
        return base_lap * perf_factor * stint_wear * traffic

    def _apply_tuning(self, engine: RealtimeRaceEngine) -> None:
        engine.BASE_SPEED_MPS = 68.0
        engine.MAX_SPEED_MPS = 88.0
        engine.MIN_SPEED_MPS = 26.0
        engine.TYRE_DEGRADATION_RATE = 0.000010
        engine.FUEL_BURN_RATE = 0.000018
        engine.ATTACK_THRESHOLD_GAP = 3.2
        engine.DEFEND_THRESHOLD_GAP = 1.9
        engine.DIRTY_AIR_PENALTY = 0.14
        engine.SLIPSTREAM_BONUS = 0.05
        engine.OVERTAKE_INCIDENT_MULTIPLIER = 1.7

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
            weather_conditions=context.weather_conditions,
            track_conditions=context.track_conditions,
        )
