"""
Staff Management System - Team Personnel Operations & Performance Impact

This module handles the operational side of staff management including hiring,
firing, salary negotiations, budget management, and how staff capabilities
affect team performance across different racing disciplines.

Features:
- Staff hiring and recruitment system
- Budget-constrained team building
- Performance impact calculations
- Information access level management (fog of war)
- Staff development and career progression
- Cross-discipline staff effectiveness

Authors: Final Year Project - Computer Science
"""

import random
import math
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from database.staff_models import (
    StaffMember, StaffRole, StaffTier, TeamStaffing,
    generate_staff_requirements, calculate_role_importance
)


@dataclass
class StaffMarket:
    """
    Staff recruitment market with available personnel
    
    Simulates the job market for racing team staff, with availability
    and quality depending on budget levels, team reputation, and discipline.
    """
    
    available_staff: List[StaffMember] = field(default_factory=list)
    market_conditions: Dict[str, float] = field(default_factory=dict)
    
    def generate_available_staff(self, count: int = 50) -> None:
        """Generate pool of available staff for recruitment"""
        self.available_staff.clear()
        
        # Generate staff across different tiers
        tier_distribution = {
            StaffTier.INTERN: 0.15,
            StaffTier.JUNIOR: 0.25,
            StaffTier.REGULAR: 0.30,
            StaffTier.SENIOR: 0.20,
            StaffTier.EXPERT: 0.08,
            StaffTier.LEGENDARY: 0.02
        }
        
        staff_id = 1
        for _ in range(count):
            # Select tier based on distribution
            tier = self._select_weighted_tier(tier_distribution)
            
            # Select role (more technical roles are rarer at higher tiers)
            role = self._select_role_for_tier(tier)
            
            # Generate staff member
            staff = self._generate_staff_member(staff_id, role, tier)
            self.available_staff.append(staff)
            staff_id += 1
            
    def _select_weighted_tier(self, distribution: Dict[StaffTier, float]) -> StaffTier:
        """Select tier based on weighted distribution"""
        rand = random.random()
        cumulative = 0.0
        
        for tier, probability in distribution.items():
            cumulative += probability
            if rand <= cumulative:
                return tier
                
        return StaffTier.REGULAR  # Default fallback
        
    def _select_role_for_tier(self, tier: StaffTier) -> StaffRole:
        """Select appropriate role based on tier"""
        
        # Role availability by tier
        role_pools = {
            StaffTier.INTERN: [
                StaffRole.MECHANIC, StaffRole.PIT_CREW_MEMBER,
                StaffRole.DATA_ANALYST, StaffRole.CAR_DESIGNER
            ],
            StaffTier.JUNIOR: [
                StaffRole.MECHANIC, StaffRole.PIT_CREW_MEMBER, StaffRole.DATA_ANALYST,
                StaffRole.SETUP_ENGINEER, StaffRole.CAR_DESIGNER, StaffRole.TEST_ENGINEER
            ],
            StaffTier.REGULAR: [
                StaffRole.CHIEF_ENGINEER, StaffRole.DATA_ANALYST, StaffRole.RACE_STRATEGIST,
                StaffRole.PIT_CREW_CHIEF, StaffRole.AERODYNAMICS_ENGINEER, StaffRole.ENGINE_ENGINEER,
                StaffRole.TEAM_MANAGER, StaffRole.MECHANIC
            ],
            StaffTier.SENIOR: [
                StaffRole.TECHNICAL_DIRECTOR, StaffRole.CHIEF_ENGINEER, StaffRole.CHIEF_DESIGNER,
                StaffRole.RACE_STRATEGIST, StaffRole.PERFORMANCE_ANALYST, StaffRole.TEAM_MANAGER,
                StaffRole.FINANCIAL_DIRECTOR
            ],
            StaffTier.EXPERT: [
                StaffRole.TECHNICAL_DIRECTOR, StaffRole.CHIEF_DESIGNER, StaffRole.TEAM_PRINCIPAL,
                StaffRole.PERFORMANCE_ANALYST, StaffRole.TELEMETRY_SPECIALIST
            ],
            StaffTier.LEGENDARY: [
                StaffRole.TEAM_PRINCIPAL, StaffRole.TECHNICAL_DIRECTOR, StaffRole.CHIEF_DESIGNER
            ]
        }
        
        available_roles = role_pools.get(tier, [StaffRole.MECHANIC])
        return random.choice(available_roles)
        
    def _generate_staff_member(self, staff_id: int, role: StaffRole, tier: StaffTier) -> StaffMember:
        """Generate realistic staff member with appropriate attributes"""
        
        # Generate basic info
        names = ["James Wilson", "Sarah Chen", "Marcus Rodriguez", "Elena Kowalski", 
                "David Thompson", "Maria Santos", "Alex Petrov", "Rachel Anderson"]
        nationalities = ["GBR", "USA", "GER", "ITA", "FRA", "ESP", "JPN", "AUS"]
        
        name = random.choice(names)
        nationality = random.choice(nationalities)
        age = random.randint(22, 55)
        birth_date = f"{1970 + (55 - age)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        
        # Generate attributes based on tier and role
        base_attributes = self._get_tier_attribute_ranges(tier)
        role_focused_attributes = self._apply_role_specialization(base_attributes, role)
        
        # Experience based on age and tier
        years_experience = max(0, age - 22 + random.randint(-3, 5))
        
        staff = StaffMember(
            id=staff_id,
            name=name,
            nationality=nationality,
            birth_date=birth_date,
            age=age,
            role=role,
            tier=tier,
            years_experience=years_experience,
            **role_focused_attributes
        )
        
        return staff
        
    def _get_tier_attribute_ranges(self, tier: StaffTier) -> Dict[str, float]:
        """Get attribute value ranges for tier"""
        
        ranges = {
            StaffTier.INTERN: (20, 50),
            StaffTier.JUNIOR: (35, 65),
            StaffTier.REGULAR: (45, 75),
            StaffTier.SENIOR: (60, 85),
            StaffTier.EXPERT: (75, 95),
            StaffTier.LEGENDARY: (85, 100)
        }
        
        min_val, max_val = ranges.get(tier, (40, 70))
        
        # Generate base attributes
        attributes = {}
        attribute_names = [
            # Technical skills
            "engineering_knowledge", "aerodynamics_expertise", "engine_knowledge",
            "suspension_expertise", "electronics_knowledge", "materials_science",
            "cfd_analysis", "cad_design", "simulation_expertise", "manufacturing_knowledge",
            "quality_control", "innovation_ability",
            
            # Analytical skills  
            "data_analysis", "telemetry_analysis", "performance_modeling",
            "statistical_methods", "pattern_recognition", "predictive_analytics",
            "software_proficiency", "database_management",
            
            # Management & leadership
            "leadership_ability", "team_coordination", "project_management",
            "resource_allocation", "conflict_resolution", "decision_making", "mentoring_ability",
            
            # Operational skills
            "pit_stop_efficiency", "race_strategy", "crisis_management",
            "equipment_maintenance", "logistics_coordination", "safety_protocols",
            "communication_skills", "adaptability",
            
            # Financial & commercial
            "financial_management", "commercial_acumen", "negotiation_skills",
            "sponsorship_development", "cost_optimization",
            
            # Discipline specializations
            "single_seater_expertise", "touring_car_expertise", "rally_expertise",
            "street_racing_expertise", "drag_racing_expertise", "rallycross_expertise",
            "endurance_expertise"
        ]
        
        for attr_name in attribute_names:
            # Add some variation within tier range
            value = random.uniform(min_val, max_val)
            attributes[attr_name] = round(value, 1)
            
        return attributes
        
    def _apply_role_specialization(self, base_attributes: Dict[str, float], role: StaffRole) -> Dict[str, float]:
        """Apply role-specific bonuses to relevant attributes"""
        
        # Role specialization bonuses
        role_bonuses = {
            StaffRole.TECHNICAL_DIRECTOR: {
                "engineering_knowledge": 15,
                "leadership_ability": 12,
                "innovation_ability": 10,
                "decision_making": 12
            },
            StaffRole.DATA_ANALYST: {
                "data_analysis": 20,
                "telemetry_analysis": 18,
                "statistical_methods": 15,
                "software_proficiency": 12
            },
            StaffRole.AERODYNAMICS_ENGINEER: {
                "aerodynamics_expertise": 20,
                "cfd_analysis": 18,
                "engineering_knowledge": 10,
                "simulation_expertise": 12
            },
            StaffRole.RACE_STRATEGIST: {
                "race_strategy": 20,
                "data_analysis": 12,
                "decision_making": 15,
                "pattern_recognition": 10
            },
            StaffRole.PIT_CREW_CHIEF: {
                "pit_stop_efficiency": 20,
                "leadership_ability": 15,
                "team_coordination": 15,
                "crisis_management": 12
            },
            StaffRole.CHIEF_DESIGNER: {
                "cad_design": 18,
                "innovation_ability": 15,
                "engineering_knowledge": 12,
                "materials_science": 10
            }
        }
        
        bonuses = role_bonuses.get(role, {})
        
        for attr_name, bonus in bonuses.items():
            if attr_name in base_attributes:
                base_attributes[attr_name] = min(100.0, base_attributes[attr_name] + bonus)
                
        return base_attributes
        
    def search_staff(self, role: Optional[StaffRole] = None, 
                    max_salary: Optional[float] = None,
                    min_tier: Optional[StaffTier] = None) -> List[StaffMember]:
        """Search available staff with filters"""
        
        results = self.available_staff.copy()
        
        if role:
            results = [s for s in results if s.role == role]
            
        if min_tier:
            tier_order = [StaffTier.INTERN, StaffTier.JUNIOR, StaffTier.REGULAR,
                         StaffTier.SENIOR, StaffTier.EXPERT, StaffTier.LEGENDARY]
            min_tier_index = tier_order.index(min_tier)
            results = [s for s in results if tier_order.index(s.tier) >= min_tier_index]
            
        if max_salary:
            # Filter by estimated salary demand
            results = [s for s in results if s.calculate_salary_demand(5_000_000, 1.0) <= max_salary]
            
        return results


