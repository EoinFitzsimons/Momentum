"""Procedural circuit layouts built from real-world corner archetypes.

Layouts are assembled from features found on real circuits (hairpins,
chicanes, esses, sweepers, double-apex corners and kinks) that turn in
both directions. Corner entries and exits use clothoids whose curvature
ramps smoothly to the arc curvature, and straight lengths are solved so the
loop closes exactly under the same discrete integration used by
``CircuitGenerator``. Every layout is deterministic for a given seed.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import lsq_linear
from scipy.spatial import ConvexHull, cKDTree

DISPLAY_WIDTH = 1000.0
DISPLAY_HEIGHT = 700.0
# The whole circuit is drawn into a 1000 x 700 box with a 28 px road, so a
# corner tighter than the road's half width renders as a rounded point.
MIN_DISPLAY_RADIUS = 12.0
MIN_DISPLAY_CLEARANCE = 46.0
# Nothing on a real circuit turns tighter than this (a kart hairpin).
MIN_REAL_RADIUS = 8.0
MAIN_STRAIGHT_CLEARANCE = 92.0
MAX_ATTEMPTS = 400

# name: (turn_count, angle range deg, radius range as multiple of the anchor)
# The anchor is the circuit's tightest corner radius, so corner size follows
# the kind of circuit it is (karting, street, grand prix) and never the lap
# length: a 10 km circuit can still have a 15 m hairpin.
FEATURES: Dict[str, Tuple[int, Tuple[float, float], Tuple[float, float]]] = {
    "hairpin": (1, (150.0, 180.0), (1.0, 1.3)),
    "slow": (1, (75.0, 105.0), (1.6, 2.6)),
    "medium": (1, (45.0, 75.0), (3.0, 5.0)),
    "sweeper": (1, (35.0, 70.0), (6.0, 11.0)),
    "kink": (1, (12.0, 24.0), (12.0, 20.0)),
    "carousel": (1, (110.0, 145.0), (3.0, 4.5)),
    "chicane": (2, (40.0, 65.0), (1.3, 2.0)),
    "esses": (3, (32.0, 58.0), (2.2, 3.5)),
    "double_apex": (2, (45.0, 75.0), (2.0, 3.0)),
}
# Real corners of each kind rarely exceed these radii, whatever the lap length.
FEATURE_MAX_RADIUS: Dict[str, float] = {
    "hairpin": 45.0, "slow": 90.0, "medium": 160.0, "sweeper": 320.0, "kink": 600.0,
    "carousel": 140.0, "chicane": 70.0, "esses": 110.0, "double_apex": 110.0,
}
# Sign pattern of each feature relative to its leading corner: a chicane
# turns one way then the other, esses alternate, a double apex keeps turning.
FEATURE_SIGNS: Dict[str, Tuple[int, ...]] = {
    "hairpin": (1,), "slow": (1,), "medium": (1,), "sweeper": (1,), "kink": (1,),
    "carousel": (1,), "chicane": (1, -1), "esses": (1, -1, 1), "double_apex": (1, 1),
}

DISCIPLINE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "SINGLE_SEATER": {
        "hairpin": 1.0, "slow": 1.4, "medium": 1.6, "sweeper": 1.2, "kink": 0.5,
        "carousel": 0.4, "chicane": 0.9, "esses": 0.8, "double_apex": 0.6,
    },
    "PRODUCTION_TOURING": {
        "hairpin": 1.0, "slow": 1.6, "medium": 1.6, "sweeper": 0.9, "kink": 0.4,
        "carousel": 0.4, "chicane": 0.8, "esses": 0.7, "double_apex": 0.6,
    },
    "ENDURANCE": {
        "hairpin": 0.6, "slow": 1.0, "medium": 1.3, "sweeper": 1.8, "kink": 1.0,
        "carousel": 0.4, "chicane": 0.8, "esses": 1.0, "double_apex": 0.5,
    },
    "URBAN_STREET": {
        "hairpin": 0.8, "slow": 3.0, "medium": 1.0, "sweeper": 0.4, "kink": 0.6,
        "carousel": 0.1, "chicane": 1.2, "esses": 0.3, "double_apex": 0.3,
    },
    "SPRINT_RALLYCROSS": {
        "hairpin": 1.4, "slow": 1.4, "medium": 1.2, "sweeper": 0.6, "kink": 0.6,
        "carousel": 0.5, "chicane": 0.3, "esses": 0.4, "double_apex": 0.2,
    },
}


@dataclass
class LayoutSpec:
    """Inputs describing the circuit to build."""

    length_m: float
    turns: int = 12
    left_turns: Optional[int] = None
    right_turns: Optional[int] = None
    longest_straight_m: Optional[float] = None
    tightest_corner_radius_m: Optional[float] = None
    discipline: str = "SINGLE_SEATER"
    seed: int = 0


@dataclass
class _Piece:
    kind: str
    angle_deg: float = 0.0
    radius_m: float = 0.0
    length_m: float = 0.0
    feature: str = ""
    role: str = "link"


@lru_cache(maxsize=4096)
def _corner_samples(
    angle_deg: float, radius: float, clothoid: int, k: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One-metre samples of a corner entered at the origin heading along +x.

    Steps exactly as ``CircuitGenerator._add_corner`` does; cached because the
    search re-simulates the same corners many times.
    """
    target = math.radians(angle_deg)
    sign = 1 if target > 0 else -1
    entry_curv = [k * i * sign for i in range(clothoid)]
    entry_turn = float(np.sum(entry_curv)) if clothoid else 0.0
    arc_n = int(abs(radius * (target - 2 * entry_turn)))
    curv = np.array(
        entry_curv + [sign / radius] * arc_n + [k * (clothoid - i) * sign for i in range(clothoid)]
    )
    theta = np.cumsum(curv)
    x = np.cumsum(np.cos(theta))
    y = np.cumsum(np.sin(theta))
    for arr in (x, y, theta):
        arr.setflags(write=False)
    return x, y, theta


