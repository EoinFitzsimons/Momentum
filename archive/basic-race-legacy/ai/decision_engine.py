"""
AI Decision-Making Framework for Momentum Simulation

This module implements AI agents that make strategic decisions for teams and drivers
in the motorsport simulation. The system uses a combination of deterministic rules,
probabilistic heuristics, and personality-driven behaviors to create realistic and
varied decision-making patterns.

Key Components:
- TeamAI: Makes strategic decisions for AI-controlled teams
- DriverAI: Handles driver-specific choices and career decisions
- MarketDynamics: Simulates economic and competitive market forces
- NarrativeEngine: Generates emergent storylines from simulation outcomes

Authors: Final Year Project - Computer Science
"""

import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from database.models import Driver, Team, Race, RaceResult
from database.database_manager import DatabaseManager


class DecisionType(Enum):
    """Types of strategic decisions that AI can make"""
    RACE_STRATEGY = "race_strategy"
    DRIVER_SIGNING = "driver_signing"  
    BUDGET_ALLOCATION = "budget_allocation"
    TEAM_DEVELOPMENT = "team_development"
    CONTRACT_NEGOTIATION = "contract_negotiation"


@dataclass
class AIDecision:
    """Represents a strategic decision made by AI"""
    decision_type: DecisionType
    team_id: int
    decision_data: Dict
    confidence: float  # How confident the AI is in this decision (0.0-1.0)
    reasoning: str     # Human-readable explanation of the decision
    expected_outcome: str  # Predicted result of this decision


class TeamPersonality:
    """
    Defines AI personality traits that influence decision-making patterns
    
    Each team has unique personality characteristics that affect how their
    AI agent approaches different situations, creating distinctive behaviors
    and strategic approaches across the grid.
    """
    
    def __init__(self, team: Team):
        """Initialize personality based on team characteristics"""
        self.team_id = team.id
        
        # Core personality traits (influenced by team attributes)
        self.risk_appetite = team.risk_appetite
        self.innovation_focus = team.innovation_focus
        self.driver_development = team.driver_development
        self.brand_focus = team.brand_focus
        
        # Derived behavioral patterns
        self.aggression_level = self._calculate_aggression(team)
        self.loyalty_factor = self._calculate_loyalty(team)
        self.financial_prudence = self._calculate_prudence(team)
        
    def _calculate_aggression(self, team: Team) -> float:
        """Calculate how aggressively team pursues opportunities"""
        # High budget + high risk appetite = more aggressive
        budget_factor = min(team.budget / 400.0, 1.0)  # Normalize against max budget
        return (team.risk_appetite * 0.6 + budget_factor * 0.4)
    
    def _calculate_loyalty(self, team: Team) -> float:
        """Calculate team loyalty to drivers and staff"""
        # Established teams with strong management tend to be more loyal
        establishment_factor = min(team.total_wins / 50.0, 1.0)  # Normalize
        return (team.management_quality * 0.5 + establishment_factor * 0.3 + 
                (1.0 - team.risk_appetite) * 0.2)
    
    def _calculate_prudence(self, team: Team) -> float:
        """Calculate financial prudence in decision making"""
        return team.financial_stability * 0.7 + (1.0 - team.risk_appetite) * 0.3


