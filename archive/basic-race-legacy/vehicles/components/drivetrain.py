"""
Drivetrain Component Models

Models for gearbox, differential, and power transmission systems.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .enums import GearboxType, DifferentialType, DrivetrainLayout


@dataclass
class Gearbox:
    """
    Transmission/Gearbox Model
    
    Represents the complete gearbox assembly including gear ratios,
    shift characteristics, and wear simulation.
    """
    gearbox_type: GearboxType
    num_gears: int                        # Number of forward gears
    gear_ratios: List[float] = field(default_factory=list)  # Gear ratios for each gear
    final_drive_ratio: float = 3.5        # Final drive ratio
    
    # Performance characteristics
    shift_time_ms: float = 50.0           # Shift time in milliseconds
    max_input_torque_nm: float = 800.0    # Maximum torque capacity
    
    # Component condition
    reliability: float = 1.0              # Overall gearbox health
    clutch_condition: float = 1.0         # Clutch wear (if applicable)
    synchro_condition: float = 1.0        # Synchronizer condition
    gear_condition: List[float] = field(default_factory=list)  # Per-gear condition
    
    # Operational parameters
    current_gear: int = 1                 # Current gear engaged
    oil_temperature: float = 80.0         # Transmission oil temp (°C)
    optimal_temp_range: tuple = (80.0, 120.0)
    
    # Usage statistics
    total_shifts: int = 0
    km_traveled: float = 0.0
    
    def __post_init__(self):
        """Initialize gear-specific conditions if not provided"""
        if not self.gear_ratios:
            # Default ratios for a 6-speed sequential
            self.gear_ratios = [3.5, 2.5, 1.9, 1.5, 1.2, 1.0]
        
        if not self.gear_condition:
            self.gear_condition = [1.0] * self.num_gears
    
    def shift_up(self) -> bool:
        """
        Shift to next higher gear
        
        Returns:
            True if shift successful, False if already in top gear
        """
        if self.current_gear < self.num_gears:
            self.current_gear += 1
            self.total_shifts += 1
            self._apply_shift_wear()
            return True
        return False
    
    def shift_down(self) -> bool:
        """
        Shift to next lower gear
        
        Returns:
            True if shift successful, False if already in first gear
        """
        if self.current_gear > 1:
            self.current_gear -= 1
            self.total_shifts += 1
            self._apply_shift_wear()
            return True
        return False
    
    def shift_to_gear(self, gear: int) -> bool:
        """
        Shift directly to specified gear
        
        Args:
            gear: Target gear number (1-indexed)
        
        Returns:
            True if shift successful
        """
        if 1 <= gear <= self.num_gears:
            self.current_gear = gear
            self.total_shifts += 1
            self._apply_shift_wear()
            return True
        return False
    
    def get_current_ratio(self) -> float:
        """Get current total drive ratio"""
        gear_ratio = self.gear_ratios[self.current_gear - 1]
        return gear_ratio * self.final_drive_ratio
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate gearbox wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        # Overall reliability degradation
        self.reliability -= 0.0004 * wear_factor
        
        # Clutch wear (if applicable)
        if self.gearbox_type in [GearboxType.MANUAL, GearboxType.SEMI_AUTO]:
            self.clutch_condition -= 0.0008 * wear_factor
        
        # Synchronizer wear
        self.synchro_condition -= 0.0005 * wear_factor
        
        # Current gear wears faster
        if 0 <= self.current_gear - 1 < len(self.gear_condition):
            self.gear_condition[self.current_gear - 1] -= 0.0006 * wear_factor
        
        self._clamp_conditions()
    
    def _apply_shift_wear(self):
        """Apply wear from a single shift"""
        shift_wear = 0.00001
        self.reliability -= shift_wear
        
        if self.gearbox_type in [GearboxType.MANUAL, GearboxType.SEMI_AUTO]:
            self.clutch_condition -= shift_wear * 1.5
        
        self.synchro_condition -= shift_wear
    
    def get_overall_condition(self) -> float:
        """Calculate overall gearbox health"""
        avg_gear_condition = sum(self.gear_condition) / len(self.gear_condition)
        
        if self.gearbox_type in [GearboxType.MANUAL, GearboxType.SEMI_AUTO]:
            return (self.reliability * 0.4 + 
                   self.clutch_condition * 0.3 + 
                   avg_gear_condition * 0.2 + 
                   self.synchro_condition * 0.1)
        else:
            return (self.reliability * 0.5 + 
                   avg_gear_condition * 0.3 + 
                   self.synchro_condition * 0.2)
    
    def requires_rebuild(self) -> bool:
        """Check if gearbox needs rebuild"""
        return (self.reliability < 0.4 or 
                self.clutch_condition < 0.3 or 
                any(gc < 0.3 for gc in self.gear_condition))
    
    def rebuild(self):
        """Perform complete gearbox rebuild"""
        self.reliability = 1.0
        self.clutch_condition = 1.0
        self.synchro_condition = 1.0
        self.gear_condition = [1.0] * self.num_gears
        self.total_shifts = 0
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.reliability = max(0.0, min(1.0, self.reliability))
        self.clutch_condition = max(0.0, min(1.0, self.clutch_condition))
        self.synchro_condition = max(0.0, min(1.0, self.synchro_condition))
        self.gear_condition = [max(0.0, min(1.0, gc)) for gc in self.gear_condition]


@dataclass
class Differential:
    """
    Differential Model
    
    Represents the differential and its impact on power distribution
    and vehicle dynamics.
    """
    diff_type: DifferentialType
    preload: float = 50.0                 # Preload force (Nm) for LSD types
    
    # Locking characteristics (for LSD types)
    power_lock_percent: float = 60.0      # Locking under power
    coast_lock_percent: float = 40.0      # Locking under engine braking
    
    # Component condition
    condition: float = 1.0                # Overall differential health
    bearing_condition: float = 1.0        # Bearing wear
    gear_condition: float = 1.0           # Gear wear
    
    # Operational parameters
    oil_temperature: float = 90.0         # Diff oil temperature (°C)
    optimal_temp_range: tuple = (85.0, 105.0)
    
    # Usage statistics
    km_traveled: float = 0.0
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate differential wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        self.condition -= 0.0005 * wear_factor
        self.bearing_condition -= 0.0006 * wear_factor
        self.gear_condition -= 0.0004 * wear_factor
        
        # Electronic diffs have additional component wear
        if self.diff_type == DifferentialType.ELECTRONIC:
            self.condition -= 0.0002 * wear_factor
        
        self._clamp_conditions()
    
    def get_overall_condition(self) -> float:
        """Calculate overall differential health"""
        return (self.condition * 0.5 + 
                self.bearing_condition * 0.3 + 
                self.gear_condition * 0.2)
    
    def requires_rebuild(self) -> bool:
        """Check if differential needs rebuild"""
        return (self.condition < 0.4 or 
                self.bearing_condition < 0.3 or 
                self.gear_condition < 0.3)
    
    def rebuild(self):
        """Perform complete differential rebuild"""
        self.condition = 1.0
        self.bearing_condition = 1.0
        self.gear_condition = 1.0
    
    def service(self):
        """Perform routine service (oil change, minor adjustments)"""
        self.condition = min(1.0, self.condition + 0.05)
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.condition = max(0.0, min(1.0, self.condition))
        self.bearing_condition = max(0.0, min(1.0, self.bearing_condition))
        self.gear_condition = max(0.0, min(1.0, self.gear_condition))


@dataclass
class Drivetrain:
    """
    Complete Drivetrain Assembly
    
    Combines gearbox, differential, and drivetrain layout into a complete
    power transmission system.
    """
    layout: DrivetrainLayout
    gearbox: Gearbox
    differential: Differential
    
    # Additional components
    driveshaft_condition: float = 1.0
    cv_joints_condition: float = 1.0
    
    # Efficiency
    transmission_efficiency: float = 0.95  # Power transmission efficiency
    
    def get_power_to_wheels(self, engine_power: float) -> float:
        """
        Calculate power delivered to wheels after drivetrain losses
        
        Args:
            engine_power: Power from engine (BHP)
        
        Returns:
            Power at wheels (BHP)
        """
        gearbox_efficiency = self.gearbox.get_overall_condition()
        diff_efficiency = self.differential.get_overall_condition()
        
        total_efficiency = (self.transmission_efficiency * 
                           gearbox_efficiency * 
                           diff_efficiency)
        
        return engine_power * total_efficiency
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """Simulate complete drivetrain wear"""
        self.gearbox.simulate_wear(intensity, duration_minutes)
        self.differential.simulate_wear(intensity, duration_minutes)
        
        wear_factor = intensity * (duration_minutes / 60.0)
        self.driveshaft_condition -= 0.0003 * wear_factor
        self.cv_joints_condition -= 0.0004 * wear_factor
        
        self._clamp_conditions()
    
    def get_overall_condition(self) -> float:
        """Calculate overall drivetrain health"""
        return (self.gearbox.get_overall_condition() * 0.4 +
                self.differential.get_overall_condition() * 0.3 +
                self.driveshaft_condition * 0.15 +
                self.cv_joints_condition * 0.15)
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.driveshaft_condition = max(0.0, min(1.0, self.driveshaft_condition))
        self.cv_joints_condition = max(0.0, min(1.0, self.cv_joints_condition))


__all__ = ['Gearbox', 'Differential', 'Drivetrain']
