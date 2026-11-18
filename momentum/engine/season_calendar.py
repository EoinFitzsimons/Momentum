"""Designed race calendars.

A season is not the track table read top to bottom with a race every
fortnight. It has a fixed number of rounds set by the discipline's
``RaceFormat``, it travels region by region so the paddock is not crossing
the world between consecutive rounds, and it runs from early March to late
November with a summer break in August. Championship mode and career mode
both build their calendars here so the two agree.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from momentum.engine.race_format import race_format_for

# The order the season visits the regions: Gulf and Asia-Pacific flyaways to
# open, Europe through the summer, then Africa and the Americas for the run-in.
REGION_TOUR = ("Middle East", "Asia-Pacific", "Europe", "Africa", "Americas")
OTHER_REGION = "Rest of World"

REGION_OF_COUNTRY: Dict[str, str] = {
    "Bahrain": "Middle East",
    "Qatar": "Middle East",
    "Saudi Arabia": "Middle East",
    "United Arab Emirates": "Middle East",
    "Kuwait": "Middle East",
    "Oman": "Middle East",
    "Turkey": "Middle East",
    "Australia": "Asia-Pacific",
    "China": "Asia-Pacific",
    "India": "Asia-Pacific",
    "Indonesia": "Asia-Pacific",
    "Japan": "Asia-Pacific",
    "Malaysia": "Asia-Pacific",
    "New Zealand": "Asia-Pacific",
    "Singapore": "Asia-Pacific",
    "South Korea": "Asia-Pacific",
    "Thailand": "Asia-Pacific",
    "Vietnam": "Asia-Pacific",
    "Austria": "Europe",
    "Belgium": "Europe",
    "Czech Republic": "Europe",
    "Denmark": "Europe",
    "Finland": "Europe",
    "France": "Europe",
    "Germany": "Europe",
    "Hungary": "Europe",
    "Ireland": "Europe",
    "Italy": "Europe",
    "Monaco": "Europe",
    "Netherlands": "Europe",
    "Norway": "Europe",
    "Poland": "Europe",
    "Portugal": "Europe",
    "Spain": "Europe",
    "Sweden": "Europe",
    "Switzerland": "Europe",
    "United Kingdom": "Europe",
    "Egypt": "Africa",
    "Kenya": "Africa",
    "Morocco": "Africa",
    "Nigeria": "Africa",
    "South Africa": "Africa",
    "Argentina": "Americas",
    "Brazil": "Americas",
    "Canada": "Americas",
    "Chile": "Americas",
    "Colombia": "Americas",
    "Mexico": "Americas",
    "United States": "Americas",
}

SEASON_OPENS = (3, 1)  # first Sunday on or after 1 March
SEASON_CLOSES = (11, 30)
SUMMER_BREAK = ((8, 1), (8, 21))


def region_of(country: Optional[str]) -> str:
    return REGION_OF_COUNTRY.get(str(country or "").strip(), OTHER_REGION)


def _tour_index(region: str) -> int:
    return REGION_TOUR.index(region) if region in REGION_TOUR else len(REGION_TOUR)


def _track_sort_key(track: Any):
    return (str(getattr(track, "country", "") or ""), str(getattr(track, "name", "") or ""))


def plan_season(tracks: Sequence[Any], rounds: int) -> List[Any]:
    """Choose and order ``rounds`` circuits so the season travels region by region.

    When more circuits are available than rounds, the regions are drawn from
    in turn so every part of the world is visited; when fewer, the tour is
    repeated. Within a region the order runs by country, so neighbouring
    rounds share a corner of the map.
    """
    rounds = max(0, int(rounds))
    if rounds == 0 or not tracks:
        return []
    by_region: Dict[str, List[Any]] = {}
    for track in sorted(tracks, key=_track_sort_key):
        by_region.setdefault(region_of(getattr(track, "country", None)), []).append(track)
    regions = sorted(by_region, key=lambda r: (_tour_index(r), r))

    if len(tracks) > rounds:
        quota = {r: 0 for r in regions}
        taken = 0
        while taken < rounds:
            for region in regions:
                if taken == rounds:
                    break
                if quota[region] < len(by_region[region]):
                    quota[region] += 1
                    taken += 1
        chosen = [t for r in regions for t in by_region[r][: quota[r]]]
    else:
        chosen = [t for r in regions for t in by_region[r]]

    calendar = list(chosen)
    while len(calendar) < rounds:
        calendar.extend(chosen)
    return calendar[:rounds]


def season_year(start: datetime) -> int:
    """The year of the first season whose opening round falls on or after ``start``."""
    opening = _season_sundays(start.year)[0]
    return start.year if start.date() <= opening.date() else start.year + 1


def _season_sundays(year: int) -> List[datetime]:
    day = datetime(year, *SEASON_OPENS)
    day += timedelta(days=(6 - day.weekday()) % 7)
    close = datetime(year, *SEASON_CLOSES)
    break_start = datetime(year, *SUMMER_BREAK[0])
    break_end = datetime(year, *SUMMER_BREAK[1])
    sundays = []
    while day <= close:
        if not break_start <= day <= break_end:
            sundays.append(day)
        day += timedelta(days=7)
    return sundays


def season_dates(rounds: int, start: datetime) -> List[datetime]:
    """Sundays for ``rounds`` races, spread evenly from March to November
    around the August break. A season longer than the window runs weekly."""
    rounds = max(0, int(rounds))
    if rounds == 0:
        return []
    sundays = _season_sundays(season_year(start))
    if rounds > len(sundays):
        first = sundays[0]
        return [first + timedelta(days=7 * i) for i in range(rounds)]
    if rounds == 1:
        return [sundays[0]]
    span = len(sundays) - 1
    return [sundays[round(i * span / (rounds - 1))] for i in range(rounds)]


@dataclass(frozen=True)
class CalendarRound:
    round_number: int
    track: Any
    date: datetime


def plan_calendar(
    tracks: Sequence[Any],
    discipline: str,
    start: datetime,
    rounds: Optional[int] = None,
) -> List[CalendarRound]:
    """The designed season for a discipline: rounds from its ``RaceFormat``,
    circuits in touring order, dates on the season's Sundays."""
    count = int(rounds) if rounds is not None else race_format_for(discipline).season_rounds
    ordered = plan_season(tracks, count)
    dates = season_dates(len(ordered), start)
    return [
        CalendarRound(i + 1, track, when)
        for i, (track, when) in enumerate(zip(ordered, dates))
    ]
