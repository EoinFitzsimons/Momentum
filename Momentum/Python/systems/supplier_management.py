"""
Momentum Motorsport Simulation - Supplier Management System

This module handles the business logic for component suppliers and team-supplier
relationships. It manages supplier selection, contract negotiation, component
procurement, and the make-vs-buy decisions that teams face.

Key Features:
- Supplier evaluation and selection
- Contract negotiation and management
- Component quality and pricing calculations
- Make-vs-buy decision support
- Supplier performance tracking
- Market dynamics simulation

Authors: Final Year Project - Computer Science
"""

import sqlite3
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from Momentum.Python.database.models.supplier_models import Supplier, ComponentContract, SupplierCategory, SupplierTier, SUPPLIER_BASE_MODELS


class SupplierManager:
    """
    Manages the supplier ecosystem and team-supplier relationships
    
    This class handles all supplier-related business logic including
    supplier creation, contract management, and procurement decisions.
    """
    
    def __init__(self, db_path: str = "momentum.db"):
        self.db_path = db_path
        self.suppliers: Dict[int, Supplier] = {}
        self.contracts: Dict[int, ComponentContract] = {}
        # Base models are available for creating custom suppliers as needed
    
    def create_supplier_from_base_model(self, category: SupplierCategory, name: str, 
                                      nationality: str = "Global",
                                      tier: SupplierTier = SupplierTier.COMPETITIVE,
                                      specializations: Optional[List[str]] = None) -> Supplier:
        """Create a supplier instance from base model templates."""
        # Convert enum to string key for base model lookup
        category_key = category.value if hasattr(category, 'value') else str(category)
        
        if category_key not in SUPPLIER_BASE_MODELS:
            raise ValueError(f"No base model available for category: {category_key}")
        
        base_model = SUPPLIER_BASE_MODELS[category_key]
        
        # Use specializations from parameter or use base model specialization types
        if not specializations:
            specializations = base_model.get("specialization_types", [])[:2]  # Take first 2
        
        # Get tier string for lookup
        tier_str = tier.value if hasattr(tier, 'value') else str(tier)
        
        # Get quality ranges from base model
        tier_ranges = base_model.get("typical_quality_ranges", {}).get(tier_str, {})
        
        if tier_ranges and "engineering_quality" in tier_ranges:
            quality_min, quality_max = tier_ranges["engineering_quality"]
        else:
            # Fallback quality multipliers
            tier_quality_multipliers = {
                SupplierTier.PREMIUM: (0.8, 1.0),
                SupplierTier.PROFESSIONAL: (0.7, 0.9),
                SupplierTier.COMPETITIVE: (0.6, 0.85),
                SupplierTier.BUDGET: (0.4, 0.7)
            }
            quality_min, quality_max = tier_quality_multipliers[tier]
        
        supplier_id = len(self.suppliers) + 1
        supplier = Supplier(
            id=supplier_id,
            name=name,
            nationality=nationality,
            founded_year=random.randint(1950, 2020),
            category=category_key,  # Use string key
            tier=tier_str,  # Use string tier
            specializations=specializations,
            headquarters=f"{nationality} HQ",
            biography=f"Leading {category_key.lower().replace('_', ' ')} manufacturer",
            engineering_quality=random.uniform(quality_min, quality_max),
            manufacturing_precision=random.uniform(quality_min, quality_max),
            innovation_level=random.uniform(quality_min, quality_max),
            single_seater_focus=random.uniform(0.3, 0.9) if "single_seater_focus" in base_model.get("discipline_specializations", []) else random.uniform(0.1, 0.5),
            production_touring_focus=random.uniform(0.3, 0.9) if "production_touring_focus" in base_model.get("discipline_specializations", []) else random.uniform(0.1, 0.5),
            rally_stage_focus=random.uniform(0.3, 0.9) if "rally_stage_focus" in base_model.get("discipline_specializations", []) else random.uniform(0.1, 0.5),
            urban_street_focus=random.uniform(0.3, 0.9) if "urban_street_focus" in base_model.get("discipline_specializations", []) else random.uniform(0.1, 0.5),
            drag_acceleration_focus=random.uniform(0.3, 0.9) if "drag_acceleration_focus" in base_model.get("discipline_specializations", []) else random.uniform(0.1, 0.5),
            sprint_rallycross_focus=random.uniform(0.3, 0.9) if "sprint_rallycross_focus" in base_model.get("discipline_specializations", []) else random.uniform(0.1, 0.5),
            endurance_focus=random.uniform(0.3, 0.9) if "endurance_focus" in base_model.get("discipline_specializations", []) else random.uniform(0.1, 0.5),
            annual_revenue_millions=base_model.get("base_annual_cost_millions", 2.0),
            pricing_tier=tier_ranges.get("pricing_tier", (0.5, 0.8))[1] if tier_ranges else 0.6  # Use max pricing for tier
        )
        
        self.suppliers[supplier_id] = supplier
        return supplier
    
    def _initialize_supplier_database(self):
        """Base models are available for creating custom suppliers"""
        # No longer auto-populate - suppliers created on demand using base models
        pass
    

    
    def get_suppliers_by_category(self, category: str) -> List[Supplier]:
        """Get all suppliers in a specific category"""
        return [supplier for supplier in self.suppliers.values() 
                if supplier.category == category]
    
    def get_suppliers_by_discipline(self, discipline: str, category: str = None) -> List[Supplier]:
        """
        Get suppliers that specialize in a specific racing discipline
        
        Args:
            discipline: Racing discipline (e.g., "SINGLE_SEATER")
            category: Optional category filter
            
        Returns:
            List of suppliers sorted by discipline compatibility
        """
        suppliers = self.suppliers.values()
        
        if category:
            suppliers = [s for s in suppliers if s.category == category]
        
        # Sort by discipline compatibility
        discipline_suppliers = [(s, s.get_discipline_compatibility(discipline)) 
                              for s in suppliers]
        discipline_suppliers.sort(key=lambda x: x[1], reverse=True)
        
        return [supplier for supplier, compatibility in discipline_suppliers if compatibility > 0.3]
    
    def calculate_component_cost(self, supplier: Supplier, team_tier: str, 
                               discipline: str) -> float:
        """
        Calculate the annual cost for a component from a specific supplier
        
        Args:
            supplier: The supplier providing the component
            team_tier: Team's competitive tier (affects pricing)
            discipline: Racing discipline
            component_type: Specific component being purchased
            
        Returns:
            Annual cost in millions USD
        """
        # Base cost factors
        base_cost = 1.0  # Base component cost in millions
        
        # Supplier pricing tier effect
        supplier_multiplier = supplier.pricing_tier
        
        # Component category effects
        category_multipliers = {
            "ENGINE_POWERTRAIN": 3.0,      # Most expensive components
            "CHASSIS_AERO": 2.0,           # Significant development costs
            "ELECTRONICS": 1.5,            # High-tech but smaller components
            "TRANSMISSION": 2.2,           # Complex mechanical systems
            "BRAKE_SYSTEMS": 1.8,          # Critical safety components
            "SUSPENSION": 1.6,             # Important for performance
            "TIRE_COMPOUND": 1.2,          # Consumable but essential
            "FUEL_ENERGY": 0.8,            # Consumable supplies
            "SAFETY_EQUIPMENT": 1.0,       # Standard safety requirements
            "SPECIALTY_PERFORMANCE": 1.4   # Niche performance items
        }
        
        category_multiplier = category_multipliers.get(supplier.category, 1.0)
        
        # Team tier discounts (bigger teams get better deals)
        tier_multipliers = {
            "tier1": 0.9,    # Premium teams get slight discounts
            "tier2": 1.0,    # Standard pricing
            "tier3": 1.1     # Smaller teams pay premium
        }
        
        tier_multiplier = tier_multipliers.get(team_tier, 1.0)
        
        # Discipline compatibility bonus (specialized suppliers cost more)
        discipline_compatibility = supplier.get_discipline_compatibility(discipline)
        discipline_multiplier = 0.8 + (discipline_compatibility * 0.4)  # 0.8 to 1.2 range
        
        # Quality premium
        quality_multiplier = 0.7 + (supplier.get_overall_quality_rating() * 0.6)  # 0.7 to 1.3 range
        
        total_cost = (base_cost * supplier_multiplier * category_multiplier * 
                     tier_multiplier * discipline_multiplier * quality_multiplier)
        
        return round(total_cost, 2)
    
    def calculate_component_performance(self, supplier: Supplier, discipline: str, 
                                      team_development_level: float = 0.5) -> float:
        """
        Calculate the performance benefit from using a specific supplier
        
        Args:
            supplier: The supplier providing the component
            discipline: Racing discipline
            team_development_level: Team's in-house development capability (0.0-1.0)
            
        Returns:
            Performance rating (0.0-1.0)
        """
        # Base performance from supplier quality
        base_performance = supplier.get_overall_quality_rating()
        
        # Discipline specialization bonus
        discipline_bonus = supplier.get_discipline_compatibility(discipline) * 0.1
        
        # Innovation bonus for cutting-edge suppliers
        innovation_bonus = supplier.innovation_level * 0.05
        
        # Team integration factor (how well team can utilize the component)
        integration_factor = 0.8 + (team_development_level * 0.2)
        
        total_performance = (base_performance + discipline_bonus + innovation_bonus) * integration_factor
        
        return min(1.0, max(0.0, total_performance))
    
    def evaluate_make_vs_buy_decision(self, component_type: str, 
                                    discipline: str, team_budget: float,
                                    team_development_capability: float) -> Dict[str, any]:
        """
        Help teams decide between developing components in-house vs buying from suppliers
        
        Args:
            team_id: Team making the decision
            component_type: Component being considered
            discipline: Racing discipline
            team_budget: Team's available budget
            team_development_capability: Team's technical capability (0.0-1.0)
            
        Returns:
            Decision analysis with recommendations
        """
        # Get available suppliers for this component
        category_map = {
            "engine": "ENGINE_POWERTRAIN",
            "tires": "TIRE_COMPOUND",
            "brakes": "BRAKE_SYSTEMS",
            "transmission": "TRANSMISSION",
            "suspension": "SUSPENSION",
            "electronics": "ELECTRONICS",
            "aerodynamics": "CHASSIS_AERO",
            "fuel": "FUEL_ENERGY",
            "safety": "SAFETY_EQUIPMENT",
            "nitrous": "SPECIALTY_PERFORMANCE"
        }
        
        category = category_map.get(component_type, "SPECIALTY_PERFORMANCE")
        available_suppliers = self.get_suppliers_by_discipline(discipline, category)
        
        # Calculate in-house development option
        in_house_cost = self._calculate_in_house_development_cost(component_type, team_development_capability)
        in_house_performance = self._calculate_in_house_performance(team_development_capability)
        in_house_time = self._calculate_development_time(component_type, team_development_capability)
        
        # Evaluate supplier options
        supplier_options = []
        for supplier in available_suppliers[:5]:  # Top 5 suppliers
            cost = self.calculate_component_cost(supplier, "tier2", discipline)  # Assume tier2
            performance = self.calculate_component_performance(supplier, discipline, team_development_capability)
            
            supplier_options.append({
                "supplier": supplier,
                "annual_cost": cost,
                "performance": performance,
                "value_ratio": performance / cost if cost > 0 else 0,
                "availability": "immediate"
            })
        
        # Sort suppliers by value ratio
        supplier_options.sort(key=lambda x: x["value_ratio"], reverse=True)
        
        # Make recommendation
        best_supplier = supplier_options[0] if supplier_options else None
        
        if best_supplier and team_budget >= best_supplier["annual_cost"]:
            if in_house_performance > best_supplier["performance"] * 1.1:  # 10% performance advantage
                recommendation = "make"
                reason = "In-house development offers significant performance advantage"
            elif best_supplier["annual_cost"] < in_house_cost * 0.8:  # 20% cost savings
                recommendation = "buy"
                reason = f"Supplier {best_supplier['supplier'].name} offers significant cost savings"
            elif in_house_time > 2:  # Takes more than 2 seasons to develop
                recommendation = "buy"
                reason = "Time to market advantage with supplier"
            else:
                recommendation = "make"
                reason = "In-house development provides better long-term value"
        else:
            recommendation = "buy" if best_supplier else "make"
            reason = "Budget constraints" if not best_supplier else "No suitable suppliers available"
        
        return {
            "recommendation": recommendation,
            "reason": reason,
            "in_house_option": {
                "cost": in_house_cost,
                "performance": in_house_performance,
                "development_time": in_house_time
            },
            "supplier_options": supplier_options,
            "best_supplier": best_supplier
        }
    
    def _calculate_in_house_development_cost(self, component_type: str, capability: float) -> float:
        """Calculate cost of developing component in-house"""
        base_costs = {
            "engine": 5.0,
            "aerodynamics": 3.0,
            "electronics": 2.0,
            "transmission": 4.0,
            "brakes": 2.5,
            "suspension": 2.0,
            "tires": 1.5,
            "fuel": 1.0,
            "safety": 1.8,
            "nitrous": 1.2
        }
        
        base_cost = base_costs.get(component_type, 2.0)
        capability_factor = 2.0 - capability  # Lower capability = higher cost
        
        return base_cost * capability_factor
    
    def _calculate_in_house_performance(self, capability: float) -> float:
        """Calculate performance from in-house development"""
        # Performance is directly related to team capability
        base_performance = 0.3 + (capability * 0.7)  # 0.3 to 1.0 range
        
        # Add some randomness for development uncertainty
        uncertainty = random.uniform(-0.1, 0.1)
        
        return min(1.0, max(0.0, base_performance + uncertainty))
    
    def _calculate_development_time(self, component_type: str, capability: float) -> int:
        """Calculate time required for in-house development (in seasons)"""
        base_times = {
            "engine": 3,
            "aerodynamics": 2,
            "electronics": 2,
            "transmission": 3,
            "brakes": 2,
            "suspension": 2,
            "tires": 1,
            "fuel": 1,
            "safety": 1,
            "nitrous": 1
        }
        
        base_time = base_times.get(component_type, 2)
        capability_factor = 2.0 - capability  # Lower capability = longer time
        
        return max(1, int(base_time * capability_factor))
    
    def create_contract(self, team_id: int, supplier_id: int, component_type: str,
                       duration: int, cost: float, contract_type: str = "customer") -> ComponentContract:
        """Create a new supplier contract"""
        contract_id = len(self.contracts) + 1
        
        contract = ComponentContract(
            id=contract_id,
            team_id=team_id,
            supplier_id=supplier_id,
            component_type=component_type,
            contract_start_season=2025,  # Current season
            contract_duration_seasons=duration,
            annual_cost_millions=cost,
            is_customer_deal=(contract_type == "customer"),
            is_works_deal=(contract_type == "works"),
            is_exclusive=(contract_type == "exclusive")
        )
        
        self.contracts[contract_id] = contract
        return contract
    
    def get_team_suppliers(self, team_id: int) -> List[Dict[str, any]]:
        """Get all active supplier relationships for a specific team"""
        team_contracts = [contract for contract in self.contracts.values() 
                         if contract.team_id == team_id and contract.contract_status == "active"]
        
        supplier_relationships = []
        for contract in team_contracts:
            supplier = self.suppliers.get(contract.supplier_id)
            if supplier:
                supplier_relationships.append({
                    "contract": contract,
                    "supplier": supplier,
                    "component_type": contract.component_type,
                    "annual_cost": contract.annual_cost_millions,
                    "contract_remaining": contract.contract_duration_seasons
                })
        
        return supplier_relationships
    
    def get_supplier_customers(self, supplier_id: int) -> List[Dict[str, any]]:
        """Get all teams currently supplied by a specific supplier"""
        supplier_contracts = [contract for contract in self.contracts.values() 
                             if contract.supplier_id == supplier_id and contract.contract_status == "active"]
        
        return [{
            "team_id": contract.team_id,
            "component_type": contract.component_type,
            "annual_value": contract.annual_cost_millions,
            "contract_type": "works" if contract.is_works_deal else "customer"
        } for contract in supplier_contracts]

    def simulate_market_dynamics(self, season: int):
        """Simulate changes in supplier market over time"""
        for supplier in self.suppliers.values():
            # Small random changes in supplier capabilities
            if random.random() < 0.1:  # 10% chance of change each season
                # Innovation can improve
                if random.random() < 0.6:
                    supplier.innovation_level = min(1.0, supplier.innovation_level + random.uniform(0.01, 0.03))
                
                # Quality can fluctuate slightly
                quality_change = random.uniform(-0.02, 0.02)
                supplier.engineering_quality = max(0.5, min(1.0, supplier.engineering_quality + quality_change))
                
                # Pricing can change based on market conditions
                pricing_change = random.uniform(-0.05, 0.05)
                supplier.pricing_tier = max(0.3, min(1.0, supplier.pricing_tier + pricing_change))


