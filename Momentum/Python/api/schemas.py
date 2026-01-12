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
    tier: str = Field(default="TIER_2")
    budget: float = Field(ge=0.0, default=50000000.0)


class TeamsListResponse(BaseModel):
    """Response model for GET /teams"""
    teams: List[TeamSummary]
    count: int


# ============================================================================
# TEAM MANAGEMENT SCHEMAS (UC-11, UC-12, UC-13, UC-14)
# ============================================================================

class StaffEntry(BaseModel):
    """Staff member entry in team roster"""
    id: int
    name: str
    role: str
    rating: float = Field(ge=0.0, le=100.0)
    annual_salary: float


class DriverEntry(BaseModel):
    """Driver entry in team roster"""
    id: int
    name: str
    position: int
    nationality: str
    current_rating: float = Field(ge=0.0, le=100.0)
    career_points: int
    contract_length: Optional[int] = None


class TeamDetails(BaseModel):
    """UC-11: Full team profile with roster and financials"""
    id: int
    name: str
    discipline: str
    nationality: str
    tier: str
    founded_year: int
    team_principal: str
    
    # Financials
    budget: float
    annual_income: float
    total_expenditure: float
    available_budget: float
    
    # Performance
    total_wins: int
    total_podiums: int
    championships: int
    operations_rating: float
    
    # Roster
    drivers: List[DriverEntry]
    staff: List[StaffEntry]
    staff_count: int
    
    # Metadata
    headquarters: str = ""
    biography: str = ""


class TeamCreate(BaseModel):
    """UC-12: Request model for creating a new team"""
    name: str = Field(..., min_length=1, max_length=100)
    discipline: str = Field(
        ...,
        description="Racing discipline",
        examples=["SINGLE_SEATER", "RALLY_STAGE", "ENDURANCE", "PRODUCTION_TOURING"]
    )
    nationality: str = Field(default="INT")
    tier: str = Field(
        default="TIER_2",
        description="Team tier level affects budget and staff limits",
        examples=["TIER_1", "TIER_2", "TIER_3"]
    )
    team_principal: str = Field(default="")
    headquarters: str = Field(default="")


class TeamCreateResponse(BaseModel):
    """UC-12: Response after team creation with initial assets"""
    id: int
    name: str
    discipline: str
    tier: str
    initial_budget: float
    staff_limit: int
    driver_slots: int
    message: str


class TeamUpdate(BaseModel):
    """UC-14: Request model for updating team attributes"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    team_principal: Optional[str] = None
    headquarters: Optional[str] = None
    biography: Optional[str] = None
    strategy_profile: Optional[str] = Field(None, examples=["aggressive", "defensive", "standard"])


class TeamUpdateResponse(BaseModel):
    """UC-14: Response after team update with audit log"""
    id: int
    name: str
    updated_at: str
    changes: Dict[str, Any]
    message: str


class BudgetAllocation(BaseModel):
    """Budget allocation breakdown"""
    category: str
    allocated: float
    used: float
    remaining: float


class TeamBudgetResponse(BaseModel):
    """Current team budget status"""
    team_id: int
    team_name: str
    total_budget: float
    allocated: List[BudgetAllocation]
    available: float
    monthly_income: float
    monthly_expenditure: float


class BudgetTransactionRequest(BaseModel):
    """Request to allocate or transfer budget"""
    category: str = Field(
        ...,
        description="Budget category",
        examples=["staff", "facility_upgrade", "driver_development", "marketing"]
    )
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


class BudgetTransactionResponse(BaseModel):
    """Response after budget transaction"""
    success: bool
    transaction_id: int
    team_id: int
    amount: float
    category: str
    remaining_budget: float
    timestamp: str


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


# ============================================================================
# CHAMPIONSHIP SCHEMAS
# ============================================================================

class ChampionshipCreate(BaseModel):
    """Request model for POST /championships"""
    name: str = Field(..., min_length=1, max_length=100)
    discipline: str = Field(
        ...,
        description="Racing discipline",
        examples=["SINGLE_SEATER", "RALLY_STAGE", "ENDURANCE"]
    )
    season_length: int = Field(ge=1, le=50, default=20)
    points_system: str = Field(default="standard")
    tier: str = Field(default="TOP_TIER")
    founded_year: int = Field(ge=1900, le=2100, default=2025)
    description: str = Field(default="")
    track_ids: List[int] = Field(
        default=[],
        description="List of track IDs for the season calendar"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Season start date (YYYY-MM-DD)"
    )


class ChampionshipResponse(BaseModel):
    """Response model for championship details"""
    id: int
    name: str
    discipline: str
    season_length: int
    points_system: str
    current_season: int
    tier: str
    founded_year: int
    description: str
    archived: bool


class StandingEntry(BaseModel):
    """Championship standing entry"""
    position: int
    driver_id: int
    driver_name: str
    team_id: int
    team_name: str
    total_points: int
    wins: int
    podiums: int
    races_started: int
    dnf_count: int
    fastest_laps: int


class ChampionshipStandingsResponse(BaseModel):
    """Response model for GET /championships/{id}/standings"""
    championship_id: int
    championship_name: str
    season: int
    standings: List[StandingEntry]


class RaceEventCreate(BaseModel):
    """Request model for POST /championships/{id}/events"""
    track_id: int
    race_date: str = Field(
        ...,
        description="Race date (YYYY-MM-DD)"
    )
    weather_conditions: str = Field(default="clear")
    laps: int = Field(ge=1, default=50)


class RaceEventResponse(BaseModel):
    """Response model for race event details"""
    race_id: int
    round_number: int
    race_date: str
    track_id: int
    track_name: str
    track_country: str
    status: str
    weather_conditions: str
    laps: int


class ChampionshipScheduleResponse(BaseModel):
    """Response model for GET /championships/{id}/schedule"""
    championship_id: int
    season: int
    races: List[RaceEventResponse]


class RaceStatusUpdate(BaseModel):
    """Request model for PATCH /races/{id}/status"""
    status: str = Field(
        ...,
        description="New race status",
        examples=["scheduled", "in-progress", "completed", "cancelled"]
    )


class ChampionshipDetailsResponse(BaseModel):
    """Response model for GET /championships/{id} with full details"""
    championship: ChampionshipResponse
    current_standings: List[StandingEntry]
    calendar: List[RaceEventResponse]


class RaceResultDetailResponse(BaseModel):
    """Response model for GET /races/{id}/results with full classification"""
    race_id: int
    championship_id: int
    season: int
    round_number: int
    track_name: str
    race_date: str
    status: str
    classification: List[Dict[str, Any]]
    fastest_lap: Optional[Dict[str, Any]] = None


class RecalculateStandingsResponse(BaseModel):
    """Response model for POST /championships/{id}/standings/recalculate"""
    success: bool
    championship_id: int
    season: int
    standings: List[StandingEntry]
    message: str