class TeamAI:
    """
    AI Agent for Team Strategic Decision Making
    
    Makes realistic strategic decisions for AI-controlled teams based on:
    - Team personality and characteristics
    - Current competitive position
    - Financial constraints and opportunities
    - Historical performance patterns
    """
    
    def __init__(self, team: Team, db_manager: DatabaseManager):
        self.team = team
        self.db_manager = db_manager
        self.personality = TeamPersonality(team)
        self.decision_history: List[AIDecision] = []
        
        # Performance tracking for learning
        self.recent_performance = self._calculate_recent_performance()
        self.market_position = self._assess_market_position()
        
    def make_race_strategy_decision(self, race: Race, weather_conditions: str, 
                                  grid_position: int) -> AIDecision:
        """
        Make strategic decision for race approach
        
        Args:
            race: Race event details
            weather_conditions: Current weather forecast
            grid_position: Starting position on grid
            
        Returns:
            AIDecision with strategy choice and reasoning
        """
        strategy_options = {
            "aggressive": {"risk": 0.8, "reward": 0.9, "description": "High-risk, high-reward approach"},
            "conservative": {"risk": 0.3, "reward": 0.4, "description": "Safe, points-focused strategy"},
            "adaptive": {"risk": 0.5, "reward": 0.6, "description": "Flexible, situation-responsive"}
        }
        
        # Personality-based strategy preference
        base_preference = self.personality.risk_appetite
        
        # Adjust for current situation
        situation_modifier = 0.0
        
        # Weather conditions affect strategy choice
        if weather_conditions == "wet":
            situation_modifier += 0.2  # More aggressive in changeable conditions
        elif weather_conditions == "dry":
            situation_modifier -= 0.1  # More conservative in stable conditions
            
        # Grid position influences strategy
        if grid_position <= 3:  # Front runners
            situation_modifier -= 0.2  # More conservative when ahead
        elif grid_position >= 15:  # Back markers
            situation_modifier += 0.3  # More aggressive when behind
            
        # Recent performance affects confidence
        if self.recent_performance < 0.3:
            situation_modifier += 0.2  # Desperate for good results
        elif self.recent_performance > 0.7:
            situation_modifier -= 0.1  # Playing it safe when doing well
            
        # Calculate final strategy preference
        strategy_aggression = np.clip(base_preference + situation_modifier, 0.0, 1.0)
        
        # Choose strategy based on calculated preference
        if strategy_aggression > 0.65:
            chosen_strategy = "aggressive"
        elif strategy_aggression < 0.35:
            chosen_strategy = "conservative"
        else:
            chosen_strategy = "adaptive"
            
        # Calculate confidence based on team characteristics
        confidence = (self.team.management_quality * 0.4 + 
                     self.personality.financial_prudence * 0.3 +
                     (1.0 - abs(strategy_aggression - base_preference)) * 0.3)
        
        # Generate reasoning explanation
        reasoning_factors = []
        if weather_conditions != "dry":
            reasoning_factors.append(f"weather conditions ({weather_conditions})")
        if grid_position <= 5:
            reasoning_factors.append("strong grid position")
        elif grid_position >= 15:
            reasoning_factors.append("need to take risks from poor grid position")
        if self.recent_performance < 0.4:
            reasoning_factors.append("pressure for improved results")
            
        reasoning = f"Chose {chosen_strategy} strategy based on team risk profile"
        if reasoning_factors:
            reasoning += f" and {', '.join(reasoning_factors)}"
            
        decision = AIDecision(
            decision_type=DecisionType.RACE_STRATEGY,
            team_id=self.team.id,
            decision_data={
                "strategy": chosen_strategy,
                "aggression_level": strategy_aggression,
                "weather_factor": weather_conditions,
                "grid_position": grid_position
            },
            confidence=confidence,
            reasoning=reasoning,
            expected_outcome=strategy_options[chosen_strategy]["description"]
        )
        
        self.decision_history.append(decision)
        return decision
    
    def evaluate_driver_signing(self, available_driver: Driver, 
                              contract_cost: float) -> AIDecision:
        """
        Evaluate whether to sign an available driver
        
        Args:
            available_driver: Driver available for signing
            contract_cost: Annual cost to sign this driver
            
        Returns:
            AIDecision with signing recommendation and analysis
        """
        # Calculate driver value based on attributes
        driver_value = self._calculate_driver_value(available_driver)
        
        # Assess financial feasibility
        budget_impact = contract_cost / self.team.budget if self.team.budget > 0 else 1.0
        financial_feasible = budget_impact <= (0.4 * self.personality.financial_prudence + 0.2)
        
        # Consider team needs and philosophy
        team_fit = self._assess_driver_team_fit(available_driver)
        
        # Age and career phase considerations
        age_factor = self._calculate_age_value_factor(available_driver)
        
        # Overall signing score
        signing_score = (driver_value * 0.4 + 
                        team_fit * 0.3 + 
                        age_factor * 0.2 + 
                        (1.0 - budget_impact) * 0.1)
        
        # Decision threshold based on team personality
        decision_threshold = 0.6 + (self.personality.risk_appetite - 0.5) * 0.2
        
        should_sign = signing_score > decision_threshold and financial_feasible
        
        # Generate reasoning
        reasoning_parts = []
        reasoning_parts.append(f"Driver value assessment: {driver_value:.2f}")
        reasoning_parts.append(f"Team fit: {team_fit:.2f}")
        reasoning_parts.append(f"Budget impact: {budget_impact:.2f}")
        
        if not financial_feasible:
            reasoning_parts.append("Contract cost exceeds budget constraints")
        if available_driver.career_phase == "veteran":
            reasoning_parts.append("Veteran experience valuable for team development")
        elif available_driver.career_phase == "rookie":
            reasoning_parts.append("Young talent aligns with development strategy")
            
        decision = AIDecision(
            decision_type=DecisionType.DRIVER_SIGNING,
            team_id=self.team.id,
            decision_data={
                "driver_id": available_driver.id,
                "contract_cost": contract_cost,
                "signing_recommendation": should_sign,
                "value_assessment": signing_score,
                "budget_impact": budget_impact
            },
            confidence=0.6 + abs(signing_score - decision_threshold) * 0.4,
            reasoning="; ".join(reasoning_parts),
            expected_outcome="Sign driver" if should_sign else "Pass on signing"
        )
        
        self.decision_history.append(decision)
        return decision
    
    def _calculate_driver_value(self, driver: Driver) -> float:
        """Calculate overall value of a driver to the team"""
        # Weight performance attributes
        performance_value = (driver.skill * 0.3 + 
                           driver.consistency * 0.25 + 
                           driver.racecraft * 0.25 + 
                           driver.adaptability * 0.2)
        
        # Factor in career achievements
        achievement_bonus = min((driver.career_wins * 0.02 + 
                               driver.career_podiums * 0.01 + 
                               driver.career_points * 0.0001), 0.2)
        
        return min(performance_value + achievement_bonus, 1.0)
    
    def _assess_driver_team_fit(self, driver: Driver) -> float:
        """Assess how well driver fits team philosophy and needs"""
        fit_score = 0.5  # Base neutral fit
        
        # Risk tolerance alignment
        driver_risk = driver.risk_tolerance
        team_risk = self.team.risk_appetite
        risk_alignment = 1.0 - abs(driver_risk - team_risk)
        fit_score += (risk_alignment - 0.5) * 0.3
        
        # Development focus vs experience needs
        if self.team.driver_development > 0.6 and driver.career_phase == "rookie":
            fit_score += 0.25  # Development teams prefer young talent
        elif self.team.driver_development < 0.4 and driver.career_phase == "veteran":
            fit_score += 0.15  # Win-now teams prefer experience
            
        # Media and marketing considerations
        if self.team.brand_focus > 0.6 and driver.media_savvy > 0.7:
            fit_score += 0.1  # Marketing-focused teams value media appeal
            
        return np.clip(fit_score, 0.0, 1.0)
    
    def _calculate_age_value_factor(self, driver: Driver) -> float:
        """Calculate value factor based on driver career phase"""
        phase_values = {
            "rookie": 0.7,    # High potential, low experience
            "active": 1.0,    # Peak value
            "veteran": 0.8,   # High experience, declining performance
            "retired": 0.0    # No value for active racing
        }
        return phase_values.get(driver.career_phase, 0.5)
    
    def _calculate_recent_performance(self) -> float:
        """Calculate team's recent performance rating"""
        # This would query recent race results in a full implementation
        # For now, return a placeholder based on team characteristics
        base_performance = (self.team.total_wins / 100.0 + 
                          self.team.management_quality * 0.3 + 
                          min(self.team.budget / 400.0, 1.0) * 0.2)
        return min(base_performance, 1.0)
    
    def _assess_market_position(self) -> str:
        """Assess team's position in competitive market"""
        if self.team.tier == "tier1":
            return "championship_contender"
        elif self.team.tier == "tier2":
            return "midfield_competitor"
        else:
            return "development_team"


