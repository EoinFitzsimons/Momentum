#!/usr/bin/env python3
"""Script to fix linting issues identified by flake8 and mypy."""

import re
from pathlib import Path

# Issues to fix
FIXES = {
    "Momentum/Python/GUI/accessibility_settings.py": [
        {"line": 10, "issue": "F401", "text": "from PyQt6.QtWidgets import QApplication", "remove": True},
    ],
    "Momentum/Python/GUI/gui_career.py": [
        {"line": 33, "issue": "F401", "text": "    QHeaderView,", "remove": True},
    ],
    "Momentum/Python/GUI/gui_main_menu.py": [
        {"line_range": (30, 34), "issue": "F401", "remove_lines": ["    center_dialog,", "    get_screen_dimensions,", "    calculate_responsive_size,"]},
    ],
    "Momentum/Python/GUI/gui_championship.py": [
        {"line_range": (43, 50), "issue": "F401", "remove_lines": ["    center_dialog,", "    get_screen_dimensions,", "    calculate_responsive_size,"]},
    ],
    "Momentum/Python/GUI/window_utils.py": [
        {"line": 6, "issue": "F401", "text": "    QApplication,", "remove": True},
        {"line": 12, "issue": "F401", "remove_lines": ["from PyQt6.QtCore import Qt, QRect", "from PyQt6.QtGui import QGuiApplication"]},
    ],
    "Momentum/Python/vehicles/vehicle_appearance.py": [
        {"line": 21, "issue": "no-redef", "text": "class QColor:", "replace": "class _QColorFallback:"},
    ],
    "Momentum/Python/GUI/gui_race_visual.py": [
        {"line": 95, "issue": "assignment", "text": "    FigureCanvas = None  # type: ignore[misc]", "replace": "    FigureCanvas = None  # type: ignore[assignment]"},
        {"line": 96, "issue": "assignment", "text": "    Figure = None  # type: ignore[misc]", "replace": "    Figure = None  # type: ignore[assignment]"},
    ],
}

def fix_file(filepath, fixes):
    """Apply fixes to a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    for fix in fixes:
        if "remove" in fix and fix["remove"]:
            # Find and remove a specific line
            target = fix["text"]
            new_lines = [l for l in lines if l.rstrip() != target.rstrip()]
            if len(new_lines) < len(lines):
                lines = new_lines
                modified = True
                print(f"  Removed: {target}")
        elif "remove_lines" in fix:
            # Remove multiple specific lines
            remove_targets = fix["remove_lines"]
            new_lines = [l for l in lines if l.rstrip() not in [t.rstrip() for t in remove_targets]]
            if len(new_lines) < len(lines):
                lines = new_lines
                modified = True
                print(f"  Removed {len(lines) - len(new_lines)} lines")
        elif "replace" in fix:
            # Replace a line
            target = fix["text"]
            replacement = fix["replace"]
            new_lines = [replacement + "\n" if l.rstrip() == target.rstrip() else l for l in lines]
            if new_lines != lines:
                lines = new_lines
                modified = True
                print(f"  Replaced: {target} -> {replacement}")
    
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✓ Fixed {filepath}")
        return True
    return False

# Apply fixes
print("Fixing linting issues...")
for filepath, fixes in FIXES.items():
    full_path = Path("Momentum/Python") / filepath.replace("Momentum/Python/", "")
    if fix_file(full_path, fixes):
        pass

print("Done!")
