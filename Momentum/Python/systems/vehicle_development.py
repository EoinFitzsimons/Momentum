"""
Vehicle Development System for Momentum Motorsport Simulation

This module handles the technical development aspects across all 7 racing disciplines.
Teams invest budget into different vehicle components to gain competitive advantages.
Each discipline has unique development trees and component interactions.

Key Features:
- Component-based development system
- Budget allocation and resource management
- Technology progression trees
- Performance impact calculations
- Cross-discipline technology transfer
- Research and development scheduling

Authors: Final Year Project - Computer Science
"""

import json
import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from database.multi_discipline_models import (
    Vehicle, RacingDiscipline, DISCIPLINE_DEVELOPMENT_TREES, 
    MultiDisciplineTeam
)


class ComponentType(Enum):
    """Core vehicle component categories"""
    AERODYNAMICS = "aerodynamics"
    ENGINE = "engine" 
    CHASSIS = "chassis"
    ELECTRONICS = "electronics"
    RELIABILITY = "reliability"
    SUSPENSION = "suspension"
    BRAKES = "brakes"
    TRANSMISSION = "transmission"
    ELECTRIC_POWERTRAIN = "electric_powertrain"
    SAFETY = "safety"


@dataclass
class DevelopmentProject:
    """Represents an active R&D project"""
    id: int
    team_id: int
    discipline: str
    component: str
    sub_component: str
    
    # Project parameters
    budget_allocated: float
    time_required_weeks: int
    time_remaining_weeks: int
    
    # Expected outcomes
    performance_gain_estimate: float  # 0.0-0.1 typical range
    reliability_impact: float        # Can be negative for aggressive development
    
    # Risk factors
    development_risk: float          # 0.0-1.0, higher risk = higher potential reward
    success_probability: float       # Based on team expertise and budget
    
    # Status
    status: str = "active"          # "active", "completed", "failed", "cancelled"


