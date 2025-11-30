"""
Clean Test Data - Remove Championship/Race Data Only

Keeps: Teams, Drivers, Tracks, Staff
Removes: Championships, Races, Race Results (test data)
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATABASE_PATH

def clean_test_data():
    print("=" * 80)
    print("CLEAN TEST DATA - Remove Championships and Races")
    print("=" * 80)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check current state
    print("\n📊 CURRENT STATE:")
    cursor.execute("SELECT COUNT(*) FROM championships")
    champs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM races")
    races = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM race_results")
    results = cursor.fetchone()[0]
    
    print(f"  Championships: {champs}")
    print(f"  Races: {races}")
    print(f"  Race Results: {results}")
    
    if champs == 0 and races == 0 and results == 0:
        print("\n✅ Database is already clean!")
        conn.close()
        return
    
    # Confirm
    print("\n⚠️  This will delete:")
    print("  • All championships")
    print("  • All races")
    print("  • All race results")
    print("\n✅ This will keep:")
    print("  • All teams")
    print("  • All drivers")
    print("  • All tracks")
    print("  • All staff")
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\n❌ Cancelled")
        conn.close()
        return
    
    # Delete in correct order (foreign key constraints)
    print("\n🧹 Cleaning...")
    
    cursor.execute("DELETE FROM race_results")
    print(f"  ✓ Deleted {cursor.rowcount} race results")
    
    cursor.execute("DELETE FROM races")
    print(f"  ✓ Deleted {cursor.rowcount} races")
    
    cursor.execute("DELETE FROM championships")
    print(f"  ✓ Deleted {cursor.rowcount} championships")
    
    conn.commit()
    
    # Verify
    print("\n📊 NEW STATE:")
    cursor.execute("SELECT COUNT(*) FROM championships")
    print(f"  Championships: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM races")
    print(f"  Races: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM race_results")
    print(f"  Race Results: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM teams")
    print(f"  Teams: {cursor.fetchone()[0]} (preserved)")
    cursor.execute("SELECT COUNT(*) FROM drivers")
    print(f"  Drivers: {cursor.fetchone()[0]} (preserved)")
    cursor.execute("SELECT COUNT(*) FROM tracks")
    print(f"  Tracks: {cursor.fetchone()[0]} (preserved)")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ CLEAN COMPLETE!")
    print("=" * 80)
    print("\nYou can now start a fresh game with gui/gui_game.py")

if __name__ == "__main__":
    clean_test_data()
