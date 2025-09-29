"""
Driver Generation Examples - Comprehensive Multi-Discipline Driver System

This module demonstrates how to create drivers with the new 50+ attribute system
and shows how different driver profiles excel in different racing disciplines.

Examples include:
- Formula Racing Specialist (Hamilton-style)
- Touring Car Battler (Plato-style)
- Rally Legend (Loeb-style)
- Street Racing Maverick (Block-style)
- Drag Racing Specialist (Force-style)
- Rallycross All-Rounder (Hansen-style)
- Endurance Marathon Master (Kristensen-style)

Each example shows realistic attribute distributions and how the same driver
can compete across disciplines with varying levels of success.

Authors: Final Year Project - Computer Science
"""

from database.models import Driver


def create_formula_specialist() -> Driver:
    """
    Create a Formula 1 specialist driver (Lewis Hamilton style)
    
    Profile: Exceptional single-seater talent with strong technical knowledge
    and championship mentality. Good at wet weather and under pressure.
    """
    return Driver(
        id=1,
        name="Alessandro Rossi",
        nationality="ITA",
        birth_date="1985-01-15",
        age=29,
        
        # ===== CORE DRIVING SKILLS =====
        raw_speed=95.0,                    # Exceptional natural pace
        consistency=88.0,                  # Very consistent performer
        racecraft=90.0,                    # Excellent wheel-to-wheel racing
        overtaking=85.0,                   # Strong overtaking ability
        defensive_driving=82.0,            # Good at defending position
        cornering_skill=94.0,              # Exceptional cornering technique
        braking_technique=91.0,            # Late braking specialist
        acceleration_control=87.0,         # Good launch technique
        spatial_awareness=89.0,            # Excellent positioning sense
        vehicle_control=92.0,              # Exceptional car control
        
        # ===== PHYSICAL & MENTAL TRAITS =====
        physical_fitness=90.0,             # Peak physical condition
        reaction_time=88.0,                # Quick reflexes
        concentration=93.0,                # Exceptional focus
        pressure_handling=91.0,            # Thrives under pressure
        pain_tolerance=85.0,               # Good endurance
        g_force_tolerance=95.0,            # Exceptional G-force handling
        coordination=90.0,                 # Excellent coordination
        multitasking=87.0,                 # Good at multiple tasks
        mental_resilience=89.0,            # Bounces back from setbacks
        adrenaline_management=88.0,        # Controls excitement well
        
        # ===== TECHNICAL KNOWLEDGE =====
        setup_knowledge=92.0,              # Excellent setup understanding
        mechanical_sympathy=85.0,          # Good mechanical preservation
        tire_management=89.0,              # Strategic tire usage
        fuel_management=87.0,              # Good fuel strategy
        aerodynamics_understanding=94.0,   # Deep aero knowledge
        suspension_feel=88.0,              # Good chassis feedback
        engine_management=86.0,            # Good power delivery control
        data_analysis=90.0,                # Strong telemetry interpretation
        
        # ===== DISCIPLINE SPECIALIZATIONS =====
        single_seater_aptitude=96.0,       # Natural Formula 1 talent
        touring_car_aptitude=65.0,         # Could adapt to touring cars
        rally_aptitude=45.0,               # Limited off-road experience
        street_racing_aptitude=35.0,       # Not suited to street racing
        drag_racing_aptitude=40.0,         # Limited straight-line focus
        rallycross_aptitude=55.0,          # Some crossover potential
        endurance_aptitude=78.0,           # Good stamina for long races
        
        # ===== RACE CRAFT & STRATEGY =====
        race_strategy=91.0,                # Excellent strategic thinking
        pit_stop_coordination=88.0,        # Works well with crew
        traffic_management=86.0,           # Good at navigating traffic
        tire_strategy=89.0,                # Strategic tire management
        fuel_strategy=87.0,                # Good fuel planning
        safety_car_awareness=85.0,         # Capitalizes on opportunities
        qualifying_optimization=94.0,      # Exceptional qualifying pace
        championship_thinking=92.0,        # Strong championship mentality
        
        # ===== ENVIRONMENTAL ADAPTATION =====
        wet_weather_skill=93.0,            # Exceptional in wet conditions
        night_racing_skill=75.0,           # Decent night racing
        temperature_adaptation=82.0,       # Adapts to temperature changes
        altitude_adaptation=78.0,          # Good at high altitude
        surface_adaptation=70.0,           # Limited to tarmac experience
        car_adaptation=88.0,               # Quickly adapts to new cars
        track_learning=90.0,               # Fast at learning circuits
        
        # ===== PERSONAL & SOCIAL TRAITS =====
        media_presence=89.0,               # Strong media personality
        team_cooperation=87.0,             # Good team player
        leadership_ability=85.0,           # Natural leadership
        risk_appetite=75.0,                # Calculated risk-taker
        ego_management=82.0,               # Handles success well
        commercial_appeal=91.0,            # High marketability
        
        # Career stats
        career_wins=15,
        career_podiums=45,
        single_seater_wins=15,
        preferred_discipline="single_seater",
        career_phase="peak"
    )


