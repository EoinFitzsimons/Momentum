"""
Main Menu GUI for Momentum Racing Simulator.

Provides:
- Race Mode selection
- Driver selection
- Race controls (pace, overtake aggressiveness)
- Options (display settings: windowed, borderless windowed, fullscreen)
"""

from database.database_manager import DatabaseManager
from config import QUICK_RACE_LIST_SIZE
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal
from services.driver_attributes import (
    # get_driver_skill removed (unused)
    get_driver_skill_int,
    get_display_name,
    get_display_nationality,
    get_preferred_window_size,
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QDialog,
)
import sys
import os
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COMBO_BOX_STYLE = """
    QComboBox {
        background-color: #353839;
        color: #B9F2FF;
        border: 2px solid #B9F2FF;
        border-radius: 8px;
        padding: 8px;
        font-size: 14px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 8px solid #B9F2FF;
    }
    QComboBox QAbstractItemView {
        background-color: #353839;
        color: #B9F2FF;
        selection-background-color: #DD2D4A;
        selection-color: #F5F5F5;
        border: 2px solid #B9F2FF;
    }
"""


class DriverCard(QWidget):
    """Premium driver card widget with team colors and detailed info."""
    
    def __init__(self, drv, db=None, parent=None):
        super().__init__(parent)
        self.drv = drv
        self.db = db
        
        # Main layout - horizontal for team color bar + content
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        
        # Team color bar (left edge indicator)
        team_bar = QWidget()
        team_bar.setFixedWidth(5)
        team = self._resolve_team(db, drv)
        
        # Get team color - use team primary color or discipline-based color
        team_color = self._resolve_team_color(team)
        
        team_bar.setStyleSheet(f'background-color: {team_color};')
        h.addWidget(team_bar)
        
        # Main card content
        card_content = QWidget()
        card_layout = QVBoxLayout(card_content)
        card_layout.setContentsMargins(12, 8, 12, 8)
        card_layout.setSpacing(4)
        
        # Top row: Initials + Name + Team
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        
        # Initials box
        display_name = get_display_name(drv)
        initials_text = (display_name[:3].upper() if display_name and display_name != 'Unknown' else '---')
        initials = QLabel(initials_text)
        initials.setFixedSize(42, 42)
        initials.setAlignment(Qt.AlignmentFlag.AlignCenter)
        initials.setStyleSheet(f'background-color: {team_color}; color: #1A1A1A; border-radius:4px; font-weight:700; font-size:13px;')
        top_row.addWidget(initials)
        
        # Name + Team info
        name_team_layout = QVBoxLayout()
        name_team_layout.setSpacing(2)
        
        # Driver name
        name_label = QLabel(display_name)
        name_label.setStyleSheet('font-weight:700; color:#B9F2FF; font-size:13px;')
        name_team_layout.addWidget(name_label)
        
        # Team name
        team_name_text = ''
        if team:
            team_name_text = getattr(team, 'name', 'Unknown Team')
        name_team_layout.addWidget(QLabel(team_name_text))
        
        top_row.addLayout(name_team_layout)
        top_row.addStretch()
        
        # Age (computed_age property)
        try:
            age = drv.computed_age if hasattr(drv, 'computed_age') else 0
        except Exception:
            age = 0
        age_label = QLabel(f"{age}y")
        age_label.setStyleSheet('color:#999; font-size:11px; font-weight:600;')
        age_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top_row.addWidget(age_label)
        
        card_layout.addLayout(top_row)
        
        # Bottom row: Nationality, Rating, Discipline
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)
        
        # Nationality with flag emoji
        nat = get_display_nationality(drv)
        nat_label = QLabel(nat)
        nat_label.setStyleSheet('color:#888; font-size:10px;')
        bottom_row.addWidget(nat_label)
        
        # Overall rating (scale 0-100)
        rating = get_driver_skill_int(drv)
        rating_label = QLabel(f"Rating: {rating}")
        rating_label.setStyleSheet('color:#B9F2FF; font-size:11px; font-weight:600;')
        bottom_row.addWidget(rating_label)
        
        # Preferred discipline (shortened)
        discipline = getattr(drv, 'preferred_discipline', 'SINGLE_SEATER')
        if discipline:
            disc_short = discipline.split('_')[0][:3]  # "SINGLE_SEATER" -> "SIN"
            disc_label = QLabel(disc_short)
            disc_label.setStyleSheet('color:#666; font-size:10px;')
            bottom_row.addWidget(disc_label)
        
        bottom_row.addStretch()
        card_layout.addLayout(bottom_row)
        
        # Card styling
        self.setStyleSheet('''
            DriverCard {{
                background-color: #2E2E2E;
                border: 1px solid #444;
                border-radius: 6px;
            }}
        ''')
        
        h.addWidget(card_content)

    @staticmethod
    def _resolve_team(db, drv):
        """Resolve driver's team object when available."""
        if not db or not hasattr(drv, 'current_team_id') or not drv.current_team_id:
            return None
        try:
            return db.get_team(int(drv.current_team_id))
        except Exception:
            return None

    @staticmethod
    def _resolve_team_color(team) -> str:
        """Resolve safe team color string for card accenting."""
        if team and hasattr(team, 'primary_color'):
            try:
                return team.primary_color if isinstance(team.primary_color, str) else '#B9F2FF'
            except Exception:
                return '#B9F2FF'
        return '#B9F2FF'

    def set_selected(self, selected: bool):
        """Update card appearance for selection."""
        if selected:
            self.setStyleSheet('''
                DriverCard {
                    background-color: #3A3A3A;
                    border: 2px solid #FFB000;
                    border-radius: 6px;
                }
            ''')
        else:
            self.setStyleSheet('''
                DriverCard {
                    background-color: #2E2E2E;
                    border: 1px solid #444;
                    border-radius: 6px;
                }
            ''')


