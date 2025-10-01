"""
Rally Stage Rulebook
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class RallyStageRulebook:
    """Technical regulations for Rally Stage racing"""
    
    engine_displacement_max_cc: float = 2000.0
    aspiration_allowed: Optional[list] = None
    max_turbo_boost_bar: float = 3.0
    
    hybrid_required: bool = False
    hybrid_allowed: bool = True
    
    minimum_weight_kg: float = 1230.0
    
    # Rally-specific
    underbody_protection_required: bool = True
    roll_cage_required: bool = True
    co_driver_seat_required: bool = True
    
    # Suspension
    suspension_travel_min_mm: float = 200.0
    
    # Tires
    tire_types_allowed: Optional[list] = None  # ["gravel", "tarmac", "snow"]
    
    # Electronics
    traction_control_allowed: bool = True
    abs_allowed: bool = True
    
    # Safety
    fia_homologation_required: bool = True
    fire_suppression_required: bool = True
    
    def __post_init__(self):
        if self.aspiration_allowed is None:
            self.aspiration_allowed = ["turbocharged"]
        if self.tire_types_allowed is None:
            self.tire_types_allowed = ["gravel", "tarmac", "snow", "mixed"]
    
    def validate_vehicle(self, vehicle) -> tuple[bool, Dict[str, list[str]]]:
        violations = {}
        
        if not vehicle.safety or not vehicle.safety.roll_cage_installed:
            violations['safety'] = ["Roll cage required"]
        
        if vehicle.total_mass < self.minimum_weight_kg:
            violations['weight'] = [f"Weight below {self.minimum_weight_kg}kg"]
        
        return len(violations) == 0, violations


RALLY_STAGE_RULEBOOK = RallyStageRulebook()

__all__ = ['RallyStageRulebook', 'RALLY_STAGE_RULEBOOK']
