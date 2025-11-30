"""
Component Manager System

Manages the lifecycle of vehicle components during races:
- Wear simulation during sessions
- Damage from incidents
- Repairs and replacements
- Performance degradation
- Syncing component state back to development system

Authors: Final Year Project - Computer Science
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random

from vehicles.vehicle import RaceCar
from vehicles.components.enums import TireCompound, TireType


@dataclass
class ComponentDamageEvent:
    """Records damage to a component"""
    component_name: str
    severity: float  # 0.0-1.0
    cause: str  # "crash", "wear", "mechanical_failure"
    lap_number: int
    session_type: str  # "practice", "qualifying", "race"


@dataclass
class RepairReport:
    """Report of repairs performed"""
    components_repaired: List[str]
    cost: float
    time_minutes: int
    success: bool


class ComponentManager:
    """
    Manages component state during race weekends
    
    Handles:
    - Session wear simulation
    - Crash damage
    - Component replacement
    - Performance calculations
    - Syncing state back to database
    """
    
    def __init__(self):
        self.damage_history: List[ComponentDamageEvent] = []
        self.repair_history: List[RepairReport] = []
    
    def simulate_session_wear(self, car: RaceCar, session_type: str,
                            duration_minutes: float, intensity: float = 0.8) -> Dict[str, float]:
        """
        Simulate component wear during a session
        
        Args:
            car: RaceCar instance
            session_type: "practice", "qualifying", "race"
            duration_minutes: Session duration
            intensity: Driving intensity (0.0-1.0)
            
        Returns:
            Dict of component condition changes
        """
        wear_report = {}
        
        # Engine wear
        if car.engine:
            before = car.engine.get_overall_condition()
            car.engine.simulate_wear(intensity, duration_minutes)
            after = car.engine.get_overall_condition()
            wear_report['engine'] = before - after
        
        # Hybrid unit wear
        if car.hybrid_unit:
            before = car.hybrid_unit.get_overall_condition()
            car.hybrid_unit.simulate_wear(intensity, duration_minutes)
            after = car.hybrid_unit.get_overall_condition()
            wear_report['hybrid_unit'] = before - after
        
        # Drivetrain wear
        if car.drivetrain:
            before = car.drivetrain.get_overall_condition()
            car.drivetrain.simulate_wear(intensity, duration_minutes)
            after = car.drivetrain.get_overall_condition()
            wear_report['drivetrain'] = before - after
        
        # Aerodynamics wear
        if car.aerodynamics:
            before = car.aerodynamics.get_overall_condition()
            car.aerodynamics.simulate_wear(intensity, duration_minutes)
            after = car.aerodynamics.get_overall_condition()
            wear_report['aerodynamics'] = before - after
        
        # Tire wear (track specific)
        if car.tires:
            track_abrasiveness = 0.7  # Default, should come from track model
            duration_seconds = duration_minutes * 60
            car.tires.simulate_wear(intensity, track_abrasiveness, duration_seconds)
            wear_report['tires'] = 1.0 - car.tires.get_average_wear()
        
        # Chassis (minimal wear during normal sessions)
        if car.chassis:
            before = car.chassis.get_overall_condition()
            car.chassis.simulate_wear(intensity, duration_minutes)
            after = car.chassis.get_overall_condition()
            wear_report['chassis'] = before - after
        
        return wear_report
    
    def apply_crash_damage(self, car: RaceCar, severity: float, 
                          lap_number: int, session_type: str,
                          components_affected: Optional[List[str]] = None) -> List[ComponentDamageEvent]:
        """
        Apply damage from a crash
        
        Args:
            car: RaceCar instance
            severity: Crash severity (0.0-1.0)
            lap_number: Lap when crash occurred
            session_type: Session type
            components_affected: Specific components hit, or None for random
            
        Returns:
            List of damage events
        """
        damage_events = []
        
        if components_affected is None:
            # Random damage based on severity
            components_affected = self._determine_crash_damage_components(severity)
        
        for component_name in components_affected:
            component_severity = severity * random.uniform(0.6, 1.0)
            
            if component_name == 'front_wing' and car.aerodynamics:
                car.aerodynamics.apply_damage('front_wing', component_severity)
                damage_events.append(ComponentDamageEvent(
                    'front_wing', component_severity, 'crash', lap_number, session_type
                ))
            
            elif component_name == 'rear_wing' and car.aerodynamics:
                car.aerodynamics.apply_damage('rear_wing', component_severity)
                damage_events.append(ComponentDamageEvent(
                    'rear_wing', component_severity, 'crash', lap_number, session_type
                ))
            
            elif component_name == 'floor' and car.aerodynamics:
                car.aerodynamics.apply_damage('floor', component_severity)
                damage_events.append(ComponentDamageEvent(
                    'floor', component_severity, 'crash', lap_number, session_type
                ))
            
            elif component_name == 'suspension' and car.drivetrain:
                # Suspension damage affects handling
                damage_events.append(ComponentDamageEvent(
                    'suspension', component_severity, 'crash', lap_number, session_type
                ))
            
            elif component_name == 'chassis' and car.chassis:
                car.chassis.apply_crash_damage(component_severity)
                damage_events.append(ComponentDamageEvent(
                    'chassis', component_severity, 'crash', lap_number, session_type
                ))
            
            elif component_name == 'gearbox' and car.drivetrain and car.drivetrain.gearbox:
                # Gearbox damage
                car.drivetrain.gearbox.reliability -= component_severity * 0.3
                damage_events.append(ComponentDamageEvent(
                    'gearbox', component_severity, 'crash', lap_number, session_type
                ))
        
        self.damage_history.extend(damage_events)
        return damage_events
    
    def change_tires(self, car: RaceCar, compound: TireCompound, 
                    tire_type: TireType) -> float:
        """
        Perform tire change
        
        Args:
            car: RaceCar instance
            compound: New tire compound
            tire_type: Tire type (slick, wet, etc.)
            
        Returns:
            Time taken for tire change (seconds)
        """
        from systems.component_factory import ComponentFactory
        
        factory = ComponentFactory()
        
        # Create new tire set
        # Use average development level for tires
        car.tires = factory.create_tire_set(
            car.discipline.value, 
            0.7  # Assume decent tire development
        )
        
        # Pit stop time varies by discipline
        pit_times = {
            'SINGLE_SEATER': 2.5,  # F1-style fast stops
            'PRODUCTION_TOURING': 4.0,
            'RALLY_STAGE': 8.0,  # Service park time
            'ENDURANCE': 3.5,
            'DRAG_ACCELERATION': 15.0,  # Full setup between runs
            'SPRINT_RALLYCROSS': 5.0,
            'URBAN_STREET': 4.0
        }
        
        return pit_times.get(car.discipline.value, 4.0)
    
    def repair_component(self, car: RaceCar, component_name: str, 
                        extent: float = 1.0) -> RepairReport:
        """
        Repair a specific component
        
        Args:
            car: RaceCar instance
            component_name: Component to repair
            extent: Repair extent (0.0-1.0, 1.0 = full repair)
            
        Returns:
            RepairReport with details
        """
        cost = 0.0
        time_minutes = 0
        success = True
        components_repaired = []
        
        if component_name == 'engine' and car.engine:
            if extent >= 1.0:
                car.engine.rebuild()
                cost = 5.0  # Million
                time_minutes = 480  # 8 hours
            else:
                car.engine.service()
                cost = 0.5
                time_minutes = 120
            components_repaired.append('engine')
        
        elif component_name == 'aerodynamics' and car.aerodynamics:
            car.aerodynamics.repair()
            cost = 0.2
            time_minutes = 60
            components_repaired.append('aerodynamics')
        
        elif component_name == 'gearbox' and car.drivetrain and car.drivetrain.gearbox:
            if extent >= 1.0:
                car.drivetrain.gearbox.rebuild()
                cost = 2.0
                time_minutes = 240
            else:
                # Minor service
                car.drivetrain.gearbox.reliability = min(1.0, car.drivetrain.gearbox.reliability + 0.1)
                cost = 0.3
                time_minutes = 90
            components_repaired.append('gearbox')
        
        elif component_name == 'chassis' and car.chassis:
            car.chassis.repair(extent)
            cost = extent * 3.0
            time_minutes = int(extent * 360)
            components_repaired.append('chassis')
        
        report = RepairReport(
            components_repaired=components_repaired,
            cost=cost,
            time_minutes=time_minutes,
            success=success
        )
        
        self.repair_history.append(report)
        return report
    
    def get_component_health_report(self, car: RaceCar) -> Dict[str, float]:
        """
        Get overall health of all components
        
        Returns:
            Dict mapping component names to condition (0.0-1.0)
        """
        report = {}
        
        if car.engine:
            report['engine'] = car.engine.get_overall_condition()
        
        if car.hybrid_unit:
            report['hybrid_unit'] = car.hybrid_unit.get_overall_condition()
        
        if car.drivetrain:
            report['drivetrain'] = car.drivetrain.get_overall_condition()
            if car.drivetrain.gearbox:
                report['gearbox'] = car.drivetrain.gearbox.get_overall_condition()
        
        if car.aerodynamics:
            report['aerodynamics'] = car.aerodynamics.get_overall_condition()
        
        if car.tires:
            report['tires'] = car.tires.get_average_wear()
            report['tire_grip'] = car.tires.get_average_grip()
        
        if car.chassis:
            report['chassis'] = car.chassis.get_overall_condition()
        
        if car.ecu:
            report['electronics'] = car.ecu.get_overall_condition()
        
        if car.steering:
            report['steering'] = car.steering.get_overall_condition()
        
        if car.safety:
            report['safety'] = car.safety.get_safety_rating()
        
        return report
    
    def sync_to_development_levels(self, car: RaceCar) -> Dict[str, float]:
        """
        Convert component conditions back to development levels
        
        Used to update the abstract development system after a race weekend.
        Component wear affects development levels.
        
        Returns:
            Dict of development levels (0.0-1.0)
        """
        health = self.get_component_health_report(car)
        
        # Map component health to development levels
        # Healthy components maintain dev level, worn ones decrease it
        dev_levels = {}
        
        if 'engine' in health:
            dev_levels['engine'] = health['engine'] * 0.95  # 5% degradation factor
        
        if 'aerodynamics' in health:
            dev_levels['aerodynamics'] = health['aerodynamics'] * 0.95
        
        if 'chassis' in health:
            dev_levels['chassis'] = health['chassis'] * 0.98  # Chassis degrades slower
        
        if 'electronics' in health:
            dev_levels['electronics'] = health['electronics'] * 0.97
        
        if 'gearbox' in health:
            dev_levels['transmission'] = health['gearbox'] * 0.96
        
        if 'drivetrain' in health:
            dev_levels['reliability'] = health['drivetrain'] * 0.95
        
        return dev_levels
    
    def requires_component_replacement(self, car: RaceCar) -> List[Tuple[str, float]]:
        """
        Check which components need replacement
        
        Returns:
            List of (component_name, condition) tuples for components below threshold
        """
        health = self.get_component_health_report(car)
        needs_replacement = []
        
        replacement_thresholds = {
            'engine': 0.3,
            'gearbox': 0.3,
            'hybrid_unit': 0.4,
            'tires': 0.2,
            'aerodynamics': 0.5,
            'chassis': 0.4
        }
        
        for component, condition in health.items():
            threshold = replacement_thresholds.get(component, 0.3)
            if condition < threshold:
                needs_replacement.append((component, condition))
        
        return needs_replacement
    
    def _determine_crash_damage_components(self, severity: float) -> List[str]:
        """Randomly determine which components are damaged in a crash"""
        damage_pool = [
            'front_wing', 'rear_wing', 'floor', 'suspension', 
            'chassis', 'gearbox'
        ]
        
        # More severe crashes damage more components
        num_damaged = int(1 + severity * 3)  # 1-4 components
        
        return random.sample(damage_pool, min(num_damaged, len(damage_pool)))
    
    def get_performance_multiplier(self, car: RaceCar) -> float:
        """
        Calculate overall performance multiplier based on component conditions
        
        Returns:
            Performance multiplier (0.0-1.0+)
        """
        health = self.get_component_health_report(car)
        
        # Weight different components
        weights = {
            'engine': 0.25,
            'aerodynamics': 0.20,
            'tires': 0.15,
            'tire_grip': 0.15,
            'chassis': 0.10,
            'gearbox': 0.08,
            'electronics': 0.07
        }
        
        total_performance = 0.0
        
        for component, weight in weights.items():
            if component in health:
                total_performance += health[component] * weight
        
        return min(total_performance, 1.0)


__all__ = ['ComponentManager', 'ComponentDamageEvent', 'RepairReport']
