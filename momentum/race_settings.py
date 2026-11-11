"""Persisted player-facing race visualisation settings."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

DEFAULT_RACE_SETTINGS: Dict[str, Any] = {
    "render_fps": 0,
    "simulation_speed": 5.0,
}


def _settings_path() -> str:
    settings_dir = os.path.join(os.path.expanduser("~"), ".momentum")
    os.makedirs(settings_dir, exist_ok=True)
    return os.path.join(settings_dir, "race_settings.json")


def normalize_race_settings(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    settings = dict(DEFAULT_RACE_SETTINGS)
    if not isinstance(raw, dict):
        return settings

    try:
        render_fps = int(raw.get("render_fps", settings["render_fps"]))
    except (TypeError, ValueError):
        render_fps = int(settings["render_fps"])
    if render_fps not in {0, 30, 60, 120, 144, 240}:
        render_fps = int(settings["render_fps"])

    try:
        simulation_speed = float(
            raw.get("simulation_speed", settings["simulation_speed"])
        )
    except (TypeError, ValueError):
        simulation_speed = float(settings["simulation_speed"])
    simulation_speed = min(20.0, max(0.25, simulation_speed))

    settings["render_fps"] = render_fps
    settings["simulation_speed"] = simulation_speed
    return settings


def load_race_settings() -> Dict[str, Any]:
    try:
        with open(_settings_path(), "r", encoding="utf-8") as settings_file:
            return normalize_race_settings(json.load(settings_file))
    except (OSError, ValueError, TypeError):
        return dict(DEFAULT_RACE_SETTINGS)


def save_race_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_race_settings(settings)
    with open(_settings_path(), "w", encoding="utf-8") as settings_file:
        json.dump(normalized, settings_file, indent=2)
    return normalized