def create_touring_car_battler() -> Driver:
    """
    Create a touring car specialist (Jason Plato style)
    
    Profile: Aggressive door-to-door racer with exceptional racecraft
    and contact racing skills. Thrives in close competition.
    """
    return Driver(
        id=2,
        name="Marcus Thompson",
        nationality="GBR",
        birth_date="1975-03-22",
        age=39,
        
        # ===== CORE DRIVING SKILLS =====
        raw_speed=82.0,                    # Good but not exceptional pace
        consistency=85.0,                  # Very consistent in races
        racecraft=94.0,                    # Exceptional wheel-to-wheel skill
        overtaking=92.0,                   # Master of overtaking in traffic
        defensive_driving=96.0,            # Legendary defensive driving
        cornering_skill=80.0,              # Good cornering technique
        braking_technique=85.0,            # Strong late braking
        acceleration_control=78.0,         # Decent launch technique
        spatial_awareness=93.0,            # Exceptional race awareness
        vehicle_control=87.0,              # Strong car control in contact
        
        # ===== PHYSICAL & MENTAL TRAITS =====
        physical_fitness=88.0,             # Excellent fitness for age
        reaction_time=91.0,                # Lightning quick reactions
        concentration=89.0,                # Strong focus in battles
        pressure_handling=94.0,            # Thrives under pressure
        pain_tolerance=92.0,               # High pain tolerance
        g_force_tolerance=75.0,            # Decent G-force handling
        coordination=88.0,                 # Good coordination
        multitasking=94.0,                 # Excellent at managing battles
        mental_resilience=95.0,            # Never gives up
        adrenaline_management=90.0,        # Uses adrenaline effectively
        
        # ===== TECHNICAL KNOWLEDGE =====
        setup_knowledge=88.0,              # Strong setup knowledge
        mechanical_sympathy=91.0,          # Preserves car in contact
        tire_management=86.0,              # Good tire preservation
        fuel_management=82.0,              # Decent fuel strategy
        aerodynamics_understanding=65.0,   # Limited aero knowledge
        suspension_feel=89.0,              # Excellent chassis feel
        engine_management=80.0,            # Good power management
        data_analysis=75.0,                # Basic data interpretation
        
        # ===== DISCIPLINE SPECIALIZATIONS =====
        single_seater_aptitude=55.0,       # Could drive single seaters
        touring_car_aptitude=97.0,         # Master of touring cars
        rally_aptitude=70.0,               # Good crossover potential
        street_racing_aptitude=85.0,       # Strong street racing ability
        drag_racing_aptitude=50.0,         # Limited drag racing
        rallycross_aptitude=82.0,          # Excellent rallycross potential
        endurance_aptitude=75.0,           # Good endurance capability
        
        # ===== RACE CRAFT & STRATEGY =====
        race_strategy=87.0,                # Good strategic thinking
        pit_stop_coordination=85.0,        # Works well with crew
        traffic_management=96.0,           # Master of traffic navigation
        tire_strategy=84.0,                # Good tire management
        fuel_strategy=80.0,                # Decent fuel planning
        safety_car_awareness=92.0,         # Capitalizes on opportunities
        qualifying_optimization=75.0,      # Focus more on race than quali
        championship_thinking=89.0,        # Strong championship approach
        
        # ===== ENVIRONMENTAL ADAPTATION =====
        wet_weather_skill=88.0,            # Strong in wet conditions
        night_racing_skill=85.0,           # Good night racing
        temperature_adaptation=90.0,       # Adapts well to conditions
        altitude_adaptation=82.0,          # Good adaptation
        surface_adaptation=85.0,           # Decent surface adaptation
        car_adaptation=91.0,               # Quickly adapts to cars
        track_learning=86.0,               # Good at learning tracks
        
        # ===== PERSONAL & SOCIAL TRAITS =====
        media_presence=85.0,               # Charismatic personality
        team_cooperation=80.0,             # Sometimes conflicts with team
        leadership_ability=88.0,           # Natural leader
        risk_appetite=92.0,                # High risk tolerance
        ego_management=70.0,               # Sometimes struggles with ego
        commercial_appeal=82.0,            # Good marketability
        
        # Career stats
        career_wins=28,
        career_podiums=89,
        touring_wins=25,
        rallycross_wins=3,
        preferred_discipline="touring_car",
        career_phase="veteran"
    )


