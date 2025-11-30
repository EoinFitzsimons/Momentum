"""
Component System Integration

Integrates ComponentFactory and ComponentManager into the existing game flow.
Handles conversion between abstract development levels and concrete components.

Authors: Final Year Project - Computer Science
"""

from typing import Dict, Optional, List
import pickle
import json

from database.models.multi_discipline_models import Vehicle, MultiDisciplineTeam
from systems.component_factory import ComponentFactory
from systems.component_manager import ComponentManager
from systems.component_persistence import ComponentPersistence
from vehicles.vehicle import RaceCar


class ComponentIntegration:
    """
    Bridges abstract development system with concrete component instances
    
    Manages the dual-layer system:
    - Abstract layer: Development levels (0.0-1.0) for UI and progression
    - Concrete layer: Actual component instances for race simulation
    """
    
    def __init__(self, database_manager):
        self.db = database_manager
        self.factory = ComponentFactory()
        self.component_managers: Dict[int, ComponentManager] = {}  # car_id -> ComponentManager
        self.race_cars: Dict[int, RaceCar] = {}  # car_id -> RaceCar instance
        self.persistence = ComponentPersistence()
    
    def create_race_car_from_vehicle(self, vehicle: Vehicle, team: MultiDisciplineTeam) -> RaceCar:
        """
        Create a RaceCar instance from abstract Vehicle data
        
        Args:
            vehicle: Abstract vehicle with development levels
            team: Team that owns the vehicle
            
        Returns:
            Concrete RaceCar with all component instances
        """
        # Extract development levels from vehicle
        dev_levels = self._extract_development_levels(vehicle)
        
        # Create RaceCar using factory
        race_car = self.factory.create_race_car(
            car_id=vehicle.id,
            team_id=team.id,
            discipline=vehicle.discipline,
            car_name=f"{team.name} {vehicle.season_year}",
            development_levels=dev_levels,
            team_budget=team.budget
        )
        
        # Store race car and create component manager
        self.race_cars[vehicle.id] = race_car
        self.component_managers[vehicle.id] = ComponentManager()
        
        # Save to database
        self.persistence.save_race_car(vehicle.id, race_car, vehicle.season_year)
        
        return race_car
    
    def update_vehicle_from_race_car(self, vehicle: Vehicle, race_car: RaceCar) -> None:
        """
        Update abstract Vehicle development levels from RaceCar component states
        
        Args:
            vehicle: Abstract vehicle to update
            race_car: Concrete RaceCar with component states
        """
        manager = self.component_managers.get(race_car.car_id)
        if not manager:
            return
        
        # Get current component health
        dev_levels = manager.sync_to_development_levels(race_car)
        
        # Update vehicle attributes
        for component, level in dev_levels.items():
            if hasattr(vehicle, component):
                current = getattr(vehicle, component)
                # Apply degradation (never increase, only decrease from wear)
                new_level = min(current, level)
                setattr(vehicle, component, new_level)
        
        # Recalculate overall performance
        vehicle.overall_performance = self._calculate_overall_performance(vehicle)
    
    def simulate_race_session(self, vehicle_id: int, session_type: str, 
                             duration_minutes: float, intensity: float = 0.8) -> Dict:
        """
        Simulate a race session with component wear
        
        Args:
            vehicle_id: ID of the vehicle
            session_type: "practice", "qualifying", "race"
            duration_minutes: Session duration
            intensity: Driving intensity (0.0-1.0)
            
        Returns:
            Dict with session results and component wear report
        """
        race_car = self.race_cars.get(vehicle_id)
        manager = self.component_managers.get(vehicle_id)
        
        if not race_car or not manager:
            return {"error": "Vehicle not found or not initialized"}
        
        # Simulate component wear
        wear_report = manager.simulate_session_wear(
            race_car, session_type, duration_minutes, intensity
        )
        
        # Get final component health
        health_report = manager.get_component_health_report(race_car)
        
        # Calculate performance multiplier
        performance = manager.get_performance_multiplier(race_car)
        
        return {
            "wear_report": wear_report,
            "component_health": health_report,
            "performance_multiplier": performance,
            "session_type": session_type,
            "duration_minutes": duration_minutes
        }
    
    def handle_crash(self, vehicle_id: int, severity: float, lap_number: int,
                    session_type: str) -> Dict:
        """
        Handle crash damage to components
        
        Args:
            vehicle_id: ID of the vehicle
            severity: Crash severity (0.0-1.0)
            lap_number: Lap when crash occurred
            session_type: Session type
            
        Returns:
            Dict with damage report
        """
        race_car = self.race_cars.get(vehicle_id)
        manager = self.component_managers.get(vehicle_id)
        
        if not race_car or not manager:
            return {"error": "Vehicle not found"}
        
        damage_events = manager.apply_crash_damage(
            race_car, severity, lap_number, session_type
        )
        
        # Record damage events to database
        for event in damage_events:
            self.persistence.record_damage_event(
                vehicle_id, event.component_name, event.severity,
                event.cause, session_type, lap_number
            )
        
        return {
            "damage_events": damage_events,
            "requires_pit": severity > 0.3,
            "components_damaged": [e.component_name for e in damage_events],
            "total_damage": sum(e.severity for e in damage_events)
        }
    
    def perform_pit_stop(self, vehicle_id: int, operations: List[str]) -> Dict:
        """
        Perform pit stop operations
        
        Args:
            vehicle_id: ID of the vehicle
            operations: List of operations ("tire_change", "repair_wing", etc.)
            
        Returns:
            Dict with pit stop details
        """
        race_car = self.race_cars.get(vehicle_id)
        manager = self.component_managers.get(vehicle_id)
        
        if not race_car or not manager:
            return {"error": "Vehicle not found"}
        
        total_time = 0.0
        completed_ops = []
        
        for operation in operations:
            if operation == "tire_change":
                from vehicles.components.enums import TireCompound, TireType
                time = manager.change_tires(
                    race_car, 
                    TireCompound.SOFT,  # Default compound
                    TireType.SLICK
                )
                total_time += time
                completed_ops.append(f"Tire change: {time:.1f}s")
            
            elif operation.startswith("repair_"):
                component = operation.replace("repair_", "")
                report = manager.repair_component(race_car, component, extent=0.5)
                # Pit repair is quick but partial
                total_time += report.time_minutes * 60 / 10  # Scale down for pit lane
                completed_ops.append(f"Repaired {component}")
        
        return {
            "total_time_seconds": total_time,
            "operations_completed": completed_ops,
            "component_health": manager.get_component_health_report(race_car)
        }
    
    def get_component_health_ui(self, vehicle_id: int) -> Dict:
        """
        Get formatted component health for UI display
        
        Returns:
            Dict with component health percentages and status
        """
        race_car = self.race_cars.get(vehicle_id)
        manager = self.component_managers.get(vehicle_id)
        
        if not race_car or not manager:
            return {}
        
        health = manager.get_component_health_report(race_car)
        
        # Format for UI
        ui_data = {}
        for component, condition in health.items():
            percentage = int(condition * 100)
            
            if percentage >= 80:
                status = "Excellent"
                color = "green"
            elif percentage >= 60:
                status = "Good"
                color = "cyan"
            elif percentage >= 40:
                status = "Worn"
                color = "yellow"
            elif percentage >= 20:
                status = "Damaged"
                color = "orange"
            else:
                status = "Critical"
                color = "red"
            
            ui_data[component] = {
                "percentage": percentage,
                "status": status,
                "color": color,
                "value": condition
            }
        
        # Add replacement recommendations
        ui_data["needs_replacement"] = manager.requires_component_replacement(race_car)
        
        return ui_data
    
    def schedule_component_repair(self, vehicle_id: int, component: str, 
                                 extent: float = 1.0) -> Dict:
        """
        Schedule component repair between races
        
        Args:
            vehicle_id: ID of the vehicle
            component: Component to repair
            extent: Repair extent (0.0-1.0)
            
        Returns:
            Dict with repair details and costs
        """
        race_car = self.race_cars.get(vehicle_id)
        manager = self.component_managers.get(vehicle_id)
        
        if not race_car or not manager:
            return {"error": "Vehicle not found"}
        
        report = manager.repair_component(race_car, component, extent)
        
        # Record repair to database
        if report.success:
            self.persistence.record_repair(
                vehicle_id, report.components_repaired, report.cost,
                report.time_minutes / 60, report.success
            )
            # Save updated race car state
            race_car_obj = self.race_cars.get(vehicle_id)
            if race_car_obj:
                self.persistence.save_race_car(vehicle_id, race_car_obj, 2025)
        
        return {
            "success": report.success,
            "components_repaired": report.components_repaired,
            "cost_millions": report.cost,
            "time_required_hours": report.time_minutes / 60,
            "time_required_days": report.time_minutes / (60 * 24)
        }
    
    def sync_all_vehicles_after_race(self) -> None:
        """
        Sync all race cars back to abstract Vehicle models after a race weekend
        """
        for car_id, race_car in self.race_cars.items():
            manager = self.component_managers.get(car_id)
            if manager:
                # Sync component states
                dev_levels = manager.sync_to_development_levels(race_car)
                
                # Save race car state to database
                self.persistence.save_race_car(car_id, race_car, 2025)
                
                # Record component health snapshot
                health_report = manager.get_component_health_report(race_car)
                self.persistence.record_component_health(car_id, health_report)
    
    def save_component_states(self, filepath: str) -> None:
        """
        Save all component states to file
        
        Args:
            filepath: Path to save file
        """
        save_data = {
            "race_cars": {},
            "component_states": {}
        }
        
        for car_id, race_car in self.race_cars.items():
            # Pickle the RaceCar (dataclasses are picklable)
            save_data["race_cars"][car_id] = pickle.dumps(race_car)
            
            # Save component manager state
            manager = self.component_managers.get(car_id)
            if manager:
                save_data["component_states"][car_id] = {
                    "damage_history": [
                        {
                            "component": e.component_name,
                            "severity": e.severity,
                            "cause": e.cause,
                            "lap": e.lap_number,
                            "session": e.session_type
                        }
                        for e in manager.damage_history
                    ],
                    "repair_history": [
                        {
                            "components": r.components_repaired,
                            "cost": r.cost,
                            "time_minutes": r.time_minutes,
                            "success": r.success
                        }
                        for r in manager.repair_history
                    ]
                }
        
        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)
    
    def load_component_states(self, filepath: str) -> None:
        """
        Load component states from file
        
        Args:
            filepath: Path to save file
        """
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)
        
        # Restore race cars
        for car_id, pickled_car in save_data["race_cars"].items():
            self.race_cars[int(car_id)] = pickle.loads(pickled_car)
        
        # Restore component managers
        for car_id, state in save_data["component_states"].items():
            manager = ComponentManager()
            # Restore history (damage/repair events would need proper reconstruction)
            self.component_managers[int(car_id)] = manager
    
    def _extract_development_levels(self, vehicle: Vehicle) -> Dict[str, float]:
        """Extract development levels from Vehicle model"""
        return {
            "aerodynamics": vehicle.aerodynamics,
            "engine": getattr(vehicle, "engine_power", 0.5) or 0.5,
            "chassis": vehicle.chassis,
            "electronics": vehicle.electronics,
            "reliability": vehicle.reliability,
            "suspension": vehicle.suspension,
            "brakes": vehicle.brakes,
            "transmission": vehicle.transmission,
            "tires": vehicle.tires_compound,
            "cooling": getattr(vehicle, "cooling_systems", 0.5) if hasattr(vehicle, "cooling_systems") else 0.5,
            "fuel_system": getattr(vehicle, "fuel_efficiency", 0.5) if hasattr(vehicle, "fuel_efficiency") else 0.5,
            "safety": vehicle.safety_systems,
            "weight_distribution": getattr(vehicle, "weight_optimization", 0.5) if hasattr(vehicle, "weight_optimization") else 0.5
        }
    
    def _calculate_overall_performance(self, vehicle: Vehicle) -> float:
        """Calculate overall performance from component levels"""
        # Use development engine's component weights
        from systems.vehicle_development import VehicleDevelopmentEngine
        
        dev_engine = VehicleDevelopmentEngine()
        weights = dev_engine._get_component_weights(vehicle.discipline)
        
        dev_levels = self._extract_development_levels(vehicle)
        
        total = 0.0
        for component, weight in weights.items():
            total += dev_levels.get(component, 0.5) * weight
        
        return min(total, 1.0)


__all__ = ['ComponentIntegration']
