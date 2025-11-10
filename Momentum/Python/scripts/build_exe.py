# MOMENTUM Game - Build to EXE
# Run this script to create a standalone executable

import os
import subprocess
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def build_exe():
    """Build standalone executable using PyInstaller"""
    
    print("=" * 60)
    print("MOMENTUM - Building Executable")
    print("=" * 60)
    
    # Change to parent directory for build
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(parent_dir)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=MOMENTUM",
        "--onefile",  # Single executable
        "--windowed",  # No console window
        "--add-data=database/momentum.db;.",  # Include database
        "--add-data=saves;saves",  # Include saves folder
        "--icon=NONE",  # Add icon later if desired
        "gui/gui_game.py"
    ]
    
    print("\nBuilding executable...")
    print("This may take a few minutes...\n")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print("\nExecutable location: dist/MOMENTUM.exe")
        print("\nYou can distribute this single file!")
        print("Note: Make sure momentum.db is in the same folder")
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        print(f"\nError: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(build_exe())
