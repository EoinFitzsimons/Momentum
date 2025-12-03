"""
Driver Attribute Mapping for Advanced Racing Physics

Maps non-existent attributes to actual Driver model attributes.
This ensures the overtaking system uses only real attributes.
"""

from database.models import Driver


def get_driver_aggression(driver: Driver) -> float:
    """Aggression = combination of bravery and overtaking tendency"""
    return (driver.overtaking * 0.6 + driver.bravery * 0.4) if hasattr(driver, 'bravery') else driver.overtaking


def get_driver_wheel_to_wheel_ability(driver: Driver) -> float:
    """Wheel-to-wheel = traffic management + spatial awareness + defensive driving"""
    return (
        driver.traffic_management * 0.4 +
        driver.spatial_awareness * 0.3 +
        driver.defensive_driving * 0.3
    )


def get_driver_confidence(driver: Driver) -> float:
    """Confidence = derived from form and professionalism"""
    base = driver.professionalism
    
    # Boost if good form
    if hasattr(driver, 'form_trend'):
        if driver.form_trend == 'improving':
            base *= 1.1
        elif driver.form_trend == 'declining':
            base *= 0.9
    
    # Experience matters
    if hasattr(driver, 'seasons_active'):
        experience_boost = min(driver.seasons_active / 10.0, 1.0) * 10
        base = min(base + experience_boost, 100.0)
    
    return base


def get_driver_patience(driver: Driver) -> float:
    """Patience = inverse of aggression, plus professionalism"""
    aggression = get_driver_aggression(driver)
    return (100 - aggression) * 0.5 + driver.professionalism * 0.5


def get_driver_bravery(driver: Driver) -> float:
    """
    Bravery estimation from existing attributes
    
    Note: Bravery might exist in DB but not in Python model.
    Using racing attributes as proxy.
    """
    # Check if it actually exists first
    if hasattr(driver, 'bravery'):
        return driver.bravery
    
    # Estimate from overtaking + risk-taking behavior
    return (
        driver.overtaking * 0.5 +
        driver.raw_speed * 0.3 +
        (100 - driver.consistency) * 0.2  # Less consistency = more risk-taking
    )


# Attribute availability check
AVAILABLE_ATTRIBUTES = [
    'raw_speed', 'consistency', 'racecraft', 'overtaking', 'defensive_driving',
    'cornering_skill', 'braking_technique', 'acceleration_control', 
    'spatial_awareness', 'vehicle_control',
    'physical_fitness', 'reaction_time', 'concentration', 'pressure_handling',
    'pain_tolerance', 'g_force_tolerance', 'coordination', 'multitasking',
    'mental_resilience', 'adrenaline_management',
    'setup_knowledge', 'mechanical_sympathy', 'tire_management', 'fuel_management',
    'aerodynamics_understanding', 'suspension_feel', 'engine_management', 'data_analysis',
    'race_strategy', 'pit_entry_exit', 'traffic_management', 'qualifying_pace',
    'race_pace', 'starting_skill', 'tyre_warming', 'energy_management',
    'wet_weather_skill', 'night_driving', 'heat_tolerance', 'cold_tolerance',
    'altitude_adaptation', 'visibility_adaptation', 'surface_adaptation',
    'media_handling', 'sponsorship_appeal', 'fan_engagement', 'team_player',
    'leadership', 'professionalism'
]


def validate_driver_attribute(attribute_name: str) -> bool:
    """Check if attribute exists in Driver model"""
    return attribute_name in AVAILABLE_ATTRIBUTES


def get_safe_attribute(driver: Driver, attribute_name: str, default: float = 50.0) -> float:
    """
    Safely get driver attribute with fallback
    
    Args:
        driver: Driver instance
        attribute_name: Name of attribute
        default: Default value if not found
    
    Returns:
        Attribute value or computed equivalent
    """
    # Direct mapping
    if hasattr(driver, attribute_name):
        return getattr(driver, attribute_name)
    
    # Computed mappings
    computed_map = {
        'aggression': lambda d: get_driver_aggression(d),
        'wheel_to_wheel_ability': lambda d: get_driver_wheel_to_wheel_ability(d),
        'confidence': lambda d: get_driver_confidence(d),
        'patience': lambda d: get_driver_patience(d),
        'bravery': lambda d: get_driver_bravery(d),
    }
    
    if attribute_name in computed_map:
        return computed_map[attribute_name](driver)
    
    # Fallback
    return default
