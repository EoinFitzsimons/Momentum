"""
Championship Mode GUI for Momentum Racing Simulator.

Provides:
- Championship selection/creation
- Season progression
- Standings view
- Race-by-race progression
- Integration with championship management API
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox, QGroupBox,
    QDialog, QLineEdit, QSpinBox, QTextEdit, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, List, Dict, Any
from database.database_manager import DatabaseManager
from services.championship_service import ChampionshipService, POINTS_SYSTEMS
from database.models import Championship
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
        
        create_btn = QPushButton("Create New Championship")
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
    
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.championship_service = ChampionshipService(db)
        
        self.setWindowTitle("Create New Championship")
        self.setMinimumSize(600, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup creation dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Create New Championship")
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
                track_ids = [t["id"] for t in tracks[:self.season_spin.value()]]
            
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
    """Main championship mode window."""
    
    return_to_menu = pyqtSignal()
    start_race_signal = pyqtSignal(dict)
    
    def __init__(self, championship: Championship, parent=None):
        super().__init__(parent)
        self.championship = championship
        self.db = DatabaseManager()
        self.championship_service = ChampionshipService(self.db)
        
        self.setWindowTitle(f"Championship: {championship.name}")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup championship window UI."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel(self.championship.name)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #B9F2FF;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        season_label = QLabel(f"Season {self.championship.current_season}")
        season_label.setStyleSheet("font-size: 18px; color: #DD2D4A; font-weight: bold;")
        header_layout.addWidget(season_label)
        
        layout.addLayout(header_layout)
        
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
        schedule_layout.addWidget(self.schedule_table)
        
        right_layout.addWidget(schedule_group)
        
        # Action buttons
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.next_race_btn = QPushButton("Start Next Race")
        self.next_race_btn.setMinimumHeight(50)
        self.next_race_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #B9F2FF;
                color: #353839;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #DD2D4A; color: white; }
            QPushButton:disabled { background-color: #555; color: #999; }
        """)
        self.next_race_btn.clicked.connect(self.start_next_race)
        actions_layout.addWidget(self.next_race_btn)
        
        refresh_btn = QPushButton("Refresh Standings")
        refresh_btn.setStyleSheet("QPushButton { padding: 8px; }")
        refresh_btn.clicked.connect(self.load_data)
        actions_layout.addWidget(refresh_btn)
        
        back_btn = QPushButton("Return to Menu")
        back_btn.setStyleSheet("QPushButton { padding: 8px; }")
        back_btn.clicked.connect(self.return_to_menu.emit)
        actions_layout.addWidget(back_btn)
        
        right_layout.addWidget(actions_group)
        
        content_layout.addLayout(right_layout, 2)
        
        layout.addLayout(content_layout)
    
    def load_data(self):
        """Load championship data."""
        # Load standings
        standings = self.championship_service.recalculate_standings(
            self.championship.id,
            self.championship.current_season
        )
        
        self.standings_table.setRowCount(len(standings))
        for i, entry in enumerate(standings):
            self.standings_table.setItem(i, 0, QTableWidgetItem(str(entry.position)))
            self.standings_table.setItem(i, 1, QTableWidgetItem(entry.driver_name))
            self.standings_table.setItem(i, 2, QTableWidgetItem(entry.team_name))
            self.standings_table.setItem(i, 3, QTableWidgetItem(str(entry.total_points)))
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
        
        for i, race in enumerate(calendar):
            self.schedule_table.setItem(i, 0, QTableWidgetItem(f"R{race['round_number']}"))
            self.schedule_table.setItem(i, 1, QTableWidgetItem(race['track_name']))
            self.schedule_table.setItem(i, 2, QTableWidgetItem(race['race_date']))
            self.schedule_table.setItem(i, 3, QTableWidgetItem(race['status'].upper()))
            
            # Store race data
            self.schedule_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, race)
            
            # Find next scheduled race
            if race['status'] == 'scheduled' and self.next_race_id is None:
                self.next_race_id = race['race_id']
                # Highlight next race
                for col in range(4):
                    item = self.schedule_table.item(i, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.darkGreen)
        
        # Enable/disable next race button
        self.next_race_btn.setEnabled(self.next_race_id is not None)
        if self.next_race_id is None:
            self.next_race_btn.setText("Season Complete")
    
    def start_next_race(self):
        """Start the next scheduled race."""
        if not self.next_race_id:
            return
        
        # Get race details
        race = self.db.get_race(self.next_race_id)
        if not race:
            QMessageBox.warning(self, "Error", "Could not load race details.")
            return
        
        # Get track
        track = self.db.get_track(race.track_id)
        
        # For now, use a default driver - in full implementation, player would select their driver
        drivers = self.db.get_all_drivers()
        if not drivers:
            QMessageBox.warning(self, "No Drivers", "No drivers available in database.")
            return
        
        # Emit race start signal with race config
        config = {
            "mode": "championship",
            "championship_id": self.championship.id,
            "race_id": self.next_race_id,
            "track_id": race.track_id,
            "driver": drivers[0],  # Default driver
            "discipline": self.championship.discipline
        }
        
        self.start_race_signal.emit(config)


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
