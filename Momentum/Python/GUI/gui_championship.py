"""
Championship Mode GUI for Momentum Racing Simulator.

Provides:
- Championship selection/creation
- Season progression with proper race transitions
- Standings view with auto-refresh
- Pre-race setup (driver/team selection, weather, tire strategies)
- Post-race results integration
- Race lifecycle management (scheduled → in-progress → completed)
- Notifications and status updates
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox, QGroupBox,
    QDialog, QLineEdit, QSpinBox, QTextEdit, QMessageBox, QHeaderView,
    QProgressBar, QListWidget, QListWidgetItem, QScrollArea, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import QTimer
from typing import Optional, List, Dict, Any, Tuple
from database.database_manager import DatabaseManager
from services.championship_service import ChampionshipService, POINTS_SYSTEMS
from database.models import Championship, Race
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('championship_mode.log')
    ]
)
logger = logging.getLogger(__name__)


# Color scheme
COLORS = {
    "primary": "#B9F2FF",
    "accent": "#DD2D4A",
    "dark": "#353839",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db"
}


class ChampionshipSelectionDialog(QDialog):
    """Dialog for selecting or creating a championship."""
    
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.championship_service = ChampionshipService(db)
        self.selected_championship = None
        
        self.setWindowTitle("Select Championship")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        self.load_championships()
    
    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        
        # Button text constant
        CREATE_CHAMPIONSHIP_TEXT = "Create New Championship"
        
        # Title
        title = QLabel("Championship Selection")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #B9F2FF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Championships list
        list_group = QGroupBox("Available Championships")
        list_layout = QVBoxLayout(list_group)
        
        self.championships_table = QTableWidget()
        self.championships_table.setColumnCount(5)
        self.championships_table.setHorizontalHeaderLabels([
            "Name", "Discipline", "Season", "Races", "Status"
        ])
        self.championships_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.championships_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.championships_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.championships_table.doubleClicked.connect(self.accept)
        list_layout.addWidget(self.championships_table)
        
        layout.addWidget(list_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        create_btn = QPushButton(CREATE_CHAMPIONSHIP_TEXT)
        create_btn.clicked.connect(self.create_championship)
        create_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #B9F2FF; color: #353839; font-weight: bold; }")
        buttons_layout.addWidget(create_btn)
        
        select_btn = QPushButton("Select Championship")
        select_btn.clicked.connect(self.select_championship)
        select_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #DD2D4A; color: white; font-weight: bold; }")
        buttons_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("QPushButton { padding: 10px; }")
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_championships(self):
        """Load available championships."""
        championships = self.db.get_all_championships()
        
        self.championships_table.setRowCount(len(championships))
        
        for i, champ in enumerate(championships):
            # Get race count
            calendar = self.championship_service.get_championship_calendar(champ.id, champ.current_season)
            
            self.championships_table.setItem(i, 0, QTableWidgetItem(champ.name))
            self.championships_table.setItem(i, 1, QTableWidgetItem(champ.discipline))
            self.championships_table.setItem(i, 2, QTableWidgetItem(str(champ.current_season)))
            self.championships_table.setItem(i, 3, QTableWidgetItem(f"{len(calendar)} races"))
            
            status = "Archived" if champ.archived else "Active"
            self.championships_table.setItem(i, 4, QTableWidgetItem(status))
            
            # Store championship object in row
            self.championships_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, champ)
    
    def select_championship(self):
        """Select the highlighted championship."""
        selected_rows = self.championships_table.selectedItems()
        if selected_rows:
            row = self.championships_table.currentRow()
            item = self.championships_table.item(row, 0)
            self.selected_championship = item.data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a championship.")
    
    def create_championship(self):
        """Show dialog to create new championship."""
        dialog = CreateChampionshipDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_championships()


class CreateChampionshipDialog(QDialog):
    """Dialog for creating a new championship."""
    
    CREATE_CHAMPIONSHIP_TITLE = "Create New Championship"
    
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.championship_service = ChampionshipService(db)
        
        self.setWindowTitle(self.CREATE_CHAMPIONSHIP_TITLE)
        self.setMinimumSize(600, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup creation dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.CREATE_CHAMPIONSHIP_TITLE)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #B9F2FF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Championship details
        details_group = QGroupBox("Championship Details")
        details_layout = QVBoxLayout(details_group)
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., 2025 Formula Championship")
        name_layout.addWidget(self.name_input)
        details_layout.addLayout(name_layout)
        
        # Discipline
        discipline_layout = QHBoxLayout()
        discipline_layout.addWidget(QLabel("Discipline:"))
        self.discipline_combo = QComboBox()
        self.discipline_combo.addItems([
            "SINGLE_SEATER",
            "RALLY_STAGE",
            "ENDURANCE",
            "PRODUCTION_TOURING",
            "URBAN_STREET",
            "DRAG_ACCELERATION",
            "SPRINT_RALLYCROSS"
        ])
        discipline_layout.addWidget(self.discipline_combo)
        details_layout.addLayout(discipline_layout)
        
        # Season length
        season_layout = QHBoxLayout()
        season_layout.addWidget(QLabel("Season Length:"))
        self.season_spin = QSpinBox()
        self.season_spin.setMinimum(1)
        self.season_spin.setMaximum(50)
        self.season_spin.setValue(20)
        self.season_spin.setSuffix(" races")
        season_layout.addWidget(self.season_spin)
        details_layout.addLayout(season_layout)
        
        # Tier
        tier_layout = QHBoxLayout()
        tier_layout.addWidget(QLabel("Tier:"))
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["TOP_TIER", "TIER_2", "TIER_3"])
        tier_layout.addWidget(self.tier_combo)
        details_layout.addLayout(tier_layout)
        
        # Description
        details_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Optional championship description...")
        details_layout.addWidget(self.description_input)
        
        layout.addWidget(details_group)
        
        # Track selection
        tracks_group = QGroupBox("Track Selection")
        tracks_layout = QVBoxLayout(tracks_group)
        
        tracks_layout.addWidget(QLabel("Tracks will be auto-generated based on discipline"))
        tracks_layout.addWidget(QLabel("(Manual track selection coming soon)"))
        
        layout.addWidget(tracks_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Championship")
        create_btn.clicked.connect(self.create_championship)
        create_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #B9F2FF; color: #353839; font-weight: bold; }")
        buttons_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("QPushButton { padding: 10px; }")
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_championship(self):
        """Create the championship."""
        name = self.name_input.text().strip()
        if not name:
            logger.warning("Championship creation attempted with empty name")
            QMessageBox.warning(self, "Invalid Name", "Please enter a championship name.")
            return
        
        try:
            logger.info(f"Creating championship: '{name}'")
            logger.info(f"  Discipline: {self.discipline_combo.currentText()}")
            logger.info(f"  Season Length: {self.season_spin.value()} races")
            logger.info(f"  Tier: {self.tier_combo.currentText()}")
            
            # Create championship object
            championship = Championship(
                id=0,
                name=name,
                discipline=self.discipline_combo.currentText(),
                season_length=self.season_spin.value(),
                points_system="standard",
                current_season=1,
                tier=self.tier_combo.currentText(),
                founded_year=datetime.now().year,
                description=self.description_input.toPlainText()
            )
            logger.info("Championship object created successfully")
            
            # Get tracks for discipline (simplified - use first N tracks)
            logger.info(f"Fetching tracks for discipline: {championship.discipline}")
            tracks = self.db.get_circuits_by_discipline(championship.discipline)
            logger.info(f"Found {len(tracks)} tracks for {championship.discipline}")
            
            if not tracks or len(tracks) < self.season_spin.value():
                logger.warning(f"Insufficient discipline-specific tracks ({len(tracks)} available, {self.season_spin.value()} needed)")
                logger.info("Falling back to all available tracks in database")
                # If not enough tracks, try to get any tracks
                all_tracks = self.db.get_all_tracks()
                logger.info(f"Total tracks available: {len(all_tracks)}")
                track_ids = [t.id for t in all_tracks[:self.season_spin.value()]]
            else:
                logger.info(f"Using {self.season_spin.value()} discipline-specific tracks")
                track_ids = [t.id for t in tracks[:self.season_spin.value()]]
            
            if not track_ids:
                logger.error("No tracks available in database - cannot create championship")
                QMessageBox.critical(self, "No Tracks", "No tracks available in database. Please add tracks first.")
                return
            
            logger.info(f"Selected {len(track_ids)} tracks for championship calendar: {track_ids}")
            
            # Create championship with calendar
            logger.info("Creating championship season with race calendar...")
            champ_id, race_ids = self.championship_service.create_championship_season(
                championship,
                track_ids,
                datetime.now()
            )
            
            logger.info(f"Championship created successfully!")
            logger.info(f"  Championship ID: {champ_id}")
            logger.info(f"  Number of races: {len(race_ids)}")
            logger.info(f"  Race IDs: {race_ids}")
            
            QMessageBox.information(
                self,
                "Success",
                f"Championship '{name}' created successfully with {len(race_ids)} races!"
            )
            
            self.accept()
            
        except ValueError as e:
            logger.error(f"Validation error while creating championship: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Validation Error",
                f"Invalid input:\n{str(e)}\n\nPlease check your inputs and try again."
            )
        except AttributeError as e:
            logger.error(f"Attribute error (likely database schema mismatch): {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Database Error",
                f"Database structure error:\n{str(e)}\n\nThe database may need to be regenerated. Check the log file for details."
            )
        except Exception as e:
            logger.error(f"Unexpected error creating championship: {type(e).__name__}: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create championship:\n\n{type(e).__name__}: {str(e)}\n\nCheck championship_mode.log for detailed error information."
            )


class ChampionshipWindow(QMainWindow):
    """Main championship mode window with real-time standings updates."""
    
    return_to_menu = pyqtSignal()
    start_race_signal = pyqtSignal(dict)
    
    def __init__(self, championship: Championship, parent=None):
        super().__init__(parent)
        self.championship = championship
        self.db = DatabaseManager()
        self.championship_service = ChampionshipService(self.db)
        self.next_race_id = None
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        self.setWindowTitle(f"Championship: {championship.name}")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup championship window UI with enhanced styling."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Header with more info
        header_layout = QHBoxLayout()
        
        title = QLabel(self.championship.name)
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['primary']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Status info
        status_layout = QVBoxLayout()
        season_label = QLabel(f"Season {self.championship.current_season}")
        season_label.setStyleSheet(f"font-size: 14px; color: {COLORS['accent']}; font-weight: bold;")
        status_layout.addWidget(season_label)
        
        discipline_label = QLabel(f"Discipline: {self.championship.discipline}")
        discipline_label.setStyleSheet(f"font-size: 12px; color: #999;")
        status_layout.addWidget(discipline_label)
        
        header_layout.addLayout(status_layout)
        
        layout.addLayout(header_layout)
        
        # Notification area
        self.notification_label = QLabel()
        self.notification_label.setStyleSheet(f"color: {COLORS['info']}; padding: 8px; background-color: rgba(52, 152, 219, 0.1); border-radius: 4px;")
        self.notification_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notification_label.hide()
        layout.addWidget(self.notification_label)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left: Standings
        standings_group = QGroupBox("Championship Standings")
        standings_layout = QVBoxLayout(standings_group)
        
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(7)
        self.standings_table.setHorizontalHeaderLabels([
            "Pos", "Driver", "Team", "Points", "Wins", "Podiums", "Races"
        ])
        self.standings_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.standings_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.standings_table.setAlternatingRowColors(True)
        self.standings_table.setStyleSheet("""
            QTableWidget { alternate-background-color: rgba(185, 242, 255, 0.05); }
            QHeaderView::section { background-color: #353839; color: #B9F2FF; padding: 5px; }
        """)
        standings_layout.addWidget(self.standings_table)
        
        content_layout.addWidget(standings_group, 3)
        
        # Right: Schedule and actions
        right_layout = QVBoxLayout()
        
        schedule_group = QGroupBox("Race Schedule")
        schedule_layout = QVBoxLayout(schedule_group)
        
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels([
            "Round", "Track", "Date", "Status"
        ])
        self.schedule_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.schedule_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.schedule_table.setStyleSheet("""
            QTableWidget { alternate-background-color: rgba(185, 242, 255, 0.05); }
            QHeaderView::section { background-color: #353839; color: #B9F2FF; padding: 5px; }
        """)
        schedule_layout.addWidget(self.schedule_table)
        
        right_layout.addWidget(schedule_group)
        
        # Action buttons
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.next_race_btn = QPushButton("Start Next Race")
        self.next_race_btn.setMinimumHeight(50)
        self.next_race_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                background-color: {COLORS['success']};
                color: white;
                border-radius: 8px;
                padding: 10px;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent']}; }}
            QPushButton:disabled {{ background-color: #555; color: #999; }}
        """)
        self.next_race_btn.clicked.connect(self.start_next_race)
        actions_layout.addWidget(self.next_race_btn)
        
        refresh_btn = QPushButton("Refresh Standings")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px;
                background-color: #555;
                color: white;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: {COLORS['info']}; }}
        """)
        refresh_btn.clicked.connect(self.load_data)
        actions_layout.addWidget(refresh_btn)
        
        back_btn = QPushButton("Return to Menu")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px;
                background-color: #555;
                color: white;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: {COLORS['danger']}; }}
        """)
        back_btn.clicked.connect(self.on_return_to_menu)
        actions_layout.addWidget(back_btn)
        
        right_layout.addWidget(actions_group)
        
        content_layout.addLayout(right_layout, 2)
        
        layout.addLayout(content_layout)
    
    def load_data(self):
        """Load championship data with standings and schedule."""
        try:
            # Load standings
            standings = self.championship_service.recalculate_standings(
                self.championship.id,
                self.championship.current_season
            )
            
            self.standings_table.setRowCount(len(standings))
            for i, entry in enumerate(standings):
                # Position
                pos_item = QTableWidgetItem(str(entry.position))
                pos_item.setForeground(QColor(COLORS['accent']))
                pos_item.setFont(QFont(pos_item.font().family(), pos_item.font().pointSize(), QFont.Weight.Bold))
                self.standings_table.setItem(i, 0, pos_item)
                
                self.standings_table.setItem(i, 1, QTableWidgetItem(entry.driver_name))
                self.standings_table.setItem(i, 2, QTableWidgetItem(entry.team_name))
                
                # Points (color by leader)
                points_item = QTableWidgetItem(str(entry.total_points))
                if i == 0:
                    points_item.setForeground(QColor(COLORS['success']))
                    points_item.setFont(QFont(points_item.font().family(), points_item.font().pointSize(), QFont.Weight.Bold))
                self.standings_table.setItem(i, 3, points_item)
                
                self.standings_table.setItem(i, 4, QTableWidgetItem(str(entry.wins)))
                self.standings_table.setItem(i, 5, QTableWidgetItem(str(entry.podiums)))
                self.standings_table.setItem(i, 6, QTableWidgetItem(str(entry.races_started)))
            
            # Load schedule
            calendar = self.championship_service.get_championship_calendar(
                self.championship.id,
                self.championship.current_season
            )
            
            self.schedule_table.setRowCount(len(calendar))
            self.next_race_id = None
            races_completed = 0
            
            for i, race in enumerate(calendar):
                self.schedule_table.setItem(i, 0, QTableWidgetItem(f"R{race['round_number']}"))
                self.schedule_table.setItem(i, 1, QTableWidgetItem(race['track_name']))
                self.schedule_table.setItem(i, 2, QTableWidgetItem(race['race_date']))
                
                # Status with color coding
                status_item = QTableWidgetItem(race['status'].upper())
                if race['status'] == 'scheduled':
                    status_item.setForeground(QColor(COLORS['info']))
                elif race['status'] == 'in-progress':
                    status_item.setForeground(QColor(COLORS['warning']))
                    status_item.setFont(QFont(status_item.font().family(), status_item.font().pointSize(), QFont.Weight.Bold))
                elif race['status'] == 'completed':
                    status_item.setForeground(QColor(COLORS['success']))
                    races_completed += 1
                
                self.schedule_table.setItem(i, 3, status_item)
                
                # Store race data
                self.schedule_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, race)
                
                # Find next scheduled race
                if race['status'] == 'scheduled' and self.next_race_id is None:
                    self.next_race_id = race['race_id']
                    # Highlight next race
                    for col in range(4):
                        item = self.schedule_table.item(i, col)
                        if item:
                            item.setBackground(QColor(COLORS['success']).darker(300))
            
            # Update button state and show progress
            if self.next_race_id is not None:
                self.next_race_btn.setEnabled(True)
                self.next_race_btn.setText("Start Next Race")
                progress = f"{races_completed}/{len(calendar)} races completed"
                self.show_notification(f"Season in progress: {progress}", "info")
            else:
                self.next_race_btn.setEnabled(False)
                self.next_race_btn.setText("Season Complete")
                self.show_notification("Championship season complete!", "success")
        
        except Exception as e:
            logger.error(f"Error loading championship data: {str(e)}", exc_info=True)
            self.show_notification(f"Error loading data: {str(e)}", "danger")
    
    def auto_refresh(self):
        """Auto-refresh data periodically (every 5 seconds)."""
        try:
            # Only refresh schedule (lightweight operation)
            calendar = self.championship_service.get_championship_calendar(
                self.championship.id,
                self.championship.current_season
            )
            
            # Check for status changes and update next race if needed
            for i, race in enumerate(calendar):
                current_status = self.schedule_table.item(i, 3).text().lower()
                
                if race['status'] != current_status:
                    # Status changed, reload all data
                    self.load_data()
                    break
        
        except Exception as e:
            logger.debug(f"Auto-refresh error (non-critical): {str(e)}")
    
    def show_notification(self, message: str, level: str = "info"):
        """Show a temporary notification."""
        colors = {
            "info": COLORS['info'],
            "success": COLORS['success'],
            "warning": COLORS['warning'],
            "danger": COLORS['danger']
        }
        
        self.notification_label.setText(message)
        self.notification_label.setStyleSheet(
            f"color: {colors.get(level, COLORS['info'])}; "
            f"padding: 8px; "
            f"background-color: rgba(52, 152, 219, 0.1); "
            f"border-radius: 4px;"
        )
        self.notification_label.show()
    
    def on_return_to_menu(self):
        """Clean up and return to menu."""
        self.refresh_timer.stop()
        self.return_to_menu.emit()
    
    def closeEvent(self, event):
        """Handle window close."""
        self.refresh_timer.stop()
        super().closeEvent(event)
    
    def start_next_race(self):
        """Start the next scheduled race with pre-race setup."""
        if not self.next_race_id:
            return
        
        # Get race details
        race = self.db.get_race(self.next_race_id)
        if not race:
            QMessageBox.warning(self, "Error", "Could not load race details.")
            return
        
        # Get track
        track = self.db.get_track(race.track_id)
        
        # Show pre-race setup dialog
        setup_dialog = PreRaceSetupDialog(
            self.db,
            self.championship,
            race,
            track,
            parent=self
        )
        
        if setup_dialog.exec() == QDialog.DialogCode.Accepted:
            # Get selected configuration
            config = setup_dialog.get_race_config()
            
            # Update race status to in-progress
            try:
                success, error_msg = self.championship_service.update_race_lifecycle_status(
                    self.next_race_id,
                    "in-progress"
                )
                
                if not success:
                    QMessageBox.warning(
                        self,
                        "Status Update Failed",
                        f"Could not update race status: {error_msg}"
                    )
                    return
                
                logger.info(f"Race {self.next_race_id} status updated to in-progress")
                
                # Emit race start signal with race config
                self.start_race_signal.emit(config)
                
            except Exception as e:
                logger.error(f"Error updating race status: {str(e)}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update race status: {str(e)}"
                )


