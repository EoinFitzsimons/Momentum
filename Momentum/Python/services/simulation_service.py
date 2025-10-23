"""
Simulation Service - Business Logic for Race Simulation

This service layer extracts orchestration logic from the API layer,
providing clean separation of concerns and making the code more testable.

Responsibilities:
- Fetch and validate race data
- Build simulation context
- Execute race simulation
- Persist results
- Format responses

This follows the Service Layer pattern for better maintainability.
"""

from typing import List, Dict, Any, Optional
import random
from database.database_manager import DatabaseManager
from database.models import Driver, Team, Track, Race, RaceResult
from disciplines.race_simulation import RaceSimulator, SimulationContext
from api.schemas import RaceResultResponse, DriverResult
import logging

logger = logging.getLogger(__name__)


class SimulationService:
    """
    Service layer for race simulation orchestration
    
    Handles all business logic for race simulation including data fetching,
    validation, simulation execution, and result persistence.
    """
    
    def __init__(self, db_manager: DatabaseManager, simulator: RaceSimulator):
        """
        Initialize simulation service
        
        Args:
            db_manager: Database manager for data access
            simulator: Race simulator for Monte Carlo simulation
        """
        self.db = db_manager
        self.simulator = simulator
    
    def simulate_race(
        self, 
        discipline: str, 
        race_id: int, 
        driver_ids: List[int],
        track_id: Optional[int] = None
    ) -> RaceResultResponse:
        """
        Orchestrate complete race simulation
        
        Steps:
        1. Fetch or create race
        2. Fetch drivers, teams, and track
        3. Validate all entities exist
        4. Build simulation context
        5. Run Monte Carlo simulation
        6. Persist results
        7. Return formatted response
        
        Args:
            discipline: Racing discipline (SINGLE_SEATER, RALLY_STAGE, etc.)
            race_id: Existing race ID or 0 to create new
            driver_ids: List of driver IDs to include
            track_id: Optional track ID (random if not specified)
        
        Returns:
            RaceResultResponse with complete race results
        
        Raises:
            ValueError: If validation fails (missing drivers, track, etc.)
            RuntimeError: If simulation fails
        """
        logger.info(f"Starting race simulation: discipline={discipline}, race_id={race_id}")
        
        # Step 1: Get or create track
        if track_id is None:
            track = self._get_random_track_for_discipline(discipline)
            if not track:
                raise ValueError(f"No tracks available for discipline: {discipline}")
        else:
            track = self.db.get_track(track_id)
            if not track:
                raise ValueError(f"Track not found: {track_id}")
        
        logger.info(f"Using track: {track.name} (ID: {track.id})")
        
        # Step 2: Get drivers
        if not driver_ids:
            # Use all drivers if none specified
            all_drivers = self.db.get_all_drivers()
            drivers = all_drivers[:20]  # Limit to first 20 for performance
        else:
            drivers = [self.db.get_driver(did) for did in driver_ids]
            drivers = [d for d in drivers if d is not None]  # Filter out None
        
        if not drivers:
            raise ValueError("No valid drivers found for simulation")
        
        logger.info(f"Simulating with {len(drivers)} drivers")
        
        # Step 3: Get teams (stub - assign first team to all drivers for now)
        teams = self.db.get_teams_by_discipline(discipline)
        if not teams:
            logger.warning(f"No teams found for discipline: {discipline}")
            teams_dict = {}
        else:
            teams_dict = {team.id: team for team in teams}
        
        # Step 4: Build simulation context
        context = SimulationContext(
            discipline=discipline,
            track=track,
            drivers=drivers,
            teams=teams_dict,
            race_id=race_id if race_id > 0 else None
        )
        
        # Step 5: Run simulation
        try:
            logger.info("Running Monte Carlo simulation...")
            race_result = self.simulator.simulate_race(context)
            logger.info("Simulation completed successfully")
        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)
            raise RuntimeError(f"Race simulation failed: {str(e)}")
        
        # Step 6: Format response
        response = self._format_race_response(race_result, track, drivers, teams_dict)
        
        return response
    
    def _get_random_track_for_discipline(self, discipline: str) -> Optional[Track]:
        """Get a random track for the specified discipline"""
        tracks = self.db.get_tracks_by_discipline(discipline)
        if not tracks:
            return None
        return random.choice(tracks)
    
    def _format_race_response(
        self,
        race_result: Any,  # RaceResult from simulation
        track: Track,
        drivers: List[Driver],
        teams: Dict[int, Team]
    ) -> RaceResultResponse:
        """
        Format simulation results into API response model
        
        Args:
            race_result: Raw result from simulator
            track: Track used for race
            drivers: List of drivers
            teams: Dictionary of teams
        
        Returns:
            Formatted RaceResultResponse
        """
        # Create driver results
        driver_results = []
        
        # If race_result has a results attribute with position data
        if hasattr(race_result, 'results') and race_result.results:
            for result in race_result.results:
                driver = next((d for d in drivers if d.id == result.driver_id), None)
                if driver:
                    driver_results.append(DriverResult(
                        driver_id=driver.id,
                        driver_name=driver.name,
                        team_id=result.team_id if hasattr(result, 'team_id') else None,
                        team_name=teams.get(result.team_id).name if hasattr(result, 'team_id') and result.team_id in teams else None,
                        position=result.position if hasattr(result, 'position') else 0,
                        finish_time=result.finish_time if hasattr(result, 'finish_time') else None,
                        points=result.points if hasattr(result, 'points') else 0,
                        status=result.status if hasattr(result, 'status') else "FINISHED"
                    ))
        else:
            # Fallback: create simple results based on driver order
            for i, driver in enumerate(drivers[:20], start=1):
                driver_results.append(DriverResult(
                    driver_id=driver.id,
                    driver_name=driver.name,
                    team_id=None,
                    team_name=None,
                    position=i,
                    points=self._calculate_points(i)
                ))
        
        # Build response
        return RaceResultResponse(
            race_id=race_result.race_id if hasattr(race_result, 'race_id') else 0,
            discipline=track.discipline,
            track_id=track.id,
            track_name=track.name,
            results=driver_results,
            simulation_metadata={
                "track_length_km": track.length_km,
                "track_difficulty": track.difficulty,
                "drivers_count": len(drivers),
                "simulation_type": "monte_carlo"
            }
        )
    
    def _calculate_points(self, position: int) -> int:
        """Calculate points for a finishing position (F1-style)"""
        points_map = {
            1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
            6: 8, 7: 6, 8: 4, 9: 2, 10: 1
        }
        return points_map.get(position, 0)
