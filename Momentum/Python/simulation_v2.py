"""
Momentum Motorsport Simulation API Server (Refactored)

Clean API layer using Pydantic models and service layer for business logic.
This refactored version provides better separation of concerns and testability.

Key Improvements:
- Pydantic models for request/response validation
- Service layer for business logic
- Proper error handling
- Clean endpoint implementations
- Type safety throughout

Version: 2.0.0 (Refactored)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging

# Database and simulation imports
from database.database_manager import DatabaseManager
from disciplines.race_simulation import RaceSimulator

# API schemas and services
from api.schemas import (
    RaceSimulationRequest,
    RaceResultResponse,
    DriversListResponse,
    DriverSummary,
    TeamsListResponse,
    TeamSummary,
    HealthCheckResponse,
    DatabaseStatsResponse,
    APIInfoResponse
)
from services.simulation_service import SimulationService

# Configuration
from config import API_HOST, API_PORT, API_RELOAD

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Momentum Simulation API",
    description="Multi-discipline Motorsport Management Simulator Backend (Refactored)",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (singleton pattern)
db_manager = DatabaseManager()
race_simulator = RaceSimulator()
simulation_service = SimulationService(db_manager, race_simulator)

logger.info("Momentum API initialized successfully")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_model=APIInfoResponse)
def root():
    """API Root - System Information"""
    return APIInfoResponse(
        message="Momentum Simulation API",
        version="2.0.0",
        status="running",
        endpoints={
            "health": "/health",
            "database_stats": "/stats",
            "drivers": "/drivers",
            "teams": "/teams",
            "simulate_race": "/simulate/race"
        }
    )


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """System Health Check"""
    try:
        stats = db_manager.get_database_stats()
        return HealthCheckResponse(
            status="healthy",
            database="connected",
            stats=stats
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/stats", response_model=DatabaseStatsResponse)
def get_database_stats():
    """Database Statistics"""
    try:
        stats = db_manager.get_database_stats()
        return DatabaseStatsResponse(database_stats=stats)
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.get("/drivers", response_model=DriversListResponse)
def get_all_drivers():
    """
    Get All Drivers
    
    Retrieves a complete list of all drivers in the simulation database.
    Returns simplified driver summaries optimized for API responses.
    """
    try:
        drivers = db_manager.get_all_drivers()
        
        # Convert to DriverSummary models
        driver_summaries = [
            DriverSummary(
                id=d.id,
                name=d.name,
                nationality=d.nationality,
                age=d.age if hasattr(d, 'age') else 25,
                raw_speed=d.raw_speed if hasattr(d, 'raw_speed') else 50.0,
                consistency=d.consistency if hasattr(d, 'consistency') else 50.0,
                racecraft=d.racecraft if hasattr(d, 'racecraft') else 50.0,
                career_wins=d.career_wins if hasattr(d, 'career_wins') else 0,
                career_podiums=d.career_podiums if hasattr(d, 'career_podiums') else 0,
                career_points=d.career_points if hasattr(d, 'career_points') else 0.0,
                current_team_id=d.current_team_id if hasattr(d, 'current_team_id') else None
            )
            for d in drivers
        ]
        
        return DriversListResponse(
            drivers=driver_summaries,
            count=len(driver_summaries)
        )
    except Exception as e:
        logger.error(f"Failed to get drivers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get drivers: {str(e)}")


@app.get("/teams", response_model=TeamsListResponse)
def get_teams(discipline: Optional[str] = None):
    """
    Get Teams
    
    Retrieves teams from the database with optional discipline filtering.
    
    Args:
        discipline: Optional filter by racing discipline
    """
    try:
        if discipline:
            teams = db_manager.get_teams_by_discipline(discipline)
        else:
            # Get all teams (simplified - just get first 100)
            all_drivers = db_manager.get_all_drivers()  # Temp workaround
            teams = db_manager.get_teams_by_discipline("SINGLE_SEATER")[:100]
        
        # Convert to TeamSummary models
        team_summaries = [
            TeamSummary(
                id=t.id,
                name=t.name,
                discipline=t.discipline if hasattr(t, 'discipline') else "SINGLE_SEATER",
                nationality=t.nationality if hasattr(t, 'nationality') else "INT",
                tier=t.tier if hasattr(t, 'tier') else 2,
                budget=t.budget if hasattr(t, 'budget') else 50000000.0
            )
            for t in teams
        ]
        
        return TeamsListResponse(
            teams=team_summaries,
            count=len(team_summaries)
        )
    except Exception as e:
        logger.error(f"Failed to get teams: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get teams: {str(e)}")


@app.post("/simulate/race", response_model=RaceResultResponse)
async def simulate_race(request: RaceSimulationRequest):
    """
    Simulate Race
    
    Runs a Monte Carlo race simulation with the specified parameters.
    Delegates to service layer for business logic.
    
    Args:
        request: RaceSimulationRequest with discipline, drivers, track
    
    Returns:
        RaceResultResponse with complete race results
    """
    try:
        logger.info(f"Received race simulation request: {request.discipline}")
        
        result = simulation_service.simulate_race(
            discipline=request.discipline,
            race_id=request.race_id,
            driver_ids=request.drivers,
            track_id=request.track_id
        )
        
        logger.info(f"Race simulation completed successfully")
        return result
        
    except ValueError as e:
        # Validation errors (bad input)
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Simulation errors
        logger.error(f"Simulation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Momentum API server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "simulation_v2:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )
