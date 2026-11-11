"""
3-lap discipline calibration runner.

Runs controlled short simulations and tunes:
- Logistic slopes (straight/braking/outside/switch/risk)
- Weibull parameters (tyre/mechanical eta,beta)

Terminology:
- Logistic slope: controls how sharply overtake/incident probability changes
    when conditions get better or worse.
- Weibull distribution: a reliability model used for failure risk over usage/time.
    In this file, it models wear/failure growth across laps.
    The term comes from Waloddi Weibull, the Swedish engineer/statistician
    who formalized and popularized this distribution in reliability work
    (notably in publications from 1939 and 1951).
- eta (scale): "life" parameter. Larger eta means failures tend to happen later.
- beta (shape): curve shape. beta < 1 early failures, beta ~= 1 near-constant
    risk, beta > 1 increasing wear-out risk.

Usage:
  python tools/calibrate_3lap.py
"""

from __future__ import annotations

import contextlib
import io
import os
import sys
import argparse
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, cast


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_ROOT = os.path.dirname(THIS_DIR)
if PYTHON_ROOT not in sys.path:
    sys.path.insert(0, PYTHON_ROOT)

from momentum.database.database_manager import DatabaseManager
from momentum.services.race_engine_factory import create_realtime_engine
from momentum.engine.disciplines.single_seater.single_seater_discipline import (
    SingleSeaterEngine,
)
from momentum.engine.disciplines.production_touring.production_touring_discipline import (
    ProductionTouringEngine,
)
from momentum.engine.disciplines.urban_street.urban_street_discipline import UrbanStreetEngine
from momentum.engine.disciplines.sprint_rallycross.sprint_rallycross_discipline import (
    SprintRallycrossEngine,
)
from momentum.engine.disciplines.endurance.endurance_discipline import EnduranceEngine

DISCIPLINES = [
    "SINGLE_SEATER",
    "PRODUCTION_TOURING",
    "URBAN_STREET",
    "DRAG_ACCELERATION",
    "SPRINT_RALLYCROSS",
    "ENDURANCE",
]

DEFAULT_LAPS = 3
CARS = 20
BASE_SEED = 4200

TARGETS: Dict[str, Dict[str, float]] = {
    "SINGLE_SEATER": {"dnf_rate": 0.010, "overtakes_per_race": 14.0},
    "PRODUCTION_TOURING": {"dnf_rate": 0.012, "overtakes_per_race": 12.0},
    "URBAN_STREET": {"dnf_rate": 0.015, "overtakes_per_race": 16.0},
    "DRAG_ACCELERATION": {"dnf_rate": 0.020, "overtakes_per_race": 0.0},
    "SPRINT_RALLYCROSS": {"dnf_rate": 0.022, "overtakes_per_race": 8.0},
    "ENDURANCE": {"dnf_rate": 0.018, "overtakes_per_race": 10.0},
}

SLOPE_CANDIDATES = [0.80, 0.92, 1.00, 1.08, 1.20]
HAZARD_CANDIDATES: List[Tuple[float, float, float, float]] = [
    # (tyre_eta, tyre_beta, mech_eta, mech_beta)
    (22.0, 2.2, 75.0, 1.9),
    (28.0, 2.6, 95.0, 2.1),
    (36.0, 3.0, 120.0, 2.3),
]

QUALITY_RULES: Dict[str, Dict[str, float]] = {
    "SINGLE_SEATER": {
        "push_min": 0.74,
        "overspeed_min": 1.8,
        "gap_min": 0.5,
        "gap_max": 18.0,
        "success_min": 0.40,
    },
    "PRODUCTION_TOURING": {
        "push_min": 0.70,
        "overspeed_min": 1.2,
        "gap_min": 0.5,
        "gap_max": 20.0,
        "success_min": 0.38,
    },
    "URBAN_STREET": {
        "push_min": 0.72,
        "overspeed_min": 1.0,
        "gap_min": 0.5,
        "gap_max": 16.0,
        "success_min": 0.36,
    },
    "DRAG_ACCELERATION": {
        "push_min": 0.78,
        "overspeed_min": 2.5,
        "gap_min": 0.3,
        "gap_max": 24.0,
        "success_min": 0.45,
    },
    "SPRINT_RALLYCROSS": {
        "push_min": 0.68,
        "overspeed_min": 0.9,
        "gap_min": 0.3,
        "gap_max": 14.0,
        "success_min": 0.34,
    },
    "ENDURANCE": {
        "push_min": 0.62,
        "overspeed_min": 0.7,
        "gap_min": 0.5,
        "gap_max": 26.0,
        "success_min": 0.32,
    },
}