class StaffManagementSystem:
    """
    Complete staff management system for racing teams
    
    Handles hiring, firing, salary negotiations, performance tracking,
    and the impact of staff on team capabilities.
    """
    
    def __init__(self):
        self.staff_market = StaffMarket()
        self.staff_market.generate_available_staff(100)
        
    def hire_staff(self, team_staffing: TeamStaffing, staff_member: StaffMember,
                   offered_salary: float) -> Tuple[bool, str]:
        """
        Attempt to hire staff member for team
        
        Args:
            team_staffing: Team's staffing configuration
            staff_member: Staff member to hire
            offered_salary: Salary offer
            
        Returns:
            (success, message) tuple
        """
        
        # Check budget constraints
        current_costs = team_staffing.calculate_staff_costs()
        if current_costs + offered_salary > team_staffing.personnel_budget:
            return False, "Insufficient budget for salary offer"
            
        # Calculate staff member's salary demand
        role_importance = calculate_role_importance(staff_member.role, team_staffing.discipline)
        expected_salary = staff_member.calculate_salary_demand(
            team_staffing.total_budget, role_importance
        )
        
        # Acceptance probability based on salary offer
        salary_ratio = offered_salary / expected_salary
        
        if salary_ratio < 0.7:
            return False, f"Salary offer too low (offered ${offered_salary:,.0f}, expects ${expected_salary:,.0f})"
        elif salary_ratio < 0.9:
            acceptance_chance = 0.3
        elif salary_ratio < 1.1:
            acceptance_chance = 0.8
        else:
            acceptance_chance = 0.95
            
        # Random acceptance based on probability
        if random.random() > acceptance_chance:
            return False, "Staff member declined offer"
            
        # Hire the staff member
        staff_member.current_team_id = team_staffing.team_id
        staff_member.salary = offered_salary
        team_staffing.staff_members.append(staff_member)
        
        # Remove from available market
        if staff_member in self.staff_market.available_staff:
            self.staff_market.available_staff.remove(staff_member)
            
        return True, f"Successfully hired {staff_member.name} as {staff_member.role.value}"
        
    def fire_staff(self, team_staffing: TeamStaffing, staff_member: StaffMember) -> Tuple[bool, str]:
        """Fire staff member from team"""
        
        if staff_member not in team_staffing.staff_members:
            return False, "Staff member not on team"
            
        # Remove from team
        team_staffing.staff_members.remove(staff_member)
        staff_member.current_team_id = None
        
        # Add back to market (with some delay in reality)
        self.staff_market.available_staff.append(staff_member)
        
        return True, f"Released {staff_member.name} from team"
        
    def calculate_team_performance_multipliers(self, team_staffing: TeamStaffing) -> Dict[str, float]:
        """
        Calculate how staff affects team performance in various areas
        
        Returns multipliers for different performance aspects:
        - overall_performance: General team competitiveness 
        - development_speed: Car development and upgrades
        - pit_stop_efficiency: Pit stop time and reliability
        - race_strategy: Strategic decision making
        - reliability: Car reliability and maintenance
        - adaptability: Adapting to conditions/changes
        """
        
        if not team_staffing.staff_members:
            # Minimal performance with no staff
            return {
                "overall_performance": 0.3,
                "development_speed": 0.2,
                "pit_stop_efficiency": 0.4,
                "race_strategy": 0.3,
                "reliability": 0.4,
                "adaptability": 0.3
            }
            
        multipliers = {}
        
        # Overall performance (average staff effectiveness)
        total_effectiveness = sum(member.get_role_effectiveness() for member in team_staffing.staff_members)
        average_effectiveness = total_effectiveness / len(team_staffing.staff_members)
        multipliers["overall_performance"] = 0.5 + (average_effectiveness / 100) * 1.0  # 0.5-1.5x
        
        # Development speed (technical roles)
        technical_roles = [StaffRole.TECHNICAL_DIRECTOR, StaffRole.CHIEF_ENGINEER, 
                          StaffRole.CHIEF_DESIGNER, StaffRole.AERODYNAMICS_ENGINEER]
        technical_staff = [m for m in team_staffing.staff_members if m.role in technical_roles]
        
        if technical_staff:
            technical_capability = sum(
                m.engineering_knowledge * 0.4 + m.innovation_ability * 0.3 + 
                m.cad_design * 0.2 + m.simulation_expertise * 0.1
                for m in technical_staff
            ) / len(technical_staff)
            multipliers["development_speed"] = 0.3 + (technical_capability / 100) * 1.2  # 0.3-1.5x
        else:
            multipliers["development_speed"] = 0.2
            
        # Pit stop efficiency
        pit_crew = [m for m in team_staffing.staff_members if 
                   m.role in [StaffRole.PIT_CREW_CHIEF, StaffRole.PIT_CREW_MEMBER]]
        
        if pit_crew:
            pit_efficiency = sum(
                m.pit_stop_efficiency * 0.6 + m.team_coordination * 0.2 + 
                m.crisis_management * 0.2 for m in pit_crew
            ) / len(pit_crew)
            multipliers["pit_stop_efficiency"] = 0.5 + (pit_efficiency / 100) * 1.0  # 0.5-1.5x
        else:
            multipliers["pit_stop_efficiency"] = 0.4
            
        # Race strategy
        strategists = [m for m in team_staffing.staff_members if 
                      m.role in [StaffRole.RACE_STRATEGIST, StaffRole.DATA_ANALYST]]
        
        if strategists:
            strategy_capability = sum(
                m.race_strategy * 0.5 + m.data_analysis * 0.3 + 
                m.decision_making * 0.2 for m in strategists
            ) / len(strategists)
            multipliers["race_strategy"] = 0.4 + (strategy_capability / 100) * 1.1  # 0.4-1.5x
        else:
            multipliers["race_strategy"] = 0.3
            
        # Reliability (mechanics and engineers)
        maintenance_staff = [m for m in team_staffing.staff_members if 
                           m.role in [StaffRole.MECHANIC, StaffRole.CHIEF_ENGINEER]]
        
        if maintenance_staff:
            reliability_capability = sum(
                m.equipment_maintenance * 0.4 + m.quality_control * 0.3 + 
                m.manufacturing_knowledge * 0.3 for m in maintenance_staff
            ) / len(maintenance_staff)
            multipliers["reliability"] = 0.4 + (reliability_capability / 100) * 1.1  # 0.4-1.5x
        else:
            multipliers["reliability"] = 0.3
            
        # Adaptability (leadership and experience)
        leadership_staff = [m for m in team_staffing.staff_members if 
                          m.leadership_ability > 60 or m.years_experience > 10]
        
        if leadership_staff:
            adaptability_capability = sum(
                m.adaptability * 0.4 + m.leadership_ability * 0.3 + 
                m.crisis_management * 0.3 for m in leadership_staff
            ) / len(leadership_staff)
            multipliers["adaptability"] = 0.4 + (adaptability_capability / 100) * 1.1  # 0.4-1.5x
        else:
            multipliers["adaptability"] = 0.3
            
        return multipliers
        
    def get_data_visibility_level(self, team_staffing: TeamStaffing) -> Dict[str, Any]:
        """
        Calculate what information the team can access (fog of war system)
        
        Returns dictionary with visibility levels for different data categories:
        - basic_performance: Driver lap times, positions
        - detailed_telemetry: Detailed car data, tire temps, etc.
        - competitor_analysis: Other teams' performance insights
        - strategic_forecasting: Weather, tire strategy predictions
        - development_insights: Car upgrade effectiveness predictions
        """
        
        info_access_level = team_staffing.calculate_information_access_level()
        
        visibility = {
            "basic_performance": True,  # Always available
            "detailed_telemetry": info_access_level >= 30,
            "competitor_analysis": info_access_level >= 50,
            "strategic_forecasting": info_access_level >= 70,
            "development_insights": info_access_level >= 80,
            "predictive_analytics": info_access_level >= 90,
        }
        
        # Detailed access levels for granular control
        detailed_access = {
            "telemetry_detail_level": min(100, max(10, info_access_level)),
            "competitor_data_accuracy": min(95, max(20, info_access_level - 10)),
            "strategy_forecast_accuracy": min(90, max(15, info_access_level - 20)),
            "development_prediction_accuracy": min(85, max(10, info_access_level - 30))
        }
        
        return {
            "visibility_flags": visibility,
            "detail_levels": detailed_access,
            "overall_access_level": info_access_level
        }
        
    def recommend_staff_hires(self, team_staffing: TeamStaffing, 
                             available_budget: float) -> List[Tuple[StaffMember, str, float]]:
        """
        Recommend staff hires based on team needs and budget
        
        Returns list of (staff_member, reason, estimated_cost) tuples
        """
        
        recommendations = []
        
        # Identify missing critical roles
        missing_roles = team_staffing.get_missing_critical_roles()
        
        for role in missing_roles[:3]:  # Top 3 priorities
            # Find suitable candidates
            candidates = self.staff_market.search_staff(role=role)
            
            if candidates:
                # Sort by effectiveness vs cost ratio
                role_importance = calculate_role_importance(role, team_staffing.discipline)
                
                scored_candidates = []
                for candidate in candidates:
                    effectiveness = candidate.get_role_effectiveness()
                    estimated_cost = candidate.calculate_salary_demand(
                        team_staffing.total_budget, role_importance
                    )
                    
                    if estimated_cost <= available_budget:
                        value_score = effectiveness / (estimated_cost / 100000)  # Effectiveness per $100k
                        scored_candidates.append((candidate, value_score, estimated_cost))
                        
                # Recommend best value candidate
                if scored_candidates:
                    scored_candidates.sort(key=lambda x: x[1], reverse=True)
                    best_candidate = scored_candidates[0]
                    
                    reason = f"Critical missing role: {role.value}"
                    recommendations.append((best_candidate[0], reason, best_candidate[2]))
                    
        return recommendations
        
    def simulate_staff_development(self, staff_member: StaffMember, months: int = 12) -> Dict[str, float]:
        """
        Simulate staff member skill development over time
        
        Args:
            staff_member: Staff member to develop
            months: Number of months to simulate
            
        Returns:
            Dictionary of attribute improvements
        """
        
        improvements = {}
        learning_rate = staff_member.learning_rate / 100  # Convert to decimal
        
        # Attributes that can be improved through experience
        improvable_attributes = [
            "engineering_knowledge", "data_analysis", "leadership_ability",
            "team_coordination", "race_strategy", "innovation_ability",
            "communication_skills", "crisis_management"
        ]
        
        for attr_name in improvable_attributes:
            if hasattr(staff_member, attr_name):
                current_value = getattr(staff_member, attr_name)
                
                # Improvement rate decreases as skill level increases
                max_improvement = (100 - current_value) * 0.1 * learning_rate
                monthly_improvement = max_improvement * (months / 12)
                
                # Add some randomness
                actual_improvement = random.uniform(0.5, 1.5) * monthly_improvement
                
                new_value = min(100.0, current_value + actual_improvement)
                setattr(staff_member, attr_name, round(new_value, 1))
                
                improvements[attr_name] = round(actual_improvement, 1)
                
        return improvements


# Export main classes
__all__ = [
    'StaffMarket', 'StaffManagementSystem'
]