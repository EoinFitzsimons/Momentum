"""
Single Seater Racing Discipline - Formula-style racing simulation

Implements F1/F2/F3 style racing with comprehensive driver attribute utilization.
MVP implementation for midpoint demo, focusing on single seater discipline only.

Key Features:
- Comprehensive driver attribute weighting (20+ relevant attributes)
- Lap-by-lap simulation with tire degradation
- Fuel load impact on lap times
- Weather adaptation for wet conditions
- Traffic impact on lap times
- Mechanical reliability simulation
- F1-style championship points system

Performance Model:
- Base performance: 50% driver attributes (weighted), 30% team, 10% weather, 10% track
- Lap time modifiers: tire wear, fuel load, traffic, weather conditions, incidents
- Consistency: Lap-to-lap variance based on driver consistency attribute

Authors: Eoin Fitzsimons
Date: September 2025
"""

import time
from typing import List, Dict, Any, Optional

# Use the realtime agent engine for single-seater demo
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from RaceLogic.base_race_engine import BaseDisciplineEngine, RaceContext, RacingDiscipline
from database.models import Driver, Team


class SingleSeaterEngine(BaseDisciplineEngine):
    """
    Single Seater Racing Engine (F1, F2, F3 style)

    Simulates Formula-style racing with sophisticated attribute-based performance
    modeling, tire strategy, fuel management, and weather adaptation.

    Attribute Utilization:
    - Core skills: raw_speed (20%), cornering_skill (15%), consistency (15%)
    - Technical: tire_management (8%), setup_knowledge (10%), fuel_management (6%)
    - Mental: concentration (8%), pressure_handling (6%), g_force_tolerance (8%)
    - Discipline: single_seater_aptitude (12%)
    - Race craft: racecraft (12%), overtaking (8%), defensive_driving (6%)
    - Environmental: wet_weather_skill (8%), car_adaptation (6%)

    Total: 20+ attributes weighted for single seater performance
    """

    def __init__(self, seed: Optional[int] = None):
        """Initialise single seater engine"""
        super().__init__(seed if seed is not None else 0)
        self.discipline = RacingDiscipline.SINGLE_SEATER

    def get_attribute_weights(self) -> Dict[str, float]:
        """
        Driver attribute weights for single seater racing (F1/Formula style)

        Returns a comprehensive mapping of driver attributes to their importance
        in single seater performance. Total weights sum to ~2.0 for normalization.
        """
        return {
            # Core driving skills (high importance - 62% combined)
            "raw_speed": 0.20,              # Critical for qualifying and race pace
            "consistency": 0.15,            # Essential for championship success
            "racecraft": 0.12,              # Important for wheel-to-wheel racing
            "cornering_skill": 0.15,        # Crucial for single seater performance

            # Physical and mental traits (30% combined)
            "concentration": 0.08,          # Long race focus
            "reaction_time": 0.06,          # Quick reflexes for starts/overtakes
            "g_force_tolerance": 0.08,      # High G forces in single seaters
            "pressure_handling": 0.06,      # Championship pressure
            "physical_fitness": 0.02,       # Endurance for long races

            # Technical knowledge (24% combined)
            "setup_knowledge": 0.10,        # Car setup crucial in F1
            "tire_management": 0.08,        # Strategic tire use
            "fuel_management": 0.06,        # Fuel strategy importance

            # Single seater specific (12%)
            "single_seater_aptitude": 0.12,  # Natural preference for formula racing

            # Race craft and strategy (28% combined)
            "overtaking": 0.08,             # Passing ability
            "defensive_driving": 0.06,      # Position defense
            "braking_technique": 0.10,      # Late braking into corners
            "race_start_skill": 0.04,       # Launch and first lap

            # Environmental adaptation (20% combined)
            "wet_weather_skill": 0.08,      # Wet conditions common
            "car_adaptation": 0.06,         # Adapting to car changes
            "track_learning": 0.05,         # Learning new circuits
            "adaptability": 0.01,           # General adaptation ability

            # Personal traits (10% combined)
            "risk_appetite": 0.04,          # Calculated risk-taking
            "aggression": 0.03,             # Controlled aggression
            "smoothness": 0.03,             # Smooth driving for tire preservation
        }

    def _apply_base_tuning(self, engine: RealtimeRaceEngine) -> None:
        engine.BASE_SPEED_MPS = 75.0
        engine.MAX_SPEED_MPS = 100.0
        engine.MIN_SPEED_MPS = 30.0
        engine.DIRTY_AIR_PENALTY = 0.22
        engine.DIRTY_AIR_DISTANCE = 160.0
        engine.SLIPSTREAM_BONUS = 0.06
        engine.SLIPSTREAM_DISTANCE = 45.0
        engine.ATTACK_THRESHOLD_GAP = 2.5
        engine.DEFEND_THRESHOLD_GAP = 1.5
        engine.NEARBY_DISTANCE_M = 140.0
        engine.TIRE_DEGRADATION_RATE = 0.000012
        engine.FUEL_BURN_RATE = 0.000025
        engine.OVERTAKE_INCIDENT_MULTIPLIER = 2.5

    def _apply_preset_tuning(self, engine: RealtimeRaceEngine, preset: str) -> None:
        preset = (preset or "balanced").lower()
        self._apply_base_tuning(engine)

        if preset == 'aggressive':
            engine.DIRTY_AIR_PENALTY = 0.14
            engine.DIRTY_AIR_DISTANCE = 120.0
            engine.SLIPSTREAM_BONUS = 0.12
            engine.SLIPSTREAM_DISTANCE = 80.0
            engine.ATTACK_THRESHOLD_GAP = 1.6
            engine.DEFEND_THRESHOLD_GAP = 1.0
            engine.NEARBY_DISTANCE_M = 160.0
            engine.OVERTAKE_INCIDENT_MULTIPLIER = 3.2
            engine.TIRE_DEGRADATION_RATE = 0.00001
        elif preset == 'tyre_sensitive':
            engine.DIRTY_AIR_PENALTY = 0.26
            engine.DIRTY_AIR_DISTANCE = 180.0
            engine.SLIPSTREAM_BONUS = 0.04
            engine.SLIPSTREAM_DISTANCE = 40.0
            engine.ATTACK_THRESHOLD_GAP = 3.0
            engine.DEFEND_THRESHOLD_GAP = 2.0
            engine.NEARBY_DISTANCE_M = 120.0
            engine.TIRE_DEGRADATION_RATE = 0.000018
            engine.FUEL_BURN_RATE = 0.000028
            engine.OVERTAKE_INCIDENT_MULTIPLIER = 2.0

    def _extract_track_conditions(self, context: RaceContext) -> Dict[str, Any]:
        return context.track_conditions if isinstance(context.track_conditions, dict) else {}

    def _extract_preset_choice(self, track_conditions: Dict[str, Any]) -> str:
        preset_raw = track_conditions.get('tuning_preset', track_conditions.get('preset', 'balanced'))
        return preset_raw if isinstance(preset_raw, str) else 'balanced'

    def _parse_player_driver_id(self, track_conditions: Dict[str, Any]) -> Optional[int]:
        pdid = track_conditions.get('player_driver_id')
        if isinstance(pdid, int):
            return int(pdid)
        if isinstance(pdid, float) and pdid.is_integer():
            return int(pdid)
        return None

    def _parse_player_team_driver_ids(self, track_conditions: Dict[str, Any]) -> Optional[List[int]]:
        ptids = track_conditions.get('player_team_driver_ids')
        if not isinstance(ptids, list):
            return None
        parsed_ids: List[int] = []
        for item in ptids:
            try:
                parsed_ids.append(int(item))
            except Exception:
                continue
        return parsed_ids

    def _parse_player_overrides(self, track_conditions: Dict[str, Any]) -> Optional[Dict[str, float]]:
        po = track_conditions.get('player_overrides')
        return po if isinstance(po, dict) else None

    def _parse_realtime_speed(self, track_conditions: Dict[str, Any]) -> float:
        rs_val = track_conditions.get('realtime_speed')
        if rs_val is not None and isinstance(rs_val, (int, float, str)):
            return float(rs_val)
        return 5.0

    def simulate_race(self, context: RaceContext) -> List[Dict[str, Any]]:
        """
        Delegate simulation to the real-time agent-based engine.

        This adapter configures the `RealtimeRaceEngine` with single-seater
        tuned parameters (high downforce, sensitive dirty-air effects,
        aggressive overtaking thresholds) and forwards events to the
        provided `context.event_callback` for GUI integration.

        Returns the list of result dictionaries produced by the realtime engine.
        """
        # Instantiate realtime engine and tune for single-seater behaviour
        engine = RealtimeRaceEngine(seed=None)
        tc = self._extract_track_conditions(context)
        preset_choice = self._extract_preset_choice(tc)
        self._apply_preset_tuning(engine, preset_choice)

        print(f"-> SingleSeaterEngine tuning preset applied: {preset_choice}")

        # Build teams dictionary if not supplied
        teams = getattr(context, 'teams', {}) or {}

        # Player overrides: safely extract typed values from track_conditions
        player_driver_id = self._parse_player_driver_id(tc)
        player_team_driver_ids = self._parse_player_team_driver_ids(tc)
        player_overrides = self._parse_player_overrides(tc)
        realtime_speed = self._parse_realtime_speed(tc)

        # Delegate to realtime engine
        results = engine.simulate_race(
            drivers=context.drivers,
            teams=teams,
            track=context.track,
            total_laps=context.total_laps,
            event_callback=context.event_callback,
            stop_event=tc.get('stop_event'),
            realtime_speed=realtime_speed,
            track_points=tc.get('track_points'),
            player_driver_id=player_driver_id,
            player_team_driver_ids=player_team_driver_ids,
            player_overrides=player_overrides
        )

        # The realtime engine returns a list of result dicts compatible with the
        # BaseDisciplineEngine expectations, so return directly.
        return results

    def calculate_lap_time(self, driver: Driver, team: Team, context: RaceContext,
                           lap_number: int, current_position: int) -> float:
        """
        Calculate lap time for driver using comprehensive attribute model

        Lap Time Components:
        1. Base lap time from track (e.g., 90 seconds)
        2. Performance modifier from base_performance calculation (±20%)
        3. Tire degradation (increases lap time as race progresses)
        4. Fuel load (decreases lap time as fuel burns off)
        5. Traffic impact (slower in traffic, faster in clean air)
        6. Consistency variance (lap-to-lap variation)
        7. Weather adaptation (rain increases lap time)

        Args:
            driver: Driver with comprehensive attributes
            team: Team with tier and budget
            context: Race context with track and conditions
            lap_number: Current lap number
            current_position: Driver's current position

        Returns:
            Lap time in seconds
        """
        # Base lap time from track (default to 90s if not set)
        base_lap_time = getattr(context.track, 'lap_time', 90.0)

        # Calculate comprehensive performance factor
        performance = self.calculate_base_performance(driver, team, context)

        # Performance modifier: range from -20% (excellent) to +20% (poor)
        # Performance of 1.0 = -20%, 0.5 = 0%, 0.0 = +20%
        performance_modifier = (1.0 - performance) * 0.4 - 0.2

        # Tire degradation (increases lap time over race)
        tire_deg_factor = self._calculate_tire_degradation(
            driver, lap_number, context)

        # Fuel load effect (lap times improve as fuel burns off)
        fuel_factor = self._calculate_fuel_effect(
            lap_number, context.total_laps)

        # Traffic impact (position-dependent)
        traffic_factor = self._calculate_traffic_impact(
            current_position, len(context.drivers))

        # Consistency variance (lap-to-lap variation)
        consistency_variance = self._calculate_consistency_variance(driver)

        # Weather impact (rain slows lap times)
        weather_factor = self._calculate_weather_lap_impact(driver, context)

        # Combine all factors
        total_modifier = (performance_modifier + tire_deg_factor + fuel_factor +
                          traffic_factor + consistency_variance + weather_factor)

        # Calculate final lap time
        lap_time = base_lap_time * (1.0 + total_modifier)

        # Ensure lap time is reasonable (50% to 200% of base time)
        lap_time = max(base_lap_time * 0.5, min(lap_time, base_lap_time * 2.0))

        return lap_time

    def _calculate_tire_degradation(self, driver: Driver, lap_number: int,
                                    context: RaceContext) -> float:
        """
        Calculate tire degradation impact on lap time

        Tire wear increases linearly over race, modified by driver tire management
        skill and weather conditions (rain reduces tire wear).

        Args:
            driver: Driver with tire_management attribute
            lap_number: Current lap
            context: Race context

        Returns:
            Tire degradation modifier (0 to +0.10 = 0% to +10% slower)
        """
        # Base tire degradation (linear over race)
        race_progress = lap_number / context.total_laps
        base_degradation = race_progress * 0.10  # Up to +10% slower by end

        # Driver tire management reduces degradation
        tire_mgmt = getattr(driver, 'tire_management', 50.0) / 100.0
        degradation_reduction = tire_mgmt * 0.5  # Up to 50% reduction

        # Weather impact (rain reduces tire wear)
        precipitation = context.weather_conditions["precipitation"]
        if precipitation > 0.5:  # Wet conditions
            weather_reduction = 0.5  # 50% less degradation in rain
        else:
            weather_reduction = 0.0

        # Final degradation
        final_degradation = base_degradation * \
            (1.0 - degradation_reduction - weather_reduction)
        return max(0.0, final_degradation)

    def _calculate_fuel_effect(self, lap_number: int,
                               total_laps: int) -> float:
        """
        Calculate fuel load effect on lap time

        Cars start heavy with full fuel and get lighter (faster) as fuel burns.
        Maximum improvement of ~2% from start to finish.

        Args:
            lap_number: Current lap
            total_laps: Total race laps

        Returns:
            Fuel effect modifier (-0.02 to 0 = -2% to 0% faster)
        """
        race_progress = lap_number / total_laps
        # Fuel burns off linearly, lap times improve by ~2%
        fuel_improvement = -0.02 * race_progress
        return fuel_improvement

    def _calculate_traffic_impact(
            self, position: int, total_drivers: int) -> float:
        """
        Calculate traffic impact on lap time

        Drivers in midfield lose time in traffic. Leaders and backmarkers
        have clean air. Maximum traffic penalty of ~3%.

        Args:
            position: Current position
            total_drivers: Total number of drivers

        Returns:
            Traffic modifier (0 to +0.03 = 0% to +3% slower)
        """
        if position == 1:
            # Leader has clean air
            return 0.0
        elif position <= 3:
            # Top 3 have minimal traffic
            return 0.005
        elif position <= total_drivers // 2:
            # Midfield has most traffic
            return 0.03
        else:
            # Back of pack has clean air again
            return 0.01

    def _calculate_consistency_variance(self, driver: Driver) -> float:
        """
        Calculate lap-to-lap consistency variance

        Uses driver consistency attribute to determine randomness in lap times.
        Inconsistent drivers have higher lap time variance.

        Args:
            driver: Driver with consistency attribute

        Returns:
            Random variance modifier (-0.02 to +0.02 for consistent drivers,
                                     -0.05 to +0.05 for inconsistent drivers)
        """
        consistency = driver.consistency / 100.0

        # Variance range based on consistency
        # Consistent driver (100): ±2%, Inconsistent driver (0): ±5%
        variance_range = 0.02 + (1.0 - consistency) * 0.03

        # Random variance (normal distribution)
        variance = self.rng.normal(0, variance_range / 2.0)

        # Clamp to range
        return max(-variance_range, min(variance, variance_range))

    def _calculate_weather_lap_impact(
            self, driver: Driver, context: RaceContext) -> float:
        """
        Calculate weather impact on lap time

        Rain slows lap times significantly. Wet weather skill reduces the penalty.

        Args:
            driver: Driver with wet_weather_skill attribute
            context: Race context with weather conditions

        Returns:
            Weather modifier (0 to +0.30 = 0% to +30% slower in heavy rain)
        """
        precipitation = context.weather_conditions["precipitation"]

        if precipitation < 0.5:
            # Dry conditions
            return 0.0

        # Wet conditions - base slowdown
        # Light rain (0.5-5mm): +5-10%, Heavy rain (10-20mm): +20-30%
        base_slowdown = min(0.05 + (precipitation / 20.0) * 0.25, 0.30)

        # Wet weather skill reduces penalty
        wet_skill = getattr(
            driver,
            'wet_weather_skill',
            driver.adaptability) / 100.0
        skill_reduction = wet_skill * 0.5  # Up to 50% reduction

        final_slowdown = base_slowdown * (1.0 - skill_reduction)
        return final_slowdown

    def _initialize_race_state(self, context: RaceContext) -> Dict[str, Any]:
        """Initialise race state tracking"""
        driver_ids = [d.id for d in context.drivers]

        return {
            "active_drivers": set(driver_ids),
            "total_times": dict.fromkeys(driver_ids, 0.0),
            "laps_completed": dict.fromkeys(driver_ids, 0),
            "positions": {did: i + 1 for i, did in enumerate(driver_ids)},
            "dnf_reasons": {},
            "dnf_laps": {},
            "drivers_by_id": {d.id: d for d in context.drivers}
        }

    def _handle_dnf(self, driver_id: int, reason: str, lap: int,
                    race_state: Dict[str, Any], context: RaceContext):
        """Handle driver DNF"""
        race_state["active_drivers"].remove(driver_id)
        race_state["dnf_reasons"][driver_id] = reason
        race_state["dnf_laps"][driver_id] = lap

        driver = race_state["drivers_by_id"][driver_id]
        self.emit_event("dnf", {
            "driver_id": driver_id,
            "driver_name": driver.name,
            "reason": reason,
            "lap": lap
        }, context)

    def _update_positions(self, race_state: Dict[str, Any]):
        """Update driver positions based on total time"""
        # Sort by total time (ascending)
        sorted_drivers = sorted(
            race_state["active_drivers"],
            key=lambda did: race_state["total_times"][did]
        )

        # Update positions
        for i, driver_id in enumerate(sorted_drivers, 1):
            race_state["positions"][driver_id] = i

    def _emit_standings(
            self, lap: int, race_state: Dict[str, Any], context: RaceContext):
        """Emit current race standings"""
        standings = []

        for driver_id in sorted(race_state["active_drivers"],
                                key=lambda did: race_state["total_times"][did]):
            driver = race_state["drivers_by_id"][driver_id]
            standings.append({
                "driver_id": driver_id,
                "name": driver.name,
                "position": race_state["positions"][driver_id],
                "time_seconds": race_state["total_times"][driver_id],
                "laps_completed": race_state["laps_completed"][driver_id],
                "running": True
            })

        # Add DNF drivers at end
        for driver_id, reason in race_state["dnf_reasons"].items():
            driver = race_state["drivers_by_id"][driver_id]
            standings.append({
                "driver_id": driver_id,
                "name": driver.name,
                "position": len(standings) + 1,
                "time_seconds": race_state["total_times"][driver_id],
                "laps_completed": race_state["laps_completed"][driver_id],
                "running": False,
                "dnf_reason": reason
            })

        self.emit_event(
            "standings", {
                "lap": lap, "standings": standings}, context)

    def _compile_results(self, race_state: Dict[str, Any],
                         context: RaceContext) -> List[Dict[str, Any]]:
        """Compile final race results"""
        results = []

        # Finishers (sorted by total time)
        for position, driver_id in enumerate(
            sorted(race_state["active_drivers"],
                   key=lambda did: race_state["total_times"][did]), 1):

            driver = race_state["drivers_by_id"][driver_id]
            results.append({
                "driver_id": driver_id,
                "driver_name": driver.name,
                "team_id": driver.current_team_id,
                "position": position,
                "total_time": race_state["total_times"][driver_id],
                "laps_completed": race_state["laps_completed"][driver_id],
                "dnf_reason": None,
                "points": self._calculate_points(position)
            })

        # DNF drivers (sorted by laps completed, then time)
        dnf_position = len(results) + 1
        for driver_id in sorted(
                race_state["dnf_reasons"].keys(),
                key=lambda did: (
                    -race_state["laps_completed"][did],
                    race_state["total_times"][did]
                )):

            driver = race_state["drivers_by_id"][driver_id]
            results.append({
                "driver_id": driver_id,
                "driver_name": driver.name,
                "team_id": driver.current_team_id,
                "position": dnf_position,
                "total_time": race_state["total_times"][driver_id],
                "laps_completed": race_state["laps_completed"][driver_id],
                "dnf_reason": race_state["dnf_reasons"][driver_id],
                "points": 0
            })
            dnf_position += 1

        return results

    def _calculate_points(self, position: int) -> int:
        """Calculate championship points (F1 system)"""
        points_table = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

        if position <= len(points_table):
            return points_table[position - 1]
        else:
            return 0


# Export the engine
__all__ = ['SingleSeaterEngine']
