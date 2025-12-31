"""
Momentum Racing Simulator Launcher.

Integrates main menu with race visualization window.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication

# Ensure a QGuiApplication exists early to avoid QPixmap-before-QApplication errors
# Some GUI modules may (incorrectly) create QPixmaps at import time; creating a
# QApplication here prevents the runtime error when running the launcher.
_existing_app = QApplication.instance()
if _existing_app is None:
    # Create a lightweight application early; MomentumLauncher will reuse it.
    _early_app = QApplication(sys.argv)


class MomentumLauncher:
    """Main application launcher that manages menu and race windows."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        # Defer importing GUI modules until after QApplication exists to avoid
        # creating QPixmaps or other Qt GUI objects at module import time.
        from GUI.gui_race_visual import RaceWindow
        from GUI.gui_main_menu import MainMenuWindow

        self.RaceWindow = RaceWindow
        self.MainMenuWindow = MainMenuWindow

        self.main_menu = None
        self.race_window = None
        self.race_config = {}

    def run(self):
        """Start the application with main menu."""
        self.show_main_menu()
        return self.app.exec()

    def show_main_menu(self):
        """Show main menu window."""
        self.main_menu = self.MainMenuWindow()
        self.main_menu.start_race_signal.connect(self.start_race)
        self.main_menu.show()

    def start_race(self, config: dict):
        """Start race with given configuration."""
        print(f"[LAUNCHER] Starting race with config: {config}")
        self.race_config = config

        # Close existing race window if any
        if self.race_window:
            self.race_window.close()
            self.race_window = None

        # Create race window with display mode, pass selected track_id if present
        track_id = config.get('track_id')
        try:
            self.race_window = self.RaceWindow(track_id=track_id)
        except TypeError:
            # Older signature fallback
            self.race_window = self.RaceWindow()

        # Set player driver
        player_driver = config.get('driver')
        if player_driver:
            self.race_window.set_player_driver(player_driver)

        # Set tuning preset
        tuning_preset = config.get('tuning_preset', 'balanced')
        self.race_window.set_tuning_preset(tuning_preset)

        # Apply display mode from config
        display_mode = config.get("display_mode", "borderless")
        self.race_window.set_display_mode(display_mode)

        # Connect race window return_to_menu signal
        self.race_window.return_to_menu.connect(self.return_to_menu)

        self.race_window.show()

        # Player driver is selected, pace/overtake are controlled during race
        driver_name = getattr(config['driver'], 'name', 'Unknown Driver')
        print(f"[LAUNCHER] Race started with player: {driver_name}")
        print("[LAUNCHER] Pace and overtaking controls are available in the race window")

    def return_to_menu(self):
        """Return from race to main menu."""
        if self.race_window:
            self.race_window.close()
            self.race_window = None

        if self.main_menu:
            self.main_menu.show()
        else:
            self.show_main_menu()


def main():
    """Main entry point."""
    launcher = MomentumLauncher()
    sys.exit(launcher.run())


if __name__ == "__main__":
    main()
