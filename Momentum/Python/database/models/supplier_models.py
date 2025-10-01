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
    # Core powertrain
    ENGINE_ICE = "ENGINE_ICE"                         # Internal combustion engines
    ENGINE_HYBRID = "ENGINE_HYBRID"                   # Hybrid power units (ERS-K, ERS-H, KERS)
    
    # Drivetrain
    GEARBOX = "GEARBOX"                               # Gearboxes and transmissions
    DIFFERENTIAL = "DIFFERENTIAL"                     # Differentials (LSD, torque vectoring)
    DRIVETRAIN = "DRIVETRAIN"                         # Complete drivetrain assemblies
    
    # Chassis systems
    SUSPENSION = "SUSPENSION"                         # Suspension systems (springs, dampers, ARB)
    BRAKE_SYSTEMS = "BRAKE_SYSTEMS"                   # Brake systems (calipers, discs, cooling)
    CHASSIS = "CHASSIS"                               # Chassis structures (monocoque, tubular)
    
    # Aerodynamics and tires
    AERODYNAMICS = "AERODYNAMICS"                     # Aerodynamic packages (wings, DRS, diffusers)
    TIRES = "TIRES"                                   # Tire manufacturers and compounds
    
    # Electronics and controls
    ECU = "ECU"                                       # Electronic control units
    STEERING = "STEERING"                             # Steering systems (rack, power assist)
    SAFETY = "SAFETY"                                 # Safety equipment (roll cage, fire suppression)
    
    # Energy and fuel
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
# Aligned with the new vehicle components system
SUPPLIER_BASE_MODELS = {
    # ===== ENGINE ICE MANUFACTURERS =====
    "ENGINE_ICE": {
        "category_description": "Internal combustion engine manufacturers",
        "specialization_types": [
            "formula_engines", "touring_engines", "rally_engines", "drag_engines",
            "turbocharged_engines", "naturally_aspirated", "rotary_engines"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 3.0
    },
    
    # ===== HYBRID POWER UNIT MANUFACTURERS =====
    "ENGINE_HYBRID": {
        "category_description": "Hybrid power unit and energy recovery system manufacturers",
        "specialization_types": [
            "ers_k_systems", "ers_h_systems", "kers", "mgu_systems",
            "battery_management", "energy_recovery", "deployment_control"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 2.5
    },
    
    # ===== GEARBOX MANUFACTURERS =====
    "GEARBOX": {
        "category_description": "Gearbox and transmission manufacturers",
        "specialization_types": [
            "sequential_gearboxes", "h_pattern", "automatic", "dual_clutch",
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
    
    # ===== DIFFERENTIAL MANUFACTURERS =====
    "DIFFERENTIAL": {
        "category_description": "Differential and traction control system manufacturers",
        "specialization_types": [
            "limited_slip_differentials", "torque_vectoring", "electronic_lsd",
            "open_differentials", "rally_differentials", "drag_differentials"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 1.8
    },
    
    # ===== DRIVETRAIN MANUFACTURERS =====
    "DRIVETRAIN": {
        "category_description": "Complete drivetrain assembly manufacturers",
        "specialization_types": [
            "integrated_drivetrain", "awd_systems", "rwd_systems", "fwd_systems",
            "power_transmission", "driveshaft_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 2.0
    },
    
    # ===== SUSPENSION MANUFACTURERS =====
    "SUSPENSION": {
        "category_description": "Suspension system manufacturers (springs, dampers, ARB)",
        "specialization_types": [
            "active_suspension", "formula_dampers", "rally_suspension", "long_travel",
            "coilovers", "adjustable_dampers", "anti_roll_bars", "pushrod_pullrod"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 1.6
    },
    
    # ===== BRAKE SYSTEM MANUFACTURERS =====
    "BRAKE_SYSTEMS": {
        "category_description": "Brake system manufacturers (calipers, discs, cooling)",
        "specialization_types": [
            "carbon_brakes", "steel_brakes", "ceramic_brakes", "cooling_systems",
            "brake_by_wire", "drag_brakes", "endurance_brakes", "temperature_monitoring"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 1.8
    },
    
    # ===== CHASSIS MANUFACTURERS =====
    "CHASSIS": {
        "category_description": "Chassis structure manufacturers (monocoque, tubular, space-frame)",
        "specialization_types": [
            "carbon_fiber_monocoque", "aluminum_monocoque", "tubular_chassis",
            "space_frame", "crash_structures", "lightweight_materials"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 2.5
    },
    
    # ===== AERODYNAMICS MANUFACTURERS =====
    "AERODYNAMICS": {
        "category_description": "Aerodynamic package manufacturers (wings, DRS, diffusers)",
        "specialization_types": [
            "front_wings", "rear_wings", "drs_systems", "ground_effect",
            "diffusers", "body_kits", "active_aerodynamics", "cfd_development"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "base_annual_cost_millions": 2.0
    },
    
    # ===== TIRE MANUFACTURERS =====
    "TIRES": {
        "category_description": "Tire and rubber compound manufacturers",
        "specialization_types": [
            "slick_compounds", "wet_tires", "intermediate_tires", "rally_tires",
            "drag_slicks", "endurance_compounds", "street_legal", "all_terrain"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 1.2
    },
    
    # ===== ECU MANUFACTURERS =====
    "ECU": {
        "category_description": "Electronic control unit and telemetry manufacturers",
        "specialization_types": [
            "standard_ecu", "advanced_ecu", "telemetry_systems", "engine_management",
            "data_logging", "traction_control", "energy_management", "sensor_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "base_annual_cost_millions": 1.5
    },
    
    # ===== STEERING SYSTEM MANUFACTURERS =====
    "STEERING": {
        "category_description": "Steering system manufacturers (rack, power assist)",
        "specialization_types": [
            "rack_and_pinion", "hydraulic_assist", "electric_assist", "electrohydraulic",
            "manual_steering", "quick_ratio", "variable_ratio"
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
        "category_description": "Safety equipment manufacturers (roll cage, fire suppression)",
        "specialization_types": [
            "roll_cages", "fire_suppression", "impact_structures", "safety_cells",
            "fia_certification", "crash_testing", "restraint_systems"
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
            "high_octane_fuel", "racing_additives", "lithium_ion_batteries",
            "supercapacitors", "fuel_cells", "hybrid_energy", "charging_systems"
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
    "ENGINE_ICE": [
        "Engine_Supplier_Premium_1", "Engine_Supplier_Premium_2", "Engine_Supplier_Premium_3",
        "Engine_Supplier_Pro_1", "Engine_Supplier_Pro_2", "Engine_Supplier_Pro_3",
        "Engine_Supplier_Comp_1", "Engine_Supplier_Comp_2",
        "Engine_Supplier_Budget_1", "Engine_Supplier_Budget_2"
    ],
    "ENGINE_HYBRID": [
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
    "SUSPENSION": [
        "Suspension_Supplier_Premium_1", "Suspension_Supplier_Premium_2",
        "Suspension_Supplier_Pro_1", "Suspension_Supplier_Pro_2",
        "Suspension_Supplier_Comp_1", "Suspension_Supplier_Comp_2",
        "Suspension_Supplier_Budget_1"
    ],
    "BRAKE_SYSTEMS": [
        "Brake_Supplier_Premium_1", "Brake_Supplier_Premium_2",
        "Brake_Supplier_Pro_1", "Brake_Supplier_Pro_2", "Brake_Supplier_Pro_3",
        "Brake_Supplier_Comp_1", "Brake_Supplier_Comp_2",
        "Brake_Supplier_Budget_1"
    ],
    "CHASSIS": [
        "Chassis_Supplier_Premium_1", "Chassis_Supplier_Premium_2",
        "Chassis_Supplier_Pro_1", "Chassis_Supplier_Pro_2",
        "Chassis_Supplier_Comp_1", "Chassis_Supplier_Budget_1"
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