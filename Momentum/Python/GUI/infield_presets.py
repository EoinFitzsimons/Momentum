"""Palette and preset definitions for infield biomes and weather modifiers.

Provides a simple API: `select_preset(surface, surface_grip, seed=None)`
returning a dict with colors and density multipliers used by the infield
renderer.
"""
from PyQt6.QtGui import QColor
from typing import Optional, Dict


PRESETS = {
    'lush': {
        'base': QColor(80, 160, 70),
        'highlight': QColor(95, 180, 85),
        'mole': QColor(40, 100, 30),
        'streak': QColor(70, 50, 30, 100),
        'density_mult': 1.2,
        'molehills_mult': 1.0,
    },
    'dry': {
        'base': QColor(150, 140, 80),
        'highlight': QColor(170, 155, 95),
        'mole': QColor(90, 70, 40),
        'streak': QColor(100, 80, 50, 110),
        'density_mult': 0.7,
        'molehills_mult': 0.6,
    },
    'autumn': {
        'base': QColor(140, 110, 60),
        'highlight': QColor(160, 130, 80),
        'mole': QColor(80, 60, 30),
        'streak': QColor(110, 70, 40, 120),
        'density_mult': 0.8,
        'molehills_mult': 0.8,
    },
    'wet': {
        'base': QColor(60, 120, 60),
        'highlight': QColor(75, 140, 75),
        'mole': QColor(30, 80, 30),
        'streak': QColor(30, 20, 20, 140),
        'density_mult': 1.0,
        'molehills_mult': 0.9,
    }
}


def select_preset(surface: str, surface_grip: Optional[float] = None, seed: Optional[int] = None) -> Dict:
    """Choose a preset based on surface and grip.

    Rules (simple heuristics):
    - If surface contains 'dirt' or 'gravel' -> 'dry'
    - If surface contains 'concrete' -> 'autumn' (less greenery)
    - If surface indicates mixed/wet or grip < 6 -> 'wet'
    - Otherwise prefer 'lush'
    """
    s = (surface or '').lower()
    preset = 'lush'
    try:
        if 'dirt' in s or 'gravel' in s:
            preset = 'dry'
        elif 'concrete' in s or 'mixed' in s:
            preset = 'autumn'
        elif 'wet' in s:
            preset = 'wet'
        elif surface_grip is not None:
            try:
                g = float(surface_grip)
                if g < 6:
                    preset = 'wet'
                elif g < 10:
                    preset = 'dry'
            except Exception:
                pass
    except Exception:
        preset = 'lush'

    p = PRESETS.get(preset, PRESETS['lush']).copy()
    # allow a seed to nudge palette slightly in future - put seed in result
    p['seed'] = seed
    p['name'] = preset
    return p
