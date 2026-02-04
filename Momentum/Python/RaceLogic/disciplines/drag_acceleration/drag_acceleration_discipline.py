"""
Drag Acceleration Racing Discipline - Quarter-mile acceleration racing simulation

Implements drag racing (top fuel, funny cars, pro stock) style quarter-mile racing.

Key Features:
- Single-run time-trial format (not lap-based)
- Reaction time simulation (launch control)
- 0-400m acceleration modeling
- Trap speed (top speed at finish) calculation
- Elimination bracket racing support
- Driver attribute utilization for drag-specific mechanics

Performance Model:
- Reaction time: 100-350ms (professional baseline ~150ms)
- Acceleration focus: 0-100 km/h, 100-top_speed phases
- Top speed (trap speed): 200-330+ km/h depending on vehicle class
- Points system: 8 positions (20,17,14,11,8,5,2,1) per race

Authors: Final Year Project - Computer Science
Date: January 2026
"""

import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from RaceLogic.base_race_engine import BaseDisciplineEngine, RaceContext, RacingDiscipline
from database.models import Driver, Team, RaceResult


@dataclass
class DragRaceResult:
    """Result from single drag race run"""
    driver_id: int
    position: int
    elapsed_time_ms: float  # Total elapsed time in milliseconds
    reaction_time_ms: float  # Launch reaction time
    trap_speed_kmh: float  # Top speed at finish line
    status: str = "completed"  # "completed", "dnf", "red_light"


