"""
Car Development System

Manage vehicle R&D, component upgrades, and performance improvements
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random


@dataclass
class ComponentDevelopment:
    """Development status of a car component"""
    component_name: str
    current_level: int = 1  # 1-10 scale
    max_level: int = 10
    development_points: float = 0.0  # Progress to next level
    points_needed: float = 100.0
    
    # Performance impact
    performance_gain_per_level: float = 0.5  # % improvement
    reliability: float = 100.0  # % reliability (degrades with pushing limits)
    
    # Costs
    upgrade_cost: float = 1.0  # Millions per level
    maintenance_cost: float = 0.1  # Millions per season


@dataclass
class DevelopmentPriorities:
    """Team's development focus allocation"""
    engine: int = 20  # % of R&D budget
    aerodynamics: int = 25
    chassis: int = 20
    suspension: int = 15
    electronics: int = 10
    reliability: int = 10
    
    def validate(self) -> bool:
        """Check if priorities sum to 100%"""
        total = (self.engine + self.aerodynamics + self.chassis + 
                self.suspension + self.electronics + self.reliability)
        return total == 100


@dataclass
class CarPerformance:
    """Overall car performance metrics"""
    team_id: int
    season: int
    
    # Component levels
    components: Dict[str, ComponentDevelopment] = field(default_factory=dict)
    
    # Overall ratings
    overall_rating: float = 50.0  # 0-100 scale
    speed_rating: float = 50.0
    handling_rating: float = 50.0
    reliability_rating: float = 50.0
    
    # Development
    development_budget: float = 10.0  # Millions per season
    development_points_per_week: float = 10.0
    priorities: DevelopmentPriorities = field(default_factory=DevelopmentPriorities)