NON_TUNABLE_DISCIPLINES = {"DRAG_ACCELERATION"}


@dataclass
class Metrics:
    races: int
    cars: int
    dnf: int
    overtakes: int
    quality_attempts: int

    @property
    def dnf_rate(self) -> float:
        return self.dnf / self.cars if self.cars else 0.0

    @property
    def overtakes_per_race(self) -> float:
        return self.overtakes / self.races if self.races else 0.0

    @property
    def quality_attempts_per_race(self) -> float:
        return self.quality_attempts / self.races if self.races else 0.0


def _coerce_float(value: object, default: float) -> float:
    """Best-effort conversion for loosely typed event payload values."""
    if value is None:
        return float(default)
    try:
        return float(cast(Any, value))
    except Exception:
        return float(default)


def _is_quality_attempt(event: Dict[str, object], discipline: str) -> bool:
    """Return True when an overtake attempt happened in a realistic window."""
    if event.get("type") != "overtake_attempt":
        return False

    rules = QUALITY_RULES.get(discipline, QUALITY_RULES["PRODUCTION_TOURING"])
    push = _coerce_float(event.get("push_intensity"), 0.0)
    overspeed = _coerce_float(event.get("speed_advantage_kmh"), 0.0)
    gap_m = _coerce_float(event.get("gap_m"), 999.0)
    success_prob = _coerce_float(event.get("success_probability"), 0.0)
    section = str(event.get("section") or "").lower()

    in_overtake_section = section in {
        "straight",
        "braking_zone",
        "fast_corner",
        "medium_corner",
    }
    return (
        in_overtake_section
        and push >= rules["push_min"]
        and overspeed >= rules["overspeed_min"]
        and rules["gap_min"] <= gap_m <= rules["gap_max"]
        and success_prob >= rules["success_min"]
    )


def _collect_drivers(
    db: DatabaseManager, discipline: str, max_cars: int
) -> Tuple[list, dict, object]:
    tracks = db.get_tracks_by_discipline(discipline)
    teams = db.get_teams_by_discipline(discipline)
    if not tracks or not teams:
        return [], {}, None

    drivers = []
    for team in teams:
        drivers.extend(db.get_drivers_by_team(team.id))
        if len(drivers) >= max_cars:
            break
    drivers = drivers[:max_cars]
    team_map = {t.id: t for t in teams}
    selected_track = min(
        tracks, key=lambda t: float(getattr(t, "length_km", 9999.0) or 9999.0)
    )
    return drivers, team_map, selected_track


def _laps_for_discipline(discipline: str) -> int:
    """Drag is a single run, while circuit disciplines stay lap-based."""
    if discipline == "DRAG_ACCELERATION":
        return 1
    return DEFAULT_LAPS


def _apply_discipline_method_tuning(
    engine: Any, discipline: str
) -> None:
    """Apply baseline tuning from each discipline adapter implementation."""
    if discipline == "SINGLE_SEATER":
        SingleSeaterEngine()._apply_base_tuning(engine)
        return
    if discipline == "PRODUCTION_TOURING":
        ProductionTouringEngine()._apply_tuning(engine)
        return
    if discipline == "URBAN_STREET":
        UrbanStreetEngine()._apply_tuning(engine)
        return
    if discipline == "SPRINT_RALLYCROSS":
        SprintRallycrossEngine()._apply_tuning(engine)
        return
    if discipline == "ENDURANCE":
        EnduranceEngine()._apply_tuning(engine)


