"""
Disciplines Package

Racing discipline definitions including metadata, regulations, and simulation engines.

Each discipline is fully self-contained with:
- discipline_config.py: Competition format and scoring
- rulebook.py: Technical regulations and compliance validation
- *_engine.py: Simulation engine for race execution

Authors: Final Year Project - Computer Science
"""

from .single_seater import (
    SingleSeaterConfig, SINGLE_SEATER_CONFIG,
    SingleSeaterRulebook, SINGLE_SEATER_RULEBOOK
)
from .production_touring import (
    ProductionTouringConfig, PRODUCTION_TOURING_CONFIG,
    ProductionTouringRulebook, PRODUCTION_TOURING_RULEBOOK
)
from .rally_stage import (
    RallyStageConfig, RALLY_STAGE_CONFIG,
    RallyStageRulebook, RALLY_STAGE_RULEBOOK
)
from .urban_street import (
    UrbanStreetConfig, URBAN_STREET_CONFIG,
    UrbanStreetRulebook, URBAN_STREET_RULEBOOK
)
from .drag_acceleration import (
    DragAccelerationConfig, DRAG_ACCELERATION_CONFIG,
    DragAccelerationRulebook, DRAG_ACCELERATION_RULEBOOK
)
from .sprint_rallycross import (
    SprintRallycrossConfig, SPRINT_RALLYCROSS_CONFIG,
    SprintRallycrossRulebook, SPRINT_RALLYCROSS_RULEBOOK
)
from .endurance import (
    EnduranceConfig, ENDURANCE_CONFIG,
    EnduranceRulebook, ENDURANCE_RULEBOOK
)

# Discipline registry for easy lookup
DISCIPLINE_CONFIGS = {
    'single_seater': SINGLE_SEATER_CONFIG,
    'production_touring': PRODUCTION_TOURING_CONFIG,
    'rally_stage': RALLY_STAGE_CONFIG,
    'urban_street': URBAN_STREET_CONFIG,
    'drag_acceleration': DRAG_ACCELERATION_CONFIG,
    'sprint_rallycross': SPRINT_RALLYCROSS_CONFIG,
    'endurance': ENDURANCE_CONFIG
}

DISCIPLINE_RULEBOOKS = {
    'single_seater': SINGLE_SEATER_RULEBOOK,
    'production_touring': PRODUCTION_TOURING_RULEBOOK,
    'rally_stage': RALLY_STAGE_RULEBOOK,
    'urban_street': URBAN_STREET_RULEBOOK,
    'drag_acceleration': DRAG_ACCELERATION_RULEBOOK,
    'sprint_rallycross': SPRINT_RALLYCROSS_RULEBOOK,
    'endurance': ENDURANCE_RULEBOOK
}

__all__ = [
    # Single Seater
    'SingleSeaterConfig', 'SINGLE_SEATER_CONFIG',
    'SingleSeaterRulebook', 'SINGLE_SEATER_RULEBOOK',
    
    # Production Touring
    'ProductionTouringConfig', 'PRODUCTION_TOURING_CONFIG',
    'ProductionTouringRulebook', 'PRODUCTION_TOURING_RULEBOOK',
    
    # Rally Stage
    'RallyStageConfig', 'RALLY_STAGE_CONFIG',
    'RallyStageRulebook', 'RALLY_STAGE_RULEBOOK',
    
    # Urban Street
    'UrbanStreetConfig', 'URBAN_STREET_CONFIG',
    'UrbanStreetRulebook', 'URBAN_STREET_RULEBOOK',
    
    # Drag Acceleration
    'DragAccelerationConfig', 'DRAG_ACCELERATION_CONFIG',
    'DragAccelerationRulebook', 'DRAG_ACCELERATION_RULEBOOK',
    
    # Sprint Rallycross
    'SprintRallycrossConfig', 'SPRINT_RALLYCROSS_CONFIG',
    'SprintRallycrossRulebook', 'SPRINT_RALLYCROSS_RULEBOOK',
    
    # Endurance
    'EnduranceConfig', 'ENDURANCE_CONFIG',
    'EnduranceRulebook', 'ENDURANCE_RULEBOOK',
    
    # Registries
    'DISCIPLINE_CONFIGS',
    'DISCIPLINE_RULEBOOKS'
]
