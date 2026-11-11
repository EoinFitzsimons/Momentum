"""Capture screenshots of all major UI screens/dialogs for review.
Saves PNGs under `saves/accessibility_screenshots/all_screens/`.
"""

import os
import sys
import time
from types import SimpleNamespace
from typing import cast

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QMessageBox

from momentum.database.database_manager import DatabaseManager


OUT_DIR = os.path.join(
    os.path.dirname(ROOT), "saves", "accessibility_screenshots", "all_screens"
)
os.makedirs(OUT_DIR, exist_ok=True)

CAPTURE_PRESETS = (
    ("16x10", 2560, 1600),
    ("16x9", 2560, 1440),
)


def save_pix(widget, name):
    widget.repaint()
    QApplication.processEvents()
    time.sleep(0.15)
    pix = widget.grab()
    path = os.path.join(OUT_DIR, name)
    pix.save(path)
    return path


def prepare_capture_window(widget, width: int, height: int):
    """Force a predictable monitor-like window size for screenshots."""
    try:
        widget.showNormal()
    except Exception:
        pass
    widget.setMinimumSize(0, 0)
    widget.setMaximumSize(16777215, 16777215)
    widget.resize(width, height)
    widget.setFixedSize(width, height)
    widget.setMinimumSize(0, 0)
    QApplication.processEvents()
    time.sleep(0.2)
    QApplication.processEvents()
    # Ensure the widget has a stylesheet; if not, inherit the app-level stylesheet
    try:
        app = QApplication.instance()
        if app is not None:
            app_ss = cast(QApplication, app).styleSheet() or ""  # type: ignore[call-overload]
            ws = widget.styleSheet() or ""
            if app_ss and not ws:
                widget.setStyleSheet(app_ss)
                print(
                    f"[DEBUG] Applied app-level stylesheet to widget {type(widget).__name__}"
                )
    except Exception:
        pass


