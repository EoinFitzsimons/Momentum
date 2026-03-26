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

from typing import Optional, Dict, Any, List
from datetime import datetime
from database.database_manager import DatabaseManager
from database.models import Team


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
        headquarters: str = "",
        player_id: Optional[str] = None
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
        
        if discipline not in self.DRIVER_SLOTS_PER_DISCIPLINE:
            raise ValueError(f"Invalid discipline: {discipline}")

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
            strategy_profile="standard",
            headquarters=headquarters,
            biography=""
        )
        
        # Create team in database
        team_id = self.db.create_team(team)
        
        if not team_id:
            raise RuntimeError(f"Failed to create team: {name}")

        if player_id:
            self.db.assign_team_owner(team_id, str(player_id))

        self._log_team_change(
            team_id,
            {
                "created": {
                    "name": name,
                    "discipline": discipline,
                    "tier": tier,
                    "initial_budget": initial_budget,
                    "staff_limit": staff_limit,
                    "driver_slots": driver_slots,
                }
            },
            actor_id=str(player_id) if player_id else None,
            action="team_created"
        )
        
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
        except Exception:
            staff_entries = []
        
        # Calculate financials
        total_driver_salaries = sum(d.salary or 800_000 for d in drivers)
        total_staff_salaries = sum(s.get("annual_salary", 800_000) for s in staff_entries)
        total_expenditure = total_driver_salaries + total_staff_salaries
        available_budget = team.budget - total_expenditure
        
        # Estimate annual income from prizes (varies by discipline and performance)
        annual_income = self._estimate_annual_income(team)
        owner_id = self.db.get_team_owner(team_id)
        facility_upgrades = self.db.get_facility_upgrades(team_id)
        
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
            "headquarters": team.headquarters,
            "biography": team.biography,
            "team_version": int(getattr(team, "version", 1) or 1),
            "staff_limit": self.TIER_STAFF_LIMITS.get(team.tier, 25),
            "driver_slots": self.DRIVER_SLOTS_PER_DISCIPLINE.get(team.discipline, 2),
            "facility_upgrades": facility_upgrades,
            "is_player_owned": owner_id is not None,
            "editable": False
        }
    
    # ========================================================================
    # UC-13: Read Player Team
    # ========================================================================
    
    def get_player_team(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the player's owned team with edit permissions.
        
        Args:
            player_id: Player ID
            
        Returns:
            Team details with editable=True flag, or None if player has no team
        """
        team_id = self.db.get_player_team_id(str(player_id))
        if not team_id:
            return None

        details = self.get_team_details(team_id)
        if not details:
            return None

        details["is_player_owned"] = True
        details["editable"] = True
        details["owner_player_id"] = str(player_id)
        return details

    def assign_owner(self, team_id: int, player_id: str) -> bool:
        """Assign ownership of a team to a player."""
        team = self.db.get_team(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")
        return self.db.assign_team_owner(team_id, str(player_id))

    def can_edit_team(self, team_id: int, player_id: Optional[str]) -> bool:
        """Permission check for team edit operations."""
        owner = self.db.get_team_owner(team_id)
        if owner is None:
            return True
        if not player_id:
            return False
        return owner == str(player_id)

    def _apply_allowed_team_field_updates(
        self,
        team: Team,
        updates: Dict[str, Any],
        allowed_fields: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Apply allowed scalar field updates and return a change map."""
        changes: Dict[str, Dict[str, Any]] = {}
        for field, value in updates.items():
            if field not in allowed_fields or value is None:
                continue
            old_value = getattr(team, field, None)
            if old_value == value:
                continue
            setattr(team, field, value)
            changes[field] = {
                "old": old_value,
                "new": value,
            }
        return changes

    def _apply_facility_upgrades(
        self,
        team_id: int,
        team: Team,
        facility_upgrades: List[Any]
    ) -> Dict[str, Dict[str, str]]:
        """Apply facility upgrades, update budget/transactions, and return change map."""
        changes: Dict[str, Dict[str, str]] = {}
        for facility_name in facility_upgrades:
            if not isinstance(facility_name, str) or not facility_name.strip():
                continue
            name = facility_name.strip()
            facility_cost = self._facility_upgrade_cost(team.tier)
            if team.budget < facility_cost:
                raise ValueError(
                    f"Insufficient budget for facility upgrade '{name}'. "
                    f"Required: €{facility_cost:,.0f}, Available: €{team.budget:,.0f}"
                )

            team.budget -= facility_cost
            self.db.add_budget_transaction(
                team_id,
                "facility_upgrade",
                facility_cost,
                f"Facility upgrade: {name}"
            )
            self.db.upsert_facility_upgrade(team_id, name, facility_cost)
            changes[f"facility_upgrade::{name}"] = {
                "old": "not-upgraded",
                "new": f"invested €{facility_cost:,.0f}"
            }
        return changes

    def _build_update_team_response(
        self,
        team_id: int,
        team: Team,
        refreshed_team: Team,
        changes: Dict[str, Any],
        message: str,
    ) -> Dict[str, Any]:
        return {
            "id": team_id,
            "name": team.name,
            "updated_at": datetime.now().isoformat(),
            "changes": changes,
            "new_version": int(getattr(refreshed_team, "version", 1) or 1),
            "message": message,
        }
    
    # ========================================================================
    # UC-14: Update Team Attributes
    # ========================================================================
    
    def update_team(
        self,
        team_id: int,
        updates: Dict[str, Any],
        actor_id: Optional[str] = None
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

        if not self.can_edit_team(team_id, actor_id):
            raise ValueError("You do not have permission to update this team")

        expected_version = updates.pop("expected_version", None)
        facility_upgrades = updates.pop("facility_upgrades", None) or []

        allowed_fields = ["name", "team_principal", "headquarters", "biography", "strategy_profile"]
        changes = self._apply_allowed_team_field_updates(team, updates, allowed_fields)
        changes.update(self._apply_facility_upgrades(team_id, team, facility_upgrades))

        if not changes:
            refreshed_team = self.db.get_team(team_id)
            return self._build_update_team_response(
                team_id,
                team,
                refreshed_team,
                {},
                "No changes were made",
            )
        
        # Update team in database
        success = self.db.update_team(team_id, team, expected_version=expected_version)
        
        if not success:
            if expected_version is not None:
                raise ValueError("Update conflict detected. Team was modified by another request")
            raise RuntimeError(f"Failed to update team {team_id}")

        refreshed_team = self.db.get_team(team_id)
        
        # Log audit trail
        self._log_team_change(team_id, changes, actor_id=actor_id, action="team_updated")

        return self._build_update_team_response(
            team_id,
            team,
            refreshed_team,
            changes,
            f"Team {team.name} updated successfully",
        )
    
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
        
        details = self.get_team_details(team_id)
        available_budget = details["available_budget"] if details else team.budget

        if amount > available_budget:
            raise ValueError(
                f"Insufficient budget. Requested: €{amount:,.0f}, Available: €{available_budget:,.0f}"
            )
        
        # Create budget transaction
        transaction_id = self.db.add_budget_transaction(team_id, category, amount, description)
        
        # Update team budget
        team.budget -= amount
        self.db.update_team(team_id, team)
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "team_id": team_id,
            "amount": amount,
            "category": category,
            "remaining_budget": team.budget,
            "timestamp": datetime.now().isoformat()
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
        
        transactions = self.db.get_budget_transactions(team_id)
        category_totals: Dict[str, float] = {}
        for tx in transactions:
            tx_category = str(tx.get("category") or "general")
            category_totals[tx_category] = category_totals.get(tx_category, 0.0) + float(tx.get("amount") or 0.0)

        allocations = [
            {
                "category": category,
                "allocated": amount,
                "used": amount,
                "remaining": 0.0
            }
            for category, amount in sorted(category_totals.items())
        ]

        total_expenditure = float((details or {}).get("total_expenditure", 0.0))

        return {
            "team_id": team_id,
            "team_name": team.name,
            "total_budget": team.budget + total_expenditure,  # Original + spent
            "allocated": allocations,
            "available": team.budget,
            "monthly_income": self._estimate_annual_income(team) / 12,
            "monthly_expenditure": total_expenditure / 12
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
    
    def _log_team_change(
        self,
        team_id: int,
        changes: Dict[str, Any],
        actor_id: Optional[str] = None,
        action: str = "team_updated"
    ) -> None:
        """Log team changes to audit trail"""
        self.db.add_team_audit_log(team_id, action, changes, actor_id=actor_id)

    def _facility_upgrade_cost(self, tier: str) -> float:
        """Facility upgrades scale by tier to preserve progression balance."""
        base = {
            "TIER_1": 6_000_000,
            "TIER_2": 3_000_000,
            "TIER_3": 1_500_000,
        }
        return float(base.get(tier, 3_000_000))


__all__ = ["TeamService"]
