"""
Vehicles Package

Complete vehicle component system for multi-discipline racing simulation.

Authors: Final Year Project - Computer Science
"""

from .vehicle import RaceCar
from .components.enums import (
    RacingDiscipline,
    AspirationType,
    FuelSystem,
    HybridSystemType,
    GearboxType,
    DifferentialType,
    SuspensionType,
    TireType,
    TireCompound,
    BrakeMaterial,
    AeroConfiguration,
    ControlUnitType,
    SteeringType
)
from .components.engine import EngineComponent, HybridPowerUnit
from .components.drivetrain import Gearbox, Differential, Drivetrain
from .components.chassis import Suspension, BrakeSystem, Chassis
from .components.aerodynamics import AerodynamicsPackage, Tire, TireSet
from .components.electronics import ElectronicControlUnit, SteeringSystem, SafetySystem

__all__ = [
    # Main vehicle
    'RaceCar',
    
    # Enums
    'RacingDiscipline',
    'AspirationType',
    'FuelSystem',
    'HybridSystemType',
    'GearboxType',
    'DifferentialType',
    'SuspensionType',
    'TireType',
    'TireCompound',
    'BrakeMaterial',
    'AeroConfiguration',
    'ControlUnitType',
    'SteeringType',
    
    # Engine components
    'EngineComponent',
    'HybridPowerUnit',
    
    # Drivetrain components
    'Gearbox',
    'Differential',
    'Drivetrain',
    
    # Chassis components
    'Suspension',
    'BrakeSystem',
    'Chassis',
    
    # Aerodynamics components
    'AerodynamicsPackage',
    'Tire',
    'TireSet',
    
    # Electronics components
    'ElectronicControlUnit',
    'SteeringSystem',
    'SafetySystem'
]
