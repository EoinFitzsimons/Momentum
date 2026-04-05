"""
Database Manager Extensions - Hiring & Progression Methods

Extension methods for DatabaseManager class to support hiring and progression systems.
Import and monkey-patch these methods into DatabaseManager at runtime.

Authors: Eoin Fitzsimons
"""

from typing import List, Optional, Dict
import random
from datetime import datetime, timedelta


def get_available_drivers(self, discipline: Optional[str] = None,
                         min_rating: float = 0.0,
                         max_salary: Optional[float] = None,
                         page: int = 1, page_size: int = 50,
                         sort_by: str = "rating",
                         sort_order: str = "desc"):
    """UC-15: Get available drivers for hire"""
    from database.models import Driver

    sort_map = {
        "rating": "((speed + racecraft + consistency) / 3.0)",
        "name": "name",
        "age": "birth_date",
        "salary": "salary",
        "career_points": "career_points"
    }
    sort_expr = sort_map.get((sort_by or "rating").lower(), sort_map["rating"])
    direction = "DESC" if (sort_order or "desc").lower() != "asc" else "ASC"
    
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
            ORDER BY {sort_expr} {direction}, id ASC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        rows = conn.execute(query_sql, params).fetchall()
        
        drivers = [self._hydrate_driver(row) for row in rows]
        return ([d for d in drivers if d], total)


def get_available_staff(self, role: Optional[str] = None,
                       min_rating: float = 0.0,
                       page: int = 1, page_size: int = 50,
                       sort_by: str = "rating",
                       sort_order: str = "desc"):
    """UC-17: Get available staff for hire"""
    sort_map = {
        "rating": "rating",
        "name": "name",
        "role": "role",
        "salary": "annual_salary"
    }
    sort_expr = sort_map.get((sort_by or "rating").lower(), sort_map["rating"])
    direction = "DESC" if (sort_order or "desc").lower() != "asc" else "ASC"

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
            ORDER BY {sort_expr} {direction}, id ASC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        rows = conn.execute(query_sql, params).fetchall()
        
        from database.models import StaffMember
        staff = [StaffMember(**dict(row)) for row in rows]
        return (staff, total)


def sign_driver_contract(self, driver_id: int, team_id: int,
                       contract_length: int, salary: float,
                       contract_start_season: Optional[int] = None,
                       performance_bonus: float = 0.0) -> None:
    """UC-16: Sign driver to team contract"""
    if contract_start_season is None:
        contract_start_season = datetime.now().year
    contract_end_season = contract_start_season + max(1, contract_length) - 1

    with self.get_connection() as conn:
        conn.execute("""
            UPDATE drivers
            SET current_team_id = ?,
                contract_length = ?,
                salary = ?,
                contract_start_season = ?,
                contract_end_season = ?,
                performance_bonus = ?
            WHERE id = ?
        """, (
            team_id,
            contract_length,
            salary,
            contract_start_season,
            contract_end_season,
            performance_bonus,
            driver_id
        ))


def sign_staff_contract(self, staff_id: int, team_id: int,
                      contract_length: int, salary: float,
                      contract_start_season: Optional[int] = None) -> None:
    """UC-18: Sign staff to team contract"""
    if contract_start_season is None:
        contract_start_season = datetime.now().year
    contract_end_season = contract_start_season + max(1, contract_length) - 1

    with self.get_connection() as conn:
        conn.execute("""
            UPDATE staff_members
            SET current_team_id = ?,
                annual_salary = ?,
                contract_length = ?,
                contract_start_season = ?,
                contract_end_season = ?
            WHERE id = ?
        """, (
            team_id,
            salary,
            contract_length,
            contract_start_season,
            contract_end_season,
            staff_id
        ))


def release_driver(self, driver_id: int) -> None:
    """Release driver from contract"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE drivers
            SET current_team_id = NULL,
                contract_length = NULL,
                contract_start_season = NULL,
                contract_end_season = NULL,
                performance_bonus = 0.0
            WHERE id = ?
        """, (driver_id,))


def release_staff(self, staff_id: int) -> None:
    """Release staff member from team"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE staff_members
            SET current_team_id = NULL,
                annual_salary = NULL,
                contract_length = NULL,
                contract_start_season = NULL,
                contract_end_season = NULL
            WHERE id = ?
        """, (staff_id,))


