"""
API Schemas - Pydantic Models for Request/Response Validation

This module defines Pydantic models for all API endpoints, providing:
- Automatic request validation
- Type safety
- API documentation (OpenAPI/Swagger)
- Serialization/deserialization

All models follow REST best practices with clear naming and documentation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================================
# RACE SIMULATION SCHEMAS
# ============================================================================

class RaceSimulationRequest(BaseModel):
    """
    Request model for POST /simulate/race

    Defines the parameters needed to simulate a race including discipline,
    track, and participating drivers.
    """
    discipline: str = Field(
        ...,
        description="Racing discipline",
        examples=[
            "SINGLE_SEATER",
            "RALLY_STAGE",
            "ENDURANCE",
            "PRODUCTION_TOURING"]
    )
    race_id: int = Field(
        default=0,
        description="Race ID to simulate. Use 0 to create a new race.",
        ge=0
    )
    drivers: List[int] = Field(
        default=[],
        description="List of driver IDs to include in the race. Empty list uses all available drivers."
    )
    track_id: Optional[int] = Field(
        default=None,
        description="Track ID to use for simulation. If not specified, a random track for the discipline will be selected."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "discipline": "SINGLE_SEATER",
                "race_id": 0,
                "drivers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "track_id": 1
            }]
        }
    }


class DriverResult(BaseModel):
    """Individual driver result in a race"""
    driver_id: int
    driver_name: str
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    position: int
    finish_time: Optional[str] = None
    points: int = 0
    status: str = "FINISHED"  # FINISHED, DNF, DSQ


class RaceResultResponse(BaseModel):
    """
    Response model for race simulation results

    Contains the complete race outcome including all driver results,
    simulation metadata, and performance statistics.
    """
    race_id: int
    discipline: str
    track_id: Optional[int] = None
    track_name: Optional[str] = None
    results: List[DriverResult]
    simulation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional simulation information (iterations, seed, etc.)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "race_id": 1,
                "discipline": "SINGLE_SEATER",
                "track_id": 1,
                "track_name": "Silverstone Circuit",
                "results": [
                    {
                        "driver_id": 1,
                        "driver_name": "John Smith",
                        "position": 1,
                        "points": 25
                    }
                ],
                "simulation_metadata": {
                    "monte_carlo_iterations": 1000,
                    "random_seed": 42
                }
            }]
        }
    }


# ============================================================================
# DRIVER SCHEMAS
# ============================================================================

class DriverSummary(BaseModel):
    """Simplified driver model for API responses"""
    id: int
    name: str
    nationality: str
    age: int = 25

    # Core skills (simplified for API)
    raw_speed: float = Field(ge=0.0, le=100.0)
    consistency: float = Field(ge=0.0, le=100.0)
    racecraft: float = Field(ge=0.0, le=100.0)

    # Career stats
    career_wins: int = 0
    career_podiums: int = 0
    career_points: float = 0.0

    current_team_id: Optional[int] = None


class DriversListResponse(BaseModel):
    """Response model for GET /drivers"""
    drivers: List[DriverSummary]
    count: int


# ============================================================================
# TEAM SCHEMAS
# ============================================================================

class TeamSummary(BaseModel):
    """Simplified team model for API responses"""
    id: int
    name: str
    discipline: str
    nationality: str = "INT"
    tier: int = Field(ge=1, le=3, default=2)
    budget: float = Field(ge=0.0, default=50000000.0)


class TeamsListResponse(BaseModel):
    """Response model for GET /teams"""
    teams: List[TeamSummary]
    count: int


# ============================================================================
# SYSTEM SCHEMAS
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Response model for GET /health"""
    status: str = "healthy"
    database: str = "connected"
    stats: Dict[str, int]


class DatabaseStatsResponse(BaseModel):
    """Response model for GET /stats"""
    database_stats: Dict[str, int]


class APIInfoResponse(BaseModel):
    """Response model for GET / (root)"""
    message: str
    version: str
    status: str
    endpoints: Dict[str, str]
