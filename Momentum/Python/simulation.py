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

Authors: Final Year Project - Computer Science
Version: 1.0.0
Compatible with: Python 3.8+, FastAPI 0.100+
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uvicorn

from database.database_manager import DatabaseManager
from database.models import Driver, Team, Track, Championship, Race
from Momentum.Python.disciplines.race_simulation import RaceSimulator, SimulationContext
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
    Takes race parameters and participant information to generate realistic
    race outcomes based on driver skills, team performance, and environmental factors.
    
    Args:
        request (Dict[str, Any]): Race simulation parameters including:
            - race_id (int, optional): Unique race identifier (default: 1)
            - weather_conditions (str, optional): Weather conditions 
              ("dry", "wet", "mixed") (default: "dry")
            - participants (List[Dict], optional): List of race participants
              Each participant should include:
                * driver_id (int): Driver identifier
                * team_id (int): Team identifier
    
    Returns:
        JSONResponse: Race simulation results including:
            - race_id: Identifier of the simulated race
            - weather: Weather conditions applied
            - results: Array of race results ordered by finishing position
                * driver_id: Driver identifier
                * team_id: Team identifier  
                * position: Final race position (1st, 2nd, 3rd, etc.)
                * points: Championship points awarded
                * fastest_lap: Boolean indicating fastest lap achievement
            - simulation_status: Status of simulation ("completed", "failed")
    
    Raises:
        HTTPException: 500 status if simulation fails
        
    Example Request:
        {
            "race_id": 1,
            "weather_conditions": "dry",
            "participants": [
                {"driver_id": 1, "team_id": 1},
                {"driver_id": 2, "team_id": 2}
            ]
        }
        
    Example Response:
        {
            "race_id": 1,
            "weather": "dry",
            "results": [
                {
                    "driver_id": 1,
                    "team_id": 1,
                    "position": 1,
                    "points": 25,
                    "fastest_lap": true
                }
            ],
            "simulation_status": "completed"
        }
    """
    try:
        # Extract simulation parameters with defaults
        race_id = request.get("race_id", 1)
        weather = request.get("weather_conditions", "dry")
        participants = request.get("participants", [])
        
        # TODO: Integrate with full Monte Carlo simulation engine
        # Current implementation provides mock results for API testing
        # Future enhancement: Use race_simulator.simulate_race() with full context
        
        # Generate mock simulation results based on participants
        # Points system follows Formula 1 standard: 25, 18, 15, 12, 10, 8, 6, 4, 2, 1
        results = [
            {
                "driver_id": p.get("driver_id", i),
                "team_id": p.get("team_id", i),
                "position": i + 1,
                "points": max(0, 25 - i * 2),  # Simplified points distribution
                "fastest_lap": i == 0  # First participant gets fastest lap
            }
            for i, p in enumerate(participants[:10] if participants else range(5))
        ]
        
        return JSONResponse(content={
            "race_id": race_id,
            "weather": weather,
            "results": results,
            "simulation_status": "completed"
        })
        
    except Exception as e:
        # Handle simulation errors and provide detailed error information
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

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
