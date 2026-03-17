"""
Team Management Tests (UC-11 to UC-14)

Tests for team CRUD operations, budget management, and permission tracking.
"""

import sys
from pathlib import Path
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database_manager import DatabaseManager
from database.models import Team, Driver
from services.team_service import TeamService
from tools.team_name_generator import generate_team_name
from datetime import datetime


@pytest.fixture(scope="module")
def team_id():
    """Create one team for tests that require a team id fixture."""
    created_ids = test_team_creation()
    return created_ids[0]


def test_team_creation():
    """UC-12: Test team creation with initial provisioning"""
    print("\n=== UC-12: Create New Team ===\n")
    
    db = DatabaseManager()
    service = TeamService(db)
    
    # Generate realistic team names using Faker
    tier_1_name = generate_team_name("SINGLE_SEATER")
    
    # Test Tier 1 team creation
    result = service.create_team(
        name=tier_1_name,
        discipline="SINGLE_SEATER",
        nationality="GB",
        tier="TIER_1",
        team_principal="John Smith",
        headquarters="Silverstone, UK"
    )
    
    print(f"[OK] Team Created:")
    print(f"  ID: {result['id']}")
    print(f"  Name: {result['name']}")
    print(f"  Discipline: {result['discipline']}")
    print(f"  Tier: {result['tier']}")
    print(f"  Initial Budget: €{result['initial_budget']:,.0f}")
    print(f"  Staff Limit: {result['staff_limit']}")
    print(f"  Driver Slots: {result['driver_slots']}")
    print(f"  Message: {result['message']}")
    
    # Test different tiers
    tier_2_name = generate_team_name("SPRINT_RALLYCROSS")
    team_id_2 = service.create_team(
        name=tier_2_name,
        discipline="SPRINT_RALLYCROSS",
        tier="TIER_2"
    )
    
    print(f"\n[OK] Tier 2 Team Created:")
    print(f"  ID: {team_id_2['id']}")
    print(f"  Budget: €{team_id_2['initial_budget']:,.0f}")
    
    tier_3_name = generate_team_name("DRAG_ACCELERATION")
    team_id_3 = service.create_team(
        name=tier_3_name,
        discipline="DRAG_ACCELERATION",
        tier="TIER_3"
    )
    
    print(f"\n[OK] Tier 3 Team Created:")
    print(f"  ID: {team_id_3['id']}")
    print(f"  Budget: €{team_id_3['initial_budget']:,.0f}")
    
    return result['id'], team_id_2['id'], team_id_3['id']


def test_read_team_details(team_id):
    """UC-11: Test reading full team profile"""
    print("\n=== UC-11: Read Team Details ===\n")
    
    db = DatabaseManager()
    service = TeamService(db)
    
    details = service.get_team_details(team_id)
    
    if not details:
        print(f"[FAIL] Team {team_id} not found")
        return
    
    print(f"[OK] Team Profile Retrieved:")
    print(f"\n  General Information:")
    print(f"    Name: {details['name']}")
    print(f"    Discipline: {details['discipline']}")
    print(f"    Nationality: {details['nationality']}")
    print(f"    Tier: {details['tier']}")
    print(f"    Founded: {details['founded_year']}")
    print(f"    Team Principal: {details['team_principal']}")
    
    print(f"\n  Financial Status:")
    print(f"    Total Budget: €{details['budget']:,.0f}")
    print(f"    Annual Income (est.): €{details['annual_income']:,.0f}")
    print(f"    Total Expenditure: €{details['total_expenditure']:,.0f}")
    print(f"    Available Budget: €{details['available_budget']:,.0f}")
    
    print(f"\n  Performance:")
    print(f"    Total Wins: {details['total_wins']}")
    print(f"    Total Podiums: {details['total_podiums']}")
    print(f"    Championships: {details['championships']}")
    print(f"    Operations Rating: {details['operations_rating']}/100")
    
    print(f"\n  Roster:")
    print(f"    Drivers: {len(details['drivers'])}")
    for driver in details['drivers']:
        print(f"      - {driver['name']} (#{driver['id']}) - Speed: {driver['current_rating']}/100")
    
    print(f"    Staff: {details['staff_count']} members")


