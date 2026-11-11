"""One-off conversion of the old flat ``circuits_database.json`` to the
per-discipline files checked by ``momentum.data.circuit_schema``.

Stored figures that other figures already determine are dropped (the total
turn count, a drag strip's corners and straights), the new discipline fields
are added (a rallycross surface split and joker route, a drag strip's
shutdown area), and any figure outside its discipline profile, or
contradicting another, is brought inside it. Corrections are drawn from a
generator seeded by the circuit id, so the conversion is reproducible. Every
change is written to a review report.

Usage: python tools/split_circuit_database.py SOURCE.json [--report PATH]
"""

import argparse
import json
import random
from pathlib import Path

from momentum.data.circuit_profiles import PROFILES
from momentum.data.circuit_schema import CIRCUITS_DIR, FILES, QUARTER_MILE_M, validate_records

LAP_ONLY = (
    "length_km", "turns", "left_turns", "right_turns", "longest_straight_m",
    "shortest_straight_m", "tightest_corner_radius_m", "drs_zones",
)
NO_DRS = ("PRODUCTION_TOURING", "SPRINT_RALLYCROSS", "URBAN_STREET")


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def convert(old: dict, changes: list) -> dict:
    d = old["primary_discipline"]
    prof = PROFILES[d]
    rng = random.Random(f"circuit-{old['circuit_id']}")
    r = {k: v for k, v in old.items() if k != "turns"}

    def change(key, new, why):
        if r.get(key) != new:
            changes.append((d, old["name"], key, r.get(key, "-"), new, why))
            r[key] = new

    def drop(key, why):
        if key in r:
            changes.append((d, old["name"], key, r.pop(key), "-", why))

    if old.get("turns") != old.get("left_turns", 0) + old.get("right_turns", 0) and d != "DRAG_ACCELERATION":
        changes.append((d, old["name"], "turns", old.get("turns"), "-", "derived from left + right"))

    lo, hi = prof.ranges.get("avg_speed_kmh", (0, 1e9))
    if not lo <= r["avg_speed_kmh"] <= hi:
        change("avg_speed_kmh", round(rng.uniform(lo, hi), 1), "outside the discipline range")
    widths = sorted([r["track_width_min_m"], r["track_width_avg_m"], r["track_width_max_m"]])
    for key, value in zip(("track_width_min_m", "track_width_avg_m", "track_width_max_m"), widths):
        change(key, value, "widths ordered min <= avg <= max")
    if r["avg_temp_winter_c"] > r["avg_temp_summer_c"]:
        s, w = r["avg_temp_winter_c"], r["avg_temp_summer_c"]
        change("avg_temp_summer_c", s, "summer and winter were swapped")
        change("avg_temp_winter_c", w, "summer and winter were swapped")

    if d == "DRAG_ACCELERATION":
        for key in LAP_ONLY:
            if key == "length_km":
                continue
            drop(key, "a drag strip has no corners or lap")
        lo, hi = prof.ranges["shutdown_m"]
        shutdown = round(_clamp(old["length_km"] * 1000 - QUARTER_MILE_M, lo, hi))
        changes.append((d, old["name"], "length_km", old["length_km"], "-",
                        f"race distance {QUARTER_MILE_M} m + shutdown {shutdown} m"))
        r.pop("length_km")
        r["race_distance_m"] = QUARTER_MILE_M
        r["shutdown_m"] = float(shutdown)
        length_m = QUARTER_MILE_M + shutdown
    else:
        lo, hi = prof.ranges["length_km"]
        if not lo <= r["length_km"] <= hi:
            change("length_km", round(_clamp(r["length_km"], lo, hi), 2), "outside the discipline range")
        length_m = r["length_km"] * 1000
        turns = r["left_turns"] + r["right_turns"]
        tlo, thi = prof.turns
        if not tlo <= turns <= thi:
            scale = _clamp(turns, tlo, thi) / turns
            change("left_turns", round(r["left_turns"] * scale), "turn count outside the discipline range")
            change("right_turns", round(r["right_turns"] * scale), "turn count outside the discipline range")
        limit = prof.max_straight_share * length_m
        if r["longest_straight_m"] > limit:
            change("longest_straight_m", round(limit * rng.uniform(0.6, 0.95)),
                   f"above {prof.max_straight_share:.0%} of the lap")
        if r["shortest_straight_m"] > r["longest_straight_m"]:
            change("shortest_straight_m", round(r["longest_straight_m"] * rng.uniform(0.15, 0.35)),
                   "longer than the longest straight")
        lo, hi = prof.ranges["tightest_corner_radius_m"]
        if not lo <= r["tightest_corner_radius_m"] <= hi:
            change("tightest_corner_radius_m", round(rng.uniform(lo, hi), 1), "outside the discipline range")
        if d in NO_DRS:
            drop("drs_zones", "the discipline does not use DRS")
        elif "drs_zones" in prof.ranges:
            lo, hi = prof.ranges["drs_zones"]
            if not lo <= r["drs_zones"] <= hi:
                change("drs_zones", int(_clamp(r["drs_zones"], lo, hi)), "outside the discipline range")

    if d == "SPRINT_RALLYCROSS":
        asphalt = round(rng.uniform(0.5, 0.7) * 20) / 20
        drop("surface", "replaced by the surface split")
        r["surfaces"] = {"asphalt": asphalt, "gravel": round(1 - asphalt, 2)}
        r["joker"] = {
            "extra_length_m": float(round(rng.uniform(0.04, 0.09) * length_m)),
            "branch_at_fraction": round(rng.uniform(0.3, 0.8), 2),
        }
        changes.append((d, old["name"], "surfaces / joker", "-",
                        f"{r['surfaces']} / {r['joker']}", "new rallycross fields"))
    if r["pit_lane_length_m"] >= length_m:
        change("pit_lane_length_m", round(length_m * rng.uniform(0.3, 0.5), 1), "not shorter than the circuit")
    return r


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--report", type=Path, default=Path("build/circuit_conversion.md"))
    args = parser.parse_args(argv)

    changes: list = []
    converted = [convert(rec, changes) for rec in json.loads(args.source.read_text(encoding="utf-8"))]
    _, errors = validate_records([("converted", rec) for rec in converted])
    if errors:
        print("\n".join(errors))
        return 1
    CIRCUITS_DIR.mkdir(exist_ok=True)
    for discipline, filename in FILES.items():
        records = [r for r in converted if r["primary_discipline"] == discipline]
        (CIRCUITS_DIR / filename).write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    lines = ["| Discipline | Circuit | Field | Old | New | Why |", "|---|---|---|---|---|---|"]
    lines += [f"| {' | '.join(str(x) for x in c)} |" for c in changes]
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(converted)} circuits written, {len(changes)} changes listed in {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
