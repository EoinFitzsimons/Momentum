"""
Chassis and Suspension Component Models

Models for chassis, suspension systems, and vehicle dynamics components.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from .enums import SuspensionType, ChassisMaterial, DamperType, BrakeMaterial, BrakeConfiguration


@dataclass
class Suspension:
    """
    Suspension System Model
    
    Represents complete suspension setup including springs, dampers,
    anti-roll bars, and geometry settings.
    """
    suspension_type: SuspensionType
    
    # Spring settings (N/mm)
    front_spring_rate: float = 80.0
    rear_spring_rate: float = 90.0
    
    # Damper settings (clicks/levels, 1-20 scale)
    front_damper_compression: int = 10
    front_damper_rebound: int = 12
    rear_damper_compression: int = 10
    rear_damper_rebound: int = 12
    damper_type: DamperType = DamperType.MONOTUBE
    
    # Anti-roll bar stiffness (N/mm)
    front_arb_stiffness: float = 50.0
    rear_arb_stiffness: float = 55.0
    
    # Geometry settings (degrees)
    front_camber: float = -2.5
    rear_camber: float = -2.0
    front_toe: float = 0.0            # Degrees (positive = toe-in)
    rear_toe: float = 0.2             # Degrees (positive = toe-in)
    front_caster: float = 6.0
    
    # Ride height (mm from ground)
    front_ride_height: float = 40.0
    rear_ride_height: float = 45.0
    
    # Component condition
    spring_condition: float = 1.0
    damper_condition: float = 1.0
    arb_condition: float = 1.0
    bushings_condition: float = 1.0
    
    # Usage statistics
    km_traveled: float = 0.0
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate suspension wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        self.spring_condition -= 0.0002 * wear_factor
        self.damper_condition -= 0.0006 * wear_factor
        self.arb_condition -= 0.0003 * wear_factor
        self.bushings_condition -= 0.0008 * wear_factor
        
        # Active damping systems wear faster
        if self.damper_type == DamperType.ACTIVE:
            self.damper_condition -= 0.0004 * wear_factor
        
        self._clamp_conditions()
    
    def get_overall_condition(self) -> float:
        """Calculate overall suspension health"""
        return (self.spring_condition * 0.2 +
                self.damper_condition * 0.4 +
                self.arb_condition * 0.2 +
                self.bushings_condition * 0.2)
    
    def get_balance(self) -> float:
        """
        Calculate suspension balance (front vs rear stiffness)
        
        Returns:
            Balance value (-1.0 to 1.0, where negative = front-biased, positive = rear-biased)
        """
        front_total = self.front_spring_rate + self.front_arb_stiffness
        rear_total = self.rear_spring_rate + self.rear_arb_stiffness
        total = front_total + rear_total
        
        if total == 0:
            return 0.0
        
        return (rear_total - front_total) / total
    
    def requires_rebuild(self) -> bool:
        """Check if suspension needs rebuild"""
        return (self.damper_condition < 0.4 or 
                self.bushings_condition < 0.3)
    
    def rebuild(self):
        """Perform complete suspension rebuild"""
        self.spring_condition = 1.0
        self.damper_condition = 1.0
        self.arb_condition = 1.0
        self.bushings_condition = 1.0
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.spring_condition = max(0.0, min(1.0, self.spring_condition))
        self.damper_condition = max(0.0, min(1.0, self.damper_condition))
        self.arb_condition = max(0.0, min(1.0, self.arb_condition))
        self.bushings_condition = max(0.0, min(1.0, self.bushings_condition))


@dataclass
class BrakeSystem:
    """
    Braking System Model
    
    Represents complete brake system including discs, calipers, and brake balance.
    """
    brake_material: BrakeMaterial
    brake_config: BrakeConfiguration
    
    # Brake specifications
    front_disc_diameter_mm: int = 380
    rear_disc_diameter_mm: int = 330
    front_caliper_pistons: int = 6
    rear_caliper_pistons: int = 4
    
    # Brake balance (percentage to front, 50-70% typical)
    brake_bias: float = 58.0
    
    # Component condition
    front_disc_wear: float = 1.0
    rear_disc_wear: float = 1.0
    front_pad_wear: float = 1.0
    rear_pad_wear: float = 1.0
    caliper_condition: float = 1.0
    brake_fluid_condition: float = 1.0
    
    # Performance characteristics
    brake_temperature_front: float = 100.0  # °C
    brake_temperature_rear: float = 90.0    # °C
    optimal_temp_range: tuple = (200.0, 800.0)
    fade_threshold_temp: float = 900.0
    
    # Usage statistics
    total_brake_applications: int = 0
    km_traveled: float = 0.0
    
    def apply_brakes(self, intensity: float, duration_seconds: float):
        """
        Apply brakes and simulate heat generation and wear
        
        Args:
            intensity: Braking intensity (0.0-1.0)
            duration_seconds: Duration of brake application
        """
        self.total_brake_applications += 1
        
        # Generate heat based on intensity
        heat_generated = intensity * 100.0 * duration_seconds
        self.brake_temperature_front += heat_generated * (self.brake_bias / 100.0)
        self.brake_temperature_rear += heat_generated * ((100.0 - self.brake_bias) / 100.0)
        
        # Apply wear
        wear = 0.00001 * intensity * duration_seconds
        self.front_disc_wear -= wear * (self.brake_bias / 100.0)
        self.rear_disc_wear -= wear * ((100.0 - self.brake_bias) / 100.0)
        self.front_pad_wear -= wear * 2.0 * (self.brake_bias / 100.0)
        self.rear_pad_wear -= wear * 2.0 * ((100.0 - self.brake_bias) / 100.0)
        
        self._clamp_conditions()
    
    def cool_brakes(self, duration_seconds: float, cooling_factor: float = 0.1):
        """
        Cool brakes naturally over time
        
        Args:
            duration_seconds: Duration of cooling period
            cooling_factor: Cooling efficiency (0.0-1.0)
        """
        ambient_temp = 25.0
        cooling_rate = cooling_factor * duration_seconds
        
        self.brake_temperature_front -= (self.brake_temperature_front - ambient_temp) * cooling_rate
        self.brake_temperature_rear -= (self.brake_temperature_rear - ambient_temp) * cooling_rate
        
        self.brake_temperature_front = max(ambient_temp, self.brake_temperature_front)
        self.brake_temperature_rear = max(ambient_temp, self.brake_temperature_rear)
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate brake system wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        # Additional general wear beyond brake applications
        self.caliper_condition -= 0.0002 * wear_factor
        self.brake_fluid_condition -= 0.0004 * wear_factor
        
        # Carbon brakes wear differently
        if self.brake_material == BrakeMaterial.CARBON:
            # Carbon brakes need heat to work optimally
            if self.brake_temperature_front < 200:
                self.front_disc_wear -= 0.0001 * wear_factor
            if self.brake_temperature_rear < 200:
                self.rear_disc_wear -= 0.0001 * wear_factor
        
        self._clamp_conditions()
    
    def get_braking_efficiency(self) -> float:
        """Calculate current braking efficiency based on temperature and wear"""
        # Temperature factor
        avg_temp = (self.brake_temperature_front + self.brake_temperature_rear) / 2.0
        
        if self.brake_material == BrakeMaterial.CARBON:
            # Carbon brakes work better when hot
            if avg_temp < 200:
                temp_factor = 0.6
            elif avg_temp > 800:
                temp_factor = 0.8
            else:
                temp_factor = 1.0
        else:
            # Steel/ceramic brakes fade when too hot
            if avg_temp > self.fade_threshold_temp:
                temp_factor = 0.5
            elif avg_temp > 700:
                temp_factor = 0.8
            else:
                temp_factor = 1.0
        
        # Wear factor
        avg_disc_wear = (self.front_disc_wear + self.rear_disc_wear) / 2.0
        avg_pad_wear = (self.front_pad_wear + self.rear_pad_wear) / 2.0
        
        wear_factor = (avg_disc_wear + avg_pad_wear) / 2.0
        
        return temp_factor * wear_factor * self.caliper_condition
    
    def get_overall_condition(self) -> float:
        """Calculate overall brake system health"""
        return ((self.front_disc_wear + self.rear_disc_wear) / 2.0 * 0.25 +
                (self.front_pad_wear + self.rear_pad_wear) / 2.0 * 0.35 +
                self.caliper_condition * 0.2 +
                self.brake_fluid_condition * 0.2)
    
    def requires_service(self) -> bool:
        """Check if brakes need service"""
        return (self.front_pad_wear < 0.2 or 
                self.rear_pad_wear < 0.2 or 
                self.brake_fluid_condition < 0.3)
    
    def service(self):
        """Perform routine brake service (pads, fluid)"""
        self.front_pad_wear = 1.0
        self.rear_pad_wear = 1.0
        self.brake_fluid_condition = 1.0
    
    def rebuild(self):
        """Perform complete brake system rebuild"""
        self.front_disc_wear = 1.0
        self.rear_disc_wear = 1.0
        self.front_pad_wear = 1.0
        self.rear_pad_wear = 1.0
        self.caliper_condition = 1.0
        self.brake_fluid_condition = 1.0
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.front_disc_wear = max(0.0, min(1.0, self.front_disc_wear))
        self.rear_disc_wear = max(0.0, min(1.0, self.rear_disc_wear))
        self.front_pad_wear = max(0.0, min(1.0, self.front_pad_wear))
        self.rear_pad_wear = max(0.0, min(1.0, self.rear_pad_wear))
        self.caliper_condition = max(0.0, min(1.0, self.caliper_condition))
        self.brake_fluid_condition = max(0.0, min(1.0, self.brake_fluid_condition))


@dataclass
class Chassis:
    """
    Chassis/Monocoque Model
    
    Represents the vehicle's structural foundation.
    """
    material: ChassisMaterial
    weight_kg: float = 600.0              # Chassis weight
    
    # Structural integrity
    structural_integrity: float = 1.0     # Overall chassis condition
    crash_damage: float = 0.0             # Accumulated crash damage (0.0-1.0)
    
    # Weight distribution (percentage front)
    weight_distribution: float = 48.0
    
    # Safety rating
    safety_rating: float = 1.0
    
    # Usage statistics
    km_traveled: float = 0.0
    crashes: int = 0
    
    def apply_crash_damage(self, severity: float):
        """
        Apply damage from a crash
        
        Args:
            severity: Crash severity (0.0-1.0)
        """
        damage = severity * 0.3  # Maximum 30% damage per crash
        self.crash_damage += damage
        self.structural_integrity -= damage * 0.5
        self.crashes += 1
        
        self._clamp_conditions()
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate chassis wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        # Chassis doesn't wear much from normal use
        self.structural_integrity -= 0.00005 * wear_factor
        
        self._clamp_conditions()
    
    def get_overall_condition(self) -> float:
        """Calculate overall chassis health"""
        return self.structural_integrity * (1.0 - self.crash_damage * 0.5)
    
    def requires_rebuild(self) -> bool:
        """Check if chassis needs rebuild"""
        return self.crash_damage > 0.5 or self.structural_integrity < 0.6
    
    def repair(self, extent: float = 1.0):
        """
        Repair chassis damage
        
        Args:
            extent: Repair completeness (0.0-1.0, where 1.0 is full repair)
        """
        self.crash_damage = max(0.0, self.crash_damage - extent)
        self.structural_integrity = min(1.0, self.structural_integrity + extent * 0.5)
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.structural_integrity = max(0.0, min(1.0, self.structural_integrity))
        self.crash_damage = max(0.0, min(1.0, self.crash_damage))


__all__ = ['Suspension', 'BrakeSystem', 'Chassis']