def test_update_team(team_id):
    """UC-14: Test updating team attributes"""
    print("\n=== UC-14: Update Team Attributes ===\n")
    
    db = DatabaseManager()
    service = TeamService(db)
    
    updates = {
        "team_principal": "Jane Doe",
        "biography": "A competitive racing team with strong technical expertise"
    }
    
    result = service.update_team(team_id, updates)
    
    print(f"[OK] Team Updated:")
    print(f"  Team ID: {result['id']}")
    print(f"  Team Name: {result['name']}")
    print(f"  Updated At: {result['updated_at']}")
    print(f"\n  Changes Made:")
    for field, change in result['changes'].items():
        print(f"    {field}:")
        print(f"      Old: {change['old']}")
        print(f"      New: {change['new']}")
    print(f"\n  {result['message']}")


def test_budget_management(team_id):
    """Test budget allocation and tracking"""
    print("\n=== Budget Management ===\n")
    
    db = DatabaseManager()
    service = TeamService(db)
    
    # Get initial budget status
    budget = service.get_budget_status(team_id)
    
    print(f"[OK] Initial Budget Status:")
    print(f"  Team: {budget['team_name']}")
    print(f"  Total Budget: €{budget['total_budget']:,.0f}")
    print(f"  Available: €{budget['available']:,.0f}")
    print(f"  Monthly Income (est.): €{budget['monthly_income']:,.0f}")
    print(f"  Monthly Expenditure (est.): €{budget['monthly_expenditure']:,.0f}")
    
    print(f"\n  Allocations:")
    for alloc in budget['allocated']:
        print(f"    {alloc['category']}:")
        print(f"      Allocated: €{alloc['allocated']:,.0f}")
        print(f"      Used: €{alloc['used']:,.0f}")
        print(f"      Remaining: €{alloc['remaining']:,.0f}")
    
    # Test budget allocation
    try:
        transaction = service.allocate_budget(
            team_id,
            "staff",
            1_000_000,
            "New chief engineer"
        )
        
        print(f"\n[OK] Budget Allocated:")
        print(f"  Category: {transaction['category']}")
        print(f"  Amount: €{transaction['amount']:,.0f}")
        print(f"  Remaining: €{transaction['remaining_budget']:,.0f}")
        print(f"  Timestamp: {transaction['timestamp']}")
        
    except ValueError as e:
        print(f"[FAIL] Budget allocation failed: {e}")


def test_budget_constraints(team_id):
    """Test budget constraint validation"""
    print("\n=== Budget Constraint Validation ===\n")
    
    db = DatabaseManager()
    service = TeamService(db)
    
    # Try to allocate more than available budget
    team = db.get_team(team_id)
    
    print(f"  Team {team.name} Budget: €{team.budget:,.0f}")
    
    try:
        # Try to allocate more than available
        transaction = service.allocate_budget(
            team_id,
            "facility_upgrade",
            team.budget + 1_000_000,
            "Major facility upgrade"
        )
        print(f"[FAIL] Budget constraint not enforced!")
        
    except ValueError as e:
        print(f"[OK] Budget constraint properly enforced:")
        print(f"  Error: {e}")


def test_tier_system():
    """Test team tier system and budget caps"""
    print("\n=== Team Tier System ===\n")
    
    db = DatabaseManager()
    service = TeamService(db)
    
    tiers = ["TIER_1", "TIER_2", "TIER_3"]
    
    print("Budget and Staff Limits by Tier:")
    for tier in tiers:
        budget = service.TIER_BUDGETS[tier]
        staff_limit = service.TIER_STAFF_LIMITS[tier]
        print(f"\n  {tier}:")
        print(f"    Budget Cap: €{budget:,.0f}")
        print(f"    Staff Limit: {staff_limit} members")


def test_discipline_driver_slots():
    """Test driver slots by discipline"""
    print("\n=== Driver Slots by Discipline ===\n")
    
    db = DatabaseManager()
    service = TeamService(db)
    
    for discipline, slots in service.DRIVER_SLOTS_PER_DISCIPLINE.items():
        print(f"  {discipline}: {slots} driver slot(s)")


def main():
    """Run all team management tests"""
    print("\n" + "="*70)
    print("TEAM MANAGEMENT TESTS (UC-11 to UC-14)")
    print("="*70)
    
    # Test team creation
    team_ids = test_team_creation()
    tier1_id, tier2_id, tier3_id = team_ids
    
    # Test reading team details
    test_read_team_details(tier1_id)
    
    # Test updating team
    test_update_team(tier1_id)
    
    # Test budget management
    test_budget_management(tier1_id)
    
    # Test budget constraints
    test_budget_constraints(tier1_id)
    
    # Test tier system
    test_tier_system()
    
    # Test driver slots
    test_discipline_driver_slots()
    
    print("\n" + "="*70)
    print("[OK] All Team Management Tests Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
