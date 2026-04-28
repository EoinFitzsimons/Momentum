"""
Urban Street discipline adapter.

Provides a dedicated adapter class for the urban/street (drifting-oriented)
discipline while delegating race execution to the realtime engine.
"""

from typing import Any, Dict, List, Optional

from RaceLogic.base_race_engine import BaseDisciplineEngine, RaceContext, RacingDiscipline
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from database.models import Driver, Team
from services.race_engine_factory import create_realtime_engine


class UrbanStreetEngine(BaseDisciplineEngine):
    """Urban/street adapter with close-pack handling and control emphasis."""

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed if seed is not None else 0)
        self.discipline = RacingDiscipline.URBAN_STREET

    def get_attribute_weights(self) -> Dict[str, float]:
        return {
            "car_control": 0.18,
            "drift_control": 0.20,
            "consistency": 0.12,
            "reaction_time": 0.10,
            "adaptability": 0.10,
            "racecraft": 0.08,
            "overtaking": 0.06,
            "defensive_driving": 0.06,
            "raw_speed": 0.06,
            "pressure_handling": 0.04,
        }

    def calculate_lap_time(
        self,
        driver: Driver,
        team: Team,
        context: RaceContext,
        lap_number: int,
        current_position: int,
    ) -> float:
        base_lap = float(getattr(context.track, "lap_time", 78.0) or 78.0)
        performance = self.calculate_base_performance(driver, team, context)
        perf_factor = 1.10 - (0.24 * performance)
        surface_variation = 1.0 + (0.004 * (lap_number % 3))
        pack_pressure = 1.0 + (0.012 if current_position > 7 else 0.0)
        return base_lap * perf_factor * surface_variation * pack_pressure

    def _apply_tuning(self, engine: RealtimeRaceEngine) -> None:
        engine.BASE_SPEED_MPS = 60.0
        engine.MAX_SPEED_MPS = 82.0
        engine.MIN_SPEED_MPS = 22.0
        engine.TYRE_DEGRADATION_RATE = 0.000016
        pass
        engine.FUEL_BURN_RATE = 0.000016
        engine.ATTACK_THRESHOLD_GAP = 2.1
        engine.DEFEND_THRESHOLD_GAP = 1.2
        engine.DIRTY_AIR_PENALTY = 0.08
        engine.SLIPSTREAM_BONUS = 0.05
        engine.OVERTAKE_INCIDENT_MULTIPLIER = 2.9

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
