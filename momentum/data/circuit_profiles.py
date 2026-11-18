"""Realistic ranges for each discipline's circuits.

``momentum.data.circuit_schema`` checks every shipped circuit against the
profile of its discipline, so a record that does not look like its sport (a
rallycross lap built round a long straight, say) stops the seed build.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

Range = Tuple[float, float]


@dataclass(frozen=True)
class DisciplineProfile:
    ranges: Dict[str, Range] = field(default_factory=dict)
    turns: Range = (0, 0)
    max_straight_share: float = 1.0  # longest straight as a share of the lap
    # Words a circuit of this discipline is called by ("Grand Prix Circuit",
    # "Dragway"). A name must carry one of them, and the most specific form it
    # carries must belong to its own discipline, so an "Endurance Circuit"
    # cannot sit in the single-seater list.
    name_forms: Tuple[str, ...] = ()


PROFILES: Dict[str, DisciplineProfile] = {
    "SINGLE_SEATER": DisciplineProfile(
        ranges={
            "length_km": (3.5, 7.5),
            "tightest_corner_radius_m": (30.0, 90.0),
            "avg_speed_kmh": (180.0, 240.0),
            "drs_zones": (1, 3),
        },
        turns=(10, 24),
        max_straight_share=0.45,
        name_forms=(
            "Grand Prix Circuit",
            "International Circuit",
            "Autodrome",
            "Autodromo",
            "Autódromo",
        ),
    ),
    "ENDURANCE": DisciplineProfile(
        ranges={
            "length_km": (6.0, 14.0),
            "tightest_corner_radius_m": (25.0, 75.0),
            "avg_speed_kmh": (170.0, 230.0),
            "drs_zones": (0, 5),
        },
        turns=(18, 42),
        max_straight_share=0.40,
        name_forms=("Endurance Circuit", "Road Course", "Motorsport Park"),
    ),
    "PRODUCTION_TOURING": DisciplineProfile(
        ranges={
            "length_km": (3.0, 6.0),
            "tightest_corner_radius_m": (25.0, 70.0),
            "avg_speed_kmh": (150.0, 200.0),
        },
        turns=(9, 22),
        max_straight_share=0.40,
        # "Ring" also as a suffix glued to the place, as in Zeelandring.
        name_forms=("Ring", r"\w+ring", "Raceway", "Rennstrecke"),
    ),
    "URBAN_STREET": DisciplineProfile(
        ranges={
            "length_km": (2.5, 6.0),
            "tightest_corner_radius_m": (15.0, 55.0),
            "avg_speed_kmh": (150.0, 210.0),
        },
        turns=(12, 30),
        max_straight_share=0.40,
        name_forms=("Street Circuit", "City Circuit", "Harbour Circuit", "Corso"),
    ),
    # Short, tight and technical: the racing is in the corners, the surface
    # changes and the joker, not on the straights.
    "SPRINT_RALLYCROSS": DisciplineProfile(
        ranges={
            "length_km": (0.8, 1.4),
            "tightest_corner_radius_m": (12.0, 35.0),
            "avg_speed_kmh": (85.0, 145.0),
        },
        turns=(8, 18),
        max_straight_share=0.25,
        name_forms=("Arena", "Rally Stage", "Rallycross Circuit", "Motor Stadium"),
    ),
    "DRAG_ACCELERATION": DisciplineProfile(
        ranges={
            "shutdown_m": (300.0, 1600.0),
            "avg_speed_kmh": (240.0, 330.0),
        },
        name_forms=("Dragway", "Drag Strip", "Dragstrip", "Raceway Park"),
    ),
}


def _form_pattern(form: str) -> "re.Pattern[str]":
    body = form if form.startswith("\\w") else re.escape(form)
    return re.compile(rf"(?<!\w){body}(?!\w)", re.IGNORECASE)


_FORM_PATTERNS = tuple(
    (key, _form_pattern(form))
    for key, profile in PROFILES.items()
    for form in profile.name_forms
)


def name_discipline(name: str) -> Optional[str]:
    """The discipline a circuit name reads as, from its most specific form.

    "Oldgate Endurance Circuit" reads as endurance even though it also ends in
    "Circuit"; "Englishtown Raceway Park" reads as a drag strip, not a raceway.
    ``None`` when the name carries no form at all.
    """
    best: Optional[Tuple[int, str]] = None
    for key, pattern in _FORM_PATTERNS:
        match = pattern.search(name)
        if match and (best is None or match.end() - match.start() > best[0]):
            best = (match.end() - match.start(), key)
    return best[1] if best else None

