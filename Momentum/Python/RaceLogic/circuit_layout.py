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
MIN_DISPLAY_RADIUS = 20.0
MIN_DISPLAY_CLEARANCE = 46.0
MAIN_STRAIGHT_CLEARANCE = 92.0
MAX_ATTEMPTS = 400

# name: (turn_count, angle range deg, radius range as multiple of base radius)
FEATURES: Dict[str, Tuple[int, Tuple[float, float], Tuple[float, float]]] = {
    "hairpin": (1, (150.0, 180.0), (1.0, 1.4)),
    "slow": (1, (75.0, 105.0), (1.3, 2.2)),
    "medium": (1, (45.0, 75.0), (2.0, 3.4)),
    "sweeper": (1, (35.0, 70.0), (4.0, 7.5)),
    "kink": (1, (12.0, 24.0), (8.0, 13.0)),
    "carousel": (1, (110.0, 145.0), (2.6, 3.8)),
    "chicane": (2, (40.0, 65.0), (1.0, 1.5)),
    "esses": (3, (32.0, 58.0), (1.9, 2.9)),
    "double_apex": (2, (45.0, 75.0), (1.5, 2.4)),
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


def _build_pieces(
    spec: LayoutSpec, rng: random.Random
) -> Optional[Tuple[List[_Piece], int]]:
    """Sample a feature sequence whose net turning is one full loop."""
    weights = DISCIPLINE_WEIGHTS.get(
        spec.discipline.upper(), DISCIPLINE_WEIGHTS["SINGLE_SEATER"]
    )
    length = spec.length_m
    short = length < 2200.0
    target_turns = max(5 if short else 7, min(20, int(spec.turns or 12)))

    left = spec.left_turns or 0
    right = spec.right_turns or 0
    if left + right > 0:
        direction = 1 if left >= right else -1
        dominant_share = max(left, right) / float(left + right)
    else:
        direction = rng.choice((1, -1))
        dominant_share = 0.65
    dominant_share = max(0.58, min(0.8, dominant_share))

    base_radius = max(12.0, 0.0085 * length)
    if spec.tightest_corner_radius_m:
        base_radius = max(
            base_radius, min(spec.tightest_corner_radius_m, 1.3 * base_radius)
        )

    corners: List[Tuple[str, List[Tuple[float, float]], List[str]]] = []
    count = 0
    while count < target_turns:
        name = _pick_feature(rng, weights)
        n_turns, (a_lo, a_hi), (r_lo, r_hi) = FEATURES[name]
        sign = direction if rng.random() < dominant_share else -direction
        parts: List[Tuple[float, float]] = []
        links: List[str] = []
        if name == "chicane":
            a = rng.uniform(a_lo, a_hi)
            r = base_radius * rng.uniform(r_lo, r_hi)
            parts = [(sign * a, r), (-sign * a * rng.uniform(0.9, 1.1), r)]
            links = ["chicane"]
        elif name == "esses":
            parts = []
            s = sign
            for _ in range(n_turns):
                parts.append(
                    (s * rng.uniform(a_lo, a_hi), base_radius * rng.uniform(r_lo, r_hi))
                )
                s = -s
            links = ["esses"] * (n_turns - 1)
        elif name == "double_apex":
            r = base_radius * rng.uniform(r_lo, r_hi)
            parts = [
                (sign * rng.uniform(a_lo, a_hi), r),
                (sign * rng.uniform(a_lo, a_hi), r * rng.uniform(0.85, 1.15)),
            ]
            links = ["apex"]
        else:
            parts = [(sign * rng.uniform(a_lo, a_hi), base_radius * rng.uniform(r_lo, r_hi))]
        corners.append((name, parts, links))
        count += n_turns

    # Flip single corners until the dominant direction can be scaled to 360 degrees.
    factor = 0.0
    for _ in range(len(corners) + 1):
        dominant = sum(a for _, ps, _ in corners for a, _ in ps if a * direction > 0)
        reverse = sum(a for _, ps, _ in corners for a, _ in ps if a * direction < 0)
        if abs(dominant) < 1e-6:
            return None
        factor = (360.0 * direction - reverse) / dominant
        if 0.75 <= factor <= 1.3:
            break
        want_sign = -direction if factor < 0.75 else direction
        singles = [
            i
            for i, (_, ps, _) in enumerate(corners)
            if len(ps) == 1 and ps[0][0] * want_sign < 0
        ]
        if not singles:
            return None
        i = rng.choice(singles)
        name, ps, links = corners[i]
        corners[i] = (name, [(-ps[0][0], ps[0][1])], links)
    if not 0.75 <= factor <= 1.3:
        return None
    scaled = []
    for name, ps, links in corners:
        new_ps = []
        for a, r in ps:
            if a * direction > 0:
                a *= factor
                if abs(a) > 190.0:
                    return None
            new_ps.append((a, r))
        scaled.append((name, new_ps, links))
    rng.shuffle(scaled)

    pieces: List[_Piece] = [_Piece("S", role="main_a")]
    for idx, (name, ps, links) in enumerate(scaled):
        for j, (a, r) in enumerate(ps):
            pieces.append(_Piece("C", angle_deg=a, radius_m=r, feature=name))
            if j < len(links):
                pieces.append(_Piece("S", role=links[j]))
        if idx < len(scaled) - 1:
            role = "approach" if scaled[idx + 1][0] == "hairpin" else "link"
            pieces.append(_Piece("S", role=role))
    pieces.append(_Piece("S", role="main_b"))
    return pieces, direction


def _assign_straights(spec: LayoutSpec, pieces: List[_Piece], rng: random.Random) -> bool:
    length = spec.length_m
    corner_total = sum(
        _corner_length(p.angle_deg, p.radius_m) for p in pieces if p.kind == "C"
    )
    if corner_total > length * 0.62:
        shrink = length * 0.62 / corner_total
        for p in pieces:
            if p.kind == "C":
                p.radius_m *= shrink
        corner_total *= shrink
    budget = length - corner_total

    main = spec.longest_straight_m or length * 0.16
    main = max(length * 0.1, min(length * 0.24, main))
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
            p.length_m = rng.uniform(lo, hi) * max(0.5, scale)
        elif p.role == "main_a":
            p.length_m = main * 0.62
        elif p.role == "main_b":
            p.length_m = main * 0.38
        else:
            w = rng.uniform(0.35, 1.0)
            if p.role == "approach":
                w += 0.6
            if p in back:
                w = rng.uniform(1.6, 2.4)
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
        replacement = _corner_instruction(new_angle, instructions[widest]["radius_m"])
        replacement["feature"] = instructions[widest].get("feature", "")
        instructions[widest] = replacement

    unit = max(0.3, min(1.5, spec.length_m / 5000.0))
    minimum = {
        "chicane": 6.0, "esses": 6.0, "apex": 8.0,
        "link": 25.0 * unit, "approach": 60.0 * unit,
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
        [main_total * 0.75 if r in ("link", "approach") else np.inf for r in roles]
    )
    for _ in range(4):
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
    instructions: List[Dict[str, Any]], direction: int
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
    if concavity > 0.9 or concavity < 0.4:
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
        score = _validate(instructions, direction)
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

    If no layout satisfies the constraints, the corner count is relaxed in
    steps so every circuit still receives a valid layout.
    """
    for tier in range(5):
        relaxed = replace(
            spec,
            turns=max(5, int(spec.turns or 12) - 2 * tier),
            seed=spec.seed + tier * 7919,
        )
        best = _search(relaxed, candidates)
        if best is not None:
            return best
    raise RuntimeError(f"No valid circuit layout found for seed {spec.seed}")
