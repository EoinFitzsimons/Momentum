"""
Endurance Racing Rulebook
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class EnduranceRulebook:
    """Endurance racing technical regulations"""
    engine_displacement_max_cc: float = 5500.0
    hybrid_required: bool = True
    max_hybrid_power_kw: float = 200.0
    minimum_weight_kg: float = 930.0
    fuel_capacity_max_liters: float = 90.0
    drs_allowed: bool = False
    traction_control_allowed: bool = True
    abs_allowed: bool = True
    
    def validate_vehicle(self, vehicle) -> tuple[bool, Dict[str, list[str]]]:
        violations = {}
        if self.hybrid_required and not vehicle.hybrid_unit:
            violations['hybrid'] = ["Hybrid system required"]
        if vehicle.total_mass < self.minimum_weight_kg:
            violations['weight'] = [f"Below {self.minimum_weight_kg}kg"]
        return len(violations) == 0, violations


ENDURANCE_RULEBOOK = EnduranceRulebook()

__all__ = ['EnduranceRulebook', 'ENDURANCE_RULEBOOK']
