"""
Vehicle Component Enumerations

Defines all classification types for vehicle components across all racing disciplines.
This provides a comprehensive taxonomy for building realistic race cars.

Authors: Final Year Project - Computer Science
"""

from enum import Enum


class RacingDiscipline(Enum):
    """Racing discipline categories - matches core.disciplines structure"""
    SINGLE_SEATER = "SINGLE_SEATER"
    PRODUCTION_TOURING = "PRODUCTION_TOURING"
    RALLY_STAGE = "RALLY_STAGE"
    URBAN_STREET = "URBAN_STREET"
    DRAG_ACCELERATION = "DRAG_ACCELERATION"
    SPRINT_RALLYCROSS = "SPRINT_RALLYCROSS"
    ENDURANCE = "ENDURANCE"


# ============================================================================
# ENGINE & POWERTRAIN ENUMS
# ============================================================================

class AspirationType(Enum):
    """Engine aspiration methods"""
    NATURALLY_ASPIRATED = "Naturally Aspirated"
    TURBOCHARGED = "Turbocharged"
    SUPERCHARGED = "Supercharged"
    TWINCHARGED = "Turbo + Supercharger"


class FuelSystem(Enum):
    """Fuel delivery systems"""
    CARBURETOR = "Carburetor"
    EFI = "Electronic Fuel Injection"
    DIRECT_INJECTION = "Direct Injection"
    PORT_INJECTION = "Port Injection"


class FuelType(Enum):
    """Fuel types for racing"""
    PETROL = "Petrol"
    DIESEL = "Diesel"
    ETHANOL = "Ethanol"
    E85 = "E85"
    METHANOL = "Methanol"
    HYDROGEN = "Hydrogen"
    ELECTRIC = "Electric"


class EngineConfiguration(Enum):
    """Engine cylinder configurations"""
    INLINE_3 = "Inline-3"
    INLINE_4 = "Inline-4"
    INLINE_5 = "Inline-5"
    INLINE_6 = "Inline-6"
    V6 = "V6"
    V8 = "V8"
    V10 = "V10"
    V12 = "V12"
    FLAT_4 = "Flat-4"
    FLAT_6 = "Flat-6"
    W12 = "W12"
    ROTARY = "Rotary"


# ============================================================================
# HYBRID & ELECTRIC SYSTEMS
# ============================================================================

class HybridSystemType(Enum):
    """Hybrid power unit types"""
    NONE = "None"
    KERS = "Kinetic Energy Recovery System"
    ERS_H = "Heat Energy Recovery (Turbo-MGU-H)"
    ERS_K = "Kinetic MGU-K"
    FULL_HYBRID = "Full Hybrid (MGU-H + MGU-K)"
    PHEV = "Plug-in Hybrid"
    ELECTRIC_ONLY = "Electric Only"


class EnergyStorageType(Enum):
    """Energy storage methods"""
    BATTERY = "Battery"
    SUPERCAPACITOR = "Supercapacitor"
    FLYWHEEL = "Flywheel"
    LITHIUM_ION = "Lithium-Ion Battery"
    SOLID_STATE = "Solid-State Battery"


class ERSMode(Enum):
    """Energy recovery strategy modes"""
    DEPLOYMENT = "Deployment"
    HARVESTING = "Harvesting"
    BALANCED = "Balanced"
    OFF = "Off"


# ============================================================================
# DRIVETRAIN ENUMS
# ============================================================================

class GearboxType(Enum):
    """Transmission types"""
    MANUAL = "Manual"
    SEQUENTIAL = "Sequential"
    SEMI_AUTO = "Semi-Automatic"
    DUAL_CLUTCH = "Dual-Clutch (DCT)"
    CVT = "CVT"
    AUTOMATED_MANUAL = "Automated Manual"
    SINGLE_SPEED = "Single-Speed (Electric)"


class DifferentialType(Enum):
    """Differential configurations"""
    OPEN = "Open"
    LSD = "Limited Slip"
    TORSEN = "Torsen"
    ELECTRONIC = "Active Electronic"
    VISCOUS = "Viscous Coupling"
    MECHANICAL_LSD = "Mechanical LSD"


class DrivetrainLayout(Enum):
    """Drivetrain power distribution"""
    FWD = "Front-Wheel Drive"
    RWD = "Rear-Wheel Drive"
    AWD = "All-Wheel Drive"
    FOUR_WD = "4WD (Permanent)"


# ============================================================================
# CHASSIS & SUSPENSION
# ============================================================================

class SuspensionType(Enum):
    """Suspension configurations"""
    DOUBLE_WISHBONE = "Double Wishbone"
    MACPHERSON = "MacPherson Strut"
    PUSHROD = "Pushrod"
    PULLROD = "Pullrod"
    MULTI_LINK = "Multi-Link"
    SOLID_AXLE = "Solid Axle"
    TORSION_BEAM = "Torsion Beam"


