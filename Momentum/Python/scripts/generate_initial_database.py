"""
Initial Database Generation - Momentum Motorsport Simulation

This script generates a complete initial database for the Momentum simulation,
including all teams, drivers, and staff across all seven racing disciplines.

Features:
- Generates teams for all 38+ leagues across 7 disciplines
- Creates realistic driver rosters (2 drivers per team for most disciplines)
- Assigns staff based on team tier and budget constraints
- Uses hybrid name generation for authentic international diversity
- Saves everything to SQLite database

Usage:
    python generate_initial_database.py

Output:
    - Populated momentum.db with ~350+ teams, ~700+ drivers, ~8000+ staff
    - Generation report with statistics and validation

"""

import os
import sys
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'database_generation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import our systems
from data.placeholder_names import (
    RACING_CATEGORIES, COUNTRIES, 
    calculate_total_entities, STAFF_ROLES, STAFF_SIZE_ESTIMATES
)
from database.database_manager import DatabaseManager
from systems.intelligent_name_generator import IntelligentNameGenerator
from systems.realistic_team_generator import generate_realistic_team_name
from database.models import Driver, Team

# Try to import staff models, but continue if not available
try:
    from database.models.staff_models import StaffMember, StaffRole, StaffTier
    STAFF_MODELS_AVAILABLE = True
except ImportError:
    logger.warning("Staff models not available - staff generation will be limited")
    STAFF_MODELS_AVAILABLE = False
    StaffTier = None