def create_rally_legend() -> Driver:
    """
    Create a rally specialist (Sebastien Loeb style)
    
    Profile: Master of all surfaces with exceptional adaptability
    and precision. Thrives on changing conditions and technical challenges.
    """
    return Driver(
        id=3,
        name="Erik Lindqvist", 
        nationality="SWE",
        birth_date="1974-02-16",
        age=40,
        
        # ===== CORE DRIVING SKILLS =====
        raw_speed=89.0,                    # Exceptional pace on all surfaces
        consistency=95.0,                  # Master of consistency
        racecraft=75.0,                    # Limited wheel-to-wheel experience
        overtaking=65.0,                   # Rarely needs to overtake
        defensive_driving=70.0,            # Limited defensive experience
        cornering_skill=92.0,              # Exceptional cornering precision
        braking_technique=88.0,            # Strong braking control
        acceleration_control=94.0,         # Master of traction control
        spatial_awareness=91.0,            # Exceptional spatial judgment
        vehicle_control=97.0,              # Legendary car control
        
        # ===== PHYSICAL & MENTAL TRAITS =====
        physical_fitness=93.0,             # Peak physical condition
        reaction_time=94.0,                # Lightning reflexes
        concentration=96.0,                # Exceptional concentration
        pressure_handling=90.0,            # Handles pressure well
        pain_tolerance=88.0,               # High pain tolerance
        g_force_tolerance=70.0,            # Limited high G experience
        coordination=95.0,                 # Perfect coordination
        multitasking=85.0,                 # Good multitasking
        mental_resilience=93.0,            # Mental strength
        adrenaline_management=92.0,        # Controls adrenaline perfectly
        
        # ===== TECHNICAL KNOWLEDGE =====
        setup_knowledge=94.0,              # Master of car setup
        mechanical_sympathy=96.0,          # Exceptional mechanical sympathy
        tire_management=91.0,              # Master of tire preservation
        fuel_management=88.0,              # Good fuel management
        aerodynamics_understanding=60.0,   # Limited aero knowledge
        suspension_feel=97.0,              # Legendary suspension feel
        engine_management=90.0,            # Excellent power management
        data_analysis=87.0,                # Good data interpretation
        
        # ===== DISCIPLINE SPECIALIZATIONS =====
        single_seater_aptitude=65.0,       # Could adapt to single seaters
        touring_car_aptitude=72.0,         # Good touring car potential
        rally_aptitude=98.0,               # Master of rally racing
        street_racing_aptitude=60.0,       # Some street racing ability
        drag_racing_aptitude=45.0,         # Limited drag racing
        rallycross_aptitude=88.0,          # Excellent rallycross ability
        endurance_aptitude=80.0,           # Good endurance potential
        
        # ===== RACE CRAFT & STRATEGY =====
        race_strategy=89.0,                # Strong strategic thinking
        pit_stop_coordination=82.0,        # Good crew coordination
        traffic_management=60.0,           # Limited traffic experience
        tire_strategy=92.0,                # Master of tire strategy
        fuel_strategy=88.0,                # Good fuel planning
        safety_car_awareness=70.0,         # Limited safety car experience
        qualifying_optimization=85.0,      # Good pace note optimization
        championship_thinking=94.0,        # Exceptional championship mentality
        
        # ===== ENVIRONMENTAL ADAPTATION =====
        wet_weather_skill=96.0,            # Master of wet conditions
        night_racing_skill=90.0,           # Excellent night driving
        temperature_adaptation=94.0,       # Master of temperature changes
        altitude_adaptation=88.0,          # Good high altitude performance
        surface_adaptation=98.0,           # Master of all surfaces
        car_adaptation=89.0,               # Adapts well to different cars
        track_learning=95.0,               # Exceptional at learning stages
        
        # ===== PERSONAL & SOCIAL TRAITS =====
        media_presence=78.0,               # Quiet but respected
        team_cooperation=92.0,             # Excellent team player
        leadership_ability=85.0,           # Leads by example
        risk_appetite=85.0,                # Calculated risk-taker
        ego_management=88.0,               # Humble despite success
        commercial_appeal=83.0,            # Strong but niche appeal
        
        # Career stats
        career_wins=78,
        career_podiums=156,
        rally_wins=76,
        rallycross_wins=2,
        preferred_discipline="rally",
        career_phase="veteran",
        championship_titles=9
    )