class ChassisMaterial(Enum):
    """Chassis construction materials"""
    STEEL_TUBE = "Steel Tubular Frame"
    ALUMINUM = "Aluminum Monocoque"
    CARBON_FIBER = "Carbon Fiber Monocoque"
    COMPOSITE = "Composite Materials"
    CHROMOLY = "Chromoly Steel"


class DamperType(Enum):
    """Shock absorber types"""
    MONOTUBE = "Monotube"
    TWIN_TUBE = "Twin-Tube"
    ACTIVE = "Active Damping"
    MAGNETIC = "Magnetic Ride Control"


# ============================================================================
# BRAKING SYSTEMS
# ============================================================================

class BrakeMaterial(Enum):
    """Brake disc materials"""
    STEEL = "Steel"
    IRON = "Cast Iron"
    CARBON = "Carbon-Carbon"
    CERAMIC = "Carbon-Ceramic"
    CARBON_STEEL = "Carbon-Steel Hybrid"


class BrakeConfiguration(Enum):
    """Brake setup types"""
    DISC = "Disc Brakes"
    DRUM = "Drum Brakes"
    VENTILATED_DISC = "Ventilated Disc"
    DRILLED_DISC = "Drilled Disc"
    SLOTTED_DISC = "Slotted Disc"


# ============================================================================
# AERODYNAMICS
# ============================================================================

class AeroConfiguration(Enum):
    """Aerodynamic package types"""
    LOW_DOWNFORCE = "Low Downforce"
    MEDIUM_DOWNFORCE = "Medium Downforce"
    HIGH_DOWNFORCE = "High Downforce"
    MONZA_SPEC = "Monza Specification"
    MONACO_SPEC = "Monaco Specification"


class WingType(Enum):
    """Wing configurations"""
    SINGLE_ELEMENT = "Single Element"
    DOUBLE_ELEMENT = "Double Element"
    TRIPLE_ELEMENT = "Triple Element"
    DRS = "DRS (Drag Reduction System)"
    PASSIVE = "Passive"


# ============================================================================
# TIRES & WHEELS
# ============================================================================

class TireType(Enum):
    """Tire surface types"""
    SLICK = "Slick"
    WET = "Wet"
    INTERMEDIATE = "Intermediate"
    GRAVEL = "Gravel"
    SNOW = "Snow/Ice"
    DRAG_SLICK = "Drag Slick"
    ALL_TERRAIN = "All-Terrain"
    MUD = "Mud Terrain"


class TireCompound(Enum):
    """Tire rubber compounds"""
    SUPER_SOFT = "Super Soft (C5)"
    SOFT = "Soft (C4)"
    MEDIUM = "Medium (C3)"
    HARD = "Hard (C2)"
    SUPER_HARD = "Super Hard (C1)"
    WET = "Wet Weather"
    INTERMEDIATE = "Intermediate"


# ============================================================================
# ELECTRONICS & CONTROLS
# ============================================================================

class ControlUnitType(Enum):
    """Electronic control unit types"""
    STANDARD_ECU = "Standard ECU"
    ADVANCED_ECU = "Advanced ECU"
    TELEMETRY_CONTROL = "Telemetry-Enabled ECU"
    FIA_SPEC = "FIA-Spec ECU"
    CUSTOM = "Custom Development ECU"


class SteeringType(Enum):
    """Steering assistance types"""
    MANUAL = "Manual"
    HYDRAULIC = "Hydraulic"
    ELECTRIC = "Electric Power Steering"
    ELECTROHYDRAULIC = "Electrohydraulic"


# ============================================================================
# SAFETY SYSTEMS
# ============================================================================

class SafetyRating(Enum):
    """Safety equipment levels"""
    BASIC = "Basic Safety"
    INTERMEDIATE = "Intermediate Safety"
    ADVANCED = "Advanced Safety"
    FIA_GRADE_1 = "FIA Grade 1"
    FIA_GRADE_2 = "FIA Grade 2"


__all__ = [
    'RacingDiscipline',
    'AspirationType', 'FuelSystem', 'FuelType', 'EngineConfiguration',
    'HybridSystemType', 'EnergyStorageType', 'ERSMode',
    'GearboxType', 'DifferentialType', 'DrivetrainLayout',
    'SuspensionType', 'ChassisMaterial', 'DamperType',
    'BrakeMaterial', 'BrakeConfiguration',
    'AeroConfiguration', 'WingType',
    'TireType', 'TireCompound',
    'ControlUnitType', 'SteeringType',
    'SafetyRating'
]
