"""
Production Touring Rulebook

Technical regulations for production-based touring car racing.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ProductionTouringRulebook:
    """Technical regulations for Production Touring racing"""
    
    # Engine
    engine_displacement_max_cc: float = 2000.0
    aspiration_allowed: Optional[list] = None
    max_turbo_boost_bar: float = 2.5
    max_engine_rpm: int = 8500
    
    # Hybrid (optional)
    hybrid_required: bool = False
    hybrid_allowed: bool = True
    max_hybrid_power_kw: float = 60.0
    
    # Weight
    minimum_weight_kg: float = 1300.0
    ballast_allowed: bool = True
    
    # Aerodynamics
    front_wing_required: bool = False
    rear_wing_max_height_mm: float = 200.0
    drs_allowed: bool = False
    active_suspension_allowed: bool = False
    ground_effect_allowed: bool = False
    
    # Tires
    tire_width_max_mm: float = 285.0
    
    # Gearbox
    gearbox_type_required: str = "h_pattern_or_sequential"
    max_forward_gears: int = 6
    
    # Electronics
    traction_control_allowed: bool = True
    abs_allowed: bool = True
    launch_control_allowed: bool = False
    
    # Safety
    roll_cage_required: bool = True
    fia_homologation_required: bool = False
    fire_suppression_required: bool = True
    
    def __post_init__(self):
        if self.aspiration_allowed is None:
            self.aspiration_allowed = ["naturally_aspirated", "turbocharged"]
    
    def validate_vehicle(self, vehicle) -> tuple[bool, Dict[str, list[str]]]:
        """Simplified validation for production touring"""
        violations = {}
        
        if vehicle.engine and vehicle.engine.displacement_cc > self.engine_displacement_max_cc:
            violations['engine'] = [f"Displacement exceeds {self.engine_displacement_max_cc}cc"]
        
        if vehicle.total_mass < self.minimum_weight_kg:
            violations['weight'] = [f"Weight below {self.minimum_weight_kg}kg minimum"]
        
        return len(violations) == 0, violations


PRODUCTION_TOURING_RULEBOOK = ProductionTouringRulebook()

__all__ = ['ProductionTouringRulebook', 'PRODUCTION_TOURING_RULEBOOK']
