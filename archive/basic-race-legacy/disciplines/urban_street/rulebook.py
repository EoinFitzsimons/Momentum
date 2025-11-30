"""Rulebooks for Urban Street, Drag, Rallycross, and Endurance"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class UrbanStreetRulebook:
    """Urban Street technical regulations"""
    engine_displacement_max_cc: float = 1600.0
    hybrid_required: bool = True
    minimum_weight_kg: float = 798.0
    drs_allowed: bool = False
    traction_control_allowed: bool = False
    abs_allowed: bool = False
    roll_cage_required: bool = True
    
    def validate_vehicle(self, vehicle) -> tuple[bool, Dict[str, list[str]]]:
        violations = {}
        if vehicle.total_mass < self.minimum_weight_kg:
            violations['weight'] = [f"Below {self.minimum_weight_kg}kg"]
        return len(violations) == 0, violations


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


# Singletons
URBAN_STREET_RULEBOOK = UrbanStreetRulebook()
DRAG_ACCELERATION_RULEBOOK = DragAccelerationRulebook()
SPRINT_RALLYCROSS_RULEBOOK = SprintRallycrossRulebook()
ENDURANCE_RULEBOOK = EnduranceRulebook()
