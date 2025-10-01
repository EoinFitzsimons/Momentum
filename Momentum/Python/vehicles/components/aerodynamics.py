"""
Aerodynamics and Tire Component Models

Models for aerodynamic packages, tires, and their impact on performance.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .enums import AeroConfiguration, WingType, TireType, TireCompound


@dataclass
class AerodynamicsPackage:
    """
    Aerodynamics Package Model
    
    Represents complete aerodynamic setup including wings, undertray,
    and bodywork generating downforce and drag.
    """
    configuration: AeroConfiguration
    
    # Wing settings (degrees of angle)
    front_wing_angle: float = 10.0
    rear_wing_angle: float = 12.0
    front_wing_type: WingType = WingType.DOUBLE_ELEMENT
    rear_wing_type: WingType = WingType.TRIPLE_ELEMENT
    
    # Undertray and diffuser
    undertray_profile: int = 5            # Profile aggressiveness (1-10)
    diffuser_angle: float = 15.0          # Degrees
    
    # DRS (Drag Reduction System)
    drs_available: bool = False
    drs_active: bool = False
    drs_drag_reduction: float = 0.15      # 15% drag reduction when active
    
    # Aerodynamic coefficients
    drag_coefficient: float = 0.85        # Cd
    downforce_coefficient: float = -3.5   # Cl (negative = downforce)
    balance: float = 0.45                 # Aero balance (0.0=front, 1.0=rear)
    
    # Component condition
    front_wing_condition: float = 1.0
    rear_wing_condition: float = 1.0
    floor_condition: float = 1.0
    bodywork_condition: float = 1.0
    
    # Damage tracking
    front_wing_damage: float = 0.0
    rear_wing_damage: float = 0.0
    floor_damage: float = 0.0
    
    # Usage statistics
    km_traveled: float = 0.0
    drs_activations: int = 0
    
    def activate_drs(self):
        """Activate DRS system"""
        if self.drs_available and not self.drs_active:
            self.drs_active = True
            self.drs_activations += 1
    
    def deactivate_drs(self):
        """Deactivate DRS system"""
        self.drs_active = False
    
    def get_effective_drag(self) -> float:
        """Calculate current drag coefficient including DRS effect"""
        base_drag = self.drag_coefficient * self.bodywork_condition
        
        if self.drs_active:
            return base_drag * (1.0 - self.drs_drag_reduction)
        
        return base_drag
    
    def get_effective_downforce(self) -> float:
        """Calculate current downforce coefficient including damage"""
        wing_multiplier = (self.front_wing_condition + self.rear_wing_condition) / 2.0
        floor_multiplier = self.floor_condition
        
        return self.downforce_coefficient * wing_multiplier * floor_multiplier
    
    def apply_damage(self, component: str, severity: float):
        """
        Apply damage to aerodynamic component
        
        Args:
            component: Component name ('front_wing', 'rear_wing', 'floor', 'bodywork')
            severity: Damage severity (0.0-1.0)
        """
        damage = severity * 0.5  # Max 50% damage per incident
        
        if component == 'front_wing':
            self.front_wing_damage += damage
            self.front_wing_condition -= damage
        elif component == 'rear_wing':
            self.rear_wing_damage += damage
            self.rear_wing_condition -= damage
        elif component == 'floor':
            self.floor_damage += damage
            self.floor_condition -= damage
        elif component == 'bodywork':
            self.bodywork_condition -= damage
        
        self._clamp_conditions()
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate aerodynamic component wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        # Aero components wear from vibration and debris
        self.front_wing_condition -= 0.0003 * wear_factor
        self.rear_wing_condition -= 0.0002 * wear_factor
        self.floor_condition -= 0.0004 * wear_factor  # Floor takes more abuse
        self.bodywork_condition -= 0.0002 * wear_factor
        
        self._clamp_conditions()
    
    def get_overall_condition(self) -> float:
        """Calculate overall aerodynamic package health"""
        return (self.front_wing_condition * 0.3 +
                self.rear_wing_condition * 0.3 +
                self.floor_condition * 0.25 +
                self.bodywork_condition * 0.15)
    
    def requires_repair(self) -> bool:
        """Check if aero package needs repair"""
        return (self.front_wing_condition < 0.5 or 
                self.rear_wing_condition < 0.5 or 
                self.floor_condition < 0.4)
    
    def repair(self, component: Optional[str] = None):
        """
        Repair aerodynamic components
        
        Args:
            component: Specific component to repair, or None for full repair
        """
        if component is None or component == 'front_wing':
            self.front_wing_condition = 1.0
            self.front_wing_damage = 0.0
        if component is None or component == 'rear_wing':
            self.rear_wing_condition = 1.0
            self.rear_wing_damage = 0.0
        if component is None or component == 'floor':
            self.floor_condition = 1.0
            self.floor_damage = 0.0
        if component is None or component == 'bodywork':
            self.bodywork_condition = 1.0
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.front_wing_condition = max(0.0, min(1.0, self.front_wing_condition))
        self.rear_wing_condition = max(0.0, min(1.0, self.rear_wing_condition))
        self.floor_condition = max(0.0, min(1.0, self.floor_condition))
        self.bodywork_condition = max(0.0, min(1.0, self.bodywork_condition))
        self.front_wing_damage = max(0.0, min(1.0, self.front_wing_damage))
        self.rear_wing_damage = max(0.0, min(1.0, self.rear_wing_damage))
        self.floor_damage = max(0.0, min(1.0, self.floor_damage))


@dataclass
class Tire:
    """
    Individual Tire Model
    
    Represents a single tire with wear, temperature, and performance characteristics.
    """
    tire_type: TireType
    compound: TireCompound
    position: str                         # 'FL', 'FR', 'RL', 'RR'
    
    # Physical characteristics
    width_mm: int = 305
    diameter_inches: int = 18
    pressure_psi: float = 24.0
    
    # Condition and wear
    tread_wear: float = 1.0               # 1.0 = new, 0.0 = worn out
    structural_integrity: float = 1.0     # Overall tire health
    
    # Temperature zones (°C)
    temp_inner: float = 70.0
    temp_middle: float = 75.0
    temp_outer: float = 70.0
    optimal_temp_range: tuple = (80.0, 110.0)
    
    # Performance characteristics
    grip_level: float = 1.0               # Current grip (0.0-1.0)
    graining: float = 0.0                 # Surface graining (0.0-1.0)
    blistering: float = 0.0               # Heat blistering (0.0-1.0)
    
    # Usage statistics
    km_traveled: float = 0.0
    laps_completed: int = 0
    flat_spots: int = 0
    
    def simulate_wear(self, intensity: float, track_abrasiveness: float, duration_seconds: float):
        """
        Simulate tire wear during running
        
        Args:
            intensity: Driving intensity (0.0-1.0)
            track_abrasiveness: Track surface abrasiveness (0.0-1.0)
            duration_seconds: Duration of running
        """
        # Base wear rate varies by compound
        compound_wear_rates = {
            TireCompound.SUPER_SOFT: 0.0012,
            TireCompound.SOFT: 0.0008,
            TireCompound.MEDIUM: 0.0005,
            TireCompound.HARD: 0.0003,
            TireCompound.SUPER_HARD: 0.0002,
            TireCompound.WET: 0.0004,
            TireCompound.INTERMEDIATE: 0.0006
        }
        
        base_wear = compound_wear_rates.get(self.compound, 0.0005)
        wear = base_wear * intensity * track_abrasiveness * (duration_seconds / 60.0)
        
        self.tread_wear -= wear
        
        # Temperature effects
        avg_temp = (self.temp_inner + self.temp_middle + self.temp_outer) / 3.0
        
        # Overheating causes blistering
        if avg_temp > self.optimal_temp_range[1] + 20:
            self.blistering += 0.001 * (duration_seconds / 60.0)
        
        # Too cold causes graining
        if avg_temp < self.optimal_temp_range[0] - 10:
            self.graining += 0.001 * (duration_seconds / 60.0)
        
        self._update_grip()
        self._clamp_conditions()
    
    def heat_tire(self, energy: float):
        """
        Heat tire from driving
        
        Args:
            energy: Heat energy input (arbitrary units)
        """
        # Distribute heat across tire zones
        self.temp_inner += energy * 0.8
        self.temp_middle += energy * 1.0
        self.temp_outer += energy * 0.9
    
    def cool_tire(self, duration_seconds: float, ambient_temp: float = 25.0, cooling_factor: float = 0.05):
        """
        Cool tire naturally
        
        Args:
            duration_seconds: Duration of cooling
            ambient_temp: Ambient temperature (°C)
            cooling_factor: Cooling efficiency
        """
        cooling = cooling_factor * (duration_seconds / 60.0)
        
        self.temp_inner -= (self.temp_inner - ambient_temp) * cooling
        self.temp_middle -= (self.temp_middle - ambient_temp) * cooling
        self.temp_outer -= (self.temp_outer - ambient_temp) * cooling
    
    def apply_lockup(self):
        """Apply damage from wheel lockup"""
        self.tread_wear -= 0.02
        self.flat_spots += 1
        self.structural_integrity -= 0.01
        self._clamp_conditions()
    
    def _update_grip(self):
        """Update grip level based on wear, temperature, and degradation"""
        # Temperature factor
        avg_temp = (self.temp_inner + self.temp_middle + self.temp_outer) / 3.0
        
        if self.optimal_temp_range[0] <= avg_temp <= self.optimal_temp_range[1]:
            temp_factor = 1.0
        elif avg_temp < self.optimal_temp_range[0]:
            # Cold tires
            temp_factor = 0.7 + 0.3 * (avg_temp / self.optimal_temp_range[0])
        else:
            # Hot tires
            excess = avg_temp - self.optimal_temp_range[1]
            temp_factor = max(0.6, 1.0 - (excess / 100.0))
        
        # Wear factor (grip drops off more rapidly below 50% tread)
        if self.tread_wear > 0.5:
            wear_factor = 0.9 + 0.1 * self.tread_wear
        else:
            wear_factor = 0.5 + 0.4 * (self.tread_wear / 0.5)
        
        # Degradation factors
        degradation_factor = 1.0 - (self.graining * 0.2 + self.blistering * 0.3)
        
        self.grip_level = temp_factor * wear_factor * degradation_factor * self.structural_integrity
    
    def get_avg_temperature(self) -> float:
        """Get average tire temperature"""
        return (self.temp_inner + self.temp_middle + self.temp_outer) / 3.0
    
    def is_optimal_temperature(self) -> bool:
        """Check if tire is in optimal temperature range"""
        avg_temp = self.get_avg_temperature()
        return self.optimal_temp_range[0] <= avg_temp <= self.optimal_temp_range[1]
    
    def requires_replacement(self) -> bool:
        """Check if tire needs replacement"""
        return (self.tread_wear < 0.1 or 
                self.structural_integrity < 0.3 or 
                self.flat_spots > 2)
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.tread_wear = max(0.0, min(1.0, self.tread_wear))
        self.structural_integrity = max(0.0, min(1.0, self.structural_integrity))
        self.grip_level = max(0.0, min(1.0, self.grip_level))
        self.graining = max(0.0, min(1.0, self.graining))
        self.blistering = max(0.0, min(1.0, self.blistering))


@dataclass
class TireSet:
    """
    Complete Set of Four Tires
    
    Manages all four tires as a coordinated set.
    """
    front_left: Tire
    front_right: Tire
    rear_left: Tire
    rear_right: Tire
    
    # Set information
    set_age: int = 0                      # Number of sessions used
    total_km: float = 0.0
    
    def simulate_wear(self, intensity: float, track_abrasiveness: float, duration_seconds: float):
        """Simulate wear for all four tires"""
        self.front_left.simulate_wear(intensity, track_abrasiveness, duration_seconds)
        self.front_right.simulate_wear(intensity, track_abrasiveness, duration_seconds)
        self.rear_left.simulate_wear(intensity, track_abrasiveness, duration_seconds)
        self.rear_right.simulate_wear(intensity, track_abrasiveness, duration_seconds)
    
    def get_average_grip(self) -> float:
        """Get average grip across all tires"""
        return (self.front_left.grip_level + 
                self.front_right.grip_level + 
                self.rear_left.grip_level + 
                self.rear_right.grip_level) / 4.0
    
    def get_average_wear(self) -> float:
        """Get average tread wear across all tires"""
        return (self.front_left.tread_wear + 
                self.front_right.tread_wear + 
                self.rear_left.tread_wear + 
                self.rear_right.tread_wear) / 4.0
    
    def get_average_temperature(self) -> float:
        """Get average temperature across all tires"""
        return (self.front_left.get_avg_temperature() + 
                self.front_right.get_avg_temperature() + 
                self.rear_left.get_avg_temperature() + 
                self.rear_right.get_avg_temperature()) / 4.0
    
    def all_tires_optimal_temp(self) -> bool:
        """Check if all tires are at optimal temperature"""
        return (self.front_left.is_optimal_temperature() and
                self.front_right.is_optimal_temperature() and
                self.rear_left.is_optimal_temperature() and
                self.rear_right.is_optimal_temperature())
    
    def requires_replacement(self) -> bool:
        """Check if any tire needs replacement"""
        return (self.front_left.requires_replacement() or
                self.front_right.requires_replacement() or
                self.rear_left.requires_replacement() or
                self.rear_right.requires_replacement())


__all__ = ['AerodynamicsPackage', 'Tire', 'TireSet']
