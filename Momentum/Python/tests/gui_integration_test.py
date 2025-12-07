"""GUI integration test: opens RaceWindow and emits standings_update events
(simulating engine 'laps completed' values). The GUI converts laps_completed
into display lap = laps_completed + 1.

Run example (PowerShell):
    $env:PYTHONPATH = 'C:/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python'
    python .\Momentum\Python\tests\gui_integration_test.py
"""
import sys
import os
import time
from types import SimpleNamespace

# Ensure imports resolve (same logic as launcher)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GUI.gui_race_visual import RaceWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer


def make_driver(did, name):
    # Include `current_team_id` (None) to avoid race engine code that
    # inspects driver.current_team_id when building the teams dict.
    return SimpleNamespace(id=did, name=name, current_team_id=None)


def emit_standings(window, driver_id, position, laps_completed, push=0.7, gap=0.0, position_m=0.0, race_time=0.0):
    # Use engine-style laps_completed value in message
    msg = f"standings_update|{driver_id}|{position}|{laps_completed}|{push:.2f}|{gap:.2f}|{position_m:.2f}|{race_time:.2f}"
    print(f"EMIT: {msg}")
    window.emitter.event_signal.emit(msg)


def main():
    app = QApplication(sys.argv)
    win = RaceWindow()
    # Prevent the RaceWindow from starting the full race engine during this
    # lightweight GUI test. Some internal handlers may call `_start_race` when
    # they see live position data; override it to avoid launching the engine
    # thread which expects full driver/team objects.
    win._start_race = lambda *a, **k: print("_start_race suppressed for GUI test")
    win.show()

    # Populate minimal drivers so table has names
    win.drivers = [make_driver(1, 'Alpha'), make_driver(2, 'Bravo')]

    # Schedule a sequence of events to simulate lap progression
    # t=0: both at laps_completed=0 (display lap should be 1)
    QTimer.singleShot(500, lambda: emit_standings(win, 1, 1, 0, position_m=50.0, race_time=10.0))
    QTimer.singleShot(500, lambda: emit_standings(win, 2, 2, 0, position_m=30.0, race_time=10.5))

    # t=2000ms: driver 1 completes first lap (laps_completed=1 -> display 2)
    QTimer.singleShot(2000, lambda: emit_standings(win, 1, 1, 1, position_m=1050.0, race_time=95.0))

    # t=3500ms: driver 2 completes first lap
    QTimer.singleShot(3500, lambda: emit_standings(win, 2, 2, 1, position_m=1005.0, race_time=95.2))

    # t=5000ms: driver 1 completes second lap (laps_completed=2 -> display 3)
    QTimer.singleShot(5000, lambda: emit_standings(win, 1, 1, 2, position_m=2050.0, race_time=190.0))

    # Quit after 7s
    QTimer.singleShot(7000, app.quit)

    print("Starting GUI integration test (window will appear).")
    app.exec()
    print("GUI integration test finished.")


if __name__ == '__main__':
    main()
