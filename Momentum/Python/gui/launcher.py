"""
Momentum Racing Simulator Launcher.

Integrates main menu with race visualization window.
"""

import sys
import os

# Configure matplotlib backend BEFORE any imports that might use it
try:
    import matplotlib
    # PyQt6 requires 'QtAgg' backend (not 'Qt5Agg')
    matplotlib.use('QtAgg', force=True)
    print("[LAUNCHER] matplotlib configured with QtAgg backend")
except ImportError:
    print("[LAUNCHER] WARNING: matplotlib not installed - position plots will not be available")
except Exception as e:
    print(f"[LAUNCHER] WARNING: matplotlib configuration failed: {e}")

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
        from GUI.gui_championship import ChampionshipWindow

        self.race_window_class = RaceWindow
        self.main_menu_class = MainMenuWindow
        self.championship_window_class = ChampionshipWindow

        self.main_menu = None
        self.race_window = None
        self.championship_window = None
        self.race_config = {}
        self.championship_config = {}

    def run(self):
        """Start the application with main menu."""
        self.show_main_menu()
        return self.app.exec()

    def show_main_menu(self):
        """Show main menu window."""
        self.main_menu = self.main_menu_class()
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

        # Create race window with display mode, pass selected track_id and discipline if present
        track_id = config.get('track_id')
        discipline = config.get('discipline', 'SINGLE_SEATER')
        championship_id = config.get('championship_id')
        race_id = config.get('race_id')
        
        try:
            self.race_window = self.race_window_class(
                track_id=track_id, 
                discipline=discipline,
                championship_id=championship_id,
                race_id=race_id
            )
        except TypeError:
            # Older signature fallback
            try:
                self.race_window = self.race_window_class(track_id=track_id, discipline=discipline)
            except TypeError:
                try:
                    self.race_window = self.race_window_class(track_id=track_id)
                except TypeError:
                    self.race_window = self.race_window_class()

        # Set player driver
        player_driver = config.get('driver')
        if player_driver:
            self.race_window.set_player_driver(player_driver)

        # Set player team so race controls can apply to all team cars.
        player_team = config.get('team')
        if player_team and hasattr(self.race_window, 'set_player_team'):
            self.race_window.set_player_team(player_team)

        # Set tuning preset
        tuning_preset = config.get('tuning_preset', 'balanced')
        self.race_window.set_tuning_preset(tuning_preset)

        # Apply display mode from config
        display_mode = config.get("display_mode", "borderless")
        self.race_window.set_display_mode(display_mode)

        # Store active game mode on race window for round-to-round routing.
        setattr(self.race_window, "_game_mode", config.get("mode", "single_race"))

        # Connect race window signals
        self.race_window.return_to_menu.connect(self.return_to_menu)
        self.race_window.next_race.connect(self.next_race)

        self.race_window.show()

        # Player driver is selected, pace/overtake are controlled during race
        driver_name = getattr(config['driver'], 'name', 'Unknown Driver')
        mode = "Championship" if championship_id else "Standalone"
        print(f"[LAUNCHER] Race started with player: {driver_name}, discipline: {discipline}, mode: {mode}")
        print("[LAUNCHER] Pace and overtaking controls are available in the race window")

    def next_race(self, config: dict):
        """Proceed to next race in championship."""
        print(f"[LAUNCHER] Proceeding to next race in championship: {config}")

        championship_id = config.get('championship_id')
        race_id = config.get('race_id')

        if not championship_id:
            print("[LAUNCHER] ERROR: No championship_id in next_race config")
            self.return_to_menu()
            return

        self._close_active_race_window()

        try:
            ctx = self._load_championship_context(championship_id)
            if ctx is None:
                return
            db, championship, championship_service = ctx

            self._mark_race_completed_safe(championship_service, race_id)
            next_race = self._get_next_scheduled_race(
                championship_service,
                championship_id,
                championship.current_season,
            )
            if not next_race:
                print("[LAUNCHER] No more scheduled races in championship")
                self.return_to_menu()
                return

            race_obj = db.get_race(next_race['race_id'])
            track_obj = db.get_track(race_obj.track_id) if race_obj else None
            setup_config = self._show_next_race_setup_dialog(
                config,
                db,
                championship,
                race_obj,
                track_obj,
            )
            if setup_config is None:
                return

            success, error_msg = championship_service.update_race_lifecycle_status(
                next_race['race_id'],
                "in-progress",
            )
            if not success:
                print(f"[LAUNCHER] ERROR updating race status: {error_msg}")
                return

            print(f"[LAUNCHER] Starting next race {next_race['race_id']}")
            self.start_race(setup_config)

        except Exception as e:
            print(f"[LAUNCHER] ERROR proceeding to next race: {e}")
            import traceback
            traceback.print_exc()
            self.return_to_menu()

    def _close_active_race_window(self) -> None:
        """Close current race window before routing to next flow."""
        if self.race_window:
            self.race_window.close()
            self.race_window = None

    def _load_championship_context(self, championship_id):
        """Load database + championship service context for race progression."""
        from database.database_manager import DatabaseManager
        from services.championship_service import ChampionshipService

        db = DatabaseManager()
        championship = db.get_championship(championship_id)
        if not championship:
            print(f"[LAUNCHER] ERROR: Could not find championship with id {championship_id}")
            self.return_to_menu()
            return None
        championship_service = ChampionshipService(db)
        return db, championship, championship_service

    def _mark_race_completed_safe(self, championship_service, race_id) -> None:
        """Best-effort update for completed race lifecycle state."""
        if not race_id:
            return
        try:
            success, error_msg = championship_service.update_race_lifecycle_status(
                race_id,
                "completed",
            )
            if success:
                print(f"[LAUNCHER] Race {race_id} marked as completed")
            else:
                print(f"[LAUNCHER] WARNING: Could not mark race as completed: {error_msg}")
        except Exception as e:
            print(f"[LAUNCHER] ERROR marking race as completed: {e}")

    def _get_next_scheduled_race(self, championship_service, championship_id, season):
        """Return next scheduled race dict from championship calendar."""
        calendar = championship_service.get_championship_calendar(championship_id, season)
        for race in calendar:
            if race['status'] == 'scheduled':
                return race
        return None

    def _show_next_race_setup_dialog(self, config: dict, db, championship, race_obj, track_obj):
        """Open mode-aware setup dialog and return race config when accepted."""
            mode = (config.get('mode') or 'championship').lower()
            if mode == 'career':
                from GUI.gui_career import CareerPreRaceSetupDialog as SetupDialog
            else:
                from GUI.gui_championship import PreRaceSetupDialog as SetupDialog

            setup_dialog = SetupDialog(
                db,
                championship,
                race_obj,
                track_obj,
                parent=None
            )
            if setup_dialog.exec() == 1:
                return setup_dialog.get_race_config()
            return None

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
