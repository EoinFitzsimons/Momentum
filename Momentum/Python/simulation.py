"""
Momentum Motorsport Simulation API Server

This is the main entry point for the Momentum multi-discipline motorsport management
simulation backend. The system provides a comprehensive racing simulation engine that
supports multiple racing disciplines including Formula Racing, Rally, Endurance, and
Street Racing.

Key Features:
- Monte Carlo-based race simulation engine
- Multi-discipline motorsport support (Formula, Rally, Endurance, Street)
- RESTful API for frontend integration
- SQLite database with comprehensive motorsport data models
- Real-time race outcome prediction based on driver/team attributes
- Championship management and standings tracking

API Endpoints:
- GET /: System information and available endpoints
- GET /health: Health check and system status
- GET /stats: Database statistics
- GET /drivers: Retrieve all drivers
- GET /teams: Retrieve teams (filterable by discipline)
- POST /simulate/race: Run race simulations
- POST /season/create: Create new championship season
- POST /season/next-race: Simulate next race in season
- GET /season/state: Get current season state
- GET /season/standings: Get championship standings

Authors: Final Year Project - Computer Science
Version: 1.0.0
Compatible with: Python 3.8+, FastAPI 0.100+
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import uuid
import uvicorn

from database.database_manager import DatabaseManager
from database.models import Driver, Team, Track, Championship, Race
from disciplines.race_simulation import RaceSimulator, SimulationContext
from systems.game_loop import GameLoop
from config import API_HOST, API_PORT, API_RELOAD

app = FastAPI(
    title="Momentum Simulation API",
    description="Multi-discipline Motorsport Management Simulator Backend",
    version="1.0.0"
)

# Enable CORS middleware for cross-origin requests
# This allows the Unity frontend (or web frontend) to communicate with the API
# WARNING: allow_origins=["*"] is permissive for development only
# In production, specify exact origins: ["http://localhost:3000", "https://yourdomain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allow all headers
)

# Initialize global application instances
# These are shared across all requests for efficiency and state management
db_manager = DatabaseManager()    # Handles all database operations and connections
race_simulator = RaceSimulator()  # Core Monte Carlo simulation engine
game_loop = GameLoop(db_manager)  # Championship and season management

@app.get("/")
def root():
    """
    API Root Endpoint - System Information
    
    Provides basic information about the Momentum Simulation API including
    version, status, and available endpoints. This serves as a health check
    and documentation entry point for API consumers.
    
    Returns:
        dict: API metadata including:
            - message: API name and purpose
            - version: Current API version
            - status: Current operational status
            - endpoints: Dictionary of available API endpoints
    
    Example Response:
        {
            "message": "Momentum Simulation API",
            "version": "1.0.0", 
            "status": "running",
            "endpoints": {...}
        }
    """
    return {
        "message": "Momentum Simulation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "database_stats": "/stats",
            "drivers": "/drivers",
            "teams": "/teams",
            "simulate_race": "/simulate/race"
        }
    }

@app.get("/health")
def health_check():
    """
    System Health Check Endpoint
    
    Performs a comprehensive health check of the simulation system including
    database connectivity and basic system statistics. Used for monitoring
    and ensuring the API is operational.
    
    Returns:
        dict: Health status information including:
            - status: Overall system health ("healthy" or "unhealthy")
            - database: Database connection status
            - stats: Current database table counts
    
    Raises:
        HTTPException: 500 status if health check fails
        
    Example Response:
        {
            "status": "healthy",
            "database": "connected",
            "stats": {"drivers": 25, "teams": 12, "races": 100}
        }
    """
    try:
        # Attempt to retrieve database statistics as a connectivity test
        stats = db_manager.get_database_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        # If any error occurs, the system is considered unhealthy
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/stats")
def get_database_stats():
    """
    Database Statistics Endpoint
    
    Retrieves comprehensive statistics about the current state of the
    simulation database including record counts for all major entities.
    Useful for system monitoring and data validation.
    
    Returns:
        JSONResponse: Database statistics including:
            - drivers: Number of driver records
            - teams: Number of team records  
            - tracks: Number of track records
            - championships: Number of championship records
            - races: Number of race records
            - race_results: Number of race result records
    
    Raises:
        HTTPException: 500 status if database query fails
        
    Example Response:
        {
            "database_stats": {
                "drivers": 50,
                "teams": 20,
                "tracks": 15,
                "championships": 4,
                "races": 200,
                "race_results": 1500
            }
        }
    """
    try:
        # Query database for comprehensive statistics across all tables
        stats = db_manager.get_database_stats()
        return JSONResponse(content={"database_stats": stats})
    except Exception as e:
        # Handle any database connection or query errors
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/drivers")
def get_all_drivers():
    """
    Get All Drivers Endpoint
    
    Retrieves a complete list of all drivers in the simulation database.
    Each driver record includes comprehensive information about their
    attributes, career statistics, and current team assignment.
    
    Returns:
        JSONResponse: Complete driver information including:
            - drivers: Array of driver objects with full attributes
                * id: Unique driver identifier
                * name: Driver's full name
                * nationality: Driver's country of origin
                * skill, consistency, aggression, racecraft, adaptability: Performance attributes (0.0-1.0)
                * career_wins, career_podiums, career_points: Career statistics
                * current_team_id: ID of current team (if assigned)
                * biography: Driver background information
            - count: Total number of drivers returned
    
    Raises:
        HTTPException: 500 status if database query fails
        
    Example Response:
        {
            "drivers": [
                {
                    "id": 1,
                    "name": "Lewis Hamilton",
                    "nationality": "GBR",
                    "skill": 0.95,
                    "consistency": 0.90,
                    "career_wins": 103,
                    ...
                }
            ],
            "count": 50
        }
    """
    try:
        # Retrieve all driver records from database
        drivers = db_manager.get_all_drivers()
        
        # Convert driver objects to dictionaries for JSON serialization
        return JSONResponse(content={
            "drivers": [driver.__dict__ for driver in drivers],
            "count": len(drivers)
        })
    except Exception as e:
        # Handle database errors and provide meaningful error messages
        raise HTTPException(status_code=500, detail=f"Failed to get drivers: {str(e)}")


@app.get("/drivers/{driver_id}")
def get_driver(driver_id: int):
    """
    Get single driver by ID (UC-1)

    Validation:
      - driver_id must be a positive integer (400)
      - driver must exist (404)
      - driver must be eligible (409) e.g. not retired

    Errors:
      - Database read failure -> 503 with diagnostic id
    """
    if not isinstance(driver_id, int) or driver_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid driver_id; must be positive integer")

    try:
        db = DatabaseManager()
        driver = db.get_driver(driver_id)
    except Exception:
        diag = uuid.uuid4().hex
        raise HTTPException(status_code=503, detail=f"Database read failure (diag={diag})")

    if driver is None:
        raise HTTPException(status_code=404, detail=f"Driver with id {driver_id} not found")

    # Simple eligibility rule: career_phase != 'retired'
    try:
        if getattr(driver, 'career_phase', None) == 'retired':
            raise HTTPException(status_code=409, detail=f"Driver {driver_id} is ineligible: retired")
    except HTTPException:
        raise
    except Exception:
        # ignore unexpected attribute errors and continue
        pass

    # Return full driver payload (dataclass -> dict)
    try:
        payload = asdict(driver)
    except Exception:
        # fallback: use __dict__
        payload = getattr(driver, '__dict__', {})

    return JSONResponse(content={"driver": payload})


@app.get("/races/{race_id}/config")
def get_race_config(race_id: int):
    """
    Return full event/race configuration (UC-2)

    Validates race_id and composes configuration from race, track and championship.
    Returns partial:true if fields are missing.
    """
    if not isinstance(race_id, int) or race_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid race_id; must be positive integer")

    db = DatabaseManager()
    try:
        race = db.get_race(race_id)
    except Exception:
        diag = uuid.uuid4().hex
        raise HTTPException(status_code=503, detail=f"Database read failure (diag={diag})")

    partial = False
    warnings = []

    if race is None:
        # try fallback temporary race generator
        race = db.get_race_by_id(race_id)
        if race is None:
            raise HTTPException(status_code=404, detail=f"Race with id {race_id} not found")
        partial = True
        warnings.append("Race record missing in DB; using temporary placeholder")

    # Track
    try:
        track = db.get_track(getattr(race, 'track_id', 1))
        if track is None:
            partial = True
            warnings.append("Track data missing for race")
            track_payload = {}
        else:
            # convert dataclass to dict where possible
            try:
                track_payload = asdict(track)
            except Exception:
                track_payload = getattr(track, '__dict__', {})
    except Exception:
        diag = uuid.uuid4().hex
        raise HTTPException(status_code=503, detail=f"Database read failure (diag={diag})")

    # Championship / ruleset
    champ_payload = {}
    try:
        champ = db.get_championship(getattr(race, 'championship_id', 1))
        if champ is None:
            partial = True
            warnings.append("Championship data missing for race")
        else:
            try:
                champ_payload = asdict(champ)
            except Exception:
                champ_payload = getattr(champ, '__dict__', {})
    except Exception:
        diag = uuid.uuid4().hex
        raise HTTPException(status_code=503, detail=f"Database read failure (diag={diag})")

    config = {
        "race_id": race_id,
        "track": track_payload,
        "race": {
            "laps": getattr(race, 'total_laps', getattr(race, 'laps', None)),
            "scheduled_date": getattr(race, 'race_date', None),
            "weather_default": getattr(race, 'weather_conditions', 'dry'),
            "status": getattr(race, 'status', 'scheduled')
        },
        "championship": champ_payload,
        "partial": partial,
        "warnings": warnings
    }

    return JSONResponse(content={"configuration": config})


@app.post("/races/{race_id}/results")
def post_race_results(race_id: int, request: Request):
    """
    Persist race results atomically and enqueue standings recalculation (UC-3)

    Expects JSON body: { "results": [ { driver_id, team_id, position, points, fastest_lap?, dnf_reason?, grid_position? }, ... ] }
    """
    if not isinstance(race_id, int) or race_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid race_id; must be positive integer")

    try:
        payload = request.json() if hasattr(request, 'json') else None
    except Exception:
        # For FastAPI Request we need to read async; but function is sync so use .json() via starlette
        payload = None

    # FastAPI will pass dict directly when using function param typing; support both
    if payload is None:
        try:
            payload = request._body if hasattr(request, '_body') else {}
        except Exception:
            payload = {}

    # Accept either dict or object created by FastAPI body binding
    if isinstance(payload, bytes):
        try:
            import json as _json
            payload = _json.loads(payload.decode('utf-8'))
        except Exception:
            payload = {}

    if not isinstance(payload, dict):
        # Try to use request.json() coroutine
        try:
            import asyncio
            payload = asyncio.get_event_loop().run_until_complete(request.json())
        except Exception:
            payload = {}

    results = payload.get('results') if isinstance(payload, dict) else None
    if not isinstance(results, list) or len(results) == 0:
        raise HTTPException(status_code=400, detail="Invalid payload: 'results' must be a non-empty list")

    db = DatabaseManager()
    # Check race status if exists
    try:
        race = db.get_race(race_id)
        if race is not None and getattr(race, 'status', None) == 'completed':
            raise HTTPException(status_code=409, detail=f"Race {race_id} is already finalised")
    except HTTPException:
        raise
    except Exception:
        # ignore and proceed (fallbacks below)
        race = None

    # Validate each result entry minimally
    for idx, r in enumerate(results):
        if not isinstance(r, dict):
            raise HTTPException(status_code=400, detail=f"Invalid result at index {idx}: must be object")
        required = ['driver_id', 'team_id', 'position', 'points']
        for field in required:
            if field not in r:
                raise HTTPException(status_code=400, detail=f"Missing field '{field}' in result at index {idx}")

    # Persist atomically using a single connection/transaction
    try:
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            # Insert/replace each result
            for r in results:
                cur.execute(
                    "INSERT OR REPLACE INTO race_results (race_id, driver_id, team_id, position, points, fastest_lap, dnf_reason, grid_position) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        race_id,
                        int(r.get('driver_id')),
                        int(r.get('team_id')),
                        int(r.get('position')),
                        int(r.get('points')),
                        1 if r.get('fastest_lap') else 0,
                        r.get('dnf_reason'),
                        int(r.get('grid_position', 1))
                    )
                )

            # Mark race completed if races table exists
            try:
                cur.execute("UPDATE races SET status = ? WHERE id = ?", ('completed', race_id))
            except Exception:
                # ignore if races table not present or other issue
                pass

            conn.commit()
        finally:
            conn.close()

    except Exception as e:
        diag = uuid.uuid4().hex
        raise HTTPException(status_code=500, detail=f"Failed to persist results (diag={diag}): {str(e)}")

    # Trigger standings recalculation (synchronous minimal implementation)
    try:
        # If race had championship_id, calculate standings for it; fallback to 1
        championship_id = getattr(race, 'championship_id', 1) if race is not None else 1
        season = getattr(race, 'season', getattr(race, 'season', 2025)) if race is not None else 2025
        standings = db.get_championship_standings(championship_id, season)
    except Exception:
        standings = []

    return JSONResponse(content={"status": "ok", "race_id": race_id, "standings": standings})

@app.get("/teams")
def get_teams(discipline: Optional[str] = None):
    """
    Get Teams Endpoint
    
    Retrieves teams from the simulation database, with optional filtering
    by motorsport discipline. Teams represent the organizational entities
    that employ drivers and compete in championships.
    
    Args:
        discipline (Optional[str]): Filter teams by racing discipline.
            Valid values: "formula", "rally", "endurance", "street"
            If None, returns teams from all disciplines.
    
    Returns:
        JSONResponse: Team information including:
            - teams: Array of team objects with full attributes
                * id: Unique team identifier
                * name: Team name
                * nationality: Team's country of origin
                * discipline: Racing discipline (formula/rally/endurance/street)
                * tier: Performance tier (tier1/tier2/tier3)
                * budget: Annual budget in millions
                * headquarters: Team's base location
                * team_principal: Name of team leader
                * total_wins, total_podiums, championships: Career statistics
                * biography: Team background information
            - count: Number of teams returned
            - discipline: Applied discipline filter (if any)
    
    Raises:
        HTTPException: 500 status if database query fails
        
    Example Response:
        {
            "teams": [
                {
                    "id": 1,
                    "name": "Mercedes AMG F1 Team",
                    "nationality": "GER",
                    "discipline": "formula",
                    "tier": "tier1",
                    "budget": 400.0,
                    ...
                }
            ],
            "count": 12,
            "discipline": "formula"
        }
    """
    try:
        if discipline:
            # Filter teams by specific discipline
            teams = db_manager.get_teams_by_discipline(discipline)
        else:
            # Get all teams across all disciplines
            # Note: This requires implementing get_all_teams method in DatabaseManager
            # For now, we'll get teams from all disciplines
            all_teams = []
            disciplines = ["formula", "rally", "endurance", "street"]
            for disc in disciplines:
                teams_in_discipline = db_manager.get_teams_by_discipline(disc)
                all_teams.extend(teams_in_discipline)
            teams = all_teams
        
        # Convert team objects to dictionaries for JSON serialization
        return JSONResponse(content={
            "teams": [team.__dict__ for team in teams],
            "count": len(teams),
            "discipline": discipline
        })
    except Exception as e:
        # Handle database errors and provide meaningful error messages
        raise HTTPException(status_code=500, detail=f"Failed to get teams: {str(e)}")

@app.post("/simulate/race")
def simulate_race(request: Dict[str, Any]):
    """
    Race Simulation Endpoint
    
    Executes Monte Carlo-based race simulations using the core simulation engine.
    Takes race parameters and generates realistic race outcomes based on driver skills,
    team performance, track characteristics, and environmental factors.
    
    Args:
        request (Dict[str, Any]): Race simulation parameters including:
            - discipline (str, required): Racing discipline 
              ("SINGLE_SEATER", "PRODUCTION_TOURING", "RALLY_STAGE", etc.)
            - track_id (int, required): ID of the track/circuit to race on
            - num_laps (int, optional): Number of laps (default: 50)
            - weather_conditions (str, optional): Weather conditions 
              ("dry", "wet", "mixed") (default: "dry")
    
    Returns:
        JSONResponse: Race simulation results including:
            - track: Track name and information
            - discipline: Racing discipline
            - weather: Weather conditions applied
            - num_laps: Number of laps raced
            - results: Array of race results ordered by finishing position
                * driver: Driver name
                * team: Team name
                * position: Final race position
                * points: Championship points awarded
                * fastest_lap: Boolean indicating fastest lap achievement
            - simulation_status: Status of simulation
    
    Raises:
        HTTPException: 400 if required parameters missing
        HTTPException: 404 if track not found or no teams in discipline
        HTTPException: 500 if simulation fails
        
    Example Request:
        {
            "discipline": "SINGLE_SEATER",
            "track_id": 1,
            "num_laps": 50,
            "weather_conditions": "dry"
        }
    """
    try:
        # Extract required parameters
        discipline = request.get("discipline")
        track_id = request.get("track_id")
        
        if not discipline or not track_id:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameters: discipline and track_id are required"
            )
        
        # Extract optional parameters
        num_laps = request.get("num_laps", 50)
        weather = request.get("weather_conditions", "dry")
        
        # Map weather to factor
        weather_map = {"dry": 1.0, "wet": 0.7, "mixed": 0.85}
        weather_factor = weather_map.get(weather.lower(), 1.0)
        
        # Initialize database manager
        db = DatabaseManager()
        
        # Load track
        track = db.get_track_by_id(track_id)
        if not track:
            raise HTTPException(status_code=404, detail=f"Track with ID {track_id} not found")
        
        # Load teams for this discipline
        teams_list = db.get_teams_by_discipline(discipline)
        if not teams_list:
            raise HTTPException(
                status_code=404,
                detail=f"No teams found for discipline: {discipline}"
            )
        
        # Get up to 20 teams for the race
        selected_teams = teams_list[:20]
        
        # Get drivers for selected teams
        all_drivers = []
        teams_dict = {}
        
        for team in selected_teams:
            teams_dict[team.id] = team
            # Get drivers for this team
            drivers = db.get_drivers_by_team(team.id)
            if drivers:
                all_drivers.extend(drivers[:2])  # Max 2 drivers per team
        
        if not all_drivers:
            raise HTTPException(
                status_code=404,
                detail=f"No drivers found for teams in discipline: {discipline}"
            )
        
        # Create a Race object for the simulation
        race = Race(
            id=1,
            name=f"{track.name} Race",
            track_id=track_id,
            championship_id=1,
            discipline=discipline,
            scheduled_date="2025-10-23",
            status="scheduled",
            laps=num_laps
        )
        
        # Create simulation context
        context = SimulationContext(
            race=race,
            track=track,
            drivers=all_drivers,
            teams=teams_dict,
            weather_factor=weather_factor
        )
        
        # Run simulation
        simulator = RaceSimulator()
        race_results = simulator.simulate_race(context)
        
        # Format results for API response
        formatted_results = []
        for result in race_results:
            driver = next((d for d in all_drivers if d.id == result.driver_id), None)
            team = teams_dict.get(result.team_id)
            
            formatted_results.append({
                "position": result.position,
                "driver": f"{driver.first_name} {driver.last_name}" if driver else "Unknown",
                "team": team.name if team else "Unknown",
                "driver_id": result.driver_id,
                "team_id": result.team_id,
                "points": result.points,
                "fastest_lap": result.fastest_lap,
                "status": result.status
            })
        
        return JSONResponse(content={
            "track": track.name,
            "discipline": discipline,
            "weather": weather,
            "num_laps": num_laps,
            "num_participants": len(all_drivers),
            "results": formatted_results,
            "simulation_status": "completed"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        # Handle simulation errors and provide detailed error information
        import traceback
        error_detail = f"Simulation failed: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/test")
def test_endpoint():
    """
    Legacy Test Endpoint
    
    Simple test endpoint for basic API connectivity verification.
    Returns a success message to confirm the API server is responding
    to requests. Useful for initial setup testing and debugging.
    
    Returns:
        JSONResponse: Simple success confirmation message
        
    Example Response:
        {
            "message": "Simulation test successful."
        }
    """
    return JSONResponse(content={"message": "Simulation test successful."})

# =============================================================================
# GAME LOOP / CHAMPIONSHIP ENDPOINTS
# =============================================================================

@app.post("/season/create")
def create_season(request: Dict[str, Any]):
    """
    Create New Championship Season
    
    Initializes a new championship season for a specified racing discipline.
    This endpoint creates a race calendar with the specified number of races,
    selects tracks appropriate for the discipline, and sets up the initial
    championship standings.
    
    Request Body:
        discipline (str): Racing discipline (e.g., "single_seater", "rally_stage")
        num_races (int, optional): Number of races in the season (default: 10)
        season_year (int, optional): Season year (default: 2025)
    
    Returns:
        JSONResponse: Season state including:
            - season_year: Year of the season
            - championship_id: Database ID of the championship
            - championship_name: Name of the championship
            - discipline: Racing discipline
            - current_round: Current round number (starts at 1)
            - total_rounds: Total number of races
            - races_completed: List of completed race details
            - races_remaining: List of upcoming race details
            - driver_standings: Current driver championship standings
            - team_standings: Current team championship standings
            - is_season_complete: Whether the season has finished
    
    Raises:
        HTTPException 400: Invalid discipline or parameters
        HTTPException 500: Database or initialization error
    
    Example Request:
        POST /season/create
        {
            "discipline": "single_seater",
            "num_races": 12,
            "season_year": 2025
        }
    
    Example Response:
        {
            "season_year": 2025,
            "championship_name": "Single Seater Championship",
            "discipline": "single_seater",
            "total_rounds": 12,
            "races_remaining": [
                {
                    "race_id": 1,
                    "round_number": 1,
                    "track_name": "Silverstone Circuit",
                    "race_date": "2025-03-01"
                },
                ...
            ],
            "driver_standings": [],
            "team_standings": []
        }
    """
    try:
        discipline = request.get("discipline")
        num_races = request.get("num_races", 10)
        season_year = request.get("season_year", 2025)
        
        if not discipline:
            raise HTTPException(status_code=400, detail="Missing required field: discipline")
        
        # Create the new season
        game_loop.create_season(
            discipline=discipline,
            num_races=num_races,
            season_year=season_year
        )
        
        # Convert to dictionary for JSON response
        return JSONResponse(content=game_loop.get_season_state())
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create season: {str(e)}")

@app.post("/season/next-race")
def simulate_next_race(request: Dict[str, Any]):
    """
    Simulate Next Race in Season
    
    Simulates the next scheduled race in the current championship season.
    This runs the full race simulation, stores results in the database,
    updates driver and team statistics, recalculates championship standings,
    and checks if the season has been completed.
    
    Request Body:
        weather (str, optional): Weather conditions (default: "dry")
            Options: "dry", "wet", "mixed"
        num_laps (int, optional): Number of laps to simulate (default: 50)
    
    Returns:
        JSONResponse: Race results and updated season state including:
            - race_info: Details about the race that was simulated
            - results: List of race results (position, driver, team, points)
            - season_update: Updated season state with new standings
            - championship_leader: Current championship leader
            - season_complete: Whether this was the final race
            - champion: Champion information (if season complete)
    
    Raises:
        HTTPException 400: No active season or season already complete
        HTTPException 500: Simulation or database error
    
    Example Request:
        POST /season/next-race
        {
            "weather": "dry",
            "num_laps": 55
        }
    
    Example Response:
        {
            "race_info": {
                "race_id": 1,
                "round_number": 1,
                "track_name": "Silverstone Circuit",
                "weather": "dry",
                "laps": 55
            },
            "results": [
                {
                    "position": 1,
                    "driver_name": "Lewis Hamilton",
                    "team_name": "Mercedes AMG",
                    "points": 25,
                    "fastest_lap": "1:27.123"
                },
                ...
            ],
            "season_update": {
                "current_round": 2,
                "total_rounds": 12,
                "races_completed": 1
            },
            "championship_leader": {
                "driver_name": "Lewis Hamilton",
                "team_name": "Mercedes AMG",
                "points": 25
            },
            "season_complete": false
        }
    """
    try:
        weather = request.get("weather", "dry")
        num_laps = request.get("num_laps", 50)
        
        # Check if there's an active season
        if game_loop.current_season is None:
            raise HTTPException(
                status_code=400,
                detail="No active season. Please create a season first using POST /season/create"
            )
        
        # Check if season is already complete
        if game_loop.current_season.is_season_complete:
            raise HTTPException(
                status_code=400,
                detail="Season is complete. Create a new season to continue."
            )
        
        # Simulate the next race
        result = game_loop.simulate_next_race(weather=weather, num_laps=num_laps)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate race: {str(e)}")

@app.get("/season/state")
def get_season_state():
    """
    Get Current Season State
    
    Retrieves the complete state of the current championship season including
    race calendar, standings, and progress information. Returns null if no
    season is currently active.
    
    Returns:
        JSONResponse: Complete season state or null if no active season:
            - season_year: Year of the season
            - championship_id: Database ID
            - championship_name: Championship name
            - discipline: Racing discipline
            - current_round: Current round number
            - total_rounds: Total races in season
            - races_completed: List of finished races with results
            - races_remaining: List of upcoming races
            - driver_standings: Top 10 driver standings (or fewer if less than 10)
            - team_standings: Top 10 team standings (or fewer if less than 10)
            - is_season_complete: Whether season has finished
            - champion_driver_id: Champion driver ID (if complete)
            - champion_team_id: Champion team ID (if complete)
    
    Example Response (Active Season):
        {
            "season_year": 2025,
            "championship_name": "Single Seater Championship",
            "current_round": 5,
            "total_rounds": 12,
            "races_completed": [...],
            "races_remaining": [...],
            "driver_standings": [
                {
                    "position": 1,
                    "driver_name": "Max Verstappen",
                    "team_name": "Red Bull Racing",
                    "points": 110,
                    "wins": 3,
                    "podiums": 4,
                    "races_completed": 4
                },
                ...
            ],
            "is_season_complete": false
        }
    
    Example Response (No Active Season):
        {
            "season": null,
            "message": "No active season"
        }
    """
    try:
        if game_loop.current_season is None:
            return JSONResponse(content={
                "season": None,
                "message": "No active season. Create one using POST /season/create"
            })
        
        return JSONResponse(content=game_loop.get_season_state())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve season state: {str(e)}")

@app.get("/season/standings")
def get_standings():
    """
    Get Championship Standings
    
    Retrieves detailed championship standings for both drivers and teams
    in the current active season. Returns more detailed information than
    the standings included in the season state endpoint.
    
    Returns:
        JSONResponse: Championship standings or error if no active season:
            - driver_standings: Complete driver standings list with:
                - position: Championship position
                - driver_id: Database ID
                - driver_name: Full name
                - team_id: Team database ID
                - team_name: Team name
                - points: Championship points
                - wins: Number of victories
                - podiums: Number of podium finishes
                - races_completed: Races participated in
                - best_finish: Best finishing position
            - team_standings: Complete team standings list with similar structure
            - season_info: Basic season information (year, discipline, progress)
    
    Raises:
        HTTPException 400: No active season
        HTTPException 500: Database or calculation error
    
    Example Response:
        {
            "season_info": {
                "season_year": 2025,
                "championship_name": "Single Seater Championship",
                "current_round": 5,
                "total_rounds": 12
            },
            "driver_standings": [
                {
                    "position": 1,
                    "driver_name": "Max Verstappen",
                    "team_name": "Red Bull Racing",
                    "points": 110,
                    "wins": 3,
                    "podiums": 4,
                    "races_completed": 4,
                    "best_finish": 1
                },
                ...
            ],
            "team_standings": [...]
        }
    """
    try:
        if game_loop.current_season is None:
            raise HTTPException(
                status_code=400,
                detail="No active season. Create one using POST /season/create"
            )
        
        season_state = game_loop.current_season
        
        return JSONResponse(content={
            "season_info": {
                "season_year": season_state.season_year,
                "championship_name": season_state.championship_name,
                "discipline": season_state.discipline,
                "current_round": season_state.current_round,
                "total_rounds": season_state.total_rounds,
                "is_season_complete": season_state.is_season_complete
            },
            "driver_standings": [
                {
                    "position": idx + 1,
                    "driver_id": standing.driver_id,
                    "driver_name": standing.driver_name,
                    "team_id": standing.team_id,
                    "team_name": standing.team_name,
                    "points": standing.points,
                    "wins": standing.wins,
                    "podiums": standing.podiums,
                    "races_completed": standing.races_completed,
                    "best_finish": standing.best_finish
                }
                for idx, standing in enumerate(season_state.driver_standings)
            ],
            "team_standings": [
                {
                    "position": idx + 1,
                    "team_id": standing.team_id,
                    "team_name": standing.team_name,
                    "points": standing.points,
                    "wins": standing.wins,
                    "podiums": standing.podiums,
                    "races_completed": standing.races_completed,
                    "best_finish": standing.best_finish
                }
                for idx, standing in enumerate(season_state.team_standings)
            ]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve standings: {str(e)}")

# Server startup configuration
# This block only executes when the file is run directly (not imported)
if __name__ == "__main__":
    """
    Main Server Startup
    
    Starts the FastAPI server using Uvicorn ASGI server with configuration
    loaded from config.py. The server supports hot-reloading during development
    and provides automatic API documentation at /docs and /redoc.
    
    Configuration:
        - host: Server bind address (from config.API_HOST)
        - port: Server port (from config.API_PORT)  
        - reload: Auto-reload on file changes (from config.API_RELOAD)
    
    Access Points:
        - API: http://localhost:8000/
        - Interactive Docs: http://localhost:8000/docs
        - Alternative Docs: http://localhost:8000/redoc
    
    Usage:
        python simulation.py
    """
    uvicorn.run(
        "simulation:app",    # Module:application pattern for Uvicorn
        host=API_HOST,       # Bind address (typically 127.0.0.1 or 0.0.0.0)
        port=API_PORT,       # Port number (typically 8000)
        reload=API_RELOAD    # Enable auto-reload for development
    )
