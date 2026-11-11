"""Where drivers and teams come from, per discipline.

Motorsport is not evenly spread across the world. Single-seaters grew up in
Britain, Italy and France; rallycross is Scandinavian at heart; drifting is
Japanese and Irish; drag racing is American. The weights below lean towards
those heartlands without copying reality exactly: every country in
``data.countries`` keeps a floor weight, so smaller nations appear more often
than they do in real grids while the big names still dominate.
"""

from __future__ import annotations

import random
from typing import Dict, Iterable, List, Optional

from momentum.data.countries import COUNTRIES

# Weight given to every country not named for a discipline. Raising it flattens
# the world; lowering it makes the heartlands more dominant.
BASE_WEIGHT = 0.6

# Codes are ISO 3166-1 alpha-3. Weights are relative within a discipline.
DISCIPLINE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "SINGLE_SEATER": {
        "GBR": 30, "ITA": 22, "FRA": 20, "DEU": 16, "BRA": 12, "ESP": 10,
        "NLD": 9, "FIN": 8, "AUS": 8, "JPN": 8, "USA": 8, "AUT": 6, "BEL": 6,
        "CHE": 5, "MCO": 5, "CAN": 5, "MEX": 5, "ARG": 5, "DNK": 4, "SWE": 4,
        "NZL": 4, "IRL": 4, "RUS": 3, "POL": 3, "CHN": 3, "IND": 3, "ZAF": 3,
        "COL": 3, "THA": 2, "PRT": 2, "CZE": 2, "HUN": 2, "ISR": 2,
    },
    "PRODUCTION_TOURING": {
        "GBR": 28, "DEU": 24, "AUS": 18, "SWE": 12, "BEL": 10, "ITA": 10,
        "FRA": 10, "NLD": 8, "ESP": 6, "ARG": 6, "BRA": 6, "JPN": 6, "USA": 6,
        "NZL": 5, "ZAF": 5, "CHE": 4, "AUT": 4, "DNK": 4, "PRT": 4, "HUN": 3,
        "CZE": 3, "CHN": 3, "MAR": 3, "URY": 2, "NOR": 2, "IRL": 2, "TUR": 2,
    },
    "URBAN_STREET": {
        "JPN": 30, "IRL": 22, "GBR": 18, "USA": 16, "POL": 10, "NZL": 9,
        "AUS": 7, "NOR": 6, "RUS": 6, "THA": 5, "LVA": 4, "LTU": 4, "FIN": 4,
        "DEU": 4, "FRA": 4, "ITA": 4, "HUN": 3, "GRC": 3, "ARE": 3, "SAU": 3,
        "MYS": 3, "IDN": 3, "PHL": 2, "ZAF": 2, "CAN": 2, "ESP": 2, "TUR": 2,
    },
    "DRAG_ACCELERATION": {
        "USA": 45, "AUS": 14, "GBR": 10, "SWE": 8, "CAN": 8, "NZL": 5,
        "DEU": 5, "FIN": 4, "NOR": 4, "NLD": 3, "ZAF": 3, "BRA": 3, "MEX": 3,
        "ARE": 3, "QAT": 3, "BHR": 2, "ITA": 2, "DNK": 2, "JPN": 2, "PRI": 2,
    },
    "SPRINT_RALLYCROSS": {
        "SWE": 28, "NOR": 24, "FIN": 18, "FRA": 14, "GBR": 12, "LVA": 8,
        "USA": 8, "DEU": 6, "BEL": 5, "AUT": 4, "HUN": 4, "DNK": 4, "ESP": 4,
        "PRT": 4, "ZAF": 3, "CZE": 3, "POL": 3, "LTU": 3, "EST": 3, "IRL": 3,
        "CAN": 2, "ITA": 2, "NLD": 2, "RUS": 2, "ARG": 2, "BRB": 2,
    },
    "ENDURANCE": {
        "FRA": 28, "GBR": 24, "DEU": 20, "JPN": 14, "USA": 14, "ITA": 10,
        "PRT": 8, "CHE": 6, "BEL": 6, "NLD": 5, "DNK": 5, "AUT": 4, "ESP": 4,
        "BRA": 4, "AUS": 4, "MCO": 3, "SWE": 3, "ARG": 3, "MEX": 3, "CAN": 3,
        "POL": 3, "CHN": 3, "MYS": 2, "THA": 2, "SGP": 2, "ZAF": 2, "IRL": 2,
    },
}


def nationality_weights(
    discipline: str, codes: Optional[Iterable[str]] = None
) -> Dict[str, float]:
    """Weight for every country code, with the discipline's heartlands on top."""
    pool: List[str] = list(codes) if codes is not None else list(COUNTRIES.keys())
    heartlands = DISCIPLINE_WEIGHTS.get(str(discipline or "").upper(), {})
    return {code: BASE_WEIGHT + heartlands.get(code, 0.0) for code in pool}


def choose_nationality(
    rng: random.Random, discipline: str, codes: Optional[Iterable[str]] = None
) -> str:
    """Pick one country for a driver or team in ``discipline``."""
    weights = nationality_weights(discipline, codes)
    population = list(weights.keys())
    return rng.choices(population, weights=[weights[c] for c in population], k=1)[0]


__all__ = [
    "BASE_WEIGHT",
    "DISCIPLINE_WEIGHTS",
    "choose_nationality",
    "nationality_weights",
]
