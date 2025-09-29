"""
Database migration strategy for Momentum simulation.
Shows how to migrate from SQLite to MySQL when needed (multiplayer/shared persistence).
"""

# Current SQLite implementation (keep this!)
from database.database_manager import DatabaseManager

# Future MySQL implementation (when needed)
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

class DatabaseFactory:
    """Factory pattern for database connections - future MySQL migration"""
    
    @staticmethod
    def create_database_manager(db_type="sqlite", **kwargs):
        """Create database manager based on type"""
        if db_type == "sqlite":
            # Your current implementation
            return DatabaseManager()  # Uses SQLite by default
        
        elif db_type == "mysql":
            # Future MySQL implementation
            # return MySQLDatabaseManager(**kwargs)
            raise NotImplementedError("MySQL support planned for multiplayer phase")
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

# Usage in your simulation.py:
# db_manager = DatabaseFactory.create_database_manager("sqlite")  # Current
# db_manager = DatabaseFactory.create_database_manager("mysql", host="localhost", ...)  # Future

"""
Migration Strategy (when needed):

1. Keep all your current database manager methods
2. Create MySQLDatabaseManager that implements same interface
3. Use SQLAlchemy for MySQL connections
4. Data migration script from SQLite to MySQL
5. Environment-based database selection

Example future requirements.txt addition:
# MySQL dependencies (when needed)
# sqlalchemy>=2.0.0
# mysql-connector-python>=8.0.0
# pymysql>=1.0.0

The beauty of your current design: Your simulation.py and all business logic
remains UNCHANGED when you migrate to MySQL later!
"""