class DragAccelerationEngine(BaseDisciplineEngine):
    """
    Drag Acceleration Racing Engine (Quarter-mile time-trial format)

    Simulates single-run quarter-mile (402m) drag racing with:
    - Launch/reaction time simulation (red light possibility)
    - Acceleration-based performance modeling (no cornering)
    - Trap speed (top-end speed) calculation
    - Single run time-trial scoring
    - Points awarded to top 8 finishers

    Attribute Utilization:
    - raw_speed (25%): Critical for top speed
    - reaction_time (20%): Launch control / reflexes
    - race_start_skill (15%): Launch precision
    - acceleration_control (12%): Throttle management
    - consistency (10%): Repeatable launches
    - concentration (8%): Focus under pressure
    - pressure_handling (6%): Mental toughness
    - g_force_tolerance (8%): Physical endurance
    """

    def __init__(self, seed: Optional[int] = None):
        """Initialize drag racing engine"""
        super().__init__(seed if seed is not None else 0)
        self.discipline = RacingDiscipline.DRAG_ACCELERATION
        self.DRAG_DISTANCE_M = 402.34  # Official quarter-mile distance

    def get_attribute_weights(self) -> Dict[str, float]:
        """
        Driver attribute weights for drag racing

        Drag racing heavily emphasizes:
        - Raw speed (top-end performance)
        - Reaction time (launch control)
        - Launch skills (race start)
        - Throttle management (acceleration control)
        - Physical/mental toughness (g-forces, pressure)
        """
        return {
            # Core acceleration attributes (57% combined)
            "raw_speed": 0.25,              # Most critical for top speed
            "reaction_time": 0.20,          # Launch reflexes
            "race_start_skill": 0.15,       # Launch precision / wheel spin control

            # Acceleration control & consistency (22% combined)
            "acceleration_control": 0.12,  # Throttle management
            "consistency": 0.10,            # Repeatable launches

            # Mental & Physical (22% combined)
            "concentration": 0.08,          # Launch focus
            "pressure_handling": 0.06,      # Mental toughness at line
            "g_force_tolerance": 0.08,      # Physical endurance (high G forces)

            # Secondary factors
            "physical_fitness": 0.02,       # Stamina for bracket racing
            "risk_appetite": 0.02,          # Calculated risk on launch
        }

    def simulate_race(self, context: RaceContext) -> List[RaceResult]:
        """
        Simulate drag racing event (single quarter-mile runs)

        Format: Time-trial qualification
        - Each driver gets one 402m run
        - Fastest elapsed time wins
        - Positions determined by time ranking
        - Top 8 finishers get championship points

        Args:
            context: RaceContext with drivers, track, conditions

        Returns:
            List of dicts (compatible with RaceResult) sorted by position (1-8 get points)
        """
        results = []

        # Simulate each driver's single run
        for i, driver in enumerate(context.drivers):
            team = context.teams.get(driver.current_team_id)
            if team is None:
                team = Team(
                    id=driver.current_team_id,
                    name=f"Team {driver.current_team_id}",
                    nationality="USA",
                    discipline="drag",
                    tier="tier1",
                    budget=50.0,
                    founded_year=2020,
                    team_principal="Unknown"
                )

            # Simulate single run
            run_result = self._simulate_single_run(driver, team, context)
            results.append(run_result)

        # Sort by elapsed time (fastest first), handling DNF (infinite time)
        results.sort(key=lambda r: r.get('time_seconds', float('inf')))

        # Update positions
        for i, result in enumerate(results):
            result['position'] = i + 1

        return results

    def _simulate_single_run(self, driver: Driver, team: Team, context: RaceContext) -> RaceResult:
        """
        Simulate single 402m drag racing run

        Calculates:
        1. Reaction time (launch quality)
        2. 0-100 km/h acceleration
        3. 100-trap_speed acceleration
        4. Total elapsed time

        Args:
            driver: Driver performing the run
            team: Team/vehicle performance
            context: Race context with track/weather

        Returns:
            Dict with elapsed time and trap speed (compatible with RaceResult)
        """
        # Calculate reaction time
        reaction_time_ms = self._calculate_reaction_time(driver, context)

        # Check for red light (false start)
        if reaction_time_ms >= 500:
            return {
                "driver_id": driver.id,
                "driver_name": driver.name,
                "team_id": team.id,
                "position": 999,  # Will be re-ranked
                "time_seconds": float('inf'),
                "laps_completed": 0,
                "dnf_reason": "red_light",
                "status": "DNF",
                "reaction_time_ms": reaction_time_ms,
                "trap_speed_kmh": 0.0
            }

        # Calculate acceleration phases
        accel_0_100_ms = self._calculate_0_to_100_acceleration(driver, team, context)
        trap_speed_kmh = self._calculate_trap_speed(driver, team, context)
        accel_100_trap_ms = self._calculate_100_to_trap_acceleration(
            driver, team, context, trap_speed_kmh
        )

        # Total elapsed time (in milliseconds for precision)
        total_elapsed_ms = reaction_time_ms + accel_0_100_ms + accel_100_trap_ms

        # Convert to seconds for RaceResult
        total_elapsed_s = total_elapsed_ms / 1000.0

        return {
            "driver_id": driver.id,
            "driver_name": driver.name,
            "team_id": team.id,
            "position": 0,  # Will be updated by caller
            "time_seconds": total_elapsed_s,
            "laps_completed": 1,  # Single "lap" (single run)
            "dnf_reason": None,
            "status": "FINISHED",
            "best_lap_time": total_elapsed_s,
            "reaction_time_ms": reaction_time_ms,
            "trap_speed_kmh": trap_speed_kmh
        }

    def _calculate_reaction_time(self, driver: Driver, context: RaceContext) -> float:
        """
        Calculate launch reaction time in milliseconds

        Range: 30-500ms
        - Red light (false start): 500ms+ (causes DNF)
        - Professional launch: 100-150ms
        - Average human: 200-250ms
        - Slow reaction: 300-400ms

        Human reaction time is typically 200-350ms. Professional drag racers
        achieve 100-150ms. Perfect launch would be <50ms (impossible for humans).

        Args:
            driver: Driver with reaction_time attribute
            context: Race context with weather/conditions

        Returns:
            Reaction time in milliseconds
        """
        # Baseline human reaction time
        baseline_ms = 180.0

        # Reaction time attribute modifier (0-100 scale)
        # Higher reaction_time = faster reflexes
        reaction_attr = getattr(driver, 'reaction_time', 50.0)
        reaction_factor = (reaction_attr / 50.0) - 1.0  # -1.0 to +1.0 range
        reaction_delta = reaction_factor * 80.0  # ±80ms from baseline

        # Race start skill bonus (smoother launch)
        start_skill = getattr(driver, 'race_start_skill', 50.0)
        start_bonus = (start_skill / 50.0 - 1.0) * 60.0  # ±60ms bonus

        # Pressure handling (clutch control under stress)
        pressure = getattr(driver, 'pressure_handling', 50.0)
        pressure_bonus = (pressure / 50.0 - 1.0) * 40.0  # ±40ms bonus

        # Random variance (nervousness, weather, track conditions)
        # Standard deviation: ±20ms for natural variation
        variance = self.rng.normal(0, 20)

        # Calculate final reaction time
        reaction_time = baseline_ms + reaction_delta + start_bonus + pressure_bonus + variance

        # Red light probability (false start)
        # More aggressive drivers have higher red light risk
        risk_appetite = getattr(driver, 'risk_appetite', 50.0)
        concentration = getattr(driver, 'concentration', 50.0)
        red_light_prob = 0.08 * (risk_appetite / 100.0) * ((100.0 - concentration) / 100.0)

        if self.rng.random() < red_light_prob:
            return 500.0  # Red light = disqualification

        # Clamp to realistic range
        return max(30.0, min(400.0, reaction_time))

    def _calculate_0_to_100_acceleration(
        self, driver: Driver, team: Team, context: RaceContext
    ) -> float:
        """
        Calculate 0-100 km/h acceleration time

        Typical ranges:
        - F1 car: ~2.5 seconds
        - Top fuel dragster: ~0.8 seconds
        - Pro stock: ~1.2 seconds
        - Road car: ~6-10 seconds
        - Poor car: ~10-15 seconds

        Args:
            driver: Driver with acceleration attributes
            team: Team/vehicle tier and budget
            context: Race context with track/weather

        Returns:
            Acceleration time in milliseconds
        """
        # Baseline acceleration time (mid-tier vehicle)
        baseline_s = 4.0

        # Raw speed attribute (0-100)
        raw_speed = getattr(driver, 'raw_speed', 50.0)
        speed_factor = raw_speed / 50.0  # 0.0-2.0 multiplier

        # Acceleration control attribute (0-100)
        accel_control = getattr(driver, 'acceleration_control', 50.0)
        control_factor = 1.0 - (accel_control / 100.0) * 0.3  # 0.7-1.0 range

        # Team performance (budget affects vehicle power)
        team_budget = getattr(team, 'budget', 50.0)  # in millions
        team_factor = 1.0 - (team_budget / 200.0) * 0.4  # Better budget = faster

        # Weather impact (grip level)
        weather_factor = self._get_weather_grip_factor(context.weather_conditions)

        # Final acceleration time
        accel_time = baseline_s * (2.0 / speed_factor) * control_factor * team_factor * weather_factor

        # Add randomness (inconsistency in launch, track conditions)
        variance = self.rng.normal(0, 0.15)

        accel_s = max(0.8, accel_time + variance)

        return accel_s * 1000.0  # Convert to milliseconds

    def _calculate_100_to_trap_acceleration(
        self, driver: Driver, team: Team, context: RaceContext, trap_speed_kmh: float
    ) -> float:
        """
        Calculate 100 km/h to trap speed acceleration

        This is the bulk of the race (typically 2-5 seconds depending on trap speed).

        Time calculation based on average acceleration:
        - v = v0 + a*t
        - Distance = v0*t + 0.5*a*t^2
        - Solve for t given distance and trap_speed

        Args:
            driver: Driver attributes
            team: Team/vehicle
            context: Race context
            trap_speed_kmh: Target speed at finish line

        Returns:
            Time in milliseconds
        """
        start_speed_kmh = 100.0
        start_speed_mps = start_speed_kmh / 3.6

        # Calculate required acceleration (m/s²)
        # Using: v² = v0² + 2*a*s
        trap_speed_mps = trap_speed_kmh / 3.6
        distance_m = self.DRAG_DISTANCE_M - 100.0  # Subtract rough 0-100 distance

        if trap_speed_mps <= start_speed_mps:
            # Driver can't reach trap speed, use minimal time
            return 4000.0

        # Calculate acceleration
        accel_required = (trap_speed_mps ** 2 - start_speed_mps ** 2) / (2 * distance_m)

        # Adjust acceleration based on consistency attribute
        consistency = getattr(driver, 'consistency', 50.0)
        consistency_factor = 1.0 - ((50.0 - consistency) / 100.0) * 0.2

        final_acceleration = accel_required * consistency_factor

        # Calculate time: t = (v - v0) / a
        if final_acceleration <= 0:
            time_s = 10.0
        else:
            time_s = (trap_speed_mps - start_speed_mps) / final_acceleration

        # Add variance
        variance = self.rng.normal(0, time_s * 0.08)

        return max(0.5, time_s + variance) * 1000.0  # Convert to ms

    def _calculate_trap_speed(self, driver: Driver, team: Team, context: RaceContext) -> float:
        """
        Calculate trap speed (speed at 402m finish line)

        This is the "top speed" achieved during the run.

        Typical ranges:
        - Top fuel dragster: 330+ mph (530+ km/h)
        - Funny car: 300+ mph (480+ km/h)
        - Pro stock: 200+ mph (320+ km/h)
        - Formula 1: 350+ km/h (top speed, not trap speed)
        - Road car: 150-250 km/h
        - Poor car: 100-150 km/h

        Args:
            driver: Driver with raw_speed and drag aptitude
            team: Team/vehicle tier and budget
            context: Race context

        Returns:
            Trap speed in km/h
        """
        # Baseline trap speed (mid-tier vehicle)
        baseline_kmh = 180.0

        # Raw speed attribute (0-100)
        raw_speed = getattr(driver, 'raw_speed', 50.0)
        speed_factor = raw_speed / 50.0  # 0.0-2.0 range

        # Drag-specific aptitude (if available)
        drag_aptitude = getattr(driver, 'drag_aptitude', 50.0)
        drag_factor = drag_aptitude / 50.0  # 0.0-2.0 range

        # Team performance (budget and tier affect vehicle)
        team_budget = getattr(team, 'budget', 50.0)
        team_factor = 0.7 + (team_budget / 200.0) * 0.6  # 0.7-1.3 range

        # Team tier bonus (TOP_TIER teams have better aerodynamics)
        tier = getattr(team, 'tier', 'tier2').upper()
        tier_multiplier = {
            'TOP_TIER': 1.2,
            'TIER_1': 1.2,
            'TIER_2': 1.0,
            'TIER_3': 0.85,
            'TIER2': 1.0,
            'TIER3': 0.85
        }.get(tier, 1.0)

        # Environmental factors
        weather_factor = self._get_weather_grip_factor(context.weather_conditions)

        # Calculate final trap speed
        trap_speed = (
            baseline_kmh * speed_factor * drag_factor * team_factor * tier_multiplier * weather_factor
        )

        # Add randomness (variance in aerodynamic drag, fuel burn)
        variance = self.rng.normal(0, trap_speed * 0.05)

        # Realistic bounds based on vehicle attributes
        min_speed = baseline_kmh * 0.4
        max_speed = baseline_kmh * 3.0

        return max(min_speed, min(max_speed, trap_speed + variance))

    def _get_weather_grip_factor(self, weather: Dict[str, float]) -> float:
        """
        Calculate weather impact on grip and acceleration

        Rain reduces grip significantly in drag racing.
        High wind affects aerodynamics.

        Args:
            weather: Weather conditions dict with precipitation, wind_speed

        Returns:
            Grip factor (0.6-1.0 range, 1.0 = optimal)
        """
        # Rain impact (significant in drag racing)
        precipitation = weather.get('precipitation', 0.0)
        if precipitation > 0:
            # Wet conditions: 0.7-0.85x grip
            rain_factor = 0.70 + (1.0 - min(precipitation / 10.0, 1.0)) * 0.15
        else:
            rain_factor = 1.0

        # Wind impact (headwind/tailwind affects trap speed)
        wind_speed = weather.get('wind_speed', 0.0)
        wind_factor = 1.0 - (abs(wind_speed) / 50.0) * 0.1  # ±10% for strong wind

        # Humidity/temperature (affects air density)
        temp = weather.get('temperature', 20.0)
        humidity = weather.get('humidity', 50.0)

        # Hot, dry conditions = better (thinner air density = less drag at top speed)
        # But this is complex; simplified to temperature only
        if temp > 25:
            temp_factor = 1.05  # Slightly better
        elif temp < 10:
            temp_factor = 0.95  # Slightly worse
        else:
            temp_factor = 1.0

        combined = rain_factor * wind_factor * temp_factor
        return max(0.6, min(1.2, combined))

    def calculate_lap_time(
        self, driver: Driver, team: Team, context: RaceContext, lap_number: int, current_position: int
    ) -> float:
        """
        Calculate lap time for driver (not used in drag racing)

        Drag racing doesn't have laps, only single runs. This method is not used
        in the main simulate_race flow, but required by BaseDisciplineEngine abstract interface.

        Returns elapsed time from a single run.
        """
        # Not applicable for drag racing (single run format)
        # Return a placeholder value
        return 10.0  # 10 seconds placeholder
