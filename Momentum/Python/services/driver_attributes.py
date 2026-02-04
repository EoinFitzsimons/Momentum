"""
Driver attribute utilities for the real-time racing prototype.

These helpers aggregate the canonical driver attributes (see
`database.models.Driver`) into a few high-level signals (bravery,
patience, aggression, wheel-to-wheel, confidence) consumed by the
race/physics engines. Only attributes from the canonical schema are
used: `speed`, `racecraft`, `consistency`, `fitness`, `reactions`,
`pressure`, `setup_knowledge`, `fuel_management`, `tyre_management`,
`feedback`, `adaptability` and the career fields (`career_points`,
`career_podiums`, `career_starts`).
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
	"""Safely read a driver attribute and clamp to canonical range."""
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
	"""Risk-taking courage in high-speed, high-G situations.

	Uses only canonical attributes.
	"""
	return _clamp(
		0.30 * get_safe_attribute(driver, "speed")
		+ 0.20 * get_safe_attribute(driver, "fitness")
		+ 0.15 * get_safe_attribute(driver, "reactions")
		+ 0.15 * get_safe_attribute(driver, "racecraft")
		+ 0.10 * get_safe_attribute(driver, "pressure")
		+ 0.10 * get_safe_attribute(driver, "adaptability")
	)


def get_driver_patience(driver: Any) -> float:
	"""Willingness to wait for the right moment rather than force moves."""
	return _clamp(
		0.30 * get_safe_attribute(driver, "consistency")
		+ 0.25 * get_safe_attribute(driver, "pressure")
		+ 0.20 * _professionalism(driver)
		+ 0.15 * get_safe_attribute(driver, "feedback")
		+ 0.10 * get_safe_attribute(driver, "racecraft")
	)


def get_driver_aggression(driver: Any) -> float:
	"""How forcefully a driver attacks and defends in close combat."""
	return _clamp(
		0.28 * get_safe_attribute(driver, "racecraft")
		+ 0.22 * _vehicle_control(driver)
		+ 0.18 * get_safe_attribute(driver, "reactions")
		+ 0.12 * get_safe_attribute(driver, "speed")
		+ 0.10 * get_safe_attribute(driver, "pressure")
		+ 0.10 * get_safe_attribute(driver, "adaptability")
	)


def get_driver_wheel_to_wheel_ability(driver: Any) -> float:
	"""Side-by-side craft: spatial judgment plus car control under pressure."""
	return _clamp(
		0.28 * get_safe_attribute(driver, "consistency")
		+ 0.24 * _vehicle_control(driver)
		+ 0.20 * get_safe_attribute(driver, "reactions")
		+ 0.14 * get_safe_attribute(driver, "racecraft")
		+ 0.14 * get_safe_attribute(driver, "pressure")
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
			get_safe_attribute(driver, "speed"),
			get_safe_attribute(driver, "racecraft"),
			get_safe_attribute(driver, "consistency"),
			get_safe_attribute(driver, "pressure"),
			_professionalism(driver),
		]
	)

	# Use canonical career fields available in the schema
	wins = get_safe_attribute(driver, "career_points", 0.0)
	podiums = get_safe_attribute(driver, "career_podiums", 0.0)
	starts = max(get_safe_attribute(driver, "career_starts", 1.0), 1.0)
	experience_boost = min((wins * 1.5 + podiums) / max(starts, 1.0) * 100.0, 12.0)

	trend_boost = _form_trend_bonus(getattr(driver, "form_trend", None))

	confidence = base + experience_boost + trend_boost
	return _clamp(confidence)


# --- Helpers mapping directly to canonical attributes ---
def _speed(driver: Any) -> float:
	return get_safe_attribute(driver, "speed")


def _vehicle_control(driver: Any) -> float:
	# Compute vehicle control from canonical technical attributes.
	v = _avg([
		get_safe_attribute(driver, "setup_knowledge"),
		get_safe_attribute(driver, "tyre_management"),
	])
	return _clamp(v)


def _defensive_driving(driver: Any) -> float:
	# Defensive driving maps to the persisted `racecraft` attribute now.
	return get_safe_attribute(driver, "racecraft")


def _cornering_skill(driver: Any) -> float:
	# Cornering is derived from consistency and vehicle control.
	return _clamp(0.95 * get_safe_attribute(driver, "consistency") + 0.05 * _vehicle_control(driver))


def _professionalism(driver: Any) -> float:
	# Compute a professionalism-like social signal from canonical
	# attributes: feedback, adaptability and racecraft.
	return _clamp(
		0.4 * get_safe_attribute(driver, "feedback")
		+ 0.3 * get_safe_attribute(driver, "adaptability")
		+ 0.3 * get_safe_attribute(driver, "racecraft")
	)


def get_driver_professionalism(driver: Any) -> float:
	"""Public helper exposing professionalism-like social signal (0-100)."""
	return _professionalism(driver)


def get_vehicle_control(driver: Any) -> float:
	"""Public helper returning vehicle control (0-100) derived from canonical attrs."""
	return _vehicle_control(driver)


def get_cornering_skill(driver: Any) -> float:
	"""Public helper returning cornering skill (0-100) derived from canonical attrs."""
	return _cornering_skill(driver)


def get_driver_skill(driver: Any) -> float:
	"""Return the most appropriate single-number skill for UI display.
	Compute a single-number skill for UI display as the average of the
	primary racing attributes. This avoids over-weighting a single field
	such as `speed` and provides a more representative summary.
	"""
	if driver is None:
		return float(DRIVER_ATTRIBUTE_DEFAULT)

	# Primary attributes to include in the UI skill summary
	attrs = [
		'speed',
		'racecraft',
		'consistency',
		'reactions',
		'setup_knowledge',
		'tyre_management',
		'fuel_management',
	]

	vals = [get_safe_attribute(driver, a) for a in attrs]
	return float(_clamp(_avg(vals, DRIVER_ATTRIBUTE_DEFAULT)))


def get_driver_skill_int(driver: Any) -> int:
	"""Return a display-friendly integer skill (0-100) for UI widgets."""
	try:
		val = float(get_driver_skill(driver))
	except Exception:
		val = float(DRIVER_ATTRIBUTE_DEFAULT)
	return int(round(_clamp(val)))


def get_display_name(driver: Any) -> str:
	"""Return the most user-friendly driver name available.

	Checks a number of common fields used across the codebase and falls
	back to a generic identifier if necessary.
	"""
	if driver is None:
		return "Unknown"

	# Common single-field names
	for field in ("name", "full_name", "display_name", "driver_name", "short_name"):
		val = getattr(driver, field, None)
		if val:
			return str(val)

	# Split name components
	first = getattr(driver, "forename", None) or getattr(driver, "first_name", None) or getattr(driver, "given_name", None)
	last = getattr(driver, "surname", None) or getattr(driver, "last_name", None) or getattr(driver, "family_name", None)
	if first and last:
		return f"{first} {last}"
	if first:
		return str(first)
	if last:
		return str(last)

	# Fallback: nationality/number style like 'JPN #112' or a simple unknown
	nat = get_display_nationality(driver)
	number = getattr(driver, "number", None) or getattr(driver, "car_number", None)
	if nat and number:
		return f"{nat} #{number}"
	if nat:
		return str(nat)

	return "Unknown"


def get_display_nationality(driver: Any) -> str:
	"""Return a readable nationality string if available.

	This prefers full names but will return country codes where that's all
	that's present. Keep this lightweight to avoid heavy locale lookups.
	"""
	if driver is None:
		return "N/A"

	for field in ("nationality", "country", "country_name", "nationality_code", "country_code", "name_locale"):
		val = getattr(driver, field, None)
		if val:
			return str(val)

	return "N/A"


def get_preferred_window_size() -> tuple[int, int]:
	"""Return preferred (width, height) for the Quick Race window to match app.

	The rest of the game's dialogs use a larger, consistent window size; use
	a sensible default here so the GUI can ask the service for sizing.
	"""
	import os
	import re

	# Priority order for determining preferred size:
	# 1. Environment variable `PREFERRED_WINDOW_SIZE` or `APP_WINDOW_SIZE` as "WxH" or "W,H"
	# 2. Environment variables `APP_WINDOW_WIDTH` and `APP_WINDOW_HEIGHT`
	# 3. If a QApplication exists, ask the primary screen size
	# 4. Fallback to 1920x1080

	env_size = os.getenv("PREFERRED_WINDOW_SIZE") or os.getenv("APP_WINDOW_SIZE")
	if env_size:
		m = re.match(r"\s*(\d+)\s*[x,\s]\s*(\d+)\s*", env_size)
		if m:
			try:
				return (int(m.group(1)), int(m.group(2)))
			except Exception:
				pass

	w = os.getenv("APP_WINDOW_WIDTH")
	h = os.getenv("APP_WINDOW_HEIGHT")
	if w and h:
		try:
			return (int(w), int(h))
		except Exception:
			pass

	# If running inside a Qt application, use the primary screen resolution
	try:
		from PyQt6.QtWidgets import QApplication
		app = QApplication.instance()
		if app is not None:
			screen = app.primaryScreen()
			if screen is not None:
				size = screen.size()
				return (int(size.width()), int(size.height()))
	except Exception:
		pass

	# Final fallback
	return (1920, 1080)


def get_driver_radar_values(driver: Any) -> list[float]:
	"""Return six canonical attribute values for a radar/polygon display.

	The 6 values represent the primary skill axes used across the UI:
	[speed, racecraft, consistency, reactions, setup_knowledge, tyre_management]

	This function uses only canonical attributes and clamps values to the
	canonical 0-100 range.
	"""
	if driver is None:
		return [float(DRIVER_ATTRIBUTE_DEFAULT)] * 6

	vals = [
		get_safe_attribute(driver, "speed"),
		get_safe_attribute(driver, "racecraft"),
		get_safe_attribute(driver, "consistency"),
		get_safe_attribute(driver, "reactions"),
		get_safe_attribute(driver, "setup_knowledge"),
		get_safe_attribute(driver, "tyre_management"),
	]
	# Ensure numeric floats
	return [float(_clamp(v)) for v in vals]


def get_attribute_value(driver: Any, attr_name: str) -> float:
	"""Return a canonical 0-100 attribute value for a requested attribute name.

	This maps common legacy names to canonical attributes or computed
	helpers. It does NOT read deprecated stored legacy fields — all values
	are computed from canonical persisted attributes.
	"""
	name = (attr_name or "").lower()

	mapping = {
		'raw_speed': lambda d: get_safe_attribute(d, 'speed'),
		'speed': lambda d: get_safe_attribute(d, 'speed'),
		'racecraft': lambda d: get_safe_attribute(d, 'racecraft'),
		'consistency': lambda d: get_safe_attribute(d, 'consistency'),
		'reactions': lambda d: get_safe_attribute(d, 'reactions'),
		'setup_knowledge': lambda d: get_safe_attribute(d, 'setup_knowledge'),
		'tyre_management': lambda d: get_safe_attribute(d, 'tyre_management'),
		'vehicle_control': lambda d: get_vehicle_control(d),
		'cornering_skill': lambda d: get_cornering_skill(d),
		'aggression': lambda d: get_driver_aggression(d),
		'professionalism': lambda d: get_driver_professionalism(d),
		'risk_taking': lambda d: (100.0 - get_driver_professionalism(d)),
		'bravery': lambda d: get_driver_bravery(d),
	}

	func = mapping.get(name)
	if func:
		try:
			return float(_clamp(func(driver)))
		except Exception:
			return float(DRIVER_ATTRIBUTE_DEFAULT)

	# Unknown attribute -> try direct canonical read
	return float(get_safe_attribute(driver, attr_name, DRIVER_ATTRIBUTE_DEFAULT))

