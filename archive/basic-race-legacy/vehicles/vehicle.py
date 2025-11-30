"""
Complete Vehicle Assembly Model

Integrates all vehicle components into a complete racing car.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from .components.enums import RacingDiscipline
from .components.engine import EngineComponent, HybridPowerUnit
from .components.drivetrain import Drivetrain
from .components.chassis import Chassis
from .components.aerodynamics import AerodynamicsPackage, TireSet
from .components.electronics import ElectronicControlUnit, SteeringSystem, SafetySystem


@dataclass
class RaceCar:
    """
    Complete Race Car Assembly
    
    Integrates all vehicle components into a functional racing car.
    Manages component interactions, overall performance, and discipline compliance.
    """
    # Identification
    car_id: int
    team_id: int
    discipline: RacingDiscipline
    car_name: str
    
    # Core Components
    engine: Optional[EngineComponent] = None
    hybrid_unit: Optional[HybridPowerUnit] = None
    drivetrain: Optional[Drivetrain] = None
    chassis: Optional[Chassis] = None
    aerodynamics: Optional[AerodynamicsPackage] = None
    tires: Optional[TireSet] = None
    ecu: Optional[ElectronicControlUnit] = None
    steering: Optional[SteeringSystem] = None
    safety: Optional[SafetySystem] = None
    
    # Overall vehicle metrics
    total_mass: float = 750.0             # kg (including driver)
    weight_distribution: float = 0.50     # Front/Rear (0.5 = 50/50)
    wheelbase: float = 2700.0             # mm
    track_width_front: float = 1500.0     # mm
    track_width_rear: float = 1450.0      # mm
    
    # Performance statistics
    total_race_distance: float = 0.0      # km
    total_race_time: float = 0.0          # hours
    crashes: int = 0
    dnfs: int = 0                         # Did Not Finish count
    
    # Regulatory compliance
    technical_inspection_passed: bool = False
    last_inspection_date: Optional[str] = None
    compliance_notes: List[str] = field(default_factory=list)
    
    def get_total_power(self) -> float:
        """
        Calculate total power output from all power sources
        
        Returns:
            Total power in horsepower
        """
        total_hp = 0.0
        
        if self.engine:
            total_hp += self.engine.get_power_output()
        
        if self.hybrid_unit and self.hybrid_unit.deployment_active:
            total_hp += self.hybrid_unit.get_available_power()
        
        return total_hp
    
    def get_power_to_weight_ratio(self) -> float:
        """
        Calculate power-to-weight ratio
        
        Returns:
            HP per kg
        """
        return self.get_total_power() / self.total_mass
    
    def get_overall_condition(self) -> float:
        """
        Calculate overall vehicle condition across all components
        
        Returns:
            Condition value (0.0-1.0)
        """
        conditions = []
        weights = []
        
        if self.engine:
            conditions.append(self.engine.get_overall_condition())
            weights.append(0.20)
        
        if self.hybrid_unit:
            conditions.append(self.hybrid_unit.get_overall_condition())
            weights.append(0.10)
        
        if self.drivetrain:
            conditions.append(self.drivetrain.get_overall_condition())
            weights.append(0.15)
        
        if self.chassis:
            conditions.append(self.chassis.get_overall_condition())
            weights.append(0.15)
        
        if self.aerodynamics:
            conditions.append(self.aerodynamics.get_overall_condition())
            weights.append(0.10)
        
        if self.tires:
            conditions.append(self.tires.get_overall_condition())
            weights.append(0.15)
        
        if self.ecu:
            conditions.append(self.ecu.get_overall_condition())
            weights.append(0.10)
        
        if self.steering:
            conditions.append(self.steering.get_overall_condition())
            weights.append(0.05)
        
        if not conditions:
            return 1.0
        
        # Weighted average
        total_weight = sum(weights)
        weighted_sum = sum(c * w for c, w in zip(conditions, weights))
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def simulate_session(self, duration_minutes: float, intensity: float):
        """
        Simulate a racing session, applying wear to all components
        
        Args:
            duration_minutes: Session duration in minutes
            intensity: Racing intensity (0.0-1.0)
        """
        if self.engine:
            self.engine.simulate_wear(intensity, duration_minutes)
        
        if self.hybrid_unit:
            self.hybrid_unit.simulate_wear(intensity, duration_minutes)
        
        if self.drivetrain:
            self.drivetrain.simulate_wear(intensity, duration_minutes)
        
        if self.chassis:
            self.chassis.simulate_wear(intensity, duration_minutes)
        
        if self.aerodynamics:
            self.aerodynamics.simulate_wear(intensity, duration_minutes)
        
        if self.tires:
            # Tires need to be simulated per lap/stint
            pass
        
        if self.ecu:
            self.ecu.simulate_wear(intensity, duration_minutes)
        
        if self.steering:
            self.steering.simulate_wear(intensity, duration_minutes)
        
        # Update statistics
        self.total_race_time += duration_minutes / 60.0
    
    def apply_crash_damage(self, severity: float):
        """
        Apply crash damage to relevant components
        
        Args:
            severity: Crash severity (0.0-1.0)
        """
        self.crashes += 1
        
        if self.chassis:
            self.chassis.apply_crash_damage(severity)
        
        if self.aerodynamics:
            self.aerodynamics.apply_crash_damage(severity)
        
        if self.safety:
            self.safety.apply_crash_damage(severity)
        
        # Severe crashes can damage mechanical components
        if severity > 0.7:
            if self.drivetrain:
                self.drivetrain.gearbox.condition -= severity * 0.2
            if self.engine:
                self.engine.block_condition -= severity * 0.15
    
    def requires_service(self) -> Dict[str, bool]:
        """
        Check which components require service
        
        Returns:
            Dictionary of component names and service requirements
        """
        service_needs = {}
        
        if self.engine:
            service_needs['engine'] = self.engine.requires_rebuild()
        
        if self.hybrid_unit:
            service_needs['hybrid'] = self.hybrid_unit.requires_service()
        
        if self.drivetrain:
            service_needs['drivetrain'] = self.drivetrain.requires_rebuild()
        
        if self.chassis:
            service_needs['chassis'] = self.chassis.requires_service()
        
        if self.aerodynamics:
            service_needs['aerodynamics'] = self.aerodynamics.requires_repair()
        
        if self.tires:
            service_needs['tires'] = self.tires.requires_change()
        
        if self.ecu:
            service_needs['ecu'] = self.ecu.requires_service()
        
        if self.steering:
            service_needs['steering'] = self.steering.requires_service()
        
        if self.safety:
            service_needs['safety'] = self.safety.requires_inspection()
        
        return service_needs
    
    def perform_full_service(self):
        """Perform complete service on all components"""
        if self.engine and self.engine.requires_rebuild():
            self.engine.rebuild()
        
        if self.hybrid_unit and self.hybrid_unit.requires_service():
            self.hybrid_unit.service()
        
        if self.drivetrain and self.drivetrain.requires_rebuild():
            self.drivetrain.rebuild()
        
        if self.chassis and self.chassis.requires_service():
            self.chassis.service()
        
        if self.aerodynamics and self.aerodynamics.requires_repair():
            self.aerodynamics.repair()
        
        if self.tires and self.tires.requires_change():
            # Note: Tire changes typically happen in-race, not service
            pass
        
        if self.ecu and self.ecu.requires_service():
            self.ecu.service()
        
        if self.steering and self.steering.requires_service():
            self.steering.service()
        
        if self.safety and self.safety.requires_inspection():
            self.safety.service()
    
    def check_discipline_compliance(self) -> bool:
        """
        Check if vehicle meets discipline-specific regulations
        
        Returns:
            True if compliant, False otherwise
        """
        # This is a placeholder - detailed regulations will be implemented
        # in the regulations module
        
        if not self.technical_inspection_passed:
            self.compliance_notes.append("Technical inspection not passed")
            return False
        
        # Basic component checks
        if not self.engine:
            self.compliance_notes.append("No engine installed")
            return False
        
        if not self.safety or not self.safety.roll_cage_installed:
            self.compliance_notes.append("Roll cage required")
            return False
        
        # Discipline-specific checks (simplified)
        if self.discipline == RacingDiscipline.SINGLE_SEATER:
            if not self.hybrid_unit:
                self.compliance_notes.append("Hybrid unit required for single-seater")
                return False
            if not self.aerodynamics or not self.aerodynamics.drs_installed:
                self.compliance_notes.append("DRS required for single-seater")
                return False
        
        return True
    
    def get_performance_summary(self) -> Dict[str, any]:
        """
        Get comprehensive performance summary
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'car_id': self.car_id,
            'car_name': self.car_name,
            'discipline': self.discipline.value,
            'total_power_hp': self.get_total_power(),
            'power_to_weight': self.get_power_to_weight_ratio(),
            'overall_condition': self.get_overall_condition(),
            'total_mass_kg': self.total_mass,
            'total_race_distance_km': self.total_race_distance,
            'total_race_time_hours': self.total_race_time,
            'crashes': self.crashes,
            'dnfs': self.dnfs,
            'technical_compliant': self.check_discipline_compliance()
        }


__all__ = ['RaceCar']
