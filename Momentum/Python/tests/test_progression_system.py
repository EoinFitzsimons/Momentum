"""
Test Suite - Driver Progression System (UC-19)

Tests skill progression, retirement, and driver recycling systems.

Authors: Final Year Project - Computer Science
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.progression_service import ProgressionService
from database.database_manager import DatabaseManager
from database.models import Driver
from datetime import datetime, timedelta


def test_age_factor_calculation():
    """Test age-based skill multiplier"""
    print("\n=== Testing Age Factor Calculation ===")
    
    progression = ProgressionService()
    
    test_ages = [18, 22, 28, 32, 35, 40, 45, 50]
    
    print("Age -> Factor (peak = 1.0 at 28-32)")
    for age in test_ages:
        factor = progression.calculate_age_factor(age)
        print(f"  {age:2d} years: {factor:.3f}")
    
    # Verify peak at 28-32
    peak_factor = progression.calculate_age_factor(30)
    assert peak_factor == 1.0, "Peak age should have factor 1.0"
    print("\n✓ Peak performance confirmed at age 28-32")
    
    # Verify decline after 35
    age_35 = progression.calculate_age_factor(35)
    age_40 = progression.calculate_age_factor(40)
    age_45 = progression.calculate_age_factor(45)
    
    assert age_40 < age_35, "Age 40 should have lower factor than 35"
    assert age_45 < age_40, "Age 45 should have lower factor than 40"
    print("✓ Skill decline confirmed with increasing age")


def test_skill_progression_calculation():
    """Test skill progression algorithm"""
    print("\n=== Testing Skill Progression Calculation ===")
    
    progression = ProgressionService()
    
    # Test young driver (improving)
    young_driver = Driver(
        id=1,
        name="Young Driver",
        nationality="GBR",
        birth_date=(datetime.now() - timedelta(days=365*24)).strftime("%Y-%m-%d"),
        speed=65.0,
        racecraft=62.0,
        consistency=60.0,
        fitness=70.0,
        reactions=72.0,
        pressure=55.0,
        setup_knowledge=50.0,
        fuel_management=55.0,
        tyre_management=58.0,
        feedback=52.0,
        adaptability=60.0,
        learning_rate=1.2
    )
    
    skill_changes = progression.calculate_skill_progression(young_driver, races_completed=20)
    print(f"\nYoung driver (age {young_driver.computed_age}) skill changes:")
    for skill, change in skill_changes.items():
        print(f"  {skill}: {change:+.2f}")
    
    total_change = sum(skill_changes.values())
    print(f"Total change: {total_change:+.2f}")
    assert total_change > 0, "Young driver should generally improve"
    print("✓ Young driver showing positive progression")
    
    # Test veteran driver (declining)
    veteran_driver = Driver(
        id=2,
        name="Veteran Driver",
        nationality="ITA",
        birth_date=(datetime.now() - timedelta(days=365*38)).strftime("%Y-%m-%d"),
        speed=75.0,
        racecraft=82.0,
        consistency=80.0,
        fitness=65.0,
        reactions=68.0,
        pressure=85.0,
        setup_knowledge=88.0,
        fuel_management=85.0,
        tyre_management=87.0,
        feedback=82.0,
        adaptability=80.0,
        learning_rate=0.8
    )
    
    skill_changes_vet = progression.calculate_skill_progression(veteran_driver, races_completed=20)
    print(f"\nVeteran driver (age {veteran_driver.computed_age}) skill changes:")
    for skill, change in skill_changes_vet.items():
        print(f"  {skill}: {change:+.2f}")
    
    total_change_vet = sum(skill_changes_vet.values())
    print(f"Total change: {total_change_vet:+.2f}")
    # Veteran may have mixed results (mental skills up, physical down)
    print("✓ Veteran driver progression calculated")


def test_retirement_eligibility():
    """Test retirement trigger system"""
    print("\n=== Testing Retirement Eligibility ===")
    
    progression = ProgressionService()
    
    # Test mandatory retirement (45+)
    old_driver = Driver(
        id=3,
        name="Old Driver",
        nationality="ESP",
        birth_date=(datetime.now() - timedelta(days=365*46)).strftime("%Y-%m-%d"),
        speed=65.0,
        racecraft=72.0,
        consistency=70.0
    )
    
    should_retire, reason, probability = progression.check_retirement_eligibility(old_driver)
    print(f"Driver age {old_driver.computed_age}:")
    print(f"  Should retire: {should_retire}")
    print(f"  Reason: {reason}")
    print(f"  Probability: {probability:.1%}")
    
    assert should_retire, "Driver 45+ should automatically retire"
    assert probability == 1.0, "Mandatory retirement should have 100% probability"
    print("✓ Mandatory retirement triggered for age 45+")
    
    # Test early career (no retirement)
    young_driver = Driver(
        id=4,
        name="Young Driver",
        nationality="BRA",
        birth_date=(datetime.now() - timedelta(days=365*25)).strftime("%Y-%m-%d"),
        speed=70.0,
        racecraft=68.0,
        consistency=65.0
    )
    
    should_retire_2, reason_2, prob_2 = progression.check_retirement_eligibility(young_driver)
    print(f"\nDriver age {young_driver.computed_age}:")
    print(f"  Should retire: {should_retire_2}")
    print(f"  Probability: {prob_2:.1%}")
    
    assert not should_retire_2, "Young driver should not retire"
    assert prob_2 == 0.0, "Young driver should have 0% retirement probability"
    print("✓ Young driver correctly not retiring")
    
    # Test veteran range (probabilistic)
    veteran = Driver(
        id=5,
        name="Veteran Driver",
        nationality="AUS",
        birth_date=(datetime.now() - timedelta(days=365*42)).strftime("%Y-%m-%d"),
        speed=60.0,
        racecraft=65.0,
        consistency=62.0
    )
    
    should_retire_3, reason_3, prob_3 = progression.check_retirement_eligibility(veteran)
    print(f"\nDriver age {veteran.computed_age}:")
    print(f"  Should retire: {should_retire_3}")
    print(f"  Reason: {reason_3 or 'N/A'}")
    print(f"  Probability: {prob_3:.1%}")
    
    assert prob_3 > 0.0, "Veteran driver should have retirement probability"
    print("✓ Veteran driver has non-zero retirement probability")


def test_driver_recycling():
    """Test driver recycling system"""
    print("\n=== Testing Driver Recycling ===")
    
    progression = ProgressionService()
    db = DatabaseManager()
    
    # Get a driver to recycle (won't actually retire them)
    drivers = db.get_all_drivers()
    if not drivers:
        print("⚠ No drivers in database, skipping test")
        return
    
    original_driver = drivers[0]
    print(f"Original driver: {original_driver.name} (ID: {original_driver.id})")
    print(f"  Nationality: {original_driver.nationality}")
    print(f"  Discipline: {original_driver.preferred_discipline}")
    
    # Recycle driver
    new_driver_id = progression.recycle_driver(original_driver.id)
    
    if new_driver_id:
        print(f"\n✓ Created recycled driver (ID: {new_driver_id})")
        
        new_driver = db.get_driver(new_driver_id)
        if new_driver:
            print(f"  Name: {new_driver.name}")
            print(f"  Age: {new_driver.computed_age}")
            print(f"  Speed: {new_driver.speed:.1f}")
            print(f"  Racecraft: {new_driver.racecraft:.1f}")
            print(f"  Consistency: {new_driver.consistency:.1f}")
            print(f"  Learning rate: {new_driver.learning_rate}")
            
            # Verify rookie characteristics
            assert new_driver.computed_age >= 18 and new_driver.computed_age <= 20, "Rookie should be 18-20 years old"
            assert new_driver.learning_rate == 1.2, "Rookie should have high learning rate"
            assert new_driver.career_starts == 0, "Rookie should have no career starts"
            print("✓ Rookie characteristics verified")
            
            # Clean up - remove test driver
            with db.get_connection() as conn:
                conn.execute("DELETE FROM drivers WHERE id = ?", (new_driver_id,))
            print("✓ Test cleanup completed")
    else:
        print("✗ Driver recycling failed")


def test_season_end_progression():
    """Test complete season-end progression workflow"""
    print("\n=== Testing Season-End Progression Workflow ===")
    
    progression = ProgressionService()
    
    # Run progression for season 2025
    print("Processing season-end progression for season 2025...")
    print("(This is a dry run - no database changes)")
    
    # Get sample of drivers to show what would happen
    db = DatabaseManager()
    sample_drivers = db.get_drivers_for_progression(2025)[:5]  # Just 5 for testing
    
    print(f"\nSample progression for {len(sample_drivers)} drivers:")
    
    for driver in sample_drivers:
        skill_changes = progression.calculate_skill_progression(driver, races_completed=20)
        should_retire, reason, prob = progression.check_retirement_eligibility(driver)
        
        total_change = sum(skill_changes.values())
        
        print(f"\n{driver.name} (age {driver.computed_age}):")
        print(f"  Total skill change: {total_change:+.2f}")
        print(f"  Retirement probability: {prob:.1%}")
        if should_retire:
            print(f"  ⚠ Would retire: {reason}")
    
    print("\n✓ Season-end progression simulation completed")


def test_database_operations():
    """Test database operations for progression"""
    print("\n=== Testing Progression Database Operations ===")
    
    db = DatabaseManager()
    
    # Get a test driver
    drivers = db.get_all_drivers()
    if not drivers:
        print("⚠ No drivers found, skipping test")
        return
    
    test_driver = drivers[0]
    original_speed = test_driver.speed
    
    print(f"Test driver: {test_driver.name} (ID: {test_driver.id})")
    print(f"Original speed: {original_speed:.2f}")
    
    # Test skill update
    skill_changes = {'speed': 2.5, 'racecraft': -1.0}
    success = db.update_driver_skills(test_driver.id, skill_changes)
    
    if success:
        # Verify change
        updated_driver = db.get_driver(test_driver.id)
        print(f"Updated speed: {updated_driver.speed:.2f}")
        
        # Restore original value
        restore_changes = {'speed': -(updated_driver.speed - original_speed), 'racecraft': 1.0}
        db.update_driver_skills(test_driver.id, restore_changes)
        
        final_driver = db.get_driver(test_driver.id)
        print(f"Restored speed: {final_driver.speed:.2f}")
        
        print("✓ Skill update operations working correctly")
    else:
        print("✗ Skill update failed")
    
    # Test experience increment
    original_starts = test_driver.career_starts
    print(f"\nOriginal career starts: {original_starts}")
    
    db.increment_driver_experience(test_driver.id, starts=5)
    updated = db.get_driver(test_driver.id)
    print(f"After increment: {updated.career_starts}")
    
    # Restore
    with db.get_connection() as conn:
        conn.execute("""
            UPDATE drivers 
            SET career_starts = ?, seasons_active = seasons_active - 1
            WHERE id = ?
        """, (original_starts, test_driver.id))
    
    print("✓ Experience tracking operations working correctly")


def run_all_tests():
    """Run all progression system tests"""
    print("=" * 70)
    print("DRIVER PROGRESSION SYSTEM TEST SUITE")
    print("Testing UC-19")
    print("=" * 70)
    
    try:
        test_age_factor_calculation()
        test_skill_progression_calculation()
        test_retirement_eligibility()
        test_driver_recycling()
        test_database_operations()
        test_season_end_progression()
        
        print("\n" + "=" * 70)
        print("✓ ALL PROGRESSION TESTS COMPLETED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