def _run_profile(
    db: DatabaseManager,
    discipline: str,
    profile: Dict[str, float],
    iterations: int,
    seed_start: int,
) -> Metrics:
    cars = 0
    dnf = 0
    overtakes = 0
    quality_attempts = 0
    races = 0

    for i in range(iterations):
        drivers, team_map, track = _collect_drivers(db, discipline, CARS)
        if len(drivers) < 8 or track is None:
            continue

        events: list[dict[str, object]] = []

        def cb(evt, sink=events):
            sink.append(evt)

        engine = create_realtime_engine(seed=seed_start + i, db=db)
        engine.debug_logging = False
        engine.START_GRID_SPACING_M = 12.0
        _apply_discipline_method_tuning(engine, discipline)
        engine.discipline_calibration[discipline].update(profile)

        race_laps = _laps_for_discipline(discipline)
        with contextlib.redirect_stdout(io.StringIO()):
            results = engine.simulate_race(
                drivers=drivers,
                teams=team_map,
                track=track,
                total_laps=race_laps,
                event_callback=cb,
                realtime_speed=250.0,
            )

        races += 1
        cars += len(results)
        dnf += sum(1 for r in results if r.get("dnf_reason"))

        event_overtakes = sum(1 for e in events if e.get("type") == "overtake")
        if event_overtakes > 0:
            overtakes += event_overtakes
        else:
            race_finished_events = [
                e for e in events if e.get("type") == "race_finished"
            ]
            if race_finished_events:
                final_payload = race_finished_events[-1]
                collision_log = final_payload.get("collision_log") or []
                if isinstance(collision_log, list):
                    overtakes += sum(
                        1 for item in collision_log if item.get("type") == "overtake"
                    )

        quality_attempts += sum(1 for e in events if _is_quality_attempt(e, discipline))

    return Metrics(
        races=races,
        cars=cars,
        dnf=dnf,
        overtakes=overtakes,
        quality_attempts=quality_attempts,
    )


def _score(metrics: Metrics, target: Dict[str, float]) -> float:
    """Return objective score where lower is better.

    The score blends:
    - DNF error against target
    - Overtake signal error against target

    Overtake signal includes realized overtakes plus a capped share of
    quality attempts so the tuner still gets directional signal when attempts
    are realistic but conversion is temporarily low.
    """
    dnf_err = abs(metrics.dnf_rate - target["dnf_rate"])
    # Weighted signal: realized overtakes + capped quality attempts as forward signal.
    capped_quality = min(
        metrics.quality_attempts_per_race, target["overtakes_per_race"] * 1.25
    )
    effective_overtake_signal = metrics.overtakes_per_race + (0.30 * capped_quality)
    ov_err = abs(effective_overtake_signal - target["overtakes_per_race"]) / max(
        1.0, target["overtakes_per_race"]
    )
    return (dnf_err * 100.0) + (ov_err * 10.0)


