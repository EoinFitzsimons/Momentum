"""
Component Integration Test

Quick test to verify component system is properly integrated into game flow.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from systems.world_state import GameWorld
from database.models.multi_discipline_models import MultiDisciplineTeam


def test_component_integration():
    """Test that components are created when player selects team"""
    
    print("=" * 60)
    print("COMPONENT INTEGRATION TEST")
    print("=" * 60)
    
    # Create game world
    world = GameWorld()
    
    print("\n1. Creating new game...")
    world.new_game("Test Player")
    print("   ✓ Game world created")
    
    # Create a test team
    print("\n2. Creating test team...")
    test_team = MultiDisciplineTeam(
        id=1,
        name="Test Racing Team",
        nationality="British",
        founded_year=2020,
        headquarters="Silverstone, UK",
        team_principal="John Smith",
        biography="Test team for component integration",
        founding_story="Founded in 2020 to test component systems",
        active_disciplines=["SINGLE_SEATER"],
        primary_discipline="SINGLE_SEATER",
        total_annual_budget=120.5
    )
    print(f"   ✓ Team created: {test_team.name}")
    print(f"   - Primary Discipline: {test_team.primary_discipline}")
    print(f"   - Budget: ${test_team.total_annual_budget}M")
    
    # Select team (this should trigger component initialization)
    print("\n3. Selecting team (should initialize components)...")
    # Note: select_team needs the team to exist in DB
    # For this test, we'll call the helper directly
    world.vehicle_helper.initialize_player_team_vehicles(test_team)
    
    # Check if components were created
    print("\n4. Verifying component creation...")
    if world.component_integration.race_cars:
        car_id = list(world.component_integration.race_cars.keys())[0]
        race_car = world.component_integration.race_cars[car_id]
        
        print(f"   ✓ RaceCar created successfully")
        print(f"   - Car ID: {race_car.car_id}")
        print(f"   - Team ID: {race_car.team_id}")
        print(f"   - Car Name: {race_car.car_name}")
        print(f"   - Discipline: {race_car.discipline}")
        
        print("\n5. Component Details:")
        if race_car.engine:
            print("   Engine:")
            print(f"     - {race_car.engine.configuration.value} {race_car.engine.displacement}L V{race_car.engine.cylinders}")
            print(f"     - Power: {race_car.engine.max_power_bhp} BHP")
        
        if race_car.aerodynamics:
            print("   Aerodynamics:")
            print(f"     - Drag Coefficient: {race_car.aerodynamics.drag_coefficient:.3f}")
        
        if race_car.chassis:
            print("   Chassis:")
            print(f"     - {race_car.chassis.material.value}, {race_car.chassis.weight_kg:.0f} kg")
        
        if race_car.tires:
            print("   Tires:")
            print(f"     - Tire set available: {race_car.tires is not None}")
        
        # Test component health UI
        print("\n6. Component Health Report:")
        health_ui = world.component_integration.get_component_health_ui(car_id)
        for component, data in health_ui.items():
            if component != "needs_replacement":
                print(f"   {component.replace('_', ' ').title()}: {data['percentage']}% ({data['status']})")
        
        # Test race session simulation
        print("\n7. Simulating Practice Session...")
        session_result = world.component_integration.simulate_race_session(
            vehicle_id=car_id,
            session_type="practice",
            duration_minutes=60,
            intensity=0.7
        )
        
        print(f"   ✓ Session completed")
        print(f"   - Performance Multiplier: {session_result['performance_multiplier']:.3f}")
        print(f"   - Components worn:")
        for component, wear in session_result['wear_report'].items():
            if wear > 0:
                print(f"     • {component}: {wear:.2%} wear")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    else:
        print("   ✗ ERROR: No race cars were created!")
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = test_component_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
