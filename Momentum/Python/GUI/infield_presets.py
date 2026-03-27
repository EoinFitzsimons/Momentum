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
        'texture_tint': QColor(70, 150, 60, 200),
        'occlusion': 0.08,
        'mole': QColor(40, 100, 30),
        'streak': QColor(70, 50, 30, 100),
        'density_mult': 1.2,
        'molehills_mult': 1.0,
    },
    'dry': {
        'base': QColor(150, 140, 80),
        'highlight': QColor(170, 155, 95),
        'texture_tint': QColor(140, 120, 70, 200),
        'occlusion': 0.10,
        'mole': QColor(90, 70, 40),
        'streak': QColor(100, 80, 50, 110),
        'density_mult': 0.7,
        'molehills_mult': 0.6,
    },
    'autumn': {
        'base': QColor(140, 110, 60),
        'highlight': QColor(160, 130, 80),
        'texture_tint': QColor(130, 100, 55, 200),
        'occlusion': 0.12,
        'mole': QColor(80, 60, 30),
        'streak': QColor(110, 70, 40, 120),
        'density_mult': 0.8,
        'molehills_mult': 0.8,
    },
    'wet': {
        'base': QColor(60, 120, 60),
        'highlight': QColor(75, 140, 75),
        'texture_tint': QColor(55, 110, 55, 200),
        'occlusion': 0.06,
        'mole': QColor(30, 80, 30),
        'streak': QColor(30, 20, 20, 140),
        'density_mult': 1.0,
        'molehills_mult': 0.9,
    }
}


def _normalize_grip_to_legacy_scale(surface_grip: Optional[float]) -> Optional[float]:
    """Normalize grip to legacy 0..20 scale used by preset thresholds."""
    if surface_grip is None:
        return None
    try:
        grip = float(surface_grip)
    except Exception:
        return None
    if grip <= 1.0:
        grip *= 20.0
    return grip


def _surface_to_preset(surface: str) -> Optional[str]:
    """Return direct preset mapping for known surface keywords."""
    if 'snow' in surface or 'ice' in surface or 'wet' in surface:
        return 'wet'
    if 'dirt' in surface or 'gravel' in surface or 'sand' in surface:
        return 'dry'
    if 'concrete' in surface or 'mixed' in surface:
        return 'autumn'
    return None


def select_preset(surface: str, surface_grip: Optional[float] = None, seed: Optional[int] = None) -> Dict:
    """Choose a preset based on surface and grip.

    Rules (simple heuristics):
    - dirt/gravel/sand/snow/ice bias toward drier or wetter terrain tones
    - concrete and mixed favor sparse vegetation tones
    - grip values can be either 0..1 or legacy 0..20 and are normalized
    - otherwise prefer lush vegetation
    """
    s = (surface or '').lower()
    preset = 'lush'
    try:
        surface_preset = _surface_to_preset(s)
        if surface_preset is not None:
            preset = surface_preset
        else:
            g = _normalize_grip_to_legacy_scale(surface_grip)
            if g is not None:
                if g < 7:
                    preset = 'wet'
                elif g < 11:
                    preset = 'dry'
    except Exception:
        preset = 'lush'

    p = PRESETS.get(preset, PRESETS['lush']).copy()
    # allow a seed to nudge palette slightly in future - put seed in result
    p['seed'] = seed
    p['name'] = preset
    return p
