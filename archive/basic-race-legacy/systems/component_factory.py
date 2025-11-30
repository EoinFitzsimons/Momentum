"""
Component Factory System

Bridges the gap between abstract development levels (0.0-1.0) and 
concrete component instances with realistic physics simulation.

This factory instantiates detailed component objects based on:
- Development level from vehicle_development system
- Racing discipline requirements
- Team budget and expertise

Authors: Final Year Project - Computer Science
"""

from typing import Optional, Dict, Any
import math

from vehicles.components.engine import EngineComponent, HybridPowerUnit
from vehicles.components.aerodynamics import AerodynamicsPackage, Tire, TireSet
from vehicles.components.chassis import Suspension, BrakeSystem, Chassis
from vehicles.components.drivetrain import Gearbox, Differential, Drivetrain
from vehicles.components.electronics import ElectronicControlUnit, SteeringSystem, SafetySystem
from vehicles.components.enums import *
from vehicles.vehicle import RaceCar


class ComponentFactory:
    """
    Creates realistic component instances from development levels
    
    Maps abstract 0.0-1.0 development levels to concrete component
    specifications appropriate for each racing discipline.
    """
    
    def __init__(self):
        self.discipline_specs = self._initialize_discipline_specifications()
    
    def create_race_car(self, car_id: int, team_id: int, discipline: str,
                       car_name: str, development_levels: Dict[str, float],
                       team_budget: float = 50.0) -> RaceCar:
        """
        Create a complete RaceCar with all components
        
        Args:
            car_id: Unique car identifier
            team_id: Team that owns the car
            discipline: Racing discipline
            car_name: Car name/designation
            development_levels: Dict of component development levels (0.0-1.0)
            team_budget: Team's budget level for component quality
            
        Returns:
            Fully configured RaceCar instance
        """
        discipline_enum = self._get_discipline_enum(discipline)
        
        # Create all components based on development levels
        engine = self.create_engine(discipline, development_levels.get('engine', 0.5), team_budget)
        hybrid = self.create_hybrid_unit(discipline, development_levels.get('electronics', 0.5))
        drivetrain = self.create_drivetrain(discipline, development_levels.get('transmission', 0.5))
        chassis = self.create_chassis(discipline, development_levels.get('chassis', 0.5))
        aero = self.create_aerodynamics(discipline, development_levels.get('aerodynamics', 0.5))
        tires = self.create_tire_set(discipline, development_levels.get('tires', 0.5))
        ecu = self.create_ecu(discipline, development_levels.get('electronics', 0.5))
        steering = self.create_steering(discipline, development_levels.get('suspension', 0.5))
        safety = self.create_safety_system(discipline, development_levels.get('safety', 0.5))
        
        # Calculate vehicle mass based on discipline and components
        total_mass = self._calculate_vehicle_mass(discipline, development_levels)
        weight_dist = development_levels.get('weight_distribution', 0.5)
        
        return RaceCar(
            car_id=car_id,
            team_id=team_id,
            discipline=discipline_enum,
            car_name=car_name,
            engine=engine,
            hybrid_unit=hybrid,
            drivetrain=drivetrain,
            chassis=chassis,
            aerodynamics=aero,
            tires=tires,
            ecu=ecu,
            steering=steering,
            safety=safety,
            total_mass=total_mass,
            weight_distribution=0.45 + (weight_dist * 0.1),  # 0.45-0.55 range
            wheelbase=self._get_wheelbase(discipline),
            track_width_front=self._get_track_width_front(discipline),
            track_width_rear=self._get_track_width_rear(discipline)
        )
    
    def create_engine(self, discipline: str, dev_level: float, 
                     budget: float = 50.0) -> Optional[EngineComponent]:
        """Create engine component based on discipline and development level"""
        specs = self.discipline_specs.get(discipline, {}).get('engine', {})
        
        if not specs:
            return None
        
        # Scale performance based on development level
        max_power = specs['base_power'] * (0.7 + (dev_level * 0.6))  # 70%-130% of base
        max_torque = specs['base_torque'] * (0.7 + (dev_level * 0.6))
        
        # Higher development = better reliability
        reliability = 0.7 + (dev_level * 0.25)  # 0.70-0.95
        
        return EngineComponent(
            displacement=specs['displacement'],
            cylinders=specs['cylinders'],
            configuration=specs['configuration'],
            aspiration=specs['aspiration'],
            fuel_system=specs['fuel_system'],
            fuel_type=specs['fuel_type'],
            max_power_bhp=max_power,
            max_power_rpm=specs['max_power_rpm'],
            max_torque_nm=max_torque,
            max_torque_rpm=specs['max_torque_rpm'],
            redline_rpm=specs['redline_rpm'],
            idle_rpm=specs['idle_rpm'],
            reliability_rating=reliability,
            fuel_consumption_rate=1.0 - (dev_level * 0.2)  # Better dev = more efficient
        )
    
    def create_hybrid_unit(self, discipline: str, dev_level: float) -> Optional[HybridPowerUnit]:
        """Create hybrid power unit if applicable to discipline"""
        # Only certain disciplines use hybrid systems
        hybrid_disciplines = ['SINGLE_SEATER', 'ENDURANCE']
        
        if discipline not in hybrid_disciplines or dev_level < 0.3:
            return None
        
        capacity = 4.0 if discipline == 'SINGLE_SEATER' else 8.0  # kWh
        
        return HybridPowerUnit(
            system_type=HybridSystemType.FULL_HYBRID,
            storage_type=EnergyStorageType.LITHIUM_ION,
            capacity_kwh=capacity,
            max_deployment_rate_kw=120.0 * (0.7 + dev_level * 0.6),
            max_harvest_rate_kw=100.0 * (0.7 + dev_level * 0.6),
            efficiency=0.85 + (dev_level * 0.1),  # 85%-95% efficient
            ers_mode=ERSMode.BALANCED
        )
    
    def create_drivetrain(self, discipline: str, dev_level: float) -> Drivetrain:
        """Create drivetrain based on discipline requirements"""
        specs = self.discipline_specs.get(discipline, {}).get('drivetrain', {})
        
        # Create gearbox
        num_gears = specs.get('num_gears', 6)
        gear_ratios = self._calculate_gear_ratios(num_gears, discipline)
        
        shift_time = 200.0 * (1.5 - dev_level)  # Better dev = faster shifts (50-200ms)
        
        gearbox = Gearbox(
            gearbox_type=specs.get('gearbox_type', GearboxType.SEQUENTIAL),
            num_gears=num_gears,
            gear_ratios=gear_ratios,
            final_drive_ratio=specs.get('final_drive', 3.5),
            shift_time_ms=shift_time,
            max_input_torque_nm=800.0 + (dev_level * 400.0)
        )
        
        # Create differential
        diff = Differential(
            diff_type=specs.get('diff_type', DifferentialType.LSD),
            preload=50.0 + (dev_level * 50.0),
            power_lock_percent=40.0 + (dev_level * 40.0),
            coast_lock_percent=30.0 + (dev_level * 30.0)
        )
        
        # Combine into drivetrain
        return Drivetrain(
            layout=specs.get('layout', DrivetrainLayout.RWD),
            gearbox=gearbox,
            differential=diff,
            transmission_efficiency=0.90 + (dev_level * 0.08)  # 90%-98%
        )
    
    def create_chassis(self, discipline: str, dev_level: float) -> Chassis:
        """Create chassis based on discipline"""
        specs = self.discipline_specs.get(discipline, {}).get('chassis', {})
        
        # Better development = lighter, stronger chassis
        base_weight = specs.get('base_weight', 600.0)
        weight = base_weight * (1.1 - dev_level * 0.2)  # Up to 20% lighter
        
        return Chassis(
            material=specs.get('material', ChassisMaterial.CARBON_FIBER),
            weight_kg=weight,
            structural_integrity=1.0,
            weight_distribution=48.0 + (dev_level * 4.0),  # 48-52% front
            safety_rating=0.8 + (dev_level * 0.2)  # 0.8-1.0
        )
    
    def create_aerodynamics(self, discipline: str, dev_level: float) -> AerodynamicsPackage:
        """Create aerodynamics package"""
        specs = self.discipline_specs.get(discipline, {}).get('aero', {})
        
        # Better development = more downforce, less drag
        base_drag = specs.get('base_drag', 0.85)
        base_downforce = specs.get('base_downforce', -3.5)
        
        drag_coef = base_drag * (1.2 - dev_level * 0.4)  # Up to 40% reduction
        downforce_coef = base_downforce * (0.7 + dev_level * 0.6)  # Up to 60% increase
        
        return AerodynamicsPackage(
            configuration=specs.get('config', AeroConfiguration.MEDIUM_DOWNFORCE),
            front_wing_angle=8.0 + (dev_level * 8.0),
            rear_wing_angle=10.0 + (dev_level * 10.0),
            front_wing_type=WingType.TRIPLE_ELEMENT if dev_level > 0.7 else WingType.DOUBLE_ELEMENT,
            rear_wing_type=WingType.TRIPLE_ELEMENT,
            drs_available=discipline in ['SINGLE_SEATER'] and dev_level > 0.5,
            drag_coefficient=drag_coef,
            downforce_coefficient=downforce_coef,
            balance=0.40 + (dev_level * 0.1)  # 40-50% balance
        )
    
    def create_tire_set(self, discipline: str, dev_level: float) -> TireSet:
        """Create tire set for the discipline"""
        specs = self.discipline_specs.get(discipline, {}).get('tires', {})
        
        tire_type = specs.get('tire_type', TireType.SLICK)
        compound = specs.get('compound', TireCompound.MEDIUM)
        
        # Create individual tires
        fl = self._create_tire(tire_type, compound, 'FL', dev_level)
        fr = self._create_tire(tire_type, compound, 'FR', dev_level)
        rl = self._create_tire(tire_type, compound, 'RL', dev_level)
        rr = self._create_tire(tire_type, compound, 'RR', dev_level)
        
        return TireSet(
            front_left=fl,
            front_right=fr,
            rear_left=rl,
            rear_right=rr
        )
    
    def _create_tire(self, tire_type: TireType, compound: TireCompound, 
                    position: str, dev_level: float) -> Tire:
        """Create individual tire"""
        # Better development = better grip and wear characteristics
        base_grip = 1.0
        grip_modifier = 0.9 + (dev_level * 0.2)  # 90%-110% grip
        
        return Tire(
            tire_type=tire_type,
            compound=compound,
            position=position,
            width_mm=305 if position.startswith('R') else 270,
            diameter_inches=18,
            pressure_psi=24.0,
            grip_level=base_grip * grip_modifier
        )
    
    def create_ecu(self, discipline: str, dev_level: float) -> ElectronicControlUnit:
        """Create ECU and electronics"""
        specs = self.discipline_specs.get(discipline, {}).get('electronics', {})
        
        # More advanced ECU with higher development
        if dev_level > 0.8:
            ecu_type = ControlUnitType.ADVANCED_ECU
        elif dev_level > 0.5:
            ecu_type = ControlUnitType.STANDARD_ECU
        else:
            ecu_type = ControlUnitType.STANDARD_ECU
        
        return ElectronicControlUnit(
            ecu_type=ecu_type,
            traction_control=dev_level > 0.3,
            traction_control_level=int(dev_level * 12) if dev_level > 0.3 else 0,
            abs_enabled=dev_level > 0.4,
            abs_level=int(dev_level * 12) if dev_level > 0.4 else 0,
            stability_control=dev_level > 0.6,
            torque_vectoring=dev_level > 0.7,
            launch_control=dev_level > 0.5,
            drs_control=discipline == 'SINGLE_SEATER' and dev_level > 0.5,
            engine_maps=min(int(1 + dev_level * 4), 5),  # 1-5 maps
            telemetry_enabled=True,
            data_logging=dev_level > 0.3
        )
    
    def create_steering(self, discipline: str, dev_level: float) -> SteeringSystem:
        """Create steering system"""
        # Better development = more responsive steering
        steering_ratio = 16.0 - (dev_level * 4.0)  # 12.0-16.0 ratio
        
        return SteeringSystem(
            steering_type=SteeringType.ELECTRIC if dev_level > 0.6 else SteeringType.HYDRAULIC,
            steering_ratio=steering_ratio,
            max_lock_angle=35.0 + (dev_level * 10.0),
            assistance_level=0.5 + (dev_level * 0.3)
        )
    
    def create_safety_system(self, discipline: str, dev_level: float) -> SafetySystem:
        """Create safety equipment"""
        return SafetySystem(
            roll_cage_installed=True,
            roll_cage_material="Chromoly Steel" if dev_level < 0.6 else "Carbon Fiber Composite",
            fire_suppression_installed=dev_level > 0.3,
            fire_suppression_charges=2 if dev_level > 0.3 else 1,
            fia_certified=dev_level > 0.7,
            crash_structure_integrity=0.8 + (dev_level * 0.2),
            side_impact_protection=0.8 + (dev_level * 0.2)
        )
    
    def _calculate_gear_ratios(self, num_gears: int, discipline: str) -> list:
        """Calculate appropriate gear ratios for discipline"""
        # Base ratios for different disciplines
        ratio_patterns = {
            'SINGLE_SEATER': [3.5, 2.8, 2.3, 1.9, 1.6, 1.35, 1.15, 1.0],
            'RALLY_STAGE': [3.2, 2.4, 1.8, 1.4, 1.1, 0.9],
            'DRAG_ACCELERATION': [2.5, 1.8, 1.4, 1.0],
            'ENDURANCE': [3.8, 2.9, 2.3, 1.85, 1.5, 1.25, 1.05],
        }
        
        pattern = ratio_patterns.get(discipline, [3.5, 2.8, 2.3, 1.9, 1.6, 1.35])
        return pattern[:num_gears]
    
    def _calculate_vehicle_mass(self, discipline: str, dev_levels: Dict[str, float]) -> float:
        """Calculate total vehicle mass based on discipline and development"""
        base_masses = {
            'SINGLE_SEATER': 798.0,  # F1 minimum
            'PRODUCTION_TOURING': 1200.0,
            'RALLY_STAGE': 1230.0,
            'URBAN_STREET': 1150.0,
            'DRAG_ACCELERATION': 900.0,
            'SPRINT_RALLYCROSS': 1300.0,
            'ENDURANCE': 900.0  # LMP1 spec
        }
        
        base_mass = base_masses.get(discipline, 1000.0)
        
        # Better chassis and weight distribution development = lighter car
        chassis_dev = dev_levels.get('chassis', 0.5)
        weight_dev = dev_levels.get('weight_distribution', 0.5)
        
        weight_reduction = (chassis_dev + weight_dev) / 2 * 0.1  # Up to 10% lighter
        
        return base_mass * (1.0 - weight_reduction)
    
    def _get_wheelbase(self, discipline: str) -> float:
        """Get appropriate wheelbase for discipline (mm)"""
        wheelbases = {
            'SINGLE_SEATER': 3600.0,
            'PRODUCTION_TOURING': 2650.0,
            'RALLY_STAGE': 2500.0,
            'URBAN_STREET': 2600.0,
            'DRAG_ACCELERATION': 3000.0,
            'SPRINT_RALLYCROSS': 2550.0,
            'ENDURANCE': 4650.0  # LMP1
        }
        return wheelbases.get(discipline, 2700.0)
    
    def _get_track_width_front(self, discipline: str) -> float:
        """Get front track width (mm)"""
        return 1500.0  # Standard for most disciplines
    
    def _get_track_width_rear(self, discipline: str) -> float:
        """Get rear track width (mm)"""
        return 1450.0
    
    def _get_discipline_enum(self, discipline: str) -> RacingDiscipline:
        """Convert discipline string to enum"""
        mapping = {
            'SINGLE_SEATER': RacingDiscipline.SINGLE_SEATER,
            'PRODUCTION_TOURING': RacingDiscipline.PRODUCTION_TOURING,
            'RALLY_STAGE': RacingDiscipline.RALLY_STAGE,
            'URBAN_STREET': RacingDiscipline.URBAN_STREET,
            'DRAG_ACCELERATION': RacingDiscipline.DRAG_ACCELERATION,
            'SPRINT_RALLYCROSS': RacingDiscipline.SPRINT_RALLYCROSS,
            'ENDURANCE': RacingDiscipline.ENDURANCE
        }
        return mapping.get(discipline, RacingDiscipline.SINGLE_SEATER)
    
    def _initialize_discipline_specifications(self) -> Dict[str, Dict[str, Any]]:
        """Initialize base specifications for each discipline"""
        return {
            'SINGLE_SEATER': {
                'engine': {
                    'displacement': 1.6,
                    'cylinders': 6,
                    'configuration': EngineConfiguration.V6,
                    'aspiration': AspirationType.TURBOCHARGED,
                    'fuel_system': FuelSystem.DIRECT_INJECTION,
                    'fuel_type': FuelType.PETROL,
                    'base_power': 850.0,
                    'base_torque': 650.0,
                    'max_power_rpm': 12000,
                    'max_torque_rpm': 10500,
                    'redline_rpm': 15000,
                    'idle_rpm': 3000
                },
                'drivetrain': {
                    'num_gears': 8,
                    'gearbox_type': GearboxType.SEQUENTIAL,
                    'diff_type': DifferentialType.ELECTRONIC,
                    'layout': DrivetrainLayout.RWD,
                    'final_drive': 3.2
                },
                'chassis': {
                    'material': ChassisMaterial.CARBON_FIBER,
                    'base_weight': 100.0
                },
                'aero': {
                    'config': AeroConfiguration.HIGH_DOWNFORCE,
                    'base_drag': 0.75,
                    'base_downforce': -4.5
                },
                'tires': {
                    'tire_type': TireType.SLICK,
                    'compound': TireCompound.SOFT
                },
                'electronics': {}
            },
            'PRODUCTION_TOURING': {
                'engine': {
                    'displacement': 2.0,
                    'cylinders': 4,
                    'configuration': EngineConfiguration.INLINE_4,
                    'aspiration': AspirationType.TURBOCHARGED,
                    'fuel_system': FuelSystem.PORT_INJECTION,
                    'fuel_type': FuelType.PETROL,
                    'base_power': 350.0,
                    'base_torque': 450.0,
                    'max_power_rpm': 6500,
                    'max_torque_rpm': 4500,
                    'redline_rpm': 7500,
                    'idle_rpm': 900
                },
                'drivetrain': {
                    'num_gears': 6,
                    'gearbox_type': GearboxType.SEQUENTIAL,
                    'diff_type': DifferentialType.LSD,
                    'layout': DrivetrainLayout.FWD,
                    'final_drive': 3.9
                },
                'chassis': {
                    'material': ChassisMaterial.STEEL_TUBE,
                    'base_weight': 250.0
                },
                'aero': {
                    'config': AeroConfiguration.LOW_DOWNFORCE,
                    'base_drag': 0.32,
                    'base_downforce': -0.5
                },
                'tires': {
                    'tire_type': TireType.SLICK,
                    'compound': TireCompound.MEDIUM
                },
                'electronics': {}
            },
            'RALLY_STAGE': {
                'engine': {
                    'displacement': 1.6,
                    'cylinders': 4,
                    'configuration': EngineConfiguration.INLINE_4,
                    'aspiration': AspirationType.TURBOCHARGED,
                    'fuel_system': FuelSystem.DIRECT_INJECTION,
                    'fuel_type': FuelType.PETROL,
                    'base_power': 380.0,
                    'base_torque': 550.0,
                    'max_power_rpm': 6000,
                    'max_torque_rpm': 4000,
                    'redline_rpm': 8500,
                    'idle_rpm': 1000
                },
                'drivetrain': {
                    'num_gears': 6,
                    'gearbox_type': GearboxType.SEQUENTIAL,
                    'diff_type': DifferentialType.MECHANICAL_LSD,
                    'layout': DrivetrainLayout.AWD,
                    'final_drive': 3.7
                },
                'chassis': {
                    'material': ChassisMaterial.STEEL_TUBE,
                    'base_weight': 300.0
                },
                'aero': {
                    'config': AeroConfiguration.LOW_DOWNFORCE,
                    'base_drag': 0.35,
                    'base_downforce': -0.3
                },
                'tires': {
                    'tire_type': TireType.GRAVEL,
                    'compound': TireCompound.SOFT
                },
                'electronics': {}
            },
            'DRAG_ACCELERATION': {
                'engine': {
                    'displacement': 8.0,
                    'cylinders': 8,
                    'configuration': EngineConfiguration.V8,
                    'aspiration': AspirationType.SUPERCHARGED,
                    'fuel_system': FuelSystem.DIRECT_INJECTION,
                    'fuel_type': FuelType.METHANOL,
                    'base_power': 3500.0,
                    'base_torque': 2800.0,
                    'max_power_rpm': 8000,
                    'max_torque_rpm': 6500,
                    'redline_rpm': 9000,
                    'idle_rpm': 1500
                },
                'drivetrain': {
                    'num_gears': 3,
                    'gearbox_type': GearboxType.AUTOMATED_MANUAL,
                    'diff_type': DifferentialType.LSD,
                    'layout': DrivetrainLayout.RWD,
                    'final_drive': 2.8
                },
                'chassis': {
                    'material': ChassisMaterial.CHROMOLY,
                    'base_weight': 150.0
                },
                'aero': {
                    'config': AeroConfiguration.LOW_DOWNFORCE,
                    'base_drag': 0.28,
                    'base_downforce': -1.2
                },
                'tires': {
                    'tire_type': TireType.DRAG_SLICK,
                    'compound': TireCompound.SOFT
                },
                'electronics': {}
            },
            'ENDURANCE': {
                'engine': {
                    'displacement': 2.4,
                    'cylinders': 6,
                    'configuration': EngineConfiguration.V6,
                    'aspiration': AspirationType.TURBOCHARGED,
                    'fuel_system': FuelSystem.DIRECT_INJECTION,
                    'fuel_type': FuelType.PETROL,
                    'base_power': 650.0,
                    'base_torque': 700.0,
                    'max_power_rpm': 9000,
                    'max_torque_rpm': 7000,
                    'redline_rpm': 11000,
                    'idle_rpm': 2000
                },
                'drivetrain': {
                    'num_gears': 7,
                    'gearbox_type': GearboxType.SEQUENTIAL,
                    'diff_type': DifferentialType.ELECTRONIC,
                    'layout': DrivetrainLayout.AWD,
                    'final_drive': 3.4
                },
                'chassis': {
                    'material': ChassisMaterial.CARBON_FIBER,
                    'base_weight': 120.0
                },
                'aero': {
                    'config': AeroConfiguration.MEDIUM_DOWNFORCE,
                    'base_drag': 0.65,
                    'base_downforce': -3.2
                },
                'tires': {
                    'tire_type': TireType.SLICK,
                    'compound': TireCompound.MEDIUM
                },
                'electronics': {}
            }
        }


__all__ = ['ComponentFactory']
