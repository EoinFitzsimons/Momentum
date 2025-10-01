"""
Staff Example Profiles - Comprehensive Multi-Role Team Personnel Examples

This module demonstrates the staff system with realistic examples across
different roles, tiers, and specializations. Shows how different staff
configurations affect team capabilities and information access.

Examples include:
- Technical Director (Adrian Newey style)
- Data Analytics Specialist (McLaren Applied style)
- Veteran Race Strategist (Ross Brawn style) 
- Pit Crew Chief (Red Bull style)
- Chief Designer (Gordon Murray style)
- Budget Team vs Premium Team comparisons

Authors: Final Year Project - Computer Science
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Momentum.Python.database.models.staff_models import StaffMember, StaffRole, StaffTier, TeamStaffing
from systems.staff_management import StaffManagementSystem


def create_technical_director_legend() -> StaffMember:
    """
    Create legendary technical director (Adrian Newey style)
    
    Profile: Exceptional aerodynamics expertise with innovative design
    approach and strong technical leadership. Transforms car performance.
    """
    return StaffMember(
        id=1,
        name="Adrian Richardson",
        nationality="GBR",
        birth_date="1959-12-26",
        age=64,
        role=StaffRole.TECHNICAL_DIRECTOR,
        tier=StaffTier.LEGENDARY,
        
        # ===== TECHNICAL SKILLS =====
        engineering_knowledge=98.0,           # Exceptional engineering depth
        aerodynamics_expertise=100.0,        # Legendary aerodynamics mastery
        engine_knowledge=75.0,               # Good but not primary focus
        suspension_expertise=88.0,           # Strong chassis understanding
        electronics_knowledge=65.0,          # Adequate electronics knowledge
        materials_science=85.0,              # Strong materials expertise
        cfd_analysis=70.0,                   # Prefers old-school methods
        cad_design=60.0,                     # Traditional design approach
        simulation_expertise=65.0,           # Prefers real-world testing
        manufacturing_knowledge=80.0,        # Good production understanding
        quality_control=90.0,                # Obsessive about quality
        innovation_ability=100.0,            # Revolutionary design thinking
        
        # ===== ANALYTICAL SKILLS =====
        data_analysis=75.0,                  # Good analytical capability
        telemetry_analysis=70.0,             # Decent telemetry reading
        performance_modeling=85.0,           # Strong performance prediction
        statistical_methods=60.0,            # Basic statistical knowledge
        pattern_recognition=95.0,            # Exceptional pattern recognition
        predictive_analytics=80.0,           # Good predictive ability
        software_proficiency=55.0,           # Limited software skills
        database_management=45.0,            # Basic database usage
        
        # ===== MANAGEMENT & LEADERSHIP =====
        leadership_ability=88.0,             # Strong technical leadership
        team_coordination=75.0,              # Good team management
        project_management=80.0,             # Solid project oversight
        resource_allocation=85.0,            # Efficient resource use
        conflict_resolution=65.0,            # Sometimes causes conflicts
        decision_making=95.0,                # Decisive technical decisions
        mentoring_ability=90.0,              # Develops young engineers
        
        # ===== OPERATIONAL SKILLS =====
        pit_stop_efficiency=40.0,            # Not operational focus
        race_strategy=70.0,                  # Good strategic understanding
        crisis_management=85.0,              # Handles pressure well
        equipment_maintenance=70.0,          # Good equipment knowledge
        logistics_coordination=50.0,         # Limited logistics involvement
        safety_protocols=95.0,               # Obsessive about safety
        communication_skills=75.0,           # Clear technical communication
        adaptability=60.0,                   # Set in proven methods
        
        # ===== FINANCIAL & COMMERCIAL =====
        financial_management=40.0,           # Not commercial focus
        commercial_acumen=35.0,              # Limited commercial interest
        negotiation_skills=50.0,             # Basic negotiation
        sponsorship_development=25.0,        # No commercial involvement
        cost_optimization=85.0,              # Efficient technical spending
        
        # ===== DISCIPLINE SPECIALIZATIONS =====
        single_seater_expertise=100.0,       # Legendary F1 expertise
        touring_car_expertise=70.0,          # Good crossover potential
        rally_expertise=45.0,                # Limited rally experience
        street_racing_expertise=30.0,        # Not street racing focused
        drag_racing_expertise=35.0,          # Basic drag racing knowledge
        rallycross_expertise=55.0,           # Some crossover potential
        endurance_expertise=80.0,            # Strong endurance car design
        
        # Career details
        years_experience=42,
        education_level="master",
        certifications="Chartered Engineer, RAeS Fellow",
        languages_spoken=2,
        salary=1500000.0,
        contract_length=3,
        job_satisfaction=95.0,
        performance_rating=98.0,
        innovation_projects=25,
        patents_held=15
    )


def create_data_analytics_specialist() -> StaffMember:
    """
    Create expert data analyst (McLaren Applied Technologies style)
    
    Profile: Cutting-edge data science expertise with advanced statistical
    methods and machine learning. Provides competitive advantage through data.
    """
    return StaffMember(
        id=2,
        name="Dr. Sarah Chen",
        nationality="USA",
        birth_date="1988-07-15",
        age=35,
        role=StaffRole.PERFORMANCE_ANALYST,
        tier=StaffTier.EXPERT,
        
        # ===== TECHNICAL SKILLS =====
        engineering_knowledge=75.0,          # Solid engineering background
        aerodynamics_expertise=60.0,         # Basic aero understanding
        engine_knowledge=65.0,               # Good engine data knowledge
        suspension_expertise=55.0,           # Basic suspension knowledge
        electronics_knowledge=85.0,          # Strong electronics/sensors
        materials_science=50.0,              # Limited materials focus
        cfd_analysis=80.0,                   # Good CFD data analysis
        cad_design=40.0,                     # Limited design skills
        simulation_expertise=90.0,           # Exceptional simulation work
        manufacturing_knowledge=45.0,        # Basic manufacturing knowledge
        quality_control=85.0,                # Strong QC methodologies
        innovation_ability=88.0,             # Innovative analytical methods
        
        # ===== ANALYTICAL SKILLS =====
        data_analysis=98.0,                  # World-class data analysis
        telemetry_analysis=95.0,             # Exceptional telemetry skills
        performance_modeling=92.0,           # Advanced performance models
        statistical_methods=96.0,            # PhD-level statistics
        pattern_recognition=94.0,            # Machine learning expertise
        predictive_analytics=95.0,           # Cutting-edge predictions
        software_proficiency=95.0,           # Expert programmer
        database_management=90.0,            # Database architecture expert
        
        # ===== MANAGEMENT & LEADERSHIP =====
        leadership_ability=65.0,             # Growing leadership skills
        team_coordination=70.0,              # Good team collaboration
        project_management=75.0,             # Solid project skills
        resource_allocation=60.0,            # Learning resource management
        conflict_resolution=55.0,            # Basic conflict handling
        decision_making=80.0,                # Data-driven decisions
        mentoring_ability=75.0,              # Mentors junior analysts
        
        # ===== OPERATIONAL SKILLS =====
        pit_stop_efficiency=30.0,            # Not operational focus
        race_strategy=85.0,                  # Strong strategic analysis
        crisis_management=70.0,              # Good under pressure
        equipment_maintenance=60.0,          # Basic equipment knowledge
        logistics_coordination=40.0,         # Limited logistics involvement
        safety_protocols=80.0,               # Strong safety awareness
        communication_skills=88.0,           # Excellent presentation skills
        adaptability=90.0,                   # Highly adaptable
        
        # ===== FINANCIAL & COMMERCIAL =====
        financial_management=50.0,           # Basic financial understanding
        commercial_acumen=45.0,              # Limited commercial focus
        negotiation_skills=55.0,             # Basic negotiation skills
        sponsorship_development=30.0,        # No commercial involvement
        cost_optimization=75.0,              # Efficient analytics spending
        
        # ===== DISCIPLINE SPECIALIZATIONS =====
        single_seater_expertise=85.0,        # Strong F1 analytics
        touring_car_expertise=75.0,          # Good touring car analysis
        rally_expertise=60.0,                # Some rally data experience
        street_racing_expertise=55.0,        # Basic street racing analysis
        drag_racing_expertise=70.0,          # Good drag racing analytics
        rallycross_expertise=65.0,           # Some rallycross experience
        endurance_expertise=80.0,            # Strong endurance analytics
        
        # Career details
        years_experience=12,
        education_level="phd",
        certifications="Data Science Professional, Six Sigma Black Belt",
        languages_spoken=3,
        salary=180000.0,
        contract_length=2,
        job_satisfaction=92.0,
        performance_rating=94.0,
        innovation_projects=15,
        patents_held=3,
        publications=12
    )


def create_veteran_strategist() -> StaffMember:
    """
    Create senior race strategist (Ross Brawn style)
    
    Profile: Decades of strategic experience with exceptional race craft
    and crisis management. Wins races through superior strategy.
    """
    return StaffMember(
        id=3,
        name="Roberto Stefanini",
        nationality="ITA",
        birth_date="1954-11-23",
        age=69,
        role=StaffRole.RACE_STRATEGIST,
        tier=StaffTier.EXPERT,
        
        # ===== TECHNICAL SKILLS =====
        engineering_knowledge=85.0,          # Strong engineering background
        aerodynamics_expertise=70.0,         # Good aero understanding
        engine_knowledge=80.0,               # Strong engine knowledge
        suspension_expertise=75.0,           # Good chassis knowledge
        electronics_knowledge=60.0,          # Basic electronics
        materials_science=65.0,              # Decent materials knowledge
        cfd_analysis=45.0,                   # Old-school approach
        cad_design=40.0,                     # Limited design skills
        simulation_expertise=55.0,           # Prefers real experience
        manufacturing_knowledge=85.0,        # Strong manufacturing knowledge
        quality_control=90.0,                # Obsessive about details
        innovation_ability=75.0,             # Creative strategic thinking
        
        # ===== ANALYTICAL SKILLS =====
        data_analysis=80.0,                  # Strong analytical skills
        telemetry_analysis=85.0,             # Excellent telemetry reading
        performance_modeling=78.0,           # Good performance models
        statistical_methods=70.0,            # Solid statistical knowledge
        pattern_recognition=95.0,            # Exceptional pattern recognition
        predictive_analytics=90.0,           # Masterful predictions
        software_proficiency=50.0,           # Basic software skills
        database_management=40.0,            # Limited database work
        
        # ===== MANAGEMENT & LEADERSHIP =====
        leadership_ability=95.0,             # Legendary leadership
        team_coordination=92.0,              # Exceptional team management
        project_management=88.0,             # Strong project oversight
        resource_allocation=90.0,            # Masterful resource use
        conflict_resolution=88.0,            # Excellent at resolving conflicts
        decision_making=98.0,                # Legendary decision making
        mentoring_ability=95.0,              # Develops future leaders
        
        # ===== OPERATIONAL SKILLS =====
        pit_stop_efficiency=85.0,            # Coordinates pit strategy
        race_strategy=100.0,                 # Legendary strategic ability
        crisis_management=98.0,              # Masterful under pressure
        equipment_maintenance=75.0,          # Good equipment knowledge
        logistics_coordination=80.0,         # Strong logistics oversight
        safety_protocols=95.0,               # Safety-first approach
        communication_skills=92.0,           # Clear communication
        adaptability=85.0,                   # Adapts strategies quickly
        
        # ===== FINANCIAL & COMMERCIAL =====
        financial_management=75.0,           # Good budget management
        commercial_acumen=70.0,              # Understands business side
        negotiation_skills=85.0,             # Strong negotiation skills
        sponsorship_development=60.0,        # Some commercial involvement
        cost_optimization=90.0,              # Extremely efficient spending
        
        # ===== DISCIPLINE SPECIALIZATIONS =====
        single_seater_expertise=100.0,       # Legendary F1 strategy
        touring_car_expertise=85.0,          # Strong touring car strategy
        rally_expertise=70.0,                # Good rally strategy
        street_racing_expertise=65.0,        # Some street racing experience
        drag_racing_expertise=55.0,          # Basic drag racing strategy
        rallycross_expertise=75.0,           # Good rallycross strategy
        endurance_expertise=95.0,            # Masterful endurance strategy
        
        # Career details
        years_experience=47,
        education_level="bachelor",
        certifications="Honorary Fellowship, Motorsport Industry Association",
        languages_spoken=4,
        salary=600000.0,
        contract_length=1,
        job_satisfaction=88.0,
        performance_rating=96.0,
        innovation_projects=8,
        patents_held=3  # Strategic innovations
    )


def create_pit_crew_chief() -> StaffMember:
    """
    Create expert pit crew chief (Red Bull Racing style)
    
    Profile: Lightning-fast pit stops with exceptional team coordination
    and crisis management. Wins races through operational excellence.
    """
    return StaffMember(
        id=4,
        name="Klaus Weber",
        nationality="GER",
        birth_date="1980-05-10", 
        age=43,
        role=StaffRole.PIT_CREW_CHIEF,
        tier=StaffTier.EXPERT,
        
        # ===== TECHNICAL SKILLS =====
        engineering_knowledge=65.0,          # Good technical background
        aerodynamics_expertise=45.0,         # Basic aero knowledge
        engine_knowledge=70.0,               # Good engine knowledge
        suspension_expertise=75.0,           # Strong chassis knowledge
        electronics_knowledge=80.0,          # Good electronics for tools
        materials_science=60.0,              # Basic materials knowledge
        cfd_analysis=25.0,                   # Not analysis focused
        cad_design=30.0,                     # Limited design work
        simulation_expertise=35.0,           # Basic simulation knowledge
        manufacturing_knowledge=85.0,        # Strong manufacturing skills
        quality_control=95.0,                # Obsessive about precision
        innovation_ability=75.0,             # Creative operational solutions
        
        # ===== ANALYTICAL SKILLS =====
        data_analysis=60.0,                  # Basic data analysis
        telemetry_analysis=70.0,             # Good telemetry for pit stops
        performance_modeling=40.0,           # Limited modeling work
        statistical_methods=45.0,            # Basic statistics
        pattern_recognition=80.0,            # Good at spotting patterns
        predictive_analytics=55.0,           # Some predictive ability
        software_proficiency=60.0,           # Basic software skills
        database_management=40.0,            # Limited database work
        
        # ===== MANAGEMENT & LEADERSHIP =====
        leadership_ability=92.0,             # Exceptional pit leadership
        team_coordination=98.0,              # Masterful team coordination
        project_management=80.0,             # Good project skills
        resource_allocation=85.0,            # Efficient resource use
        conflict_resolution=85.0,            # Good at resolving conflicts
        decision_making=90.0,                # Quick decisive decisions
        mentoring_ability=88.0,              # Develops pit crew members
        
        # ===== OPERATIONAL SKILLS =====
        pit_stop_efficiency=100.0,           # World-record pit stops
        race_strategy=75.0,                  # Good strategic input
        crisis_management=95.0,              # Exceptional under pressure
        equipment_maintenance=95.0,          # Masterful equipment care
        logistics_coordination=90.0,         # Excellent logistics
        safety_protocols=98.0,               # Safety-first approach
        communication_skills=90.0,           # Clear, concise communication
        adaptability=88.0,                   # Adapts to changing conditions
        
        # ===== FINANCIAL & COMMERCIAL =====
        financial_management=50.0,           # Basic budget awareness
        commercial_acumen=35.0,              # Limited commercial focus
        negotiation_skills=60.0,             # Basic negotiation
        sponsorship_development=25.0,        # No commercial involvement
        cost_optimization=80.0,              # Efficient equipment spending
        
        # ===== DISCIPLINE SPECIALIZATIONS =====
        single_seater_expertise=95.0,        # Expert F1 pit stops
        touring_car_expertise=85.0,          # Strong touring car ops
        rally_expertise=60.0,                # Some rally service experience
        street_racing_expertise=70.0,        # Good street racing ops
        drag_racing_expertise=80.0,          # Strong drag racing ops
        rallycross_expertise=75.0,           # Good rallycross ops
        endurance_expertise=90.0,            # Excellent endurance ops
        
        # Career details
        years_experience=21,
        education_level="apprenticeship",
        certifications="Advanced Motorsport Operations, Safety Marshal",
        languages_spoken=3,
        salary=120000.0,
        contract_length=2,
        job_satisfaction=94.0,
        performance_rating=96.0,
        innovation_projects=4  # Pit stop innovations
    )


def create_budget_team_configuration(team_id: int) -> TeamStaffing:
    """
    Create realistic budget team staff configuration
    
    Profile: Small budget team with minimal staff but passionate
    individuals wearing multiple hats. Limited data access but scrappy.
    """
    budget_team = TeamStaffing(
        team_id=team_id,
        discipline="touring_car",
        total_budget=800000.0,
        personnel_budget=240000.0  # 30% of budget for staff
    )
    
    # Minimal staff roster
    budget_team.staff_members = [
        # Team owner/manager wearing multiple hats
        StaffMember(
            id=101, name="Mike Johnson", nationality="USA", age=45,
            birth_date="1978-03-15", role=StaffRole.TEAM_MANAGER, tier=StaffTier.REGULAR,
            engineering_knowledge=60.0, leadership_ability=75.0, financial_management=70.0,
            years_experience=15, salary=45000.0
        ),
        
        # Chief mechanic/engineer
        StaffMember(
            id=102, name="Carlos Rodriguez", nationality="ESP", age=38,
            birth_date="1985-08-22", role=StaffRole.CHIEF_ENGINEER, tier=StaffTier.SENIOR,
            engineering_knowledge=80.0, equipment_maintenance=85.0, innovation_ability=65.0,
            years_experience=18, salary=65000.0
        ),
        
        # Junior mechanics (2)
        StaffMember(
            id=103, name="Tommy Anderson", nationality="GBR", age=26,
            birth_date="1997-06-08", role=StaffRole.MECHANIC, tier=StaffTier.JUNIOR,
            equipment_maintenance=70.0, pit_stop_efficiency=60.0,
            years_experience=4, salary=35000.0
        ),
        
        StaffMember(
            id=104, name="Jake Wilson", nationality="AUS", age=24,
            birth_date="1999-11-30", role=StaffRole.MECHANIC, tier=StaffTier.JUNIOR,
            equipment_maintenance=65.0, pit_stop_efficiency=65.0,
            years_experience=2, salary=32000.0
        ),
        
        # Part-time data person
        StaffMember(
            id=105, name="Lisa Chen", nationality="CAN", age=29,
            birth_date="1994-02-14", role=StaffRole.DATA_ANALYST, tier=StaffTier.REGULAR,
            data_analysis=70.0, telemetry_analysis=65.0, software_proficiency=75.0,
            years_experience=6, salary=42000.0, contract_type="part_time"
        )
    ]
    
    return budget_team


def create_premium_team_configuration(team_id: int) -> TeamStaffing:
    """
    Create realistic premium team staff configuration
    
    Profile: Well-funded professional team with comprehensive staff
    across all areas. Extensive data capabilities and operational excellence.
    """
    premium_team = TeamStaffing(
        team_id=team_id,
        discipline="single_seater", 
        total_budget=12000000.0,
        personnel_budget=4200000.0  # 35% of budget for staff
    )
    
    # Comprehensive staff roster
    premium_team.staff_members = [
        # Leadership team
        create_technical_director_legend(),  # Adrian Richardson
        
        StaffMember(
            id=201, name="Jonathan Mills", nationality="GBR", age=52,
            birth_date="1971-04-18", role=StaffRole.TEAM_PRINCIPAL, tier=StaffTier.EXPERT,
            leadership_ability=90.0, financial_management=85.0, commercial_acumen=88.0,
            negotiation_skills=92.0, years_experience=28, salary=800000.0
        ),
        
        # Technical team
        StaffMember(
            id=202, name="Dr. Elena Volkov", nationality="RUS", age=41,
            birth_date="1982-09-12", role=StaffRole.CHIEF_DESIGNER, tier=StaffTier.EXPERT,
            cad_design=92.0, aerodynamics_expertise=88.0, innovation_ability=85.0,
            years_experience=19, salary=400000.0
        ),
        
        StaffMember(
            id=203, name="Hans Mueller", nationality="GER", age=46,
            birth_date="1977-01-25", role=StaffRole.AERODYNAMICS_ENGINEER, tier=StaffTier.EXPERT,
            aerodynamics_expertise=94.0, cfd_analysis=90.0, engineering_knowledge=85.0,
            years_experience=22, salary=280000.0
        ),
        
        # Analytics team
        create_data_analytics_specialist(),  # Dr. Sarah Chen
        
        StaffMember(
            id=204, name="Raj Patel", nationality="IND", age=33,
            birth_date="1990-07-03", role=StaffRole.TELEMETRY_SPECIALIST, tier=StaffTier.SENIOR,
            telemetry_analysis=88.0, data_analysis=82.0, software_proficiency=90.0,
            years_experience=11, salary=140000.0
        ),
        
        # Strategy team
        create_veteran_strategist(),  # Roberto Stefanini
        
        StaffMember(
            id=205, name="Michelle Dubois", nationality="FRA", age=36,
            birth_date="1987-10-19", role=StaffRole.RACE_STRATEGIST, tier=StaffTier.SENIOR,
            race_strategy=85.0, data_analysis=78.0, decision_making=82.0,
            years_experience=14, salary=180000.0
        ),
        
        # Operations team
        create_pit_crew_chief(),  # Klaus Weber
        
        # Multiple mechanics and pit crew members would be added...
        # (Abbreviated for brevity)
    ]
    
    return premium_team


def demonstrate_staff_system_capabilities():
    """Demonstrate comprehensive staff system functionality"""
    
    print("COMPREHENSIVE STAFF SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Create staff management system
    staff_system = StaffManagementSystem()
    
    # Create team configurations
    budget_team = create_budget_team_configuration(1)
    premium_team = create_premium_team_configuration(2)
    
    teams = [
        ("Budget Team", budget_team),
        ("Premium Team", premium_team)
    ]
    
    for team_name, team in teams:
        print(f"\n{team_name.upper()} ANALYSIS")
        print("=" * 40)
        
        # Basic team info
        print(f"Total Budget: ${team.total_budget:,.0f}")
        print(f"Personnel Budget: ${team.personnel_budget:,.0f}")
        print(f"Staff Count: {len(team.staff_members)}")
        print(f"Annual Staff Costs: ${team.calculate_staff_costs():,.0f}")
        
        # Performance multipliers
        multipliers = staff_system.calculate_team_performance_multipliers(team)
        print(f"\nPerformance Multipliers:")
        for area, multiplier in multipliers.items():
            print(f"  {area.replace('_', ' ').title()}: {multiplier:.2f}x")
            
        # Information access (fog of war)
        data_access = staff_system.get_data_visibility_level(team)
        print(f"\nInformation Access Level: {data_access['overall_access_level']:.1f}/100")
        
        visibility = data_access['visibility_flags']
        print("Data Visibility:")
        for data_type, accessible in visibility.items():
            status = "✓" if accessible else "✗"
            print(f"  {status} {data_type.replace('_', ' ').title()}")
            
        # Staff expertise by discipline
        print(f"\nDiscipline Expertise Levels:")
        disciplines = ["single_seater", "touring_car", "rally", "endurance"]
        for discipline in disciplines:
            expertise = team.get_discipline_expertise_level(discipline)
            print(f"  {discipline.replace('_', ' ').title()}: {expertise:.1f}/100")
            
        # Missing critical roles
        missing_roles = team.get_missing_critical_roles()
        if missing_roles:
            print(f"\nMissing Critical Roles:")
            for role in missing_roles:
                print(f"  - {role.value}")
        else:
            print(f"\n✓ All critical roles filled")
    
    # Compare team capabilities
    print(f"\n" + "=" * 60)
    print("TEAM COMPARISON SUMMARY")
    print("=" * 60)
    
    budget_access = budget_team.calculate_information_access_level()
    premium_access = premium_team.calculate_information_access_level()
    
    print(f"Information Access Advantage: Premium team has {premium_access - budget_access:.1f} point advantage")
    
    budget_multipliers = staff_system.calculate_team_performance_multipliers(budget_team)
    premium_multipliers = staff_system.calculate_team_performance_multipliers(premium_team)
    
    print(f"\nPerformance Advantages:")
    for area in budget_multipliers.keys():
        advantage = premium_multipliers[area] - budget_multipliers[area]
        print(f"  {area.replace('_', ' ').title()}: +{advantage:.2f}x advantage")
        
    print(f"\n💰 Budget Reality: Premium team spends {premium_team.calculate_staff_costs()/budget_team.calculate_staff_costs():.1f}x more on staff")
    print(f"🏆 Performance Reality: Premium team has significant operational advantages")
    print(f"📊 Information Reality: Premium team sees much more detailed data and analytics")


if __name__ == "__main__":
    demonstrate_staff_system_capabilities()