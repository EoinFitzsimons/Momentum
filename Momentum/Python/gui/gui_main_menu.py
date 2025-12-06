"""
Main Menu GUI for Momentum Racing Simulator.

Provides:
- Race Mode selection
- Driver selection
- Race controls (pace, overtake aggressiveness)
- Options (display settings: windowed, borderless windowed, fullscreen)
"""

import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QSlider, QGroupBox, QRadioButton,
    QButtonGroup, QMessageBox, QListWidget, QListWidgetItem, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent

from database.database_manager import DatabaseManager


class MainMenuWindow(QMainWindow):
    """Main menu for Momentum Racing Simulator."""
    
    # Signals
    start_race_signal = pyqtSignal(dict)  # Emits race configuration
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Momentum - Main Menu")
        self.setMinimumSize(1000, 700)
        
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
            QListWidget::item:selected { background-color: #FFB000; color: #1A1A1A; font-weight: 700; }

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
        self.display_button_group.buttonClicked.connect(self._on_display_mode_changed)
        
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
        setup_window = QuickRaceSetupWindow(self, self.drivers, self.display_mode)
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
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
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
        
        # Driver selection
        driver_group = QGroupBox("Select Your Driver")
        driver_layout = QVBoxLayout(driver_group)
        
        self.driver_list = QListWidget()
        self.driver_list.setMinimumHeight(200)
        self.driver_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: #FFD700;
                color: #353839;
                font-weight: bold;
            }
        """)
        
        # Populate driver list
        for driver in self.drivers[:20]:  # Show first 20 drivers
            name = driver.name  # Use the name field directly
            skill = int(driver.raw_speed)  # Use raw_speed as overall skill indicator
            item = QListWidgetItem(f"{name} (Skill: {skill})")
            item.setData(Qt.ItemDataRole.UserRole, driver)
            self.driver_list.addItem(item)
        
        self.driver_list.setCurrentRow(0)  # Select first driver by default
        driver_layout.addWidget(self.driver_list)
        
        layout.addWidget(driver_group)
        
        # Tuning preset selection
        preset_group = QGroupBox("Race Tuning Preset")
        preset_layout = QVBoxLayout(preset_group)
        
        preset_label = QLabel("Choose simulation style:")
        preset_layout.addWidget(preset_label)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Balanced (Default)", "balanced")
        self.preset_combo.addItem("Aggressive (More Overtakes)", "aggressive")
        self.preset_combo.addItem("Tyre Sensitive (Strategic)", "tyre_sensitive")
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
        
        layout.addWidget(preset_group)
        
        # Info note about controls
        info_label = QLabel("💡 Race pace and overtaking controls are available during the race")
        info_label.setStyleSheet("font-size: 12px; color: #888; font-style: italic;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        start_btn = QPushButton("Start Race")
        start_btn.setMinimumHeight(50)
        start_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white;")
        start_btn.clicked.connect(self._start_race)
        button_layout.addWidget(start_btn)
        
        layout.addLayout(button_layout)
    
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
        
        driver_name = getattr(self.selected_driver, 'name', 
                            f"{getattr(self.selected_driver, 'first_name', 'Unknown')} {getattr(self.selected_driver, 'last_name', 'Driver')}")
        print(f"[INFO] Starting race with driver: {driver_name}")
        
        self.race_start.emit(config)
        self.accept()  # Close dialog with accept status


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
