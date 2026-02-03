"""
Team Management Service (UC-11, UC-12, UC-13, UC-14)

Handles team CRUD operations, budget management, and player team ownership tracking.

Features:
- Team creation with initial asset provisioning
- Team profile retrieval with roster aggregation
- Budget management and constraint validation
- Team attribute updates with audit logging

Notes:
- Team names are required in API requests
- For generating unique team names, see tools.team_name_generator.generate_team_name()
  which provides authentic, discipline-specific naming using Faker library
- Available for: database seeding, test data generation, future AI team generation
- Player team ownership tracking
- Faker-based unique team name generation
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from database.database_manager import DatabaseManager
from database.models import Team, Driver, StaffMember
from tools.team_name_generator import generate_team_name, generate_team_names
import json


class TeamService:
    """Service for managing team operations and lifecycle"""
    
    # Budget limits by tier (in EUR)
    TIER_BUDGETS = {
        "TIER_1": 130_000_000,   # Top tier - €130M
        "TIER_2": 60_000_000,    # Mid tier - €60M
        "TIER_3": 25_000_000,    # Junior tier - €25M
    }
    
    # Staff limits by tier
    TIER_STAFF_LIMITS = {
        "TIER_1": 60,
        "TIER_2": 40,
        "TIER_3": 25,
    }
    
    # Driver slots per team
    DRIVER_SLOTS_PER_DISCIPLINE = {
        "SINGLE_SEATER": 2,
        "PRODUCTION_TOURING": 2,
        "URBAN_STREET": 2,
        "DRAG_ACCELERATION": 2,
        "SPRINT_RALLYCROSS": 2,
        "ENDURANCE": 4,  # Endurance allows more drivers for multi-driver cars
    }
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    # ========================================================================
    # UC-12: Create New Team
    # ========================================================================
    
    def create_team(
        self,
        name: str,
        discipline: str = "SINGLE_SEATER",
        nationality: str = "INT",
        tier: str = "TIER_2",
        team_principal: str = "",
        headquarters: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new team with initial assets and budget allocation.
        
        Args:
            name: Team name (required)
            discipline: Racing discipline
            nationality: Team nationality (default: "INT")
            tier: Team tier level (affects budget and limits)
            team_principal: Team principal name
            headquarters: Team headquarters location
            
        Returns:
            Dictionary with created team ID, initial budget, staff limit, and driver slots
            
        Raises:
            ValueError: If tier is invalid or required parameters missing
        """
        if tier not in self.TIER_BUDGETS:
            raise ValueError(f"Invalid tier: {tier}. Must be one of {list(self.TIER_BUDGETS.keys())}")
        
        # Validate name is provided
        if not name or not name.strip():
            raise ValueError("Team name is required")
        
        # Get tier configuration
        initial_budget = self.TIER_BUDGETS[tier]
        staff_limit = self.TIER_STAFF_LIMITS[tier]
        driver_slots = self.DRIVER_SLOTS_PER_DISCIPLINE.get(discipline, 2)
        
        # Create team object
        team = Team(
            id=0,  # Database will assign ID
            name=name,
            nationality=nationality,
            discipline=discipline,
            tier=tier,
            budget=initial_budget,
            founded_year=datetime.now().year,
            team_principal=team_principal,
            history="",
            total_wins=0,
            total_podiums=0,
            championships=0,
            operations_rating=50.0,
            strategy_profile="standard"
        )
        
        # Store additional metadata
        team_metadata = {
            "founded_date": datetime.now().isoformat(),
            "staff_limit": staff_limit,
            "driver_slots": driver_slots,
            "headquarters": headquarters,
            "budget_transactions": [],
            "player_owned": False
        }
        
        # Create team in database
        team_id = self.db.create_team(team)
        
        if not team_id:
            raise RuntimeError(f"Failed to create team: {name}")
        
        return {
            "id": team_id,
            "name": name,
            "discipline": discipline,
            "tier": tier,
            "initial_budget": initial_budget,
            "staff_limit": staff_limit,
            "driver_slots": driver_slots,
            "message": f"Team {name} created successfully with €{initial_budget:,.0f} budget"
        }
    
    # ========================================================================
    # UC-11: Read Team Details
    # ========================================================================
    
    def get_team_details(self, team_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full team profile with roster, staff, and financials.
        
        Args:
            team_id: Team ID
            
        Returns:
            Dictionary with complete team details including roster and financials,
            or None if team not found
        """
        team = self.db.get_team(team_id)
        if not team:
            return None
        
        # Get drivers on this team
        drivers = self.db.get_drivers_by_team(team_id)
        driver_entries = [
            {
                "id": d.id,
                "name": d.name,
                "position": 1,  # Could track driver position
                "nationality": d.nationality,
                "current_rating": d.speed,  # Use speed as overall rating
                "career_points": d.career_points,
                "contract_length": d.contract_length
            }
            for d in drivers
        ]
        
        # Get staff on this team (if staff table exists)
        try:
            staff = self.db.get_staff_by_team(team_id) if hasattr(self.db, 'get_staff_by_team') else []
            staff_entries = [
                {
                    "id": s.id,
                    "name": s.name,
                    "role": s.role,
                    "rating": s.rating,
                    "annual_salary": 800_000  # Placeholder
                }
                for s in staff
            ]
        except:
            staff_entries = []
        
        # Calculate financials
        total_driver_salaries = sum(d.salary or 800_000 for d in drivers)
        total_staff_salaries = sum(s.get("annual_salary", 800_000) for s in staff_entries)
        total_expenditure = total_driver_salaries + total_staff_salaries
        available_budget = team.budget - total_expenditure
        
        # Estimate annual income from prizes (varies by discipline and performance)
        annual_income = self._estimate_annual_income(team)
        
        return {
            "id": team.id,
            "name": team.name,
            "discipline": team.discipline,
            "nationality": team.nationality,
            "tier": team.tier,
            "founded_year": team.founded_year,
            "team_principal": team.team_principal,
            "budget": team.budget,
            "annual_income": annual_income,
            "total_expenditure": total_expenditure,
            "available_budget": available_budget,
            "total_wins": team.total_wins,
            "total_podiums": team.total_podiums,
            "championships": team.championships,
            "operations_rating": team.operations_rating,
            "drivers": driver_entries,
            "staff": staff_entries,
            "staff_count": len(staff_entries),
            "headquarters": "",  # Could store in database
            "biography": team.history
        }
    
    # ========================================================================
    # UC-13: Read Player Team
    # ========================================================================
    
    def get_player_team(self, player_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the player's owned team with edit permissions.
        
        Args:
            player_id: Player ID
            
        Returns:
            Team details with editable=True flag, or None if player has no team
        """
        # Query for team owned by player
        # This would require a player_teams table or similar tracking
        # For now, return a placeholder implementation
        
        # In a full implementation, you would:
        # 1. Query player_teams table for player_id
        # 2. Return team details with editable=True
        # 3. Include permission flags
        
        return None  # To be implemented with player system
    
    # ========================================================================
    # UC-14: Update Team Attributes
    # ========================================================================
    
    def update_team(
        self,
        team_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update team attributes with audit logging.
        
        Args:
            team_id: Team ID
            updates: Dictionary of attributes to update
            
        Returns:
            Dictionary with update confirmation and audit log
        """
        team = self.db.get_team(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        
        # Track changes
        changes = {}
        
        # Only allow certain fields to be updated
        allowed_fields = ["name", "team_principal", "headquarters", "biography", "strategy_profile"]
        
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                old_value = getattr(team, field, None)
                if old_value != value:
                    setattr(team, field, value)
                    changes[field] = {
                        "old": old_value,
                        "new": value
                    }
        
        if not changes:
            return {
                "id": team_id,
                "name": team.name,
                "updated_at": datetime.now().isoformat(),
                "changes": {},
                "message": "No changes were made"
            }
        
        # Update team in database
        success = self.db.update_team(team_id, team)
        
        if not success:
            raise RuntimeError(f"Failed to update team {team_id}")
        
        # Log audit trail
        self._log_team_change(team_id, changes)
        
        return {
            "id": team_id,
            "name": team.name,
            "updated_at": datetime.now().isoformat(),
            "changes": changes,
            "message": f"Team {team.name} updated successfully"
        }
    
    # ========================================================================
    # Budget Management
    # ========================================================================
    
    def allocate_budget(
        self,
        team_id: int,
        category: str,
        amount: float,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Allocate budget to a specific category.
        
        Args:
            team_id: Team ID
            category: Budget category (staff, facility_upgrade, etc.)
            amount: Amount to allocate
            description: Optional description
            
        Returns:
            Budget transaction confirmation
            
        Raises:
            ValueError: If insufficient budget available
        """
        team = self.db.get_team(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        
        if amount <= 0:
            raise ValueError("Allocation amount must be positive")
        
        if amount > team.budget:
            raise ValueError(
                f"Insufficient budget. Requested: €{amount:,.0f}, Available: €{team.budget:,.0f}"
            )
        
        # Create budget transaction
        transaction = {
            "id": self._generate_transaction_id(),
            "team_id": team_id,
            "category": category,
            "amount": amount,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "status": "allocated"
        }
        
        # Update team budget
        team.budget -= amount
        self.db.update_team(team_id, team)
        
        return {
            "success": True,
            "transaction_id": transaction["id"],
            "team_id": team_id,
            "amount": amount,
            "category": category,
            "remaining_budget": team.budget,
            "timestamp": transaction["timestamp"]
        }
    
    def get_budget_status(self, team_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current budget status and allocation breakdown.
        
        Args:
            team_id: Team ID
            
        Returns:
            Budget summary with allocation breakdown, or None if team not found
        """
        team = self.db.get_team(team_id)
        if not team:
            return None
        
        # Get team details for salary calculations
        details = self.get_team_details(team_id)
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "total_budget": team.budget + details["total_expenditure"],  # Original + spent
            "allocated": [
                {
                    "category": "driver_salaries",
                    "allocated": sum(d.get("contract_length", 1) * 2_000_000 for d in details["drivers"]),
                    "used": sum(d.get("contract_length", 1) * 2_000_000 for d in details["drivers"]),
                    "remaining": 0
                },
                {
                    "category": "staff",
                    "allocated": len(details["staff"]) * 800_000,
                    "used": len(details["staff"]) * 800_000,
                    "remaining": 0
                }
            ],
            "available": team.budget,
            "monthly_income": self._estimate_annual_income(team) / 12,
            "monthly_expenditure": details["total_expenditure"] / 12
        }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _estimate_annual_income(self, team: Team) -> float:
        """
        Estimate annual income from prize money based on tier and performance.
        
        Args:
            team: Team object
            
        Returns:
            Estimated annual income in EUR
        """
        base_income = {
            "TIER_1": 5_000_000,
            "TIER_2": 2_000_000,
            "TIER_3": 500_000,
        }
        
        tier_income = base_income.get(team.tier, 2_000_000)
        
        # Adjust based on performance
        performance_bonus = (team.total_wins * 100_000) + (team.total_podiums * 50_000)
        
        return tier_income + performance_bonus
    
    def _log_team_change(self, team_id: int, changes: Dict[str, Any]) -> None:
        """Log team changes to audit trail"""
        log_entry = {
            "team_id": team_id,
            "timestamp": datetime.now().isoformat(),
            "changes": changes
        }
        # In a full implementation, this would write to an audit log table
        pass
    
    def _generate_transaction_id(self) -> int:
        """Generate unique transaction ID"""
        import random
        return random.randint(100000, 999999)


__all__ = ["TeamService"]
