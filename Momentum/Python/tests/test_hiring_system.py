"""
Test Suite - Hiring & Contract Management (UC-15 to UC-18)

Tests hiring service, contract validation, budget checks, and salary cap enforcement.

Authors: Final Year Project - Computer Science
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.hiring_service import HiringService
from database.database_manager import DatabaseManager
from database.models import Driver, Team
from datetime import datetime, timedelta


def test_salary_estimation():
    """Test driver salary estimation algorithm"""
    print("\n=== Testing Salary Estimation ===")
    
    hiring = HiringService()
    
    # Create test driver
    test_driver = Driver(
        id=999,
        name="Test Driver",
        nationality="GBR",
        birth_date=(datetime.now() - timedelta(days=365*28)).strftime("%Y-%m-%d"),
        speed=85.0,
        racecraft=82.0,
        consistency=80.0,
        career_points=500,
        career_podiums=10,
        seasons_active=5,
        preferred_discipline="SINGLE_SEATER"
    )
    
    salary = hiring.estimate_driver_salary(test_driver, "SINGLE_SEATER")
    print(f"✓ Estimated salary for skilled driver (avg 82.3): €{salary:,.0f}")
    
    # Test rookie
    rookie = Driver(
        id=998,
        name="Rookie Driver",
        nationality="USA",
        birth_date=(datetime.now() - timedelta(days=365*20)).strftime("%Y-%m-%d"),
        speed=55.0,
        racecraft=50.0,
        consistency=52.0,
        career_points=0,
        career_podiums=0,
        seasons_active=0,
        preferred_discipline="SINGLE_SEATER"
    )
    
    rookie_salary = hiring.estimate_driver_salary(rookie, "SINGLE_SEATER")
    print(f"✓ Estimated salary for rookie (avg 52.3): €{rookie_salary:,.0f}")
    
    # Verify rookie earns less
    assert rookie_salary < salary, "Rookie should earn less than experienced driver"
    print("✓ Rookie salary correctly lower than experienced driver")


def test_salary_cap_enforcement():
    """Test salary cap validation"""
    print("\n=== Testing Salary Cap Enforcement ===")
    
    hiring = HiringService()
    db = DatabaseManager()
    
    # Get a real team
    teams = db.get_teams_by_discipline("SINGLE_SEATER")
    if not teams:
        print("⚠ No teams found, skipping test")
        return
    
    team = teams[0]
    print(f"Testing with team: {team.name} (ID: {team.id})")
    
    # Check current salary commitment
    current_commitment = hiring.calculate_team_salary_commitment(team.id)
    print(f"✓ Current salary commitment: €{current_commitment:,.0f}")
    
    # Check salary cap compliance
    is_compliant, current, cap = hiring.check_salary_cap_compliance(team.id)
    print(f"✓ Salary cap for {team.discipline}: €{cap:,.0f}")
    print(f"✓ Current usage: €{current:,.0f} ({(current/cap)*100:.1f}%)")
    print(f"✓ Compliant: {is_compliant}")
    
    # Test with additional salary that would exceed cap
    # Since current is €0, we need to add MORE than the cap to fail
    excessive_salary = cap * 1.1  # 110% of cap
    is_compliant_2, current_2, cap_2 = hiring.check_salary_cap_compliance(
        team.id, 
        excessive_salary
    )
    
    if not is_compliant_2:
        print(f"✓ Correctly rejected excessive salary of €{excessive_salary:,.0f}")
    else:
        print(f"⚠ Salary cap validation failed - should reject €{excessive_salary:,.0f} (cap: €{cap:,.0f})")
    
    # Test with reasonable salary that should pass
    reasonable_salary = cap * 0.15  # 15% of cap
    is_compliant_3, current_3, cap_3 = hiring.check_salary_cap_compliance(
        team.id,
        reasonable_salary
    )
    
    if is_compliant_3:
        print(f"✓ Correctly accepted reasonable salary of €{reasonable_salary:,.0f}")
    else:
        print(f"⚠ Incorrectly rejected reasonable salary")


def test_available_drivers_endpoint():
    """Test UC-15: Get available drivers"""
    print("\n=== Testing UC-15: Get Available Drivers ===")
    
    hiring = HiringService()
    
    # Get all available drivers
    drivers, total = hiring.get_available_drivers()
    print(f"✓ Found {total} total available drivers")
    print(f"✓ Returned {len(drivers)} drivers on page 1")
    
    if drivers:
        sample = drivers[0]
        print(f"\nSample driver:")
        print(f"  Name: {sample['name']}")
        print(f"  Age: {sample['age']}")
        print(f"  Rating: {(sample['speed'] + sample['racecraft'] + sample['consistency'])/3:.1f}")
        print(f"  Estimated Salary: €{sample['estimated_salary']:,.0f}")
    
    # Test with discipline filter
    single_seater_drivers, ss_total = hiring.get_available_drivers(
        discipline="SINGLE_SEATER"
    )
    print(f"\n✓ Single Seater drivers: {ss_total}")
    
    # Test with rating filter
    high_rated, hr_total = hiring.get_available_drivers(min_rating=70.0)
    print(f"✓ High-rated drivers (70+): {hr_total}")
    
    # Test pagination
    page2_drivers, _ = hiring.get_available_drivers(page=2, page_size=10)
    print(f"✓ Page 2 results: {len(page2_drivers)} drivers")


def test_available_staff_endpoint():
    """Test UC-17: Get available staff"""
    print("\n=== Testing UC-17: Get Available Staff ===")
    
    hiring = HiringService()
    
    # Get all available staff
    staff, total = hiring.get_available_staff()
    print(f"✓ Found {total} total available staff")
    print(f"✓ Returned {len(staff)} staff on page 1")
    
    if staff:
        sample = staff[0]
        print(f"\nSample staff:")
        print(f"  Name: {sample['name']}")
        print(f"  Role: {sample['role']}")
        print(f"  Rating: {sample['rating']:.1f}")
        print(f"  Estimated Salary: €{sample['estimated_salary']:,.0f}")
    
    # Test with role filter
    engineers, eng_total = hiring.get_available_staff(role="RACE_ENGINEER")
    print(f"\n✓ Race Engineers: {eng_total}")
    
    # Test with rating filter
    top_staff, top_total = hiring.get_available_staff(min_rating=75.0)
    print(f"✓ Top-rated staff (75+): {top_total}")


def test_driver_contract_signing():
    """Test UC-16: Sign driver contract"""
    print("\n=== Testing UC-16: Driver Contract Signing ===")
    
    hiring = HiringService()
    db = DatabaseManager()
    
    # Get an available driver
    drivers, total = hiring.get_available_drivers(page_size=1)
    if not drivers:
        print("⚠ No available drivers, skipping test")
        return None
    
    driver = drivers[0]
    print(f"Test driver: {driver['name']} (ID: {driver['id']})")
    
    # Get a team with sufficient budget
    teams = db.get_teams_by_discipline("SINGLE_SEATER")
    team = None
    for t in teams:
        if t.budget > 20_000_000:  # Need sufficient budget
            team = t
            break
    
    if not team:
        print("⚠ No team with sufficient budget, skipping test")
        return None
    
    print(f"Test team: {team.name} (ID: {team.id}, Budget: €{team.budget:,.0f})")
    
    # Calculate a reasonable salary
    salary = driver['estimated_salary']
    contract_length = 2
    
    print(f"\nAttempting to sign contract:")
    print(f"  Salary: €{salary:,.0f}/year")
    print(f"  Length: {contract_length} seasons")
    print(f"  Total value: €{salary * contract_length:,.0f}")
    
    # Test contract validation first
    is_valid, error_msg = hiring.validate_contract_budget(
        team.id, salary, contract_length
    )
    
    if is_valid:
        print(f"✓ Contract validation passed")
        
        # Sign contract (note: this modifies database)
        success, message, details = hiring.sign_driver_contract(
            team_id=team.id,
            driver_id=driver['id'],
            contract_length=contract_length,
            salary=salary
        )
        
        if success:
            print(f"✓ Contract signed successfully")
            print(f"  Signing bonus paid: €{details['signing_bonus_paid']:,.0f}")
            print(f"  Remaining budget: €{details['remaining_budget']:,.0f}")
            
            # Return contract details for use in release test
            return {
                'driver_id': driver['id'],
                'driver_name': driver['name'],
                'team_id': team.id,
                'team_name': team.name,
                'signing_bonus': details['signing_bonus_paid']
            }
        else:
            print(f"✗ Contract signing failed: {message}")
    else:
        print(f"✗ Contract validation failed: {error_msg}")
    
    return None


def test_staff_contract_signing():
    """Test UC-18: Sign staff contract"""
    print("\n=== Testing UC-18: Staff Contract Signing ===")
    
    hiring = HiringService()
    db = DatabaseManager()
    
    # Get an available staff member
    staff, total = hiring.get_available_staff(page_size=1)
    if not staff:
        print("⚠ No staff in database - creating test staff member")
        # Create a test staff member
        from database.models import StaffMember
        with db.get_connection() as conn:
            conn.execute("""
                INSERT INTO staff_members (name, role, rating)
                VALUES (?, ?, ?)
            """, ("Test Engineer", "RACE_ENGINEER", 75.0))
            conn.commit()
        
        # Try again
        staff, total = hiring.get_available_staff(page_size=1)
        if not staff:
            print("✗ Failed to create test staff")
            return
        print("✓ Created test staff member")
    
    staff_member = staff[0]
    print(f"Test staff: {staff_member['name']} (ID: {staff_member['id']}, Role: {staff_member['role']})")
    
    # Get a team with budget
    teams = db.get_teams_by_discipline("SINGLE_SEATER")
    team = None
    for t in teams:
        if t.budget > 5_000_000:
            team = t
            break
    
    if not team:
        print("⚠ No team with sufficient budget, skipping test")
        return
    
    print(f"Test team: {team.name} (ID: {team.id}, Budget: €{team.budget:,.0f})")
    
    # Use estimated salary
    salary = staff_member['estimated_salary']
    contract_length = 3
    
    print(f"\nAttempting to sign staff contract:")
    print(f"  Salary: €{salary:,.0f}/year")
    print(f"  Length: {contract_length} seasons")
    
    # Sign contract
    success, message, details = hiring.sign_staff_contract(
        team_id=team.id,
        staff_id=staff_member['id'],
        contract_length=contract_length,
        salary=salary
    )
    
    if success:
        print(f"✓ Staff contract signed successfully")
        print(f"  Signing bonus paid: €{details['signing_bonus_paid']:,.0f}")
        print(f"  Remaining budget: €{details['remaining_budget']:,.0f}")
        
        # Clean up
        db.release_staff(staff_member['id'])
        db.update_team_budget(team.id, details['signing_bonus_paid'])
        print(f"✓ Test cleanup completed")
    else:
        print(f"✗ Staff contract signing failed: {message}")


def test_contract_release(contract_info=None):
    """Test contract release with buyout"""
    print("\n=== Testing Contract Release ===")
    
    hiring = HiringService()
    db = DatabaseManager()
    
    # Use the driver from the signing test if provided
    if contract_info:
        print(f"Using driver from contract signing test: {contract_info['driver_name']}")
        driver = db.get_driver(contract_info['driver_id'])
        team = db.get_team(contract_info['team_id'])
        
        if not driver or not team:
            print("✗ Failed to retrieve contracted driver/team")
            return
        
        print(f"Test driver: {driver.name} (ID: {driver.id})")
        print(f"Team: {team.name} (ID: {team.id})")
        print(f"Current salary: €{driver.salary or 0:,.0f}")
        print(f"Contract length: {driver.contract_length or 0} seasons")
        
        # Calculate expected buyout
        if driver.salary and driver.contract_length:
            remaining_value = driver.salary * driver.contract_length
            expected_buyout = remaining_value * 0.5
            print(f"Expected buyout (50%): €{expected_buyout:,.0f}")
            
            if team.budget > expected_buyout:
                print("\n✓ Team has sufficient budget for buyout")
                
                # Actually test the release
                success, message, details = hiring.release_personnel_contract(
                    team_id=team.id,
                    personnel_id=driver.id,
                    personnel_type='driver',
                    buyout_percentage=0.5
                )
                
                if success:
                    print(f"✓ Driver released successfully")
                    print(f"  Buyout cost: €{details['buyout_cost']:,.0f}")
                    print(f"  Remaining budget: €{details['remaining_budget']:,.0f}")
                    
                    # Verify driver is available again
                    released_driver = db.get_driver(driver.id)
                    if released_driver.current_team_id is None:
                        print(f"✓ Driver confirmed as available in market")
                    
                    # Restore budget for future tests
                    db.update_team_budget(team.id, details['buyout_cost'] + contract_info['signing_bonus'])
                    print(f"✓ Test cleanup completed")
                else:
                    print(f"✗ Release failed: {message}")
            else:
                print("\n⚠ Team has insufficient budget for buyout")
        else:
            print("⚠ Driver missing salary/contract info")
    else:
        # Fallback to old behavior
        print("⚠ No contract info provided from signing test, skipping release test")


def run_all_tests():
    """Run all hiring and contract tests"""
    print("=" * 70)
    print("HIRING & CONTRACT MANAGEMENT TEST SUITE")
    print("Testing UC-15, UC-16, UC-17, UC-18")
    print("=" * 70)
    
    try:
        test_salary_estimation()
        test_salary_cap_enforcement()
        test_available_drivers_endpoint()
        test_available_staff_endpoint()
        
        # Sign contract and get details for release test
        contract_info = test_driver_contract_signing()
        test_staff_contract_signing()
        
        # Test release using the contracted driver
        test_contract_release(contract_info)
        
        print("\n" + "=" * 70)
        print("✓ ALL HIRING TESTS COMPLETED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