class CarDevelopmentManager:
    """
    Manages car development and performance upgrades
    
    Features:
    - Component-level development
    - R&D budget allocation
    - Performance testing
    - Upgrade planning
    """
    
    def __init__(self):
        self.team_cars: Dict[int, CarPerformance] = {}  # team_id -> performance
    
    def initialize_car(self, team_id: int, team_tier: str, season: int) -> CarPerformance:
        """Initialize car performance based on team tier"""
        # Base ratings by tier
        tier_ratings = {
            'tier1': 85.0,
            'tier2': 75.0,
            'tier3': 65.0,
            'tier4': 55.0,
            'tier5': 45.0,
            'tier6': 35.0
        }
        
        base_rating = tier_ratings.get(team_tier, 50.0)
        
        car = CarPerformance(
            team_id=team_id,
            season=season,
            overall_rating=base_rating,
            speed_rating=base_rating + random.uniform(-5, 5),
            handling_rating=base_rating + random.uniform(-5, 5),
            reliability_rating=base_rating + random.uniform(-5, 5)
        )
        
        # Initialize components
        components = ['engine', 'aerodynamics', 'chassis', 'suspension', 'electronics', 'gearbox']
        for comp in components:
            initial_level = max(1, int(base_rating / 10))
            car.components[comp] = ComponentDevelopment(
                component_name=comp,
                current_level=initial_level,
                performance_gain_per_level=0.5,
                upgrade_cost=1.0 + (initial_level * 0.2),
                points_needed=100.0 * initial_level
            )
        
        self.team_cars[team_id] = car
        return car
    
    def allocate_development_budget(
        self,
        team_id: int,
        total_budget: float,
        priorities: DevelopmentPriorities
    ) -> bool:
        """Allocate development budget across components"""
        if not priorities.validate():
            return False
        
        car = self.team_cars.get(team_id)
        if not car:
            return False
        
        car.development_budget = total_budget
        car.priorities = priorities
        
        return True
    
    def process_weekly_development(self, team_id: int) -> Dict[str, float]:
        """
        Process one week of development
        
        Returns progress made on each component
        """
        car = self.team_cars.get(team_id)
        if not car:
            return {}
        
        # Calculate points generated this week
        base_points = car.development_points_per_week
        budget_multiplier = car.development_budget / 10.0  # 10M is baseline
        
        total_points = base_points * budget_multiplier
        
        # Distribute points based on priorities
        progress = {}
        component_map = {
            'engine': car.priorities.engine,
            'aerodynamics': car.priorities.aerodynamics,
            'chassis': car.priorities.chassis,
            'suspension': car.priorities.suspension,
            'electronics': car.priorities.electronics
        }
        
        for component, priority_pct in component_map.items():
            if component not in car.components:
                continue
            
            comp = car.components[component]
            points_allocated = total_points * (priority_pct / 100.0)
            comp.development_points += points_allocated
            
            # Check for level up
            progress[component] = points_allocated
            
            if comp.development_points >= comp.points_needed:
                if comp.current_level < comp.max_level:
                    comp.current_level += 1
                    comp.development_points = 0
                    comp.points_needed *= 1.5  # Exponential difficulty
                    progress[component] = -1  # Signal level up
        
        # Update overall ratings
        self._recalculate_ratings(car)
        
        return progress
    
    def upgrade_component(
        self,
        team_id: int,
        component: str,
        budget_available: float
    ) -> Tuple[bool, str, float]:
        """
        Force upgrade a component (costs money, instant level up)
        
        Returns (success, message, cost)
        """
        car = self.team_cars.get(team_id)
        if not car or component not in car.components:
            return False, "Component not found", 0.0
        
        comp = car.components[component]
        
        if comp.current_level >= comp.max_level:
            return False, "Component already at max level", 0.0
        
        cost = comp.upgrade_cost
        if budget_available < cost:
            return False, f"Insufficient budget. Need €{cost:.1f}M", 0.0
        
        # Upgrade
        comp.current_level += 1
        comp.upgrade_cost *= 1.3  # Increasing costs
        comp.points_needed *= 1.5
        comp.development_points = 0
        
        # Slight reliability hit from rushed upgrade
        comp.reliability = max(80.0, comp.reliability - 5.0)
        
        self._recalculate_ratings(car)
        
        return True, f"Upgraded {component} to level {comp.current_level}", cost
    
    def run_test_session(
        self,
        team_id: int,
        focus_area: str,
        budget: float = 0.5
    ) -> Dict:
        """
        Run a test session to gain development data
        
        Returns test results and insights
        """
        car = self.team_cars.get(team_id)
        if not car:
            return {'success': False, 'message': 'Car not initialized'}
        
        # Testing provides bonus development points
        bonus_points = budget * 50.0  # 50 points per million spent
        
        if focus_area in car.components:
            comp = car.components[focus_area]
            comp.development_points += bonus_points
            
            # Gain reliability data
            comp.reliability = min(100.0, comp.reliability + random.uniform(0, 2.0))
        
        # Generate test results
        results = {
            'success': True,
            'focus_area': focus_area,
            'points_gained': bonus_points,
            'current_level': car.components[focus_area].current_level if focus_area in car.components else 0,
            'findings': self._generate_test_findings(car, focus_area),
            'cost': budget
        }
        
        return results
    
    def get_development_recommendations(self, team_id: int) -> List[Dict]:
        """Get AI recommendations for development priorities"""
        car = self.team_cars.get(team_id)
        if not car:
            return []
        
        recommendations = []
        
        # Find weakest components
        component_levels = [(name, comp.current_level) 
                           for name, comp in car.components.items()]
        component_levels.sort(key=lambda x: x[1])
        
        # Recommend upgrading weakest
        for name, level in component_levels[:3]:
            comp = car.components[name]
            recommendations.append({
                'type': 'upgrade',
                'component': name,
                'current_level': level,
                'estimated_cost': comp.upgrade_cost,
                'expected_gain': f"+{comp.performance_gain_per_level:.1f}% performance",
                'priority': 'high' if level < 5 else 'medium'
            })
        
        # Recommend reliability improvements if needed
        for name, comp in car.components.items():
            if comp.reliability < 85.0:
                recommendations.append({
                    'type': 'reliability',
                    'component': name,
                    'current_reliability': comp.reliability,
                    'action': 'Run test session or reduce development pace',
                    'priority': 'high' if comp.reliability < 75.0 else 'medium'
                })
        
        return recommendations
    
    def compare_with_competitors(
        self,
        team_id: int,
        competitor_ids: List[int]
    ) -> Dict:
        """Compare car performance with competitors"""
        car = self.team_cars.get(team_id)
        if not car:
            return {}
        
        comparison = {
            'your_team': {
                'overall': car.overall_rating,
                'speed': car.speed_rating,
                'handling': car.handling_rating,
                'reliability': car.reliability_rating
            },
            'competitors': []
        }
        
        for comp_id in competitor_ids:
            comp_car = self.team_cars.get(comp_id)
            if comp_car:
                comparison['competitors'].append({
                    'team_id': comp_id,
                    'overall': comp_car.overall_rating,
                    'speed': comp_car.speed_rating,
                    'handling': comp_car.handling_rating,
                    'reliability': comp_car.reliability_rating
                })
        
        # Calculate rankings
        all_ratings = [car.overall_rating] + [c['overall'] for c in comparison['competitors']]
        all_ratings.sort(reverse=True)
        comparison['your_ranking'] = all_ratings.index(car.overall_rating) + 1
        comparison['total_teams'] = len(all_ratings)
        
        return comparison
    
    def _recalculate_ratings(self, car: CarPerformance):
        """Recalculate overall ratings based on component levels"""
        # Speed influenced by engine and aero
        engine_level = car.components.get('engine', ComponentDevelopment('engine')).current_level
        aero_level = car.components.get('aerodynamics', ComponentDevelopment('aero')).current_level
        car.speed_rating = 30.0 + (engine_level * 4.0) + (aero_level * 3.0)
        
        # Handling influenced by chassis and suspension
        chassis_level = car.components.get('chassis', ComponentDevelopment('chassis')).current_level
        suspension_level = car.components.get('suspension', ComponentDevelopment('suspension')).current_level
        car.handling_rating = 30.0 + (chassis_level * 3.5) + (suspension_level * 3.5)
        
        # Reliability is average of all component reliabilities
        reliabilities = [comp.reliability for comp in car.components.values()]
        car.reliability_rating = sum(reliabilities) / len(reliabilities) if reliabilities else 50.0
        
        # Overall is weighted average
        car.overall_rating = (car.speed_rating * 0.4 + 
                            car.handling_rating * 0.4 + 
                            car.reliability_rating * 0.2)
    
    def _generate_test_findings(self, car: CarPerformance, focus_area: str) -> List[str]:
        """Generate realistic test session findings"""
        findings = []
        
        if focus_area in car.components:
            comp = car.components[focus_area]
            
            if comp.current_level < 5:
                findings.append(f"{focus_area.title()} shows potential for significant improvement")
            else:
                findings.append(f"{focus_area.title()} performing well but reaching development plateau")
            
            if comp.reliability < 90:
                findings.append(f"Reliability concerns detected - recommend additional testing")
            else:
                findings.append(f"Component reliability within acceptable parameters")
            
            findings.append(f"Current performance level: {comp.current_level}/10")
            findings.append(f"Estimated {comp.points_needed - comp.development_points:.0f} points needed for next upgrade")
        
        return findings
