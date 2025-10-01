"""
Multi-Discipline Racing Simulator - Main coordinator for all racing disciplines

This module serves as the main entry point for race simulations, routing
requests to the appropriate discipline-specific engines while maintaining
backwards compatibility with the existing race_simulation.py interface.

Features:
- Automatic discipline detection and routing
- Backwards compatibility with existing code
- Unified race result handling
- Configuration management for discipline-specific settings
- Error handling and fallback mechanisms

Supported Disciplines:
- Single Seater
- Production/Touring
- Rally/Stage
- Urban/Street
- Drag/Acceleration
- Sprint/Rallycross
- Endurance

Authors: Final Year Project - Computer Science
"""

from typing import List, Dict, Optional, Type, Any
import logging

from database.models import Driver, Team, Race, RaceResult
from .base_engine import BaseDisciplineEngine, DisciplineContext, RacingDiscipline, RaceEventType
from .single_seater.single_seater_engine import SingleSeaterEngine
from .production_touring.production_touring_engine import ProductionTouringEngine
from .rally_stage.rally_stage_engine import RallyStageEngine
from .urban_street.urban_street_engine import UrbanStreetEngine
from .drag_acceleration.drag_acceleration_engine import DragAccelerationEngine
from .sprint_rallycross.sprint_rallycross_engine import SprintRallycrossEngine
from .endurance.endurance_engine import EnduranceEngine