def expire_contracts_for_season(self, season: int) -> Dict[str, int]:
    """Release personnel whose contracts expired before the target season starts."""
    with self.get_connection() as conn:
        driver_rows = conn.execute(
            """
            SELECT id FROM drivers
            WHERE current_team_id IS NOT NULL
              AND contract_end_season IS NOT NULL
              AND contract_end_season < ?
            """,
            (season,)
        ).fetchall()

        staff_rows = conn.execute(
            """
            SELECT id FROM staff_members
            WHERE current_team_id IS NOT NULL
              AND contract_end_season IS NOT NULL
              AND contract_end_season < ?
            """,
            (season,)
        ).fetchall()

        for row in driver_rows:
            conn.execute(
                """
                UPDATE drivers
                SET current_team_id = NULL,
                    contract_length = NULL,
                    contract_start_season = NULL,
                    contract_end_season = NULL,
                    performance_bonus = 0.0
                WHERE id = ?
                """,
                (row["id"],)
            )

        for row in staff_rows:
            conn.execute(
                """
                UPDATE staff_members
                SET current_team_id = NULL,
                    annual_salary = NULL,
                    contract_length = NULL,
                    contract_start_season = NULL,
                    contract_end_season = NULL
                WHERE id = ?
                """,
                (row["id"],)
            )

        return {
            "drivers_released": len(driver_rows),
            "staff_released": len(staff_rows)
        }


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


def update_driver_skills(self, driver_id: int, skill_changes: Dict[str, float]) -> None:
    """UC-19: Update driver skills with progression changes"""
    with self.get_connection() as conn:
        set_clauses = []
        params = []
        
        for skill, change in skill_changes.items():
            set_clauses.append(f"{skill} = MAX(0, MIN(100, {skill} + ?))")
            params.append(change)
        
        if not set_clauses:
            return
        
        params.append(driver_id)
        sql = f"UPDATE drivers SET {', '.join(set_clauses)} WHERE id = ?"
        conn.execute(sql, params)


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


def retire_driver(self, driver_id: int) -> None:
    """UC-19: Retire driver from active competition"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE drivers
            SET career_phase = 'retired',
                current_team_id = NULL,
                contract_length = NULL
            WHERE id = ?
        """, (driver_id,))


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


def increment_driver_experience(self, driver_id: int, starts: int = 1) -> None:
    """Increment driver career starts and seasons active"""
    with self.get_connection() as conn:
        conn.execute("""
            UPDATE drivers
            SET career_starts = career_starts + ?,
                seasons_active = seasons_active + 1
            WHERE id = ?
        """, (starts, driver_id))


# Monkey-patch methods into DatabaseManager
def patch_database_manager():
    """Add hiring and progression methods to DatabaseManager class"""
    from database.database_manager import DatabaseManager
    
    DatabaseManager.get_available_drivers = get_available_drivers  # type: ignore[attr-defined]
    DatabaseManager.get_available_staff = get_available_staff  # type: ignore[attr-defined]
    DatabaseManager.sign_driver_contract = sign_driver_contract  # type: ignore[attr-defined]
    DatabaseManager.sign_staff_contract = sign_staff_contract  # type: ignore[attr-defined]
    DatabaseManager.release_driver = release_driver  # type: ignore[attr-defined]
    DatabaseManager.release_staff = release_staff  # type: ignore[attr-defined]
    DatabaseManager.update_team_budget = update_team_budget  # type: ignore[attr-defined]
    DatabaseManager.update_driver_skills = update_driver_skills  # type: ignore[attr-defined]
    DatabaseManager.age_driver = age_driver  # type: ignore[attr-defined]
    DatabaseManager.retire_driver = retire_driver  # type: ignore[attr-defined]
    DatabaseManager.recycle_driver = recycle_driver  # type: ignore[attr-defined]
    DatabaseManager.get_drivers_for_progression = get_drivers_for_progression  # type: ignore[attr-defined]
    DatabaseManager.increment_driver_experience = increment_driver_experience  # type: ignore[attr-defined]
    DatabaseManager.expire_contracts_for_season = expire_contracts_for_season  # type: ignore[attr-defined]


# Auto-patch on import
patch_database_manager()
