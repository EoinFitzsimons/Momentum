"""
Electronic Control Systems

Models for ECU, driver aids, and electronic systems.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from .enums import ControlUnitType, SteeringType


@dataclass
class ElectronicControlUnit:
    """
    Electronic Control Unit (ECU) Model
    
    Represents the car's computer system managing engine, electronics,
    and driver assistance systems.
    """
    ecu_type: ControlUnitType
    
    # Driver assistance systems
    traction_control: bool = False
    traction_control_level: int = 0       # 0 = off, 1-12 = intervention level
    abs_enabled: bool = False
    abs_level: int = 0                    # 0 = off, 1-12 = intervention level
    stability_control: bool = False
    torque_vectoring: bool = False
    launch_control: bool = False
    drs_control: bool = False
    
    # Engine management
    engine_maps: int = 3                  # Number of engine maps available
    active_engine_map: int = 1            # Currently selected map
    fuel_mixture_control: bool = True
    ignition_timing_control: bool = True
    boost_control: bool = False           # For turbocharged engines
    
    # Data systems
    telemetry_enabled: bool = True
    data_logging: bool = True
    real_time_strategy: bool = False
    
    # Component condition
    reliability: float = 1.0
    sensor_health: float = 1.0
    actuator_health: float = 1.0
    
    # Usage statistics
    total_operating_hours: float = 0.0
    error_count: int = 0
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate ECU and electronics wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        self.reliability -= 0.0002 * wear_factor
        self.sensor_health -= 0.0003 * wear_factor
        self.actuator_health -= 0.0004 * wear_factor
        
        # Advanced systems have more complexity = more failure points
        if self.ecu_type in [ControlUnitType.ADVANCED_ECU, ControlUnitType.TELEMETRY_CONTROL]:
            self.reliability -= 0.0001 * wear_factor
        
        self._clamp_conditions()
    
    def get_overall_condition(self) -> float:
        """Calculate overall ECU health"""
        return (self.reliability * 0.5 +
                self.sensor_health * 0.3 +
                self.actuator_health * 0.2)
    
    def log_error(self):
        """Log an ECU error"""
        self.error_count += 1
        self.reliability -= 0.001
        self._clamp_conditions()
    
    def reset_errors(self):
        """Clear error codes"""
        self.error_count = 0
    
    def requires_service(self) -> bool:
        """Check if ECU needs service"""
        return (self.reliability < 0.7 or 
                self.sensor_health < 0.6 or 
                self.error_count > 10)
    
    def service(self):
        """Perform ECU service (diagnostics, sensor calibration)"""
        self.reliability = min(1.0, self.reliability + 0.1)
        self.sensor_health = min(1.0, self.sensor_health + 0.15)
        self.error_count = 0
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.reliability = max(0.0, min(1.0, self.reliability))
        self.sensor_health = max(0.0, min(1.0, self.sensor_health))
        self.actuator_health = max(0.0, min(1.0, self.actuator_health))


@dataclass
class SteeringSystem:
    """
    Steering System Model
    
    Represents the steering mechanism and power assistance.
    """
    steering_type: SteeringType
    
    # Steering characteristics
    steering_ratio: float = 14.5          # Steering wheel degrees per road wheel degree
    max_lock_angle: float = 35.0          # Maximum steering angle (degrees)
    
    # Power assistance (if applicable)
    assistance_level: float = 0.7         # 0.0 = no assist, 1.0 = full assist
    
    # Component condition
    condition: float = 1.0
    rack_condition: float = 1.0
    pump_condition: float = 1.0           # For hydraulic/electrohydraulic
    
    # Usage statistics
    total_steering_inputs: int = 0
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate steering system wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        self.condition -= 0.0002 * wear_factor
        self.rack_condition -= 0.0003 * wear_factor
        
        if self.steering_type in [SteeringType.HYDRAULIC, SteeringType.ELECTROHYDRAULIC]:
            self.pump_condition -= 0.0004 * wear_factor
        
        self._clamp_conditions()
    
    def get_overall_condition(self) -> float:
        """Calculate overall steering system health"""
        if self.steering_type in [SteeringType.HYDRAULIC, SteeringType.ELECTROHYDRAULIC]:
            return (self.condition * 0.4 +
                    self.rack_condition * 0.4 +
                    self.pump_condition * 0.2)
        else:
            return (self.condition * 0.5 +
                    self.rack_condition * 0.5)
    
    def requires_service(self) -> bool:
        """Check if steering needs service"""
        return (self.condition < 0.5 or 
                self.rack_condition < 0.4)
    
    def service(self):
        """Perform steering system service"""
        self.condition = min(1.0, self.condition + 0.1)
        self.rack_condition = min(1.0, self.rack_condition + 0.1)
        if self.steering_type in [SteeringType.HYDRAULIC, SteeringType.ELECTROHYDRAULIC]:
            self.pump_condition = 1.0
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.condition = max(0.0, min(1.0, self.condition))
        self.rack_condition = max(0.0, min(1.0, self.rack_condition))
        self.pump_condition = max(0.0, min(1.0, self.pump_condition))


@dataclass
class SafetySystem:
    """
    Safety Systems Model
    
    Represents safety equipment including roll cage, fire suppression, etc.
    """
    # Safety equipment
    roll_cage_installed: bool = True
    roll_cage_material: str = "Chromoly Steel"
    fire_suppression_installed: bool = True
    fire_suppression_charges: int = 2
    
    # Crash structure
    crash_structure_integrity: float = 1.0
    side_impact_protection: float = 1.0
    
    # Safety equipment condition
    seat_belts_condition: float = 1.0
    hans_device_condition: float = 1.0
    seat_condition: float = 1.0
    
    # Certifications
    fia_certified: bool = False
    fia_expiry_date: Optional[str] = None
    
    def activate_fire_suppression(self) -> bool:
        """
        Activate fire suppression system
        
        Returns:
            True if successfully activated, False if no charges remain
        """
        if self.fire_suppression_charges > 0:
            self.fire_suppression_charges -= 1
            return True
        return False
    
    def apply_crash_damage(self, severity: float):
        """
        Apply damage from a crash
        
        Args:
            severity: Crash severity (0.0-1.0)
        """
        self.crash_structure_integrity -= severity * 0.3
        self.side_impact_protection -= severity * 0.2
        self._clamp_conditions()
    
    def get_safety_rating(self) -> float:
        """Calculate overall safety rating"""
        rating = 0.0
        
        if self.roll_cage_installed:
            rating += 0.3 * self.crash_structure_integrity
        if self.fire_suppression_installed:
            rating += 0.2
        if self.fia_certified:
            rating += 0.2
        
        rating += self.seat_belts_condition * 0.15
        rating += self.hans_device_condition * 0.15
        
        return min(1.0, rating)
    
    def requires_inspection(self) -> bool:
        """Check if safety equipment needs inspection"""
        return (self.crash_structure_integrity < 0.8 or 
                self.seat_belts_condition < 0.7 or 
                self.fire_suppression_charges == 0)
    
    def service(self):
        """Perform safety equipment service"""
        self.seat_belts_condition = 1.0
        self.hans_device_condition = 1.0
        self.seat_condition = 1.0
        if self.fire_suppression_installed:
            self.fire_suppression_charges = 2
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.crash_structure_integrity = max(0.0, min(1.0, self.crash_structure_integrity))
        self.side_impact_protection = max(0.0, min(1.0, self.side_impact_protection))
        self.seat_belts_condition = max(0.0, min(1.0, self.seat_belts_condition))
        self.hans_device_condition = max(0.0, min(1.0, self.hans_device_condition))
        self.seat_condition = max(0.0, min(1.0, self.seat_condition))


__all__ = ['ElectronicControlUnit', 'SteeringSystem', 'SafetySystem']