def calibrate(
    stage1_iters: int,
    stage2_iters: int,
    final_iters: int,
    disciplines: List[str],
) -> Dict[str, Dict[str, float]]:
    db = DatabaseManager()
    tuned: Dict[str, Dict[str, float]] = {}

    for idx, discipline in enumerate(disciplines):
        target = TARGETS[discipline]
        base_seed = BASE_SEED + (idx * 100)
        laps = _laps_for_discipline(discipline)
        print(
            f"[CAL] {discipline}: stage1 slope search ({stage1_iters} iters/candidate)",
            flush=True,
        )
        print(f"[CAL] {discipline}: race format laps={laps}", flush=True)

        # Stage 1: tune logistic slopes with default hazards.
        best_profile = {
            "straight_slope": 3.8,
            "braking_slope": 3.4,
            "outside_slope": 3.2,
            "switch_slope": 3.0,
            "risk_slope": 3.4,
            "tyre_eta": 28.0,
            "tyre_beta": 2.6,
            "mech_eta": 95.0,
            "mech_beta": 2.1,
        }
        baseline_metrics = _run_profile(
            db, discipline, best_profile, iterations=stage1_iters, seed_start=base_seed
        )
        best_score = _score(baseline_metrics, target)

        if discipline in NON_TUNABLE_DISCIPLINES:
            print(
                f"[CAL] {discipline}: skipping slope/hazard search (non-lap sprint format)",
                flush=True,
            )
            final_metrics = _run_profile(
                db,
                discipline,
                best_profile,
                iterations=final_iters,
                seed_start=base_seed + 60,
            )
            tuned[discipline] = dict(best_profile)
            print(
                f"{discipline}: "
                f"DNF={final_metrics.dnf_rate:.4f} (target {target['dnf_rate']:.4f}), "
                f"OVR/race={final_metrics.overtakes_per_race:.2f} (target {target['overtakes_per_race']:.2f}), "
                f"QUAL_ATT/race={final_metrics.quality_attempts_per_race:.2f}"
            )
            print(f"  tuned={best_profile}")
            continue

        for scale in SLOPE_CANDIDATES:
            candidate = dict(best_profile)
            candidate.update(
                {
                    "straight_slope": 3.8 * scale,
                    "braking_slope": 3.4 * scale,
                    "outside_slope": 3.2 * scale,
                    "switch_slope": 3.0 * scale,
                    "risk_slope": 3.4 * scale,
                }
            )
            metrics = _run_profile(
                db,
                discipline,
                candidate,
                iterations=stage1_iters,
                seed_start=base_seed + 20,
            )
            score = _score(metrics, target)
            if score < best_score:
                best_score = score
                best_profile = candidate

        # Stage 2: tune Weibull eta/beta.
        print(
            f"[CAL] {discipline}: stage2 hazard search ({stage2_iters} iters/candidate)",
            flush=True,
        )
        for tyre_eta, tyre_beta, mech_eta, mech_beta in HAZARD_CANDIDATES:
            candidate = dict(best_profile)
            candidate.update(
                {
                    "tyre_eta": tyre_eta,
                    "tyre_beta": tyre_beta,
                    "mech_eta": mech_eta,
                    "mech_beta": mech_beta,
                }
            )
            metrics = _run_profile(
                db,
                discipline,
                candidate,
                iterations=stage2_iters,
                seed_start=base_seed + 40,
            )
            score = _score(metrics, target)
            if score < best_score:
                best_score = score
                best_profile = candidate

        # Final validation pass.
        print(f"[CAL] {discipline}: final validation ({final_iters} iters)", flush=True)
        final_metrics = _run_profile(
            db,
            discipline,
            best_profile,
            iterations=final_iters,
            seed_start=base_seed + 60,
        )

        tuned[discipline] = dict(best_profile)
        print(
            f"{discipline}: "
            f"DNF={final_metrics.dnf_rate:.4f} (target {target['dnf_rate']:.4f}), "
            f"OVR/race={final_metrics.overtakes_per_race:.2f} (target {target['overtakes_per_race']:.2f}), "
            f"QUAL_ATT/race={final_metrics.quality_attempts_per_race:.2f}"
        )
        print(f"  tuned={best_profile}")

    return tuned


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3-lap discipline calibration runner")
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    parser.add_argument("--discipline", choices=DISCIPLINES)
    args = parser.parse_args()

    if args.mode == "quick":
        stage1_iters, stage2_iters, final_iters = 1, 1, 2
    else:
        stage1_iters, stage2_iters, final_iters = 2, 2, 4

    selected_disciplines = [args.discipline] if args.discipline else DISCIPLINES

    print("CALIBRATION_3LAP_START")
    print(
        f"MODE={args.mode} stage1={stage1_iters} stage2={stage2_iters} final={final_iters}"
    )
    print(f"DISCIPLINES={','.join(selected_disciplines)}")
    tuned_profiles = calibrate(
        stage1_iters, stage2_iters, final_iters, selected_disciplines
    )
    print("CALIBRATION_3LAP_DONE")
    for disc, profile in tuned_profiles.items():
        print(disc, profile)