def create_versatile_all_rounder() -> Driver:
    """
    Create a versatile driver who can compete across multiple disciplines
    
    Profile: Well-rounded driver with good adaptability but no single
    outstanding specialization. Could succeed in multiple categories.
    """
    return Driver(
        id=4,
        name="Sofia Martinez",
        nationality="ESP", 
        birth_date="1992-08-10",
        age=26,
        
        # ===== CORE DRIVING SKILLS =====
        raw_speed=78.0,                    # Good overall pace
        consistency=82.0,                  # Reliable performer
        racecraft=80.0,                    # Solid wheel-to-wheel skills
        overtaking=79.0,                   # Good overtaking ability
        defensive_driving=77.0,            # Decent defensive skills
        cornering_skill=81.0,              # Good cornering technique
        braking_technique=79.0,            # Solid braking skills
        acceleration_control=80.0,         # Good launch technique
        spatial_awareness=84.0,            # Strong awareness
        vehicle_control=83.0,              # Good car control
        
        # ===== PHYSICAL & MENTAL TRAITS =====
        physical_fitness=85.0,             # Good physical condition
        reaction_time=82.0,                # Good reflexes
        concentration=80.0,                # Solid focus
        pressure_handling=78.0,            # Handles pressure reasonably
        pain_tolerance=79.0,               # Good endurance
        g_force_tolerance=81.0,            # Decent G-force tolerance
        coordination=83.0,                 # Good coordination
        multitasking=81.0,                 # Good multitasking
        mental_resilience=82.0,            # Resilient mindset
        adrenaline_management=79.0,        # Controls adrenaline well
        
        # ===== TECHNICAL KNOWLEDGE =====
        setup_knowledge=82.0,              # Good setup understanding
        mechanical_sympathy=80.0,          # Good mechanical preservation
        tire_management=81.0,              # Good tire management
        fuel_management=79.0,              # Decent fuel strategy
        aerodynamics_understanding=75.0,   # Basic aero knowledge
        suspension_feel=80.0,              # Good chassis feedback
        engine_management=78.0,            # Good power management
        data_analysis=83.0,                # Strong data interpretation
        
        # ===== DISCIPLINE SPECIALIZATIONS =====
        single_seater_aptitude=75.0,       # Could compete in formula
        touring_car_aptitude=78.0,         # Good touring car potential
        rally_aptitude=73.0,               # Decent rally ability
        street_racing_aptitude=80.0,       # Good street racing potential
        drag_racing_aptitude=65.0,         # Some drag racing ability
        rallycross_aptitude=81.0,          # Strong rallycross potential
        endurance_aptitude=79.0,           # Good endurance capability
        
        # ===== RACE CRAFT & STRATEGY =====
        race_strategy=84.0,                # Strong strategic thinking
        pit_stop_coordination=80.0,        # Good crew coordination
        traffic_management=82.0,           # Good traffic navigation
        tire_strategy=81.0,                # Good tire strategy
        fuel_strategy=80.0,                # Good fuel planning
        safety_car_awareness=79.0,         # Capitalizes on opportunities
        qualifying_optimization=78.0,      # Decent qualifying pace
        championship_thinking=85.0,        # Strong championship approach
        
        # ===== ENVIRONMENTAL ADAPTATION =====
        wet_weather_skill=83.0,            # Good wet weather skills
        night_racing_skill=80.0,           # Good night racing
        temperature_adaptation=84.0,       # Adapts well to conditions
        altitude_adaptation=81.0,          # Good adaptation
        surface_adaptation=85.0,           # Strong surface adaptation
        car_adaptation=88.0,               # Excellent car adaptation
        track_learning=86.0,               # Fast at learning new tracks
        
        # ===== PERSONAL & SOCIAL TRAITS =====
        media_presence=82.0,               # Good media personality
        team_cooperation=87.0,             # Excellent team player
        leadership_ability=79.0,           # Developing leadership
        risk_appetite=76.0,                # Measured risk-taker
        ego_management=84.0,               # Handles success and failure well
        commercial_appeal=81.0,            # Good marketability
        
        # Career stats
        career_wins=5,
        career_podiums=18,
        single_seater_wins=2,
        touring_wins=2,
        rallycross_wins=1,
        preferred_discipline="single_seater",
        career_phase="rising"
    )


