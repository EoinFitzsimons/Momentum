"""
Database Manager Extensions - Hiring & Progression Methods

Extension methods for DatabaseManager class to support hiring and progression systems.
Import and monkey-patch these methods into DatabaseManager at runtime.

Authors: Final Year Project - Computer Science
"""

from typing import List, Optional, Dict
import random
from datetime import datetime, timedelta


def get_available_drivers(self, discipline: Optional[str] = None,
                         min_rating: float = 0.0,
                         max_salary: Optional[float] = None,
                         page: int = 1, page_size: int = 50):
    """UC-15: Get available drivers for hire"""
    from database.models import Driver
    
    with self.get_connection() as conn:
        where_clauses = ["current_team_id IS NULL", "career_phase = 'active'"]
        params = []
        
        if discipline:
            where_clauses.append("preferred_discipline = ?")
            params.append(discipline)
        
        if min_rating > 0:
            where_clauses.append("((speed + racecraft + consistency) / 3.0) >= ?")
            params.append(min_rating)
        
        if max_salary is not None:
            where_clauses.append("(salary IS NULL OR salary <= ?)")
            params.append(max_salary)
        
        where_sql = " AND ".join(where_clauses)
        
        count_sql = f"SELECT COUNT(*) FROM drivers WHERE {where_sql}"
        total = conn.execute(count_sql, params).fetchone()[0]
        
        offset = (page - 1) * page_size
        query_sql = f"""
            SELECT * FROM drivers 
            WHERE {where_sql}
            ORDER BY (speed + racecraft + consistency) DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        rows = conn.execute(query_sql, params).fetchall()
        
        drivers = [self._hydrate_driver(row) for row in rows]
        return ([d for d in drivers if d], total)


def get_available_staff(self, role: Optional[str] = None,
                       min_rating: float = 0.0,
                       page: int = 1, page_size: int = 50):
    """UC-17: Get available staff for hire"""
    with self.get_connection() as conn:
        where_clauses = ["current_team_id IS NULL"]
        params = []
        
        if role:
            where_clauses.append("role = ?")
            params.append(role)
        
        if min_rating > 0:
            where_clauses.append("rating >= ?")
            params.append(min_rating)
        
        where_sql = " AND ".join(where_clauses)
        
        count_sql = f"SELECT COUNT(*) FROM staff_members WHERE {where_sql}"
        total = conn.execute(count_sql, params).fetchone()[0]
        
        offset = (page - 1) * page_size
        query_sql = f"""
            SELECT * FROM staff_members 
            WHERE {where_sql}
            ORDER BY rating DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        rows = conn.execute(query_sql, params).fetchall()
        
        from database.models import StaffMember
        staff = [StaffMember(**dict(row)) for row in rows]
        return (staff, total)


def sign_driver_contract(self, driver_id: int, team_id: int,
                       contract_length: int, salary: float) -> bool:
    """UC-16: Sign driver to team contract"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE drivers
            SET current_team_id = ?,
                contract_length = ?,
                salary = ?
            WHERE id = ?
        """, (team_id, contract_length, salary, driver_id))
        return True


def sign_staff_contract(self, staff_id: int, team_id: int,
                      contract_length: int, salary: float) -> bool:
    """UC-18: Sign staff to team contract"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE staff_members
            SET current_team_id = ?
            WHERE id = ?
        """, (team_id, staff_id))
        return True


def release_driver(self, driver_id: int) -> bool:
    """Release driver from contract"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE drivers
            SET current_team_id = NULL,
                contract_length = NULL
            WHERE id = ?
        """, (driver_id,))
        return True


def release_staff(self, staff_id: int) -> bool:
    """Release staff member from team"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE staff_members
            SET current_team_id = NULL
            WHERE id = ?
        """, (staff_id,))
        return True


def update_team_budget(self, team_id: int, amount: float) -> float:
    """Update team budget (add or subtract)"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE teams
            SET budget = budget + ?
            WHERE id = ?
        """, (amount, team_id))
        
        row = conn.execute("SELECT budget FROM teams WHERE id = ?", (team_id,)).fetchone()
        return row[0] if row else 0.0