class VehicleDevelopmentEngine:
    """
    Core vehicle development system
    
    Manages technical development across all disciplines with realistic
    budget constraints, time requirements, and risk/reward mechanics.
    """
    
    def __init__(self):
        self.development_costs = self._initialize_development_costs()
        self.component_interactions = self._initialize_component_interactions()
        self.technology_dependencies = self._initialize_technology_dependencies()
    
    def calculate_development_cost(self, discipline: str, component: str, 
                                 sub_component: str, current_level: float) -> float:
        """
        Calculate cost to improve a specific component
        
        Cost increases exponentially as performance level increases,
        reflecting the real-world difficulty of marginal gains.
        
        Args:
            discipline: Racing discipline (F1, WEC, etc.)
            component: Main component category
            sub_component: Specific sub-component
            current_level: Current performance level (0.0-1.0)
            
        Returns:
            Cost in millions for 0.01 performance improvement
        """
        base_costs = self.development_costs.get(discipline, {})
        component_base_cost = base_costs.get(component, 1.0)
        
        # Exponential cost scaling - harder to improve at higher levels
        difficulty_multiplier = math.exp(current_level * 3)  # e^(3*level)
        
        # Sub-component specific multipliers
        sub_component_multipliers = {
            "basic": 0.5, "standard": 1.0, "advanced": 2.0, "cutting_edge": 4.0
        }
        
        sub_multiplier = sub_component_multipliers.get(
            self._categorize_sub_component(sub_component), 1.0
        )
        
        return component_base_cost * difficulty_multiplier * sub_multiplier
    
    def estimate_development_time(self, discipline: str, component: str,
                                sub_component: str, budget_allocated: float,
                                team_expertise: float) -> int:
        """
        Estimate development time in weeks
        
        Args:
            discipline: Racing discipline
            component: Component category
            sub_component: Specific component
            budget_allocated: Budget for this project (millions)
            team_expertise: Team's expertise in this discipline (0.0-1.0)
            
        Returns:
            Estimated time in weeks
        """
        base_time_weeks = self._get_base_development_time(discipline, component)
        
        # Budget acceleration - more money = more parallel work
        budget_factor = 1.0 / (1.0 + budget_allocated / 5.0)  # Diminishing returns
        
        # Team expertise reduces time
        expertise_factor = 2.0 - team_expertise  # Range: 1.0-2.0
        
        # Sub-component complexity
        complexity_multiplier = self._get_complexity_multiplier(sub_component)
        
        estimated_weeks = int(
            base_time_weeks * budget_factor * expertise_factor * complexity_multiplier
        )
        
        return max(estimated_weeks, 2)  # Minimum 2 weeks for any project
    
    def calculate_performance_gain(self, project: DevelopmentProject,
                                 team: MultiDisciplineTeam) -> Tuple[float, bool]:
        """
        Calculate actual performance gain from completed project
        
        Args:
            project: Completed development project
            team: Team that conducted the development
            
        Returns:
            Tuple of (actual_performance_gain, was_successful)
        """
        # Base performance gain from budget
        budget_factor = min(project.budget_allocated / 10.0, 1.0)  # Normalize
        base_gain = 0.02 * budget_factor  # Up to 2% improvement
        
        # Team expertise bonus
        discipline_expertise = team.technical_expertise.get(project.discipline, 0.5)
        expertise_multiplier = 0.5 + discipline_expertise
        
        # Risk/reward calculation
        risk_multiplier = 1.0 + project.development_risk
        
        # Success roll based on probability
        success_roll = random.random()
        project_successful = success_roll <= project.success_probability
        
        if project_successful:
            # Successful project
            actual_gain = base_gain * expertise_multiplier * risk_multiplier
            # Add some randomness (±25%)
            randomness = random.uniform(0.75, 1.25)
            actual_gain *= randomness
        else:
            # Failed project - minimal or no gain
            actual_gain = base_gain * 0.1 * random.uniform(0.0, 0.5)
        
        return min(actual_gain, 0.05), project_successful  # Cap at 5% gain
    
    def simulate_component_interactions(self, vehicle: Vehicle) -> Dict[str, float]:
        """
        Calculate performance bonuses from component synergies
        
        Some component combinations work better together, creating
        emergent performance gains beyond individual component levels.
        
        Args:
            vehicle: Vehicle with current component levels
            
        Returns:
            Dictionary of interaction bonuses per component
        """
        bonuses = {}
        interactions = self.component_interactions.get(vehicle.discipline, {})
        
        for primary_component, synergies in interactions.items():
            total_bonus = 0.0
            
            primary_level = getattr(vehicle, primary_component, 0.5)
            
            for synergy_component, interaction_strength in synergies.items():
                synergy_level = getattr(vehicle, synergy_component, 0.5)
                
                # Synergy bonus when both components are well developed
                synergy_bonus = (primary_level * synergy_level * 
                               interaction_strength * 0.02)  # Max 2% bonus
                total_bonus += synergy_bonus
            
            bonuses[primary_component] = total_bonus
        
        return bonuses
    
    def calculate_overall_performance(self, vehicle: Vehicle, 
                                    team: MultiDisciplineTeam) -> float:
        """
        Calculate vehicle's overall performance rating
        
        Combines individual component levels, synergy bonuses, and
        team expertise to determine competitive performance.
        
        Args:
            vehicle: Vehicle with component levels
            team: Team that built the vehicle
            
        Returns:
            Overall performance rating (0.0-1.0+, can exceed 1.0 for exceptional vehicles)
        """
        # Get base component performance
        component_weights = self._get_component_weights(vehicle.discipline)
        base_performance = 0.0
        
        for component, weight in component_weights.items():
            component_level = getattr(vehicle, component, 0.5)
            base_performance += component_level * weight
        
        # Apply synergy bonuses
        synergy_bonuses = self.simulate_component_interactions(vehicle)
        for component, bonus in synergy_bonuses.items():
            base_performance += bonus
        
        # Team expertise modifier
        team_expertise = team.technical_expertise.get(vehicle.discipline, 0.5)
        expertise_modifier = 0.9 + (team_expertise * 0.2)  # 0.9 to 1.1 range
        
        # Facility quality bonuses
        facility_bonus = 0.0
        if hasattr(team, 'wind_tunnel_quality'):
            facility_bonus += team.wind_tunnel_quality * 0.05
        if hasattr(team, 'simulator_quality'):
            facility_bonus += team.simulator_quality * 0.03
        
        final_performance = (base_performance * expertise_modifier) + facility_bonus
        
        return min(final_performance, 1.2)  # Cap to prevent unrealistic values
    
    def recommend_development_priorities(self, vehicle: Vehicle, 
                                       team: MultiDisciplineTeam,
                                       available_budget: float) -> List[Dict]:
        """
        AI recommendation system for development priorities
        
        Analyzes current vehicle state and suggests optimal development
        areas based on cost-effectiveness and strategic impact.
        
        Args:
            vehicle: Current vehicle state
            team: Team capabilities
            available_budget: Budget available for development
            
        Returns:
            List of recommended development projects with priorities
        """
        recommendations = []
        
        # Analyze current weaknesses
        component_levels = {}
        for component in ComponentType:
            level = getattr(vehicle, component.value, None)
            if level is not None:
                component_levels[component.value] = level
        
        # Find components below team average
        average_level = sum(component_levels.values()) / len(component_levels)
        weak_components = {k: v for k, v in component_levels.items() 
                         if v < average_level * 0.9}
        
        # Calculate cost-effectiveness for each potential development
        development_tree = DISCIPLINE_DEVELOPMENT_TREES.get(vehicle.discipline, {})
        
        for component, sub_components in development_tree.items():
            current_level = component_levels.get(component, 0.5)
            
            for sub_component in sub_components:
                cost = self.calculate_development_cost(
                    vehicle.discipline, component, sub_component, current_level
                )
                
                if cost <= available_budget:
                    # Estimate performance impact
                    impact = self._estimate_performance_impact(
                        vehicle.discipline, component, current_level
                    )
                    
                    # Calculate priority score
                    priority_score = self._calculate_priority_score(
                        component, current_level, impact, cost, weak_components
                    )
                    
                    recommendations.append({
                        'component': component,
                        'sub_component': sub_component,
                        'cost': cost,
                        'estimated_impact': impact,
                        'priority_score': priority_score,
                        'reasoning': self._generate_recommendation_reasoning(
                            component, current_level, impact, cost
                        )
                    })
        
        # Sort by priority score
        recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _initialize_development_costs(self) -> Dict[str, Dict[str, float]]:
        """Initialize base development costs per discipline and component"""
        return {
            "F1": {
                "aerodynamics": 8.0,  # Most expensive in F1
                "engine": 12.0,       # Power unit development very costly
                "chassis": 5.0,
                "electronics": 6.0,
                "reliability": 3.0
            },
            "F2": {
                "aerodynamics": 3.0,
                "engine": 4.0,
                "chassis": 2.5,
                "electronics": 2.0
            },
            "F3": {
                "aerodynamics": 1.5,
                "chassis": 1.0,
                "electronics": 0.5
            },
            "WEC": {
                "aerodynamics": 4.0,
                "engine": 8.0,       # Hybrid systems complex
                "chassis": 3.0,
                "reliability": 6.0,  # Critical for endurance
                "brakes": 2.0
            },
            "WRC": {
                "chassis": 4.0,      # Suspension critical
                "engine": 3.0,
                "transmission": 2.5,
                "safety": 2.0
            },
            "MotoGP": {
                "engine": 6.0,
                "chassis": 4.0,
                "electronics": 5.0,  # Rider aids very important
                "aerodynamics": 3.0
            },
            "FormulaE": {
                "electric_powertrain": 8.0,  # Main differentiator
                "aerodynamics": 3.0,
                "chassis": 2.0,
                "electronics": 4.0
            }
        }
    
    def _initialize_component_interactions(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Define synergies between different components"""
        return {
            "F1": {
                "aerodynamics": {"chassis": 0.3, "electronics": 0.2},
                "engine": {"electronics": 0.4, "reliability": 0.3},
                "chassis": {"aerodynamics": 0.3, "suspension": 0.4}
            },
            "WEC": {
                "engine": {"reliability": 0.5, "electronics": 0.3},
                "aerodynamics": {"chassis": 0.2, "brakes": 0.1},
                "reliability": {"engine": 0.4, "brakes": 0.3}
            },
            "WRC": {
                "chassis": {"suspension": 0.6, "transmission": 0.3},
                "engine": {"transmission": 0.4, "electronics": 0.2},
                "suspension": {"chassis": 0.5}
            },
            "MotoGP": {
                "chassis": {"electronics": 0.4, "engine": 0.3},
                "electronics": {"engine": 0.5, "chassis": 0.3},
                "engine": {"chassis": 0.2, "electronics": 0.4}
            },
            "FormulaE": {
                "electric_powertrain": {"electronics": 0.6, "aerodynamics": 0.2},
                "electronics": {"electric_powertrain": 0.5},
                "aerodynamics": {"chassis": 0.3}
            }
        }
    
    def _initialize_technology_dependencies(self) -> Dict[str, Dict[str, List[str]]]:
        """Define technology prerequisites for advanced developments"""
        return {
            "F1": {
                "aerodynamics": {
                    "advanced_cfd": ["basic_wing_design", "wind_tunnel_correlation"],
                    "active_aero": ["advanced_cfd", "electronics_integration"]
                },
                "engine": {
                    "mgu_h_optimization": ["basic_hybrid", "advanced_controls"],
                    "fuel_efficiency": ["combustion_optimization", "injection_mapping"]
                }
            }
            # Add more disciplines as needed
        }
    
    def _categorize_sub_component(self, sub_component: str) -> str:
        """Categorize sub-component complexity level"""
        advanced_keywords = ["advanced", "cutting_edge", "optimization", "integration"]
        basic_keywords = ["basic", "standard", "tuning"]
        
        sub_lower = sub_component.lower()
        
        if any(keyword in sub_lower for keyword in advanced_keywords):
            return "advanced"
        elif any(keyword in sub_lower for keyword in basic_keywords):
            return "basic"
        else:
            return "standard"
    
    def _get_base_development_time(self, discipline: str, component: str) -> int:
        """Get base development time in weeks for component type"""
        base_times = {
            "aerodynamics": 8, "engine": 12, "chassis": 6, 
            "electronics": 4, "reliability": 6, "suspension": 4,
            "brakes": 3, "transmission": 5, "electric_powertrain": 10,
            "safety": 4
        }
        return base_times.get(component, 6)
    
    def _get_complexity_multiplier(self, sub_component: str) -> float:
        """Get complexity multiplier for development time"""
        complexity_map = {
            "basic": 0.7, "standard": 1.0, "advanced": 1.5, "cutting_edge": 2.0
        }
        category = self._categorize_sub_component(sub_component)
        return complexity_map.get(category, 1.0)
    
    def _get_component_weights(self, discipline: str) -> Dict[str, float]:
        """Get relative importance weights for components per discipline"""
        weights = {
            "F1": {
                "aerodynamics": 0.25, "engine": 0.30, "chassis": 0.20,
                "electronics": 0.15, "reliability": 0.10
            },
            "F2": {
                "aerodynamics": 0.30, "engine": 0.25, "chassis": 0.25,
                "electronics": 0.20
            },
            "WEC": {
                "aerodynamics": 0.15, "engine": 0.25, "chassis": 0.20,
                "reliability": 0.30, "brakes": 0.10
            },
            "WRC": {
                "chassis": 0.35, "engine": 0.25, "transmission": 0.20,
                "safety": 0.20
            },
            "MotoGP": {
                "engine": 0.30, "chassis": 0.25, "electronics": 0.25,
                "aerodynamics": 0.20
            },
            "FormulaE": {
                "electric_powertrain": 0.40, "aerodynamics": 0.25,
                "chassis": 0.20, "electronics": 0.15
            }
        }
        return weights.get(discipline, {"aerodynamics": 0.5, "engine": 0.5})
    
    def _estimate_performance_impact(self, discipline: str, component: str, 
                                   current_level: float) -> float:
        """Estimate performance impact of improving a component"""
        component_weights = self._get_component_weights(discipline)
        component_weight = component_weights.get(component, 0.1)
        
        # Higher impact when component is currently weak
        weakness_factor = 1.0 - current_level
        
        return component_weight * weakness_factor * 0.02  # Max 2% impact
    
    def _calculate_priority_score(self, component: str, current_level: float,
                                impact: float, cost: float, 
                                weak_components: Dict[str, float]) -> float:
        """Calculate development priority score"""
        # Cost-effectiveness base score
        cost_effectiveness = impact / cost if cost > 0 else 0
        
        # Weakness bonus - prioritize weak areas
        weakness_bonus = 2.0 if component in weak_components else 1.0
        
        # Diminishing returns penalty for high-level components
        diminishing_penalty = 1.0 - (current_level * 0.5)
        
        return cost_effectiveness * weakness_bonus * diminishing_penalty
    
    def _generate_recommendation_reasoning(self, component: str, current_level: float,
                                         impact: float, cost: float) -> str:
        """Generate human-readable reasoning for development recommendation"""
        reasons = []
        
        if current_level < 0.5:
            reasons.append(f"{component} is currently underperforming")
        if impact > 0.015:
            reasons.append("high performance impact expected")
        if cost < 3.0:
            reasons.append("relatively low development cost")
        
        return "; ".join(reasons) if reasons else "balanced development opportunity"


# Export main classes
__all__ = ['VehicleDevelopmentEngine', 'DevelopmentProject', 'ComponentType']