class DatabaseGenerator:
    """
    Main database generation coordinator
    
    Handles the complete generation of teams, drivers, and staff
    for all racing disciplines and leagues.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize the generator with database connection"""
        self.db_path = db_path or "database/momentum.db"
        self.db = DatabaseManager(self.db_path)
        self.name_generator = IntelligentNameGenerator()
        self.stats = {
            'teams_created': 0,
            'drivers_created': 0,
            'staff_created': 0,
            'errors': []
        }
        
    def generate_complete_database(self):
        """Generate the complete initial database"""
        logger.info("=" * 80)
        logger.info("MOMENTUM MOTORSPORT SIMULATION - DATABASE GENERATION")
        logger.info("=" * 80)
        
        # Step 1: Calculate requirements
        logger.info("\n[STATS] Calculating generation requirements...")
        totals = calculate_total_entities()
        logger.info(f"  → Teams needed: {totals['teams']:,}")
        logger.info(f"  → Drivers needed: {totals['drivers']:,}")
        logger.info(f"  → Staff needed: {totals['staff']:,}")
        logger.info(f"  → Total personnel: {totals['total_personnel']:,}")
        
        # Step 2: Generate for each discipline
        logger.info("\n[GENERATING] Teams, drivers, and staff by discipline...")
        
        for category_name, category_data in RACING_CATEGORIES.items():
            self._generate_discipline(category_name, category_data)
        
        # Step 3: Generate final report
        self._generate_report()
        
        logger.info("\n[SUCCESS] Database generation complete!")
        logger.info(f"   Teams: {self.stats['teams_created']:,}")
        logger.info(f"   Drivers: {self.stats['drivers_created']:,}")
        logger.info(f"   Staff: {self.stats['staff_created']:,}")
        
        if self.stats['errors']:
            logger.warning(f"\n[WARNING]  Encountered {len(self.stats['errors'])} errors (see log)")
    
    def _generate_discipline(self, category_name: str, category_data: Dict):
        """Generate all teams, drivers, and staff for a specific discipline"""
        logger.info(f"\n{'=' * 60}")
        logger.info(f"[CATEGORY] {category_data['name']} ({category_name})")
        logger.info(f"{'=' * 60}")
        
        for league_code, league_info in category_data['leagues'].items():
            self._generate_league(league_code, league_info, category_name)
    
    def _generate_league(self, league_code: str, league_info, category_name: str):
        """Generate teams for a specific league"""
        logger.info(f"\n  [LEAGUE] {league_info.full_name} ({league_code}) - Tier {league_info.tier}")
        
        # Determine number of teams
        num_teams = random.randint(league_info.min_teams, league_info.max_teams)
        logger.info(f"     Creating {num_teams} teams...")
        
        for team_num in range(num_teams):
            try:
                self._generate_team(league_code, league_info, category_name, team_num + 1)
            except Exception as e:
                error_msg = f"Error creating team {team_num + 1} in {league_code}: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
    
    def _generate_team(self, league_code: str, league_info, category_name: str, team_num: int):
        """Generate a single team with drivers and staff"""
        
        # Generate team with realistic name generator (base name only, no title sponsor)
        team_name = generate_realistic_team_name(
            category=category_name,
            tier=league_info.tier
        )
        
        # Determine team budget based on tier
        budget = self._calculate_team_budget(league_info.tier)
        
        # Generate headquarters location from weighted nationalities
        nationalities = self._get_weighted_nationalities()
        headquarters_country = random.choices(
            list(nationalities.keys()),
            weights=list(nationalities.values()),
            k=1
        )[0]
        
        # Generate team principal name
        gender = random.choice(["M", "F"])
        principal_data = self.name_generator.generate_unique_name(headquarters_country, gender, role='principal')
        team_principal_name = principal_data['full_name']
        
        # Create team entity
        team = Team(
            id=0,  # Auto-incremented by database
            name=team_name,
            nationality=headquarters_country,
            founded_year=random.randint(1990, 2023),
            discipline=category_name,
            tier=f"tier{league_info.tier}",  # Convert integer tier to string format (tier1, tier2, etc.)
            budget=budget,
            headquarters=f"{random.choice(['City', 'Town', 'Base'])} in {COUNTRIES[headquarters_country]}",
            team_principal=team_principal_name
        )
        
        # Save team to database and get the actual ID
        team_id = self.db.create_team(team)
        self.stats['teams_created'] += 1
        
        # Generate drivers for this team
        drivers = self._generate_drivers_for_team(
            team_id, team_name, league_code, league_info.cars_per_team
        )
        
        # Generate staff for this team
        staff = self._generate_staff_for_team(
            team_id, team_name, league_info.tier, budget, category_name
        )
        
        logger.info(f"     [OK] {team_name} ({team_id})")
        logger.info(f"       Budget: €{budget:,.0f} | Drivers: {len(drivers)} | Staff: {len(staff)}")
    
    def _generate_drivers_for_team(
        self, team_id: int, team_name: str, league_code: str, num_drivers: int
    ) -> List[Driver]:
        """Generate drivers for a team"""
        drivers = []
        
        # Get weighted nationality distribution
        nationalities = self._get_weighted_nationalities()
        
        for driver_num in range(num_drivers):
            # Select nationality
            nationality = random.choices(
                list(nationalities.keys()),
                weights=list(nationalities.values()),
                k=1
            )[0]
            
            # Generate name using intelligent generator
            gender = random.choice(["M", "F"])
            name_data = self.name_generator.generate_unique_name(nationality, gender, role='driver')
            full_name = name_data['full_name']
            
            # Generate birth date (age between 18-45)
            age = random.randint(18, 45)
            birth_year = datetime.now().year - age
            birth_date = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            
            # Create driver with randomized attributes
            # All attributes default to 50.0, we'll randomize them for variety
            driver = Driver(
                id=0,  # Auto-incremented by database
                name=full_name,
                nationality=nationality,
                birth_date=birth_date,
                age=age,
                current_team_id=team_id,
                # Core Driving Skills - randomize each
                raw_speed=random.uniform(40, 95),
                consistency=random.uniform(40, 95),
                racecraft=random.uniform(40, 95),
                overtaking=random.uniform(40, 95),
                defensive_driving=random.uniform(40, 95),
                cornering_skill=random.uniform(40, 95),
                braking_technique=random.uniform(40, 95),
                acceleration_control=random.uniform(40, 95),
                spatial_awareness=random.uniform(40, 95),
                vehicle_control=random.uniform(40, 95),
                # Physical & Mental Traits
                physical_fitness=random.uniform(50, 95),
                reaction_time=random.uniform(50, 95),
                concentration=random.uniform(50, 95),
                pressure_handling=random.uniform(40, 95),
                pain_tolerance=random.uniform(50, 95),
                g_force_tolerance=random.uniform(50, 95),
                coordination=random.uniform(50, 95),
                multitasking=random.uniform(50, 95),
                mental_resilience=random.uniform(40, 95),
                adrenaline_management=random.uniform(40, 95),
                # Technical Knowledge
                setup_knowledge=random.uniform(30, 90),
                mechanical_sympathy=random.uniform(40, 90),
                tire_management=random.uniform(40, 90),
                fuel_management=random.uniform(40, 90),
                aerodynamics_understanding=random.uniform(30, 90),
                suspension_feel=random.uniform(40, 90),
                engine_management=random.uniform(40, 90),
                data_analysis=random.uniform(30, 90),
                # Discipline Specializations - will vary based on category
                single_seater_aptitude=random.uniform(30, 95),
                touring_car_aptitude=random.uniform(30, 95),
                rally_aptitude=random.uniform(30, 95),
                street_racing_aptitude=random.uniform(30, 95),
                drag_racing_aptitude=random.uniform(30, 95),
                rallycross_aptitude=random.uniform(30, 95),
                endurance_aptitude=random.uniform(30, 95),
                # Race Craft & Strategy
                race_strategy=random.uniform(40, 90),
                pit_entry_exit=random.uniform(40, 90),
                traffic_management=random.uniform(40, 90),
                qualifying_pace=random.uniform(40, 95),
                race_pace=random.uniform(40, 95),
                starting_skill=random.uniform(40, 90),
                tyre_warming=random.uniform(40, 90),
                energy_management=random.uniform(40, 90),
                # Environmental Adaptation
                wet_weather_skill=random.uniform(30, 95),
                night_driving=random.uniform(40, 90),
                heat_tolerance=random.uniform(50, 90),
                cold_tolerance=random.uniform(50, 90),
                altitude_adaptation=random.uniform(50, 90),
                visibility_adaptation=random.uniform(40, 90),
                surface_adaptation=random.uniform(40, 90),
                # Personal & Social Traits
                media_handling=random.uniform(30, 90),
                sponsorship_appeal=random.uniform(30, 95),
                fan_engagement=random.uniform(30, 95),
                team_player=random.uniform(40, 95),
                leadership=random.uniform(30, 90),
                professionalism=random.uniform(50, 95),
            )
            
            # Save driver to database
            self.db.create_driver(driver)
            drivers.append(driver)
            self.stats['drivers_created'] += 1
        
        return drivers
    
    def _generate_staff_for_team(
        self, team_id: str, team_name: str, tier: int, budget: float, discipline: str
    ) -> List[StaffMember]:
        """Generate staff members for a team based on tier and budget"""
        staff_members = []
        
        # Get staff requirements for this tier
        tier_requirements = STAFF_SIZE_ESTIMATES.get(tier, STAFF_SIZE_ESTIMATES[6])
        
        # Get weighted nationality distribution
        nationalities = self._get_weighted_nationalities()
        
        for role_category, (min_staff, max_staff) in tier_requirements.items():
            if role_category == "drivers":
                continue  # Already handled
            
            # Determine number of staff in this category
            num_staff = random.randint(min_staff, max_staff)
            
            # Get available roles for this category
            available_roles = STAFF_ROLES.get(role_category, [])
            if not available_roles:
                continue
            
            for staff_num in range(num_staff):
                # Select role
                role_display_name = random.choice(available_roles)
                # Convert display name to database format (lowercase with underscores)
                role_name = role_display_name.lower().replace(" ", "_")
                
                # Select nationality
                nationality = random.choices(
                    list(nationalities.keys()),
                    weights=list(nationalities.values()),
                    k=1
                )[0]
                
                # Generate name using intelligent generator
                gender = random.choice(["M", "F"])
                name_data = self.name_generator.generate_unique_name(nationality, gender, role=role_name)
                
                # Generate full name for staff member
                full_staff_name = name_data['full_name']
                
                # Determine staff tier based on team tier
                staff_tier = self._determine_staff_tier(tier)
                
                # Create staff member
                staff = StaffMember(
                    id=0,  # Auto-incremented by database
                    name=full_staff_name,
                    nationality=nationality,
                    birth_date=self._generate_birth_date(random.randint(25, 65)),
                    age=random.randint(25, 65),
                    current_team_id=team_id,
                    role=role_name,
                    tier=staff_tier,
                    # Core attributes
                    technical_expertise=random.uniform(40.0, 95.0),
                    experience_years=random.randint(2, 30),
                    management_skill=random.uniform(30.0, 90.0),
                    innovation_ability=random.uniform(30.0, 95.0),
                    communication=random.uniform(40.0, 90.0),
                    work_under_pressure=random.uniform(50.0, 95.0)
                    # Note: Other attributes use default values from dataclass
                )
                
                # Save to database
                try:
                    staff_id = self.db.create_staff_member(staff)
                    self.stats['staff_created'] += 1
                    staff_members.append(staff)
                except Exception as e:
                    error_msg = f"Error creating staff member (role: {role_name}): {str(e)}"
                    logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
        
        return staff_members
    
    def _generate_birth_date(self, age: int) -> str:
        """Generate a birth date for a given age"""
        today = datetime.now()
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Simplified to avoid invalid dates
        return f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    def _calculate_team_budget(self, tier: int) -> float:
        """Calculate team budget based on tier"""
        budget_ranges = {
            1: (8_000_000, 12_000_000),   # Tier 1: €8M - €12M
            2: (5_000_000, 8_000_000),    # Tier 2: €5M - €8M
            3: (3_000_000, 5_000_000),    # Tier 3: €3M - €5M
            4: (1_500_000, 3_000_000),    # Tier 4: €1.5M - €3M
            5: (800_000, 1_500_000),      # Tier 5: €800K - €1.5M
            6: (400_000, 800_000),        # Tier 6: €400K - €800K
        }
        
        min_budget, max_budget = budget_ranges.get(tier, (500_000, 1_000_000))
        return random.uniform(min_budget, max_budget)
    
    def _determine_staff_tier(self, team_tier: int) -> str:
        """Determine staff tier based on team tier"""
        # Staff tiers align with team tiers
        # Higher tier teams (1-2) get mostly tier1-tier2 staff
        # Lower tier teams (5-6) get mostly tier4-tier6 staff
        tier_mapping = {
            1: ["tier1", "tier1", "tier2"],  # Weighted towards tier1
            2: ["tier1", "tier2", "tier2"],  # Mix of tier1 and tier2
            3: ["tier2", "tier3", "tier3"],  # Mix of tier2 and tier3
            4: ["tier3", "tier4", "tier4"],  # Mix of tier3 and tier4
            5: ["tier4", "tier5", "tier5"],  # Mix of tier4 and tier5
            6: ["tier5", "tier6", "tier6"]   # Mix of tier5 and tier6
        }
        
        available_tiers = tier_mapping.get(team_tier, ["tier4", "tier5"])
        return random.choice(available_tiers)
    
    def _calculate_staff_salary(self, staff_tier: str, role: str, team_budget: float) -> float:
        """Calculate staff salary based on tier and role"""
        # Base salaries by tier
        base_salaries = {
            "WORLD_CLASS": 250_000,
            "ELITE": 180_000,
            "SENIOR": 120_000,
            "EXPERIENCED": 80_000,
            "INTERMEDIATE": 50_000,
            "JUNIOR": 30_000,
            "INTERN": 18_000
        }
        
        # Role multipliers
        role_multipliers = {
            "Team Principal": 2.0,
            "Technical Director": 1.8,
            "Chief Engineer": 1.6,
            "Race Engineer": 1.4,
            "Data Analyst": 1.3,
            "Race Strategist": 1.5,
        }
        
        base_salary = base_salaries.get(staff_tier, 50_000)
        role_multiplier = role_multipliers.get(role, 1.0)
        
        # Add some randomness
        salary = base_salary * role_multiplier * random.uniform(0.9, 1.1)
        
        # Cap at reasonable percentage of team budget
        max_salary = team_budget * 0.05  # No single staff member makes more than 5% of budget
        return min(salary, max_salary)
    
    def _get_weighted_nationalities(self) -> Dict[str, float]:
        """Get nationality distribution weighted by motorsport heritage"""
        # Major motorsport nations get higher weights
        major_nations = {
            "GBR": 0.12, "USA": 0.10, "GER": 0.09, "ITA": 0.08,
            "FRA": 0.07, "ESP": 0.06, "BRA": 0.05, "JPN": 0.04,
            "AUS": 0.04, "NLD": 0.03, "BEL": 0.03, "FIN": 0.03,
            "SWE": 0.02, "CAN": 0.02, "MEX": 0.02, "AUT": 0.02,
        }
        
        # Remaining countries share the rest
        other_countries = [c for c in COUNTRIES.keys() if c not in major_nations]
        remaining_weight = 1.0 - sum(major_nations.values())
        weight_per_other = remaining_weight / len(other_countries)
        
        all_weights = {**major_nations}
        for country in other_countries:
            all_weights[country] = weight_per_other
        
        return all_weights
    
    def _generate_report(self):
        """Generate a comprehensive generation report"""
        report_path = "database_generation_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MOMENTUM MOTORSPORT SIMULATION - DATABASE GENERATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {self.db_path}\n\n")
            
            f.write("GENERATION SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Teams Created:   {self.stats['teams_created']:>8,}\n")
            f.write(f"Drivers Created: {self.stats['drivers_created']:>8,}\n")
            f.write(f"Staff Created:   {self.stats['staff_created']:>8,}\n")
            f.write(f"Total Personnel: {self.stats['drivers_created'] + self.stats['staff_created']:>8,}\n\n")
            
            if self.stats['errors']:
                f.write("ERRORS ENCOUNTERED\n")
                f.write("-" * 40 + "\n")
                for error in self.stats['errors']:
                    f.write(f"  • {error}\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        logger.info(f"\n[REPORT] Generation report saved to: {report_path}")


def main():
    """Main entry point for database generation"""
    print("\n" + "=" * 80)
    print("MOMENTUM MOTORSPORT SIMULATION")
    print("Initial Database Generation Script")
    print("=" * 80 + "\n")
    
    # Confirm before proceeding
    # response = input("This will generate a complete database with ~10,000+ entities.\nContinue? (yes/no): ")
    # if response.lower() not in ['yes', 'y']:
    #     print("❌ Generation cancelled.")
    #     return
    
    print("Generating database with ~10,000+ entities...")
    
    # Create generator and run
    generator = DatabaseGenerator()
    
    try:
        generator.generate_complete_database()
        print("\n[SUCCESS] Database generation completed successfully!")
        print("   Check 'database_generation_report.txt' for details.")
        
    except Exception as e:
        logger.error(f"[ERROR] Fatal error during generation: {str(e)}", exc_info=True)
        print(f"\n[ERROR] Generation failed: {str(e)}")
        print("   Check 'database_generation.log' for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
