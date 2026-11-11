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

Authors: Eoin Fitzsimons
Version: 2.0.0 (Championship Management Update)
Compatible with: Python 3.8+, FastAPI 0.100+
"""

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Annotated
from datetime import datetime
import uvicorn

from momentum.database.database_manager import DatabaseManager
from momentum.database.models import Championship, Race
from momentum.services.championship_service import ChampionshipService
from momentum.services.team_service import TeamService
from momentum.services.hiring_service import HiringService
from momentum.services.progression_service import ProgressionService
from momentum.api.schemas import (
    ChampionshipCreate,
    ChampionshipResponse,
    ChampionshipDetailsResponse,
    ChampionshipScheduleResponse,
    RaceEventCreate,
    RaceEventResponse,
    RaceStatusUpdate,
    RaceResultDetailResponse,
    RecalculateStandingsResponse,
    HealthCheckResponse,
    StandingEntry,
    TeamCreate,
    TeamCreateResponse,
    TeamDetails,
    TeamUpdate,
    TeamUpdateResponse,
    TeamBudgetResponse,
    BudgetTransactionRequest,
    BudgetTransactionResponse,
    # Hiring & Contract schemas
    AvailableDriver,
    AvailableDriversResponse,
    AvailableStaff,
    AvailableStaffResponse,
    DriverContractRequest,
    DriverContractResponse,
    StaffContractRequest,
    StaffContractResponse,
    ContractReleaseRequest,
    ContractReleaseResponse,
    # Progression schemas
    SeasonProgressionRequest,
    SeasonProgressionResponse,
    DriverProgression,
)
from momentum.config import API_HOST, API_PORT, API_RELOAD

# Initialise FastAPI application
app = FastAPI(
    title="Momentum Simulation API",
    description="Multi-discipline Motorsport Management Simulator - Championship Management System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialise services
db_manager = DatabaseManager()
championship_service = ChampionshipService(db_manager)
team_service = TeamService(db_manager)
hiring_service = HiringService()
progression_service = ProgressionService()


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
            "Real-time Standings Calculation",
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
            "race_results": "GET /races/{id}/results",
        },
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    responses={500: {"description": "Health check failed"}},
)
def health_check():
    """
    Health Check Endpoint

    Verifies API and database connectivity.
    """
    try:
        stats = db_manager.get_database_stats()
        return {"status": "healthy", "database": "connected", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# ============================================================================
# DRIVER & TEAM ENDPOINTS
# ============================================================================


@app.get("/drivers", responses={500: {"description": "Database error"}})
def list_drivers(
    discipline: Annotated[
        Optional[str], Query(description="Filter by preferred discipline")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
):
    """Get list of drivers with optional filtering"""
    try:
        drivers = db_manager.get_all_drivers()

        if discipline:
            drivers = [d for d in drivers if d.preferred_discipline == discipline]

        return {
            "drivers": drivers[:limit],
            "count": len(drivers[:limit]),
            "total": len(drivers),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/teams", responses={500: {"description": "Database error"}})
def list_teams(
    discipline: Annotated[
        Optional[str], Query(description="Filter by discipline")
    ] = None,
):
    """Get list of teams with optional filtering"""
    try:
        if discipline:
            teams = db_manager.get_teams_by_discipline(discipline)
        else:
            teams = db_manager.get_all_teams()

        return {"teams": teams, "count": len(teams)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TEAM MANAGEMENT ENDPOINTS (UC-11 to UC-14)
# ============================================================================


@app.get(
    "/teams/me",
    responses={
        401: {"description": "Missing X-Player-Id header"},
        404: {"description": "No team found"},
        500: {"description": "Database error"},
    },
)
def get_player_team(
    x_player_id: Annotated[Optional[str], Header(alias="X-Player-Id")] = None,
):
    """
    UC-13: Read Player Team

    Get the authenticated player's owned team with edit permissions.
    Uses X-Player-Id as a lightweight auth header.

    Returns:
        Player's team with editable flags
    """
    if not x_player_id:
        raise HTTPException(status_code=401, detail="Missing X-Player-Id header")

    try:
        team = team_service.get_player_team(x_player_id)
        if not team:
            raise HTTPException(status_code=404, detail="No team owned by this player")
        return team
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/teams/{team_id}",
    response_model=TeamDetails,
    responses={
        404: {"description": "Team not found"},
        500: {"description": "Database error"},
    },
)
def get_team_details(team_id: int):
    """
    UC-11: Read Team Details

    Get full team profile including roster, staff, and financial information.

    Args:
        team_id: Team ID

    Returns:
        Complete team details with roster aggregation
    """
    try:
        team_details = team_service.get_team_details(team_id)
        if not team_details:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        return team_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/teams",
    response_model=TeamCreateResponse,
    status_code=201,
    responses={
        400: {"description": "Invalid team creation request"},
        500: {"description": "Database error"},
    },
)
def create_team(request: TeamCreate):
    """
    UC-12: Create New Team

    Create a new team with initial budget allocation and provisioning.
    Applies tier-based budget caps and staff limits.

    Args:
        request: Team creation parameters (name required)

    Returns:
        Created team with initial budget and limits
    """
    try:
        result = team_service.create_team(
            name=request.name,
            discipline=request.discipline,
            nationality=request.nationality,
            tier=request.tier,
            team_principal=request.team_principal,
            headquarters=request.headquarters,
            player_id=request.player_id,
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch(
    "/teams/{team_id}",
    response_model=TeamUpdateResponse,
    responses={
        403: {"description": "Permission denied"},
        409: {"description": "Conflict in update"},
        400: {"description": "Invalid update request"},
        500: {"description": "Database error"},
    },
)
def update_team(
    team_id: int,
    request: TeamUpdate,
    x_player_id: Annotated[Optional[str], Header(alias="X-Player-Id")] = None,
):
    """
    UC-14: Update Team Attributes

    Update team attributes with audit logging.
    Prevents modification of budget and tier directly.

    Args:
        team_id: Team ID
        request: Team update parameters

    Returns:
        Update confirmation with audit trail
    """
    try:
        result = team_service.update_team(
            team_id, request.model_dump(exclude_none=True), actor_id=x_player_id
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        detail = str(e)
        if "permission" in detail.lower():
            raise HTTPException(status_code=403, detail=detail)
        if "conflict" in detail.lower():
            raise HTTPException(status_code=409, detail=detail)
        raise HTTPException(status_code=400, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/teams/{team_id}/budget/allocate",
    response_model=BudgetTransactionResponse,
    responses={
        400: {"description": "Invalid budget request"},
        500: {"description": "Database error"},
    },
)
def allocate_budget(team_id: int, request: BudgetTransactionRequest):
    """
    Allocate budget to a specific category.

    Args:
        team_id: Team ID
        request: Budget allocation request

    Returns:
        Budget transaction confirmation with remaining balance
    """
    try:
        result = team_service.allocate_budget(
            team_id, request.category, request.amount, request.description or ""
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/teams/{team_id}/budget",
    response_model=TeamBudgetResponse,
    responses={
        404: {"description": "Team not found"},
        500: {"description": "Database error"},
    },
)
def get_team_budget(team_id: int):
    """
    Get current budget status and allocation breakdown.

    Args:
        team_id: Team ID

    Returns:
        Budget summary with category breakdown
    """
    try:
        budget_status = team_service.get_budget_status(team_id)
        if not budget_status:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        return budget_status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-10: CREATE CHAMPIONSHIP
# ============================================================================


@app.post(
    "/championships",
    response_model=ChampionshipResponse,
    status_code=201,
    responses={
        400: {"description": "Invalid championship request"},
        500: {"description": "Database error"},
    },
)
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
            archived=False,
        )

        # Set start date
        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        else:
            start_date = datetime.now()

        # Create championship with calendar
        if request.track_ids:
            champ_id, _ = championship_service.create_championship_season(
                championship, request.track_ids, start_date
            )
        else:
            champ_id = db_manager.create_championship(championship)

        # Retrieve created championship
        if champ_id is None:
            raise HTTPException(status_code=500, detail="Failed to create championship")
        created_champ = db_manager.get_championship(champ_id)

        if not created_champ:
            raise HTTPException(
                status_code=500, detail="Championship created but not retrievable"
            )

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
            archived=created_champ.archived,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create championship: {str(e)}"
        )


# ============================================================================
# UC-5: READ CHAMPIONSHIP DETAILS
# ============================================================================


@app.get(
    "/championships/{championship_id}",
    response_model=ChampionshipDetailsResponse,
    responses={
        404: {"description": "Championship not found"},
        500: {"description": "Database error"},
    },
)
def get_championship_details(
    championship_id: int,
    season: Annotated[
        Optional[int], Query(description="Season number (defaults to current)")
    ] = None,
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
            raise HTTPException(
                status_code=404, detail=f"Championship {championship_id} not found"
            )

        # Use current season if not specified
        target_season = season if season is not None else championship.current_season

        # Get standings
        standings = championship_service.recalculate_standings(
            championship_id, target_season
        )

        # Get calendar
        calendar = championship_service.get_championship_calendar(
            championship_id, target_season
        )

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
                archived=championship.archived,
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
                    fastest_laps=s.fastest_laps,
                )
                for s in standings
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
                    laps=r["laps"],
                )
                for r in calendar
            ],
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
    response_model=RecalculateStandingsResponse,
    responses={
        404: {"description": "Championship not found"},
        500: {"description": "Database error"},
    },
)
def recalculate_championship_standings(
    championship_id: int,
    season: Annotated[Optional[int], Query(description="Season to recalculate")] = None,
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
            raise HTTPException(
                status_code=404, detail=f"Championship {championship_id} not found"
            )

        target_season = season if season is not None else championship.current_season

        # Recalculate standings
        standings = championship_service.recalculate_standings(
            championship_id, target_season
        )

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
                    fastest_laps=s.fastest_laps,
                )
                for s in standings
            ],
            message=f"Standings recalculated for {len(standings)} drivers",
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
    status_code=201,
    responses={
        404: {"description": "Championship not found"},
        400: {"description": "Invalid race request"},
        500: {"description": "Database error"},
    },
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
            raise HTTPException(
                status_code=404, detail=f"Championship {championship_id} not found"
            )

        # Validate event
        is_valid, error_msg = championship_service.validate_race_event(
            championship_id,
            request.track_id,
            request.race_date,
            championship.current_season,
        )

        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Get current round number
        calendar = championship_service.get_championship_calendar(
            championship_id, championship.current_season
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
            status="scheduled",
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
            laps=request.laps,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-8: READ RACE SCHEDULE
# ============================================================================


@app.get(
    "/championships/{championship_id}/schedule",
    response_model=ChampionshipScheduleResponse,
    responses={
        404: {"description": "Championship not found"},
        500: {"description": "Database error"},
    },
)
def get_championship_schedule(
    championship_id: int,
    season: Annotated[Optional[int], Query(description="Season number")] = None,
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
            raise HTTPException(
                status_code=404, detail=f"Championship {championship_id} not found"
            )

        target_season = season if season is not None else championship.current_season

        calendar = championship_service.get_championship_calendar(
            championship_id, target_season
        )

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
                    laps=r["laps"],
                )
                for r in calendar
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-9: UPDATE RACE STATUS
# ============================================================================


@app.patch(
    "/races/{race_id}/status",
    responses={
        400: {"description": "Invalid status transition"},
        500: {"description": "Database error"},
    },
)
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
            race_id, request.status
        )

        if not success:
            raise HTTPException(status_code=400, detail=error_msg)

        return {
            "success": True,
            "race_id": race_id,
            "new_status": request.status,
            "message": f"Race status updated to {request.status}",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UC-4: READ RACE RESULTS
# ============================================================================


def _build_race_result_entry(result):
    """Helper to build a race result classification entry"""
    driver = db_manager.get_driver(result.driver_id)
    team = db_manager.get_team(result.team_id) if result.team_id else None

    return {
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
        "status": "DNF" if result.dnf_reason else "Finished",
    }


@app.get(
    "/races/{race_id}/results",
    response_model=RaceResultDetailResponse,
    responses={
        404: {"description": "Race not found"},
        500: {"description": "Database error"},
    },
)
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
            entry = _build_race_result_entry(result)
            classification.append(entry)

            if result.fastest_lap and not fastest_lap_info:
                driver = db_manager.get_driver(result.driver_id)
                fastest_lap_info = {
                    "driver_name": (
                        driver.name if driver else f"Driver {result.driver_id}"
                    ),
                    "time": result.time_seconds,
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
            fastest_lap=fastest_lap_info,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RACE COMPLETION & STANDINGS UPDATE
# ============================================================================


@app.post(
    "/races/{race_id}/complete",
    responses={
        404: {"description": "Race not found"},
        400: {"description": "Invalid race state"},
        500: {"description": "Database error"},
    },
)
def complete_race_and_update_standings(race_id: int):
    """
    Complete a race and automatically update championship standings.

    Updates race status to 'completed' and recalculates standings.

    Args:
        race_id: Race ID to complete

    Returns:
        Updated standings
    """
    try:
        race = db_manager.get_race(race_id)

        if not race:
            raise HTTPException(status_code=404, detail=f"Race {race_id} not found")

        # Update race status to completed
        success, error_msg = championship_service.update_race_lifecycle_status(
            race_id, "completed"
        )

        if not success:
            raise HTTPException(status_code=400, detail=error_msg)

        # Recalculate standings
        standings = championship_service.recalculate_standings(
            race.championship_id, race.season
        )

        # Return updated standings
        return {
            "success": True,
            "race_id": race_id,
            "standings": [
                StandingEntry(
                    driver_id=entry.driver_id,
                    driver_name=entry.driver_name,
                    team_id=entry.team_id,
                    team_name=entry.team_name,
                    total_points=entry.total_points,
                    wins=entry.wins,
                    podiums=entry.podiums,
                    races_started=entry.races_started,
                    dnf_count=entry.dnf_count,
                    fastest_laps=entry.fastest_laps,
                    position=entry.position,
                )
                for entry in standings
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to complete race: {str(e)}"
        )


@app.get(
    "/championships/{championship_id}/next-race",
    responses={
        404: {"description": "Championship not found"},
        500: {"description": "Database error"},
    },
)
def get_next_race(championship_id: int):
    """
    Get the next scheduled race in a championship.

    Args:
        championship_id: Championship ID

    Returns:
        Next race details or null if season complete
    """
    try:
        championship = db_manager.get_championship(championship_id)

        if not championship:
            raise HTTPException(
                status_code=404, detail=f"Championship {championship_id} not found"
            )

        # Get calendar
        calendar = championship_service.get_championship_calendar(
            championship_id, championship.current_season
        )

        # Find next scheduled race
        for race in calendar:
            if race["status"] == "scheduled":
                return {
                    "found": True,
                    "race_id": race["race_id"],
                    "round_number": race["round_number"],
                    "track_name": race["track_name"],
                    "track_country": race["track_country"],
                    "race_date": race["race_date"],
                    "laps": race["laps"],
                    "weather": race["weather_conditions"],
                }

        # No scheduled races found
        return {"found": False, "message": "No scheduled races remaining"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADDITIONAL ENDPOINTS
# ============================================================================


@app.get("/championships", responses={500: {"description": "Database error"}})
def list_championships(
    discipline: Annotated[
        Optional[str], Query(description="Filter by discipline")
    ] = None,
    archived: Annotated[
        bool, Query(description="Include archived championships")
    ] = False,
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
                    archived=c.archived,
                )
                for c in championships
            ],
            "count": len(championships),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HIRING & CONTRACT ENDPOINTS (UC-15, UC-16, UC-17, UC-18)
# ============================================================================


@app.get(
    "/drivers/available",
    response_model=AvailableDriversResponse,
    tags=["Hiring"],
    responses={500: {"description": "Database error"}},
)
def get_available_drivers(
    discipline: Annotated[
        Optional[str], Query(description="Filter by preferred discipline")
    ] = None,
    min_rating: Annotated[
        float, Query(ge=0.0, le=100.0, description="Minimum average skill rating")
    ] = 0.0,
    max_salary: Annotated[
        Optional[float], Query(description="Maximum salary budget")
    ] = None,
    sort_by: Annotated[
        str, Query(description="Sort field: rating, name, age, salary, career_points")
    ] = "rating",
    sort_order: Annotated[
        str, Query(description="Sort direction: asc or desc")
    ] = "desc",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Results per page")] = 50,
):
    """
    UC-15: Get Available Drivers for Hire

    Returns list of drivers available for contract signing. Includes:
    - Skill ratings and career statistics
    - Estimated salary based on performance
    - Pagination support
    - Discipline and rating filters

    Market includes:
    - Drivers without current team contracts
    - Active career phase drivers
    - Optional discipline specialization filter
    """
    try:
        drivers, total = hiring_service.get_available_drivers(
            discipline=discipline,
            min_rating=min_rating,
            max_salary=max_salary,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = (total + page_size - 1) // page_size

        return AvailableDriversResponse(
            drivers=[AvailableDriver(**d) for d in drivers],
            count=len(drivers),
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching available drivers: {str(e)}"
        )


@app.get(
    "/staff/available",
    response_model=AvailableStaffResponse,
    tags=["Hiring"],
    responses={500: {"description": "Database error"}},
)
def get_available_staff(
    role: Annotated[Optional[str], Query(description="Filter by staff role")] = None,
    min_rating: Annotated[
        float, Query(ge=0.0, le=100.0, description="Minimum skill rating")
    ] = 0.0,
    sort_by: Annotated[
        str, Query(description="Sort field: rating, name, role, salary")
    ] = "rating",
    sort_order: Annotated[
        str, Query(description="Sort direction: asc or desc")
    ] = "desc",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Results per page")] = 50,
):
    """
    UC-17: Get Available Staff for Hire

    Returns list of staff members available for hire. Includes:
    - Role and skill rating
    - Estimated salary by role
    - Pagination support
    - Role-based filtering

    Staff roles include:
    - Team Principal, Technical Director
    - Race Engineer, Data Analyst
    - Mechanic, Strategist
    - Aerodynamicist, Designer
    """
    try:
        staff, total = hiring_service.get_available_staff(
            role=role,
            min_rating=min_rating,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = (total + page_size - 1) // page_size

        return AvailableStaffResponse(
            staff=[AvailableStaff(**s) for s in staff],
            count=len(staff),
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching available staff: {str(e)}"
        )


@app.post(
    "/contracts/driver",
    response_model=DriverContractResponse,
    tags=["Hiring"],
    responses={
        400: {"description": "Invalid contract request"},
        500: {"description": "Database error"},
    },
)
def sign_driver_contract(request: DriverContractRequest):
    """
    UC-16: Sign Driver Contract

    Create a contract between a team and driver. Process includes:
    1. Validate driver availability
    2. Check team budget sufficiency
    3. Verify salary cap compliance
    4. Calculate signing bonus (20% of total value)
    5. Update driver and team records

    Budget Impact:
    - Immediate: Signing bonus deducted (20% of total contract)
    - Annual: Salary counted against salary cap
    - Reserve: 10% of salary cap required as buffer

    Validation:
    - Driver must be available (no current team)
    - Team budget must cover signing bonus
    - Salary cap compliance enforced
    - Contract length: 1-5 seasons
    """
    try:
        success, message, details = hiring_service.sign_driver_contract(
            team_id=request.team_id,
            driver_id=request.driver_id,
            contract_length=request.contract_length,
            salary=request.salary,
            performance_bonus=request.performance_bonus,
            start_season=request.start_season,
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return DriverContractResponse(
            driver_id=details["driver_id"],
            driver_name=details["driver_name"],
            team_id=details["team_id"],
            team_name=details["team_name"],
            contract_length=details["contract_length"],
            contract_start_season=details.get("contract_start_season"),
            contract_end_season=details.get("contract_end_season"),
            salary=details["salary"],
            performance_bonus=details["performance_bonus"],
            total_contract_value=details["total_contract_value"],
            remaining_budget=details["remaining_budget"],
            message=message,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error signing driver contract: {str(e)}"
        )


@app.post(
    "/contracts/staff",
    response_model=StaffContractResponse,
    tags=["Hiring"],
    responses={
        400: {"description": "Invalid contract request"},
        500: {"description": "Database error"},
    },
)
def sign_staff_contract(request: StaffContractRequest):
    """
    UC-18: Sign Staff Contract

    Create a contract between a team and staff member. Process includes:
    1. Validate staff availability
    2. Check team budget sufficiency
    3. Calculate signing bonus (10% of total value)
    4. Update staff and team records

    Budget Impact:
    - Immediate: Signing bonus deducted (10% of total contract)
    - Annual: Salary affects team operations budget

    Validation:
    - Staff must be available (no current team)
    - Team budget must cover signing bonus
    - Contract length: 1-5 seasons
    """
    try:
        success, message, details = hiring_service.sign_staff_contract(
            team_id=request.team_id,
            staff_id=request.staff_id,
            contract_length=request.contract_length,
            salary=request.salary,
            start_season=request.start_season,
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return StaffContractResponse(
            staff_id=details["staff_id"],
            staff_name=details["staff_name"],
            team_id=details["team_id"],
            team_name=details["team_name"],
            contract_length=details["contract_length"],
            contract_start_season=details.get("contract_start_season"),
            contract_end_season=details.get("contract_end_season"),
            salary=details["salary"],
            total_contract_value=details["total_contract_value"],
            remaining_budget=details["remaining_budget"],
            message=message,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error signing staff contract: {str(e)}"
        )


@app.post(
    "/contracts/release",
    response_model=ContractReleaseResponse,
    tags=["Hiring"],
    responses={
        400: {"description": "Invalid release request"},
        500: {"description": "Database error"},
    },
)
def release_contract(request: ContractReleaseRequest):
    """
    Release Driver or Staff from Contract

    Terminate a contract with buyout cost. Process includes:
    1. Validate personnel is contracted to team
    2. Calculate buyout cost (percentage of remaining value)
    3. Check team budget sufficiency
    4. Release personnel to market

    Buyout Calculation:
    - Driver: buyout_percentage * (annual_salary * remaining_seasons)
    - Staff: Fixed 50k EUR fee (simplified)

    Default buyout percentage: 50%
    """
    try:
        success, message, details = hiring_service.release_personnel_contract(
            team_id=request.team_id,
            personnel_id=request.personnel_id,
            personnel_type=request.personnel_type,
            buyout_percentage=request.buyout_percentage,
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return ContractReleaseResponse(
            personnel_id=details["personnel_id"],
            personnel_name=details["personnel_name"],
            team_id=details["team_id"],
            buyout_cost=details["buyout_cost"],
            remaining_budget=details["remaining_budget"],
            message=message,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error releasing contract: {str(e)}"
        )


# ============================================================================
# PROGRESSION ENDPOINTS (UC-19)
# ============================================================================


@app.post(
    "/progression/season",
    response_model=SeasonProgressionResponse,
    tags=["Progression"],
    responses={500: {"description": "Database error"}},
)
def process_season_progression(request: SeasonProgressionRequest):
    """
    UC-19: Process Season-End Driver Progression

    Apply progression to all active drivers at season end. Process includes:
    1. Calculate skill changes based on age and experience
    2. Check retirement eligibility
    3. Retire eligible drivers
    4. Recycle retired drivers as rookies

    Progression Factors:
    - Age-based curves (peak 28-32, decline 35+)
    - Experience growth (learning rate)
    - Career achievements
    - Form trends

    Retirement Triggers:
    - Age 45+: Automatic
    - Age 40-44: 10-30% probability
    - Age 35-39 with poor performance: 5-15% probability

    Recycling System:
    - Retired drivers generate new rookies (18-20 years old)
    - Reset skills to 35-55 range
    - Maintains driver pool population
    """
    try:
        results = progression_service.process_season_end_progression(
            season=request.season
        )

        # Convert results to response format
        progressions = []
        for prog in results["progressions"]:
            progressions.append(
                DriverProgression(
                    driver_id=prog["driver_id"],
                    driver_name=prog["driver_name"],
                    age=prog["age"],
                    skill_changes=prog["skill_changes"],
                    retired=prog["retired"],
                    career_phase="retired" if prog["retired"] else "active",
                )
            )

        return SeasonProgressionResponse(
            season=results["season"],
            drivers_processed=results["drivers_processed"],
            drivers_progressed=progressions,
            drivers_retired=results["summary"]["retired"],
            drivers_recycled=results["summary"]["recycled"],
            summary=results["summary"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing season progression: {str(e)}"
        )


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("Starting Momentum Simulation API Server...")
    print(f"Server: {API_HOST}:{API_PORT}")
    print(f"Reload: {API_RELOAD}")
    print(f"Docs: http://{API_HOST}:{API_PORT}/docs")

    uvicorn.run("momentum.api.app:app", host=API_HOST, port=API_PORT, reload=API_RELOAD)