# Helper functions
def get_performance_level(rating: float) -> str:
    """
    Convert numerical rating to performance level description
    
    Args:
        rating: Numerical rating (0-100)
        
    Returns:
        Performance level description string
    """
    if rating >= 90:
        return "Exceptional"
    elif rating >= 80:
        return "Excellent"
    elif rating >= 70:
        return "Good"
    elif rating >= 60:
        return "Average"
    elif rating >= 50:
        return "Below Average"
    else:
        return "Poor"


def print_driver_profile(driver, disciplines):
    """
    Print performance profile for a single driver
    
    Args:
        driver: Driver object to analyze
        disciplines: List of discipline names to evaluate
    """
    print(f"\n{driver.name} ({driver.nationality}, Age {driver.age}):")
    print(f"Primary: {driver.preferred_discipline.replace('_', ' ').title()}")
    print("-" * 40)
    
    for discipline in disciplines:
        rating = driver.get_discipline_rating(discipline)
        performance_level = get_performance_level(rating)
        discipline_name = discipline.replace('_', ' ').title()
        print(f"{discipline_name:15}: {rating:5.1f} ({performance_level})")


def demonstrate_driver_versatility():
    """
    Demonstrate how drivers with different profiles perform across disciplines
    """
    # Create example drivers
    drivers = [
        create_formula_specialist(),
        create_touring_car_battler(),
        create_rally_legend(),
        create_versatile_all_rounder()
    ]
    
    disciplines = [
        "single_seater", "touring_car", "rally", "street_racing", 
        "drag_racing", "rallycross", "endurance"
    ]
    
    print("Driver Performance Across Disciplines:")
    print("=" * 80)
    
    for driver in drivers:
        print_driver_profile(driver, disciplines)


if __name__ == "__main__":
    demonstrate_driver_versatility()


# Export example functions
__all__ = [
    'create_formula_specialist', 
    'create_touring_car_battler',
    'create_rally_legend',
    'create_versatile_all_rounder',
    'demonstrate_driver_versatility'
]