# Usage example and testing
if __name__ == "__main__":
    # Initialize supplier manager
    supplier_manager = SupplierManager()
    
    print("=== Motorsport Supplier Ecosystem ===")
    print(f"Total suppliers: {len(supplier_manager.suppliers)}")
    
    # Show suppliers by category
    for category in SupplierCategory:
        suppliers = supplier_manager.get_suppliers_by_category(category.value)
        print(f"\n{category.value}: {len(suppliers)} suppliers")
        for supplier in suppliers[:2]:  # Show first 2 in each category
            print(f"  - {supplier.name} ({supplier.nationality}, {supplier.tier})")
    
    # Example: Team looking for Single Seater engine supplier
    print("\n=== Single Seater Engine Suppliers ===")
    engine_suppliers = supplier_manager.get_suppliers_by_discipline("SINGLE_SEATER", "ENGINE_POWERTRAIN")
    for supplier in engine_suppliers[:3]:
        cost = supplier_manager.calculate_component_cost(supplier, "tier2", "SINGLE_SEATER")
        performance = supplier_manager.calculate_component_performance(supplier, "SINGLE_SEATER", 0.7)
        print(f"{supplier.name}: ${cost:.1f}M/year, Performance: {performance:.2f}")
    
    # Example: Make vs Buy decision
    print("\n=== Make vs Buy Analysis ===")
    decision = supplier_manager.evaluate_make_vs_buy_decision(
        component_type="engine", discipline="SINGLE_SEATER", 
        team_budget=10.0, team_development_capability=0.6
    )
    print(f"Recommendation: {decision['recommendation']}")
    print(f"Reason: {decision['reason']}")
    if decision['best_supplier']:
        print(f"Best supplier option: {decision['best_supplier']['supplier'].name} "
              f"(${decision['best_supplier']['annual_cost']:.1f}M, Performance: {decision['best_supplier']['performance']:.2f})")