class MultiDisciplineSimulator:
    """
    Main coordinator for multi-discipline racing simulation
    
    Routes races to appropriate discipline-specific engines based on
    race configuration and discipline settings. Provides a unified
    interface for all racing simulations while maintaining backwards
    compatibility.
    """
    
    def __init__(self, seed: int = None):
        """Initialize the multi-discipline simulator with all engines"""
        self.seed = seed
        self._engines: Dict[RacingDiscipline, BaseDisciplineEngine] = {}
        self._initialize_engines()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _initialize_engines(self) -> None:
        """Initialize all discipline-specific engines"""
        self._engines = {
            RacingDiscipline.SINGLE_SEATER: SingleSeaterEngine(self.seed),
            RacingDiscipline.PRODUCTION_TOURING: ProductionTouringEngine(self.seed),
            RacingDiscipline.RALLY_STAGE: RallyStageEngine(self.seed),
            RacingDiscipline.URBAN_STREET: UrbanStreetEngine(self.seed),
            RacingDiscipline.DRAG_ACCELERATION: DragAccelerationEngine(self.seed),
            RacingDiscipline.SPRINT_RALLYCROSS: SprintRallycrossEngine(self.seed),
            RacingDiscipline.ENDURANCE: EnduranceEngine(self.seed)
        }
    
    def simulate_race(self, race: Race, drivers: List[Driver], teams: Dict[int, Team], 
                     event_type: RaceEventType = RaceEventType.MAIN_RACE,
                     discipline_config: Optional[Dict[str, Any]] = None) -> List[RaceResult]:
        """
        Main race simulation entry point
        
        Args:
            race: Race object containing race information
            drivers: List of participating drivers
            teams: Dictionary of teams indexed by team ID
            event_type: Type of event (qualifying, main race, etc.)
            discipline_config: Optional discipline-specific configuration
            
        Returns:
            List of race results ordered by finishing position
        """
        try:
            # Determine racing discipline
            discipline = self._determine_discipline(race, discipline_config)
            
            # Get appropriate engine
            engine = self._get_engine(discipline)
            
            # Create discipline context
            context = self._create_discipline_context(
                race, drivers, teams, event_type, discipline_config
            )
            
            # Validate event type is supported
            if not self._validate_event_type(engine, event_type):
                raise ValueError(f"Event type {event_type} not supported for {discipline}")
            
            # Log simulation start
            self.logger.info(f"Starting {discipline.value} {event_type.value} simulation for race {race.id}")
            
            # Execute simulation
            results = engine.simulate_event(context)
            
            # Validate and post-process results
            results = self._post_process_results(results, race, drivers, teams)
            
            self.logger.info(f"Completed simulation with {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Race simulation failed: {str(e)}")
            # Fallback to basic simulation to maintain compatibility
            return self._fallback_simulation(race, drivers, teams, event_type)
    
    def get_discipline_info(self, discipline: RacingDiscipline) -> Dict[str, Any]:
        """
        Get information about a specific racing discipline
        
        Returns discipline characteristics, supported events, and strategic elements
        """
        engine = self._get_engine(discipline)
        
        return {
            'discipline': discipline.value,
            'attribute_weights': engine.get_attribute_weights(),
            'supported_events': [event.value for event in engine.get_supported_event_types()],
            'strategic_elements': engine.get_strategic_elements(),
            'scoring_system': engine.get_scoring_system()
        }
    
    def get_all_disciplines(self) -> List[Dict[str, Any]]:
        """Get information about all supported racing disciplines"""
        return [self.get_discipline_info(discipline) for discipline in RacingDiscipline]
    
    def _determine_discipline(self, race: Race, discipline_config: Optional[Dict[str, Any]]) -> RacingDiscipline:
        """
        Determine the racing discipline for this race
        
        Uses race configuration, series information, or defaults to single seater
        """
        if discipline_config and 'discipline' in discipline_config:
            # Explicit discipline configuration
            discipline_name = discipline_config['discipline'].lower()
            discipline_map = {
                'single_seater': RacingDiscipline.SINGLE_SEATER,
                'formula': RacingDiscipline.SINGLE_SEATER,
                'f1': RacingDiscipline.SINGLE_SEATER,
                'indycar': RacingDiscipline.SINGLE_SEATER,
                'production': RacingDiscipline.PRODUCTION_TOURING,
                'touring': RacingDiscipline.PRODUCTION_TOURING,
                'btcc': RacingDiscipline.PRODUCTION_TOURING,
                'wtcc': RacingDiscipline.PRODUCTION_TOURING,
                'rally': RacingDiscipline.RALLY_STAGE,
                'wrc': RacingDiscipline.RALLY_STAGE,
                'stage': RacingDiscipline.RALLY_STAGE,
                'urban': RacingDiscipline.URBAN_STREET,
                'street': RacingDiscipline.URBAN_STREET,
                'drift': RacingDiscipline.URBAN_STREET,
                'drag': RacingDiscipline.DRAG_ACCELERATION,
                'acceleration': RacingDiscipline.DRAG_ACCELERATION,
                'nhra': RacingDiscipline.DRAG_ACCELERATION,
                'sprint': RacingDiscipline.SPRINT_RALLYCROSS,
                'rallycross': RacingDiscipline.SPRINT_RALLYCROSS,
                'worldrx': RacingDiscipline.SPRINT_RALLYCROSS,
                'endurance': RacingDiscipline.ENDURANCE,
                'lemans': RacingDiscipline.ENDURANCE,
                'imsa': RacingDiscipline.ENDURANCE,
                'wec': RacingDiscipline.ENDURANCE
            }
            
            return discipline_map.get(discipline_name, RacingDiscipline.SINGLE_SEATER)
        
        # Try to determine from race name or track characteristics
        race_name = getattr(race, 'name', '').lower()
        track_name = getattr(race, 'track', '').lower()
        
        # Check for discipline keywords in race/track names
        if any(keyword in race_name or keyword in track_name for keyword in ['rally', 'stage', 'wrc']):
            return RacingDiscipline.RALLY_STAGE
        elif any(keyword in race_name or keyword in track_name for keyword in ['drift', 'street', 'underground']):
            return RacingDiscipline.URBAN_STREET
        elif any(keyword in race_name or keyword in track_name for keyword in ['drag', 'quarter', 'nhra']):
            return RacingDiscipline.DRAG_ACCELERATION
        elif any(keyword in race_name or keyword in track_name for keyword in ['rallycross', 'sprint', 'rx']):
            return RacingDiscipline.SPRINT_RALLYCROSS
        elif any(keyword in race_name or keyword in track_name for keyword in ['endurance', 'lemans', '24', 'hours']):
            return RacingDiscipline.ENDURANCE
        elif any(keyword in race_name or keyword in track_name for keyword in ['touring', 'production', 'btcc', 'wtcc']):
            return RacingDiscipline.PRODUCTION_TOURING
        
        # Default to single seater for backwards compatibility
        return RacingDiscipline.SINGLE_SEATER
    
    def _get_engine(self, discipline: RacingDiscipline) -> BaseDisciplineEngine:
        """Get the appropriate engine for the discipline"""
        engine = self._engines.get(discipline)
        if not engine:
            raise ValueError(f"No engine available for discipline: {discipline}")
        return engine
    
    def _create_discipline_context(self, race: Race, drivers: List[Driver], teams: Dict[int, Team],
                                 event_type: RaceEventType, discipline_config: Optional[Dict[str, Any]]) -> DisciplineContext:
        """Create discipline context for the simulation"""
        # Default weather conditions if not specified
        default_weather = {
            "temperature": 25.0,
            "humidity": 0.5,
            "precipitation": 0.0,
            "wind_speed": 10.0
        }
        
        # Extract weather from race or use defaults
        weather_conditions = getattr(race, 'weather_conditions', default_weather)
        if isinstance(weather_conditions, str):
            # If weather is stored as string, parse or use defaults
            weather_conditions = default_weather
        
        return DisciplineContext(
            race=race,
            drivers=drivers,
            teams=teams,
            event_type=event_type,
            weather_conditions=weather_conditions,
            discipline_config=discipline_config or {}
        )
    
    def _validate_event_type(self, engine: BaseDisciplineEngine, event_type: RaceEventType) -> bool:
        """Validate that the engine supports the requested event type"""
        return event_type in engine.get_supported_event_types()
    
    def _post_process_results(self, results: List[RaceResult], race: Race, 
                            drivers: List[Driver], teams: Dict[int, Team]) -> List[RaceResult]:
        """
        Post-process simulation results for consistency and validation
        """
        # Ensure results are properly ordered by position
        results.sort(key=lambda x: (x.dnf_reason is not None, x.position))
        
        # Validate result consistency
        for i, result in enumerate(results):
            # Ensure position matches list order
            expected_position = i + 1
            if result.position != expected_position:
                result.position = expected_position
            
            # Validate driver and team references
            if not any(d.id == result.driver_id for d in drivers):
                self.logger.warning(f"Invalid driver ID in result: {result.driver_id}")
                continue
            
            if result.team_id not in teams:
                self.logger.warning(f"Invalid team ID in result: {result.team_id}")
                continue
        
        return results
    
    def _fallback_simulation(self, race: Race, drivers: List[Driver], 
                           teams: Dict[int, Team], event_type: RaceEventType) -> List[RaceResult]:
        """
        Fallback simulation using single seater engine for backwards compatibility
        """
        self.logger.warning("Using fallback simulation due to error")
        
        try:
            engine = self._engines[RacingDiscipline.SINGLE_SEATER]
            context = self._create_discipline_context(race, drivers, teams, event_type, None)
            return engine.simulate_event(context)
        except Exception as e:
            self.logger.error(f"Fallback simulation also failed: {str(e)}")
            # Ultimate fallback - basic results
            return self._create_basic_results(race, drivers, teams)
    
    def _create_basic_results(self, race: Race, drivers: List[Driver], teams: Dict[int, Team]) -> List[RaceResult]:
        """Create basic results when all else fails"""
        import random
        
        # Shuffle drivers for random results
        shuffled_drivers = drivers.copy()
        random.shuffle(shuffled_drivers)
        
        results = []
        for position, driver in enumerate(shuffled_drivers, 1):
            result = RaceResult(
                id=0,
                race_id=race.id,
                driver_id=driver.id,
                team_id=driver.current_team_id,
                position=position,
                points=max(0, 26 - position) if position <= 10 else 0,
                fastest_lap=position == 1,
                dnf_reason=None,
                grid_position=position
            )
            results.append(result)
        
        return results


# Backwards compatibility function - maintains existing interface
def simulate_race(race: Race, drivers: List[Driver], teams: Dict[int, Team], 
                 event_type: RaceEventType = RaceEventType.MAIN_RACE,
                 discipline: Optional[str] = None, **kwargs) -> List[RaceResult]:
    """
    Backwards compatible race simulation function
    
    This function maintains the same interface as the original race_simulation.py
    while routing to the new multi-discipline system.
    """
    # Create discipline config from parameters
    discipline_config = {}
    if discipline:
        discipline_config['discipline'] = discipline
    
    # Add any additional configuration from kwargs
    discipline_config.update(kwargs)
    
    # Create simulator and run simulation
    simulator = MultiDisciplineSimulator()
    return simulator.simulate_race(race, drivers, teams, event_type, discipline_config)


# Export main classes and functions
__all__ = ['MultiDisciplineSimulator', 'simulate_race', 'RacingDiscipline', 'RaceEventType']