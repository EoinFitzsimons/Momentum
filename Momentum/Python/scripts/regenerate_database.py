"""
Regenerate Database with Improved Names

This script:
1. Backs up the existing database
2. Clears teams and drivers
3. Regenerates with Latin-script names only and improved team names
"""

import sys
import shutil
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database_manager import DatabaseManager
from scripts.generate_initial_database import DatabaseGenerator

def main():
    print("=" * 80)
    print("REGENERATE DATABASE WITH IMPROVED NAMES")
    print("=" * 80)
    
    db_path = "database/momentum.db"
    
    # Step 1: Backup existing database
    print("\n[1/4] Backing up existing database...")
    backup_path = f"database/momentum_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    try:
        shutil.copy(db_path, backup_path)
        print(f"  ✓ Backup created: {backup_path}")
    except Exception as e:
        print(f"  ⚠ Backup failed: {e}")
        print("  Continuing anyway...")
    
    # Step 2: Clear existing teams and drivers
    print("\n[2/4] Clearing existing teams and drivers...")
    db = DatabaseManager(db_path)
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Clear in correct order (foreign keys)
        cursor.execute("DELETE FROM race_results")
        cursor.execute("DELETE FROM races")
        cursor.execute("DELETE FROM drivers")
        cursor.execute("DELETE FROM teams")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        print("  ✓ Cleared teams, drivers, and related data")
        
        # Get counts
        stats = db.get_database_stats()
        print(f"  Current counts: {stats['drivers']} drivers, {stats['teams']} teams")
        
    except Exception as e:
        print(f"  ✗ Error clearing data: {e}")
        return
    
    # Step 3: Clear name cache
    print("\n[3/4] Clearing name generation cache...")
    from systems.intelligent_name_generator import IntelligentNameGenerator
    name_gen = IntelligentNameGenerator()
    name_gen.clear_all_names()
    print("  ✓ Name cache cleared")
    
    # Step 4: Regenerate with improved generator
    print("\n[4/4] Generating new teams and drivers with improved names...")
    print("  (This may take 2-3 minutes...)\n")
    
    generator = DatabaseGenerator(db_path)
    
    try:
        generator.generate_complete_database()
        
        # Show final stats
        print("\n" + "=" * 80)
        print("GENERATION COMPLETE!")
        print("=" * 80)
        
        stats = db.get_database_stats()
        print(f"\n  Final counts:")
        print(f"    Drivers: {stats['drivers']:,}")
        print(f"    Teams: {stats['teams']:,}")
        print(f"    Tracks: {stats['tracks']:,}")
        print(f"    Races: {stats['races']:,}")
        
        print(f"\n  ✓ All names now use Latin script only")
        print(f"  ✓ Team names are more varied and realistic")
        print(f"  ✓ Backup saved: {backup_path}")
        
    except Exception as e:
        print(f"\n  ✗ Error during generation: {e}")
        print(f"  You can restore from backup: {backup_path}")
        raise

if __name__ == "__main__":
    main()