def update_driver_skills(self, driver_id: int, skill_changes: Dict[str, float]) -> bool:
    """UC-19: Update driver skills with progression changes"""
    with self.get_connection() as conn:
        set_clauses = []
        params = []
        
        for skill, change in skill_changes.items():
            set_clauses.append(f"{skill} = MAX(0, MIN(100, {skill} + ?))")
            params.append(change)
        
        if not set_clauses:
            return True
        
        params.append(driver_id)
        sql = f"UPDATE drivers SET {', '.join(set_clauses)} WHERE id = ?"
        conn.execute(sql, params)
        return True


def age_driver(self, driver_id: int) -> int:
    """Increment driver age by updating birth_date"""
    with self.get_connection() as conn:
        row = conn.execute("SELECT birth_date FROM drivers WHERE id = ?", 
                         (driver_id,)).fetchone()
        if not row or not row[0]:
            return 0
        
        birth_date = datetime.strptime(row[0], "%Y-%m-%d")
        new_birth_date = birth_date.replace(year=birth_date.year - 1)
        
        conn.execute("""
            UPDATE drivers
            SET birth_date = ?
            WHERE id = ?
        """, (new_birth_date.strftime("%Y-%m-%d"), driver_id))
        
        driver = self.get_driver(driver_id)
        return driver.computed_age if driver else 0


def retire_driver(self, driver_id: int) -> bool:
    """UC-19: Retire driver from active competition"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE drivers
            SET career_phase = 'retired',
                current_team_id = NULL,
                contract_length = NULL
            WHERE id = ?
        """, (driver_id,))
        return True


def recycle_driver(self, driver_id: int) -> Optional[int]:
    """UC-19: Recycle retired driver as new rookie"""
    with self.get_connection() as conn:
        original = self.get_driver(driver_id)
        if not original:
            return None
        
        age = random.randint(18, 20)
        birth_date = (datetime.now() - timedelta(days=365*age)).strftime("%Y-%m-%d")
        
        cursor = conn.execute("""
            INSERT INTO drivers (
                name, nationality, birth_date,
                speed, racecraft, consistency, fitness, reactions,
                pressure, setup_knowledge, fuel_management, tyre_management,
                feedback, adaptability,
                preferred_discipline, career_phase, learning_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        """, (
            f"{original.name} Jr.",
            original.nationality,
            birth_date,
            random.uniform(35, 55),
            random.uniform(35, 55),
            random.uniform(35, 55),
            random.uniform(40, 60),
            random.uniform(40, 60),
            random.uniform(30, 50),
            random.uniform(30, 50),
            random.uniform(30, 50),
            random.uniform(30, 50),
            random.uniform(30, 50),
            random.uniform(30, 50),
            original.preferred_discipline,
            1.2
        ))
        
        return cursor.lastrowid


def get_drivers_for_progression(self, season: int):
    """Get all active drivers for season-end progression"""
    from database.models import Driver
    
    with self.get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM drivers
            WHERE career_phase = 'active'
            ORDER BY id
        """).fetchall()
        
        drivers = [self._hydrate_driver(row) for row in rows]
        return [d for d in drivers if d]


def increment_driver_experience(self, driver_id: int, starts: int = 1) -> bool:
    """Increment driver career starts and seasons active"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE drivers
            SET career_starts = career_starts + ?,
                seasons_active = seasons_active + 1
            WHERE id = ?
        """, (starts, driver_id))
        return True


# Monkey-patch methods into DatabaseManager
def patch_database_manager():
    """Add hiring and progression methods to DatabaseManager class"""
    from database.database_manager import DatabaseManager
    
    DatabaseManager.get_available_drivers = get_available_drivers
    DatabaseManager.get_available_staff = get_available_staff
    DatabaseManager.sign_driver_contract = sign_driver_contract
    DatabaseManager.sign_staff_contract = sign_staff_contract
    DatabaseManager.release_driver = release_driver
    DatabaseManager.release_staff = release_staff
    DatabaseManager.update_team_budget = update_team_budget
    DatabaseManager.update_driver_skills = update_driver_skills
    DatabaseManager.age_driver = age_driver
    DatabaseManager.retire_driver = retire_driver
    DatabaseManager.recycle_driver = recycle_driver
    DatabaseManager.get_drivers_for_progression = get_drivers_for_progression
    DatabaseManager.increment_driver_experience = increment_driver_experience


# Auto-patch on import
patch_database_manager()
