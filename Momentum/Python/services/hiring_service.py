"""
Hiring & Contract Service - Personnel Management (UC-15, UC-16, UC-17, UC-18)

Handles driver and staff hiring with:
- Contract validation and budget checks
- Salary cap enforcement
- Market availability filtering
- Contract release with buyout costs

Key Features:
- Budget validation before signing
- Salary cap enforcement per discipline
- Performance-based salary estimation
- Contract buyout calculations

Authors: Eoin Fitzsimons
"""

import math
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Import database extensions to add hiring methods
import database.database_extensions  # noqa
from database.database_manager import DatabaseManager
from database.models import Driver, Team, StaffMember
from config import DATABASE_PATH


class HiringService:
    """
    Hiring & Contract Service
    
    Manages personnel hiring, contracts, and budget validation
    for teams across all disciplines.
    """
    
    # Salary cap limits by discipline (annual, in EUR)
    SALARY_CAPS = {
        'SINGLE_SEATER': 130_000_000,      # F1-style cap
        'PRODUCTION_TOURING': 50_000_000,  # Touring car cap
        'URBAN_STREET': 35_000_000,        # Street racing cap
        'DRAG_ACCELERATION': 25_000_000,   # Drag racing cap
        'SPRINT_RALLYCROSS': 30_000_000,   # Rallycross cap
        'ENDURANCE': 60_000_000            # Endurance cap (Le Mans)
    }
    
    # Base salary ranges for staff roles (annual, in EUR)
    STAFF_SALARY_RANGES = {
        'TEAM_PRINCIPAL': (500_000, 5_000_000),
        'TECHNICAL_DIRECTOR': (400_000, 3_000_000),
        'RACE_ENGINEER': (150_000, 800_000),
        'STRATEGIST': (150_000, 600_000),
        'DATA_ANALYST': (80_000, 300_000),
        'MECHANIC': (50_000, 150_000),
        'AERODYNAMICIST': (120_000, 500_000),
        'POWERTRAIN_ENGINEER': (140_000, 550_000),
        'SUSPENSION_ENGINEER': (130_000, 520_000),
        'TYRE_SPECIALIST': (110_000, 450_000),
        'CREW_CHIEF': (180_000, 700_000),
        'DRIFT_COACH': (160_000, 650_000),
        'SIMULATOR_DRIVER': (90_000, 250_000),
        'SPORTS_PSYCHOLOGIST': (120_000, 400_000),
        'LOGISTICS_MANAGER': (100_000, 350_000),
        'MARKETING_DIRECTOR': (120_000, 500_000)
    }
    
    # Error messages
    TEAM_NOT_FOUND_ERROR = "Team not found"
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialise hiring service with database connection"""
        self.db = DatabaseManager(db_path)
    
    # ========================================================================
    # SALARY ESTIMATION
    # ========================================================================
    
    def estimate_driver_salary(self, driver: Driver, discipline: str) -> float:
        """
        Estimate fair market salary for a driver
        
        Factors:
        - Average skill rating (primary)
        - Career achievements (wins, podiums, points)
        - Experience (seasons active)
        - Age (peak vs. rookie vs. veteran)
        - Discipline salary cap
        
        Args:
            driver: Driver object
            discipline: Racing discipline
            
        Returns:
            Estimated annual salary in EUR
        """
        # Get discipline salary cap
        cap = self.SALARY_CAPS.get(discipline, 50_000_000)
        
        # Calculate skill-based salary (50-95% of position budget)
        avg_skill = (driver.speed + driver.racecraft + driver.consistency) / 3.0
        skill_factor = avg_skill / 100.0
        
        # Career achievement multiplier
        achievement_bonus = 1.0
        if driver.career_points > 1000:
            achievement_bonus = 1.3
        elif driver.career_points > 500:
            achievement_bonus = 1.2
        elif driver.career_points > 100:
            achievement_bonus = 1.1
        
        # Experience multiplier
        experience_factor = 1.0 + (driver.seasons_active * 0.02)  # 2% per season
        experience_factor = min(experience_factor, 1.5)  # Cap at 50% bonus
        
        # Age adjustment
        age = driver.computed_age
        age_factor = 1.0
        if age < 25:
            age_factor = 0.7  # Rookie discount
        elif age > 35:
            age_factor = 0.85  # Veteran discount
        
        # Base salary calculation (typical driver gets 3-8M from cap)
        base_salary = (cap * 0.05) * skill_factor  # 5% of cap as base
        
        # Apply multipliers
        final_salary = base_salary * achievement_bonus * experience_factor * age_factor
        
        # Clamp to reasonable range (500k minimum, 20% of cap maximum)
        min_salary = 500_000
        max_salary = cap * 0.20
        
        return max(min_salary, min(final_salary, max_salary))
    
    def estimate_staff_salary(self, role: str, rating: float) -> float:
        """
        Estimate fair market salary for staff member
        
        Args:
            role: Staff role
            rating: Skill rating (0-100)
            
        Returns:
            Estimated annual salary in EUR
        """
        salary_range = self.STAFF_SALARY_RANGES.get(role.upper(), (50_000, 200_000))
        min_salary, max_salary = salary_range
        
        # Scale linearly by rating
        rating_factor = rating / 100.0
        estimated = min_salary + (max_salary - min_salary) * rating_factor
        
        return round(estimated, -3)  # Round to nearest thousand
    
    # ========================================================================
    # BUDGET VALIDATION
    # ========================================================================
    
    def calculate_team_salary_commitment(self, team_id: int) -> float:
        """
        Calculate team's total annual salary commitment
        
        Includes all contracted drivers and staff.
        
        Args:
            team_id: Team ID
            
        Returns:
            Total annual salary in EUR
        """
        total = 0.0
        
        # Get all contracted drivers
        drivers = self.db.get_drivers_by_team(team_id)
        for driver in drivers:
            if driver.salary:
                total += driver.salary
        
        # Add contracted staff salaries where available.
        with self.db.get_connection() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(annual_salary), 0) AS staff_salary_total
                FROM staff_members
                WHERE current_team_id = ?
                """,
                (team_id,)
            ).fetchone()
            if row:
                total += float(row["staff_salary_total"] or 0.0)
        
        return total
    
    def check_salary_cap_compliance(self, team_id: int, 
                                   additional_salary: float = 0.0) -> Tuple[bool, float, float]:
        """
        Check if team is within salary cap limits
        
        Args:
            team_id: Team ID
            additional_salary: Proposed additional salary to check
            
        Returns:
            Tuple of (is_compliant, current_commitment, cap_limit)
        """
        team = self.db.get_team(team_id)
        if not team:
            return (False, 0.0, 0.0)
        
        # Get salary cap for discipline
        cap = self.SALARY_CAPS.get(team.discipline, 50_000_000)
        
        # Calculate current commitment
        current = self.calculate_team_salary_commitment(team_id)
        
        # Check compliance with additional salary
        projected = current + additional_salary
        is_compliant = projected <= cap
        
        return (is_compliant, current, cap)
    
    def validate_contract_budget(self, team_id: int, 
                                annual_salary: float,
                                contract_length: int) -> Tuple[bool, str]:
        """
        Validate team can afford contract
        
        Checks:
        1. Team has sufficient budget for signing bonus
        2. Salary cap compliance
        3. Reasonable budget buffer
        
        Args:
            team_id: Team ID
            annual_salary: Annual salary
            contract_length: Contract duration in seasons
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        team = self.db.get_team(team_id)
        if not team:
            return (False, self.TEAM_NOT_FOUND_ERROR)
        
        # Calculate total contract value
        total_value = annual_salary * contract_length
        
        # Check 1: Immediate budget for signing bonus (20% of total)
        signing_bonus = total_value * 0.20
        if team.budget < signing_bonus:
            return (False, f"Insufficient budget for signing bonus. Need {signing_bonus:,.0f} EUR, have {team.budget:,.0f} EUR")
        
        # Check 2: Salary cap compliance
        is_compliant, current, cap = self.check_salary_cap_compliance(team_id, annual_salary)
        if not is_compliant:
            return (False, f"Salary cap exceeded. Current: {current:,.0f} EUR, Cap: {cap:,.0f} EUR, Additional: {annual_salary:,.0f} EUR")
        
        # Check 3: Budget buffer (keep at least 10% of cap in reserve)
        required_buffer = cap * 0.10
        if (team.budget - signing_bonus) < required_buffer:
            return (False, f"Insufficient budget buffer. Need {required_buffer:,.0f} EUR reserve")
        
        return (True, "Contract validated")
    
    # ========================================================================
    # DRIVER HIRING (UC-15, UC-16)
    # ========================================================================
    
    def get_available_drivers(self, discipline: Optional[str] = None,
                             min_rating: float = 0.0,
                             max_salary: Optional[float] = None,
                             page: int = 1,
                             page_size: int = 50,
                             sort_by: str = "rating",
                             sort_order: str = "desc") -> Tuple[List[Dict], int]:
        """
        UC-15: Get available drivers for hire
        
        Args:
            discipline: Filter by preferred discipline
            min_rating: Minimum average skill rating
            max_salary: Maximum salary budget
            page: Page number
            page_size: Results per page
            
        Returns:
            Tuple of (driver list with salary estimates, total count)
        """
        drivers, total = self.db.get_available_drivers(  # type: ignore[attr-defined]
            discipline=discipline,
            min_rating=min_rating,
            max_salary=max_salary,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Add salary estimates
        result = []
        for driver in drivers:
            driver_dict = {
                'id': driver.id,
                'name': driver.name,
                'nationality': driver.nationality,
                'age': driver.computed_age,
                'speed': driver.speed,
                'racecraft': driver.racecraft,
                'consistency': driver.consistency,
                'career_points': driver.career_points,
                'career_podiums': driver.career_podiums,
                'career_starts': driver.career_starts,
                'seasons_active': driver.seasons_active,
                'preferred_discipline': driver.preferred_discipline,
                'career_phase': driver.career_phase,
                'contract_end_season': driver.contract_end_season,
                'estimated_salary': self.estimate_driver_salary(
                    driver, 
                    discipline or driver.preferred_discipline
                ),
                'contract_status': 'available'
            }
            result.append(driver_dict)
        
        return (result, total)
    
    def sign_driver_contract(self, team_id: int, driver_id: int,
                           contract_length: int, salary: float,
                           performance_bonus: float = 0.0,
                           start_season: Optional[int] = None) -> Tuple[bool, str, Dict]:
        """
        UC-16: Sign driver to contract
        
        Args:
            team_id: Team ID
            driver_id: Driver ID
            contract_length: Contract duration (1-5 seasons)
            salary: Annual salary
            performance_bonus: Additional bonus for performance
            
        Returns:
            Tuple of (success, message, contract_details)
        """
        # Validate inputs
        if contract_length < 1 or contract_length > 5:
            return (False, "Contract length must be 1-5 seasons", {})
        
        # Check driver availability
        driver = self.db.get_driver(driver_id)
        if not driver:
            return (False, "Driver not found", {})
        
        if driver.current_team_id is not None:
            return (False, f"Driver already contracted to team {driver.current_team_id}", {})
        
        # Check team exists
        team = self.db.get_team(team_id)
        if not team:
            return (False, self.TEAM_NOT_FOUND_ERROR, {})
        
        # Validate budget
        is_valid, error_msg = self.validate_contract_budget(team_id, salary, contract_length)
        if not is_valid:
            return (False, error_msg, {})
        
        # Calculate costs
        total_value = salary * contract_length
        signing_bonus = total_value * 0.20
        contract_start = start_season or datetime.now().year
        contract_end = contract_start + contract_length - 1
        
        # Sign contract
        success = self.db.sign_driver_contract(  # type: ignore[attr-defined]
            driver_id,
            team_id,
            contract_length,
            salary,
            contract_start,
            performance_bonus
        )
        if not success:
            return (False, "Database error during contract signing", {})
        
        # Deduct signing bonus from team budget
        new_budget = self.db.update_team_budget(team_id, -signing_bonus)  # type: ignore[attr-defined]
        
        # Return contract details
        contract_details = {
            'driver_id': driver_id,
            'driver_name': driver.name,
            'team_id': team_id,
            'team_name': team.name,
            'contract_length': contract_length,
            'salary': salary,
            'performance_bonus': performance_bonus,
            'contract_start_season': contract_start,
            'contract_end_season': contract_end,
            'total_contract_value': total_value,
            'signing_bonus_paid': signing_bonus,
            'remaining_budget': new_budget
        }
        
        return (True, f"Successfully signed {driver.name} to {contract_length}-season contract", contract_details)
    
    # ========================================================================
    # PERSONNEL RELEASE HELPERS
    # ========================================================================
    
    def _release_driver(self, team_id: int, personnel_id: int, 
                       team: Team, buyout_percentage: float) -> Tuple[bool, str, Dict]:
        """Helper to release driver from contract"""
        driver = self.db.get_driver(personnel_id)
        if not driver:
            return (False, "Driver not found", {})
        
        if driver.current_team_id != team_id:
            return (False, "Driver not contracted to this team", {})
        
        # Calculate buyout (remaining contract value * percentage)
        current_season = datetime.now().year
        remaining_seasons = driver.contract_length or 1
        if hasattr(driver, 'contract_end_season') and driver.contract_end_season:
            remaining_seasons = max(1, driver.contract_end_season - current_season + 1)
        remaining_value = (driver.salary or 0) * remaining_seasons
        buyout_cost = remaining_value * buyout_percentage
        
        # Check budget
        if team.budget < buyout_cost:
            return (False, f"Insufficient budget for buyout. Need {buyout_cost:,.0f} EUR", {})
        
        # Release driver
        self.db.release_driver(personnel_id)  # type: ignore[attr-defined]
        new_budget = self.db.update_team_budget(team_id, -buyout_cost)  # type: ignore[attr-defined]
        
        return (True, f"Released {driver.name} from contract", {
            'personnel_id': personnel_id,
            'personnel_name': driver.name,
            'team_id': team_id,
            'buyout_cost': buyout_cost,
            'remaining_budget': new_budget
        })
    
    def _release_staff(self, team_id: int, personnel_id: int,
                      team: Team) -> Tuple[bool, str, Dict]:
        """Helper to release staff member from contract"""
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM staff_members WHERE id = ?", (personnel_id,)).fetchone()
            if not row:
                return (False, "Staff member not found", {})
            
            from database.models import StaffMember
            staff = StaffMember(**dict(row))
            
            if staff.current_team_id != team_id:
                return (False, "Staff not contracted to this team", {})
        
        # Estimate buyout at 50k EUR flat fee
        buyout_cost = 50_000
        
        if team.budget < buyout_cost:
            return (False, "Insufficient budget for buyout", {})
        
        # Release staff
        self.db.release_staff(personnel_id)  # type: ignore[attr-defined]
        new_budget = self.db.update_team_budget(team_id, -buyout_cost)  # type: ignore[attr-defined]
        
        return (True, f"Released {staff.name} from contract", {
            'personnel_id': personnel_id,
            'personnel_name': staff.name,
            'team_id': team_id,
            'buyout_cost': buyout_cost,
            'remaining_budget': new_budget
        })
    
    def release_personnel_contract(self, team_id: int, personnel_id: int,
                                  personnel_type: str,
                                  buyout_percentage: float = 0.5) -> Tuple[bool, str, Dict]:
        """
        Release driver or staff from contract with buyout
        
        Args:
            team_id: Team ID
            personnel_id: Driver or staff ID
            personnel_type: 'driver' or 'staff'
            buyout_percentage: Percentage of remaining contract value (0.0-1.0)
            
        Returns:
            Tuple of (success, message, release_details)
        """
        team = self.db.get_team(team_id)
        if not team:
            return (False, self.TEAM_NOT_FOUND_ERROR, {})
        
        if personnel_type.lower() == 'driver':
            return self._release_driver(team_id, personnel_id, team, buyout_percentage)
        elif personnel_type.lower() == 'staff':
            return self._release_staff(team_id, personnel_id, team)
        else:
            return (False, "Invalid personnel type. Must be 'driver' or 'staff'", {})
    
    # ========================================================================
    # STAFF HIRING (UC-17, UC-18)
    # ========================================================================
    
    def get_available_staff(self, role: Optional[str] = None,
                          min_rating: float = 0.0,
                          page: int = 1,
                          page_size: int = 50,
                          sort_by: str = "rating",
                          sort_order: str = "desc") -> Tuple[List[Dict], int]:
        """
        UC-17: Get available staff for hire
        
        Args:
            role: Filter by staff role
            min_rating: Minimum skill rating
            page: Page number
            page_size: Results per page
            
        Returns:
            Tuple of (staff list with salary estimates, total count)
        """
        staff_list, total = self.db.get_available_staff(  # type: ignore[attr-defined]
            role=role,
            min_rating=min_rating,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Add salary estimates
        result = []
        for staff in staff_list:
            staff_dict = {
                'id': staff.id,
                'name': staff.name,
                'role': staff.role,
                'rating': staff.rating,
                'current_team_id': staff.current_team_id,
                'contract_end_season': staff.contract_end_season,
                'estimated_salary': self.estimate_staff_salary(staff.role, staff.rating),
                'contract_status': 'available' if staff.current_team_id is None else 'contracted'
            }
            result.append(staff_dict)
        
        return (result, total)
    
    def sign_staff_contract(self, team_id: int, staff_id: int,
                          contract_length: int, salary: float,
                          start_season: Optional[int] = None) -> Tuple[bool, str, Dict]:
        """
        UC-18: Sign staff to contract
        
        Args:
            team_id: Team ID
            staff_id: Staff ID
            contract_length: Contract duration (1-5 seasons)
            salary: Annual salary
            
        Returns:
            Tuple of (success, message, contract_details)
        """
        # Validate inputs
        if contract_length < 1 or contract_length > 5:
            return (False, "Contract length must be 1-5 seasons", {})
        
        # Check staff availability
        from database.models import StaffMember
        # Get staff using raw query since get_available_staff returns tuples
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM staff_members WHERE id = ?", (staff_id,)).fetchone()
            if not row:
                return (False, "Staff member not found", {})
            staff = StaffMember(**dict(row))
        
        if staff.current_team_id is not None:
            return (False, f"Staff already contracted to team {staff.current_team_id}", {})
        
        # Check team exists
        team = self.db.get_team(team_id)
        if not team:
            return (False, self.TEAM_NOT_FOUND_ERROR, {})
        
        # Validate budget (staff costs less, 10% signing bonus)
        total_value = salary * contract_length
        signing_bonus = total_value * 0.10
        
        if team.budget < signing_bonus:
            return (False, f"Insufficient budget. Need {signing_bonus:,.0f} EUR", {})

        # Staff salaries count against cap as well.
        is_compliant, current, cap = self.check_salary_cap_compliance(team_id, salary)
        if not is_compliant:
            return (False, f"Salary cap exceeded. Current: {current:,.0f} EUR, Cap: {cap:,.0f} EUR, Additional: {salary:,.0f} EUR", {})

        contract_start = start_season or datetime.now().year
        contract_end = contract_start + contract_length - 1
        
        # Sign contract
        success = self.db.sign_staff_contract(  # type: ignore[attr-defined]
            staff_id,
            team_id,
            contract_length,
            salary,
            contract_start
        )
        if not success:
            return (False, "Database error during contract signing", {})
        
        # Deduct signing bonus
        new_budget = self.db.update_team_budget(team_id, -signing_bonus)  # type: ignore[attr-defined]
        
        # Return contract details
        contract_details = {
            'staff_id': staff_id,
            'staff_name': staff.name,
            'team_id': team_id,
            'team_name': team.name,
            'contract_length': contract_length,
            'salary': salary,
            'contract_start_season': contract_start,
            'contract_end_season': contract_end,
            'total_contract_value': total_value,
            'signing_bonus_paid': signing_bonus,
            'remaining_budget': new_budget
        }
        
        return (True, f"Successfully signed {staff.name} to {contract_length}-season contract", contract_details)
    
    # ========================================================================
    # CONTRACT RELEASE
    # ========================================================================
    

