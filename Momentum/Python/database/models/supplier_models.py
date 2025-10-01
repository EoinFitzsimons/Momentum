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
    """Categories of component suppliers in the motorsport ecosystem"""
    ENGINE_POWERTRAIN = "ENGINE_POWERTRAIN"           # ICE engines, electric motors, hybrid systems
    TIRE_COMPOUND = "TIRE_COMPOUND"                   # Tire manufacturers and compounds
    CHASSIS_AERO = "CHASSIS_AERO"                     # Chassis, aerodynamics, bodywork
    ELECTRONICS = "ELECTRONICS"                       # ECU, telemetry, data systems
    TRANSMISSION = "TRANSMISSION"                     # Gearboxes, differentials, drivetrain
    BRAKE_SYSTEMS = "BRAKE_SYSTEMS"                   # Brake calipers, discs, cooling
    SUSPENSION = "SUSPENSION"                         # Dampers, springs, anti-roll bars
    FUEL_ENERGY = "FUEL_ENERGY"                      # Fuel, batteries, energy systems
    SAFETY_EQUIPMENT = "SAFETY_EQUIPMENT"            # Roll cages, fire systems, helmets
    SPECIALTY_PERFORMANCE = "SPECIALTY_PERFORMANCE"   # Nitrous, launch control, exotic systems


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
# These define the characteristics and typical ranges for each supplier type
SUPPLIER_BASE_MODELS = {
    # ===== ENGINE/POWERTRAIN MANUFACTURERS =====
    "ENGINE_POWERTRAIN": {
        "category_description": "Engine and powertrain system manufacturers",
        "specialization_types": [
            "formula_engines", "touring_engines", "rally_engines", "drag_engines",
            "electric_powertrains", "hybrid_systems", "turbocharged_engines"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 3.0
    },
    
    # ===== TIRE MANUFACTURERS =====
    "TIRE_COMPOUND": {
        "category_description": "Tire and rubber compound manufacturers",
        "specialization_types": [
            "formula_compounds", "endurance_tires", "rally_tires", "drag_slicks",
            "wet_weather", "all_terrain", "street_compounds", "racing_slicks"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 1.2
    },
    
    # ===== CHASSIS & AERODYNAMICS =====
    "CHASSIS_AERO": {
        "category_description": "Chassis, aerodynamics, and bodywork manufacturers",
        "specialization_types": [
            "carbon_fiber", "monocoque_chassis", "aerodynamic_packages", "body_kits",
            "ground_effect", "active_aerodynamics", "lightweight_materials"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.85)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 2.0
    },
    
    # ===== ELECTRONICS & DATA SYSTEMS =====
    "ELECTRONICS": {
        "category_description": "Electronic control units, telemetry, and data systems",
        "specialization_types": [
            "telemetry_systems", "ecu_development", "engine_management", "data_logging",
            "driver_aids", "traction_control", "energy_management", "sensor_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 1.5
    },
    
    # ===== TRANSMISSION MANUFACTURERS =====
    "TRANSMISSION": {
        "category_description": "Gearbox, differential, and drivetrain manufacturers",
        "specialization_types": [
            "sequential_gearboxes", "formula_transmissions", "awd_systems", "rally_gearboxes",
            "drag_transmissions", "torque_converters", "limited_slip_differentials"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.80, 0.90)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.70, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 2.2
    },
    
    # ===== BRAKE SYSTEM MANUFACTURERS =====
    "BRAKE_SYSTEMS": {
        "category_description": "Brake calipers, discs, and cooling system manufacturers",
        "specialization_types": [
            "carbon_brakes", "steel_brakes", "cooling_systems", "brake_by_wire",
            "drag_brakes", "endurance_brakes", "lightweight_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.85, 0.95)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.80)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 1.8
    },
    
    # ===== SUSPENSION SPECIALISTS =====
    "SUSPENSION": {
        "category_description": "Suspension dampers, springs, and anti-roll bar manufacturers",
        "specialization_types": [
            "active_suspension", "formula_dampers", "rally_suspension", "long_travel",
            "coilovers", "adjustable_dampers", "anti_roll_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.60, 0.70)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.45, 0.60)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 1.6
    },
    
    # ===== FUEL & ENERGY SUPPLIERS =====
    "FUEL_ENERGY": {
        "category_description": "Fuel, battery, and energy storage system providers",
        "specialization_types": [
            "high_octane_fuel", "racing_additives", "battery_systems", "energy_storage",
            "fuel_cells", "hybrid_energy", "charging_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.85, 1.0), "pricing_tier": (0.70, 0.80)},
            "PROFESSIONAL": {"engineering_quality": (0.80, 0.90), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.80), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.55)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 0.8
    },
    
    # ===== SAFETY EQUIPMENT =====
    "SAFETY_EQUIPMENT": {
        "category_description": "Safety systems, roll cages, and fire suppression manufacturers",
        "specialization_types": [
            "roll_cages", "fire_suppression", "impact_structures", "safety_cells",
            "helmets", "racing_suits", "restraint_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.90, 1.0), "pricing_tier": (0.75, 0.85)},
            "PROFESSIONAL": {"engineering_quality": (0.85, 0.95), "pricing_tier": (0.65, 0.75)},
            "COMPETITIVE": {"engineering_quality": (0.75, 0.85), "pricing_tier": (0.55, 0.65)},
            "BUDGET": {"engineering_quality": (0.60, 0.75), "pricing_tier": (0.45, 0.55)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 1.0
    },
    
    # ===== SPECIALTY PERFORMANCE COMPONENTS =====
    "SPECIALTY_PERFORMANCE": {
        "category_description": "Specialized performance components for specific disciplines",
        "specialization_types": [
            "nitrous_systems", "launch_control", "traction_control", "launch_systems",
            "turbocharger_systems", "intercoolers", "exhaust_systems"
        ],
        "typical_quality_ranges": {
            "PREMIUM": {"engineering_quality": (0.80, 1.0), "pricing_tier": (0.65, 0.75)},
            "PROFESSIONAL": {"engineering_quality": (0.75, 0.90), "pricing_tier": (0.60, 0.70)},
            "COMPETITIVE": {"engineering_quality": (0.70, 0.85), "pricing_tier": (0.50, 0.60)},
            "BUDGET": {"engineering_quality": (0.50, 0.70), "pricing_tier": (0.40, 0.50)}
        },
        "discipline_specializations": [
            "single_seater_focus", "production_touring_focus", "rally_stage_focus",
            "urban_street_focus", "drag_acceleration_focus", "sprint_rallycross_focus", "endurance_focus"
        ],
        "base_annual_cost_millions": 1.4
    }
}

__all__ = [
    'SupplierCategory', 'SupplierTier', 'Supplier', 'ComponentContract', 'SUPPLIER_BASE_MODELS'
]