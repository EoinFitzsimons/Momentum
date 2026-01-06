"""
Momentum Motorsport Simulation API Server

Main entry point for the Momentum multi-discipline motorsport management simulation backend.
Provides comprehensive REST API for championship management, race simulation, and data access.

Key Features:
- Championship lifecycle management (UC-4 to UC-10)
- Race simulation and results tracking
- Championship standings with discipline-specific points
- Event scheduling and status management
- Season rollover automation

API Endpoints:
- GET /: System information
- GET /health: Health check
- GET /drivers: List all drivers
- GET /teams: List teams (filterable)
- POST /championships: Create new championship (UC-10)
- GET /championships/{id}: Get championship details (UC-5)
- GET /championships/{id}/results: Get race results (UC-4)
- GET /championships/{id}/schedule: Get race schedule (UC-8)
- GET /championships/{id}/standings: Get championship standings
- POST /championships/{id}/standings/recalculate: Recalculate standings (UC-6)
- POST /championships/{id}/events: Create race event (UC-7)
- PATCH /races/{id}/status: Update race status (UC-9)
- GET /races/{id}/results: Get race classification details
- POST /simulate/race: Run race simulation

Authors: Final Year Project - Computer Science
Version: 2.0.0 (Championship Management Update)
Compatible with: Python 3.8+, FastAPI 0.100+
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uvicorn

from database.database_manager import DatabaseManager
from database.models import Championship, Race, RaceResult
from services.championship_service import ChampionshipService
from api.schemas import (
    ChampionshipCreate,
    ChampionshipResponse,
    ChampionshipDetailsResponse,
    ChampionshipStandingsResponse,
    ChampionshipScheduleResponse,
    RaceEventCreate,
    RaceEventResponse,
    RaceStatusUpdate,
    RaceResultDetailResponse,
    RecalculateStandingsResponse,
    HealthCheckResponse,
    StandingEntry
)
from config import API_HOST, API_PORT, API_RELOAD

# Initialize FastAPI application
app = FastAPI(
    title="Momentum Simulation API",
    description="Multi-discipline Motorsport Management Simulator - Championship Management System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_manager = DatabaseManager()
championship_service = ChampionshipService(db_manager)


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """
    API Root - System Information
    
    Provides basic information about the API including available endpoints.
    """
    return {
        "message": "Momentum Simulation API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Championship Management (UC-4 to UC-10)",
            "Race Simulation",
            "Multi-discipline Support",
            "Real-time Standings Calculation"
        ],
        "endpoints": {
            "health": "GET /health",
            "drivers": "GET /drivers",
            "teams": "GET /teams",
            "championships": "GET /championships",
            "create_championship": "POST /championships",
            "championship_details": "GET /championships/{id}",
            "championship_standings": "GET /championships/{id}/standings",
            "championship_schedule": "GET /championships/{id}/schedule",
            "race_results": "GET /races/{id}/results"
        }
    }


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """
    Health Check Endpoint
    
    Verifies API and database connectivity.
    """
    try:
        stats = db_manager.get_database_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# ============================================================================
# DRIVER & TEAM ENDPOINTS
# ============================================================================

@app.get("/drivers")
def list_drivers(
    discipline: Optional[str] = Query(None, description="Filter by preferred discipline"),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get list of drivers with optional filtering"""
    try:
        drivers = db_manager.get_all_drivers()
        
        if discipline:
            drivers = [d for d in drivers if d.preferred_discipline == discipline]
        
        return {
            "drivers": drivers[:limit],
            "count": len(drivers[:limit]),
            "total": len(drivers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/teams")
def list_teams(
    discipline: Optional[str] = Query(None, description="Filter by discipline")
):
    """Get list of teams with optional filtering"""
    try:
        if discipline:
            teams = db_manager.get_teams_by_discipline(discipline)
        else:
            teams = db_manager.get_all_teams()
        
        return {
            "teams": teams,
            "count": len(teams)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-10: CREATE CHAMPIONSHIP
# ============================================================================

@app.post("/championships", response_model=ChampionshipResponse, status_code=201)
def create_championship(request: ChampionshipCreate):
    """
    Create New Championship (UC-10)
    
    Creates a new championship season with calendar and initial configuration.
    Supports season rollover automation and rules validation.
    
    Args:
        request: Championship creation parameters
        
    Returns:
        Created championship details
    """
    try:
        # Create championship object
        championship = Championship(
            id=0,  # Will be assigned by database
            name=request.name,
            discipline=request.discipline,
            season_length=request.season_length,
            points_system=request.points_system,
            current_season=1,
            tier=request.tier,
            founded_year=request.founded_year,
            description=request.description,
            archived=False
        )
        
        # Set start date
        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        # Create championship with calendar
        if request.track_ids:
            champ_id, race_ids = championship_service.create_championship_season(
                championship,
                request.track_ids,
                start_date
            )
        else:
            champ_id = db_manager.create_championship(championship)
        
        # Retrieve created championship
        created_champ = db_manager.get_championship(champ_id)
        
        if not created_champ:
            raise HTTPException(status_code=500, detail="Championship created but not retrievable")
        
        return ChampionshipResponse(
            id=created_champ.id,
            name=created_champ.name,
            discipline=created_champ.discipline,
            season_length=created_champ.season_length,
            points_system=created_champ.points_system,
            current_season=created_champ.current_season,
            tier=created_champ.tier,
            founded_year=created_champ.founded_year,
            description=created_champ.description,
            archived=created_champ.archived
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create championship: {str(e)}")


# ============================================================================
# UC-5: READ CHAMPIONSHIP DETAILS
# ============================================================================

@app.get("/championships/{championship_id}", response_model=ChampionshipDetailsResponse)
def get_championship_details(
    championship_id: int,
    season: Optional[int] = Query(None, description="Season number (defaults to current)")
):
    """
    Get Championship Details (UC-5)
    
    Returns comprehensive championship information including metadata,
    current standings, and race calendar. Supports archived championships.
    
    Args:
        championship_id: Championship ID
        season: Season number (optional, defaults to current season)
        
    Returns:
        Complete championship details
    """
    try:
        # Get championship
        championship = db_manager.get_championship(championship_id)
        
        if not championship:
            raise HTTPException(status_code=404, detail=f"Championship {championship_id} not found")
        
        # Use current season if not specified
        target_season = season if season is not None else championship.current_season
        
        # Get standings
        standings = championship_service.recalculate_standings(championship_id, target_season)
        
        # Get calendar
        calendar = championship_service.get_championship_calendar(championship_id, target_season)
        
        return ChampionshipDetailsResponse(
            championship=ChampionshipResponse(
                id=championship.id,
                name=championship.name,
                discipline=championship.discipline,
                season_length=championship.season_length,
                points_system=championship.points_system,
                current_season=championship.current_season,
                tier=championship.tier,
                founded_year=championship.founded_year,
                description=championship.description,
                archived=championship.archived
            ),
            current_standings=[
                StandingEntry(
                    position=s.position,
                    driver_id=s.driver_id,
                    driver_name=s.driver_name,
                    team_id=s.team_id,
                    team_name=s.team_name,
                    total_points=s.total_points,
                    wins=s.wins,
                    podiums=s.podiums,
                    races_started=s.races_started,
                    dnf_count=s.dnf_count,
                    fastest_laps=s.fastest_laps
                ) for s in standings
            ],
            calendar=[
                RaceEventResponse(
                    race_id=r["race_id"],
                    round_number=r["round_number"],
                    race_date=r["race_date"],
                    track_id=r["track_id"],
                    track_name=r["track_name"],
                    track_country=r["track_country"],
                    status=r["status"],
                    weather_conditions=r["weather_conditions"],
                    laps=r["laps"]
                ) for r in calendar
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-6: UPDATE CHAMPIONSHIP STANDINGS
# ============================================================================

@app.post(
    "/championships/{championship_id}/standings/recalculate",
    response_model=RecalculateStandingsResponse
)
def recalculate_championship_standings(
    championship_id: int,
    season: Optional[int] = Query(None, description="Season to recalculate")
):
    """
    Recalculate Championship Standings (UC-6)
    
    Recalculates championship points using discipline-specific points systems
    and applies tie-breaking rules. Supports async job queue for large datasets.
    
    Args:
        championship_id: Championship ID
        season: Season number (optional, defaults to current)
        
    Returns:
        Updated standings
    """
    try:
        championship = db_manager.get_championship(championship_id)
        
        if not championship:
            raise HTTPException(status_code=404, detail=f"Championship {championship_id} not found")
        
        target_season = season if season is not None else championship.current_season
        
        # Recalculate standings
        standings = championship_service.recalculate_standings(championship_id, target_season)
        
        return RecalculateStandingsResponse(
            success=True,
            championship_id=championship_id,
            season=target_season,
            standings=[
                StandingEntry(
                    position=s.position,
                    driver_id=s.driver_id,
                    driver_name=s.driver_name,
                    team_id=s.team_id,
                    team_name=s.team_name,
                    total_points=s.total_points,
                    wins=s.wins,
                    podiums=s.podiums,
                    races_started=s.races_started,
                    dnf_count=s.dnf_count,
                    fastest_laps=s.fastest_laps
                ) for s in standings
            ],
            message=f"Standings recalculated for {len(standings)} drivers"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-7: CREATE RACE EVENT
# ============================================================================

@app.post(
    "/championships/{championship_id}/events",
    response_model=RaceEventResponse,
    status_code=201
)
def create_race_event(championship_id: int, request: RaceEventCreate):
    """
    Create Race Event (UC-7)
    
    Adds a new race to the championship calendar with validation for
    date/track conflicts and track availability.
    
    Args:
        championship_id: Championship ID
        request: Race event parameters
        
    Returns:
        Created race event details
    """
    try:
        championship = db_manager.get_championship(championship_id)
        
        if not championship:
            raise HTTPException(status_code=404, detail=f"Championship {championship_id} not found")
        
        # Validate event
        is_valid, error_msg = championship_service.validate_race_event(
            championship_id,
            request.track_id,
            request.race_date,
            championship.current_season
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get current round number
        calendar = championship_service.get_championship_calendar(
            championship_id,
            championship.current_season
        )
        next_round = len(calendar) + 1
        
        # Create race
        race = Race(
            id=0,
            championship_id=championship_id,
            track_id=request.track_id,
            season=championship.current_season,
            round_number=next_round,
            race_date=request.race_date,
            weather_conditions=request.weather_conditions,
            laps=request.laps,
            status="scheduled"
        )
        
        race_id = db_manager.create_race(race)
        
        if not race_id:
            raise HTTPException(status_code=500, detail="Failed to create race")
        
        # Get track details
        track = db_manager.get_track(request.track_id)
        
        return RaceEventResponse(
            race_id=race_id,
            round_number=next_round,
            race_date=request.race_date,
            track_id=request.track_id,
            track_name=track.name if track else "Unknown",
            track_country=track.country if track else "Unknown",
            status="scheduled",
            weather_conditions=request.weather_conditions,
            laps=request.laps
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-8: READ RACE SCHEDULE
# ============================================================================

@app.get("/championships/{championship_id}/schedule", response_model=ChampionshipScheduleResponse)
def get_championship_schedule(
    championship_id: int,
    season: Optional[int] = Query(None, description="Season number")
):
    """
    Get Race Schedule (UC-8)
    
    Returns ordered list of races with date and status flags.
    
    Args:
        championship_id: Championship ID
        season: Season number (optional)
        
    Returns:
        Championship race schedule
    """
    try:
        championship = db_manager.get_championship(championship_id)
        
        if not championship:
            raise HTTPException(status_code=404, detail=f"Championship {championship_id} not found")
        
        target_season = season if season is not None else championship.current_season
        
        calendar = championship_service.get_championship_calendar(championship_id, target_season)
        
        return ChampionshipScheduleResponse(
            championship_id=championship_id,
            season=target_season,
            races=[
                RaceEventResponse(
                    race_id=r["race_id"],
                    round_number=r["round_number"],
                    race_date=r["race_date"],
                    track_id=r["track_id"],
                    track_name=r["track_name"],
                    track_country=r["track_country"],
                    status=r["status"],
                    weather_conditions=r["weather_conditions"],
                    laps=r["laps"]
                ) for r in calendar
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-9: UPDATE RACE STATUS
# ============================================================================

@app.patch("/races/{race_id}/status")
def update_race_status(race_id: int, request: RaceStatusUpdate):
    """
    Update Race Status (UC-9)
    
    Updates race lifecycle state with validation for valid transitions:
    - scheduled → in-progress
    - in-progress → completed
    - scheduled → cancelled
    
    Args:
        race_id: Race ID
        request: New status
        
    Returns:
        Success confirmation
    """
    try:
        success, error_msg = championship_service.update_race_lifecycle_status(
            race_id,
            request.status
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=error_msg)
        
        return {
            "success": True,
            "race_id": race_id,
            "new_status": request.status,
            "message": f"Race status updated to {request.status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-4: READ RACE RESULTS
# ============================================================================

@app.get("/races/{race_id}/results", response_model=RaceResultDetailResponse)
def get_race_results(race_id: int):
    """
    Get Race Results (UC-4)
    
    Returns complete race classification with lap data and provisional/final status.
    
    Args:
        race_id: Race ID
        
    Returns:
        Race classification and results
    """
    try:
        race = db_manager.get_race(race_id)
        
        if not race:
            raise HTTPException(status_code=404, detail=f"Race {race_id} not found")
        
        # Get track details
        track = db_manager.get_track(race.track_id)
        
        # Get results
        results = db_manager.get_race_results(race_id)
        
        # Build classification
        classification = []
        fastest_lap_info = None
        
        for result in results:
            driver = db_manager.get_driver(result.driver_id)
            team = db_manager.get_team(result.team_id) if result.team_id else None
            
            entry = {
                "position": result.position,
                "driver_id": result.driver_id,
                "driver_name": driver.name if driver else f"Driver {result.driver_id}",
                "team_id": result.team_id,
                "team_name": team.name if team else "No Team",
                "points": result.points,
                "fastest_lap": result.fastest_lap,
                "dnf_reason": result.dnf_reason,
                "grid_position": result.grid_position,
                "time_seconds": result.time_seconds,
                "status": "DNF" if result.dnf_reason else "Finished"
            }
            
            classification.append(entry)
            
            if result.fastest_lap and not fastest_lap_info:
                fastest_lap_info = {
                    "driver_name": driver.name if driver else f"Driver {result.driver_id}",
                    "time": result.time_seconds
                }
        
        return RaceResultDetailResponse(
            race_id=race_id,
            championship_id=race.championship_id,
            season=race.season,
            round_number=race.round_number,
            track_name=track.name if track else "Unknown",
            race_date=race.race_date,
            status=race.status,
            classification=classification,
            fastest_lap=fastest_lap_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADDITIONAL ENDPOINTS
# ============================================================================

@app.get("/championships")
def list_championships(
    discipline: Optional[str] = Query(None, description="Filter by discipline"),
    archived: bool = Query(False, description="Include archived championships")
):
    """List all championships with optional filtering"""
    try:
        championships = db_manager.get_all_championships()
        
        # Apply filters
        if discipline:
            championships = [c for c in championships if c.discipline == discipline]
        
        if not archived:
            championships = [c for c in championships if not c.archived]
        
        return {
            "championships": [
                ChampionshipResponse(
                    id=c.id,
                    name=c.name,
                    discipline=c.discipline,
                    season_length=c.season_length,
                    points_system=c.points_system,
                    current_season=c.current_season,
                    tier=c.tier,
                    founded_year=c.founded_year,
                    description=c.description,
                    archived=c.archived
                ) for c in championships
            ],
            "count": len(championships)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("Starting Momentum Simulation API Server...")
    print(f"Server: {API_HOST}:{API_PORT}")
    print(f"Reload: {API_RELOAD}")
    print(f"Docs: http://{API_HOST}:{API_PORT}/docs")
    
    uvicorn.run(
        "simulation:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )
