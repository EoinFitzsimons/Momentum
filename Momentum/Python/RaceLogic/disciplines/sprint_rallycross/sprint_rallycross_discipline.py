"""
Sprint Rallycross discipline adapter.

Provides a concrete adapter class with rallycross-specific tuning and joker-ready
behaviour through the shared realtime engine.
"""

from typing import Any, Dict, List, Optional

from RaceLogic.base_race_engine import BaseDisciplineEngine, RaceContext, RacingDiscipline
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from database.models import Driver, Team
from services.race_engine_factory import create_realtime_engine


class SprintRallycrossEngine(BaseDisciplineEngine):
    """Sprint/rallycross adapter emphasizing launches and car control."""

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed if seed is not None else 0)
        self.discipline = RacingDiscipline.SPRINT_RALLYCROSS

    def get_attribute_weights(self) -> Dict[str, float]:
        return {
            "reaction_time": 0.14,
            "race_start_skill": 0.14,
            "car_control": 0.16,
            "consistency": 0.12,
            "adaptability": 0.10,
            "wet_weather_skill": 0.08,
            "overtaking": 0.08,
            "defensive_driving": 0.06,
            "raw_speed": 0.06,
            "braking_technique": 0.06,
        }

    def calculate_lap_time(
        self,
        driver: Driver,
        team: Team,
        context: RaceContext,
        lap_number: int,
        current_position: int,
    ) -> float:
        base_lap = float(getattr(context.track, "lap_time", 70.0) or 70.0)
        performance = self.calculate_base_performance(driver, team, context)
        perf_factor = 1.08 - (0.22 * performance)
        dirt_variance = 1.0 + (0.006 if lap_number % 2 == 0 else 0.0)
        launch_traffic = 1.0 + (0.014 if current_position > 6 else 0.0)
        return base_lap * perf_factor * dirt_variance * launch_traffic

    def _apply_tuning(self, engine: RealtimeRaceEngine) -> None:
        engine.BASE_SPEED_MPS = 57.0
        engine.MAX_SPEED_MPS = 78.0
        engine.MIN_SPEED_MPS = 20.0
        engine.TYRE_DEGRADATION_RATE = 0.000014
        pass
        engine.FUEL_BURN_RATE = 0.000014
        engine.ATTACK_THRESHOLD_GAP = 1.9
        engine.DEFEND_THRESHOLD_GAP = 1.1
        engine.DIRTY_AIR_PENALTY = 0.10
        engine.SLIPSTREAM_BONUS = 0.04
        engine.OVERTAKE_INCIDENT_MULTIPLIER = 2.8

    def _track_conditions(self, context: RaceContext) -> Dict[str, Any]:
        return context.track_conditions if isinstance(context.track_conditions, dict) else {}

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
        engine_cls = globals().get('RealtimeRaceEngine')
        if engine_cls is not None:
            engine = engine_cls(seed=getattr(self, 'seed', None))
        else:
            engine = create_realtime_engine(seed=getattr(self, 'seed', None))
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
