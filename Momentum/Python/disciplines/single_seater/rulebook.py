"""
Single Seater Rulebook

Technical regulations and compliance rules for single-seater formula racing.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SingleSeaterRulebook:
    """
    Technical regulations for Single Seater racing.
    
    Defines legal specifications for vehicles competing in this discipline.
    Vehicles are validated against these rules before competition.
    """
    
    # ===== ENGINE REGULATIONS =====
    engine_displacement_max_cc: float = 1600.0
    engine_cylinders_max: int = 6
    aspiration_allowed: list = None  # ["naturally_aspirated", "turbocharged"]
    max_turbo_boost_bar: float = 3.5
    max_engine_rpm: int = 15000
    
    fuel_flow_limit_kg_per_hour: float = 100.0
    fuel_type_required: str = "E10"  # 10% ethanol blend
    
    # ===== HYBRID SYSTEM REGULATIONS =====
    hybrid_required: bool = True
    hybrid_systems_allowed: list = None  # ["ERS_K", "ERS_H"]
    max_hybrid_power_kw: float = 120.0
    max_energy_recovery_per_lap_mj: float = 4.0
    max_energy_deployment_per_lap_mj: float = 4.0
    
    battery_type_allowed: str = "lithium_ion"
    max_battery_capacity_kwh: float = 4.0
    
    # ===== WEIGHT REGULATIONS =====
    minimum_weight_kg: float = 798.0  # Including driver
    driver_minimum_weight_kg: float = 80.0
    ballast_allowed: bool = True
    
    # ===== AERODYNAMICS REGULATIONS =====
    front_wing_required: bool = True
    rear_wing_required: bool = True
    max_front_wing_width_mm: float = 1800.0
    max_rear_wing_width_mm: float = 1050.0
    max_rear_wing_height_mm: float = 950.0
    
    drs_allowed: bool = True
    drs_activation_zones: int = 2  # Typical per circuit
    active_suspension_allowed: bool = False
    ground_effect_allowed: bool = True
    
    # ===== TIRE REGULATIONS =====
    tire_supplier_exclusive: bool = True
    tire_compounds_available: int = 5  # C1-C5
    tire_width_front_mm: float = 305.0
    tire_width_rear_mm: float = 405.0
    tire_diameter_inch: float = 18.0
    
    # ===== GEARBOX REGULATIONS =====
    gearbox_type_required: str = "sequential"
    max_forward_gears: int = 8
    reverse_gear_required: bool = True
    
    # ===== ELECTRONICS REGULATIONS =====
    ecu_type_required: str = "STANDARD_FIA"
    ecu_modifications_allowed: bool = False
    traction_control_allowed: bool = False
    abs_allowed: bool = False
    launch_control_allowed: bool = False
    
    # ===== SAFETY REGULATIONS =====
    roll_hoop_required: bool = True
    survival_cell_required: bool = True
    fia_homologation_required: bool = True
    hans_device_required: bool = True
    fire_suppression_required: bool = True
    
    # ===== CHASSIS REGULATIONS =====
    monocoque_required: bool = True
    minimum_cockpit_opening_dimensions_mm: Dict[str, float] = None
    crash_test_required: bool = True
    
    # ===== DIMENSIONS REGULATIONS =====
    max_length_mm: float = 5500.0
    max_width_mm: float = 2000.0
    max_height_mm: float = 950.0
    wheelbase_min_mm: float = 3400.0
    wheelbase_max_mm: float = 3700.0
    
    def __post_init__(self):
        if self.aspiration_allowed is None:
            self.aspiration_allowed = ["turbocharged"]
        
        if self.hybrid_systems_allowed is None:
            self.hybrid_systems_allowed = ["ERS_K", "ERS_H", "KERS"]
        
        if self.minimum_cockpit_opening_dimensions_mm is None:
            self.minimum_cockpit_opening_dimensions_mm = {
                "width": 300.0,
                "length": 700.0
            }
    
    def validate_engine(self, vehicle) -> tuple[bool, list[str]]:
        """
        Validate engine compliance
        
        Args:
            vehicle: RaceCar instance to validate
            
        Returns:
            (is_compliant, list_of_violations)
        """
        violations = []
        
        if not vehicle.engine:
            violations.append("No engine installed")
            return False, violations
        
        if vehicle.engine.displacement_cc > self.engine_displacement_max_cc:
            violations.append(f"Engine displacement {vehicle.engine.displacement_cc}cc exceeds limit {self.engine_displacement_max_cc}cc")
        
        if vehicle.engine.cylinders > self.engine_cylinders_max:
            violations.append(f"Engine cylinders {vehicle.engine.cylinders} exceeds limit {self.engine_cylinders_max}")
        
        if vehicle.engine.max_rpm > self.max_engine_rpm:
            violations.append(f"Engine RPM limit {vehicle.engine.max_rpm} exceeds {self.max_engine_rpm}")
        
        return len(violations) == 0, violations
    
    def validate_hybrid(self, vehicle) -> tuple[bool, list[str]]:
        """Validate hybrid system compliance"""
        violations = []
        
        if self.hybrid_required and not vehicle.hybrid_unit:
            violations.append("Hybrid power unit required but not installed")
            return False, violations
        
        if vehicle.hybrid_unit:
            max_power_kw = vehicle.hybrid_unit.max_deployment_power_kw
            if max_power_kw > self.max_hybrid_power_kw:
                violations.append(f"Hybrid power {max_power_kw}kW exceeds limit {self.max_hybrid_power_kw}kW")
        
        return len(violations) == 0, violations
    
    def validate_weight(self, vehicle) -> tuple[bool, list[str]]:
        """Validate weight compliance"""
        violations = []
        
        if vehicle.total_mass < self.minimum_weight_kg:
            violations.append(f"Vehicle mass {vehicle.total_mass}kg below minimum {self.minimum_weight_kg}kg")
        
        return len(violations) == 0, violations
    
    def validate_aerodynamics(self, vehicle) -> tuple[bool, list[str]]:
        """Validate aerodynamics compliance"""
        violations = []
        
        if not vehicle.aerodynamics:
            violations.append("No aerodynamics package installed")
            return False, violations
        
        if self.drs_allowed and not vehicle.aerodynamics.drs_installed:
            violations.append("DRS system required but not installed")
        
        return len(violations) == 0, violations
    
    def validate_electronics(self, vehicle) -> tuple[bool, list[str]]:
        """Validate electronics compliance"""
        violations = []
        
        if not vehicle.ecu:
            violations.append("No ECU installed")
            return False, violations
        
        if not self.traction_control_allowed and vehicle.ecu.traction_control:
            violations.append("Traction control not allowed")
        
        if not self.abs_allowed and vehicle.ecu.abs_enabled:
            violations.append("ABS not allowed")
        
        if not self.launch_control_allowed and vehicle.ecu.launch_control:
            violations.append("Launch control not allowed")
        
        return len(violations) == 0, violations
    
    def validate_safety(self, vehicle) -> tuple[bool, list[str]]:
        """Validate safety equipment compliance"""
        violations = []
        
        if not vehicle.safety:
            violations.append("No safety equipment installed")
            return False, violations
        
        if self.fire_suppression_required and not vehicle.safety.fire_suppression_installed:
            violations.append("Fire suppression system required")
        
        if self.fia_homologation_required and not vehicle.safety.fia_certified:
            violations.append("FIA homologation required")
        
        return len(violations) == 0, violations
    
    def validate_vehicle(self, vehicle) -> tuple[bool, Dict[str, list[str]]]:
        """
        Perform complete technical compliance check
        
        Args:
            vehicle: RaceCar instance to validate
            
        Returns:
            (is_fully_compliant, dict_of_violations_by_category)
        """
        all_violations = {}
        
        # Check each subsystem
        engine_ok, engine_violations = self.validate_engine(vehicle)
        if engine_violations:
            all_violations['engine'] = engine_violations
        
        hybrid_ok, hybrid_violations = self.validate_hybrid(vehicle)
        if hybrid_violations:
            all_violations['hybrid'] = hybrid_violations
        
        weight_ok, weight_violations = self.validate_weight(vehicle)
        if weight_violations:
            all_violations['weight'] = weight_violations
        
        aero_ok, aero_violations = self.validate_aerodynamics(vehicle)
        if aero_violations:
            all_violations['aerodynamics'] = aero_violations
        
        electronics_ok, electronics_violations = self.validate_electronics(vehicle)
        if electronics_violations:
            all_violations['electronics'] = electronics_violations
        
        safety_ok, safety_violations = self.validate_safety(vehicle)
        if safety_violations:
            all_violations['safety'] = safety_violations
        
        is_compliant = len(all_violations) == 0
        return is_compliant, all_violations


# Singleton instance
SINGLE_SEATER_RULEBOOK = SingleSeaterRulebook()


__all__ = ['SingleSeaterRulebook', 'SINGLE_SEATER_RULEBOOK']
