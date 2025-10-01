"""
Staff Management System - Comprehensive Multi-Role Team Personnel

This module defines the complete staff system for racing teams, including
various roles, attributes, budget scaling, and information access control.
Works alongside the multi-discipline driver system to provide complete
team management simulation.

Features:
- 40+ staff attributes across 6 categories
- 25+ different staff roles with specialisations  
- Multi-currency support with EUR default (2025 F1 budget cap: $140.4M USD)
- Budget-based staff scaling and hiring
- Information fog-of-war based on staff capabilities
- Cross-discipline compatibility
- Performance impact on team operations

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union, Tuple
from enum import Enum
from datetime import datetime
import random
import sys
import os

# Import currency system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from systems.currency_system import Currency, currency_system
except ImportError:
    # Fallback if currency system not available
    class Currency:
        EUR = "EUR"
        USD = "USD"
    
    class MockCurrencySystem:
        def format_amount(self, amount, currency=Currency.EUR, show_code=False):
            return f"€{amount:,.0f}" if currency == Currency.EUR else f"${amount:,.0f}"
    
    currency_system = MockCurrencySystem()


class StaffRole(Enum):
    """Staff role categories with specialisation areas"""
    
    # Core Technical Roles
    TECHNICAL_DIRECTOR = "TECHNICAL_DIRECTOR"
    CHIEF_ENGINEER = "CHIEF_ENGINEER"
    AERODYNAMICS_ENGINEER = "AERODYNAMICS_ENGINEER"
    ENGINE_ENGINEER = "ENGINE_ENGINEER"
    SUSPENSION_ENGINEER = "SUSPENSION_ENGINEER"
    DATA_ANALYST = "DATA_ANALYST"
    SETUP_ENGINEER = "SETUP_ENGINEER"
    
    # Operational Roles
    TEAM_MANAGER = "TEAM_MANAGER"
    RACE_STRATEGIST = "RACE_STRATEGIST"
    PIT_CREW_CHIEF = "PIT_CREW_CHIEF"
    PIT_CREW_MEMBER = "PIT_CREW_MEMBER"
    MECHANIC = "MECHANIC"
    
    # Development Roles
    CHIEF_DESIGNER = "CHIEF_DESIGNER"
    CAR_DESIGNER = "CAR_DESIGNER"
    SIMULATOR_ENGINEER = "SIMULATOR_ENGINEER"
    TEST_ENGINEER = "TEST_ENGINEER"
    
    # Business & Support Roles
    TEAM_PRINCIPAL = "TEAM_PRINCIPAL"
    FINANCIAL_DIRECTOR = "FINANCIAL_DIRECTOR"
    COMMERCIAL_DIRECTOR = "COMMERCIAL_DIRECTOR"
    MARKETING_MANAGER = "MARKETING_MANAGER"
    
    # Discipline-Specific Roles
    DRIVER_COACH = "DRIVER_COACH"
    FITNESS_TRAINER = "FITNESS_TRAINER"
    PSYCHOLOGIST = "PSYCHOLOGIST"
    
    # Advanced Analytics
    PERFORMANCE_ANALYST = "PERFORMANCE_ANALYST"
    TELEMETRY_SPECIALIST = "TELEMETRY_SPECIALIST"
    WEATHER_SPECIALIST = "WEATHER_SPECIALIST"


class StaffTier(Enum):
    """Staff quality/experience tiers"""
    INTERN = "INTERN"
    JUNIOR = "JUNIOR"
    REGULAR = "REGULAR"
    SENIOR = "SENIOR"
    EXPERT = "EXPERT"
    LEGENDARY = "LEGENDARY"


class BudgetCategory(Enum):
    """Budget categories that affect staff hiring"""
    DEVELOPMENT = "DEVELOPMENT"
    OPERATIONS = "OPERATIONS"
    PERSONNEL = "PERSONNEL"
    TECHNOLOGY = "TECHNOLOGY"
    INFRASTRUCTURE = "INFRASTRUCTURE"


@dataclass
class StaffMember:
    """
    Comprehensive staff member with 40+ attributes across 6 categories
    
    Similar to the driver system but focused on team operational capabilities
    rather than racing performance. Each staff member has specialisations
    and contributes to different aspects of team performance.
    """
    
    # ===== BASIC INFORMATION =====
    id: int
    name: str
    nationality: str
    birth_date: str
    age: int
    role: StaffRole
    tier: StaffTier
    
    # ===== TECHNICAL SKILLS (12 attributes) =====
    # Core technical competencies for engineering and development
    engineering_knowledge: float = 50.0        # General engineering understanding
    aerodynamics_expertise: float = 50.0       # Aerodynamic design and analysis
    engine_knowledge: float = 50.0             # Powertrain and engine systems
    suspension_expertise: float = 50.0         # Chassis and suspension systems
    electronics_knowledge: float = 50.0       # Electronic systems and controls
    materials_science: float = 50.0           # Material selection and properties
    cfd_analysis: float = 50.0                # Computational fluid dynamics
    cad_design: float = 50.0                  # Computer-aided design skills
    simulation_expertise: float = 50.0        # Virtual testing and modeling
    manufacturing_knowledge: float = 50.0     # Production and fabrication
    quality_control: float = 50.0             # Testing and validation processes
    innovation_ability: float = 50.0          # Creative problem solving
    
    # ===== ANALYTICAL SKILLS (8 attributes) =====
    # Data analysis and performance optimisation capabilities
    data_analysis: float = 50.0               # Statistical analysis and interpretation
    telemetry_analysis: float = 50.0          # Real-time data interpretation
    performance_modeling: float = 50.0        # Predictive performance models
    statistical_methods: float = 50.0         # Advanced statistical techniques
    pattern_recognition: float = 50.0         # Identifying trends and patterns
    predictive_analytics: float = 50.0        # Forecasting and predictions
    software_proficiency: float = 50.0        # Technical software mastery
    database_management: float = 50.0         # Data storage and retrieval
    
    # ===== MANAGEMENT & LEADERSHIP (7 attributes) =====
    # Team coordination and organisational capabilities
    leadership_ability: float = 50.0          # Natural leadership and influence
    team_coordination: float = 50.0           # Organising and managing teams
    project_management: float = 50.0          # Planning and executing projects
    resource_allocation: float = 50.0         # Efficient resource utilization
    conflict_resolution: float = 50.0         # Handling team conflicts
    decision_making: float = 50.0             # Strategic decision capability
    mentoring_ability: float = 50.0           # Developing junior staff
    
    # ===== OPERATIONAL SKILLS (8 attributes) =====
    # Day-to-day racing and team operations
    pit_stop_efficiency: float = 50.0         # Pit stop execution speed
    race_strategy: float = 50.0               # Strategic race planning
    crisis_management: float = 50.0           # Handling emergency situations
    equipment_maintenance: float = 50.0       # Maintaining tools and systems
    logistics_coordination: float = 50.0      # Travel and equipment planning
    safety_protocols: float = 50.0            # Safety awareness and implementation
    communication_skills: float = 50.0        # Clear and effective communication
    adaptability: float = 50.0                # Adjusting to changing conditions
    
    # ===== FINANCIAL & COMMERCIAL (5 attributes) =====
    # Business and financial management capabilities
    financial_management: float = 50.0        # Budget and cost management
    commercial_acumen: float = 50.0           # Business development skills
    negotiation_skills: float = 50.0          # Contract and deal negotiation
    sponsorship_development: float = 50.0     # Attracting and managing sponsors
    cost_optimisation: float = 50.0           # Efficient spending strategies
    
    # ===== DISCIPLINE SPECIALISATIONS (7 attributes) =====
    # Expertise in specific racing disciplines
    single_seater_expertise: float = 50.0     # Formula racing specialisation
    touring_car_expertise: float = 50.0       # Production car racing knowledge
    rally_expertise: float = 50.0             # Rally and stage racing knowledge
    street_racing_expertise: float = 50.0     # Urban racing specialisation
    drag_racing_expertise: float = 50.0       # Straight-line racing knowledge
    rallycross_expertise: float = 50.0        # Mixed surface racing expertise
    endurance_expertise: float = 50.0         # Long-distance racing knowledge
    
    # ===== CAREER & DEVELOPMENT =====
    # Professional progression and experience tracking
    years_experience: int = 0                 # Total years in motorsport
    previous_teams: str = ""                  # JSON list of previous employment
    education_level: str = "bachelor"         # Educational background
    certifications: str = ""                  # Professional certifications
    languages_spoken: int = 1                 # Number of languages
    
    # Current employment details
    current_team_id: Optional[int] = None     # Team assignment (FK)
    salary: float = 50000.0                   # Annual salary in USD
    contract_length: int = 1                  # Remaining contract years
    contract_type: str = "full_time"          # Employment type
    
    # Performance and satisfaction
    job_satisfaction: float = 75.0            # Current job satisfaction
    workload_capacity: float = 100.0          # Maximum workload handling
    current_workload: float = 50.0            # Current workload percentage
    performance_rating: float = 75.0          # Recent performance evaluation
    
    # Professional development
    learning_rate: float = 50.0               # Speed of skill development
    innovation_projects: int = 0              # Number of innovation projects led
    patents_held: int = 0                     # Technical patents owned
    publications: int = 0                     # Technical papers published
    
    def get_role_effectiveness(self) -> float:
        """
        Calculate overall effectiveness in current role
        
        Combines relevant attributes based on role requirements
        to determine how well this staff member performs their duties.
        
        Returns:
            Overall role effectiveness (0-100 scale)
        """
        role_weights = self._get_role_attribute_weights()
        
        total_score = 0.0
        total_weight = 0.0
        
        for attribute, weight in role_weights.items():
            if hasattr(self, attribute):
                value = getattr(self, attribute)
                total_score += value * weight
                total_weight += weight
                
        if total_weight == 0:
            return 50.0  # Default if no weights defined
            
        effectiveness = total_score / total_weight
        
        # Apply experience and tier bonuses
        experience_bonus = min(self.years_experience * 2, 20)  # Up to 20% bonus
        tier_bonus = self._get_tier_bonus()
        
        final_effectiveness = effectiveness + experience_bonus + tier_bonus
        return round(min(100.0, max(0.0, final_effectiveness)), 1)
        
    def _get_role_attribute_weights(self) -> Dict[str, float]:
        """Get attribute weights specific to staff role"""
        
        role_weights = {
            # Technical Director - Strategic technical oversight
            StaffRole.TECHNICAL_DIRECTOR: {
                "engineering_knowledge": 0.20,
                "leadership_ability": 0.15,
                "decision_making": 0.15,
                "innovation_ability": 0.12,
                "team_coordination": 0.10,
                "project_management": 0.10,
                "aerodynamics_expertise": 0.08,
                "engine_knowledge": 0.10
            },
            
            # Chief Engineer - Hands-on technical leadership
            StaffRole.CHIEF_ENGINEER: {
                "engineering_knowledge": 0.25,
                "problem_solving": 0.15,
                "team_coordination": 0.12,
                "quality_control": 0.10,
                "manufacturing_knowledge": 0.10,
                "simulation_expertise": 0.08,
                "communication_skills": 0.10,
                "mentoring_ability": 0.10
            },
            
            # Data Analyst - Performance analysis specialist
            StaffRole.DATA_ANALYST: {
                "data_analysis": 0.25,
                "telemetry_analysis": 0.20,
                "statistical_methods": 0.15,
                "pattern_recognition": 0.12,
                "software_proficiency": 0.10,
                "predictive_analytics": 0.10,
                "performance_modeling": 0.08
            },
            
            # Race Strategist - Strategic race planning
            StaffRole.RACE_STRATEGIST: {
                "race_strategy": 0.25,
                "data_analysis": 0.15,
                "decision_making": 0.15,
                "pattern_recognition": 0.12,
                "crisis_management": 0.10,
                "communication_skills": 0.10,
                "adaptability": 0.13
            },
            
            # Pit Crew Chief - Pit stop leadership
            StaffRole.PIT_CREW_CHIEF: {
                "pit_stop_efficiency": 0.25,
                "leadership_ability": 0.20,
                "team_coordination": 0.15,
                "crisis_management": 0.12,
                "communication_skills": 0.10,
                "safety_protocols": 0.10,
                "equipment_maintenance": 0.08
            },
            
            # Chief Designer - Car design leadership
            StaffRole.CHIEF_DESIGNER: {
                "cad_design": 0.20,
                "aerodynamics_expertise": 0.18,
                "innovation_ability": 0.15,
                "engineering_knowledge": 0.12,
                "leadership_ability": 0.10,
                "materials_science": 0.10,
                "simulation_expertise": 0.15
            },
            
            # Team Principal - Overall team leadership
            StaffRole.TEAM_PRINCIPAL: {
                "leadership_ability": 0.25,
                "financial_management": 0.15,
                "commercial_acumen": 0.12,
                "decision_making": 0.12,
                "negotiation_skills": 0.10,
                "team_coordination": 0.10,
                "crisis_management": 0.08,
                "communication_skills": 0.08
            }
        }
        
        return role_weights.get(self.role, {})
        
    def _get_tier_bonus(self) -> float:
        """Get effectiveness bonus based on staff tier"""
        tier_bonuses = {
            StaffTier.INTERN: -10.0,
            StaffTier.JUNIOR: -5.0,
            StaffTier.REGULAR: 0.0,
            StaffTier.SENIOR: 5.0,
            StaffTier.EXPERT: 10.0,
            StaffTier.LEGENDARY: 15.0
        }
        return tier_bonuses.get(self.tier, 0.0)
        
    def get_discipline_expertise(self, discipline: str) -> float:
        """
        Get expertise level for specific racing discipline
        
        Args:
            discipline: Racing discipline name
            
        Returns:
            Expertise level (0-100) for the discipline
        """
        expertise_map = {
            "single_seater": self.single_seater_expertise,
            "touring_car": self.touring_car_expertise,
            "rally": self.rally_expertise,
            "street_racing": self.street_racing_expertise,
            "drag_racing": self.drag_racing_expertise,
            "rallycross": self.rallycross_expertise,
            "endurance": self.endurance_expertise
        }
        
        base_expertise = expertise_map.get(discipline, 50.0)
        
        # Add general competence bonus
        general_bonus = (self.engineering_knowledge + self.years_experience) / 20
        
        return round(min(100.0, base_expertise + general_bonus), 1)
        
    def calculate_salary_demand(self, team_budget: float, role_importance: float) -> float:
        """
        Calculate salary expectation based on skills and market value
        
        Args:
            team_budget: Team's total budget
            role_importance: Importance multiplier for role (1.0-3.0)
            
        Returns:
            Expected annual salary in USD
        """
        # Base salary by tier
        base_salaries = {
            StaffTier.INTERN: 25000,
            StaffTier.JUNIOR: 45000,
            StaffTier.REGULAR: 75000,
            StaffTier.SENIOR: 120000,
            StaffTier.EXPERT: 200000,
            StaffTier.LEGENDARY: 350000
        }
        
        base_salary = base_salaries.get(self.tier, 50000)
        
        # Skill bonus (up to 50% increase)
        skill_average = self.get_role_effectiveness()
        skill_bonus = (skill_average - 50) / 100  # -50% to +50%
        
        # Experience bonus
        experience_bonus = min(self.years_experience * 0.02, 0.3)  # Up to 30%
        
        # Role importance multiplier
        role_multiplier = role_importance
        
        # Team budget factor (richer teams pay more)
        budget_factor = min(team_budget / 10_000_000, 2.0)  # Up to 2x for $10M+ budgets
        
        final_salary = base_salary * (1 + skill_bonus + experience_bonus) * role_multiplier * budget_factor
        
        return round(final_salary, -3)  # Round to nearest thousand
        
    def get_formatted_salary(self, currency: Currency = Currency.EUR, 
                           show_currency_code: bool = False) -> str:
        """
        Get formatted salary string in specified currency
        
        Args:
            currency: Target currency for display
            show_currency_code: Whether to show currency code (e.g., "EUR")
            
        Returns:
            Formatted salary string (e.g., "€120,000" or "$130,000")
        """
        # Convert from USD (stored) to target currency
        converted_salary = currency_system.convert_amount(
            self.salary, Currency.USD, currency
        )
        return currency_system.format_amount(
            converted_salary, currency, show_currency_code
        )
        
    def calculate_salary_demand_in_currency(self, team_budget: float, 
                                          role_importance: float,
                                          currency: Currency = Currency.EUR) -> float:
        """
        Calculate salary demand in specified currency
        
        Args:
            team_budget: Team's total budget in specified currency
            role_importance: Role importance multiplier
            currency: Target currency
            
        Returns:
            Expected salary in target currency
        """
        # Convert team budget to USD for calculation
        usd_budget = currency_system.convert_amount(team_budget, currency, Currency.USD)
        
        # Calculate salary in USD
        usd_salary = self.calculate_salary_demand(usd_budget, role_importance)
        
        # Convert result to target currency
        return currency_system.convert_amount(usd_salary, Currency.USD, currency)
        
    def get_contract_value_display(self, currency: Currency = Currency.EUR) -> Dict[str, str]:
        """
        Get comprehensive contract information for display
        
        Args:
            currency: Display currency
            
        Returns:
            Dictionary with formatted contract details
        """
        annual_salary = currency_system.convert_amount(
            self.salary, Currency.USD, currency
        )
        total_value = annual_salary * self.contract_length
        
        return {
            "annual_salary": currency_system.format_amount(annual_salary, currency, True),
            "contract_length": f"{self.contract_length} year{'s' if self.contract_length != 1 else ''}",
            "total_value": currency_system.format_amount(total_value, currency, True),
            "contract_type": self.contract_type.replace("_", " ").title(),
            "job_satisfaction": f"{self.job_satisfaction:.1f}%",
            "performance_rating": f"{self.performance_rating:.1f}%"
        }
        
    def __repr__(self):
        return f"<StaffMember(name='{self.name}', role='{self.role.value}', tier='{self.tier.value}', effectiveness={self.get_role_effectiveness():.1f})>"


@dataclass 
class TeamStaffing:
    """
    Team staffing configuration with budget constraints
    
    Manages the complete staff roster for a racing team, including
    budget allocation, role requirements, and performance impact.
    """
    
    team_id: int
    discipline: str
    
    # Budget allocation
    total_budget: float = 5_000_000.0         # Total team budget
    personnel_budget: float = 1_500_000.0     # Staff salary budget
    
    # Staff roster
    staff_members: List[StaffMember] = field(default_factory=list)
    
    # Role requirements by discipline and budget level
    minimum_staff_requirements: Dict[str, int] = field(default_factory=dict)
    optimal_staff_targets: Dict[str, int] = field(default_factory=dict)
    
    # Performance multipliers
    staff_performance_multiplier: float = 1.0  # Overall team performance impact
    development_speed_multiplier: float = 1.0  # Car development speed
    data_access_level: float = 50.0            # Information visibility (0-100)
    
    def calculate_staff_costs(self) -> float:
        """Calculate total annual staff costs"""
        return sum(member.salary for member in self.staff_members)
        
    def get_role_coverage(self) -> Dict[StaffRole, int]:
        """Get count of staff members by role"""
        coverage = {}
        for member in self.staff_members:
            coverage[member.role] = coverage.get(member.role, 0) + 1
        return coverage
        
    def get_discipline_expertise_level(self, discipline: str) -> float:
        """
        Calculate team's expertise level for specific discipline
        
        Args:
            discipline: Racing discipline to evaluate
            
        Returns:
            Team expertise level (0-100) for the discipline
        """
        if not self.staff_members:
            return 0.0
            
        # Weight expertise by role importance
        role_weights = {
            StaffRole.TECHNICAL_DIRECTOR: 0.20,
            StaffRole.CHIEF_ENGINEER: 0.15,
            StaffRole.CHIEF_DESIGNER: 0.15,
            StaffRole.DATA_ANALYST: 0.12,
            StaffRole.RACE_STRATEGIST: 0.10,
            # Other roles get lower weights
        }
        
        total_weighted_expertise = 0.0
        total_weight = 0.0
        
        for member in self.staff_members:
            weight = role_weights.get(member.role, 0.05)  # Default weight for other roles
            expertise = member.get_discipline_expertise(discipline)
            
            total_weighted_expertise += expertise * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0.0
            
        return round(total_weighted_expertise / total_weight, 1)
        
    def calculate_information_access_level(self) -> float:
        """
        Calculate what level of information/data the team can access
        
        Better analysts and engineers provide more detailed insights
        into performance, competitor analysis, and strategic planning.
        This creates a "fog of war" effect where teams with better
        staff can see more detailed information.
        
        Returns:
            Information access level (0-100) where:
            0-25: Basic information only
            26-50: Standard information with some analysis
            51-75: Detailed analysis and insights
            76-100: Advanced analytics and predictive capabilities
        """
        if not self.staff_members:
            return 10.0  # Minimal information with no staff
            
        # Key roles for information access
        analyst_roles = [
            StaffRole.DATA_ANALYST,
            StaffRole.PERFORMANCE_ANALYST,
            StaffRole.TELEMETRY_SPECIALIST,
            StaffRole.TECHNICAL_DIRECTOR
        ]
        
        # Calculate analytical capability
        analytical_power = 0.0
        analyst_count = 0
        
        for member in self.staff_members:
            if member.role in analyst_roles:
                # Weight analytical skills heavily
                analytical_capability = (
                    member.data_analysis * 0.3 +
                    member.telemetry_analysis * 0.25 +
                    member.statistical_methods * 0.2 +
                    member.predictive_analytics * 0.15 +
                    member.pattern_recognition * 0.1
                )
                analytical_power += analytical_capability
                analyst_count += 1
                
        # Base information level from general staff competence
        if analyst_count > 0:
            average_analytical_power = analytical_power / analyst_count
        else:
            average_analytical_power = 25.0  # Limited without dedicated analysts
            
        # Bonus for multiple analysts (diminishing returns)
        analyst_bonus = min(analyst_count * 5, 20)  # Up to +20 for 4+ analysts
        
        # Technology budget impact (better tools = better analysis)
        tech_budget_factor = min(self.total_budget / 2_000_000, 1.5)  # Up to 1.5x for $2M+ budgets
        
        final_access_level = (average_analytical_power + analyst_bonus) * tech_budget_factor
        
        return round(min(100.0, max(10.0, final_access_level)), 1)
        
    def get_missing_critical_roles(self) -> List[StaffRole]:
        """Identify critical roles that the team is missing"""
        current_roles = {member.role for member in self.staff_members}
        
        # Critical roles every team needs
        critical_roles = [
            StaffRole.TEAM_MANAGER,
            StaffRole.CHIEF_ENGINEER,
            StaffRole.PIT_CREW_CHIEF,
        ]
        
        # Additional roles based on budget level
        if self.total_budget > 3_000_000:
            critical_roles.extend([
                StaffRole.TECHNICAL_DIRECTOR,
                StaffRole.DATA_ANALYST,
                StaffRole.RACE_STRATEGIST
            ])
            
        if self.total_budget > 8_000_000:
            critical_roles.extend([
                StaffRole.CHIEF_DESIGNER,
                StaffRole.AERODYNAMICS_ENGINEER
            ])
            
        return [role for role in critical_roles if role not in current_roles]
        
    def get_budget_breakdown(self, currency: Currency = Currency.EUR) -> Dict[str, str]:
        """
        Get formatted budget breakdown in specified currency
        
        Args:
            currency: Display currency
            
        Returns:
            Dictionary with formatted budget information
        """
        # Convert budgets from USD to target currency
        total_budget_converted = currency_system.convert_amount(
            self.total_budget, Currency.USD, currency
        )
        personnel_budget_converted = currency_system.convert_amount(
            self.personnel_budget, Currency.USD, currency
        )
        
        current_costs = sum(
            currency_system.convert_amount(member.salary, Currency.USD, currency)
            for member in self.staff_members
        )
        
        remaining_budget = personnel_budget_converted - current_costs
        budget_utilization = (current_costs / personnel_budget_converted) * 100 if personnel_budget_converted > 0 else 0
        
        return {
            "total_budget": currency_system.format_amount(total_budget_converted, currency, True),
            "personnel_budget": currency_system.format_amount(personnel_budget_converted, currency, True),
            "current_costs": currency_system.format_amount(current_costs, currency, True),
            "remaining_budget": currency_system.format_amount(remaining_budget, currency, True),
            "budget_utilization": f"{budget_utilization:.1f}%",
            "staff_count": str(len(self.staff_members)),
            "info_access_level": f"{self.calculate_information_access_level():.1f}/100"
        }
        
    def check_budget_compliance(self, discipline: str = "single_seater") -> Dict[str, Any]:
        """
        Check compliance with racing discipline budget caps
        
        Args:
            discipline: Racing discipline for budget cap reference (single_seater, production_touring, etc.)
            
        Returns:
            Dictionary with compliance information
        """
        try:
            budget_cap_usd = currency_system.get_budget_cap(discipline, Currency.USD)
            over_budget = self.total_budget > budget_cap_usd
            
            return {
                "discipline": discipline,
                "budget_cap": currency_system.get_formatted_budget_cap(discipline, Currency.EUR),
                "team_budget": currency_system.format_amount(
                    currency_system.convert_amount(self.total_budget, Currency.USD, Currency.EUR), 
                    Currency.EUR, True
                ),
                "compliant": not over_budget,
                "excess_amount": currency_system.format_amount(
                    currency_system.convert_amount(max(0, self.total_budget - budget_cap_usd), Currency.USD, Currency.EUR),
                    Currency.EUR, True
                ) if over_budget else "€0",
                "utilization_percentage": f"{(self.total_budget / budget_cap_usd) * 100:.1f}%"
            }
        except ValueError:
            return {"error": f"Unknown discipline: {discipline}"}
        
    def get_staff_salary_summary(self, currency: Currency = Currency.EUR) -> List[Dict[str, str]]:
        """
        Get summary of all staff salaries in specified currency
        
        Args:
            currency: Display currency
            
        Returns:
            List of staff salary information
        """
        staff_summary = []
        
        for member in sorted(self.staff_members, key=lambda x: x.salary, reverse=True):
            converted_salary = currency_system.convert_amount(
                member.salary, Currency.USD, currency
            )
            
            staff_summary.append({
                "name": member.name,
                "role": member.role.value.replace("_", " ").title(),
                "tier": member.tier.value.title(),
                "annual_salary": currency_system.format_amount(converted_salary, currency),
                "contract_years": str(member.contract_length),
                "effectiveness": f"{member.get_role_effectiveness():.1f}%",
                "nationality": member.nationality
            })
            
        return staff_summary
        
    def __repr__(self):
        return f"<TeamStaffing(team_id={self.team_id}, staff_count={len(self.staff_members)}, budget=${self.total_budget:,.0f}, info_access={self.calculate_information_access_level():.1f})>"


# Helper functions for staff generation and management

def generate_staff_requirements(budget: float, discipline: str) -> Dict[StaffRole, Tuple[int, int]]:
    """
    Generate minimum and optimal staff requirements based on budget and discipline
    
    Args:
        budget: Team's total budget
        discipline: Primary racing discipline
        
    Returns:
        Dict mapping roles to (minimum, optimal) staff counts
    """
    requirements = {}
    
    # Budget tiers
    if budget < 1_000_000:  # Budget tier
        requirements.update({
            StaffRole.TEAM_MANAGER: (1, 1),
            StaffRole.CHIEF_ENGINEER: (1, 1),
            StaffRole.MECHANIC: (2, 4),
            StaffRole.PIT_CREW_MEMBER: (4, 6),
        })
    elif budget < 3_000_000:  # Mid-tier
        requirements.update({
            StaffRole.TEAM_MANAGER: (1, 1),
            StaffRole.CHIEF_ENGINEER: (1, 1),
            StaffRole.DATA_ANALYST: (1, 2),
            StaffRole.RACE_STRATEGIST: (1, 1),
            StaffRole.MECHANIC: (3, 6),
            StaffRole.PIT_CREW_CHIEF: (1, 1),
            StaffRole.PIT_CREW_MEMBER: (6, 8),
        })
    elif budget < 8_000_000:  # Professional tier
        requirements.update({
            StaffRole.TEAM_PRINCIPAL: (1, 1),
            StaffRole.TECHNICAL_DIRECTOR: (1, 1),
            StaffRole.CHIEF_ENGINEER: (1, 2),
            StaffRole.DATA_ANALYST: (2, 3),
            StaffRole.RACE_STRATEGIST: (1, 2),
            StaffRole.CHIEF_DESIGNER: (1, 1),
            StaffRole.AERODYNAMICS_ENGINEER: (1, 2),
            StaffRole.MECHANIC: (4, 8),
            StaffRole.PIT_CREW_CHIEF: (1, 2),
            StaffRole.PIT_CREW_MEMBER: (8, 12),
        })
    else:  # Top-tier (F1 level)
        requirements.update({
            StaffRole.TEAM_PRINCIPAL: (1, 1),
            StaffRole.TECHNICAL_DIRECTOR: (1, 1),
            StaffRole.CHIEF_ENGINEER: (2, 3),
            StaffRole.DATA_ANALYST: (3, 5),
            StaffRole.PERFORMANCE_ANALYST: (2, 3),
            StaffRole.TELEMETRY_SPECIALIST: (1, 2),
            StaffRole.RACE_STRATEGIST: (2, 2),
            StaffRole.CHIEF_DESIGNER: (1, 1),
            StaffRole.AERODYNAMICS_ENGINEER: (2, 4),
            StaffRole.ENGINE_ENGINEER: (1, 2),
            StaffRole.SUSPENSION_ENGINEER: (1, 2),
            StaffRole.SIMULATOR_ENGINEER: (1, 2),
            StaffRole.MECHANIC: (6, 12),
            StaffRole.PIT_CREW_CHIEF: (2, 2),
            StaffRole.PIT_CREW_MEMBER: (12, 16),
        })
        
    return requirements


def calculate_role_importance(role: StaffRole, discipline: str) -> float:
    """
    Calculate importance multiplier for role in specific discipline
    
    Args:
        role: Staff role
        discipline: Racing discipline
        
    Returns:
        Importance multiplier (0.5-3.0)
    """
    # Base importance by role
    base_importance = {
        StaffRole.TEAM_PRINCIPAL: 3.0,
        StaffRole.TECHNICAL_DIRECTOR: 2.5,
        StaffRole.CHIEF_ENGINEER: 2.0,
        StaffRole.CHIEF_DESIGNER: 2.0,
        StaffRole.DATA_ANALYST: 1.8,
        StaffRole.RACE_STRATEGIST: 1.5,
        StaffRole.AERODYNAMICS_ENGINEER: 1.8,
        StaffRole.PIT_CREW_CHIEF: 1.3,
        StaffRole.MECHANIC: 1.0,
        StaffRole.PIT_CREW_MEMBER: 0.8,
    }
    
    importance = base_importance.get(role, 1.0)
    
    # Discipline-specific adjustments
    discipline_adjustments = {
        "single_seater": {
            StaffRole.AERODYNAMICS_ENGINEER: 1.5,  # Very important in F1
            StaffRole.DATA_ANALYST: 1.3,
            StaffRole.TELEMETRY_SPECIALIST: 1.4,
        },
        "endurance": {
            StaffRole.RACE_STRATEGIST: 1.4,  # Strategy critical in long races
            StaffRole.MECHANIC: 1.2,  # Reliability important
            StaffRole.PIT_CREW_CHIEF: 1.3,
        },
        "rally": {
            StaffRole.SUSPENSION_ENGINEER: 1.5,  # Critical for rally
            StaffRole.WEATHER_SPECIALIST: 1.3,
            StaffRole.TEST_ENGINEER: 1.2,
        }
    }
    
    if discipline in discipline_adjustments and role in discipline_adjustments[discipline]:
        importance *= discipline_adjustments[discipline][role]
        
    return round(min(3.0, max(0.5, importance)), 2)


# Export all classes and functions
__all__ = [
    'StaffRole', 'StaffTier', 'BudgetCategory',
    'StaffMember', 'TeamStaffing',
    'generate_staff_requirements', 'calculate_role_importance'
]