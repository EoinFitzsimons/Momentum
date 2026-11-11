"""
Progression Service - Driver Skill Development & Retirement (UC-19)

Handles season-end progression including:
- Age-based skill decline (peak at 28-32, decline after 35)
- Experience-based skill growth (learning rate)
- Retirement triggering (age 45+ or performance-based)
- Driver recycling (retired drivers become rookies)

Key Features:
- Monte Carlo-based progression with randomness
- Discipline-specific skill curves
- Form trend tracking
- Automatic retirement and recycling

Authors: Eoin Fitzsimons
"""

import random
from typing import Dict, Tuple, Optional, Any

# Import database extensions to add progression methods
import database.database_extensions  # noqa
from database.database_manager import DatabaseManager
from database.models import Driver
from config import DATABASE_PATH


class ProgressionService:
    """
    Driver Progression Service

    Manages driver skill development, retirement, and recycling
    across seasons. Implements realistic aging curves and experience
    growth based on motorsport career patterns.
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialise progression service with database connection"""
        self.db = DatabaseManager(db_path)

    # ========================================================================
    # SKILL PROGRESSION (UC-19)
    # ========================================================================

    def calculate_age_factor(self, age: int) -> float:
        """
        Calculate age-based skill multiplier

        Peak performance: 28-32 years (factor = 1.0)
        Growth phase: 18-27 years (factor = 0.9 to 1.0)
        Decline phase: 33+ years (factor gradually decreases)

        Args:
            age: Driver age

        Returns:
            Age factor (0.5 to 1.0)
        """
        if age < 18:
            return 0.7
        elif age <= 22:
            # Rookie phase: 0.75 to 0.9
            return 0.75 + (age - 18) * 0.0375
        elif age <= 27:
            # Development phase: 0.9 to 1.0
            return 0.9 + (age - 22) * 0.02
        elif age <= 32:
            # Peak phase: 1.0
            return 1.0
        elif age <= 35:
            # Early decline: 1.0 to 0.95
            return 1.0 - (age - 32) * 0.0167
        elif age <= 40:
            # Mid decline: 0.95 to 0.85
            return 0.95 - (age - 35) * 0.02
        elif age <= 45:
            # Late decline: 0.85 to 0.70
            return 0.85 - (age - 40) * 0.03
        else:
            # Veteran decline: 0.70 and below
            return max(0.5, 0.70 - (age - 45) * 0.04)

    def _calculate_core_skills(
        self, driver: Driver, base_change: float, age_factor: float, age: int
    ) -> Dict[str, float]:
        """Calculate changes for core driving skills (speed, racecraft, consistency)"""
        changes = {}
        core_skills = ["speed", "racecraft", "consistency"]

        for skill in core_skills:
            current_value = getattr(driver, skill, 50.0)

            if age < 28:
                change = base_change * random.uniform(0.5, 2.0)
            elif age <= 32:
                change = base_change * random.uniform(-0.2, 0.5)
            else:
                decline_factor = (age - 32) / 10.0
                change = -base_change * random.uniform(0.1, 0.5) * decline_factor

            # Diminishing returns at high levels
            if current_value > 80:
                change *= 0.3
            elif current_value > 70:
                change *= 0.6

            changes[skill] = change * age_factor

        return changes

    def _calculate_physical_skills(
        self, base_change: float, age_factor: float, age: int
    ) -> Dict[str, float]:
        """Calculate changes for physical skills (fitness, reactions)"""
        changes = {}
        physical_skills = ["fitness", "reactions"]

        for skill in physical_skills:
            if age < 28:
                change = base_change * random.uniform(0.3, 1.0)
            elif age <= 32:
                change = 0.0
            else:
                decline_factor = (age - 32) / 8.0
                change = -base_change * random.uniform(0.3, 0.8) * decline_factor

            changes[skill] = change * age_factor

        return changes

    def _calculate_mental_skills(
        self, base_change: float, age: int
    ) -> Dict[str, float]:
        """Calculate changes for mental skills (pressure, setup_knowledge, adaptability)"""
        changes = {}
        mental_skills = ["pressure", "setup_knowledge", "adaptability"]

        for skill in mental_skills:
            if age < 35:
                change = base_change * random.uniform(0.2, 0.8)
            else:
                change = -base_change * random.uniform(0.0, 0.2)

            changes[skill] = change

        return changes

    def _calculate_management_skills(
        self, base_change: float, age: int
    ) -> Dict[str, float]:
        """Calculate changes for management skills (fuel_management, tyre_management)"""
        changes = {}
        management_skills = ["fuel_management", "tyre_management"]

        for skill in management_skills:
            if age < 40:
                change = base_change * random.uniform(0.1, 0.5)
            else:
                change = 0.0

            changes[skill] = change

        return changes

    def calculate_skill_progression(
        self, driver: Driver, races_completed: int = 20
    ) -> Dict[str, float]:
        """
        Calculate skill changes for a driver based on age, experience, and performance

        Args:
            driver: Driver object
            races_completed: Number of races in the season

        Returns:
            Dictionary of skill changes {skill_name: change_value}
        """
        age = driver.computed_age
        age_factor = self.calculate_age_factor(age)
        learning_rate = driver.learning_rate or 1.0

        # Base progression amount (scaled by races)
        base_change = (races_completed / 20.0) * learning_rate

        skill_changes = {}
        skill_changes.update(
            self._calculate_core_skills(driver, base_change, age_factor, age)
        )
        skill_changes.update(
            self._calculate_physical_skills(base_change, age_factor, age)
        )
        skill_changes.update(self._calculate_mental_skills(base_change, age))
        skill_changes.update(self._calculate_management_skills(base_change, age))

        return skill_changes

    def apply_progression_to_driver(
        self, driver_id: int, races_completed: int = 20
    ) -> Dict[str, float]:
        """
        Apply season-end progression to a single driver

        Args:
            driver_id: Driver ID
            races_completed: Number of races completed this season

        Returns:
            Dictionary of applied skill changes
        """
        driver = self.db.get_driver(driver_id)
        if not driver:
            return {}

        # Calculate skill changes
        skill_changes = self.calculate_skill_progression(driver, races_completed)

        # Apply changes to database
        self.db.update_driver_skills(driver_id, skill_changes)  # type: ignore[attr-defined]

        # Age the driver
        self.db.age_driver(driver_id)  # type: ignore[attr-defined]

        # Increment experience
        self.db.increment_driver_experience(driver_id, races_completed)  # type: ignore[attr-defined]

        return skill_changes

    # ========================================================================
    # RETIREMENT SYSTEM (UC-19)
    # ========================================================================

    def check_retirement_eligibility(self, driver: Driver) -> Tuple[bool, str, float]:
        """
        Check if driver should retire

        Retirement triggers:
        - Age 45+: Automatic retirement
        - Age 40-44: 10-30% chance per year
        - Age 35-39 with low performance: 5-15% chance
        - Severe skill decline: Special consideration

        Args:
            driver: Driver object

        Returns:
            Tuple of (should_retire, reason, probability)
        """
        age = driver.computed_age

        # Calculate average skill rating
        avg_skill = (driver.speed + driver.racecraft + driver.consistency) / 3.0

        # Age 45+: Automatic retirement
        if age >= 45:
            return (True, "Age-based mandatory retirement (45+)", 1.0)

        # Age 40-44: Increasing retirement probability
        if age >= 40:
            base_prob = 0.10 + (age - 40) * 0.05  # 10% at 40, 30% at 44

            # Lower skills increase retirement chance
            if avg_skill < 60:
                base_prob *= 1.5
            elif avg_skill > 75:
                base_prob *= 0.5

            should_retire = random.random() < base_prob
            reason = "Voluntary retirement (veteran age)" if should_retire else ""
            return (should_retire, reason, base_prob)

        # Age 35-39: Low probability, performance-based
        if age >= 35:
            base_prob = 0.02 + (age - 35) * 0.01  # 2% at 35, 6% at 39

            # Poor performance increases retirement chance
            if avg_skill < 50:
                base_prob *= 2.0
                should_retire = random.random() < base_prob
                reason = (
                    "Early retirement (declining performance)" if should_retire else ""
                )
                return (should_retire, reason, base_prob)

        # No retirement
        return (False, "", 0.0)

    def retire_driver(self, driver_id: int) -> bool:
        """
        Retire driver from active competition

        Args:
            driver_id: Driver ID

        Returns:
            True if successful
        """
        return self.db.retire_driver(driver_id)  # type: ignore[attr-defined]

    def recycle_driver(self, driver_id: int) -> Optional[int]:
        """
        Recycle retired driver as new rookie

        Creates a new young driver with reset skills to maintain
        driver pool population.

        Args:
            driver_id: Original driver ID

        Returns:
            New driver ID if successful
        """
        return self.db.recycle_driver(driver_id)  # type: ignore[attr-defined]

    # ========================================================================
    # SEASON-END PROCESSING (UC-19)
    # ========================================================================

    def process_season_end_progression(self, season: int) -> Dict[str, Any]:
        """
        Process season-end progression for all drivers

        UC-19: Complete progression workflow including:
        1. Calculate and apply skill changes
        2. Check retirement eligibility
        3. Retire eligible drivers
        4. Recycle retired drivers as rookies

        Args:
            season: Season number
            championship_id: Optional championship filter

        Returns:
            Summary dictionary with progression results
        """
        # Get all active drivers
        drivers = self.db.get_drivers_for_progression(season)  # type: ignore[attr-defined]

        results: Dict[str, Any] = {
            "season": season,
            "drivers_processed": len(drivers),
            "progressions": [],
            "retirements": [],
            "recycled": [],
            "summary": {
                "improved": 0,
                "declined": 0,
                "retired": 0,
                "recycled": 0,
                "contracts_expired_drivers": 0,
                "contracts_expired_staff": 0,
            },
        }

        # Release personnel with expired contracts as the new season opens.
        expired = self.db.expire_contracts_for_season(season)  # type: ignore[attr-defined]
        results["summary"]["contracts_expired_drivers"] = expired.get(
            "drivers_released", 0
        )
        results["summary"]["contracts_expired_staff"] = expired.get("staff_released", 0)

        for driver in drivers:
            # Apply progression
            skill_changes = self.apply_progression_to_driver(driver.id)

            # Track improvement/decline
            total_change = sum(skill_changes.values())
            if total_change > 0:
                results["summary"]["improved"] += 1
            elif total_change < 0:
                results["summary"]["declined"] += 1

            # Check retirement
            should_retire, reason, _ = self.check_retirement_eligibility(driver)

            if should_retire:
                self.retire_driver(driver.id)
                results["retirements"].append(
                    {
                        "driver_id": driver.id,
                        "driver_name": driver.name,
                        "age": driver.computed_age,
                        "reason": reason,
                    }
                )
                results["summary"]["retired"] += 1

                # Recycle driver
                new_id = self.recycle_driver(driver.id)
                if new_id:
                    new_driver = self.db.get_driver(new_id)
                    results["recycled"].append(
                        {
                            "original_id": driver.id,
                            "original_name": driver.name,
                            "new_id": new_id,
                            "new_name": new_driver.name if new_driver else "Unknown",
                        }
                    )
                    results["summary"]["recycled"] += 1

            # Store progression details
            results["progressions"].append(
                {
                    "driver_id": driver.id,
                    "driver_name": driver.name,
                    "age": driver.computed_age,
                    "skill_changes": skill_changes,
                    "retired": should_retire,
                }
            )

        return results
