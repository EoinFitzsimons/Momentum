"""
Driver attribute utilities for the real-time racing prototype.

These helpers aggregate the rich 50+ driver attributes into a few
high-level signals (bravery, patience, aggression, etc.) that the
race/physics engines consume. Values are clamped to the canonical
0-100 range defined in `config.py` and tolerate missing fields so the
GUI demo can run on partial driver data.
"""
from typing import Any

from config import (
    DRIVER_ATTRIBUTE_DEFAULT,
    DRIVER_ATTRIBUTE_MAX,
    DRIVER_ATTRIBUTE_MIN,
)


def _clamp(value: float, min_val: float = DRIVER_ATTRIBUTE_MIN,
           max_val: float = DRIVER_ATTRIBUTE_MAX) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return float(DRIVER_ATTRIBUTE_DEFAULT)
    return max(min_val, min(max_val, v))


def get_safe_attribute(driver: Any, attr: str,
                       default: float = DRIVER_ATTRIBUTE_DEFAULT) -> float:
    """Safely read a driver attribute and clamp to 0-100."""
    if driver is None:
        return float(default)
    value = getattr(driver, attr, default)
    if value is None:
        value = default
    return _clamp(value)


def _avg(values: list[float],
         fallback: float = DRIVER_ATTRIBUTE_DEFAULT) -> float:
    cleaned = [v for v in values if v is not None]
    if not cleaned:
        return float(fallback)
    return sum(cleaned) / len(cleaned)


def get_driver_bravery(driver: Any) -> float:
    """Risk-taking courage in high-speed, high-G situations."""
    return _clamp(
        0.22 * get_safe_attribute(driver, "raw_speed")
        + 0.18 * get_safe_attribute(driver, "g_force_tolerance")
        + 0.18 * get_safe_attribute(driver, "adrenaline_management")
        + 0.16 * get_safe_attribute(driver, "overtaking")
        + 0.16 * get_safe_attribute(driver, "pressure_handling")
        + 0.10 * get_safe_attribute(driver, "defensive_driving")
    )


def get_driver_patience(driver: Any) -> float:
    """Willingness to wait for the right moment rather than force moves."""
    return _clamp(
        0.28 * get_safe_attribute(driver, "mental_resilience")
        + 0.22 * get_safe_attribute(driver, "concentration")
        + 0.18 * get_safe_attribute(driver, "professionalism")
        + 0.16 * get_safe_attribute(driver, "pressure_handling")
        + 0.16 * get_safe_attribute(driver, "racecraft")
    )


def get_driver_aggression(driver: Any) -> float:
    """How forcefully a driver attacks and defends in close combat."""
    return _clamp(
        0.24 * get_safe_attribute(driver, "overtaking")
        + 0.20 * get_safe_attribute(driver, "defensive_driving")
        + 0.18 * get_safe_attribute(driver, "acceleration_control")
        + 0.16 * get_safe_attribute(driver, "reaction_time")
        + 0.12 * get_safe_attribute(driver, "adrenaline_management")
        + 0.10 * get_safe_attribute(driver, "raw_speed")
    )


def get_driver_wheel_to_wheel_ability(driver: Any) -> float:
    """Side-by-side craft: spatial judgment plus car control under pressure."""
    return _clamp(
        0.24 * get_safe_attribute(driver, "spatial_awareness")
        + 0.22 * get_safe_attribute(driver, "vehicle_control")
        + 0.18 * get_safe_attribute(driver, "reaction_time")
        + 0.16 * get_safe_attribute(driver, "defensive_driving")
        + 0.12 * get_safe_attribute(driver, "overtaking")
        + 0.08 * get_safe_attribute(driver, "pressure_handling")
    )


def _form_trend_bonus(trend: str | None) -> float:
    if not trend:
        return 0.0
    trend = trend.lower()
    if trend in ("improving", "peak"):
        return 8.0
    if trend == "stable":
        return 2.0
    if trend == "declining":
        return -6.0
    return 0.0


def get_driver_confidence(driver: Any) -> float:
    """Confidence built from pace, composure, and career results."""
    base = _avg(
        [
            get_safe_attribute(driver, "raw_speed"),
            get_safe_attribute(driver, "racecraft"),
            get_safe_attribute(driver, "consistency"),
            get_safe_attribute(driver, "pressure_handling"),
            get_safe_attribute(driver, "professionalism"),
        ]
    )

    wins = get_safe_attribute(driver, "career_wins", 0.0)
    podiums = get_safe_attribute(driver, "career_podiums", 0.0)
    starts = max(get_safe_attribute(driver, "career_starts", 1.0), 1.0)
    experience_boost = min((wins * 1.5 + podiums) /
                           max(starts, 1.0) * 100.0, 12.0)

    trend_boost = _form_trend_bonus(getattr(driver, "form_trend", None))

    confidence = base + experience_boost + trend_boost
    return _clamp(confidence)
