"""
Enhanced API endpoints for Multi-Discipline Momentum Simulation

This module extends the simulation API to support all 7 racing disciplines
with comprehensive vehicle development, championship management, and
AI-driven decision systems.

New endpoints for Unity integration:
- Multi-discipline team and driver management  
- Vehicle development and technology trees
- Championship standings across all series
- Transfer market and contract negotiations
- AI recommendations and strategic decisions

Authors: Final Year Project - Computer Science
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
import json

from database.database_manager import DatabaseManager
from Momentum.Python.database.models.multi_discipline_models import (
    MultiDisciplineDriver, MultiDisciplineTeam, Vehicle, RacingDiscipline
)
from systems.vehicle_development import VehicleDevelopmentEngine, DevelopmentProject
from systems.championship_manager import ChampionshipManager, TransferMarket
from ai.decision_engine import TeamAI, DriverAI, AIDecision
from Momentum.Python.disciplines.race_simulation import RaceSimulator
from data.placeholder_names import (
    DISCIPLINES, TEAM_NAMES, DRIVER_POOL, TRACK_NAMES, 
    get_random_driver_name, get_random_team_name
)
from config import Config

app = FastAPI(
    title="Momentum Multi-Discipline Motorsport Simulation API",
    description="Comprehensive motorsport management API supporting all major racing disciplines with generic, non-licensed content",
    version="2.0.0"
)

# Enable CORS for Unity integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Unity's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize core systems
db_manager = DatabaseManager(Config.DATABASE_PATH)
development_engine = VehicleDevelopmentEngine()
championship_manager = ChampionshipManager(db_manager)
race_simulator = RaceSimulator(db_manager)

# ============================================================================
# MULTI-DISCIPLINE TEAM MANAGEMENT
# ============================================================================

@app.get("/teams/multi-discipline", response_model=List[Dict])
async def get_multi_discipline_teams():
    """
    Get all teams with their multi-discipline participation
    
    Returns comprehensive team data including:
    - Active disciplines and expertise levels
    - Budget allocation across series
    - Technical capabilities and facilities
    - AI personality traits for decision making
    """
    try:
        teams = []
        # Implementation would query multi-discipline teams
        # This is a structure example
        example_team = {
            "id": 1,
            "name": "Apex Racing",
            "nationality": "GBR", 
            "active_disciplines": ["GPC", "EGP", "WEC"],
            "primary_discipline": "GPC",
            "total_budget": 400.0,
            "budget_allocation": {
                "GPC": 0.75,
                "EGP": 0.15, 
                "WEC": 0.10
            },
            "technical_expertise": {
                "GPC": 0.92,
                "EGP": 0.78,
                "WEC": 0.65
            },
            "facilities": {
                "wind_tunnel_quality": 0.95,
                "simulator_quality": 0.88,
                "manufacturing_capability": 0.90
            },
            "ai_personality": {
                "risk_appetite": 0.72,
                "innovation_focus": 0.85,
                "driver_development": 0.68
            }
        }
        teams.append(example_team)
        return teams
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}/disciplines/{discipline}/vehicle")
async def get_team_vehicle(team_id: int, discipline: str):
    """
    Get team's vehicle development status for specific discipline
    
    Returns:
    - Component levels (aerodynamics, engine, chassis, etc.)
    - Active development projects
    - Performance projections
    - Recommended development priorities
    """
    try:
        # Implementation would query vehicle data
        vehicle_data = {
            "team_id": team_id,
            "discipline": discipline,
            "season_year": 2025,
            "overall_performance": 0.76,
            "components": {
                "aerodynamics": 0.82,
                "engine": 0.74,
                "chassis": 0.78,
                "electronics": 0.85,
                "reliability": 0.72
            },
            "active_projects": [
                {
                    "component": "aerodynamics",
                    "sub_component": "front_wing_optimization",
                    "budget_allocated": 8.5,
                    "time_remaining_weeks": 6,
                    "expected_gain": 0.025
                }
            ],
            "development_recommendations": development_engine.recommend_development_priorities(
                None, None, 50.0  # Placeholder values
            )
        }
        return vehicle_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DRIVER MANAGEMENT AND CONTRACTS
# ============================================================================

@app.get("/drivers/multi-discipline", response_model=List[Dict])
async def get_multi_discipline_drivers():
    """
    Get all drivers with multi-discipline capabilities
    
    Returns:
    - Discipline-specific skill ratings
    - Contract status across all series
    - Career progression and achievements
    - Market value and transfer potential
    """
    try:
        drivers = []
        example_driver = {
            "id": 1,
            "name": "Alex Sterling",
            "nationality": "GBR",
            "age": 27,
            "primary_discipline": "GPC",
            "active_disciplines": ["GPC", "WEC"],
            "discipline_skills": {
                "GPC": {"skill": 0.98, "consistency": 0.94, "racecraft": 0.96},
                "WEC": {"skill": 0.85, "consistency": 0.88, "racecraft": 0.82}
            },
            "current_contracts": {
                "GPC": {"team_id": 1, "salary": 45.0, "expires": "2028"},
                "WEC": None
            },
            "career_stats": {
                "GPC": {"wins": 62, "podiums": 104, "points": 2845, "championships": 4},
                "WEC": {"wins": 0, "podiums": 0, "points": 0}
            },
            "market_value": 55.0,
            "ai_traits": {
                "ambition": 0.95,
                "loyalty": 0.72,
                "risk_tolerance": 0.78
            }
        }
        drivers.append(example_driver)
        return drivers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/drivers/{driver_id}/contract-offers")
async def get_driver_contract_offers(driver_id: int):
    """
    Get current contract offers for a driver across all disciplines
    
    Returns pending contract negotiations with terms and AI recommendations
    """
    try:
        offers = []
        example_offer = {
            "team_id": 3,
            "team_name": "Crimson Motorsport",
            "discipline": "GPC", 
            "offer_details": {
                "annual_salary": 42.0,
                "contract_length": 3,
                "performance_bonuses": {"win": 0.5, "podium": 0.2, "championship": 5.0},
                "clauses": {"release_clause": 80.0}
            },
            "ai_recommendation": {
                "should_accept": True,
                "confidence": 0.82,
                "reasoning": "Significant salary increase and championship-winning car"
            }
        }
        offers.append(example_offer)
        return offers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VEHICLE DEVELOPMENT SYSTEM
# ============================================================================

@app.post("/teams/{team_id}/disciplines/{discipline}/develop")
async def start_development_project(
    team_id: int, 
    discipline: str,
    component: str,
    sub_component: str,
    budget: float
):
    """
    Start a vehicle development project
    
    Args:
        component: Component to develop (aerodynamics, engine, etc.)
        sub_component: Specific sub-component
        budget: Budget allocation for project
        
    Returns:
        Development project details with timeline and expected outcomes
    """
    try:
        # Calculate development parameters
        current_level = 0.65  # Placeholder - would query actual vehicle
        team_expertise = 0.78  # Placeholder - would query team data
        
        cost = development_engine.calculate_development_cost(
            discipline, component, sub_component, current_level
        )
        
        time_required = development_engine.estimate_development_time(
            discipline, component, sub_component, budget, team_expertise
        )
        
        project = {
            "project_id": 123,  # Would be generated
            "team_id": team_id,
            "discipline": discipline,
            "component": component,
            "sub_component": sub_component,
            "budget_allocated": budget,
            "estimated_cost": cost,
            "time_required_weeks": time_required,
            "expected_performance_gain": 0.018,
            "risk_level": 0.25,
            "success_probability": 0.82,
            "status": "active"
        }
        
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}/development/recommendations")
async def get_development_recommendations(team_id: int, discipline: str, budget: float = 50.0):
    """
    Get AI-generated development recommendations for team
    
    Returns prioritized list of development opportunities with cost-benefit analysis
    """
    try:
        # This would use the actual VehicleDevelopmentEngine
        recommendations = [
            {
                "component": "aerodynamics",
                "sub_component": "rear_wing_efficiency",
                "priority_score": 8.7,
                "estimated_cost": 6.2,
                "expected_impact": 0.022,
                "reasoning": "High impact, relatively low cost, addresses current weakness"
            },
            {
                "component": "engine",
                "sub_component": "fuel_efficiency",
                "priority_score": 7.9,
                "estimated_cost": 9.1,
                "expected_impact": 0.018,
                "reasoning": "Critical for race strategy, significant long-term benefits"
            }
        ]
        
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CHAMPIONSHIP MANAGEMENT
# ============================================================================

@app.get("/championships/standings")
async def get_all_championship_standings(season_year: int = 2025):
    """
    Get current championship standings across all active disciplines
    
    Returns driver and constructor standings for all racing series
    """
    try:
        standings = {}
        
        for discipline in ["single_seater", "production_touring", "rally_stage", "endurance", "urban_street", "drag_acceleration", "sprint_rallycross"]:
            standings[discipline] = {
                "drivers": [
                    {"position": 1, "driver_id": 1, "name": "Alex Sterling", "points": 393, "wins": 8},
                    {"position": 2, "driver_id": 2, "name": "Lucas Phoenix", "points": 331, "wins": 3}
                ],
                "constructors": [
                    {"position": 1, "team_id": 1, "name": "Apex Racing", "points": 589, "wins": 10},
                    {"position": 2, "team_id": 2, "name": "Phoenix Grand Prix", "points": 521, "wins": 4}
                ]
            }
        
        return standings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/championships/calendar")
async def get_season_calendar(year: int = 2025):
    """
    Get coordinated racing calendar across all disciplines
    
    Returns race schedule with dates, tracks, and potential conflicts
    """
    try:
        calendar = championship_manager.create_season_calendar(
            year, ["single_seater", "production_touring", "rally_stage", "endurance", "urban_street", "drag_acceleration", "sprint_rallycross"]
        )
        
        return {
            "season_year": year,
            "season_start": calendar.season_start_date,
            "season_end": calendar.season_end_date,
            "race_weekends": calendar.race_weekends,
            "transfer_windows": calendar.transfer_windows,
            "total_race_weekends": len(calendar.race_weekends)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRANSFER MARKET AND NEGOTIATIONS
# ============================================================================

@app.get("/transfers/market")
async def get_transfer_market_status():
    """
    Get current transfer market status and rumors
    
    Returns available drivers, team needs, and market rumors
    """
    try:
        market_data = {
            "transfer_window_status": "summer_open",
            "window_closes": "2025-08-31",
            "available_drivers": [
                {
                    "driver_id": 15,
                    "name": "Carlos Nexus",
                    "current_team": "Crimson Motorsport",
                    "contract_expires": "2024-12-31",
                    "disciplines": ["GPC", "WEC"],
                    "market_value": 25.0,
                    "interested_teams": [3, 7, 12]
                }
            ],
            "team_vacancies": [
                {
                    "team_id": 8,
                    "team_name": "Lightning Racing",
                    "discipline": "GPC",
                    "budget_available": 15.0,
                    "requirements": {
                        "minimum_experience": 2,
                        "preferred_age_max": 28
                    }
                }
            ],
            "transfer_rumors": championship_manager.transfer_market.generate_transfer_rumors()
        }
        
        return market_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transfers/negotiate")
async def negotiate_contract(driver_id: int, team_id: int, discipline: str):
    """
    Simulate contract negotiation between driver and team
    
    Returns negotiation outcome with contract terms or rejection reasons
    """
    try:
        negotiation_result = championship_manager.simulate_contract_negotiations(
            driver_id, team_id, discipline
        )
        
        return negotiation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AI DECISION SYSTEMS
# ============================================================================

@app.get("/teams/{team_id}/ai-decisions")
async def get_team_ai_decisions(team_id: int, discipline: str):
    """
    Get recent AI decisions made by team management
    
    Returns strategic decisions with reasoning and confidence levels
    """
    try:
        # This would use actual TeamAI system
        decisions = [
            {
                "decision_type": "race_strategy",
                "decision_date": "2025-09-28",
                "decision_data": {
                    "strategy": "aggressive",
                    "confidence": 0.78
                },
                "reasoning": "Championship pressure requires risk-taking approach",
                "expected_outcome": "Higher chance of podium finish"
            },
            {
                "decision_type": "driver_signing", 
                "decision_date": "2025-09-25",
                "decision_data": {
                    "target_driver": "Oscar Azure",
                    "max_offer": 18.5,
                    "confidence": 0.85
                },
                "reasoning": "Young talent with high potential, fits team development philosophy",
                "expected_outcome": "Long-term competitive advantage"
            }
        ]
        
        return decisions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/drivers/{driver_id}/ai-analysis") 
async def get_driver_ai_analysis(driver_id: int):
    """
    Get AI analysis of driver's career and decision patterns
    
    Returns career trajectory analysis and strategic recommendations
    """
    try:
        analysis = {
            "driver_id": driver_id,
            "career_phase": "peak_performance",
            "market_position": "tier_1_star",
            "career_trajectory": "ascending",
            "strengths": ["racecraft", "consistency", "pressure_handling"],
            "development_areas": ["technical_feedback", "media_presence"],
            "optimal_disciplines": ["single_seater", "endurance"],
            "contract_recommendations": {
                "preferred_contract_length": 3,
                "target_salary_range": [35.0, 45.0],
                "key_clauses": ["performance_bonuses", "championship_bonus"]
            },
            "team_compatibility": {
                "best_fits": ["championship_contenders", "development_focused"],
                "avoid": ["unstable_financial", "poor_management"]
            }
        }
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RACE SIMULATION (ENHANCED)
# ============================================================================

@app.post("/races/{race_id}/simulate-enhanced")
async def simulate_race_enhanced(race_id: int, discipline: str):
    """
    Enhanced race simulation with discipline-specific features
    
    Includes vehicle performance, strategy decisions, and emergent events
    """
    try:
        # This would integrate with enhanced race simulation
        race_result = {
            "race_id": race_id,
            "discipline": discipline,
            "race_status": "completed",
            "race_duration": "1:45:23.456" if discipline in ["single_seater"] else "varies",
            "results": [
                {
                    "position": 1,
                    "driver_id": 1,
                    "driver_name": "Alex Johnson",
                    "team_id": 1,
                    "team_name": "Thunder Racing Team",
                    "finish_time": "1:45:23.456",
                    "gap_to_leader": "0.000",
                    "points_awarded": 25,
                    "fastest_lap": True
                }
            ],
            "race_events": [
                {
                    "lap": 23,
                    "event_type": "pit_stop",
                    "driver": "Lewis Eclipse", 
                    "details": "Tire change to medium compound"
                },
                {
                    "lap": 45,
                    "event_type": "overtake",
                    "details": "Lucas Phoenix passes Marco Veloce for P3"
                }
            ],
            "performance_analysis": {
                "strategy_effectiveness": 0.87,
                "vehicle_performance_rating": 0.82,
                "driver_performance_rating": 0.91
            }
        }
        
        return race_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/disciplines/info")
async def get_disciplines_info():
    """Get information about all supported racing disciplines"""
    try:
        # Define constants to avoid duplication
        STANDARD_RACE_LENGTH = "45 minutes"
        MOTORCYCLE_CHARACTERISTICS = ["motorcycle", "lean_angles", "close_racing"]
        FORMULA_CHARACTERISTICS_SPEC = ["spec_chassis", "talent_development", "reverse_grid"]
        
        return {
            "GPC": {
                "full_name": "Global Premier Championship",
                "description": "Premier single-seater racing championship",
                "grid_size": 20,
                "typical_race_length": "90 minutes",
                "key_characteristics": ["high_speed", "advanced_technology", "global_audience"]
            },
            "GPDC": {
                "full_name": "Global Premier Development Championship", 
                "description": "Direct feeder series to Global Premier Championship",
                "grid_size": 22,
                "typical_race_length": STANDARD_RACE_LENGTH,
                "key_characteristics": FORMULA_CHARACTERISTICS_SPEC
            },
            "GPAC": {
                "full_name": "Global Premier Academy Championship",
                "description": "Entry-level formula racing series", 
                "grid_size": 24,
                "typical_race_length": "35 minutes",
                "key_characteristics": ["cost_controlled", "young_drivers", "close_racing"]
            },
            "endurance": {
                "full_name": "Global Endurance Championship",
                "description": "Multi-class prototype and sports car endurance racing",
                "grid_size": 60,
                "typical_race_length": "6-24 hours",
                "key_characteristics": ["endurance", "multi_class", "manufacturer_focus"]
            },
            "rally_stage": {
                "full_name": "International Rally Championship", 
                "description": "Point-to-point stage rally competition",
                "grid_size": 16,
                "typical_event_length": "3 days",
                "key_characteristics": ["varied_surfaces", "co_driver", "stage_racing"]
            },
            "MPG": {
                "full_name": "Motorcycle Premier Grand Prix",
                "description": "Premier motorcycle road racing championship",
                "grid_size": 24, 
                "typical_race_length": STANDARD_RACE_LENGTH,
                "key_characteristics": MOTORCYCLE_CHARACTERISTICS
            },
            "EGP": {
                "full_name": "Electric Grand Prix",
                "description": "Electric single-seater championship",
                "grid_size": 22,
                "typical_race_length": STANDARD_RACE_LENGTH,
                "key_characteristics": ["electric", "street_circuits", "attack_mode"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)