class DriverAI:
    """
    AI Agent for Driver Career Decisions
    
    Handles driver-specific choices including:
    - Contract negotiations and team changes
    - Career development priorities
    - Retirement decisions
    - Performance consistency factors
    """
    
    def __init__(self, driver: Driver, db_manager: DatabaseManager):
        self.driver = driver
        self.db_manager = db_manager
        self.career_goals = self._determine_career_goals()
        self.market_value = self._calculate_market_value()
    
    def evaluate_team_offer(self, team: Team, contract_offer: Dict) -> AIDecision:
        """Evaluate a contract offer from a team"""
        # Implementation for driver contract decision-making
        pass
    
    def _determine_career_goals(self) -> List[str]:
        """Determine driver's primary career objectives"""
        goals = []
        
        if self.driver.career_wins < 5:
            goals.append("win_first_race")
        if self.driver.career_phase == "rookie":
            goals.append("establish_reputation")
        elif self.driver.career_phase == "active":
            goals.append("maximize_championships")
        else:
            goals.append("legacy_building")
            
        return goals
    
    def _calculate_market_value(self) -> float:
        """Calculate driver's current market value"""
        # Implementation for market value calculation
        return (self.driver.skill + self.driver.consistency + self.driver.racecraft) / 3.0


# Export main classes for use in simulation
__all__ = ['TeamAI', 'DriverAI', 'AIDecision', 'DecisionType', 'TeamPersonality']