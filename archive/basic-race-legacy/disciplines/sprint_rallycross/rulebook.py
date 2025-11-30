"""
Sprint Rallycross Rulebook
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class SprintRallycrossRulebook:
    """Sprint Rallycross technical regulations"""
    engine_displacement_max_cc: float = 2000.0
    aspiration_allowed: Optional[list] = None
    minimum_weight_kg: float = 1230.0
    underbody_protection_required: bool = True
    roll_cage_required: bool = True
    traction_control_allowed: bool = True
    
    def __post_init__(self):
        if self.aspiration_allowed is None:
            self.aspiration_allowed = ["turbocharged"]
    
    def validate_vehicle(self, vehicle) -> tuple[bool, Dict[str, list[str]]]:
        violations = {}
        if not vehicle.safety or not vehicle.safety.roll_cage_installed:
            violations['safety'] = ["Roll cage required"]
        return len(violations) == 0, violations


SPRINT_RALLYCROSS_RULEBOOK = SprintRallycrossRulebook()

__all__ = ['SprintRallycrossRulebook', 'SPRINT_RALLYCROSS_RULEBOOK']
