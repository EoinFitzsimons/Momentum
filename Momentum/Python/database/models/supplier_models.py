"""
Momentum Motorsport Simulation - Supplier & Manufacturer Models

This module defines the supplier ecosystem that provides components to racing teams.
Teams can either develop components in-house or purchase from external suppliers,
creating realistic business relationships and technical partnerships.

Supplier Categories:
- Engine/Powertrain Manufacturers (ICE, Electric, Hybrid)
- Tire Companies (Compound specialists for different disciplines)
- Chassis & Aerodynamics Suppliers
- Electronics & Data Systems
- Transmission & Drivetrain
- Brake System Manufacturers
- Suspension Specialists
- Fuel & Energy Suppliers
- Safety Equipment
- Specialty Components (Nitrous, Launch Systems, etc.)

Authors: Final Year Project - Computer Science
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum


class SupplierCategory(Enum):
    """Categories of component suppliers matching the vehicle components system"""
    # Engine & Powertrain (engine.py)
    ENGINE = "ENGINE"                                 # Internal combustion engines
    HYBRID_SYSTEM = "HYBRID_SYSTEM"                   # Hybrid power units (KERS, ERS-H, ERS-K)
    
    # Drivetrain (drivetrain.py)
    GEARBOX = "GEARBOX"                               # Transmissions and gearboxes
    DIFFERENTIAL = "DIFFERENTIAL"                     # Differentials (LSD, torque vectoring, etc.)
    DRIVETRAIN = "DRIVETRAIN"                         # Complete drivetrain assemblies
    
    # Chassis (chassis.py)
    CHASSIS = "CHASSIS"                               # Chassis structures (monocoque, tubular)
    SUSPENSION = "SUSPENSION"                         # Suspension systems (dampers, springs, ARB)
    BRAKES = "BRAKES"                                 # Brake systems (discs, calipers, cooling)
    
    # Aerodynamics (aerodynamics.py)
    AERODYNAMICS = "AERODYNAMICS"                     # Aerodynamic packages (wings, diffusers, DRS)
    
    # Tires (part of chassis/vehicle system)
    TIRES = "TIRES"                                   # Tire manufacturers and compounds
    
    # Electronics (electronics.py)
    ECU = "ECU"                                       # Electronic control units
    TELEMETRY = "TELEMETRY"                           # Telemetry and data systems
    STEERING = "STEERING"                             # Steering systems
    
    # Safety & Energy
    SAFETY = "SAFETY"                                 # Safety equipment (roll cage, fire suppression)
    FUEL_ENERGY = "FUEL_ENERGY"                      # Fuel, batteries, energy storage


class SupplierTier(Enum):
    """Quality and prestige tiers for suppliers"""
    PREMIUM = "PREMIUM"         # Top-tier suppliers (Ferrari, Mercedes, Brembo)
    PROFESSIONAL = "PROFESSIONAL"  # High-quality suppliers (Cosworth, Xtrac)
    COMPETITIVE = "COMPETITIVE"    # Mid-tier suppliers (good quality, reasonable price)
    BUDGET = "BUDGET"             # Cost-effective suppliers (lower performance)


@dataclass
class Supplier:
    """
    Component Supplier/Manufacturer Entity
    
    Represents companies that provide racing components to teams. Teams can
    choose to develop components in-house or purchase from these suppliers,
    creating realistic technical partnerships and business relationships.
    """
    # ===== CORE IDENTIFICATION =====
    id: int                                   # Unique supplier identifier
    name: str                                 # Company name (e.g., "Brembo", "Pirelli")
    nationality: str                          # Company's home country (ISO code)
    founded_year: int                         # Year company was established
    
    # ===== BUSINESS CLASSIFICATION =====
    category: str                             # SupplierCategory enum value
    tier: str                                 # SupplierTier enum value
    specializations: List[str]                # Specific component types they excel at
    
    # ===== COMPANY INFORMATION =====
    headquarters: str                         # Company's main location
    biography: str = ""                       # Company history and background
    racing_heritage: str = ""                 # Motorsport involvement history
    
    # ===== TECHNICAL CAPABILITIES =====
    # Overall quality ratings (0.0-1.0 scale)
    engineering_quality: float = 0.7         # Technical excellence of products
    manufacturing_precision: float = 0.7     # Build quality and consistency
    innovation_level: float = 0.6            # R&D and cutting-edge technology
    reliability_rating: float = 0.8          # Component durability and failure rates
    
    # ===== BUSINESS CHARACTERISTICS =====
    pricing_tier: float = 0.7                # Cost level (0.1=cheap, 1.0=premium)
    production_capacity: int = 100           # Max teams they can supply per season
    exclusivity_deals: bool = False          # Whether they do exclusive partnerships
    
    # Customer service and support
    technical_support_quality: float = 0.7   # Engineer support and development help
    delivery_reliability: float = 0.8        # On-time delivery and logistics
    customization_capability: float = 0.6    # Ability to create bespoke solutions
    
    # ===== DISCIPLINE FOCUS =====
    # Which racing disciplines this supplier serves (0.0-1.0 specialization)
    single_seater_focus: float = 0.5         # Formula racing specialization
    production_touring_focus: float = 0.5    # GT/Touring car specialization
    rally_stage_focus: float = 0.5           # Rally/WRC specialization
    urban_street_focus: float = 0.5          # Electric/Formula E specialization
    drag_acceleration_focus: float = 0.5     # Drag racing specialization
    sprint_rallycross_focus: float = 0.5     # Rallycross specialization
    endurance_focus: float = 0.5             # Long-distance racing specialization
    
    # ===== FINANCIAL DATA =====
    annual_revenue_millions: float = 50.0    # Company size indicator
    rd_investment_percentage: float = 0.15   # % of revenue spent on R&D
    market_share_percentage: float = 0.1     # Share of their component market
    
    # ===== PARTNERSHIP PREFERENCES =====
    preferred_team_tiers: Optional[List[str]] = None   # Which team tiers they prefer to work with
    minimum_contract_length: int = 1         # Minimum partnership duration (seasons)
    maximum_customers: int = 10              # Max teams they'll supply simultaneously
    
    # ===== COMPONENT-SPECIFIC ATTRIBUTES =====
    # These are populated based on the supplier's category
    component_specifications: Optional[Dict[str, float]] = None  # Technical specs
    performance_characteristics: Optional[Dict[str, float]] = None  # Performance data
    
    def get_discipline_compatibility(self, discipline: str) -> float:
        """
        Calculate how well this supplier serves a specific racing discipline
        
        Args:
            discipline: Racing discipline to evaluate
        
        Returns:
            Compatibility rating (0.0-1.0)
        """
        discipline_map = {
            "SINGLE_SEATER": self.single_seater_focus,
            "PRODUCTION_TOURING": self.production_touring_focus,
            "RALLY_STAGE": self.rally_stage_focus,
            "URBAN_STREET": self.urban_street_focus,
            "DRAG_ACCELERATION": self.drag_acceleration_focus,
            "SPRINT_RALLYCROSS": self.sprint_rallycross_focus,
            "ENDURANCE": self.endurance_focus
        }
        
        return discipline_map.get(discipline, 0.5)
    
    def get_overall_quality_rating(self) -> float:
        """
        Calculate overall supplier quality across all factors
        
        Returns:
            Overall quality rating (0.0-1.0)
        """
        quality_factors = [
            self.engineering_quality,
            self.manufacturing_precision,
            self.innovation_level,
            self.reliability_rating,
            self.technical_support_quality,
            self.delivery_reliability
        ]
        
        return sum(quality_factors) / len(quality_factors)


@dataclass
class ComponentContract:
    """
    Contract between a team and supplier for component provision
    
    Represents business agreements for component supply, including
    pricing, exclusivity, technical support, and performance targets.
    """
    # ===== CONTRACT IDENTIFICATION =====
    id: int                                   # Unique contract identifier
    team_id: int                             # Customer team (FK to teams.id)
    supplier_id: int                         # Supplier (FK to suppliers.id)
    component_type: str                      # Which component type being supplied
    
    # ===== CONTRACT TERMS =====
    contract_start_season: int               # When contract begins
    contract_duration_seasons: int          # Length of agreement
    annual_cost_millions: float             # Cost per season
    
    # ===== CONTRACT TYPE =====
    is_exclusive: bool = False               # Exclusive supplier for this component
    is_works_deal: bool = False              # Factory/works partnership (premium support)
    is_customer_deal: bool = True            # Standard customer relationship
    
    # ===== PERFORMANCE TERMS =====
    performance_targets: Optional[Dict[str, float]] = None  # Expected performance levels
    development_collaboration: bool = False  # Joint development projects
    data_sharing_agreement: bool = False     # Telemetry and performance data sharing
    
    # ===== SUPPORT SERVICES =====
    includes_technical_support: bool = True  # Engineer support at races
    includes_development_support: bool = False  # Custom development work
    includes_testing_allocation: bool = False   # Test sessions and development time
    
    # ===== FINANCIAL STRUCTURE =====
    base_cost: float = 0.0                   # Fixed annual fee
    performance_bonuses: float = 0.0         # Success-based payments
    volume_discounts: float = 0.0            # Discounts for multiple components
    
    # ===== CONTRACT STATUS =====
    contract_status: str = "active"          # active, expired, terminated, negotiating
    renewal_option: bool = True              # Can be renewed
    termination_penalty: float = 0.0         # Cost to break contract early


# Base supplier templates for each component category
# Aligned with the vehicle components system (engine.py, drivetrain.py, chassis.py, aerodynamics.py, electronics.py)
SUPPLIER_BASE_MODELS = {
    # ===== ENGINE MANUFACTURERS (engine.py - EngineComponent) =====
    "ENGINE": {
        "category_description": "Internal combustion engine manufacturers",
        "specialization_types": [
            "naturally_aspirated", "turbocharged", "supercharged", "twincharged",
            "inline_engines", "v_engines", "flat_engines", "rotary_engines",
            "formula_engines", "touring_engines", "rally_engines", "drag_engines"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 3.0
    },
    
    # ===== HYBRID SYSTEM MANUFACTURERS (engine.py - HybridSystem) =====
    "HYBRID_SYSTEM": {
        "category_description": "Hybrid power unit and energy recovery system manufacturers",
        "specialization_types": [
            "kers", "ers_h", "ers_k", "full_hybrid", "mgu_systems",
            "battery_management", "energy_recovery", "deployment_control",
            "supercapacitor", "flywheel_ers"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 2.5
    },
    
    # ===== GEARBOX MANUFACTURERS (drivetrain.py - Gearbox) =====
    "GEARBOX": {
        "category_description": "Gearbox and transmission manufacturers",
        "specialization_types": [
            "sequential", "manual", "semi_auto", "dual_clutch", "cvt",
            "automated_manual", "single_speed_electric",
            "formula_transmissions", "rally_gearboxes", "drag_transmissions"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 2.2
    },
    
    # ===== DIFFERENTIAL MANUFACTURERS (drivetrain.py - Differential) =====
    "DIFFERENTIAL": {
        "category_description": "Differential and traction control system manufacturers",
        "specialization_types": [
            "open", "lsd", "torsen", "electronic_active", "viscous_coupling",
            "mechanical_lsd", "torque_vectoring", "rally_differentials"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 1.8
    },
    
    # ===== DRIVETRAIN MANUFACTURERS (drivetrain.py - complete assemblies) =====
    "DRIVETRAIN": {
        "category_description": "Complete drivetrain assembly manufacturers",
        "specialization_types": [
            "fwd_systems", "rwd_systems", "awd_systems", "four_wd",
            "integrated_drivetrain", "power_transmission", "driveshaft_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 2.0
    },
    
    # ===== CHASSIS MANUFACTURERS (chassis.py - Chassis) =====
    "CHASSIS": {
        "category_description": "Chassis structure manufacturers",
        "specialization_types": [
            "carbon_fiber_monocoque", "aluminum_monocoque", "steel_tubular",
            "chromoly_tubular", "composite_materials", "space_frame",
            "crash_structures", "lightweight_construction"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 2.5
    },
    
    # ===== SUSPENSION MANUFACTURERS (chassis.py - Suspension) =====
    "SUSPENSION": {
        "category_description": "Suspension system manufacturers",
        "specialization_types": [
            "double_wishbone", "macpherson", "pushrod", "pullrod", "multi_link",
            "active_suspension", "monotube_dampers", "twin_tube_dampers",
            "magnetic_dampers", "coilovers", "anti_roll_bars"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 1.6
    },
    
    # ===== BRAKE MANUFACTURERS (chassis.py - BrakeSystem) =====
    "BRAKES": {
        "category_description": "Brake system manufacturers",
        "specialization_types": [
            "carbon_carbon", "carbon_ceramic", "steel_discs", "cast_iron",
            "ventilated_discs", "drilled_discs", "slotted_discs",
            "brake_cooling", "brake_by_wire", "abs_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 1.8
    },
    
    # ===== AERODYNAMICS MANUFACTURERS (aerodynamics.py - AeroPackage) =====
    "AERODYNAMICS": {
        "category_description": "Aerodynamic package manufacturers",
        "specialization_types": [
            "front_wings", "rear_wings", "drs_systems", "ground_effect",
            "diffusers", "body_kits", "active_aerodynamics", "splitters",
            "low_downforce_packages", "high_downforce_packages", "cfd_development"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 2.0
    },
    
    # ===== TIRE MANUFACTURERS (vehicle tires) =====
    "TIRES": {
        "category_description": "Tire and rubber compound manufacturers",
        "specialization_types": [
            "slick_tires", "wet_tires", "intermediate_tires", "gravel_tires",
            "snow_tires", "drag_slicks", "all_terrain", "mud_terrain",
            "super_soft", "soft", "medium", "hard", "super_hard"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 1.2
    },
    
    # ===== ECU MANUFACTURERS (electronics.py - ControlUnit) =====
    "ECU": {
        "category_description": "Electronic control unit manufacturers",
        "specialization_types": [
            "standard_ecu", "advanced_ecu", "telemetry_control", "fia_spec_ecu",
            "custom_development", "engine_management", "traction_control",
            "energy_management", "data_logging"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 1.5
    },
    
    # ===== TELEMETRY MANUFACTURERS (electronics.py - telemetry systems) =====
    "TELEMETRY": {
        "category_description": "Telemetry and data acquisition system manufacturers",
        "specialization_types": [
            "real_time_telemetry", "data_acquisition", "sensor_systems",
            "wireless_telemetry", "pit_wall_systems", "driver_displays",
            "performance_analysis", "predictive_analytics"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 1.2
    },
    
    # ===== STEERING MANUFACTURERS (electronics.py - SteeringSystem) =====
    "STEERING": {
        "category_description": "Steering system manufacturers",
        "specialization_types": [
            "manual_steering", "hydraulic_assist", "electric_assist",
            "electrohydraulic", "rack_and_pinion", "quick_ratio", "variable_ratio"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.70, 0.80)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.60, 0.70)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.55)}
        },
        "base_annual_cost_millions": 0.8
    },
    
    # ===== SAFETY EQUIPMENT MANUFACTURERS =====
    "SAFETY": {
        "category_description": "Safety equipment manufacturers",
        "specialization_types": [
            "roll_cages", "fire_suppression", "impact_structures", "safety_cells",
            "fia_certification", "crash_testing", "restraint_systems",
            "basic_safety", "intermediate_safety", "advanced_safety", "fia_grade_1"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.85, 0.95), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.75, 0.85), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.60, 0.75), "pricing_tier": (0.45, 0.55)}
        },
        "base_annual_cost_millions": 1.0
    },
    
    # ===== FUEL & ENERGY SUPPLIERS =====
    "FUEL_ENERGY": {
        "category_description": "Fuel, battery, and energy storage system providers",
        "specialization_types": [
            "petrol", "diesel", "ethanol", "e85", "methanol", "hydrogen",
            "lithium_ion_batteries", "solid_state_batteries", "supercapacitors",
            "fuel_cells", "hybrid_energy", "charging_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.70, 0.80)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 0.8
    }
}


# Placeholder supplier names organized by category
PLACEHOLDER_SUPPLIERS = {
    "ENGINE": [
        "Engine_Supplier_Premium_1", "Engine_Supplier_Premium_2", "Engine_Supplier_Premium_3",
        "Engine_Supplier_Pro_1", "Engine_Supplier_Pro_2", "Engine_Supplier_Pro_3",
        "Engine_Supplier_Comp_1", "Engine_Supplier_Comp_2",
        "Engine_Supplier_Budget_1", "Engine_Supplier_Budget_2"
    ],
    "HYBRID_SYSTEM": [
        "Hybrid_Supplier_Premium_1", "Hybrid_Supplier_Premium_2",
        "Hybrid_Supplier_Pro_1", "Hybrid_Supplier_Pro_2",
        "Hybrid_Supplier_Comp_1", "Hybrid_Supplier_Budget_1"
    ],
    "GEARBOX": [
        "Gearbox_Supplier_Premium_1", "Gearbox_Supplier_Premium_2",
        "Gearbox_Supplier_Pro_1", "Gearbox_Supplier_Pro_2", "Gearbox_Supplier_Pro_3",
        "Gearbox_Supplier_Comp_1", "Gearbox_Supplier_Comp_2",
        "Gearbox_Supplier_Budget_1"
    ],
    "DIFFERENTIAL": [
        "Diff_Supplier_Premium_1", "Diff_Supplier_Premium_2",
        "Diff_Supplier_Pro_1", "Diff_Supplier_Pro_2",
        "Diff_Supplier_Comp_1", "Diff_Supplier_Budget_1"
    ],
    "DRIVETRAIN": [
        "Drivetrain_Supplier_Premium_1", "Drivetrain_Supplier_Pro_1",
        "Drivetrain_Supplier_Comp_1", "Drivetrain_Supplier_Budget_1"
    ],
    "CHASSIS": [
        "Chassis_Supplier_Premium_1", "Chassis_Supplier_Premium_2",
        "Chassis_Supplier_Pro_1", "Chassis_Supplier_Pro_2",
        "Chassis_Supplier_Comp_1", "Chassis_Supplier_Budget_1"
    ],
    "SUSPENSION": [
        "Suspension_Supplier_Premium_1", "Suspension_Supplier_Premium_2",
        "Suspension_Supplier_Pro_1", "Suspension_Supplier_Pro_2",
        "Suspension_Supplier_Comp_1", "Suspension_Supplier_Comp_2",
        "Suspension_Supplier_Budget_1"
    ],
    "BRAKES": [
        "Brake_Supplier_Premium_1", "Brake_Supplier_Premium_2",
        "Brake_Supplier_Pro_1", "Brake_Supplier_Pro_2", "Brake_Supplier_Pro_3",
        "Brake_Supplier_Comp_1", "Brake_Supplier_Comp_2",
        "Brake_Supplier_Budget_1"
    ],
    "AERODYNAMICS": [
        "Aero_Supplier_Premium_1", "Aero_Supplier_Premium_2",
        "Aero_Supplier_Pro_1", "Aero_Supplier_Pro_2",
        "Aero_Supplier_Comp_1", "Aero_Supplier_Comp_2",
        "Aero_Supplier_Budget_1"
    ],
    "TIRES": [
        "Tire_Supplier_Premium_1", "Tire_Supplier_Premium_2",
        "Tire_Supplier_Pro_1", "Tire_Supplier_Pro_2",
        "Tire_Supplier_Comp_1", "Tire_Supplier_Comp_2",
        "Tire_Supplier_Budget_1"
    ],
    "ECU": [
        "ECU_Supplier_Premium_1", "ECU_Supplier_Pro_1", "ECU_Supplier_Pro_2",
        "ECU_Supplier_Comp_1", "ECU_Supplier_Budget_1"
    ],
    "TELEMETRY": [
        "Telemetry_Supplier_Premium_1", "Telemetry_Supplier_Pro_1",
        "Telemetry_Supplier_Comp_1", "Telemetry_Supplier_Budget_1"
    ],
    "STEERING": [
        "Steering_Supplier_Premium_1", "Steering_Supplier_Pro_1",
        "Steering_Supplier_Comp_1", "Steering_Supplier_Budget_1"
    ],
    "SAFETY": [
        "Safety_Supplier_Premium_1", "Safety_Supplier_Premium_2",
        "Safety_Supplier_Pro_1", "Safety_Supplier_Pro_2",
        "Safety_Supplier_Comp_1", "Safety_Supplier_Budget_1"
    ],
    "FUEL_ENERGY": [
        "Fuel_Supplier_Premium_1", "Fuel_Supplier_Pro_1", "Fuel_Supplier_Pro_2",
        "Fuel_Supplier_Comp_1", "Fuel_Supplier_Budget_1"
    ]
}

__all__ = [
    'SupplierCategory', 'SupplierTier', 'Supplier', 'ComponentContract', 
    'SUPPLIER_BASE_MODELS', 'PLACEHOLDER_SUPPLIERS'
]