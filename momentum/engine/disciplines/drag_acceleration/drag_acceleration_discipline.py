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

Authors: Eoin Fitzsimons
Date: January 2026
"""

import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from momentum.engine.base_race_engine import (
    BaseDisciplineEngine,
    RaceContext,
    RacingDiscipline,
)
from momentum.engine.race_format import DRAG_ACCELERATION_FORMAT
from momentum.database.models import Driver, Team

UNKNOWN_DRIVER_LABEL = "Unknown Driver"


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

    race_format = DRAG_ACCELERATION_FORMAT

    def __init__(self, seed: Optional[int] = None):
        """Initialise drag racing engine"""
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
            "raw_speed": 0.25,  # Most critical for top speed
            "reaction_time": 0.20,  # Launch reflexes
            "race_start_skill": 0.15,  # Launch precision / wheel spin control
            # Acceleration control & consistency (22% combined)
            "acceleration_control": 0.12,  # Throttle management
            "consistency": 0.10,  # Repeatable launches
            # Mental & Physical (22% combined)
            "concentration": 0.08,  # Launch focus
            "pressure_handling": 0.06,  # Mental toughness at line
            "g_force_tolerance": 0.08,  # Physical endurance (high G forces)
            # Secondary factors
            "physical_fitness": 0.02,  # Stamina for bracket racing
            "risk_appetite": 0.02,  # Calculated risk on launch
        }

    def simulate_race(self, context: RaceContext) -> List[Dict[str, Any]]:
        """
        Simulate drag racing event as a single-elimination knockout tournament.

        Format:
        - One representative per team (best raw speed)
        - Qualifying run to seed bracket
        - Head-to-head elimination rounds until one winner remains
        - Emits position/race_finished events for GUI integration

        Args:
            context: RaceContext with drivers, track, conditions

        Returns:
            List of dicts (compatible with RaceResult) sorted by position (1-8 get points)
        """
        entrants = self._select_team_representatives(context)
        if not entrants:
            return []

        qualified = self._run_drag_qualifying(entrants, context)
        self._emit_drag_bracket_seeded(context, qualified)

        frame = 0
        race_time = 0.0
        realtime_speed = self._extract_realtime_speed(context)
        stop_event = self._extract_stop_event(context)
        self._emit_drag_position_update(
            context,
            qualified,
            frame=frame,
            race_time=race_time,
            progress=0.0,
            running=False,
            active_ids=[],
        )

        competitors, eliminated, race_time, frame = self._run_knockout_bracket(
            qualified,
            context,
            race_time,
            frame,
            realtime_speed,
            stop_event,
        )
        ranking_entries, final_results = self._build_drag_ranking_and_results(
            qualified, competitors, eliminated
        )

        final_race_time = max(
            (
                float(r.get("time_seconds", 0.0))
                for r in final_results
                if r.get("time_seconds") not in (None, float("inf"))
            ),
            default=0.0,
        )
        self._emit_drag_position_update(
            context,
            ranking_entries,
            frame=frame + 20,
            race_time=max(race_time, final_race_time),
            progress=1.0,
            running=False,
            active_ids=[],
        )
        self._emit_drag_race_finished(
            context, final_results, max(race_time, final_race_time)
        )
        return final_results

    def _run_drag_qualifying(
        self, entrants: List[Dict[str, Any]], context: RaceContext
    ) -> List[Dict[str, Any]]:
        """Run one qualifying pass per entrant and return seeded order."""
        qualified = []
        for entrant in entrants:
            run_result = self._simulate_single_run(
                entrant["driver"], entrant["team"], context
            )
            qualified.append(
                {
                    "driver": entrant["driver"],
                    "team": entrant["team"],
                    "result": run_result,
                }
            )
        qualified.sort(key=lambda e: e["result"].get("time_seconds", float("inf")))
        return qualified

    def _run_knockout_bracket(
        self,
        qualified: List[Dict[str, Any]],
        context: RaceContext,
        race_time: float,
        frame: int,
        realtime_speed: float,
        stop_event: Any,
    ):
        """Execute elimination rounds and return survivors/eliminations/time/frame."""
        competitors = qualified
        eliminated: List[Dict[str, Any]] = []
        round_idx = 1

        while len(competitors) > 1:
            next_round, i, race_time, frame, aborted = self._run_knockout_round(
                competitors,
                context,
                round_idx,
                race_time,
                frame,
                realtime_speed,
                stop_event,
                eliminated,
            )

            if aborted:
                while i < len(competitors):
                    next_round.append(competitors[i])
                    i += 1
                competitors = next_round
                break

            competitors = next_round
            frame += 10
            self._emit_drag_position_update(
                context,
                competitors,
                frame=frame,
                race_time=race_time,
                progress=0.0,
                running=False,
                active_ids=[],
            )
            round_idx += 1

        return competitors, eliminated, race_time, frame

    def _run_knockout_round(
        self,
        competitors: List[Dict[str, Any]],
        context: RaceContext,
        round_idx: int,
        race_time: float,
        frame: int,
        realtime_speed: float,
        stop_event: Any,
        eliminated: List[Dict[str, Any]],
    ):
        """Run one bracket round and return round state plus abort flag."""
        next_round: List[Dict[str, Any]] = []
        i = 0
        while i < len(competitors):
            if stop_event is not None and stop_event.is_set():
                return next_round, i, race_time, frame, True
            if i == len(competitors) - 1:
                next_round.append(competitors[i])
                i += 1
                continue

            left = competitors[i]
            right = competitors[i + 1]
            heat_idx = (i // 2) + 1
            winner, loser, heat_time, frame = self._run_head_to_head_showdown(
                left,
                right,
                context,
                frame=frame,
                race_time=race_time,
                realtime_speed=realtime_speed,
                stop_event=stop_event,
            )
            race_time += heat_time

            # Reconstruct lane-ordered result payloads from winner/loser entries.
            winner_id = int(getattr(winner.get("driver"), "id", 0) or 0)
            left_id = int(getattr(left.get("driver"), "id", 0) or 0)
            if winner_id == left_id:
                left_entry, right_entry = winner, loser
            else:
                left_entry, right_entry = loser, winner

            self._emit_drag_heat_result(
                context, round_idx, heat_idx, left_entry, right_entry, winner, race_time
            )
            next_round.append(winner)
            loser["eliminated_round"] = round_idx
            eliminated.append(loser)
            i += 2

        return next_round, i, race_time, frame, False

    def _build_drag_ranking_and_results(
        self,
        qualified: List[Dict[str, Any]],
        competitors: List[Dict[str, Any]],
        eliminated: List[Dict[str, Any]],
    ):
        """Build final ranking entries and result payload."""
        if not competitors:
            competitors = qualified[:1]

        champion = competitors[0]
        ranking_entries = [champion]
        eliminated.sort(
            key=lambda e: (
                -int(e.get("eliminated_round", 0)),
                float(e.get("result", {}).get("time_seconds", float("inf"))),
            )
        )
        ranking_entries.extend(eliminated)

        final_results: List[Dict[str, Any]] = []
        for pos, entry in enumerate(ranking_entries, 1):
            result = dict(entry["result"])
            result["position"] = pos
            if pos == 1:
                result["status"] = "WINNER"
            elif result.get("dnf_reason"):
                result["status"] = "DNF"
            else:
                result["status"] = "ELIMINATED"
            final_results.append(result)
        return ranking_entries, final_results

    def _extract_realtime_speed(self, context: RaceContext) -> float:
        """Read realtime speed from track conditions and clamp for watchability."""
        tc = getattr(context, "track_conditions", {}) if context is not None else {}
        raw = tc.get("realtime_speed", 1.0) if isinstance(tc, dict) else 1.0
        try:
            speed = float(raw)
        except Exception:
            speed = 1.0
        speed = max(0.25, min(2.0, speed))
        return speed

    def _extract_stop_event(self, context: RaceContext):
        """Read optional stop event from track conditions."""
        tc = getattr(context, "track_conditions", {}) if context is not None else {}
        if isinstance(tc, dict):
            return tc.get("stop_event")
        return None

    def _extract_player_driver_id(self, context: RaceContext) -> Optional[int]:
        """Read selected player driver id from context track conditions."""
        tc = getattr(context, "track_conditions", {}) if context is not None else {}
        if not isinstance(tc, dict):
            return None
        raw = tc.get("player_driver_id")
        try:
            return int(raw) if raw is not None else None
        except Exception:
            return None

    def _select_team_representatives(
        self, context: RaceContext
    ) -> List[Dict[str, Any]]:
        """Pick one best driver per team for drag knockout brackets."""
        best_by_team = self._best_driver_by_team(context.drivers)
        self._override_with_selected_player(best_by_team, context)
        entrants = self._build_drag_entrants(best_by_team, context)
        entrants.sort(
            key=lambda e: float(
                getattr(e["driver"], "raw_speed", getattr(e["driver"], "speed", 50.0))
                or 50.0
            ),
            reverse=True,
        )
        return entrants[:16]

    def _best_driver_by_team(self, drivers: List[Driver]) -> Dict[int, Driver]:
        """Select highest-speed driver for each team."""
        best_by_team: Dict[int, Driver] = {}
        for driver in drivers:
            team_id = int(getattr(driver, "current_team_id", 0) or 0)
            if team_id <= 0:
                continue
            prev = best_by_team.get(team_id)
            if prev is None or self._driver_speed(driver) > self._driver_speed(prev):
                best_by_team[team_id] = driver
        return best_by_team

    def _driver_speed(self, driver: Driver) -> float:
        """Return comparable speed score for bracket seeding."""
        return float(
            getattr(driver, "raw_speed", getattr(driver, "speed", 50.0)) or 50.0
        )

    def _override_with_selected_player(
        self, best_by_team: Dict[int, Driver], context: RaceContext
    ) -> None:
        """Force selected player to represent their team when available."""
        player_driver_id = self._extract_player_driver_id(context)
        if player_driver_id is None:
            return
        selected = next(
            (
                d
                for d in context.drivers
                if int(getattr(d, "id", 0) or 0) == player_driver_id
            ),
            None,
        )
        if selected is None:
            return
        selected_team_id = int(getattr(selected, "current_team_id", 0) or 0)
        if selected_team_id > 0:
            best_by_team[selected_team_id] = selected

    def _build_drag_entrants(
        self, best_by_team: Dict[int, Driver], context: RaceContext
    ) -> List[Dict[str, Any]]:
        """Build entrant payload with driver-team pairs for simulation."""
        entrants: List[Dict[str, Any]] = []
        for team_id, driver in best_by_team.items():
            team = context.teams.get(team_id)
            if team is None:
                team = Team(
                    id=team_id,
                    name=f"Team {team_id}",
                    nationality="USA",
                    discipline="drag",
                    tier="TIER_1",
                    budget=50.0,
                    founded_year=2020,
                    team_principal="Unknown",
                )
            entrants.append({"driver": driver, "team": team})
        return entrants

    def _emit_drag_bracket_seeded(
        self, context: RaceContext, qualified: List[Dict[str, Any]]
    ) -> None:
        """Emit initial bracket seed order for GUI knockout tree rendering."""
        cb = getattr(context, "event_callback", None)
        if not callable(cb):
            return
        seeds: List[Dict[str, Any]] = []
        for idx, entry in enumerate(qualified, 1):
            driver = entry.get("driver")
            if driver is None:
                continue
            seeds.append(
                {
                    "seed": idx,
                    "driver_id": int(getattr(driver, "id", 0) or 0),
                    "driver_name": str(getattr(driver, "name", f"Driver {idx}")),
                }
            )
        cb(
            {
                "type": "drag_bracket_seeded",
                "seeds": seeds,
                "entrant_count": len(seeds),
            }
        )

    def _emit_drag_heat_result(
        self,
        context: RaceContext,
        round_idx: int,
        heat_idx: int,
        left_entry: Dict[str, Any],
        right_entry: Dict[str, Any],
        winner: Dict[str, Any],
        race_time: float,
    ) -> None:
        """Emit one completed heat result for GUI bracket updates."""
        cb = getattr(context, "event_callback", None)
        if not callable(cb):
            return
        left_driver = left_entry.get("driver")
        right_driver = right_entry.get("driver")
        winner_driver = winner.get("driver")
        left_result = left_entry.get("result", {})
        right_result = right_entry.get("result", {})
        cb(
            {
                "type": "drag_heat_result",
                "round_index": int(round_idx),
                "heat_index": int(heat_idx),
                "left_id": int(getattr(left_driver, "id", 0) or 0),
                "left_name": str(getattr(left_driver, "name", UNKNOWN_DRIVER_LABEL)),
                "left_time_s": left_result.get("time_seconds"),
                "left_reaction_ms": left_result.get("reaction_time_ms"),
                "left_trap_kmh": left_result.get("trap_speed_kmh"),
                "right_id": int(getattr(right_driver, "id", 0) or 0),
                "right_name": str(getattr(right_driver, "name", UNKNOWN_DRIVER_LABEL)),
                "right_time_s": right_result.get("time_seconds"),
                "right_reaction_ms": right_result.get("reaction_time_ms"),
                "right_trap_kmh": right_result.get("trap_speed_kmh"),
                "winner_id": int(getattr(winner_driver, "id", 0) or 0),
                "winner_name": str(
                    getattr(winner_driver, "name", UNKNOWN_DRIVER_LABEL)
                ),
                "race_time": float(race_time),
            }
        )

    def _is_dnf_result(self, result: Dict[str, Any]) -> bool:
        """Return whether a run result represents a failed pass."""
        if result.get("dnf_reason"):
            return True
        t = result.get("time_seconds")
        return t is None or t == float("inf")

    def _run_head_to_head(
        self, left: Dict[str, Any], right: Dict[str, Any], context: RaceContext
    ):
        """Simulate one elimination pairing and return winner/loser entries."""
        left_result = self._simulate_single_run(left["driver"], left["team"], context)
        right_result = self._simulate_single_run(
            right["driver"], right["team"], context
        )
        left_entry = {
            "driver": left["driver"],
            "team": left["team"],
            "result": left_result,
        }
        right_entry = {
            "driver": right["driver"],
            "team": right["team"],
            "result": right_result,
        }

        left_dnf = self._is_dnf_result(left_result)
        right_dnf = self._is_dnf_result(right_result)
        if left_dnf and not right_dnf:
            return right_entry, left_entry
        if right_dnf and not left_dnf:
            return left_entry, right_entry
        if left_dnf and right_dnf:
            if float(left_result.get("reaction_time_ms", 9999.0)) <= float(
                right_result.get("reaction_time_ms", 9999.0)
            ):
                return left_entry, right_entry
            return right_entry, left_entry

        if float(left_result.get("time_seconds", float("inf"))) <= float(
            right_result.get("time_seconds", float("inf"))
        ):
            return left_entry, right_entry
        return right_entry, left_entry

    def _run_head_to_head_showdown(
        self,
        left: Dict[str, Any],
        right: Dict[str, Any],
        context: RaceContext,
        frame: int,
        race_time: float,
        realtime_speed: float,
        stop_event: Any,
    ):
        """Animate and resolve a single 1v1 drag heat."""
        winner, loser = self._run_head_to_head(left, right, context)
        left_id = int(left["driver"].id)
        right_id = int(right["driver"].id)
        heat_entries = [left, right]

        left_time = float(left["result"].get("time_seconds", 6.5))
        right_time = float(right["result"].get("time_seconds", 6.5))
        if left_time == float("inf"):
            left_time = 7.5
        if right_time == float("inf"):
            right_time = 7.5
        heat_duration = max(left_time, right_time, 5.5)
        heat_frames = max(90, int(heat_duration * 30))

        print(
            f"[DRAG HEAT] {left['driver'].name} vs {right['driver'].name} -> "
            f"winner: {winner['driver'].name}"
        )

        for step in range(heat_frames + 1):
            if stop_event is not None and stop_event.is_set():
                break
            progress = step / float(heat_frames)
            # Ease-out motion gives a stronger launch feel.
            eased = 1.0 - ((1.0 - progress) ** 1.45)
            self._emit_drag_position_update(
                context,
                heat_entries,
                frame=frame,
                race_time=race_time + progress * heat_duration,
                progress=eased,
                running=step < heat_frames,
                active_ids=[left_id, right_id],
            )
            frame += 1
            if step < heat_frames:
                target_sleep = (1.0 / 30.0) / realtime_speed
                time.sleep(target_sleep)

        return winner, loser, heat_duration, frame

    def _emit_drag_position_update(
        self,
        context: RaceContext,
        entries: List[Dict[str, Any]],
        frame: int,
        race_time: float,
        progress: float,
        running: bool,
        active_ids: List[int],
    ) -> None:
        """Emit synthetic realtime packets so GUI can animate drag races."""
        cb = getattr(context, "event_callback", None)
        if not callable(cb):
            return

        progress = max(0.0, min(1.0, progress))
        active_set = set(active_ids)
        strip_distance_m = self._resolve_visual_drag_distance(context)
        positions = []
        for idx, entry in enumerate(entries, 1):
            driver = entry["driver"]
            result = entry.get("result", {})
            driver_id = int(driver.id)
            is_active = driver_id in active_set
            distance = strip_distance_m * progress
            velocity_mps = 0.0
            if running and is_active:
                velocity_mps = 70.0 * progress
            positions.append(
                {
                    "driver_id": driver_id,
                    "driver_name": driver.name,
                    "position": idx,
                    "lap": 1,
                    "position_m": distance,
                    "velocity_mps": velocity_mps,
                    "racing_mode": "attack",
                    "push_intensity": 0.95,
                    "push_fatigue": min(1.0, progress * 0.5),
                    "tyre_condition": 0.98,
                    "fuel_load": 0.98,
                    "gap_ahead": 0.0 if idx == 1 else float(idx - 1) * 0.12,
                    "gap_behind": 0.0,
                    "running": running
                    and is_active
                    and not self._is_dnf_result(result),
                    "in_pit_lane": False,
                    "pit_time_remaining_s": 0.0,
                    "pit_stops_completed": 0,
                }
            )

        cb(
            {
                "type": "position_update",
                "frame": int(frame),
                "time": float(race_time),
                "positions": positions,
            }
        )

    def _resolve_visual_drag_distance(self, context: RaceContext) -> float:
        """Return strip distance used by GUI position packets."""
        track = getattr(context, "track", None)
        length_km = getattr(track, "length_km", None)
        if length_km is not None:
            try:
                length_m = float(length_km) * 1000.0
                if length_m > 50.0:
                    return length_m
            except (TypeError, ValueError):
                pass
        return float(self.DRAG_DISTANCE_M)

    def _emit_drag_race_finished(
        self, context: RaceContext, results: List[Dict[str, Any]], race_time: float
    ) -> None:
        """Emit race_finished payload for GUI handlers."""
        cb = getattr(context, "event_callback", None)
        if not callable(cb):
            return
        cb(
            {
                "type": "race_finished",
                "total_laps": 1,
                "race_time": float(race_time),
                "results": results,
                "collision_log": [],
            }
        )

    def _simulate_single_run(
        self, driver: Driver, team: Team, context: RaceContext
    ) -> Dict[str, Any]:
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
                "time_seconds": float("inf"),
                "laps_completed": 0,
                "dnf_reason": "red_light",
                "status": "DNF",
                "reaction_time_ms": reaction_time_ms,
                "trap_speed_kmh": 0.0,
            }

        # Calculate acceleration phases
        accel_0_100_ms = self._calculate_0_to_100_acceleration(driver, team, context)
        trap_speed_kmh = self._calculate_trap_speed(driver, team, context)
        accel_100_trap_ms = self._calculate_100_to_trap_acceleration(
            driver, team, context, trap_speed_kmh
        )

        # Total elapsed time (in milliseconds for precision)
        total_elapsed_ms = reaction_time_ms + accel_0_100_ms + accel_100_trap_ms
        total_elapsed_ms *= self._player_time_multiplier(
            context, int(getattr(driver, "id", 0) or 0)
        )

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
            "trap_speed_kmh": trap_speed_kmh,
        }

    def _player_time_multiplier(self, context: RaceContext, driver_id: int) -> float:
        """Convert UI pace/overtake overrides to a drag elapsed-time multiplier."""
        tc = getattr(context, "track_conditions", {}) if context is not None else {}
        if not isinstance(tc, dict):
            return 1.0

        controlled_ids = set()
        player_driver_id = tc.get("player_driver_id")
        try:
            if player_driver_id is not None:
                controlled_ids.add(int(player_driver_id))
        except Exception:
            pass

        for item in tc.get("player_team_driver_ids", []) or []:
            try:
                controlled_ids.add(int(item))
            except Exception:
                continue

        if driver_id not in controlled_ids:
            return 1.0

        overrides = tc.get("player_overrides", {})
        if not isinstance(overrides, dict):
            return 1.0

        pace = float(overrides.get("pace", 0.7) or 0.7)
        overtake = float(overrides.get("overtake", 0.5) or 0.5)
        pace = max(0.0, min(1.0, pace))
        overtake = max(0.0, min(1.0, overtake))
        push = max(0.0, min(1.0, 0.55 * pace + 0.45 * overtake))

        # 1.08x at minimum push -> 0.90x at maximum push.
        return 1.08 - (0.18 * push)

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
        reaction_attr = getattr(driver, "reaction_time", None)
        if reaction_attr is None:
            reaction_attr = getattr(driver, "reactions", 50.0)
        reaction_attr = float(reaction_attr or 50.0)  # Ensure float type
        reaction_factor = (reaction_attr / 50.0) - 1.0  # -1.0 to +1.0 range
        reaction_delta = reaction_factor * 80.0  # ±80ms from baseline

        # Race start skill bonus (smoother launch)
        start_skill = getattr(driver, "race_start_skill", 50.0)
        start_bonus = (start_skill / 50.0 - 1.0) * 60.0  # ±60ms bonus

        # Pressure handling (clutch control under stress)
        pressure = getattr(driver, "pressure_handling", 50.0)
        pressure_bonus = (pressure / 50.0 - 1.0) * 40.0  # ±40ms bonus

        # Random variance (nervousness, weather, track conditions)
        # Standard deviation: ±20ms for natural variation
        variance = self.rng.normal(0, 20)

        # Calculate final reaction time
        reaction_time = (
            baseline_ms + reaction_delta + start_bonus + pressure_bonus + variance
        )

        # Red light probability (false start)
        # More aggressive drivers have higher red light risk
        risk_appetite = getattr(driver, "risk_appetite", 50.0)
        concentration = getattr(driver, "concentration", 50.0)
        red_light_prob = (
            0.08 * (risk_appetite / 100.0) * ((100.0 - concentration) / 100.0)
        )

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
            team: Team with car development rating
            context: Race context with track/weather

        Returns:
            Acceleration time in milliseconds
        """
        # Baseline acceleration time (mid-tier vehicle)
        baseline_s = 4.0

        # Raw speed attribute (0-100)
        raw_speed = getattr(driver, "raw_speed", 50.0)
        speed_factor = raw_speed / 50.0  # 0.0-2.0 multiplier

        # Acceleration control attribute (0-100)
        accel_control = getattr(driver, "acceleration_control", 50.0)
        control_factor = 1.0 - (accel_control / 100.0) * 0.3  # 0.7-1.0 range

        # Team performance: car development (power upgrades) shortens the run
        team_factor = 1.0 - (self._team_car_rating(team) * 0.4)

        # Weather impact (grip level)
        weather_factor = self._get_weather_grip_factor(context.weather_conditions)

        # Final acceleration time
        accel_time = (
            baseline_s
            * (2.0 / speed_factor)
            * control_factor
            * team_factor
            * weather_factor
        )

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
        accel_required = (trap_speed_mps**2 - start_speed_mps**2) / (2 * distance_m)

        # Adjust acceleration based on consistency attribute
        consistency = getattr(driver, "consistency", 50.0)
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

    def _calculate_trap_speed(
        self, driver: Driver, team: Team, context: RaceContext
    ) -> float:
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
            team: Team with car development rating
            context: Race context

        Returns:
            Trap speed in km/h
        """
        # Baseline trap speed (mid-tier vehicle)
        baseline_kmh = 180.0

        # Raw speed attribute (0-100)
        raw_speed = getattr(driver, "raw_speed", 50.0)
        speed_factor = raw_speed / 50.0  # 0.0-2.0 range

        # Drag-specific aptitude (if available)
        drag_aptitude = getattr(driver, "drag_aptitude", 50.0)
        drag_factor = drag_aptitude / 50.0  # 0.0-2.0 range

        # Team performance: car development (power/aero upgrades) raises trap speed
        team_factor = 0.85 + (self._team_car_rating(team) * 0.45)  # 0.85-1.30 range

        # Environmental factors
        weather_factor = self._get_weather_grip_factor(context.weather_conditions)

        # Calculate final trap speed
        trap_speed = (
            baseline_kmh
            * speed_factor
            * drag_factor
            * team_factor
            * weather_factor
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
        precipitation = weather.get("precipitation", 0.0)
        if precipitation > 0:
            # Wet conditions: 0.7-0.85x grip
            rain_factor = 0.70 + (1.0 - min(precipitation / 10.0, 1.0)) * 0.15
        else:
            rain_factor = 1.0

        # Wind impact (headwind/tailwind affects trap speed)
        wind_speed = weather.get("wind_speed", 0.0)
        wind_factor = 1.0 - (abs(wind_speed) / 50.0) * 0.1  # ±10% for strong wind

        # Humidity/temperature (affects air density)
        temp = weather.get("temperature", 20.0)

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
        self,
        driver: Driver,
        team: Team,
        context: RaceContext,
        lap_number: int,
        current_position: int,
    ) -> float:
        """
        Calculate lap time for driver (not used in drag racing)

        Drag racing doesn't have laps, only single runs. This method is not used
        in the main simulate_race flow, but required by BaseDisciplineEngine abstract interface.

        Returns elapsed time from a single run.
        """
        # Drag does not use lap loops; return a representative single-run elapsed time.
        run = self._simulate_single_run(driver, team, context)
        elapsed = run.get("time_seconds")
        if isinstance(elapsed, (int, float)) and elapsed != float("inf"):
            return float(elapsed)
        return float("inf")
