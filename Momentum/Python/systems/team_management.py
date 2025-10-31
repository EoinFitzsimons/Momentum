"""
Team Management System

Comprehensive team management including:
- Driver hiring/firing
- Staff management
- Contract negotiations
- Team performance tracking
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import random

from database.database_manager import DatabaseManager


@dataclass
class Contract:
    """Driver or staff contract"""
    person_id: int
    person_name: str
    role: str  # "driver", "engineer", "manager", etc.
    salary_per_year: float  # Millions
    contract_years: int
    years_remaining: int
    performance_bonus: float = 0.0
    signing_bonus: float = 0.0
    buyout_clause: float = 0.0


@dataclass
class TeamFinancials:
    """Team financial status"""
    team_id: int
    current_budget: float  # Millions
    season_budget: float
    
    # Income sources
    prize_money: float = 0.0
    sponsorship_income: float = 0.0
    manufacturer_bonus: float = 0.0
    
    # Expenses
    driver_salaries: float = 0.0
    staff_salaries: float = 0.0
    development_costs: float = 0.0
    operational_costs: float = 0.0
    
    # Projections
    projected_end_of_season_budget: float = 0.0


class TeamManager:
    """
    Manages all team operations including:
    - Driver contracts and hiring
    - Staff management
    - Budget allocation
    - Team development priorities
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.active_contracts: Dict[int, List[Contract]] = {}  # team_id -> contracts
        self.team_financials: Dict[int, TeamFinancials] = {}  # team_id -> financials
    
    def initialize_team(self, team_id: int) -> TeamFinancials:
        """Initialize team management for a team"""
        team = self.db.get_team(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        
        # Initialize financials
        financials = TeamFinancials(
            team_id=team_id,
            current_budget=team.budget,
            season_budget=team.budget
        )
        
        # Load existing drivers as contracts
        drivers = self.db.get_drivers_by_team(team_id)
        contracts = []
        
        for driver in drivers:
            # Generate contract based on driver skill
            avg_skill = (driver.raw_speed + driver.consistency + driver.racecraft) / 3.0
            salary = self._calculate_driver_salary(avg_skill)
            
            contracts.append(Contract(
                person_id=driver.id,
                person_name=driver.name,
                role="driver",
                salary_per_year=salary,
                contract_years=2,
                years_remaining=random.randint(1, 2),
                performance_bonus=salary * 0.2,
                buyout_clause=salary * 3.0
            ))
            
            financials.driver_salaries += salary
        
        # Load staff as contracts
        staff = self.db.get_team_staff(team_id)
        for staff_member in staff[:10]:  # Limit to top 10 staff
            salary = staff_member.salary_demand / 1000000.0  # Convert to millions
            
            contracts.append(Contract(
                person_id=staff_member.id,
                person_name=staff_member.name,
                role=staff_member.role,
                salary_per_year=salary,
                contract_years=3,
                years_remaining=random.randint(1, 3)
            ))
            
            financials.staff_salaries += salary
        
        self.active_contracts[team_id] = contracts
        self.team_financials[team_id] = financials
        
        return financials
    
    def get_available_drivers(self, discipline: str, team_id: int) -> List[Dict]:
        """
        Get list of drivers available for hire
        
        Returns drivers not currently on a team or with expiring contracts
        """
        all_drivers = self.db.get_all_drivers()
        
        # Get drivers currently on other teams
        current_team_drivers = set()
        for contracts in self.active_contracts.values():
            current_team_drivers.update(
                c.person_id for c in contracts if c.role == "driver"
            )
        
        # Filter available drivers
        available = []
        for driver in all_drivers:
            # Skip if driver is already on this team
            team_drivers = self.db.get_drivers_by_team(team_id)
            if any(d.id == driver.id for d in team_drivers):
                continue
            
            # Calculate overall rating
            avg_skill = (driver.raw_speed + driver.consistency + driver.racecraft) / 3.0
            
            # Get discipline aptitude
            aptitude_attr = f"{discipline.lower()}_aptitude"
            discipline_aptitude = getattr(driver, aptitude_attr, 50.0)
            
            # Calculate asking salary
            salary = self._calculate_driver_salary(avg_skill)
            
            available.append({
                'id': driver.id,
                'name': driver.name,
                'age': driver.age,
                'nationality': driver.nationality,
                'overall_skill': round(avg_skill, 1),
                'discipline_aptitude': round(discipline_aptitude, 1),
                'asking_salary': round(salary, 2),
                'career_wins': driver.career_wins,
                'career_podiums': driver.career_podiums,
                'is_free_agent': driver.id not in current_team_drivers
            })
        
        # Sort by overall skill descending
        available.sort(key=lambda x: x['overall_skill'], reverse=True)
        
        return available
    
    def hire_driver(
        self,
        team_id: int,
        driver_id: int,
        salary: float,
        contract_years: int,
        performance_bonus: float = 0.0
    ) -> Tuple[bool, str]:
        """
        Hire a driver
        
        Returns (success, message)
        """
        # Check budget
        financials = self.team_financials.get(team_id)
        if not financials:
            financials = self.initialize_team(team_id)
        
        if financials.current_budget < salary:
            return False, f"Insufficient budget. Need €{salary}M, have €{financials.current_budget:.1f}M"
        
        # Check if team already has 2 drivers
        current_drivers = [c for c in self.active_contracts[team_id] if c.role == "driver"]
        if len(current_drivers) >= 2:
            return False, "Team already has 2 drivers. Fire one first."
        
        # Get driver
        all_drivers = self.db.get_all_drivers()
        driver = next((d for d in all_drivers if d.id == driver_id), None)
        if not driver:
            return False, "Driver not found"
        
        # Create contract
        contract = Contract(
            person_id=driver_id,
            person_name=driver.name,
            role="driver",
            salary_per_year=salary,
            contract_years=contract_years,
            years_remaining=contract_years,
            performance_bonus=performance_bonus,
            signing_bonus=salary * 0.5,  # 50% signing bonus
            buyout_clause=salary * contract_years * 1.5
        )
        
        # Deduct signing bonus and first year salary
        total_cost = contract.signing_bonus + salary
        financials.current_budget -= total_cost
        financials.driver_salaries += salary
        
        # Add contract
        self.active_contracts[team_id].append(contract)
        
        return True, f"Hired {driver.name} for €{salary}M/year ({contract_years} years). Paid €{total_cost:.1f}M upfront."
    
    def fire_driver(self, team_id: int, driver_id: int) -> Tuple[bool, str]:
        """
        Fire a driver (must pay buyout clause)
        
        Returns (success, message)
        """
        contracts = self.active_contracts.get(team_id, [])
        contract = next((c for c in contracts if c.person_id == driver_id and c.role == "driver"), None)
        
        if not contract:
            return False, "Driver not on team"
        
        # Calculate buyout cost
        buyout = contract.buyout_clause if contract.buyout_clause > 0 else contract.salary_per_year * contract.years_remaining
        
        financials = self.team_financials[team_id]
        if financials.current_budget < buyout:
            return False, f"Cannot afford buyout. Need €{buyout:.1f}M, have €{financials.current_budget:.1f}M"
        
        # Pay buyout and remove contract
        financials.current_budget -= buyout
        financials.driver_salaries -= contract.salary_per_year
        contracts.remove(contract)
        
        return True, f"Fired {contract.person_name}. Paid €{buyout:.1f}M buyout clause."
    
    def get_available_staff(self, role: Optional[str] = None) -> List[Dict]:
        """Get available staff members for hire"""
        all_staff = self.db.get_all_staff()
        
        # Get currently employed staff
        employed_staff = set()
        for contracts in self.active_contracts.values():
            employed_staff.update(
                c.person_id for c in contracts if c.role != "driver"
            )
        
        available = []
        for staff in all_staff:
            if staff.id in employed_staff:
                continue
            
            if role and staff.role != role:
                continue
            
            salary = staff.salary_demand / 1000000.0  # Convert to millions
            
            available.append({
                'id': staff.id,
                'name': staff.name,
                'role': staff.role,
                'nationality': staff.nationality,
                'skill_level': staff.technical_expertise,  # Use actual skill attribute
                'experience_years': staff.experience_years,
                'asking_salary': round(salary, 2),
                'specialization': staff.specialization
            })
        
        available.sort(key=lambda x: x['skill_level'], reverse=True)
        return available[:50]  # Return top 50
    
    def hire_staff(
        self,
        team_id: int,
        staff_id: int,
        salary: float,
        contract_years: int
    ) -> Tuple[bool, str]:
        """Hire a staff member"""
        financials = self.team_financials.get(team_id)
        if not financials:
            financials = self.initialize_team(team_id)
        
        if financials.current_budget < salary:
            return False, f"Insufficient budget"
        
        # Get staff member
        all_staff = self.db.get_all_staff()
        staff = next((s for s in all_staff if s.id == staff_id), None)
        if not staff:
            return False, "Staff member not found"
        
        # Create contract
        contract = Contract(
            person_id=staff_id,
            person_name=staff.name,
            role=staff.role,
            salary_per_year=salary,
            contract_years=contract_years,
            years_remaining=contract_years
        )
        
        financials.current_budget -= salary
        financials.staff_salaries += salary
        
        self.active_contracts[team_id].append(contract)
        
        return True, f"Hired {staff.name} ({staff.role}) for €{salary}M/year"
    
    def fire_staff(self, team_id: int, staff_id: int) -> Tuple[bool, str]:
        """Fire a staff member"""
        contracts = self.active_contracts.get(team_id, [])
        contract = next((c for c in contracts if c.person_id == staff_id and c.role != "driver"), None)
        
        if not contract:
            return False, "Staff member not on team"
        
        # Pay severance (6 months salary)
        severance = contract.salary_per_year * 0.5
        
        financials = self.team_financials[team_id]
        financials.current_budget -= severance
        financials.staff_salaries -= contract.salary_per_year
        contracts.remove(contract)
        
        return True, f"Fired {contract.person_name}. Paid €{severance:.1f}M severance."
    
    def process_race_income(self, team_id: int, position: int, fastest_lap: bool = False):
        """Add prize money from race results"""
        financials = self.team_financials.get(team_id)
        if not financials:
            return
        
        # Prize money scale
        prize_money = {
            1: 5.0, 2: 3.0, 3: 2.0, 4: 1.5, 5: 1.0,
            6: 0.8, 7: 0.6, 8: 0.4, 9: 0.2, 10: 0.1
        }
        
        amount = prize_money.get(position, 0.0)
        if fastest_lap and position <= 10:
            amount += 0.5
        
        financials.prize_money += amount
        financials.current_budget += amount
    
    def process_season_sponsorship(self, team_id: int, championship_position: int):
        """Add sponsorship income based on championship position"""
        financials = self.team_financials.get(team_id)
        if not financials:
            return
        
        # Sponsorship scale (millions)
        sponsorship = {
            1: 50.0, 2: 40.0, 3: 30.0, 4: 25.0, 5: 20.0,
            6: 15.0, 7: 12.0, 8: 10.0, 9: 8.0, 10: 6.0
        }
        
        amount = sponsorship.get(championship_position, 5.0)
        financials.sponsorship_income += amount
        financials.current_budget += amount
    
    def _calculate_driver_salary(self, skill: float) -> float:
        """Calculate driver salary based on skill (returns millions)"""
        # Scale: 50 skill = 1M, 100 skill = 10M
        base_salary = 0.5 + (skill / 100.0) * 10.0
        variance = random.uniform(0.8, 1.2)
        return round(base_salary * variance, 2)
    
    def get_team_roster(self, team_id: int) -> Dict:
        """Get complete team roster with contracts"""
        if team_id not in self.active_contracts:
            self.initialize_team(team_id)
        
        contracts = self.active_contracts[team_id]
        financials = self.team_financials[team_id]
        
        drivers = [c for c in contracts if c.role == "driver"]
        staff = [c for c in contracts if c.role != "driver"]
        
        return {
            'drivers': drivers,
            'staff': staff,
            'financials': financials,
            'total_salary_commitment': sum(c.salary_per_year for c in contracts)
        }