def _instruction_samples(instr: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if instr["type"] == "S":
        n = int(instr["length_m"])
        steps = np.arange(1, n + 1, dtype=float)
        return steps, np.zeros(n), np.zeros(n)
    return _corner_samples(
        float(instr["angle_deg"]),
        float(instr["radius_m"]),
        int(instr["clothoid_len"]),
        float(instr["k"]),
    )


def _end_state(instructions: Sequence[Dict[str, Any]]) -> Tuple[float, float, float, int]:
    """Final (x, y, theta, sample count) without materialising every sample."""
    x = y = theta = 0.0
    count = 0
    for instr in instructions:
        if instr["type"] == "S":
            n = int(instr["length_m"])
            x += n * math.cos(theta)
            y += n * math.sin(theta)
            count += n
            continue
        lx, ly, lt = _instruction_samples(instr)
        if len(lx):
            c, s_ = math.cos(theta), math.sin(theta)
            x += c * lx[-1] - s_ * ly[-1]
            y += s_ * lx[-1] + c * ly[-1]
            theta += lt[-1]
            count += len(lx)
    return x, y, theta, count


def simulate(instructions: Sequence[Dict[str, Any]]) -> np.ndarray:
    """Integrate dict instructions as ``CircuitGenerator`` does.

    Returns an (n, 3) array of x, y, theta at one-metre samples.
    """
    x = y = theta = 0.0
    chunks = []
    for instr in instructions:
        lx, ly, lt = _instruction_samples(instr)
        if not len(lx):
            continue
        c, s_ = math.cos(theta), math.sin(theta)
        gx = x + c * lx - s_ * ly
        gy = y + s_ * lx + c * ly
        gt = theta + lt
        chunks.append(np.column_stack((gx, gy, gt)))
        x, y, theta = float(gx[-1]), float(gy[-1]), float(gt[-1])
    return np.vstack(chunks) if chunks else np.zeros((0, 3))


def _corner_instruction(angle_deg: float, radius_m: float) -> Dict[str, Any]:
    arc_len = radius_m * math.radians(abs(angle_deg))
    clothoid = int(max(4.0, min(arc_len * 0.28, radius_m * 0.6)))
    return {
        "type": "C",
        "angle_deg": float(angle_deg),
        "radius_m": float(radius_m),
        "clothoid_len": clothoid,
        "k": 1.0 / (radius_m * clothoid),
    }


def _corner_length(angle_deg: float, radius_m: float) -> float:
    instr = _corner_instruction(angle_deg, radius_m)
    clothoid_turn = instr["clothoid_len"] / radius_m
    arc = max(0.0, math.radians(abs(angle_deg)) - clothoid_turn) * radius_m
    return 2 * instr["clothoid_len"] + arc


def _pick_feature(rng: random.Random, weights: Dict[str, float]) -> str:
    names = list(weights)
    return rng.choices(names, weights=[weights[n] for n in names])[0]


def _display_radius_floor(length_m: float) -> float:
    """Smallest corner radius that still draws as a curve for a lap this long.

    A lap of ``length_m`` metres spans roughly ``length_m / 3.4`` metres across
    once closed, and is scaled into the 1000 px display box, so this is
    MIN_DISPLAY_RADIUS converted back into metres at that scale.
    """
    return MIN_DISPLAY_RADIUS * length_m / 3400.0


def _corner_counts(spec: LayoutSpec, rng: random.Random) -> Tuple[int, int]:
    """Left and right corner counts the layout must contain, exactly."""
    left = int(spec.left_turns or 0)
    right = int(spec.right_turns or 0)
    if left + right > 0:
        return max(0, left), max(0, right)
    total = max(4, int(spec.turns or 12))
    dominant = int(round(total * rng.uniform(0.55, 0.7)))
    dominant = min(total - 1, max(1, dominant))
    return (dominant, total - dominant) if rng.random() < 0.5 else (total - dominant, dominant)


def _scale_to_loop(
    corners: List[Tuple[str, List[Tuple[float, float]], List[str]]], direction: int
) -> Optional[List[Tuple[str, List[Tuple[float, float]], List[str]]]]:
    """Scale corner angles so the lap turns through exactly one loop.

    Corner counts are fixed, so the balance comes from the angles: the
    reverse-direction corners are scaled first (they decide how much the
    dominant side has to make up), then the dominant ones. Either side may
    only stretch or shrink within a plausible range, otherwise the sample is
    rejected and another drawn.
    """
    dominant = sum(a for _, ps, _ in corners for a, _ in ps if a * direction > 0)
    reverse = -sum(a for _, ps, _ in corners for a, _ in ps if a * direction < 0)
    dominant, reverse = abs(dominant), abs(reverse)
    if dominant < 1e-6:
        return None
    lo, hi = 0.5, 1.7
    g = 1.0
    f = (360.0 + g * reverse) / dominant
    if f > hi:
        g = max(lo, (hi * dominant - 360.0) / reverse) if reverse > 1e-6 else lo
        f = (360.0 + g * reverse) / dominant
    elif f < lo:
        g = min(hi, (lo * dominant - 360.0) / reverse) if reverse > 1e-6 else hi
        f = (360.0 + g * reverse) / dominant
    if not lo <= f <= hi or not lo <= g <= hi:
        return None
    scaled = [
        (name, [(a * (f if a * direction > 0 else g), r) for a, r in ps], links)
        for name, ps, links in corners
    ]
    # No corner turns more than a hairpin. Whatever the clamp removes is
    # spread over the dominant corners that still have room, so the lap keeps
    # turning through exactly one loop; if none have room the sample is out.
    for _ in range(6):
        deficit = 0.0
        room = []
        for ci, (_, ps, _) in enumerate(scaled):
            for pi, (a, _) in enumerate(ps):
                if abs(a) > 180.0:
                    deficit += (abs(a) - 180.0) * direction * (1 if a * direction > 0 else -1)
                elif a * direction > 0 and abs(a) < 179.0:
                    room.append((ci, pi))
        if abs(deficit) < 1e-6:
            break
        if not room:
            return None
        share = deficit / len(room)
        scaled = [
            (name, [
                (max(-180.0, min(180.0, a)) + (share if (ci, pi) in room else 0.0), r)
                for pi, (a, r) in enumerate(ps)
            ], links)
            for ci, (name, ps, links) in enumerate(scaled)
        ]
    if any(abs(a) > 180.0 + 1e-6 for _, ps, _ in scaled for a, _ in ps):
        return None
    return scaled


def _order_around_lap(
    scaled: List[Tuple[str, List[Tuple[float, float]], List[str]]],
    direction: int,
    rng: random.Random,
) -> List[Tuple[str, List[Tuple[float, float]], List[str]]]:
    """Arrange features so the heading drifts steadily round one loop.

    A random order of forty corners wanders off like a river; a real circuit
    turns its way round because the corners that make up the 360 degrees are
    spread along the lap and the opposite-handed ones sit between them as
    S-bends. Reverse corners are paired with a dominant corner of similar
    size into a near-neutral complex, the remaining dominant corners carry
    the loop, and the complexes are dealt out evenly between them.
    """
    def net(feature):
        return sum(a for a, _ in feature[1]) * direction

    loop = [f for f in scaled if net(f) > 0]
    reverse = [f for f in scaled if net(f) <= 0]
    rng.shuffle(loop)
    rng.shuffle(reverse)
    complexes = []
    for rev in reverse:
        if not loop:
            complexes.append([rev])
            continue
        # The dominant partner closest in size to the reverse corner.
        i = min(range(len(loop)), key=lambda k: abs(net(loop[k]) + net(rev)))
        partner = loop.pop(i)
        complexes.append([rev, partner] if rng.random() < 0.5 else [partner, rev])
    rng.shuffle(complexes)
    units: List[List] = [[f] for f in loop] + complexes
    if not loop:
        return [f for c in units for f in c]
    # Deal the loop corners out at even intervals among the complexes so the
    # heading drifts round steadily instead of all the turning happening in
    # one part of the lap.
    total = len(units)
    slots = sorted(
        int(round((k + rng.uniform(0.25, 0.75)) * total / len(loop))) % total
        for k in range(len(loop))
    )
    ordered_units: List[Optional[List]] = [None] * total
    loop_units = [[f] for f in loop]
    for pos, unit in zip(slots, loop_units):
        while ordered_units[pos] is not None:
            pos = (pos + 1) % total
        ordered_units[pos] = unit
    fill = iter(complexes)
    for i in range(total):
        if ordered_units[i] is None:
            ordered_units[i] = next(fill)
    return [f for unit in ordered_units for f in unit]  # type: ignore[union-attr]


def _build_pieces(
    spec: LayoutSpec, rng: random.Random
) -> Optional[Tuple[List[_Piece], int]]:
    """Sample a feature sequence with the circuit's exact corner counts.

    Every corner in the source data is a real change of direction, so the
    layout contains exactly ``left_turns`` left-handers and ``right_turns``
    right-handers (or ``turns`` split two ways when the sides are unknown).
    Features draw their signs from those two pools until both are empty; a
    chicane needs one of each, esses two of one and one of the other.
    Corner radii follow the circuit's tightest corner rather than its length,
    and on a busy circuit corners run straight into one another, as on a real
    technical section, instead of always being separated by a straight.
    """
    weights = DISCIPLINE_WEIGHTS.get(
        spec.discipline.upper(), DISCIPLINE_WEIGHTS["SINGLE_SEATER"]
    )
    length = spec.length_m
    left, right = _corner_counts(spec, rng)
    if left + right < 3:
        return None
    direction = 1 if left >= right else -1
    pools = {1: left, -1: right}

    anchor = float(spec.tightest_corner_radius_m or 25.0)
    anchor = max(MIN_REAL_RADIUS, _display_radius_floor(length), min(anchor, 60.0))

    # With equal numbers of lefts and rights the lap can only close if the
    # dominant side turns through more per corner than the other, so on a
    # balanced circuit the dominant corners lean towards hairpins and slow
    # corners and the reverse ones towards sweepers and kinks.
    balanced = min(left, right) / max(left, right) >= 0.6
    tight = {k: v for k, v in weights.items() if k in ("hairpin", "slow", "carousel", "double_apex")}
    open_ = {k: v for k, v in weights.items() if k in ("sweeper", "kink", "medium", "esses")}

    corners: List[Tuple[str, List[Tuple[float, float]], List[str]]] = []
    while pools[1] + pools[-1] > 0:
        name = _pick_feature(rng, weights)
        if balanced and rng.random() < 0.6:
            name = _pick_feature(rng, tight if pools[direction] >= pools[-direction] else open_)
        pattern = FEATURE_SIGNS[name]
        options = []
        for lead in (1, -1):
            need = {1: 0, -1: 0}
            for sgn in pattern:
                need[sgn * lead] += 1
            if need[1] <= pools[1] and need[-1] <= pools[-1]:
                options.append(lead)
        if not options:
            # Nothing multi-corner fits what is left: spend a single corner.
            lead = 1 if pools[1] > 0 else -1
            name = "slow" if rng.random() < 0.6 else "medium"
            pattern = FEATURE_SIGNS[name]
            options = [lead]
        lead = rng.choice(options) if len(options) == 1 else (
            direction if rng.random() < 0.65 else -direction
        )
        if lead not in options:
            lead = options[0]
        _, (a_lo, a_hi), (r_lo, r_hi) = FEATURES[name]
        parts: List[Tuple[float, float]] = []
        r = anchor * rng.uniform(r_lo, r_hi)
        r = max(anchor * r_lo, min(FEATURE_MAX_RADIUS[name], r))
        for sgn in pattern:
            pools[sgn * lead] -= 1
            parts.append((sgn * lead * rng.uniform(a_lo, a_hi), r * rng.uniform(0.9, 1.1)))
        if name == "chicane":
            links = ["chicane"]
        elif name == "esses":
            links = ["esses"] * (len(pattern) - 1)
        elif name == "double_apex":
            links = ["apex"]
        else:
            links = []
        corners.append((name, parts, links))

    scaled = _scale_to_loop(corners, direction)
    if scaled is None:
        return None
    scaled = _order_around_lap(scaled, direction, rng)

    # Corners may take a larger share of a busy lap, but straights still need
    # room to close the loop: shrink the open corners towards the anchor when
    # the sampled set is too long for the lap.
    density = (left + right) / max(0.8, length / 1000.0)
    share = max(0.38, min(0.66, 0.30 + 0.045 * density))
    corner_total = sum(_corner_length(a, r) for _, ps, _ in scaled for a, r in ps)
    if corner_total > share * length:
        shrink = share * length / corner_total
        floor = max(MIN_REAL_RADIUS, _display_radius_floor(length))
        scaled = [
            (name, [(a, max(floor, r * shrink)) for a, r in ps], links)
            for name, ps, links in scaled
        ]
        corner_total = sum(_corner_length(a, r) for _, ps, _ in scaled for a, r in ps)
        if corner_total > 0.72 * length:
            return None

    # Dense circuits flow corner into corner; open ones keep a straight between.
    p_flow = max(0.0, min(0.5, (density - 3.0) / 8.0))

    pieces: List[_Piece] = [_Piece("S", role="main_a")]
    for idx, (name, ps, links) in enumerate(scaled):
        for j, (a, r) in enumerate(ps):
            pieces.append(_Piece("C", angle_deg=a, radius_m=r, feature=name))
            if j < len(links):
                pieces.append(_Piece("S", role=links[j]))
        if idx < len(scaled) - 1:
            if scaled[idx + 1][0] == "hairpin" and rng.random() < 0.5:
                pieces.append(_Piece("S", role="approach"))
            elif rng.random() >= p_flow:
                pieces.append(_Piece("S", role="link"))
    pieces.append(_Piece("S", role="main_b"))
    # Closure solves for straight lengths, so it needs a spread of them.
    wanted = max(3, len(scaled) // 4)
    for i in range(len(pieces) - 2, 1, -1):
        if sum(1 for p in pieces if p.kind == "S" and p.role in ("link", "approach")) >= wanted:
            break
        if pieces[i].kind == "C" and pieces[i - 1].kind == "C":
            pieces.insert(i, _Piece("S", role="link"))
    return pieces, direction


def _assign_straights(spec: LayoutSpec, pieces: List[_Piece], rng: random.Random) -> bool:
    length = spec.length_m
    corner_total = sum(
        _corner_length(p.angle_deg, p.radius_m) for p in pieces if p.kind == "C"
    )
    if corner_total > length * 0.78:
        shrink = length * 0.78 / corner_total
        for p in pieces:
            if p.kind == "C":
                p.radius_m *= shrink
        corner_total *= shrink
    budget = length - corner_total

    turns = sum(1 for p in pieces if p.kind == "C")
    density = turns / max(0.8, length / 1000.0)
    busy = max(0.0, min(1.0, (density - 3.0) / 3.0))
    main = spec.longest_straight_m or length * 0.16
    main = max(length * 0.07, min(length * (0.24 - 0.08 * busy), main))
    scale = length / 5000.0
    fixed = {"chicane": (12.0, 30.0), "esses": (10.0, 35.0), "apex": (15.0, 50.0)}
    links = [p for p in pieces if p.kind == "S" and p.role in ("link", "approach")]
    back = rng.sample(links, k=min(len(links), 1 if length < 3000 else 2))
    weights = []
    for p in pieces:
        if p.kind != "S":
            continue
        if p.role in fixed:
            lo, hi = fixed[p.role]
            p.length_m = rng.uniform(lo, hi) * max(0.4, scale)
        elif p.role == "main_a":
            p.length_m = main * 0.62
        elif p.role == "main_b":
            p.length_m = main * 0.38
        else:
            # Busy laps spread their straights evenly; open ones vary more and
            # carry a second long straight on the back of the circuit.
            w = rng.uniform(0.35 + 0.35 * busy, 1.0)
            if p.role == "approach":
                w += 0.6 - 0.3 * busy
            if p in back:
                w = rng.uniform(1.6 - 0.5 * busy, 2.4 - 0.9 * busy)
            weights.append((p, w))
    remaining = budget - sum(
        p.length_m for p in pieces if p.kind == "S" and p.length_m > 0
    )
    if remaining <= 0 or not weights:
        return False
    total_w = sum(w for _, w in weights)
    for p, w in weights:
        p.length_m = remaining * w / total_w
    return True


def _to_instructions(pieces: List[_Piece]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in pieces:
        if p.kind == "S":
            out.append({"type": "S", "length_m": int(round(max(1.0, p.length_m)))})
        else:
            instr = _corner_instruction(p.angle_deg, p.radius_m)
            instr["feature"] = p.feature
            out.append(instr)
    return out


def _straight_directions(instructions: List[Dict[str, Any]]) -> List[Tuple[int, float]]:
    """Return (instruction index, heading) for each straight."""
    theta = 0.0
    result = []
    for idx, instr in enumerate(instructions):
        if instr["type"] == "S":
            result.append((idx, theta))
        else:
            turn = _instruction_samples(instr)[2]
            theta += float(turn[-1]) if len(turn) else 0.0
    return result


def _close_loop(spec: LayoutSpec, pieces: List[_Piece], direction: int) -> Optional[List[Dict[str, Any]]]:
    """Fix heading on the last corner and solve straights for position and length."""
    instructions = _to_instructions(pieces)
    corner_idx = [i for i, ins in enumerate(instructions) if ins["type"] == "C"]
    widest = max(corner_idx, key=lambda i: instructions[i]["radius_m"])
    for _ in range(3):
        err = _end_state(instructions)[2] - 2 * math.pi * direction
        if abs(err) < math.radians(0.3):
            break
        new_angle = instructions[widest]["angle_deg"] - math.degrees(err)
        if new_angle * instructions[widest]["angle_deg"] <= 0 or abs(new_angle) > 180.0:
            return None  # the correction would reverse this corner or exceed a hairpin
        replacement = _corner_instruction(new_angle, instructions[widest]["radius_m"])
        replacement["feature"] = instructions[widest].get("feature", "")
        instructions[widest] = replacement

    unit = max(0.3, min(1.5, spec.length_m / 5000.0))
    turns = (spec.left_turns or 0) + (spec.right_turns or 0) or int(spec.turns or 12)
    density = turns / max(0.8, spec.length_m / 1000.0)
    # Busy circuits link corners with short straights; open ones with longer.
    link_unit = unit * max(0.3, min(1.0, 4.0 / max(density, 1e-6)))
    minimum = {
        "chicane": 6.0, "esses": 6.0, "apex": 8.0,
        "link": 25.0 * link_unit, "approach": 60.0 * link_unit,
        "main_a": 0.0, "main_b": 0.0,
    }
    straight_pieces = [p for p in pieces if p.kind == "S"]
    for p in straight_pieces:
        if p.role.startswith("main"):
            minimum[p.role] = p.length_m * 0.8
    dirs = _straight_directions(instructions)
    roles = [straight_pieces[n].role for n in range(len(dirs))]
    lower = np.array([minimum[r] for r in roles])
    main_total = sum(p.length_m for p in straight_pieces if p.role.startswith("main"))
    upper = np.array(
        [
            max(main_total * 0.75, 0.12 * spec.length_m) if r in ("link", "approach") else np.inf
            for r in roles
        ]
    )
    for _ in range(6):
        end_x, end_y, _, count = _end_state(instructions)
        gap = np.array([end_x, end_y])
        total = float(count)
        if np.hypot(*gap) < 1.0 and abs(total - spec.length_m) < 30.0:
            return instructions
        lengths = np.array([instructions[i]["length_m"] for i, _ in dirs], dtype=float)
        a_rows = np.array(
            [
                [math.cos(t) for _, t in dirs],
                [math.sin(t) for _, t in dirs],
                [1.0] * len(dirs),
            ]
        )
        b = np.array([-gap[0], -gap[1], spec.length_m - total])
        # Bounded least squares: closure rows dominate, regularisation keeps
        # each straight near its intended length.
        stiffness = np.array(
            [0.2 if r in ("link", "approach") else 3.0 for r in roles]
        )
        system = np.vstack([a_rows * 40.0, np.diag(stiffness)])
        rhs = np.concatenate([b * 40.0, np.zeros(len(dirs))])
        res = lsq_linear(
            system, rhs, bounds=(lower - lengths, np.maximum(upper - lengths, 1e-6)), method="bvls"
        )
        if res.status < 0:
            return None
        for n, (i, _) in enumerate(dirs):
            instructions[i]["length_m"] = int(round(lengths[n] + res.x[n]))
    end_x, end_y, _, _ = _end_state(instructions)
    return instructions if math.hypot(end_x, end_y) < 2.0 else None


def _validate(
    instructions: List[Dict[str, Any]], direction: int, one_sided: bool = False
) -> Optional[float]:
    """Return a quality score for a closed layout, or None if it is unusable."""
    pts = simulate(instructions)
    xy = pts[:, :2]
    width = float(np.ptp(xy[:, 0]))
    height = float(np.ptp(xy[:, 1]))
    if width <= 0 or height <= 0:
        return None
    scale = min(DISPLAY_WIDTH / width, DISPLAY_HEIGHT / height)
    radii = [ins["radius_m"] for ins in instructions if ins["type"] == "C"]
    if min(radii) * scale < MIN_DISPLAY_RADIUS:
        return None

    step = 4
    sample = xy[::step] * scale
    n = len(sample)
    s = np.arange(n) * step * scale
    total = len(xy) * scale
    # Only pairs closer than the larger clearance can fail either check.
    pairs = cKDTree(sample).query_pairs(MAIN_STRAIGHT_CLEARANCE, output_type="ndarray")
    if len(pairs):
        i, j = pairs[:, 0], pairs[:, 1]
        dist = np.linalg.norm(sample[i] - sample[j], axis=1)
        sep = np.abs(s[i] - s[j])
        sep = np.minimum(sep, total - sep)
        if np.any((sep > MIN_DISPLAY_CLEARANCE * 3.2) & (dist < MIN_DISPLAY_CLEARANCE)):
            return None
        main_mask = np.zeros(n, dtype=bool)
        main_mask[: int(instructions[0]["length_m"] / step)] = True
        main_mask[n - int(instructions[-1]["length_m"] / step):] = True
        on_main = main_mask[i] | main_mask[j]
        if np.any(on_main & (sep > MAIN_STRAIGHT_CLEARANCE * 3.2) & (dist < MAIN_STRAIGHT_CLEARANCE)):
            return None

    aspect = width / height
    signed_area = 0.5 * float(
        np.sum(xy[:-1, 0] * xy[1:, 1] - xy[1:, 0] * xy[:-1, 1])
    )
    if signed_area * direction <= 0:
        return None
    hull_area = float(ConvexHull(xy[::step]).volume)
    concavity = abs(signed_area) / max(1.0, hull_area)
    # Real road circuits fill 40-90% of their hull; a lap with no corners the
    # other way (an oval or tri-oval) is convex by nature and allowed to be.
    if concavity > (1.01 if one_sided else 0.9) or concavity < 0.4:
        return None
    return -abs(concavity - 0.68) - 0.25 * abs(math.log(aspect / 1.43))


def _search(spec: LayoutSpec, candidates: int) -> Optional[List[Dict[str, Any]]]:
    rng = random.Random(spec.seed)
    best: Optional[List[Dict[str, Any]]] = None
    best_score = -math.inf
    found = 0
    for _ in range(MAX_ATTEMPTS):
        built = _build_pieces(spec, rng)
        if built is None:
            continue
        pieces, direction = built
        if not _assign_straights(spec, pieces, rng):
            continue
        instructions = _close_loop(spec, pieces, direction)
        if instructions is None:
            continue
        one_sided = (spec.left_turns or 0) + (spec.right_turns or 0) > 0 and (
            not spec.left_turns or not spec.right_turns
        )
        score = _validate(instructions, direction, one_sided=one_sided)
        if score is None:
            continue
        found += 1
        if score > best_score:
            best, best_score = instructions, score
        if found >= candidates:
            break
    return best


def generate_layout(spec: LayoutSpec, candidates: int = 6) -> List[Dict[str, Any]]:
    """Build a closed, non-overlapping layout and return dict instructions.

    The layout carries the circuit's exact corner counts. Only if repeated
    searches with fresh seeds find nothing are the counts trimmed, a few at a
    time, so every circuit still receives a valid layout.
    """
    for tier in range(6):
        trim = max(0, tier - 2)
        left = spec.left_turns or 0
        right = spec.right_turns or 0
        relaxed = replace(
            spec,
            turns=max(4, int(spec.turns or 12) - 2 * trim),
            left_turns=(max(1, left - trim) if left else 0) if left + right else None,
            right_turns=(max(1, right - trim) if right else 0) if left + right else None,
            seed=spec.seed + tier * 7919,
        )
        best = _search(relaxed, candidates)
        if best is not None:
            return best
    raise RuntimeError(f"No valid circuit layout found for seed {spec.seed}")
