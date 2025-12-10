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
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MainMenuWindow(QMainWindow):
    """Main menu for Momentum Racing Simulator."""

    # Signals
    start_race_signal = pyqtSignal(dict)  # Emits race configuration

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Momentum - Main Menu")
        # Use preferred application dialog size to match the rest of the game
        pref_w, pref_h = get_preferred_window_size()
        self.setMinimumSize(pref_w, pref_h)

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
        championship_btn.setEnabled(False)  # Not implemented yet
        championship_btn.setToolTip("Coming Soon")
        layout.addWidget(championship_btn)

        # Career Mode (placeholder)
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
        career_btn.setEnabled(False)  # Not implemented yet
        career_btn.setToolTip("Coming Soon")
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
        self.drivers = drivers
        self.display_mode = display_mode
        self.selected_driver = None

        self.setWindowTitle("Quick Race Setup")
        # Use application-modal dialog with window flags so it appears as a
        # standalone dialog (not an embedded child) and can be resized.
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        # Ensure dialog has a normal window frame so it can be resized and
        # positioned independent of the (possibly frameless) main window.
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)

        # Size dialog slightly smaller than main app window for comfortable padding
        pref_w, pref_h = get_preferred_window_size()
        w = int(pref_w * 0.85)
        h = int(pref_h * 0.85)
        self.setMinimumSize(w, h)
        # Also explicitly resize so the window shows at the preferred size
        # instead of relying only on layout hints.
        try:
            self.resize(w, h)
        except Exception:
            pass

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
        driver_group.setMinimumWidth(420)
        driver_layout = QVBoxLayout(driver_group)

        self.driver_list = QListWidget()
        self.driver_list.setMinimumHeight(480)
        self.driver_list.setStyleSheet("""
            QListWidget::item:selected { background-color: transparent; color: #353839; font-weight: bold; }
        """)

        # Use SingleSelection so keyboard up/down arrows change the current
        # item; the stylesheet prevents the native selection background so
        # our DriverCard draws the visible selection instead.
        self.driver_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        # Small DriverCard widget for visual entries
        class DriverCard(QWidget):
            def __init__(self, drv, parent=None):
                super().__init__(parent)
                self.drv = drv
                h = QHBoxLayout(self)
                # Small internal padding, the card will draw its own background
                h.setContentsMargins(6, 6, 6, 6)
                h.setSpacing(8)
                # Base card appearance
                self._base_style = (
                    'background:#2E2E2E; color:#B9F2FF; border-radius:8px; padding:6px;'
                )
                self._selected_style = (
                    'background:#2E2E2E; color:#1A1A1A; border:3px solid #FFB000; border-radius:8px; padding:6px;'
                )
                self.setStyleSheet(self._base_style)

                # Use display name helper for robust name access
                display_name = get_display_name(drv)
                initials_text = (display_name[:3].upper() if display_name and display_name != 'Unknown' else '---')
                initials = QLabel(initials_text)
                initials.setFixedSize(48, 48)
                initials.setStyleSheet('background:transparent; color:#B9F2FF; border-radius:6px; font-weight:700; font-size:14px;')
                initials.setAlignment(Qt.AlignmentFlag.AlignCenter)
                h.addWidget(initials)

                v = QVBoxLayout()
                title = QLabel(display_name)
                title.setStyleSheet('font-weight:700; color:#B9F2FF; background: transparent;')
                v.addWidget(title)

                nat = get_display_nationality(drv)
                sub = QLabel(f"{nat} • Skill: {get_driver_skill_int(drv)}")
                sub.setStyleSheet('color:#999; font-size:11px; background: transparent;')
                v.addWidget(sub)

                h.addLayout(v)

        # Populate with DriverCard widgets (selection pool defined in config)
        for driver in self.drivers[:QUICK_RACE_LIST_SIZE]:
            item = QListWidgetItem()
            # Store driver object for retrieval
            item.setData(Qt.ItemDataRole.UserRole, driver)

            # Create a small visual card. We avoid setting the item's text
            # because the custom widget draws the name; setting text causes
            # duplicate name rendering in some Qt themes.
            card = DriverCard(driver)
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

            def paintEvent(self, event):
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
        self.preset_combo.setStyleSheet("""
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
        """)
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

        # Build config (pace and overtake will be controlled during race)
        config = {
            "driver": self.selected_driver,
            "display_mode": self.display_mode,
            "tuning_preset": selected_preset
        }

        driver_name = get_display_name(self.selected_driver)
        print(f"[INFO] Starting race with driver: {driver_name}")

        self.race_start.emit(config)
        self.accept()  # Close dialog with accept status

    def _on_driver_selected(self, current, previous):
        """Update the right-hand profile panel when selection changes."""
        if current is None:
            return
        driver = current.data(Qt.ItemDataRole.UserRole)
        if driver is None:
            return

        # Use service helpers for robust, canonical-driven display
        name = get_display_name(driver)
        nationality = get_display_nationality(driver)
        skill = get_driver_skill_int(driver)

        self.profile_name.setText(name)
        self.profile_nationality.setText(f"Nationality: {nationality}")
        self.profile_skill.setText(f"Skill: {skill}")

        # Update radar widget with canonical 6-axis values
        try:
            from services.driver_attributes import get_driver_radar_values
            radar_vals = get_driver_radar_values(driver)
            # radar widget expects floats 0-100
            self.radar.set_values(radar_vals)
        except Exception:
            # If radar helper missing, leave the default values
            pass

        # Update visual selection on DriverCard widgets: clear previous, set selected border
        try:
            prev_widget = None
            if previous is not None:
                prev_widget = self.driver_list.itemWidget(previous)
            cur_widget = self.driver_list.itemWidget(current)

            if prev_widget is not None and hasattr(prev_widget, 'setStyleSheet'):
                # revert to base style if available
                try:
                    base = getattr(prev_widget, '_base_style', None)
                    if base:
                        prev_widget.setStyleSheet(base)
                    else:
                        prev_widget.setStyleSheet('')
                except Exception:
                    pass

            if cur_widget is not None and hasattr(cur_widget, 'setStyleSheet'):
                try:
                    sel = getattr(cur_widget, '_selected_style', None)
                    if sel:
                        cur_widget.setStyleSheet(sel)
                except Exception:
                    pass
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

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts inside the quick race dialog.

        - Up/Down: navigate driver list (handled by list when focused)
        - Enter/Return: start the race
        - Backspace: close dialog (go back)
        - Left/Right: change preset when preset combo has focus or when list has focus
        """
        # local import removed - QKeyEvent imported at module level
        try:
            k = event.key()
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
            super().keyPressEvent(event)
        except Exception:
            try:
                super().keyPressEvent(event)
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
