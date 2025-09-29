"""
Driver System Test Suite - Comprehensive Multi-Discipline Driver Testing

This module provides comprehensive testing for the new 50+ attribute driver system,
validating that drivers can compete across all racing disciplines with realistic
performance variations based on their aptitudes and skills.

Test Categories:
1. Driver Creation and Validation
2. Cross-Discipline Performance Testing  
3. Attribute System Validation
4. Racing Engine Integration Testing
5. Performance Scaling and Balance Testing

Authors: Final Year Project - Computer Science
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Driver
from examples.driver_examples import (
    create_formula_specialist, create_touring_car_battler,
    create_rally_legend, create_versatile_all_rounder
)
from core.disciplines.base_engine import BaseDisciplineEngine
from core.disciplines.single_seater_engine import SingleSeaterEngine
from core.disciplines.production_touring_engine import ProductionTouringEngine


class DriverSystemTester:
    """Comprehensive testing suite for the multi-discipline driver system"""
    
    def __init__(self):
        self.drivers = []
        self.engines = {}
        self.test_results = {}
        
    def setup_test_environment(self):
        """Initialize test drivers and racing engines"""
        print("Setting up test environment...")
        
        # Create test drivers
        self.drivers = [
            create_formula_specialist(),
            create_touring_car_battler(), 
            create_rally_legend(),
            create_versatile_all_rounder()
        ]
        
        # Initialize available racing engines
        self.engines = {
            "single_seater": SingleSeaterEngine(),
            "touring_car": ProductionTouringEngine()
        }
        
        print(f"✓ Created {len(self.drivers)} test drivers")
        print(f"✓ Initialized {len(self.engines)} racing engines")
        
    def test_driver_creation(self):
        """Test that all drivers are created with valid attribute ranges"""
        print("\n" + "="*60)
        print("TEST 1: Driver Creation and Attribute Validation")
        print("="*60)
        
        all_passed = True
        
        for i, driver in enumerate(self.drivers, 1):
            print(f"\nDriver {i}: {driver.name}")
            print("-" * 40)
            
            # Test basic properties
            assert hasattr(driver, 'name'), "Driver missing name"
            assert hasattr(driver, 'nationality'), "Driver missing nationality"
            assert hasattr(driver, 'age'), "Driver missing age"
            print(f"✓ Basic properties: {driver.name} ({driver.nationality}, {driver.age})")
            
            # Test core driving attributes (0-100 range)
            core_attrs = [
                'raw_speed', 'consistency', 'racecraft', 'overtaking',
                'defensive_driving', 'cornering_skill', 'braking_technique',
                'acceleration_control', 'spatial_awareness', 'vehicle_control'
            ]
            
            for attr in core_attrs:
                value = getattr(driver, attr)
                assert 0 <= value <= 100, f"{attr} out of range: {value}"
                
            print("✓ Core driving attributes valid (10 attributes checked)")
            
            # Test discipline aptitudes
            discipline_attrs = [
                'single_seater_aptitude', 'touring_car_aptitude', 'rally_aptitude',
                'street_racing_aptitude', 'drag_racing_aptitude', 
                'rallycross_aptitude', 'endurance_aptitude'
            ]
            
            for attr in discipline_attrs:
                value = getattr(driver, attr)
                assert 0 <= value <= 100, f"{attr} out of range: {value}"
                
            print("✓ Discipline aptitudes valid (7 disciplines checked)")
            
            # Test that preferred discipline has high aptitude
            preferred = driver.preferred_discipline
            preferred_aptitude = getattr(driver, f"{preferred}_aptitude")
            if preferred_aptitude < 70:
                print(f"⚠ Warning: Low aptitude ({preferred_aptitude}) for preferred discipline ({preferred})")
            else:
                print(f"✓ Preferred discipline aptitude: {preferred_aptitude}")
                
        print(f"\n✓ All {len(self.drivers)} drivers passed creation validation")
        return all_passed
        
    def test_cross_discipline_performance(self):
        """Test driver performance ratings across all disciplines"""
        print("\n" + "="*60)
        print("TEST 2: Cross-Discipline Performance Testing")
        print("="*60)
        
        disciplines = ["single_seater", "touring_car", "rally", "street_racing", 
                      "drag_racing", "rallycross", "endurance"]
        
        performance_matrix = {}
        
        for driver in self.drivers:
            print(f"\n{driver.name} Performance Profile:")
            print("-" * 40)
            
            driver_performance = {}
            for discipline in disciplines:
                rating = driver.get_discipline_rating(discipline)
                driver_performance[discipline] = rating
                
                # Performance level categorization
                if rating >= 85:
                    level = "Elite"
                elif rating >= 75:
                    level = "Strong"
                elif rating >= 65:
                    level = "Competent"
                elif rating >= 55:
                    level = "Adequate"
                else:
                    level = "Weak"
                    
                print(f"{discipline.replace('_', ' ').title():15}: {rating:5.1f} ({level})")
                
            performance_matrix[driver.name] = driver_performance
            
            # Validate that preferred discipline is among top ratings
            preferred = driver.preferred_discipline
            preferred_rating = driver_performance[preferred]
            sorted_ratings = sorted(driver_performance.values(), reverse=True)
            
            if preferred_rating in sorted_ratings[:3]:
                print(f"✓ Preferred discipline ({preferred}) in top 3 ratings")
            else:
                print(f"⚠ Preferred discipline ({preferred}) not in top 3")
                
        self.test_results['performance_matrix'] = performance_matrix
        print(f"\n✓ Cross-discipline testing completed for {len(self.drivers)} drivers")
        
    def test_racing_engine_integration(self):
        """Test integration with racing engines"""
        print("\n" + "="*60)
        print("TEST 3: Racing Engine Integration Testing")
        print("="*60)
        
        for engine_name, engine in self.engines.items():
            print(f"\nTesting {engine_name.replace('_', ' ').title()} Engine:")
            print("-" * 40)
            
            # Test that engine can calculate performance for all drivers
            for driver in self.drivers:
                try:
                    performance = engine.calculate_base_performance(driver)
                    assert 0 <= performance <= 100, f"Performance out of range: {performance}"
                    print(f"✓ {driver.name}: {performance:.1f}")
                    
                except Exception as e:
                    print(f"✗ Error calculating performance for {driver.name}: {e}")
                    return False
                    
        print("\n✓ All racing engines successfully integrated")
        return True
        
    def test_attribute_weighting_consistency(self):
        """Test that attribute weighting produces consistent results"""
        print("\n" + "="*60)
        print("TEST 4: Attribute Weighting Consistency")
        print("="*60)
        
        # Test single seater engine attribute weights
        if "single_seater" in self.engines:
            engine = self.engines["single_seater"]
            weights = engine.get_attribute_weights()
            
            print("Single Seater Engine - Attribute Weights:")
            total_weight = sum(weights.values())
            print(f"Total weight sum: {total_weight:.3f}")
            
            # Check that weights sum to approximately 1.0
            assert 0.95 <= total_weight <= 1.05, f"Weights don't sum to 1.0: {total_weight}"
            print(f"✓ Weights properly normalized")
            
            # Check for key attributes having meaningful weights
            key_attributes = ['raw_speed', 'cornering_skill', 'single_seater_aptitude']
            for attr in key_attributes:
                if attr in weights and weights[attr] > 0.05:
                    print(f"✓ {attr}: {weights[attr]:.3f} (significant weight)")
                    
        # Test touring car engine attribute weights  
        if "touring_car" in self.engines:
            engine = self.engines["touring_car"]
            weights = engine.get_attribute_weights()
            
            print("\nTouring Car Engine - Attribute Weights:")
            total_weight = sum(weights.values())
            print(f"Total weight sum: {total_weight:.3f}")
            
            assert 0.95 <= total_weight <= 1.05, f"Weights don't sum to 1.0: {total_weight}"
            print(f"✓ Weights properly normalized")
            
        print("\n✓ Attribute weighting consistency validated")
        
    def test_performance_scaling(self):
        """Test that performance scales realistically across skill levels"""
        print("\n" + "="*60)
        print("TEST 5: Performance Scaling and Balance Testing")
        print("="*60)
        
        # Create drivers with different skill levels for comparison
        test_drivers = [
            Driver(
                id=100, name="Novice Driver", nationality="TST", age=20,
                raw_speed=40.0, consistency=35.0, racecraft=30.0,
                vehicle_control=45.0, spatial_awareness=40.0,
                single_seater_aptitude=35.0, touring_car_aptitude=40.0
            ),
            Driver(
                id=101, name="Average Driver", nationality="TST", age=25,
                raw_speed=65.0, consistency=60.0, racecraft=58.0,
                vehicle_control=62.0, spatial_awareness=64.0,
                single_seater_aptitude=60.0, touring_car_aptitude=65.0
            ),
            Driver(
                id=102, name="Expert Driver", nationality="TST", age=30,
                raw_speed=90.0, consistency=88.0, racecraft=92.0,
                vehicle_control=89.0, spatial_awareness=91.0,
                single_seater_aptitude=95.0, touring_car_aptitude=85.0
            )
        ]
        
        for engine_name, engine in self.engines.items():
            print(f"\n{engine_name.replace('_', ' ').title()} Performance Scaling:")
            
            performances = []
            for driver in test_drivers:
                perf = engine.calculate_base_performance(driver)
                performances.append(perf)
                print(f"{driver.name}: {perf:.1f}")
                
            # Validate that performance increases with skill level
            assert performances[0] < performances[1] < performances[2], \
                   "Performance doesn't scale with skill level"
            print("✓ Performance scales correctly with skill level")
            
            # Check reasonable performance spread
            spread = performances[2] - performances[0]
            assert spread >= 20, f"Performance spread too small: {spread:.1f}"
            print(f"✓ Performance spread adequate: {spread:.1f} points")
            
        print("\n✓ Performance scaling validation completed")
        
    def run_comprehensive_test_suite(self):
        """Run all test categories"""
        print("COMPREHENSIVE DRIVER SYSTEM TEST SUITE")
        print("=" * 60)
        print("Testing new 50+ attribute multi-discipline driver system")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_test_environment()
            
            # Run test categories
            test_methods = [
                self.test_driver_creation,
                self.test_cross_discipline_performance,
                self.test_racing_engine_integration,
                self.test_attribute_weighting_consistency,
                self.test_performance_scaling
            ]
            
            passed_tests = 0
            total_tests = len(test_methods)
            
            for test_method in test_methods:
                try:
                    result = test_method()
                    if result is not False:
                        passed_tests += 1
                except Exception as e:
                    print(f"✗ Test failed with error: {e}")
                    
            # Final summary
            print("\n" + "="*60)
            print("TEST SUITE SUMMARY")
            print("="*60)
            print(f"Tests Passed: {passed_tests}/{total_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            
            if passed_tests == total_tests:
                print("✓ ALL TESTS PASSED - Driver system ready for production")
            else:
                print("⚠ Some tests failed - review implementation")
                
            return passed_tests == total_tests
            
        except Exception as e:
            print(f"✗ Test suite failed: {e}")
            return False
            
    def generate_performance_report(self):
        """Generate detailed performance analysis report"""
        if 'performance_matrix' not in self.test_results:
            print("Run cross-discipline performance test first")
            return
            
        print("\n" + "="*60)
        print("DETAILED PERFORMANCE ANALYSIS REPORT")
        print("="*60)
        
        matrix = self.test_results['performance_matrix']
        disciplines = ["single_seater", "touring_car", "rally", "street_racing", 
                      "drag_racing", "rallycross", "endurance"]
        
        # Driver specialization analysis
        print("\nDriver Specialization Analysis:")
        print("-" * 40)
        
        for driver_name, performance in matrix.items():
            sorted_disciplines = sorted(performance.items(), key=lambda x: x[1], reverse=True)
            top_3 = sorted_disciplines[:3]
            bottom_2 = sorted_disciplines[-2:]
            
            print(f"\n{driver_name}:")
            print(f"  Strengths: {', '.join([d[0].replace('_', ' ').title() + f' ({d[1]:.1f})' for d in top_3])}")
            print(f"  Weaknesses: {', '.join([d[0].replace('_', ' ').title() + f' ({d[1]:.1f})' for d in bottom_2])}")
            print(f"  Range: {sorted_disciplines[0][1] - sorted_disciplines[-1][1]:.1f} points")
            
        # Discipline competitiveness analysis
        print("\n\nDiscipline Competitiveness Analysis:")
        print("-" * 40)
        
        for discipline in disciplines:
            ratings = [matrix[driver][discipline] for driver in matrix.keys()]
            avg_rating = sum(ratings) / len(ratings)
            max_rating = max(ratings)
            min_rating = min(ratings)
            
            print(f"\n{discipline.replace('_', ' ').title()}:")
            print(f"  Average: {avg_rating:.1f}")
            print(f"  Range: {min_rating:.1f} - {max_rating:.1f}")
            print(f"  Competitiveness: {max_rating - min_rating:.1f} point spread")


def main():
    """Main testing function"""
    tester = DriverSystemTester()
    
    # Run comprehensive test suite
    success = tester.run_comprehensive_test_suite()
    
    # Generate detailed report if tests passed
    if success:
        tester.generate_performance_report()
        
    return success


if __name__ == "__main__":
    main()