def capture_main_menu(app, width: int, height: int, suffix: str):
    # Import GUI widgets after QApplication exists to avoid QPixmap-before-QApplication
    from momentum.gui.gui_main_menu import MainMenuWindow

    win = MainMenuWindow()
    try:
        win.display_mode = "windowed"
        win._apply_display_mode()
    except Exception:
        pass
    prepare_capture_window(win, width, height)
    win.show()
    # Debug: print stylesheet information to diagnose missing theme issues
    try:
        ws = win.styleSheet() or ""
        print(f"[DEBUG] main_menu.styleSheet len={len(ws)} snippet={ws[:200]!r}")
    except Exception:
        pass
    path = save_pix(win, f"main_menu_{suffix}.png")
    # Try opening About as a separate capture
    about = QMessageBox()
    about.setWindowTitle("About Momentum")
    about.setText("<h2>Momentum Racing Simulator</h2>\n<p>About snapshot</p>")
    about.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_capture_window(about, max(900, width // 2), max(500, height // 3))
    about.show()
    QApplication.processEvents()
    time.sleep(0.1)
    try:
        aws = about.styleSheet() or ""
        print(f"[DEBUG] about_dialog.styleSheet len={len(aws)} snippet={aws[:200]!r}")
    except Exception:
        pass
    about_path = save_pix(about, f"about_dialog_{suffix}.png")
    about.close()
    return win, path, about_path


def capture_quick_race(app, parent_win, width: int, height: int, suffix: str):
    # Use parent drivers for realistic dialog
    from momentum.gui.gui_main_menu import QuickRaceSetupWindow

    drivers = getattr(parent_win, "drivers", [])
    dialog = QuickRaceSetupWindow(
        parent_win, drivers, getattr(parent_win, "display_mode", "borderless")
    )
    prepare_capture_window(dialog, width, height)
    dialog.show()
    path = save_pix(dialog, f"quick_race_setup_{suffix}.png")
    dialog.close()
    return path


def capture_race_window(app, width: int, height: int, suffix: str):
    # Create race window but don't start the race thread
    from momentum.gui.gui_race_visual import RaceWindow

    rw = RaceWindow()
    try:
        rw.set_display_mode("windowed")
    except Exception:
        prepare_capture_window(rw, width, height)
    else:
        prepare_capture_window(rw, width, height)
    rw.show()
    path = save_pix(rw, f"race_window_{suffix}.png")
    return rw, path


def _seed_career_world() -> tuple[SimpleNamespace, int, str]:
    """Create a small career save so the career HQ window has real content."""
    from momentum.services.tier_service import normalise_tier
    from momentum.gui.gui_career import (
        CareerSelectionDialog,
        PLAYER_ID,
        WORLD_START_DATE,
    )

    db = DatabaseManager()
    seed_dialog = CareerSelectionDialog(db)
    seed_dialog._ensure_career_tables()
    seed_dialog._upsert_profile(
        PLAYER_ID,
        {
            "player_name": "Screenshot Driver",
            "age": 28,
            "height_cm": 180.0,
            "nationality": "Irish",
            "bio": "Temporary career save for screenshot capture.",
        },
    )
    seed_dialog._reset_world_to_start_date(PLAYER_ID, WORLD_START_DATE)

    with db.get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, name, discipline, tier, season_length, current_season
            FROM career_championships
            WHERE player_id = ?
            ORDER BY id
            LIMIT 1
            """,
            (PLAYER_ID,),
        ).fetchone()
        if row is None:
            raise RuntimeError("Could not seed career championships for screenshots")
        championship = SimpleNamespace(**dict(row))

    teams = db.get_teams_by_discipline(str(championship.discipline))
    if not teams:
        teams = db.get_all_teams()
    if not teams:
        raise RuntimeError("Could not find any teams for career screenshot capture")

    team = None
    desired_tier = normalise_tier(getattr(championship, "tier", "TIER_2"))
    for candidate in teams:
        if normalise_tier(getattr(candidate, "tier", "TIER_2")) == desired_tier:
            team = candidate
            break
    if team is None:
        team = teams[0]

    db.assign_team_owner(int(team.id), PLAYER_ID)
    return championship, int(team.id), str(team.discipline)


def capture_career_windows(app, width: int, height: int, suffix: str):
    from momentum.gui.gui_career import (
        CareerProfileDialog,
        CareerSelectionDialog,
        CareerTeamSelectionDialog,
        CareerWindow,
    )

    championship, team_id, discipline = _seed_career_world()
    generated = []

    selection_db = DatabaseManager()
    selection_dialog = CareerSelectionDialog(selection_db)
    prepare_capture_window(selection_dialog, width, height)
    selection_dialog.show()
    generated.append(save_pix(selection_dialog, f"career_selection_{suffix}.png"))
    selection_dialog.close()

    profile_dialog = CareerProfileDialog()
    prepare_capture_window(profile_dialog, width, height)
    profile_dialog.show()
    generated.append(save_pix(profile_dialog, f"career_profile_{suffix}.png"))
    profile_dialog.close()

    team_dialog = CareerTeamSelectionDialog(
        selection_db, discipline, getattr(championship, "tier", None)
    )
    prepare_capture_window(team_dialog, width, height)
    team_dialog.show()
    generated.append(save_pix(team_dialog, f"career_team_selection_{suffix}.png"))
    team_dialog.close()

    career_window = CareerWindow(championship)
    prepare_capture_window(career_window, width, height)
    career_window.show()
    generated.append(save_pix(career_window, f"career_hq_{suffix}.png"))
    career_window.close()

    return generated


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    # Ensure consistent style and apply accessibility settings (like launcher does)
    try:
        app.setStyle("Fusion")
    except Exception:
        pass
    try:
        from momentum.gui.accessibility_settings import (
            load_accessibility_settings,
            apply_accessibility_to_app,
        )

        settings = load_accessibility_settings()
        apply_accessibility_to_app(app, settings)
        print(
            f"[DEBUG] Applied accessibility settings: theme={settings.get('theme')}, ui_scale={settings.get('ui_scale')}"
        )
        ss = app.styleSheet() or ""
        print(f"[DEBUG] app.styleSheet len={len(ss)} snippet={ss[:200]!r}")
    except Exception as e:
        print(f"[DEBUG] Could not apply accessibility at app-level: {e}")
    generated = []

    for suffix, width, height in CAPTURE_PRESETS:
        menu_win, menu_path, about_path = capture_main_menu(app, width, height, suffix)
        generated.extend([menu_path, about_path])

        qr_path = capture_quick_race(app, menu_win, width, height, suffix)
        generated.append(qr_path)

        rw, race_path = capture_race_window(app, width, height, suffix)
        generated.append(race_path)

        generated.extend(capture_career_windows(app, width, height, suffix))

    print("\nCaptured:")
    for p in generated:
        print(" -", p)

    # Close windows
    try:
        menu_win.close()
    except Exception:
        pass
    try:
        rw.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()
