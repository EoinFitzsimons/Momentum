"""
Momentum Racing Simulator Launcher.

Integrates main menu with race visualisation window.
"""

import sys
import os

# Configure matplotlib backend BEFORE any imports that might use it
try:
    import matplotlib

    # PyQt6 requires 'QtAgg' backend (not 'Qt5Agg')
    matplotlib.use("QtAgg", force=True)
    print("[LAUNCHER] matplotlib configured with QtAgg backend")
except ImportError:
    print(
        "[LAUNCHER] WARNING: matplotlib not installed - position plots will not be available"
    )
except Exception as e:
    print(f"[LAUNCHER] WARNING: matplotlib configuration failed: {e}")

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from GUI.accessibility_settings import (
    apply_accessibility_to_app,
    load_accessibility_settings,
)

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
        self.accessibility_settings = load_accessibility_settings()
        apply_accessibility_to_app(self.app, self.accessibility_settings)

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
        track_id = config.get("track_id")
        discipline = config.get("discipline", "SINGLE_SEATER")
        tier = config.get("tier")
        championship_id = config.get("championship_id")
        race_id = config.get("race_id")

        try:
            self.race_window = self.race_window_class(
                track_id=track_id,
                discipline=discipline,
                tier=tier,
                championship_id=championship_id,
                race_id=race_id,
            )
        except TypeError:
            # Older signature fallback
            try:
                self.race_window = self.race_window_class(
                    track_id=track_id, discipline=discipline
                )
            except TypeError:
                try:
                    self.race_window = self.race_window_class(track_id=track_id)
                except TypeError:
                    self.race_window = self.race_window_class()

        # Set player driver
        player_driver = config.get("driver")
        if player_driver:
            self.race_window.set_player_driver(player_driver)

        # Set player team so race controls can apply to all team cars.
        player_team = config.get("team")
        if player_team and hasattr(self.race_window, "set_player_team"):
            self.race_window.set_player_team(player_team)

        # Set tuning preset
        tuning_preset = config.get("tuning_preset", "balanced")
        self.race_window.set_tuning_preset(tuning_preset)

        # Apply display mode from config
        display_mode = config.get("display_mode", "borderless")
        self.race_window.set_display_mode(display_mode)

        accessibility = config.get(
            "accessibility", getattr(self, "accessibility_settings", None)
        )
        if accessibility is None:
            # Lazy-load defaults if launcher was constructed without __init__ (test stubs)
            try:
                accessibility = load_accessibility_settings()
            except Exception:
                accessibility = None
        if hasattr(self.race_window, "set_accessibility_profile"):
            self.race_window.set_accessibility_profile(accessibility)

        # Store active game mode on race window for round-to-round routing.
        setattr(self.race_window, "_game_mode", config.get("mode", "single_race"))

        # Connect race window signals
        self.race_window.return_to_menu.connect(self.return_to_menu)
        self.race_window.next_race.connect(self.next_race)

        self.race_window.show()

        # Player driver is selected, pace/overtake are controlled during race
        driver_name = getattr(config["driver"], "name", "Unknown Driver")
        mode = "Championship" if championship_id else "Standalone"
        print(
            f"[LAUNCHER] Race started with player: {driver_name}, discipline: {discipline}, mode: {mode}"
        )
        print(
            "[LAUNCHER] Pace and overtaking controls are available in the race window"
        )

    def next_race(self, config: dict):
        """Proceed to next race in championship."""
        print(f"[LAUNCHER] Proceeding to next race in championship: {config}")

        championship_id = config.get("championship_id")
        race_id = config.get("race_id")
        mode = (config.get("mode") or "championship").lower()

        if mode == "career":
            self._handle_career_next_race(config)
            return

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

            self._mark_race_completed_safe(
                championship_service,
                race_id,
                db=db,
                discipline=championship.discipline,
            )
            next_race = self._get_next_scheduled_race(
                championship_service,
                championship_id,
                championship.current_season,
            )

            if not next_race:
                print("[LAUNCHER] No more scheduled races in championship")
                self.return_to_menu()
                return

            race_obj = db.get_race(next_race["race_id"])
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
                next_race["race_id"],
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
            print(
                f"[LAUNCHER] ERROR: Could not find championship with id {championship_id}"
            )
            self.return_to_menu()
            return None
        championship_service = ChampionshipService(db)
        return db, championship, championship_service

    def _mark_race_completed_safe(
        self, championship_service, race_id, db=None, discipline: str = "SINGLE_SEATER"
    ) -> None:
        """Best-effort update for completed race lifecycle state."""
        if not race_id:
            return
        try:
            self._backfill_race_points_if_needed(
                championship_service,
                race_id,
                db=db,
                discipline=discipline,
            )
            success, error_msg = championship_service.update_race_lifecycle_status(
                race_id,
                "completed",
            )
            if success:
                print(f"[LAUNCHER] Race {race_id} marked as completed")
            else:
                print(
                    f"[LAUNCHER] WARNING: Could not mark race as completed: {error_msg}"
                )
        except Exception as e:
            print(f"[LAUNCHER] ERROR marking race as completed: {e}")

    def _backfill_race_points_if_needed(
        self,
        championship_service,
        race_id: int,
        db=None,
        discipline: str = "SINGLE_SEATER",
    ) -> None:
        """Repair missing points for saved race results from older zero-point payloads."""
        if db is None:
            return

        from services.race_simulation_api import persist_race_results

        try:
            results = db.get_race_results(race_id)
        except Exception as e:
            print(
                f"[LAUNCHER] WARNING: Could not load race results for points backfill: {e}"
            )
            return

        if not results:
            return

        updated = 0
        for result in results:
            if getattr(result, "dnf_reason", None):
                expected_points = 0
            else:
                expected_points = championship_service.calculate_points(
                    position=int(getattr(result, "position", 0) or 0),
                    discipline=discipline,
                    fastest_lap=bool(getattr(result, "fastest_lap", False)),
                )

            current_points = int(getattr(result, "points", 0) or 0)
            if current_points == expected_points:
                continue

            result.points = expected_points
            updated += 1

        if updated:
            try:
                persist_race_results(db, results)
            except Exception as e:
                print(
                    f"[LAUNCHER] WARNING: Could not persist backfilled race results: {e}"
                )
            print(
                f"[LAUNCHER] Backfilled points for {updated} race result rows in race {race_id}"
            )

    def _get_next_scheduled_race(self, championship_service, championship_id, season):
        """Return next scheduled race dict from championship calendar."""
        calendar = championship_service.get_championship_calendar(
            championship_id, season
        )
        for race in calendar:
            if race["status"] == "scheduled":
                return race
        return None

    def _show_next_race_setup_dialog(
        self, config: dict, db, championship, race_obj, track_obj
    ):
        """Open mode-aware setup dialog and return race config when accepted."""
        from GUI.gui_championship import PreRaceSetupDialog as SetupDialog

        locked_team_id = None
        team_obj = config.get("team") or self.race_config.get("team")
        if team_obj is not None:
            locked_team_id = getattr(team_obj, "id", None)

        setup_dialog = SetupDialog(
            db,
            championship,
            race_obj,
            track_obj,
            locked_team_id=locked_team_id,
            parent=None,
        )
        if setup_dialog.exec() == 1:
            return setup_dialog.get_race_config()
        return None

    def _show_or_create_career_hq(self, championship):
        """Show existing career HQ window if present, otherwise create one."""
        existing = None
        if self.main_menu and hasattr(self.main_menu, "career_window"):
            existing = getattr(self.main_menu, "career_window")

        if existing is not None:
            if hasattr(existing, "load_data"):
                existing.load_data()
            existing.show()
            existing.raise_()
            existing.activateWindow()
            if self.main_menu:
                self.main_menu.hide()
            return

        from GUI.gui_career import CareerWindow

        parent = self.main_menu if self.main_menu else None
        career_window = CareerWindow(championship, parent)
        career_window.return_to_menu.connect(self.return_to_menu)
        career_window.start_race_signal.connect(self.start_race)
        if self.main_menu is not None:
            setattr(self.main_menu, "career_window", career_window)
            self.main_menu.hide()
        career_window.show()

    def _handle_career_next_race(self, config: dict) -> None:
        """Career progression handler using career_* tables (no championships dependency)."""
        self._close_active_race_window()

        try:
            from database.database_manager import DatabaseManager

            db = DatabaseManager()
            race_id = int(config.get("career_race_id") or config.get("race_id") or 0)
            if race_id > 0:
                with db.get_connection() as conn:
                    conn.execute(
                        "UPDATE career_races SET status = 'completed' WHERE id = ?",
                        (race_id,),
                    )
                    conn.commit()

            career_championship_id = int(config.get("career_championship_id") or 0)
            championship = None
            if career_championship_id > 0:
                with db.get_connection() as conn:
                    row = conn.execute(
                        """
                        SELECT id, name, discipline, tier, season_length, current_season
                        FROM career_championships
                        WHERE id = ?
                        """,
                        (career_championship_id,),
                    ).fetchone()
                    if row:
                        rowd = dict(row)
                        from types import SimpleNamespace

                        championship = SimpleNamespace(**rowd)

            if (
                championship is None
                and self.main_menu
                and hasattr(self.main_menu, "career_window")
            ):
                existing = getattr(self.main_menu, "career_window")
                championship = getattr(existing, "championship", None)

            if championship is None:
                self.return_to_menu()
                return

            self._show_or_create_career_hq(championship)
        except Exception as e:
            print(f"[LAUNCHER] ERROR progressing career mode: {e}")
            import traceback

            traceback.print_exc()
            self.return_to_menu()

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
