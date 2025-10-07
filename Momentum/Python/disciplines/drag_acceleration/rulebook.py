"""
Drag Acceleration Rulebook
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class DragAccelerationRulebook:
    """Drag racing technical regulations"""
    engine_displacement_max_cc: float = 8000.0
    aspiration_allowed: Optional[list] = None
    hybrid_required: bool = False
    minimum_weight_kg: float = 900.0
    parachute_required: bool = True
    wheelie_bars_allowed: bool = True
    
    def __post_init__(self):
        if self.aspiration_allowed is None:
            self.aspiration_allowed = ["naturally_aspirated", "turbocharged", "supercharged"]
    
    def validate_vehicle(self, vehicle) -> tuple[bool, Dict[str, list[str]]]:
        violations = {}
        if vehicle.engine and vehicle.engine.displacement_cc > self.engine_displacement_max_cc:
            violations['engine'] = [f"Exceeds {self.engine_displacement_max_cc}cc"]
        return len(violations) == 0, violations


DRAG_ACCELERATION_RULEBOOK = DragAccelerationRulebook()

__all__ = ['DragAccelerationRulebook', 'DRAG_ACCELERATION_RULEBOOK']