class MainMenuWindow(QMainWindow):
    """Main menu for Momentum Racing Simulator."""

    # Signals
    start_race_signal = pyqtSignal(dict)  # Emits race configuration

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Momentum - Main Menu")
        # Use screen-relative sizing for responsiveness
        from PyQt6.QtGui import QGuiApplication
        screen_obj = QGuiApplication.primaryScreen()
        screen = screen_obj.geometry() if screen_obj is not None else None
        # Use 70% of screen size, but respect preferred minimums
        pref_w, pref_h = get_preferred_window_size()
        screen_w = screen.width() if screen is not None else pref_w
        screen_h = screen.height() if screen is not None else pref_h
        window_w = max(pref_w, int(screen_w * 0.7))
        window_h = max(pref_h, int(screen_h * 0.7))
        self.resize(window_w, window_h)
        self.setMinimumSize(800, 600)  # Absolute minimum for usability

        # Apply a dark Momentum palette consistent with existing branding
        self.setStyleSheet("""
            /* Global dark theme */
            QMainWindow { background-color: #353839; }
            QWidget { background-color: #353839; color: #B9F2FF; font-family: 'Inter', 'Segoe UI', sans-serif; }

            /* Group boxes / panels */
            QGroupBox { background-color: transparent; border: 1px solid rgba(185,242,255,0.08); border-radius: 8px; margin-top: 12px; padding: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #DD2D4A; font-size: 14px; font-weight: 600; }

            /* Labels and typography */
            QLabel { color: #B9F2FF; }
            QLabel.h1 { font-size: 36px; font-weight: 700; }
            QLabel.h2 { font-size: 22px; font-weight: 600; }

            /* Buttons */
            QPushButton { border: none; border-radius: 8px; padding: 10px; font-weight: 700; }
            QPushButton.primary { background-color: #B9F2FF; color: #353839; }
            QPushButton.secondary { background-color: #DD2D4A; color: #FFFFFF; }
            QPushButton:disabled { background-color: #2E2E2E; color: #777777; }

            /* ComboBox */
            QComboBox { background-color: #2E2E2E; color: #B9F2FF; border: 1px solid rgba(185,242,255,0.08); padding: 6px; }

            /* Radio buttons */
            QRadioButton { color: #B9F2FF; }
            QRadioButton::indicator { width: 16px; height: 16px; }

            /* List / Driver selector */
            QListWidget { background-color: #2C2C2C; color: #B9F2FF; border: 1px solid rgba(185,242,255,0.06); }
            QListWidget::item { border: none; }
            /* Remove the default selection background; cards will draw their own */
            QListWidget::item:selected { background-color: transparent; color: #1A1A1A; font-weight: 700; }

            /* Headers */
            QHeaderView::section { background-color: #2F2F2F; color: #B9F2FF; padding: 6px; border: none; }
        """)

        # Display settings
        self.display_mode = "borderless"  # Default: borderless windowed

        # Race settings
        self.selected_driver = None
        self.pace_setting = 50  # 0-100 scale
        self.overtake_aggression = 50  # 0-100 scale

        # Database
        self.db: Optional[DatabaseManager] = None
        self.drivers = []

        self._setup_ui()
        self._load_drivers()
        self._apply_display_mode()

    def _setup_ui(self):
        """Setup main menu UI."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("MOMENTUM")
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #B9F2FF; font-weight: bold;")
        main_layout.addWidget(title)

        subtitle = QLabel("Multi-Discipline Motorsport Manager")
        subtitle_font = QFont()
        subtitle_font.setPointSize(16)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #DD2D4A; font-weight: bold;")
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(30)

        # Main buttons container
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(20)

        # Left side: Race Mode
        race_mode_box = self._create_race_mode_section()
        buttons_container.addWidget(race_mode_box)

        # Right side: Options
        options_box = self._create_options_section()
        buttons_container.addWidget(options_box)

        main_layout.addLayout(buttons_container)

        # Exit button at bottom
        exit_btn = QPushButton("Exit")
        exit_btn.setMinimumHeight(50)
        exit_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #353839;
                color: #B9F2FF;
                border: 3px solid #B9F2FF;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #DD2D4A;
                color: #F5F5F5;
                border-color: #DD2D4A;
            }
            QPushButton:pressed {
                background-color: #8B0000;
                color: #F5F5F5;
            }
        """)
        exit_btn.clicked.connect(self.close)
        main_layout.addWidget(exit_btn)

    def _create_race_mode_section(self):
        """Create race mode selection section."""
        group = QGroupBox("Race Mode")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Quick Race button
        quick_race_btn = QPushButton("Quick Race")
        quick_race_btn.setMinimumHeight(80)
        quick_race_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #353839;
                color: #B9F2FF;
                border: 4px solid #B9F2FF;
                border-radius: 12px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #B9F2FF;
                color: #353839;
            }
            QPushButton:pressed {
                background-color: #DD2D4A;
                color: #F5F5F5;
                border-color: #DD2D4A;
            }
        """)
        quick_race_btn.clicked.connect(self._show_quick_race_setup)
        layout.addWidget(quick_race_btn)

        # Championship Mode (placeholder)
        championship_btn = QPushButton("Championship Mode")
        championship_btn.setMinimumHeight(80)
        championship_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #353839;
                color: #B9F2FF;
                border: 4px solid #B9F2FF;
                border-radius: 12px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #B9F2FF;
                color: #353839;
            }
            QPushButton:pressed {
                background-color: #DD2D4A;
                color: #F5F5F5;
                border-color: #DD2D4A;
            }
            QPushButton:disabled {
                background-color: #353839;
                color: #666;
                border-color: #555;
            }
        """)
        championship_btn.setEnabled(True)  # Now implemented!
        championship_btn.setToolTip("Start or continue a championship season")
        championship_btn.clicked.connect(self._show_championship_mode)
        layout.addWidget(championship_btn)

        # Career Mode
        career_btn = QPushButton("Career Mode")
        career_btn.setMinimumHeight(80)
        career_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #353839;
                color: #B9F2FF;
                border: 4px solid #B9F2FF;
                border-radius: 12px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #B9F2FF;
                color: #353839;
            }
            QPushButton:pressed {
                background-color: #DD2D4A;
                color: #F5F5F5;
                border-color: #DD2D4A;
            }
            QPushButton:disabled {
                background-color: #353839;
                color: #666;
                border-color: #555;
            }
        """)
        career_btn.setEnabled(True)
        career_btn.setToolTip("Start or continue a career season")
        career_btn.clicked.connect(self._show_career_mode)
        layout.addWidget(career_btn)

        layout.addStretch()

        return group

    def _create_options_section(self):
        """Create options section with display settings."""
        group = QGroupBox("Options")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Display settings
        display_label = QLabel("Display Mode:")
        display_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(display_label)

        # Radio buttons for display mode
        self.display_button_group = QButtonGroup(self)

        windowed_radio = QRadioButton("Windowed (1600x900)")
        windowed_radio.setProperty("mode", "windowed")
        self.display_button_group.addButton(windowed_radio, 1)
        layout.addWidget(windowed_radio)

        borderless_radio = QRadioButton("Borderless Windowed (Fullscreen)")
        borderless_radio.setProperty("mode", "borderless")
        borderless_radio.setChecked(True)  # Default
        self.display_button_group.addButton(borderless_radio, 2)
        layout.addWidget(borderless_radio)

        fullscreen_radio = QRadioButton("Fullscreen (Exclusive)")
        fullscreen_radio.setProperty("mode", "fullscreen")
        self.display_button_group.addButton(fullscreen_radio, 3)
        layout.addWidget(fullscreen_radio)

        # Connect radio buttons
        self.display_button_group.buttonClicked.connect(
            self._on_display_mode_changed)

        layout.addSpacing(20)

        # Apply button
        apply_btn = QPushButton("Apply Display Settings")
        apply_btn.setMinimumHeight(50)
        apply_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #353839;
                color: #B9F2FF;
                border: 3px solid #B9F2FF;
                border-radius: 10px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #B9F2FF;
                color: #353839;
            }
            QPushButton:pressed {
                background-color: #DD2D4A;
                color: #F5F5F5;
            }
        """)
        apply_btn.clicked.connect(self._apply_display_mode)
        layout.addWidget(apply_btn)
        layout.addStretch()

        # About button
        about_btn = QPushButton("About")
        about_btn.setMinimumHeight(50)
        about_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #353839;
                color: #B9F2FF;
                border: 3px solid #B9F2FF;
                border-radius: 10px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #B9F2FF;
                color: #353839;
            }
            QPushButton:pressed {
                background-color: #DD2D4A;
                color: #F5F5F5;
            }
        """)
        about_btn.clicked.connect(self._show_about)
        layout.addWidget(about_btn)

        return group

    def _show_quick_race_setup(self):
        """Show quick race setup dialog."""
        setup_window = QuickRaceSetupWindow(
            self, self.drivers, self.display_mode)
        setup_window.race_start.connect(self._on_race_start)
        setup_window.exec()
    
    def _show_championship_mode(self):
        """Show championship selection/management."""
        from GUI.gui_championship import ChampionshipSelectionDialog, ChampionshipWindow
        if self.db is None:
            QMessageBox.warning(self, "Database Unavailable", "Database is not initialized.")
            return
        
        # Show championship selection
        dialog = ChampionshipSelectionDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_championship:
            # Show championship window
            self.championship_window = ChampionshipWindow(dialog.selected_championship, self)
            self.championship_window.return_to_menu.connect(self._return_from_championship)
            self.championship_window.start_race_signal.connect(self._start_championship_race)
            self.championship_window.show()
            self.hide()

    def _show_career_mode(self):
        """Show career selection/management in a dedicated career GUI."""
        from GUI.gui_career import CareerSelectionDialog, CareerWindow
        if self.db is None:
            QMessageBox.warning(self, "Database Unavailable", "Database is not initialized.")
            return

        dialog = CareerSelectionDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_championship:
            self.career_window = CareerWindow(dialog.selected_championship, self)
            self.career_window.return_to_menu.connect(self._return_from_career)
            self.career_window.start_race_signal.connect(self._start_career_race)
            self.career_window.show()
            self.hide()
    
    def _return_from_championship(self):
        """Return from championship to main menu."""
        if hasattr(self, 'championship_window'):
            self.championship_window.close()
        self.show()

    def _return_from_career(self):
        """Return from career to main menu."""
        if hasattr(self, 'career_window'):
            self.career_window.close()
        self.show()
    
    def _start_championship_race(self, config: dict):
        """Start a championship race."""
        # Add display mode to config
        config["display_mode"] = self.display_mode
        self.start_race_signal.emit(config)
        if hasattr(self, 'championship_window'):
            self.championship_window.hide()

    def _start_career_race(self, config: dict):
        """Start a career race."""
        config["display_mode"] = self.display_mode
        self.start_race_signal.emit(config)
        if hasattr(self, 'career_window'):
            self.career_window.hide()

    def _on_display_mode_changed(self, button):
        """Handle display mode radio button change."""
        self.display_mode = button.property("mode")
        print(f"[INFO] Display mode selected: {self.display_mode}")

    def _apply_display_mode(self):
        """Apply current display mode to main menu window."""
        screen_obj = QApplication.primaryScreen()
        screen = screen_obj.geometry() if screen_obj else None

        if self.display_mode == "windowed":
            self.setWindowFlags(Qt.WindowType.Window)
            self.showNormal()
            self.setGeometry(100, 100, 1000, 700)
            print("[INFO] Applied windowed mode (1000x700)")

        elif self.display_mode == "borderless":
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            if screen is not None:
                self.setGeometry(screen)
            self.showMaximized()
            print("[INFO] Applied borderless windowed fullscreen")

        elif self.display_mode == "fullscreen":
            self.setWindowFlags(Qt.WindowType.Window)
            self.showFullScreen()
            print("[INFO] Applied exclusive fullscreen")

        self.show()

    def _load_drivers(self):
        """Load drivers from database."""
        try:
            self.db = DatabaseManager()
            self.drivers = self.db.get_all_drivers()
            print(f"[INFO] Loaded {len(self.drivers)} drivers from database")
        except Exception as e:
            print(f"[ERROR] Failed to load drivers: {e}")
            import traceback
            traceback.print_exc()
            self.drivers = []

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Momentum",
            "<h2>Momentum Racing Simulator</h2>"
            "<p>Version 1.0 Alpha</p>"
            "<p>A multi-discipline motorsport management simulator.</p>"
            "<p><b>Developer:</b> Eoin Fitzsimons</p>"
            "<p><b>Project:</b> Final Year Computer Science Project</p>"
            "<p><b>Year:</b> 2025-2026</p>"
        )

    def _on_race_start(self, config: dict):
        """Handle race start from setup dialog."""
        print(f"[INFO] Starting race with config: {config}")
        self.start_race_signal.emit(config)
        self.hide()  # Hide main menu while racing

    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        """Handle ESC key to exit fullscreen/borderless modes."""
        if a0 is None:
            return
        if a0.key() == Qt.Key.Key_Escape:
            if self.display_mode in ["fullscreen", "borderless"]:
                # Return to windowed mode
                for button in self.display_button_group.buttons():
                    if button.property("mode") == "windowed":
                        button.setChecked(True)
                        self.display_mode = "windowed"
                        self._apply_display_mode()
                        break
            else:
                # In windowed mode, ESC does nothing (or could close)
                pass
        else:
            super().keyPressEvent(a0)


class QuickRaceSetupWindow(QDialog):
    """Quick race setup dialog with driver selection and race controls."""

    race_start = pyqtSignal(dict)  # Emits race configuration

    def __init__(self, parent, drivers, display_mode):
        super().__init__(parent)
        self.parent_window = parent
        self.drivers = drivers
        self.db = getattr(parent, "db", None)
        self.display_mode = display_mode
        self.selected_driver = None
        self.selected_team = None

        self.setWindowTitle("Quick Race Setup")
        # Use application-modal dialog with window flags so it appears as a
        # standalone dialog (not an embedded child) and can be resized.
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        # Ensure dialog has a normal window frame so it can be resized and
        # positioned independent of the (possibly frameless) main window.
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)

        # Size dialog responsively based on screen size
        from PyQt6.QtGui import QGuiApplication
        screen_obj = QGuiApplication.primaryScreen()
        screen = screen_obj.geometry() if screen_obj is not None else None
        screen_w = screen.width() if screen is not None else 1400
        screen_h = screen.height() if screen is not None else 1000
        w = min(int(screen_w * 0.85), 1400)  # Max 85% of screen or 1400px
        h = min(int(screen_h * 0.85), 1000)  # Max 85% of screen or 1000px
        self.setMinimumSize(800, 600)  # Usable minimum
        self.resize(w, h)

        # Build UI once
        self._setup_ui()

    def _setup_ui(self):
        """Setup quick race setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Quick Race Setup")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Driver selection + profile area
        selection_container = QHBoxLayout()
        selection_container.setSpacing(16)

        # Left: driver list with compact cards
        driver_group = QGroupBox("Select Your Driver")
        # Remove fixed minimum width - let it be flexible
        from PyQt6.QtWidgets import QSizePolicy
        driver_group.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        driver_layout = QVBoxLayout(driver_group)

        self.driver_list = QListWidget()
        # Remove fixed minimum height - let it expand to fill space
        self.driver_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.driver_list.setStyleSheet("""
            QListWidget { background-color: #1A1A1A; }
            QListWidget::item:selected { background-color: transparent; }
        """)

        # Use SingleSelection so keyboard up/down arrows change the current
        # item; the stylesheet prevents the native selection background so
        # our DriverCard draws the visible selection instead.
        self.driver_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.driver_list.setSpacing(4)  # Compact spacing between cards

        # Populate with DriverCard widgets (selection pool defined in config)
        for driver in self.drivers[:QUICK_RACE_LIST_SIZE]:
            item = QListWidgetItem()
            # Store driver object for retrieval
            item.setData(Qt.ItemDataRole.UserRole, driver)

            # Create a small visual card. We avoid setting the item's text
            # because the custom widget draws the name; setting text causes
            # duplicate name rendering in some Qt themes.
            card = DriverCard(driver, self.db)
            # Ensure the item has enough height to show the widget
            item.setSizeHint(card.sizeHint())

            self.driver_list.addItem(item)
            self.driver_list.setItemWidget(item, card)

        self.driver_list.setCurrentRow(0)
        driver_layout.addWidget(self.driver_list)

        selection_container.addWidget(driver_group)

        # Right side: profile + presets
        right_vbox = QVBoxLayout()
        # Driver profile with radar polygon visualisation
        profile_group = QGroupBox("Driver Profile")
        profile_layout = QVBoxLayout(profile_group)

        self.profile_name = QLabel("Name: -")
        self.profile_name.setStyleSheet('font-weight:700; font-size:16px; color:#B9F2FF;')
        profile_layout.addWidget(self.profile_name)

        self.profile_nationality = QLabel("Nationality: -")
        profile_layout.addWidget(self.profile_nationality)

        self.profile_skill = QLabel("Skill: -")
        profile_layout.addWidget(self.profile_skill)

        self.profile_team = QLabel("Team: -")
        profile_layout.addWidget(self.profile_team)

        # RadarWidget placeholder - draws a 6-axis polygon visualisation
        from PyQt6.QtWidgets import QSizePolicy
        from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
        from PyQt6.QtCore import QPointF

        class RadarWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.values = [50.0] * 6
                self.setMinimumSize(220, 220)
                self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            def set_values(self, vals: list[float]):
                if not vals or len(vals) < 6:
                    return
                self.values = [float(v) for v in vals[:6]]
                self.update()

            def paintEvent(self, a0):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                w = self.width()
                h = self.height()
                cx = w / 2
                cy = h / 2
                radius = min(w, h) * 0.40

                # Draw concentric rings
                pen = QPen(QColor('#555555'))
                painter.setPen(pen)
                for i in range(1, 5):
                    r = radius * (i / 5.0)
                    painter.drawEllipse(QPointF(cx, cy), r, r)

                # Draw axes and labels
                axes = 6
                import math
                labels = ['Speed', 'Racecraft', 'Consistency', 'Reactions', 'Setup', 'Tyres']
                for i in range(axes):
                    angle = (math.pi * 2.0 * i) / axes - math.pi / 2
                    x = cx + math.cos(angle) * radius
                    y = cy + math.sin(angle) * radius
                    painter.setPen(QPen(QColor('#888888')))
                    painter.drawLine(QPointF(cx, cy), QPointF(x, y))
                    # Label
                    lx = cx + math.cos(angle) * (radius + 18)
                    ly = cy + math.sin(angle) * (radius + 18)
                    painter.setPen(QPen(QColor('#B9F2FF')))
                    painter.drawText(int(lx - 20), int(ly - 6), 80, 16, Qt.AlignmentFlag.AlignCenter, labels[i])

                # Draw polygon filled
                points = []
                for i, val in enumerate(self.values):
                    ratio = float(val) / 100.0
                    angle = (math.pi * 2.0 * i) / axes - math.pi / 2
                    x = cx + math.cos(angle) * radius * ratio
                    y = cy + math.sin(angle) * radius * ratio
                    points.append(QPointF(x, y))

                # Fill
                painter.setBrush(QBrush(QColor(255, 200, 0, 120)))
                painter.setPen(QPen(QColor('#FFB000'), 2))
                painter.drawPolygon(*points)

        self.radar = RadarWidget()
        profile_layout.addWidget(self.radar, 0, Qt.AlignmentFlag.AlignCenter)

        right_vbox.addWidget(profile_group)

        # Tuning preset selection
        preset_group = QGroupBox("Race Tuning Preset")
        preset_layout = QVBoxLayout(preset_group)

        preset_label = QLabel("Choose simulation style:")
        preset_layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Balanced (Default)", "balanced")
        self.preset_combo.addItem("Aggressive (More Overtakes)", "aggressive")
        self.preset_combo.addItem(
            "Tyre Sensitive (Strategic)",
            "tyre_sensitive")
        self.preset_combo.setCurrentIndex(0)
        self.preset_combo.setStyleSheet(COMBO_BOX_STYLE)
        preset_layout.addWidget(self.preset_combo)

        # Preset descriptions
        preset_desc = QLabel(
            "<b>Balanced:</b> Moderate dirty-air, balanced overtaking<br>"
            "<b>Aggressive:</b> More slipstream, easier overtakes, exciting racing<br>"
            "<b>Tyre Sensitive:</b> High degradation, strategic pit stops"
        )
        preset_desc.setWordWrap(True)
        preset_desc.setStyleSheet("font-size: 11px; color: #999;")
        preset_layout.addWidget(preset_desc)

        right_vbox.addWidget(preset_group)

        # Info note about controls
        info_label = QLabel(
            "💡 Race pace and overtaking controls are available during the race")
        info_label.setStyleSheet(
            "font-size: 12px; color: #888; font-style: italic;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_vbox.addWidget(info_label)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)

        start_btn = QPushButton("Start Race")
        start_btn.setMinimumHeight(50)
        start_btn.setStyleSheet(
            "font-weight: bold; background-color: #4CAF50; color: white;")
        start_btn.clicked.connect(self._start_race)
        button_layout.addWidget(start_btn)

        right_vbox.addLayout(button_layout)

        # Attach right_vbox into selection container and add to main layout
        selection_container.addLayout(right_vbox)
        layout.addLayout(selection_container)

        # Discipline selection (comes first, affects track list)
        discipline_group = QGroupBox("Racing Discipline")
        discipline_layout = QVBoxLayout(discipline_group)
        discipline_label = QLabel("Choose Discipline:")
        discipline_layout.addWidget(discipline_label)

        self.discipline_combo = QComboBox()
        # Add all available disciplines
        self.disciplines_map = {
            "SINGLE_SEATER": "Single Seater (Default)",
            "DRAG_ACCELERATION": "Drag Acceleration",
            "PRODUCTION_TOURING": "Production/Touring",
            "URBAN_STREET": "Urban Street (Drifting)",
            "SPRINT_RALLYCROSS": "Sprint/Rallycross",
            "ENDURANCE": "Endurance",
        }
        for discipline_id, display_name in self.disciplines_map.items():
            self.discipline_combo.addItem(display_name, discipline_id)
        
        self.discipline_combo.setStyleSheet(COMBO_BOX_STYLE)
        self.discipline_combo.setCurrentIndex(0)
        self.discipline_combo.currentIndexChanged.connect(self._on_discipline_changed)
        discipline_layout.addWidget(self.discipline_combo)
        layout.addWidget(discipline_group)

        # Tier selection (discipline first, then tier, then driver)
        tier_group = QGroupBox("Team Tier")
        tier_layout = QVBoxLayout(tier_group)
        tier_label = QLabel("Choose Tier:")
        tier_layout.addWidget(tier_label)

        self.tier_combo = QComboBox()
        self.tier_combo.setStyleSheet(self.discipline_combo.styleSheet())
        self.tier_combo.currentIndexChanged.connect(self._on_tier_changed)
        tier_layout.addWidget(self.tier_combo)
        layout.addWidget(tier_group)

        # Track selection (populates based on selected discipline)
        track_group = QGroupBox("Track Selection")
        track_layout = QVBoxLayout(track_group)
        track_label = QLabel("Choose Track:")
        track_layout.addWidget(track_label)

        self.track_combo = QComboBox()
        self.track_combo.setStyleSheet(COMBO_BOX_STYLE)
        track_layout.addWidget(self.track_combo)
        layout.addWidget(track_group)

        # Populate tracks for initial discipline
        self._update_tiers_for_selected_discipline()
        self._update_tracks_for_discipline()
        self._refresh_driver_list_for_selected_discipline()

        # Connect selection updates
        # Manage selection both for mouse and keyboard changes
        self._prev_selected_item = None
        self.driver_list.itemClicked.connect(self._handle_item_clicked)
        # currentItemChanged handles keyboard-based selection changes
        self.driver_list.currentItemChanged.connect(self._on_driver_selected)

        # Initialise profile with first driver if present
        if self.driver_list.count() > 0:
            self._on_driver_selected(self.driver_list.currentItem(), None)

    def _start_race(self):
        """Start race with current settings."""
        # Get selected driver
        current_item = self.driver_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Driver", "Please select a driver.")
            return

        self.selected_driver = current_item.data(Qt.ItemDataRole.UserRole)

        # Get selected tuning preset
        selected_preset = self.preset_combo.currentData()

        # Get selected discipline and tier
        selected_discipline = self.discipline_combo.currentData()
        selected_tier = self.tier_combo.currentData() if hasattr(self, "tier_combo") else "TIER_2"

        # Enforce valid driver-team contract for the chosen discipline.
        selected_team = self._resolve_driver_team(self.selected_driver)
        if selected_team is None:
            QMessageBox.warning(
                self,
                "No Team Contract",
                "Selected driver is not contracted to a team and cannot start a race."
            )
            return

        team_disc = self._normalize_discipline(getattr(selected_team, "discipline", ""))
        wanted_disc = self._normalize_discipline(selected_discipline)
        if team_disc != wanted_disc:
            QMessageBox.warning(
                self,
                "Discipline Mismatch",
                "Selected driver's contracted team is not in the chosen discipline."
            )
            return

        team_tier = self._normalize_tier(getattr(selected_team, "tier", ""))
        wanted_tier = self._normalize_tier(selected_tier)
        if wanted_tier and team_tier != wanted_tier:
            QMessageBox.warning(
                self,
                "Tier Mismatch",
                "Selected driver's contracted team is not in the chosen tier."
            )
            return

        self.selected_team = selected_team

        # Build config (pace and overtake will be controlled during race)
        # Determine selected track id (None -> default)
        track_id = None
        try:
            data = self.track_combo.currentData()
            track_id = int(data) if data is not None else None
        except Exception:
            track_id = None

        config = {
            "mode": "single_race",
            "personnel_transfers_enabled": False,
            "driver": self.selected_driver,
            "team": self.selected_team,
            "display_mode": self.display_mode,
            "tuning_preset": selected_preset,
            "track_id": track_id,
            "discipline": selected_discipline,
            "tier": self._canonical_tier(selected_tier)
        }

        driver_name = get_display_name(self.selected_driver)
        print(f"[INFO] Starting race with driver: {driver_name}, discipline: {selected_discipline}")

        self.race_start.emit(config)
        self.accept()  # Close dialog with accept status

    def _on_discipline_changed(self):
        """Handle discipline selection change."""
        self._update_tiers_for_selected_discipline()
        self._update_tracks_for_discipline()
        self._refresh_driver_list_for_selected_discipline()

    def _on_tier_changed(self):
        """Handle tier selection change."""
        self._refresh_driver_list_for_selected_discipline()

    def _update_tiers_for_selected_discipline(self):
        """Populate available tiers for the selected discipline."""
        if not hasattr(self, "tier_combo"):
            return

        selected_discipline = self.discipline_combo.currentData()
        previous_tier = self.tier_combo.currentData()
        found_tiers = []

        if self.db is not None and selected_discipline:
            norm_disc = self._normalize_discipline(selected_discipline).lower()
            with self.db.get_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT DISTINCT tier
                    FROM teams
                    WHERE LOWER(REPLACE(discipline, ' ', '_')) = ?
                    ORDER BY tier ASC
                    """,
                    (norm_disc,)
                ).fetchall()
                found_tiers = [self._canonical_tier(r[0]) for r in rows if r and r[0]]

        if not found_tiers:
            found_tiers = ["TIER_1", "TIER_2", "TIER_3"]

        self.tier_combo.blockSignals(True)
        self.tier_combo.clear()
        for tier in found_tiers:
            if tier.endswith("_1"):
                display = "Tier 1"
            elif tier.endswith("_2"):
                display = "Tier 2"
            elif tier.endswith("_3"):
                display = "Tier 3"
            else:
                display = tier.replace("_", " ").title()
            self.tier_combo.addItem(display, tier)

        target = self._canonical_tier(previous_tier)
        idx = self.tier_combo.findData(target)
        self.tier_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.tier_combo.blockSignals(False)

    @staticmethod
    def _normalize_discipline(value: Optional[str]) -> str:
        if not value:
            return ""
        return str(value).strip().upper().replace(" ", "_")

    @staticmethod
    def _normalize_tier(value: Optional[str]) -> str:
        if not value:
            return ""
        return str(value).strip().lower().replace("_", "")

    def _canonical_tier(self, value: Optional[str]) -> str:
        norm = self._normalize_tier(value)
        mapping = {
            "tier1": "TIER_1",
            "tier2": "TIER_2",
            "tier3": "TIER_3",
        }
        return mapping.get(norm, str(value).strip().upper() if value else "TIER_2")

    def _resolve_driver_team(self, driver):
        """Resolve the contracted team object for a driver when available."""
        if driver is None or self.db is None:
            return None
        team_id = getattr(driver, "current_team_id", None)
        if not team_id:
            return None
        try:
            return self.db.get_team(int(team_id))
        except Exception:
            return None

    def _get_contracted_drivers_for_discipline(self, discipline: str, tier: Optional[str] = None) -> List[object]:
        """Return drivers with valid team contracts matching the selected discipline."""
        wanted = self._normalize_discipline(discipline)
        wanted_tier = self._normalize_tier(tier)
        if not wanted or self.db is None:
            return []

        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT d.id
                FROM drivers d
                JOIN teams t ON t.id = d.current_team_id
                WHERE LOWER(REPLACE(t.discipline, ' ', '_')) = ?
                  AND LOWER(REPLACE(t.tier, '_', '')) = ?
                ORDER BY d.speed DESC, d.id ASC
                LIMIT ?
                """,
                (wanted.lower(), wanted_tier, int(QUICK_RACE_LIST_SIZE))
            ).fetchall()

        selected: List[object] = []
        for row in rows:
            driver = self.db.get_driver(int(row[0]))
            if driver is not None:
                selected.append(driver)
        return selected

    def _ensure_contracted_pool_for_discipline(self, discipline: str, tier: Optional[str] = None):
        """Assign uncontracted drivers to discipline teams to keep quick race playable."""
        wanted = self._normalize_discipline(discipline)
        wanted_tier = self._normalize_tier(tier)
        if not wanted or self.db is None:
            return

        with self.db.get_connection() as conn:
            assigned_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM drivers d
                JOIN teams t ON t.id = d.current_team_id
                WHERE LOWER(REPLACE(t.discipline, ' ', '_')) = ?
                                    AND LOWER(REPLACE(t.tier, '_', '')) = ?
                """,
                                (wanted.lower(), wanted_tier)
            ).fetchone()[0]

            target = int(QUICK_RACE_LIST_SIZE)
            needed = max(0, target - int(assigned_count))
            if needed <= 0:
                return

            team_rows = conn.execute(
                """
                SELECT id
                FROM teams
                WHERE LOWER(REPLACE(discipline, ' ', '_')) = ?
                                    AND LOWER(REPLACE(tier, '_', '')) = ?
                ORDER BY operations_rating DESC, id ASC
                """,
                                (wanted.lower(), wanted_tier)
            ).fetchall()
            team_ids = [int(r[0]) for r in team_rows]
            if not team_ids:
                return

            preferred = conn.execute(
                """
                SELECT id
                FROM drivers
                WHERE current_team_id IS NULL
                  AND LOWER(REPLACE(preferred_discipline, ' ', '_')) = ?
                ORDER BY speed DESC, id ASC
                LIMIT ?
                """,
                (wanted.lower(), needed)
            ).fetchall()
            driver_ids = [int(r[0]) for r in preferred]

            if len(driver_ids) < needed:
                fallback = conn.execute(
                    """
                    SELECT id
                    FROM drivers
                    WHERE current_team_id IS NULL
                    ORDER BY speed DESC, id ASC
                    LIMIT ?
                    """,
                    (needed - len(driver_ids),)
                ).fetchall()
                driver_ids.extend(int(r[0]) for r in fallback)

            for idx, driver_id in enumerate(driver_ids):
                team_id = team_ids[idx % len(team_ids)]
                conn.execute(
                    """
                    UPDATE drivers
                    SET current_team_id = ?,
                        contract_length = COALESCE(contract_length, 2),
                        salary = COALESCE(salary, 800000)
                    WHERE id = ?
                    """,
                    (team_id, driver_id)
                )

            if driver_ids:
                conn.commit()
                print(
                    f"[QUICK RACE GRID FIX] Assigned {len(driver_ids)} drivers to {wanted} {self._canonical_tier(tier)} teams"
                )

    def _refresh_driver_list_for_selected_discipline(self):
        """Rebuild quick-race driver list using contracted drivers in current discipline."""
        if not hasattr(self, "driver_list") or not hasattr(self, "discipline_combo"):
            return

        selected_discipline = self.discipline_combo.currentData()
        selected_tier = self.tier_combo.currentData() if hasattr(self, "tier_combo") else "TIER_2"
        contracted = self._get_contracted_drivers_for_discipline(selected_discipline, selected_tier)
        if not contracted:
            self.driver_list.clear()
            self.selected_driver = None
            self.selected_team = None
            self.profile_name.setText("Name: No contracted drivers available")
            self.profile_nationality.setText("Nationality: -")
            self.profile_skill.setText("Skill: -")
            self.profile_team.setText("Team: -")
            return

        self.driver_list.clear()
        for driver in contracted[:QUICK_RACE_LIST_SIZE]:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, driver)
            
            # Create a visual card using the new DriverCard design
            card = DriverCard(driver, self.db)
            item.setSizeHint(card.sizeHint())
            
            self.driver_list.addItem(item)
            self.driver_list.setItemWidget(item, card)

        self.driver_list.setCurrentRow(0)
        self._on_driver_selected(self.driver_list.currentItem(), None)

    def _update_tracks_for_discipline(self):
        """Populate track list based on selected discipline."""
        self.track_combo.clear()
        
        selected_discipline = self.discipline_combo.currentData()
        
        try:
            db = self.parent_window.db if hasattr(self.parent_window, 'db') else None
            if db:
                # Try to get tracks by discipline
                try:
                    tracks = db.get_circuits_by_discipline(selected_discipline)
                except Exception:
                    # Fallback: get all tracks
                    tracks = db.get_all_tracks()
            else:
                tracks = []
            
            if not tracks:
                # No tracks found -> placeholder
                self.track_combo.addItem("Test Circuit (Default)", None)
            else:
                for track in tracks:
                    # Store track id as user data
                    track_name = getattr(track, 'name', f'Track {track.id}')
                    self.track_combo.addItem(track_name, track.id)
        except Exception as e:
            print(f"[WARNING] Error loading tracks: {e}")
            self.track_combo.addItem("Test Circuit (Default)", None)

    def _on_driver_selected(self, current, previous):
        """Update the right-hand profile panel when selection changes."""
        if current is None:
            return
        driver = current.data(Qt.ItemDataRole.UserRole)
        if driver is None:
            return

        self._update_profile_panel(driver)
        self._update_radar_widget_safe(driver)
        self._update_driver_card_selection_style(current, previous)

    def _update_profile_panel(self, driver) -> None:
        """Update profile text fields and selected team for the chosen driver."""
        name = get_display_name(driver)
        nationality = get_display_nationality(driver)
        skill = get_driver_skill_int(driver)
        self.profile_name.setText(name)
        self.profile_nationality.setText(f"Nationality: {nationality}")
        self.profile_skill.setText(f"Skill: {skill}")

        team = self._resolve_driver_team(driver)
        self.selected_team = team
        if team is None:
            self.profile_team.setText("Team: Unassigned")
            return
        team_name = getattr(team, "name", "Unknown Team")
        team_tier = getattr(team, "tier", "N/A")
        self.profile_team.setText(f"Team: {team_name} ({team_tier})")

    def _update_radar_widget_safe(self, driver) -> None:
        """Refresh radar polygon values if helper is available."""
        try:
            from services.driver_attributes import get_driver_radar_values
            self.radar.set_values(get_driver_radar_values(driver))
        except Exception:
            pass

    def _apply_card_style_safe(self, widget, attr_name: str, fallback_style: str = "") -> None:
        """Apply a style stored on a card widget; no-op on failures."""
        if widget is None or not hasattr(widget, 'setStyleSheet'):
            return
        try:
            style = getattr(widget, attr_name, None)
            widget.setStyleSheet(style if style else fallback_style)
        except Exception:
            pass

    def _update_driver_card_selection_style(self, current, previous) -> None:
        """Update visual selection styles for previous and current card widgets."""
        try:
            prev_widget = self.driver_list.itemWidget(previous) if previous is not None else None
            cur_widget = self.driver_list.itemWidget(current)
            self._apply_card_style_safe(prev_widget, '_base_style', '')
            self._apply_card_style_safe(cur_widget, '_selected_style')
        except Exception:
            pass

    def _handle_item_clicked(self, item):
        """Handle clicks on list items and manage selection styles manually."""
        try:
            previous = self._prev_selected_item
            current = item

            # Update previous/current visuals via the existing handler
            self._on_driver_selected(current, previous)

            # Track previous item and update current selection state
            self._prev_selected_item = current

            # Also ensure currentItem is set so other code can read it
            try:
                self.driver_list.setCurrentItem(current)
            except Exception:
                pass
        except Exception:
            pass

    def keyPressEvent(self, a0):
        """Handle keyboard shortcuts inside the quick race dialog.

        - Up/Down: navigate driver list (handled by list when focused)
        - Enter/Return: start the race
        - Backspace: close dialog (go back)
        - Left/Right: change preset when preset combo has focus or when list has focus
        """
        # local import removed - QKeyEvent imported at module level
        try:
            if a0 is None:
                return
            k = a0.key()
            # Start race on Enter/Return
            if k in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._start_race()
                return

            # Backspace -> go back / cancel
            if k == Qt.Key.Key_Backspace:
                self.close()
                return

            # Left/Right to change preset if focus is on preset combo or driver list
            if k in (Qt.Key.Key_Left, Qt.Key.Key_Right):
                fw = self.focusWidget()
                if fw is self.preset_combo or fw is self.driver_list:
                    idx = max(0, self.preset_combo.currentIndex())
                    if k == Qt.Key.Key_Left:
                        idx = max(0, idx - 1)
                    else:
                        idx = min(self.preset_combo.count() - 1, idx + 1)
                    self.preset_combo.setCurrentIndex(idx)
                    return

            # Default: let Qt handle navigation (so Up/Down change current item)
            super().keyPressEvent(a0)
        except Exception:
            try:
                super().keyPressEvent(a0)
            except Exception:
                pass


def main():
    """Run main menu standalone."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    window = MainMenuWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
