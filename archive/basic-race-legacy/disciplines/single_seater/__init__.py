"""
Single Seater Discipline Package

Formula-style open-wheel racing with hybrid power units.

Authors: Final Year Project - Computer Science
"""

from .discipline_config import SingleSeaterConfig, SINGLE_SEATER_CONFIG
from .rulebook import SingleSeaterRulebook, SINGLE_SEATER_RULEBOOK

__all__ = [
    'SingleSeaterConfig',
    'SINGLE_SEATER_CONFIG',
    'SingleSeaterRulebook',
    'SINGLE_SEATER_RULEBOOK'
]
