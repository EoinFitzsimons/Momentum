"""
Main Menu GUI for Momentum Racing Simulator.

Provides:
- Race Mode selection
- Driver selection
- Race controls (pace, overtake aggressiveness)
- Options (display settings: windowed, borderless windowed, fullscreen)
"""

from momentum.database.database_manager import DatabaseManager
from momentum.config import QUICK_RACE_LIST_SIZE
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal
from momentum.services.driver_attributes import (
    # get_driver_skill removed (unused)
    get_driver_skill_int,
    get_display_name,
    get_display_nationality,
    get_preferred_window_size,
)
from momentum.gui.accessibility_settings import (
    apply_accessibility_to_app,
    available_screen_geometry,
    centred_window_geometry,
    current_ui_scale,
    get_focus_stylesheet,
    get_theme_stylesheet,
    load_accessibility_settings,
    normalize_accessibility_settings,
    save_accessibility_settings,
    scaled,
    scaled_font,
    size_dialog_to_screen,
)
from momentum.gui.themed_messagebox import information, warning, about
from momentum.race_settings import load_race_settings, save_race_settings
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
)
import sys
from typing import Optional, List
from momentum.services.tier_service import DEFAULT_TIER, TIERS, normalise_tier, tier_label


COMBO_BOX_STYLE_TEMPLATE = """
    QComboBox {
        background-color: #353839;
        color: #B9F2FF;
        border: 2px solid #B9F2FF;
        border-radius: 8px;
        padding: __PAD__px;
        font-size: __FONT__px;
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


def combo_box_style() -> str:
    """Combo box stylesheet with padding and font size at the current UI scale."""
    return COMBO_BOX_STYLE_TEMPLATE.replace("__PAD__", str(scaled(8))).replace(
        "__FONT__", str(scaled(14))
    )


def logo_style() -> str:
    """Wordmark style at the current UI scale."""
    return (
        f"font-size: {scaled(30)}px; font-weight: 700; color: #B9F2FF; "
        "letter-spacing: 2px;"
    )


def form_label_style() -> str:
    """Form label style at the current UI scale."""
    return f"font-size: {scaled(14)}px; font-weight: bold;"


COMBO_BOX_STYLE = combo_box_style()
FEINT_BUTTON_BORDER = "1px solid rgba(185,242,255,0.24)"
LOGO_STYLE = logo_style()
UNKNOWN_TEAM = "Unknown Team"
FORM_LABEL_STYLE = form_label_style()
CONTROLS_TUTORIAL_TITLE = "Controls Tutorial"

DISPLAY_MODE_LABELS = {
    "windowed": "Windowed",
    "borderless": "Borderless Windowed (Fullscreen)",
    "fullscreen": "Fullscreen (Exclusive)",
}

RACE_MODE_CAPTIONS = {
    "quick": "One-off race: pick a driver, discipline, tier and circuit.",
    "championship": "A full season calendar with standings across every round.",
    "career": "Build a racing life: team, staff, finances and progression.",
}


def main_menu_stylesheet(theme: str) -> str:
    """Main menu stylesheet with every pixel size derived from the UI scale."""
    px = scaled
    return (
        f"""
            /* Global dark theme */
            QMainWindow {{ background-color: #353839; }}
            QWidget {{ background-color: #353839; color: #B9F2FF; font-family: 'Inter', 'Segoe UI', sans-serif; }}

            /* Group boxes / panels */
            QGroupBox {{ background-color: transparent; border: 1px solid rgba(185,242,255,0.08); border-radius: 8px; margin-top: {px(14)}px; padding: {px(12)}px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: {px(12)}px; padding: 0 {px(6)}px; color: #DD2D4A; font-size: {px(14)}px; font-weight: 600; }}

            /* Labels and typography */
            QLabel {{ color: #B9F2FF; }}
            QLabel.h1 {{ font-size: {px(36)}px; font-weight: 700; }}
            QLabel.h2 {{ font-size: {px(22)}px; font-weight: 600; }}

            /* Buttons */
            QPushButton {{ border: 1px solid rgba(185,242,255,0.24); border-radius: 8px; padding: {px(10)}px; font-weight: 700; }}
            QPushButton[primary="true"] {{ background-color: #B9F2FF; color: #353839; }}
            QPushButton[secondary="true"] {{ background-color: #DD2D4A; color: #FFFFFF; }}
            QPushButton:disabled {{ background-color: #2E2E2E; color: #777777; }}

            /* ComboBox */
            QComboBox {{ background-color: #2E2E2E; color: #B9F2FF; border: 1px solid rgba(185,242,255,0.08); padding: {px(6)}px; }}

            /* Radio buttons */
            QRadioButton {{ color: #B9F2FF; }}
            QRadioButton::indicator {{ width: {px(16)}px; height: {px(16)}px; }}

            /* List / Driver selector */
            QListWidget {{ background-color: #2C2C2C; color: #B9F2FF; border: 1px solid rgba(185,242,255,0.06); }}
            QListWidget::item {{ border: none; }}
            /* Remove the default selection background; cards will draw their own */
            QListWidget::item:selected {{ background-color: transparent; color: #1A1A1A; font-weight: 700; }}

            /* Headers */
            QHeaderView::section {{ background-color: #2F2F2F; color: #B9F2FF; padding: {px(6)}px; border: none; }}
        """
        + get_focus_stylesheet()
        + get_theme_stylesheet(theme, current_ui_scale())
    )


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
        team_bar.setFixedWidth(scaled(5))
        team = self._resolve_team(db, drv)

        # Get team color - use team primary color or discipline-based color
        team_color = self._resolve_team_color(team)

        team_bar.setStyleSheet(f"background-color: {team_color};")
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
        initials_text = (
            display_name[:3].upper()
            if display_name and display_name != "Unknown"
            else "---"
        )
        initials = QLabel(initials_text)
        initials.setFixedSize(scaled(42), scaled(42))
        initials.setAlignment(Qt.AlignmentFlag.AlignCenter)
        initials.setStyleSheet(
            f"background-color: {team_color}; color: #1A1A1A; border-radius:4px; font-weight:700; font-size:{scaled(13)}px;"
        )
        top_row.addWidget(initials)

        # Name + Team info
        name_team_layout = QVBoxLayout()
        name_team_layout.setSpacing(2)

        # Driver name
        name_label = QLabel(display_name)
        name_label.setStyleSheet(f"font-weight:700; color:#B9F2FF; font-size:{scaled(13)}px;")
        name_team_layout.addWidget(name_label)

        # Team name
        team_name_text = ""
        if team:
            team_name_text = getattr(team, "name", UNKNOWN_TEAM)
        name_team_layout.addWidget(QLabel(team_name_text))

        top_row.addLayout(name_team_layout)
        top_row.addStretch()

        # Age (computed_age property)
        try:
            age = drv.computed_age if hasattr(drv, "computed_age") else 0
        except Exception:
            age = 0
        age_label = QLabel(f"{age}y")
        age_label.setStyleSheet(f"color:#999; font-size:{scaled(11)}px; font-weight:600;")
        age_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        top_row.addWidget(age_label)

        card_layout.addLayout(top_row)

        # Bottom row: Nationality, Rating, Discipline
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        # Nationality with flag emoji
        nat = get_display_nationality(drv)
        nat_label = QLabel(nat)
        nat_label.setStyleSheet(f"color:#888; font-size:{scaled(10)}px;")
        bottom_row.addWidget(nat_label)

        # Overall rating (scale 0-100)
        rating = get_driver_skill_int(drv)
        rating_label = QLabel(f"Rating: {rating}")
        rating_label.setStyleSheet(f"color:#B9F2FF; font-size:{scaled(11)}px; font-weight:600;")
        bottom_row.addWidget(rating_label)

        # Preferred discipline (shortened)
        discipline = getattr(drv, "preferred_discipline", "SINGLE_SEATER")
        if discipline:
            disc_short = discipline.split("_")[0][:3]  # "SINGLE_SEATER" -> "SIN"
            disc_label = QLabel(disc_short)
            disc_label.setStyleSheet(f"color:#666; font-size:{scaled(10)}px;")
            bottom_row.addWidget(disc_label)

        bottom_row.addStretch()
        card_layout.addLayout(bottom_row)

        # Card styling
        self.setStyleSheet(
            """
            DriverCard {{
                background-color: #2E2E2E;
                border: 1px solid #444;
                border-radius: 6px;
            }}
        """
        )

        h.addWidget(card_content)

    @staticmethod
    def _resolve_team(db, drv):
        """Resolve driver's team object when available."""
        if not db or not hasattr(drv, "current_team_id") or not drv.current_team_id:
            return None
        try:
            return db.get_team(int(drv.current_team_id))
        except Exception:
            return None

    @staticmethod
    def _resolve_team_color(team) -> str:
        """Resolve safe team color string for card accenting."""
        if team and hasattr(team, "primary_color"):
            try:
                return (
                    team.primary_color
                    if isinstance(team.primary_color, str)
                    else "#B9F2FF"
                )
            except Exception:
                return "#B9F2FF"
        return "#B9F2FF"

    def set_selected(self, selected: bool):
        """Update card appearance for selection."""
        if selected:
            self.setStyleSheet(
                """
                DriverCard {
                    background-color: #3A3A3A;
                    border: 2px solid #FFB000;
                    border-radius: 6px;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                DriverCard {
                    background-color: #2E2E2E;
                    border: 1px solid #444;
                    border-radius: 6px;
                }
            """
            )


class MainMenuWindow(QMainWindow):
    """Main menu for Momentum Racing Simulator."""

    # Signals
    start_race_signal = pyqtSignal(dict)  # Emits race configuration

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Momentum - Main Menu")

        # Widgets whose heights, fonts or stylesheets follow the UI scale.
        self._scaled_heights: list = []
        self._scaled_max_heights: list = []
        self._scaled_fonts: list = []
        self._scaled_styles: list = []
        self._form_labels: list = []
        self._embedded_views = {}
        self._ui_ready = False

        self.accessibility_settings = load_accessibility_settings()
        self.race_settings = load_race_settings()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            apply_accessibility_to_app(app, self.accessibility_settings)

        # Size from the available screen: 70% of the desktop, never below a
        # scaled usable minimum and never larger than the screen itself.
        pref_w, pref_h = get_preferred_window_size()
        self.setGeometry(
            centred_window_geometry(0.7, 0.7, min(pref_w, 960), min(pref_h, 640))
        )
        self._apply_scaled_minimum_size()
        self._apply_menu_stylesheet()

        # Display settings
        self.display_mode = "borderless"  # Default: borderless windowed
        self._applied_display_mode = "borderless"

        # Race settings
        self.selected_driver = None
        self.pace_setting = 50  # 0-100 scale
        self.overtake_aggression = 50  # 0-100 scale

        # Database
        self.db: Optional[DatabaseManager] = None
        self.drivers = []
        self.view_stack: Optional[QStackedWidget] = None
        self.menu_page: Optional[QWidget] = None
        self._embedded_views = {}
        self._embedded_hosts = {}

        self._setup_ui()
        self._load_drivers()
        self._apply_display_mode()

    def _setup_ui(self):
        """Setup main menu UI."""
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.view_stack = QStackedWidget()
        root_layout.addWidget(self.view_stack)

        # The menu content sits in a scroll area so that a large UI scale on
        # a small display never pushes the controls out of reach.
        self.menu_page = QScrollArea()
        self.menu_page.setWidgetResizable(True)
        self.menu_page.setFrameShape(QScrollArea.Shape.NoFrame)
        menu_content = QWidget()
        self.menu_page.setWidget(menu_content)
        self.view_stack.addWidget(self.menu_page)
        self.view_stack.setCurrentWidget(self.menu_page)

        main_layout = QVBoxLayout(menu_content)
        margin = scaled(40)
        main_layout.setContentsMargins(margin, scaled(28), margin, scaled(28))
        main_layout.setSpacing(scaled(16))

        # Title
        title = QLabel("MOMENTUM")
        self._register_scaled_font(title, 40, True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #B9F2FF; font-weight: bold;")
        main_layout.addWidget(title)

        subtitle = QLabel("Multi-Discipline Motorsport Manager")
        self._register_scaled_font(subtitle, 15, True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #DD2D4A; font-weight: bold;")
        main_layout.addWidget(subtitle)

        self.menu_summary_label = QLabel(
            "Game Hub: Choose a mode, tune your options, and jump straight into racing. "
            "Shortcuts: Ctrl+1 Quick Race, Ctrl+2 Championship, Ctrl+3 Career, "
            "Ctrl+Enter Apply Settings, F1 About."
        )
        self.menu_summary_label.setWordWrap(True)
        self.menu_summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.menu_summary_label)

        # Main panels: race modes fill the left column, options the right.
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(scaled(20))

        race_mode_box = self._create_race_mode_section()
        buttons_container.addWidget(race_mode_box, 5)

        options_box = self._create_options_section()
        buttons_container.addWidget(options_box, 6)

        main_layout.addLayout(buttons_container, 1)

        # Exit button at bottom
        exit_btn = QPushButton("Exit")
        self._register_scaled_height(exit_btn, 50)
        exit_btn.setStyleSheet(
            """
            QPushButton {
                font-size: __FONT__px;
                font-weight: bold;
                background-color: #353839;
                color: #B9F2FF;
                border: 1px solid rgba(185,242,255,0.30);
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
        """
        )
        self._register_scaled_style(exit_btn, exit_btn.styleSheet(), {"__FONT__": 16})
        exit_btn.setShortcut("Ctrl+Q")
        exit_btn.setToolTip("Exit the game launcher (Ctrl+Q)")
        exit_btn.setAccessibleName("Exit Application")
        exit_btn.clicked.connect(self.close)
        main_layout.addWidget(exit_btn)

        self._ui_ready = True
        self._update_apply_state()

    def _set_embedded_window(
        self, key: str, host_window: QMainWindow
    ) -> Optional[QWidget]:
        """Embed a mode window into the main stack to keep a single top-level window."""
        if self.view_stack is None:
            return None

        existing_page = self._embedded_views.get(key)
        if existing_page is not None:
            self.view_stack.removeWidget(existing_page)
            existing_page.deleteLater()
            self._embedded_views.pop(key, None)

        existing_host = self._embedded_hosts.get(key)
        if existing_host is not None:
            existing_host.close()
            self._embedded_hosts.pop(key, None)

        embedded_page = host_window.takeCentralWidget()
        if embedded_page is None:
            return None

        embedded_page.setParent(self.view_stack)
        self.view_stack.addWidget(embedded_page)
        self._embedded_views[key] = embedded_page
        self._embedded_hosts[key] = host_window
        return embedded_page

    def _show_menu_page(self):
        """Return to the main menu view in the stacked layout."""
        if self.view_stack is not None and self.menu_page is not None:
            self.view_stack.setCurrentWidget(self.menu_page)

    def _register_scaled_height(self, widget, base_height: int) -> None:
        """Track a widget whose minimum height is a 100%-scale design value."""
        self._scaled_heights.append((widget, int(base_height)))
        widget.setMinimumHeight(scaled(base_height))

    def _register_scaled_max_height(self, widget, base_height: int) -> None:
        """Track a widget whose maximum height is a 100%-scale design value."""
        self._scaled_max_heights.append((widget, int(base_height)))
        widget.setMaximumHeight(scaled(base_height))

    def _register_scaled_font(self, widget, point_size: float, bold: bool = False) -> None:
        """Track a widget whose font point size follows the UI scale."""
        self._scaled_fonts.append((widget, float(point_size), bool(bold)))
        widget.setFont(scaled_font(point_size, bold))

    def _register_scaled_style(self, widget, template: str, sizes: dict) -> None:
        """Track a widget stylesheet whose ``__NAME__`` placeholders are scaled pixels."""
        self._scaled_styles.append((widget, template, dict(sizes)))
        widget.setStyleSheet(self._render_scaled_style(template, sizes))

    @staticmethod
    def _render_scaled_style(template: str, sizes: dict) -> str:
        css = template
        for placeholder, base_px in sizes.items():
            css = css.replace(placeholder, str(scaled(base_px)))
        return css

    def _apply_menu_stylesheet(self) -> None:
        theme = str(self.accessibility_settings.get("theme", "standard"))
        self.setStyleSheet(main_menu_stylesheet(theme))

    def _apply_scaled_metrics(self) -> None:
        """Re-apply every registered scale-dependent height, font and stylesheet."""
        for widget, base_height in self._scaled_heights:
            widget.setMinimumHeight(scaled(base_height))
        for widget, base_height in self._scaled_max_heights:
            widget.setMaximumHeight(scaled(base_height))
        for widget, point_size, bold in self._scaled_fonts:
            widget.setFont(scaled_font(point_size, bold))
        for widget, template, sizes in self._scaled_styles:
            widget.setStyleSheet(self._render_scaled_style(template, sizes))
        for combo in self._option_combos():
            combo.setStyleSheet(combo_box_style())
        for label in self._form_labels:
            label.setStyleSheet(form_label_style())
        self._apply_scaled_minimum_size()

    def _apply_scaled_minimum_size(self) -> None:
        """Usable minimum at the current UI scale, never larger than the screen."""
        screen = available_screen_geometry(self)
        self.setMinimumSize(
            min(scaled(960), screen.width()), min(scaled(640), screen.height())
        )

    def _option_combos(self) -> list:
        return [
            combo
            for combo in (
                getattr(self, "theme_combo", None),
                getattr(self, "ui_scale_combo", None),
                getattr(self, "render_fps_combo", None),
                getattr(self, "simulation_speed_combo", None),
            )
            if combo is not None
        ]

    def refresh_accessibility(self, settings: dict) -> None:
        """Live hook: re-style this window for a new theme or UI scale."""
        self.accessibility_settings = normalize_accessibility_settings(settings)
        self._apply_menu_stylesheet()
        if not self._ui_ready:
            return
        self._apply_scaled_metrics()
        self._sync_accessibility_controls()
        self._update_apply_state()
        for view in list(self._embedded_views.values()):
            hook = getattr(view, "refresh_accessibility", None)
            if callable(hook):
                hook(dict(self.accessibility_settings))
        if self.centralWidget() is not None:
            self.centralWidget().updateGeometry()

    def _create_race_mode_section(self):
        """Create race mode selection section."""
        group = QGroupBox("Race Mode")
        layout = QVBoxLayout(group)
        layout.setSpacing(scaled(12))

        modes = (
            ("Quick Race", "quick", "Ctrl+1", "Quick Race Mode",
             "Start a one-off quick race (Ctrl+1)", self._show_quick_race_setup),
            ("Quick Championship", "championship", "Ctrl+2", "Championship Mode",
             "Start or continue a championship season (Ctrl+2)",
             self._show_championship_mode),
            ("Career Mode", "career", "Ctrl+3", "Career Mode",
             "Start or continue a career season (Ctrl+3)", self._show_career_mode),
        )
        for text, key, shortcut, accessible_name, tooltip, handler in modes:
            button = QPushButton(text)
            button.setProperty("primary", True)
            button.setShortcut(shortcut)
            button.setToolTip(tooltip)
            button.setAccessibleName(accessible_name)
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self._register_scaled_height(button, 96)
            self._register_scaled_max_height(button, 180)
            self._register_scaled_font(button, 16, True)
            button.clicked.connect(handler)
            layout.addWidget(button, 1)

            caption = QLabel(RACE_MODE_CAPTIONS[key])
            caption.setWordWrap(True)
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
            caption.setStyleSheet("color: #9ED8DB;")
            layout.addWidget(caption)
            layout.addSpacing(scaled(8))

        layout.addStretch(1)
        return group

    def _make_form_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(form_label_style())
        self._form_labels.append(label)
        return label

    def _create_options_section(self):
        """Create the options panel: display, appearance and race preferences with one Apply action."""
        group = QGroupBox("Options")
        layout = QVBoxLayout(group)
        layout.setSpacing(scaled(12))

        grid = QGridLayout()
        grid.setHorizontalSpacing(scaled(16))
        grid.setVerticalSpacing(scaled(12))

        # Display mode
        display_box = QGroupBox("Display")
        display_layout = QVBoxLayout(display_box)
        display_layout.addWidget(self._make_form_label("Display Mode:"))
        self.display_button_group = QButtonGroup(self)
        for index, mode in enumerate(("windowed", "borderless", "fullscreen"), start=1):
            radio = QRadioButton(DISPLAY_MODE_LABELS[mode])
            radio.setProperty("mode", mode)
            radio.setChecked(mode == "borderless")
            self.display_button_group.addButton(radio, index)
            display_layout.addWidget(radio)
        self.display_button_group.buttonClicked.connect(self._on_display_mode_changed)
        grid.addWidget(display_box, 0, 0)

        # Appearance / accessibility
        appearance_box = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_box)
        appearance_layout.addWidget(self._make_form_label("Accessibility Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Standard", "standard")
        self.theme_combo.addItem("High Contrast", "high_contrast")
        self.theme_combo.addItem("Colourblind Safe", "colorblind_safe")
        self.theme_combo.setStyleSheet(combo_box_style())
        self.theme_combo.setAccessibleName("Accessibility Theme")
        appearance_layout.addWidget(self.theme_combo)

        appearance_layout.addWidget(self._make_form_label("UI Scale:"))
        self.ui_scale_combo = QComboBox()
        self.ui_scale_combo.addItem("100%", 100)
        self.ui_scale_combo.addItem("125%", 125)
        self.ui_scale_combo.addItem("150%", 150)
        self.ui_scale_combo.setStyleSheet(combo_box_style())
        self.ui_scale_combo.setAccessibleName("UI Scale")
        appearance_layout.addWidget(self.ui_scale_combo)
        grid.addWidget(appearance_box, 0, 1)

        # Race preferences
        race_box = QGroupBox("Race")
        race_layout = QVBoxLayout(race_box)
        race_layout.addWidget(self._make_form_label("Render FPS:"))
        self.render_fps_combo = QComboBox()
        self.render_fps_combo.addItem("Uncapped", 0)
        for fps in (30, 60, 120, 144, 240):
            self.render_fps_combo.addItem(f"{fps} FPS", fps)
        self.render_fps_combo.setStyleSheet(combo_box_style())
        self.render_fps_combo.setAccessibleName("Render FPS")
        race_layout.addWidget(self.render_fps_combo)

        race_layout.addWidget(self._make_form_label("Race Speed:"))
        self.simulation_speed_combo = QComboBox()
        for speed in (0.5, 1.0, 2.0, 5.0, 10.0, 20.0):
            self.simulation_speed_combo.addItem(f"{speed:g}x", speed)
        self.simulation_speed_combo.setStyleSheet(combo_box_style())
        self.simulation_speed_combo.setAccessibleName("Race Speed")
        race_layout.addWidget(self.simulation_speed_combo)
        grid.addWidget(race_box, 1, 0)

        # Help
        help_box = QGroupBox("Help")
        help_layout = QVBoxLayout(help_box)
        tutorial_btn = QPushButton(CONTROLS_TUTORIAL_TITLE)
        self._register_scaled_height(tutorial_btn, 44)
        tutorial_btn.setToolTip(
            "Show quick controls tutorial relevant to current screens"
        )
        tutorial_btn.setAccessibleName(CONTROLS_TUTORIAL_TITLE)
        tutorial_btn.clicked.connect(self._show_controls_tutorial)
        help_layout.addWidget(tutorial_btn)

        about_btn = QPushButton("About")
        self._register_scaled_height(about_btn, 44)
        about_btn.setShortcut("F1")
        about_btn.setToolTip("About this build (F1)")
        about_btn.setAccessibleName("About Momentum")
        about_btn.clicked.connect(self._show_about)
        help_layout.addWidget(about_btn)
        grid.addWidget(help_box, 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)

        # One clear action for the whole options page.
        self.settings_status_label = QLabel("")
        self.settings_status_label.setWordWrap(True)
        self.settings_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settings_status_label.setStyleSheet("color: #9ED8DB;")
        layout.addWidget(self.settings_status_label)

        self.apply_settings_btn = QPushButton("Apply Settings")
        self._register_scaled_height(self.apply_settings_btn, 50)
        self.apply_settings_btn.setProperty("primary", True)
        self.apply_settings_btn.setShortcut("Ctrl+Return")
        self.apply_settings_btn.setToolTip(
            "Apply every changed option on this page (Ctrl+Enter)"
        )
        self.apply_settings_btn.setAccessibleName("Apply Settings")
        self.apply_settings_btn.clicked.connect(self._apply_settings)
        layout.addWidget(self.apply_settings_btn)
        layout.addStretch(1)

        self._sync_option_controls()
        for combo in self._option_combos():
            combo.currentIndexChanged.connect(self._update_apply_state)

        return group

    def _sync_accessibility_controls(self) -> None:
        """Set the theme and scale combos to the applied accessibility settings."""
        for combo in (self.theme_combo, self.ui_scale_combo):
            combo.blockSignals(True)
        try:
            theme_idx = self.theme_combo.findData(
                str(self.accessibility_settings.get("theme", "standard"))
            )
            self.theme_combo.setCurrentIndex(theme_idx if theme_idx >= 0 else 0)
            scale_idx = self.ui_scale_combo.findData(
                int(self.accessibility_settings.get("ui_scale", 100))
            )
            self.ui_scale_combo.setCurrentIndex(scale_idx if scale_idx >= 0 else 0)
        finally:
            for combo in (self.theme_combo, self.ui_scale_combo):
                combo.blockSignals(False)

    def _sync_option_controls(self) -> None:
        """Set every option control to the currently applied values."""
        self._sync_accessibility_controls()
        for combo in (self.render_fps_combo, self.simulation_speed_combo):
            combo.blockSignals(True)
        try:
            fps_idx = self.render_fps_combo.findData(
                int(self.race_settings.get("render_fps", 0))
            )
            self.render_fps_combo.setCurrentIndex(fps_idx if fps_idx >= 0 else 0)
            speed_idx = self.simulation_speed_combo.findData(
                float(self.race_settings.get("simulation_speed", 5.0))
            )
            self.simulation_speed_combo.setCurrentIndex(speed_idx if speed_idx >= 0 else 3)
        finally:
            for combo in (self.render_fps_combo, self.simulation_speed_combo):
                combo.blockSignals(False)
        self.display_mode = self._applied_display_mode
        for button in self.display_button_group.buttons():
            if button.property("mode") == self._applied_display_mode:
                button.setChecked(True)
        self._update_apply_state()

    def pending_setting_changes(self) -> List[str]:
        """Names of the options that differ from what is currently applied."""
        changes: List[str] = []
        if self.display_mode != self._applied_display_mode:
            changes.append("display mode")
        if str(self.theme_combo.currentData()) != str(
            self.accessibility_settings.get("theme", "standard")
        ):
            changes.append("theme")
        if int(self.ui_scale_combo.currentData() or 100) != int(
            self.accessibility_settings.get("ui_scale", 100)
        ):
            changes.append("UI scale")
        if int(self.render_fps_combo.currentData() or 0) != int(
            self.race_settings.get("render_fps", 0)
        ):
            changes.append("render FPS")
        if float(self.simulation_speed_combo.currentData() or 5.0) != float(
            self.race_settings.get("simulation_speed", 5.0)
        ):
            changes.append("race speed")
        return changes

    def _update_apply_state(self, *_args) -> None:
        """Enable the Apply button only when something would actually change."""
        if not hasattr(self, "apply_settings_btn"):
            return
        changes = self.pending_setting_changes()
        self.apply_settings_btn.setEnabled(bool(changes))
        if changes:
            self.settings_status_label.setText("Unapplied changes: " + ", ".join(changes))
        else:
            self.settings_status_label.setText("All settings applied")

    def _apply_settings(self) -> None:
        """Apply every changed option in one action and report what changed."""
        changes = self.pending_setting_changes()
        if not changes:
            return
        if "display mode" in changes:
            self._apply_display_mode()
        if "theme" in changes or "UI scale" in changes:
            self._apply_accessibility_settings()
        if "render FPS" in changes or "race speed" in changes:
            self._apply_race_settings()
        self._update_apply_state()
        saved = [change for change in changes if change != "display mode"]
        lines = []
        if saved:
            lines.append("Saved: " + ", ".join(saved) + ".")
        if "display mode" in changes:
            lines.append("Display mode applied for this session.")
        information(self, "Settings", " ".join(lines))

    def _show_quick_race_setup(self):
        """Show quick race setup dialog."""
        setup_window = QuickRaceSetupWindow(self, self.drivers, self.display_mode)
        setup_window.race_start.connect(self._on_race_start)
        setup_window.exec()

    def _show_championship_mode(self):
        """Show championship selection/management."""
        from momentum.gui.gui_championship import ChampionshipSelectionDialog, ChampionshipWindow

        if self.db is None:
            warning(self, "Database Unavailable", "Database is not initialised.")
            return

        # Show championship selection
        dialog = ChampionshipSelectionDialog(self.db, self)
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.selected_championship
        ):
            self.championship_window = ChampionshipWindow(
                dialog.selected_championship, self
            )
            self.championship_window.return_to_menu.connect(
                self._return_from_championship
            )
            self.championship_window.start_race_signal.connect(
                self._start_championship_race
            )

            championship_page = self._set_embedded_window(
                "championship", self.championship_window
            )
            if championship_page is None or self.view_stack is None:
                warning(self, "Navigation Error", "Could not open championship view.")
                return
            self.view_stack.setCurrentWidget(championship_page)

    def _show_career_mode(self):
        """Show career selection/management in a dedicated career GUI."""
        from momentum.gui.gui_career import CareerSelectionDialog, CareerWindow

        if self.db is None:
            warning(self, "Database Unavailable", "Database is not initialised.")
            return

        dialog = CareerSelectionDialog(self.db, self)
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.selected_championship
        ):
            self.career_window = CareerWindow(dialog.selected_championship, self)
            self.career_window.return_to_menu.connect(self._return_from_career)
            self.career_window.start_race_signal.connect(self._start_career_race)

            career_page = self._set_embedded_window("career", self.career_window)
            if career_page is None or self.view_stack is None:
                warning(self, "Navigation Error", "Could not open career view.")
                return
            self.view_stack.setCurrentWidget(career_page)

    def show_career_page(self) -> bool:
        """Bring the embedded Career HQ back, refreshed; False if none is open."""
        return self._show_embedded_page("career", "career_window")

    def show_championship_page(self) -> bool:
        """Bring the embedded championship window back, refreshed; False if none is open."""
        return self._show_embedded_page("championship", "championship_window")

    def _show_embedded_page(self, key: str, window_attr: str) -> bool:
        window = getattr(self, window_attr, None)
        page = self._embedded_views.get(key) if hasattr(self, "_embedded_views") else None
        if window is None or page is None or self.view_stack is None:
            return False
        if hasattr(window, "load_data"):
            window.load_data()
        self.view_stack.setCurrentWidget(page)
        self.show()
        self.raise_()
        self.activateWindow()
        return True

    def _return_from_championship(self):
        """Return from championship to main menu."""
        self._show_menu_page()
        self.show()

    def _return_from_career(self):
        """Return from career to main menu."""
        self._show_menu_page()
        self.show()

    def _start_championship_race(self, config: dict):
        """Start a championship race."""
        # Add display mode to config
        config["display_mode"] = self.display_mode
        config["accessibility"] = dict(self.accessibility_settings)
        config["race_settings"] = dict(self.race_settings)
        self._show_menu_page()
        self.start_race_signal.emit(config)
        self.hide()

    def _start_career_race(self, config: dict):
        """Start a career race."""
        config["display_mode"] = self.display_mode
        config["accessibility"] = dict(self.accessibility_settings)
        config["race_settings"] = dict(self.race_settings)
        self._show_menu_page()
        self.start_race_signal.emit(config)
        self.hide()

    def _on_display_mode_changed(self, button):
        """Handle display mode radio button change."""
        self.display_mode = button.property("mode")
        print(f"[INFO] Display mode selected: {self.display_mode}")
        self._update_apply_state()

    def _apply_display_mode(self):
        """Apply current display mode to main menu window."""
        screen_obj = QApplication.primaryScreen()
        screen = screen_obj.geometry() if screen_obj else None

        if self.display_mode == "windowed":
            self.setWindowFlags(Qt.WindowType.Window)
            self.showNormal()
            geometry = centred_window_geometry(0.7, 0.7, 960, 640, self)
            self.setGeometry(geometry)
            print(
                f"[INFO] Applied windowed mode ({geometry.width()}x{geometry.height()})"
            )

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

        self._applied_display_mode = self.display_mode
        self.show()
        self._update_apply_state()

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
        about(
            self,
            "About Momentum",
            "<h2>Momentum Racing Simulator</h2>"
            "<p>Version 1.0 Alpha</p>"
            "<p>A multi-discipline motorsport management simulator.</p>"
            "<p><b>Developer:</b> Eoin Fitzsimons</p>"
            "<p>Copyright (c) 2026 Eoin Fitzsimons. All rights reserved.</p>",
        )

    def _apply_accessibility_settings(self) -> None:
        """Apply and persist the selected theme and UI scale to every open window."""
        selected_theme = str(self.theme_combo.currentData() or "standard")
        selected_scale = int(self.ui_scale_combo.currentData() or 100)
        new_settings = normalize_accessibility_settings(
            {"theme": selected_theme, "ui_scale": selected_scale}
        )
        self.accessibility_settings = new_settings
        save_accessibility_settings(new_settings)

        app = QApplication.instance()
        if isinstance(app, QApplication):
            # Re-styles the application and calls refresh_accessibility on
            # this window and every other open window.
            apply_accessibility_to_app(app, new_settings)
        else:
            self.refresh_accessibility(new_settings)

    def _show_controls_tutorial(self) -> None:
        """Show a short in-app tutorial for menu and race controls."""
        information(
            self,
            CONTROLS_TUTORIAL_TITLE,
            "Main Menu:\n"
            "- Ctrl+1: Quick Race\n"
            "- Ctrl+2: Championship\n"
            "- Ctrl+3: Career\n"
            "- Ctrl+Enter: Apply display settings\n"
            "- F1: About\n\n"
            "Race Screen (default bindings):\n"
            "- Space: Pause/Resume\n"
            "- A/Z: Increase/Decrease push intensity\n"
            "- X: Toggle overtaking mode\n"
            "- R: Restart race (while paused, with confirmation)\n"
            "- ESC: Return to menu\n\n"
            "You can remap race controls in the race window using Control Bindings.",
        )

    def _apply_race_settings(self) -> None:
        """Persist player-facing render and simulation speed preferences."""
        self.race_settings = save_race_settings(
            {
                "render_fps": self.render_fps_combo.currentData(),
                "simulation_speed": self.simulation_speed_combo.currentData(),
            }
        )
        self._update_apply_state()

    def _on_race_start(self, config: dict):
        """Handle race start from setup dialog."""
        print(f"[INFO] Starting race with config: {config}")
        config["accessibility"] = dict(self.accessibility_settings)
        config["race_settings"] = dict(self.race_settings)
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

        # 80% of the available screen, never below a scaled usable minimum.
        size_dialog_to_screen(self, 0.8, 0.85, 1040, 760)

        # Build UI once
        self._setup_ui()

    def _setup_ui(self):
        """Setup quick race setup UI."""
        layout = QVBoxLayout(self)
        margin = scaled(30)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(scaled(16))

        self.setStyleSheet(f"QPushButton {{ border: {FEINT_BUTTON_BORDER}; }}")

        logo = QLabel("MOMENTUM")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(logo_style())
        layout.addWidget(logo)

        # Title
        title = QLabel("Quick Race Setup")
        title.setFont(scaled_font(22, True))
        layout.addWidget(title)

        self.selection_summary = QLabel(
            "Ready: Select a driver, discipline, tier, and track."
        )
        self.selection_summary.setWordWrap(True)
        self.selection_summary.setStyleSheet(
            "background-color: #18212B; border: 1px solid #2E3B4A; border-radius: 8px; "
            f"padding: {scaled(10)}px; color: #CFE8FF;"
        )
        layout.addWidget(self.selection_summary)

        # Driver selection + profile area. This row takes all spare height so
        # the driver list grows while the profile and preset panels keep the
        # height they need to draw every line.
        selection_container = QHBoxLayout()
        selection_container.setSpacing(scaled(16))

        # Left: driver list with compact cards
        driver_group = QGroupBox("Select Your Driver")
        driver_group.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        driver_layout = QVBoxLayout(driver_group)

        self.driver_list = QListWidget()
        # Remove fixed minimum height - let it expand to fill space
        self.driver_list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.driver_list.setStyleSheet(
            """
            QListWidget { background-color: #1A1A1A; }
            QListWidget::item:selected { background-color: transparent; }
        """
        )

        # Use SingleSelection so keyboard up/down arrows change the current
        # item; the stylesheet prevents the native selection background so
        # our DriverCard draws the visible selection instead.
        self.driver_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.driver_list.setSpacing(4)  # Compact spacing between cards
        self.driver_list.setAccessibleName("Driver Selection List")
        self.driver_list.setToolTip("Use Up/Down keys to select a driver")

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

        selection_container.addWidget(driver_group, 3)

        # Right side: profile + presets, in a panel with a scaled minimum
        # width so labels and the combo box always have room.
        right_panel = QWidget()
        right_panel.setMinimumWidth(scaled(380))
        right_panel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        right_vbox = QVBoxLayout(right_panel)
        right_vbox.setContentsMargins(0, 0, 0, 0)
        right_vbox.setSpacing(scaled(12))
        # Driver profile with radar polygon visualisation
        profile_group = QGroupBox("Driver Profile")
        profile_group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        profile_layout = QVBoxLayout(profile_group)
        profile_layout.setSpacing(scaled(6))

        self.profile_name = QLabel("Name: -")
        self.profile_name.setWordWrap(True)
        self.profile_name.setStyleSheet(
            f"font-weight:700; font-size:{scaled(16)}px; color:#B9F2FF;"
        )
        profile_layout.addWidget(self.profile_name)

        self.profile_nationality = QLabel("Nationality: -")
        self.profile_nationality.setWordWrap(True)
        profile_layout.addWidget(self.profile_nationality)

        self.profile_skill = QLabel("Skill: -")
        profile_layout.addWidget(self.profile_skill)

        self.profile_team = QLabel("Team: -")
        self.profile_team.setWordWrap(True)
        profile_layout.addWidget(self.profile_team)

        # RadarWidget - draws a 6-axis polygon visualisation
        from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
        from PyQt6.QtCore import QPointF

        class RadarWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.values = [50.0] * 6
                side = scaled(240)
                self.setFixedSize(side, side)

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
                # Leave room outside the outer ring for the axis labels.
                radius = min(w, h) * 0.33

                # Draw concentric rings
                pen = QPen(QColor("#555555"))
                painter.setPen(pen)
                for i in range(1, 5):
                    r = radius * (i / 5.0)
                    painter.drawEllipse(QPointF(cx, cy), r, r)

                # Draw axes and labels
                axes = 6
                import math

                labels = [
                    "Speed",
                    "Racecraft",
                    "Consistency",
                    "Reactions",
                    "Setup",
                    "Tyres",
                ]
                for i in range(axes):
                    angle = (math.pi * 2.0 * i) / axes - math.pi / 2
                    x = cx + math.cos(angle) * radius
                    y = cy + math.sin(angle) * radius
                    painter.setPen(QPen(QColor("#888888")))
                    painter.drawLine(QPointF(cx, cy), QPointF(x, y))
                    # Label
                    lx = cx + math.cos(angle) * (radius + scaled(16))
                    ly = cy + math.sin(angle) * (radius + scaled(16))
                    painter.setPen(QPen(QColor("#B9F2FF")))
                    label_w = scaled(84)
                    label_h = scaled(16)
                    painter.drawText(
                        int(lx - label_w / 2),
                        int(ly - label_h / 2),
                        label_w,
                        label_h,
                        Qt.AlignmentFlag.AlignCenter,
                        labels[i],
                    )

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
                painter.setPen(QPen(QColor("#FFB000"), 2))
                painter.drawPolygon(*points)

        self.radar = RadarWidget()
        profile_layout.addWidget(self.radar, 0, Qt.AlignmentFlag.AlignCenter)
        right_vbox.addWidget(profile_group)

        # Tuning preset selection: label, combo and description each get
        # their own row so nothing is drawn over the combo box.
        preset_group = QGroupBox("Race Tuning Preset")
        preset_group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        preset_layout = QVBoxLayout(preset_group)
        preset_layout.setSpacing(scaled(6))
        preset_label = QLabel("Choose simulation style:")
        preset_layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Balanced (Default)", "balanced")
        self.preset_combo.addItem("Aggressive (More Overtakes)", "aggressive")
        self.preset_combo.addItem("Tyre Sensitive (Strategic)", "tyre_sensitive")
        self.preset_combo.setCurrentIndex(0)
        self.preset_combo.setStyleSheet(combo_box_style())
        self.preset_combo.setMinimumHeight(scaled(36))
        self.preset_combo.setAccessibleName("Race Tuning Preset")
        preset_layout.addWidget(self.preset_combo)

        # Preset descriptions
        preset_desc = QLabel(
            "<b>Balanced:</b> Moderate dirty-air, balanced overtaking<br>"
            "<b>Aggressive:</b> More slipstream, easier overtakes, exciting racing<br>"
            "<b>Tyre Sensitive:</b> High degradation, strategic pit stops"
        )
        preset_desc.setWordWrap(True)
        preset_desc.setStyleSheet(f"font-size: {scaled(11)}px; color: #999;")
        preset_layout.addWidget(preset_desc)
        right_vbox.addWidget(preset_group)

        # Info note about controls. The leading glyph is a plain "i" badge
        # drawn with the UI font rather than an emoji the bundled font lacks.
        info_row = QHBoxLayout()
        info_row.setSpacing(scaled(8))
        info_badge = QLabel("i")
        badge_side = scaled(18)
        info_badge.setFixedSize(badge_side, badge_side)
        info_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_badge.setStyleSheet(
            f"font-size: {scaled(11)}px; font-weight: 700; font-style: italic; "
            "color: #16211F; background-color: #B9F2FF; "
            f"border-radius: {badge_side // 2}px;"
        )
        info_row.addWidget(info_badge, 0, Qt.AlignmentFlag.AlignTop)
        info_label = QLabel(
            "Race pace and overtaking controls are available during the race"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            f"font-size: {scaled(12)}px; color: #9EB4C2; font-style: italic;"
        )
        info_row.addWidget(info_label, 1)
        right_vbox.addLayout(info_row)
        right_vbox.addStretch(1)
        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(scaled(50))
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)

        start_btn = QPushButton("Start Race")
        start_btn.setMinimumHeight(scaled(50))
        start_btn.setStyleSheet(
            "font-weight: bold; background-color: #4CAF50; color: white;"
        )
        start_btn.clicked.connect(self._start_race)
        button_layout.addWidget(start_btn)

        right_vbox.addLayout(button_layout)

        # Attach the right panel into the selection container and give the
        # whole row the spare height.
        selection_container.addWidget(right_panel, 2)
        layout.addLayout(selection_container, 1)

        # Discipline, tier and track sit side by side on one row so the
        # dialog's fixed-height content stays compact at every UI scale.
        choices_row = QHBoxLayout()
        choices_row.setSpacing(scaled(16))

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

        self.discipline_combo.setStyleSheet(combo_box_style())
        self.discipline_combo.setCurrentIndex(0)
        self.discipline_combo.setAccessibleName("Racing Discipline")
        self.discipline_combo.currentIndexChanged.connect(self._on_discipline_changed)
        discipline_layout.addWidget(self.discipline_combo)
        choices_row.addWidget(discipline_group, 1)

        # Tier selection (discipline first, then tier, then driver)
        tier_group = QGroupBox("Team Tier")
        tier_layout = QVBoxLayout(tier_group)
        tier_label = QLabel("Choose Tier:")
        tier_layout.addWidget(tier_label)

        self.tier_combo = QComboBox()
        self.tier_combo.setStyleSheet(self.discipline_combo.styleSheet())
        self.tier_combo.setAccessibleName("Team Tier")
        self.tier_combo.currentIndexChanged.connect(self._on_tier_changed)
        tier_layout.addWidget(self.tier_combo)
        choices_row.addWidget(tier_group, 1)

        # Track selection (populates based on selected discipline)
        track_group = QGroupBox("Track Selection")
        track_layout = QVBoxLayout(track_group)
        track_label = QLabel("Choose Track:")
        track_layout.addWidget(track_label)

        self.track_combo = QComboBox()
        self.track_combo.setStyleSheet(combo_box_style())
        self.track_combo.setAccessibleName("Track Selection")
        self.track_combo.currentIndexChanged.connect(self._update_setup_summary)
        track_layout.addWidget(self.track_combo)
        choices_row.addWidget(track_group, 2)
        layout.addLayout(choices_row)

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
        self._update_setup_summary()

    def _start_race(self):
        """Start race with current settings."""
        # Get selected driver
        current_item = self.driver_list.currentItem()
        if not current_item:
            warning(self, "No Driver", "Please select a driver.")
            return

        self.selected_driver = current_item.data(Qt.ItemDataRole.UserRole)

        # Get selected tuning preset
        selected_preset = self.preset_combo.currentData()

        # Get selected discipline and tier
        selected_discipline = self.discipline_combo.currentData()
        selected_tier = (
            self.tier_combo.currentData() if hasattr(self, "tier_combo") else DEFAULT_TIER
        )

        # Enforce valid driver-team contract for the chosen discipline.
        selected_team = self._resolve_driver_team(self.selected_driver)
        if selected_team is None:
            warning(
                self,
                "No Team Contract",
                "Selected driver is not contracted to a team and cannot start a race.",
            )
            return

        team_disc = self._normalize_discipline(getattr(selected_team, "discipline", ""))
        wanted_disc = self._normalize_discipline(selected_discipline)
        if team_disc != wanted_disc:
            warning(
                self,
                "Discipline Mismatch",
                "Selected driver's contracted team is not in the chosen discipline.",
            )
            return

        team_tier = self._normalize_tier(getattr(selected_team, "tier", ""))
        wanted_tier = self._normalize_tier(selected_tier)
        if wanted_tier and team_tier != wanted_tier:
            warning(
                self,
                "Tier Mismatch",
                "Selected driver's contracted team is not in the chosen tier.",
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
            "tier": self._canonical_tier(selected_tier),
        }

        driver_name = get_display_name(self.selected_driver)
        print(
            f"[INFO] Starting race with driver: {driver_name}, discipline: {selected_discipline}"
        )

        self.race_start.emit(config)
        self.accept()  # Close dialog with accept status

    def _on_discipline_changed(self):
        """Handle discipline selection change."""
        self._update_tiers_for_selected_discipline()
        self._update_tracks_for_discipline()
        self._refresh_driver_list_for_selected_discipline()
        self._update_setup_summary()

    def _on_tier_changed(self):
        """Handle tier selection change."""
        self._refresh_driver_list_for_selected_discipline()
        self._update_setup_summary()

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
                    (norm_disc,),
                ).fetchall()
                found_tiers = [self._canonical_tier(r[0]) for r in rows if r and r[0]]

        if not found_tiers:
            found_tiers = list(TIERS)

        self.tier_combo.blockSignals(True)
        self.tier_combo.clear()
        for tier in found_tiers:
            self.tier_combo.addItem(tier_label(tier), tier)

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
        return normalise_tier(value)

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

    def _get_contracted_drivers_for_discipline(
        self, discipline: str, tier: Optional[str] = None
    ) -> List[object]:
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
                (wanted.lower(), wanted_tier, int(QUICK_RACE_LIST_SIZE)),
            ).fetchall()

        selected: List[object] = []
        for row in rows:
            driver = self.db.get_driver(int(row[0]))
            if driver is not None:
                selected.append(driver)
        return selected

    def _ensure_contracted_pool_for_discipline(
        self, discipline: str, tier: Optional[str] = None
    ):
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
                (wanted.lower(), wanted_tier),
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
                (wanted.lower(), wanted_tier),
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
                (wanted.lower(), needed),
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
                    (needed - len(driver_ids),),
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
                    (team_id, driver_id),
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
        selected_tier = (
            self.tier_combo.currentData() if hasattr(self, "tier_combo") else DEFAULT_TIER
        )
        contracted = self._get_contracted_drivers_for_discipline(
            selected_discipline, selected_tier
        )
        if not contracted:
            self.driver_list.clear()
            self.selected_driver = None
            self.selected_team = None
            self.profile_name.setText("Name: No contracted drivers available")
            self.profile_nationality.setText("Nationality: -")
            self.profile_skill.setText("Skill: -")
            self.profile_team.setText("Team: -")
            self._update_setup_summary()
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
        self._update_setup_summary()

    def _update_tracks_for_discipline(self):
        """Populate track list based on selected discipline."""
        self.track_combo.clear()

        selected_discipline = self.discipline_combo.currentData()

        try:
            db = self.parent_window.db if hasattr(self.parent_window, "db") else None
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
                self.track_combo.addItem("Fallback Circuit", None)
            else:
                for track in tracks:
                    # Store track id as user data
                    track_name = getattr(track, "name", f"Track {track.id}")
                    self.track_combo.addItem(track_name, track.id)
        except Exception as e:
            print(f"[WARNING] Error loading tracks: {e}")
            self.track_combo.addItem("Fallback Circuit", None)

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
        self._update_setup_summary()

    def _update_setup_summary(self):
        """Render a concise setup summary so players can confirm key selections quickly."""
        discipline = (
            self.discipline_combo.currentText()
            if hasattr(self, "discipline_combo")
            else "-"
        )
        tier = self.tier_combo.currentText() if hasattr(self, "tier_combo") else "-"
        track = self.track_combo.currentText() if hasattr(self, "track_combo") else "-"

        current_item = (
            self.driver_list.currentItem() if hasattr(self, "driver_list") else None
        )
        driver_name = "No driver"
        team_name = "No team"
        if current_item is not None:
            driver = current_item.data(Qt.ItemDataRole.UserRole)
            if driver is not None:
                driver_name = get_display_name(driver)
                team = self._resolve_driver_team(driver)
                if team is not None:
                    team_name = getattr(team, "name", UNKNOWN_TEAM)

        ready = current_item is not None and self.track_combo.count() > 0
        state = "READY TO START" if ready else "SETUP INCOMPLETE"
        self.selection_summary.setText(
            f"{state} | Discipline: {discipline} | Tier: {tier} | Track: {track} | "
            f"Driver: {driver_name} | Team: {team_name}"
        )

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
        team_name = getattr(team, "name", UNKNOWN_TEAM)
        team_tier = getattr(team, "tier", "N/A")
        self.profile_team.setText(f"Team: {team_name} ({team_tier})")

    def _update_radar_widget_safe(self, driver) -> None:
        """Refresh radar polygon values if helper is available."""
        try:
            from momentum.services.driver_attributes import get_driver_radar_values

            self.radar.set_values(get_driver_radar_values(driver))
        except Exception:
            pass

    def _apply_card_style_safe(
        self, widget, attr_name: str, fallback_style: str = ""
    ) -> None:
        """Apply a style stored on a card widget; no-op on failures."""
        if widget is None or not hasattr(widget, "setStyleSheet"):
            return
        try:
            style = getattr(widget, attr_name, None)
            widget.setStyleSheet(style if style else fallback_style)
        except Exception:
            pass

    def _update_driver_card_selection_style(self, current, previous) -> None:
        """Update visual selection styles for previous and current card widgets."""
        try:
            prev_widget = (
                self.driver_list.itemWidget(previous) if previous is not None else None
            )
            cur_widget = self.driver_list.itemWidget(current)
            self._apply_card_style_safe(prev_widget, "_base_style", "")
            self._apply_card_style_safe(cur_widget, "_selected_style")
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