class PreRaceSetupDialog(QDialog):
    """Dialog for pre-race setup: driver selection, weather, tire strategy."""
    
    def __init__(
        self,
        db: DatabaseManager,
        championship: Championship,
        race: Race,
        track,
        parent=None
    ):
        super().__init__(parent)
        self.db = db
        self.championship = championship
        self.race = race
        self.track = track
        self.selected_driver = None
        self.selected_team = None
        self.race_config = {}
        
        self.setWindowTitle(f"Pre-Race Setup - {track.name if track else 'Race'}")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup pre-race setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with track info
        header_layout = QHBoxLayout()
        
        track_info = QLabel()
        track_info.setText(f"<b>{self.track.name if self.track else 'Unknown'}</b> - {self.track.country if self.track else ''}")
        track_info.setStyleSheet(f"color: {COLORS['primary']}; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(track_info)
        
        header_layout.addStretch()
        
        round_info = QLabel(f"Round {self.race.round_number}")
        round_info.setStyleSheet(f"color: {COLORS['accent']}; font-size: 14px;")
        header_layout.addWidget(round_info)
        
        layout.addLayout(header_layout)
        
        # Main content - two columns
        content_layout = QHBoxLayout()
        
        # Left: Driver and Team Selection
        left_layout = QVBoxLayout()
        
        # Driver Selection
        driver_group = QGroupBox("Driver Selection")
        driver_layout = QVBoxLayout(driver_group)
        
        driver_layout.addWidget(QLabel("Select your driver:"))
        self.driver_combo = QComboBox()
        
        # Populate drivers
        drivers = self.db.get_all_drivers()
        if drivers:
            for driver in drivers:
                self.driver_combo.addItem(driver.name, driver)
                self.selected_driver = drivers[0]
        
        self.driver_combo.currentIndexChanged.connect(self.on_driver_selected)
        driver_layout.addWidget(self.driver_combo)
        
        # Driver stats
        self.driver_stats = QLabel()
        self.driver_stats.setStyleSheet("color: #999;")
        driver_layout.addWidget(self.driver_stats)
        driver_layout.addStretch()
        
        left_layout.addWidget(driver_group)
        
        # Team Selection
        team_group = QGroupBox("Team")
        team_layout = QVBoxLayout(team_group)
        
        team_layout.addWidget(QLabel("Select team:"))
        self.team_combo = QComboBox()
        
        # Populate teams
        teams = self.db.get_teams_by_discipline(self.championship.discipline)
        if teams:
            for team in teams:
                self.team_combo.addItem(team.name, team)
                self.selected_team = teams[0]
        
        self.team_combo.currentIndexChanged.connect(self.on_team_selected)
        team_layout.addWidget(self.team_combo)
        
        # Team budget
        self.team_budget = QLabel()
        self.team_budget.setStyleSheet("color: #999;")
        team_layout.addWidget(self.team_budget)
        team_layout.addStretch()
        
        left_layout.addWidget(team_group)
        content_layout.addLayout(left_layout, 1)
        
        # Right: Race Setup
        right_layout = QVBoxLayout()
        
        # Weather Conditions
        weather_group = QGroupBox("Weather Conditions")
        weather_layout = QVBoxLayout(weather_group)
        
        weather_layout.addWidget(QLabel("Weather:"))
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(["Clear", "Cloudy", "Rainy", "Wet", "Storm"])
        weather_layout.addWidget(self.weather_combo)
        
        weather_layout.addStretch()
        right_layout.addWidget(weather_group)
        
        # Tire Strategy
        tire_group = QGroupBox("Tire Strategy")
        tire_layout = QVBoxLayout(tire_group)
        
        tire_layout.addWidget(QLabel("Starting tires:"))
        self.tire_combo = QComboBox()
        self.tire_combo.addItems(["Soft", "Medium", "Hard", "Intermediate", "Wet"])
        tire_layout.addWidget(self.tire_combo)
        
        tire_layout.addStretch()
        right_layout.addWidget(tire_group)
        
        # Race Info Summary
        info_group = QGroupBox("Race Information")
        info_layout = QVBoxLayout(info_group)
        
        info_layout.addWidget(QLabel(f"Laps: {self.race.laps}"))
        info_layout.addWidget(QLabel(f"Date: {self.race.race_date}"))
        info_layout.addWidget(QLabel(f"Surface: {self.track.surface if self.track else 'Unknown'}"))
        
        right_layout.addWidget(info_group)
        right_layout.addStretch()
        
        content_layout.addLayout(right_layout, 1)
        layout.addLayout(content_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        start_btn = QPushButton("Start Race")
        start_btn.setMinimumHeight(50)
        start_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 14px;
                font-weight: bold;
                background-color: {COLORS['success']};
                color: white;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent']}; }}
        """)
        start_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(start_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 14px;
                background-color: #555;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        # Update display
        self.on_driver_selected()
        self.on_team_selected()
    
    def on_driver_selected(self):
        """Update display when driver is selected."""
        if self.driver_combo.currentIndex() >= 0:
            self.selected_driver = self.driver_combo.currentData()
            if self.selected_driver:
                stats_text = f"Speed: {self.selected_driver.speed:.0f} | Racecraft: {self.selected_driver.racecraft:.0f} | Consistency: {self.selected_driver.consistency:.0f}"
                self.driver_stats.setText(stats_text)
    
    def on_team_selected(self):
        """Update display when team is selected."""
        if self.team_combo.currentIndex() >= 0:
            self.selected_team = self.team_combo.currentData()
            if self.selected_team:
                budget_text = f"Budget: €{self.selected_team.budget:,.0f} | Tier: {self.selected_team.tier}"
                self.team_budget.setText(budget_text)
    
    def get_race_config(self) -> Dict[str, Any]:
        """Return the configured race setup."""
        return {
            "mode": "championship",
            "championship_id": self.championship.id,
            "race_id": self.race.id,
            "track_id": self.race.track_id,
            "driver": self.selected_driver,
            "team": self.selected_team,
            "discipline": self.championship.discipline,
            "weather": self.weather_combo.currentText(),
            "tire_strategy": self.tire_combo.currentText(),
            "laps": self.race.laps
        }


class PostRaceResultsDialog(QDialog):
    """Dialog showing race results and standings update."""
    
    def __init__(
        self,
        db: DatabaseManager,
        championship_service: ChampionshipService,
        championship: Championship,
        race_id: int,
        results: List[Dict[str, Any]],
        parent=None
    ):
        super().__init__(parent)
        self.db = db
        self.championship_service = championship_service
        self.championship = championship
        self.race_id = race_id
        self.results = results
        
        self.setWindowTitle("Race Results")
        self.setMinimumSize(900, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup results display UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Race Results")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['primary']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Results table
        results_group = QGroupBox("Classification")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Pos", "Driver", "Team", "Status", "Points", "Fastest Lap", "Gap"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Populate results
        self.results_table.setRowCount(len(self.results))
        for i, result in enumerate(self.results):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(result.get('position', '-'))))
            self.results_table.setItem(i, 1, QTableWidgetItem(result.get('driver_name', 'Unknown')))
            self.results_table.setItem(i, 2, QTableWidgetItem(result.get('team_name', 'Unknown')))
            
            status = "DNF" if result.get('dnf_reason') else "Finished"
            self.results_table.setItem(i, 3, QTableWidgetItem(status))
            
            self.results_table.setItem(i, 4, QTableWidgetItem(str(result.get('points', 0))))
            
            fastest_lap = "✓" if result.get('fastest_lap') else ""
            self.results_table.setItem(i, 5, QTableWidgetItem(fastest_lap))
            
            self.results_table.setItem(i, 6, QTableWidgetItem(result.get('gap', '-')))
        
        results_layout.addWidget(self.results_table)
        layout.addWidget(results_group)
        
        # Updated standings preview
        standings_group = QGroupBox("Updated Championship Standings")
        standings_layout = QVBoxLayout(standings_group)
        
        # Get updated standings
        standings = self.championship_service.recalculate_standings(
            self.championship.id,
            self.championship.current_season
        )
        
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(6)
        self.standings_table.setHorizontalHeaderLabels([
            "Pos", "Driver", "Team", "Points", "Wins", "Races"
        ])
        self.standings_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.standings_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.standings_table.setMaximumHeight(250)
        
        self.standings_table.setRowCount(min(10, len(standings)))  # Show top 10
        for i, entry in enumerate(standings[:10]):
            self.standings_table.setItem(i, 0, QTableWidgetItem(str(entry.position)))
            self.standings_table.setItem(i, 1, QTableWidgetItem(entry.driver_name))
            self.standings_table.setItem(i, 2, QTableWidgetItem(entry.team_name))
            self.standings_table.setItem(i, 3, QTableWidgetItem(str(entry.total_points)))
            self.standings_table.setItem(i, 4, QTableWidgetItem(str(entry.wins)))
            self.standings_table.setItem(i, 5, QTableWidgetItem(str(entry.races_started)))
        
        standings_layout.addWidget(self.standings_table)
        layout.addWidget(standings_group)
        
        # Close button
        close_btn = QPushButton("Continue to Championship")
        close_btn.setMinimumHeight(50)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 14px;
                font-weight: bold;
                background-color: {COLORS['primary']};
                color: {COLORS['dark']};
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent']}; color: white; }}
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    db = DatabaseManager()
    
    # Show selection dialog
    dialog = ChampionshipSelectionDialog(db)
    if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_championship:
        window = ChampionshipWindow(dialog.selected_championship)
        window.show()
        sys.exit(app.exec())
