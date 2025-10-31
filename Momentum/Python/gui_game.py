"""
MOMENTUM - Motorsport Management Game
Desktop GUI Application using PyQt6

A professional multi-discipline motorsport management simulation.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTableWidget, QTableWidgetItem,
    QStackedWidget, QGroupBox, QGridLayout, QProgressBar, QMessageBox,
    QComboBox, QTextEdit, QScrollArea, QFrame, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

from database.database_manager import DatabaseManager
from systems.world_state import GameWorld
from systems.race_weekend import RaceWeekendManager, RaceWeekendResults
from systems.standings_manager import StandingsManager
from systems.team_management import TeamManager
from systems.car_development import CarDevelopmentManager
from logging_system import logger, setup_exception_handler, LoggedOperation


class MomentumTheme:
    """Game color theme and styling"""
    
    # Racing-inspired color palette
    PRIMARY = "#E10600"      # Racing red
    SECONDARY = "#1A1A1A"    # Carbon black
    ACCENT = "#FFD700"       # Gold
    BACKGROUND = "#0D0D0D"   # Dark background
    SURFACE = "#1E1E1E"      # Surface dark
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B0B0B0"
    SUCCESS = "#00C853"
    WARNING = "#FFB300"
    DANGER = "#D32F2F"
    
    @staticmethod
    def apply_dark_theme(app):
        """Apply dark theme to application"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(MomentumTheme.BACKGROUND))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(MomentumTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Base, QColor(MomentumTheme.SURFACE))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(MomentumTheme.SECONDARY))
        palette.setColor(QPalette.ColorRole.Text, QColor(MomentumTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Button, QColor(MomentumTheme.SURFACE))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(MomentumTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(MomentumTheme.PRIMARY))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(MomentumTheme.TEXT_PRIMARY))
        app.setPalette(palette)
        
        # Apply stylesheet for additional styling
        app.setStyleSheet(f"""
            QMainWindow {{
                background-color: {MomentumTheme.BACKGROUND};
            }}
            QPushButton {{
                background-color: {MomentumTheme.PRIMARY};
                color: {MomentumTheme.TEXT_PRIMARY};
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #FF1A00;
            }}
            QPushButton:pressed {{
                background-color: #B30500;
            }}
            QPushButton:disabled {{
                background-color: #444444;
                color: #666666;
            }}
            QLabel {{
                color: {MomentumTheme.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QGroupBox {{
                color: {MomentumTheme.ACCENT};
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {MomentumTheme.PRIMARY};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QTableWidget {{
                background-color: {MomentumTheme.SURFACE};
                color: {MomentumTheme.TEXT_PRIMARY};
                gridline-color: {MomentumTheme.SECONDARY};
                border: 1px solid {MomentumTheme.PRIMARY};
            }}
            QTableWidget::item:selected {{
                background-color: {MomentumTheme.PRIMARY};
            }}
            QHeaderView::section {{
                background-color: {MomentumTheme.SECONDARY};
                color: {MomentumTheme.ACCENT};
                padding: 5px;
                border: none;
                font-weight: bold;
            }}
            QListWidget {{
                background-color: {MomentumTheme.SURFACE};
                color: {MomentumTheme.TEXT_PRIMARY};
                border: 1px solid {MomentumTheme.PRIMARY};
            }}
            QListWidget::item:selected {{
                background-color: {MomentumTheme.PRIMARY};
            }}
            QTextEdit {{
                background-color: {MomentumTheme.SURFACE};
                color: {MomentumTheme.TEXT_PRIMARY};
                border: 1px solid {MomentumTheme.SECONDARY};
            }}
            QComboBox {{
                background-color: {MomentumTheme.SURFACE};
                color: {MomentumTheme.TEXT_PRIMARY};
                border: 1px solid {MomentumTheme.PRIMARY};
                padding: 5px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {MomentumTheme.TEXT_PRIMARY};
            }}
            QProgressBar {{
                border: 1px solid {MomentumTheme.SECONDARY};
                border-radius: 5px;
                text-align: center;
                background-color: {MomentumTheme.SURFACE};
                color: {MomentumTheme.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {MomentumTheme.PRIMARY};
            }}
        """)


class MainMenuScreen(QWidget):
    """Main menu screen"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title = QLabel("MOMENTUM")
        title_font = QFont("Arial", 48, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {MomentumTheme.PRIMARY};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Multi-Discipline Motorsport Manager")
        subtitle_font = QFont("Arial", 16)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"color: {MomentumTheme.ACCENT};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(50)
        
        # Menu buttons
        btn_new_career = QPushButton("NEW CAREER")
        btn_new_career.setFixedSize(300, 50)
        btn_new_career.clicked.connect(self.parent.show_discipline_selection)
        layout.addWidget(btn_new_career, alignment=Qt.AlignmentFlag.AlignCenter)
        
        btn_load = QPushButton("LOAD CAREER")
        btn_load.setFixedSize(300, 50)
        btn_load.clicked.connect(self.load_career)
        layout.addWidget(btn_load, alignment=Qt.AlignmentFlag.AlignCenter)
        
        btn_exit = QPushButton("EXIT")
        btn_exit.setFixedSize(300, 50)
        btn_exit.clicked.connect(self.parent.close)
        layout.addWidget(btn_exit, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(50)
        
        # Version info
        version = QLabel("v0.1.0 - Prototype Build")
        version.setStyleSheet(f"color: {MomentumTheme.TEXT_SECONDARY};")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        self.setLayout(layout)
    
    def load_career(self):
        """Load saved career"""
        QMessageBox.information(self, "Load Career", "Load functionality coming soon!")


class DisciplineSelectionScreen(QWidget):
    """Discipline selection screen"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("SELECT RACING DISCIPLINE")
        header_font = QFont("Arial", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setStyleSheet(f"color: {MomentumTheme.ACCENT};")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        layout.addSpacing(20)
        
        # Discipline grid
        grid = QGridLayout()
        
        disciplines = [
            ("SINGLE SEATER", "Formula & Open-Wheel Racing", "SINGLE_SEATER"),
            ("PRODUCTION TOURING", "Sedan & Tin-Top Racing", "PRODUCTION_TOURING"),
            ("RALLY STAGE", "Point-to-Point Rally", "RALLY_STAGE"),
            ("URBAN STREET", "Street Racing & Drift", "URBAN_STREET"),
            ("DRAG ACCELERATION", "Quarter Mile Racing", "DRAG_ACCELERATION"),
            ("SPRINT RALLYCROSS", "Mixed Surface Sprint", "SPRINT_RALLYCROSS"),
            ("ENDURANCE", "Multi-Hour Racing", "ENDURANCE"),
        ]
        
        row, col = 0, 0
        for name, desc, key in disciplines:
            btn = QPushButton(f"{name}\n{desc}")
            btn.setFixedSize(350, 100)
            btn.clicked.connect(lambda checked, d=key: self.select_discipline(d))
            grid.addWidget(btn, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        layout.addLayout(grid)
        
        layout.addSpacing(20)
        
        # Back button
        btn_back = QPushButton("BACK")
        btn_back.setFixedSize(200, 40)
        btn_back.clicked.connect(self.parent.show_main_menu)
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
    
    def select_discipline(self, discipline):
        """Select discipline and move to team selection"""
        self.parent.selected_discipline = discipline
        self.parent.show_team_selection()


class TeamSelectionScreen(QWidget):
    """Team selection screen"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.teams = []
        self.selected_team_id = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        self.header = QLabel("SELECT YOUR TEAM")
        header_font = QFont("Arial", 24, QFont.Weight.Bold)
        self.header.setFont(header_font)
        self.header.setStyleSheet(f"color: {MomentumTheme.ACCENT};")
        layout.addWidget(self.header)
        
        # Tier filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Tier:"))
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["All Tiers", "Tier 1 (Elite)", "Tier 2 (Midfield)", "Tier 3 (Backmarker)"])
        self.tier_combo.currentTextChanged.connect(self.filter_teams)
        filter_layout.addWidget(self.tier_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Teams table
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(5)
        self.teams_table.setHorizontalHeaderLabels(["Team Name", "Nationality", "Tier", "Budget (€M)", "ID"])
        self.teams_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.teams_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.teams_table.itemSelectionChanged.connect(self.on_team_selected)
        layout.addWidget(self.teams_table)
        
        # Team details
        self.team_details = QTextEdit()
        self.team_details.setReadOnly(True)
        self.team_details.setMaximumHeight(150)
        layout.addWidget(self.team_details)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        btn_back = QPushButton("BACK")
        btn_back.setFixedSize(150, 40)
        btn_back.clicked.connect(self.parent.show_discipline_selection)
        button_layout.addWidget(btn_back)
        
        button_layout.addStretch()
        
        self.btn_select = QPushButton("SELECT TEAM")
        self.btn_select.setFixedSize(200, 40)
        self.btn_select.setEnabled(False)
        self.btn_select.clicked.connect(self.confirm_selection)
        button_layout.addWidget(self.btn_select)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_teams(self):
        """Load teams for selected discipline"""
        try:
            discipline = self.parent.selected_discipline
            self.header.setText(f"SELECT YOUR {discipline.replace('_', ' ')} TEAM")
            
            logger.info(f"Loading teams for discipline: {discipline}")
            
            with LoggedOperation(f"Load {discipline} teams"):
                db = self.parent.db
                self.teams = db.get_teams_by_discipline(discipline)
            
            logger.info(f"Loaded {len(self.teams)} teams")
            self.display_teams(self.teams)
        
        except Exception as e:
            logger.error("Failed to load teams", exception=e)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load teams:\n{str(e)}\n\nCheck error log for details"
            )

    
    def display_teams(self, teams):
        """Display teams in table"""
        self.teams_table.setRowCount(len(teams))
        
        for i, team in enumerate(teams):
            self.teams_table.setItem(i, 0, QTableWidgetItem(team.name))
            self.teams_table.setItem(i, 1, QTableWidgetItem(team.nationality))
            self.teams_table.setItem(i, 2, QTableWidgetItem(team.tier))
            self.teams_table.setItem(i, 3, QTableWidgetItem(f"{team.budget:.1f}"))
            self.teams_table.setItem(i, 4, QTableWidgetItem(str(team.id)))
        
        self.teams_table.resizeColumnsToContents()
    
    def filter_teams(self, tier_filter):
        """Filter teams by tier"""
        if tier_filter == "All Tiers":
            self.display_teams(self.teams)
        else:
            tier_map = {
                "Tier 1 (Elite)": "tier1",
                "Tier 2 (Midfield)": "tier2",
                "Tier 3 (Backmarker)": "tier3"
            }
            tier = tier_map.get(tier_filter)
            filtered = [t for t in self.teams if t.tier == tier]
            self.display_teams(filtered)
    
    def on_team_selected(self):
        """Handle team selection"""
        selected_rows = self.teams_table.selectedItems()
        if selected_rows:
            row = self.teams_table.currentRow()
            team_id = int(self.teams_table.item(row, 4).text())
            self.selected_team_id = team_id
            
            # Find team
            team = next((t for t in self.teams if t.id == team_id), None)
            if team:
                details = f"""
<b>Team:</b> {team.name}<br>
<b>Nationality:</b> {team.nationality}<br>
<b>Tier:</b> {team.tier.upper()}<br>
<b>Budget:</b> €{team.budget:.1f}M annually<br>
<b>Founded:</b> {team.founded_year}<br>
<br>
<b>Challenge:</b> {self.get_tier_description(team.tier)}
                """
                self.team_details.setHtml(details)
                self.btn_select.setEnabled(True)
    
    def get_tier_description(self, tier):
        """Get tier description"""
        descriptions = {
            "tier1": "Win championships immediately. High expectations, high pressure.",
            "tier2": "Build competitive team over 2-3 seasons. Balanced challenge.",
            "tier3": "Long-term project. Survive financially while developing."
        }
        return descriptions.get(tier, "")
    
    def confirm_selection(self):
        """Confirm team selection and start career"""
        if self.selected_team_id:
            self.parent.start_career(self.selected_team_id)


class RaceWeekendScreen(QWidget):
    """Race weekend execution screen"""
    
    def __init__(self, parent, race_id: int):
        super().__init__()
        self.parent = parent
        self.race_id = race_id
        self.weekend_manager = RaceWeekendManager(parent.db)
        self.results = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("RACE WEEKEND")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Circuit info
        self.circuit_label = QLabel("Loading...")
        self.circuit_label.setFont(QFont("Arial", 14))
        self.circuit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.circuit_label)
        
        # Tab widget for sessions
        self.tabs = QTabWidget()
        
        # Practice tab
        self.practice_view = QTextEdit()
        self.practice_view.setReadOnly(True)
        self.practice_view.setFont(QFont("Courier New", 10))
        self.tabs.addTab(self.practice_view, "Practice")
        
        # Qualifying tab
        self.qualifying_view = QTextEdit()
        self.qualifying_view.setReadOnly(True)
        self.qualifying_view.setFont(QFont("Courier New", 10))
        self.tabs.addTab(self.qualifying_view, "Qualifying")
        
        # Race tab
        self.race_view = QTextEdit()
        self.race_view.setReadOnly(True)
        self.race_view.setFont(QFont("Courier New", 10))
        self.tabs.addTab(self.race_view, "Race Results")
        
        layout.addWidget(self.tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.btn_practice = QPushButton("Run Practice")
        self.btn_practice.clicked.connect(self.run_practice)
        button_layout.addWidget(self.btn_practice)
        
        self.btn_qualifying = QPushButton("Run Qualifying")
        self.btn_qualifying.clicked.connect(self.run_qualifying)
        self.btn_qualifying.setEnabled(False)
        button_layout.addWidget(self.btn_qualifying)
        
        self.btn_race = QPushButton("Run Race")
        self.btn_race.clicked.connect(self.run_race)
        self.btn_race.setEnabled(False)
        button_layout.addWidget(self.btn_race)
        
        self.btn_finish = QPushButton("Finish Weekend")
        self.btn_finish.clicked.connect(self.finish_weekend)
        self.btn_finish.setEnabled(False)
        button_layout.addWidget(self.btn_finish)
        
        layout.addLayout(button_layout)
        
        btn_back = QPushButton("Back to Hub")
        btn_back.clicked.connect(lambda: self.parent.show_career_hub())
        layout.addWidget(btn_back)
        
        self.setLayout(layout)
        
        # Load circuit info
        self.load_circuit_info()
    
    def load_circuit_info(self):
        """Load and display circuit information"""
        try:
            race = self.parent.db.get_race_by_id(self.race_id)
            if race:
                circuit = self.parent.db.get_circuit_by_id(race.circuit_id)
                if circuit:
                    self.circuit_label.setText(
                        f"{circuit.name} | {circuit.country}, {circuit.region} | {circuit.length_km:.2f}km"
                    )
        except Exception as e:
            logger.error(f"Failed to load circuit info: {e}")
            self.circuit_label.setText("Unknown Circuit")
    
    def run_practice(self):
        """Run practice session"""
        try:
            with LoggedOperation("Run practice session"):
                results = self.weekend_manager.run_practice_session(self.race_id)
                
                # Display results
                output = "PRACTICE SESSION RESULTS\n"
                output += "=" * 60 + "\n\n"
                output += f"{'Pos':<4} {'Driver':<25} {'Team':<20} {'Time':<10}\n"
                output += "-" * 60 + "\n"
                
                for result in results[:10]:
                    time_str = f"{result.time_or_points:.3f}s"
                    gap_str = f"+{result.gap_to_leader:.3f}" if result.gap_to_leader > 0 else "Leader"
                    output += f"{result.position:<4} {result.driver_name:<25} {result.team_name:<20} {time_str:<10}\n"
                
                self.practice_view.setPlainText(output)
                self.tabs.setCurrentIndex(0)
                
                self.btn_practice.setEnabled(False)
                self.btn_qualifying.setEnabled(True)
                
        except Exception as e:
            logger.error(f"Practice session failed: {e}")
            QMessageBox.critical(self, "Error", f"Practice session failed:\n{str(e)}")
    
    def run_qualifying(self):
        """Run qualifying session"""
        try:
            with LoggedOperation("Run qualifying session"):
                results = self.weekend_manager.run_qualifying(self.race_id)
                
                # Display results
                output = "QUALIFYING RESULTS - STARTING GRID\n"
                output += "=" * 60 + "\n\n"
                output += f"{'Pos':<4} {'Driver':<25} {'Team':<20} {'Time':<10}\n"
                output += "-" * 60 + "\n"
                
                for result in results:
                    time_str = f"{result.time_or_points:.3f}s"
                    output += f"{result.position:<4} {result.driver_name:<25} {result.team_name:<20} {time_str:<10}\n"
                
                self.qualifying_view.setPlainText(output)
                self.tabs.setCurrentIndex(1)
                
                # Update standings with pole position
                if hasattr(self.parent, 'standings_manager') and self.parent.world.state:
                    if self.parent.world.state.active_championship_id:
                        self.parent.standings_manager.add_qualifying_results(
                            self.parent.world.state.active_championship_id,
                            results
                        )
                
                self.btn_qualifying.setEnabled(False)
                self.btn_race.setEnabled(True)
                
        except Exception as e:
            logger.error(f"Qualifying failed: {e}")
            QMessageBox.critical(self, "Error", f"Qualifying failed:\n{str(e)}")
    
    def run_race(self):
        """Run the main race"""
        try:
            with LoggedOperation("Run race"):
                results = self.weekend_manager.run_race(self.race_id)
                
                # Display results
                output = "RACE RESULTS\n"
                output += "=" * 60 + "\n\n"
                output += f"{'Pos':<4} {'Driver':<25} {'Team':<20} {'Points':<8}\n"
                output += "-" * 60 + "\n"
                
                for result in results:
                    points_str = f"{int(result.time_or_points)}"
                    fastest_lap = " FL" if result.fastest_lap else ""
                    output += f"{result.position:<4} {result.driver_name:<25} {result.team_name:<20} {points_str:<8}{fastest_lap}\n"
                
                self.race_view.setPlainText(output)
                self.tabs.setCurrentIndex(2)
                
                # Update championship standings
                if hasattr(self.parent, 'standings_manager') and self.parent.world.state:
                    if self.parent.world.state.active_championship_id:
                        race = self.parent.db.get_race_by_id(self.race_id)
                        circuit = self.parent.db.get_circuit_by_id(race.circuit_id)
                        
                        self.parent.standings_manager.update_with_race_results(
                            self.parent.world.state.active_championship_id,
                            results,
                            circuit.name if circuit else "Unknown"
                        )
                
                self.btn_race.setEnabled(False)
                self.btn_finish.setEnabled(True)
                
        except Exception as e:
            logger.error(f"Race failed: {e}")
            QMessageBox.critical(self, "Error", f"Race failed:\n{str(e)}")
    
    def finish_weekend(self):
        """Complete weekend and return to hub"""
        # Update player stats
        if self.parent.world.state and self.parent.world.state.player_profile:
            self.parent.world.state.player_profile.total_races += 1
            self.parent.world.state.current_race_index += 1
        
        QMessageBox.information(
            self, 
            "Weekend Complete", 
            "Race weekend finished!\nStandings have been updated."
        )
        
        self.parent.show_career_hub()


class StandingsScreen(QWidget):
    """Championship standings display"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("CHAMPIONSHIP STANDINGS")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabs for driver and constructor standings
        self.tabs = QTabWidget()
        
        # Driver standings
        self.driver_table = QTableWidget()
        self.driver_table.setColumnCount(8)
        self.driver_table.setHorizontalHeaderLabels([
            "Pos", "Driver", "Team", "Points", "Wins", "Podiums", "Poles", "Change"
        ])
        self.driver_table.horizontalHeader().setStretchLastSection(False)
        self.driver_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabs.addTab(self.driver_table, "Driver Standings")
        
        # Constructor standings
        self.constructor_table = QTableWidget()
        self.constructor_table.setColumnCount(7)
        self.constructor_table.setHorizontalHeaderLabels([
            "Pos", "Team", "Points", "Wins", "Podiums", "1-2s", "Change"
        ])
        self.constructor_table.horizontalHeader().setStretchLastSection(False)
        self.constructor_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabs.addTab(self.constructor_table, "Constructor Standings")
        
        layout.addWidget(self.tabs)
        
        # Championship info
        self.info_label = QLabel("")
        self.info_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.info_label)
        
        btn_back = QPushButton("Back to Hub")
        btn_back.clicked.connect(lambda: self.parent.show_career_hub())
        layout.addWidget(btn_back)
        
        self.setLayout(layout)
    
    def update_display(self):
        """Update standings tables"""
        if not hasattr(self.parent, 'standings_manager'):
            return
        
        if not self.parent.world.state or not self.parent.world.state.active_championship_id:
            return
        
        standings = self.parent.standings_manager.get_standings(
            self.parent.world.state.active_championship_id
        )
        
        if not standings:
            return
        
        # Update driver standings
        self.driver_table.setRowCount(len(standings.driver_standings))
        for row, driver in enumerate(standings.driver_standings):
            self.driver_table.setItem(row, 0, QTableWidgetItem(str(driver.position)))
            self.driver_table.setItem(row, 1, QTableWidgetItem(driver.driver_name))
            self.driver_table.setItem(row, 2, QTableWidgetItem(driver.team_name))
            self.driver_table.setItem(row, 3, QTableWidgetItem(str(int(driver.points))))
            self.driver_table.setItem(row, 4, QTableWidgetItem(str(driver.wins)))
            self.driver_table.setItem(row, 5, QTableWidgetItem(str(driver.podiums)))
            self.driver_table.setItem(row, 6, QTableWidgetItem(str(driver.poles)))
            
            change = driver.position_change
            change_str = f"+{change}" if change > 0 else str(change) if change < 0 else "-"
            self.driver_table.setItem(row, 7, QTableWidgetItem(change_str))
        
        # Update constructor standings
        self.constructor_table.setRowCount(len(standings.constructor_standings))
        for row, constructor in enumerate(standings.constructor_standings):
            self.constructor_table.setItem(row, 0, QTableWidgetItem(str(constructor.position)))
            self.constructor_table.setItem(row, 1, QTableWidgetItem(constructor.team_name))
            self.constructor_table.setItem(row, 2, QTableWidgetItem(str(int(constructor.points))))
            self.constructor_table.setItem(row, 3, QTableWidgetItem(str(constructor.wins)))
            self.constructor_table.setItem(row, 4, QTableWidgetItem(str(constructor.podiums)))
            self.constructor_table.setItem(row, 5, QTableWidgetItem(str(constructor.one_two_finishes)))
            
            change = constructor.position_change
            change_str = f"+{change}" if change > 0 else str(change) if change < 0 else "-"
            self.constructor_table.setItem(row, 6, QTableWidgetItem(change_str))
        
        # Update info
        self.info_label.setText(
            f"Season {standings.season} | {standings.discipline} | "
            f"Races: {standings.races_completed}/{standings.total_races}"
        )


class CareerHubScreen(QWidget):
    """Main career hub screen"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Top bar - Season info
        top_bar = QHBoxLayout()
        
        self.season_label = QLabel("Season 1 - 2025")
        self.season_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        top_bar.addWidget(self.season_label)
        
        top_bar.addStretch()
        
        self.date_label = QLabel("March 2025")
        self.date_label.setFont(QFont("Arial", 14))
        top_bar.addWidget(self.date_label)
        
        layout.addLayout(top_bar)
        
        # Main content area
        content = QHBoxLayout()
        
        # Left panel - Team info
        left_panel = QVBoxLayout()
        
        team_group = QGroupBox("YOUR TEAM")
        team_layout = QVBoxLayout()
        self.team_name_label = QLabel("Team Name")
        self.team_name_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        team_layout.addWidget(self.team_name_label)
        
        self.team_info_label = QLabel("Team Info")
        team_layout.addWidget(self.team_info_label)
        
        team_group.setLayout(team_layout)
        left_panel.addWidget(team_group)
        
        # Championship standing
        standing_group = QGroupBox("CHAMPIONSHIP STANDING")
        standing_layout = QVBoxLayout()
        self.standing_label = QLabel("Not started")
        self.standing_label.setFont(QFont("Arial", 14))
        standing_layout.addWidget(self.standing_label)
        standing_group.setLayout(standing_layout)
        left_panel.addWidget(standing_group)
        
        # Budget
        budget_group = QGroupBox("FINANCES")
        budget_layout = QVBoxLayout()
        self.budget_label = QLabel("Budget: €0M")
        self.budget_label.setFont(QFont("Arial", 14))
        budget_layout.addWidget(self.budget_label)
        budget_group.setLayout(budget_layout)
        left_panel.addWidget(budget_group)
        
        left_panel.addStretch()
        
        content.addLayout(left_panel, 1)
        
        # Right panel - Actions
        right_panel = QVBoxLayout()
        
        actions_group = QGroupBox("ACTIONS")
        actions_layout = QVBoxLayout()
        
        btn_next_race = QPushButton("NEXT RACE WEEKEND")
        btn_next_race.setFixedHeight(50)
        btn_next_race.clicked.connect(self.next_race)
        actions_layout.addWidget(btn_next_race)
        
        btn_standings = QPushButton("VIEW STANDINGS")
        btn_standings.setFixedHeight(50)
        btn_standings.clicked.connect(self.view_standings)
        actions_layout.addWidget(btn_standings)
        
        btn_calendar = QPushButton("SEASON CALENDAR")
        btn_calendar.setFixedHeight(50)
        btn_calendar.clicked.connect(self.view_calendar)
        actions_layout.addWidget(btn_calendar)
        
        btn_team = QPushButton("TEAM MANAGEMENT")
        btn_team.setFixedHeight(50)
        btn_team.clicked.connect(self.manage_team)
        actions_layout.addWidget(btn_team)
        
        btn_development = QPushButton("CAR DEVELOPMENT")
        btn_development.setFixedHeight(50)
        btn_development.clicked.connect(self.car_development)
        actions_layout.addWidget(btn_development)
        
        btn_finances = QPushButton("FINANCIAL OVERVIEW")
        btn_finances.setFixedHeight(50)
        btn_finances.clicked.connect(self.finances)
        actions_layout.addWidget(btn_finances)
        
        actions_layout.addStretch()
        
        btn_save = QPushButton("SAVE GAME")
        btn_save.setFixedHeight(40)
        btn_save.clicked.connect(self.save_game)
        actions_layout.addWidget(btn_save)
        
        btn_exit = QPushButton("EXIT TO MENU")
        btn_exit.setFixedHeight(40)
        btn_exit.clicked.connect(self.exit_career)
        actions_layout.addWidget(btn_exit)
        
        actions_group.setLayout(actions_layout)
        right_panel.addWidget(actions_group)
        
        content.addLayout(right_panel, 1)
        
        layout.addLayout(content)
        
        self.setLayout(layout)
    
    def update_display(self):
        """Update all displayed information"""
        if not self.parent.world.state:
            return
        
        state = self.parent.world.state
        
        # Season and date
        self.season_label.setText(f"Season {state.season_number} - {state.calendar_year}")
        self.date_label.setText(state.current_date)
        
        # Team info
        if state.player_profile:
            team = self.parent.db.get_team(state.player_profile.team_id)
            if team:
                self.team_name_label.setText(team.name)
                self.team_info_label.setText(
                    f"<b>Manager:</b> {state.player_profile.player_name}<br>"
                    f"<b>Discipline:</b> {team.discipline}<br>"
                    f"<b>Tier:</b> {team.tier.upper()}"
                )
                self.budget_label.setText(f"Budget: €{team.budget:.1f}M")
        
        # Championship standing
        if state.player_profile:
            self.standing_label.setText(
                f"<b>Races:</b> {state.player_profile.total_races}<br>"
                f"<b>Wins:</b> {state.player_profile.total_wins}<br>"
                f"<b>Podiums:</b> {state.player_profile.podium_finishes}"
            )
    
    def next_race(self):
        """Progress to next race"""
        if not self.parent.world.state or not self.parent.world.current_season_races:
            QMessageBox.warning(self, "No Races", "No races available in current season.")
            return
        
        # Get current race index
        race_index = self.parent.world.state.current_race_index
        
        if race_index >= len(self.parent.world.current_season_races):
            QMessageBox.information(self, "Season Complete", "All races completed for this season!")
            return
        
        # Get next race
        next_race = self.parent.world.current_season_races[race_index]
        
        # Show race weekend screen
        self.parent.show_race_weekend(next_race.id)
    
    def view_standings(self):
        """View championship standings"""
        self.parent.show_standings()
    
    def view_calendar(self):
        """View season calendar"""
        if not self.parent.world.current_season_races:
            QMessageBox.warning(self, "No Calendar", "No season calendar available.")
            return
        
        # Build calendar text
        calendar_text = "SEASON CALENDAR\n"
        calendar_text += "=" * 60 + "\n\n"
        
        for idx, race in enumerate(self.parent.world.current_season_races, 1):
            circuit = self.parent.db.get_circuit_by_id(race.circuit_id)
            status = "✓ COMPLETED" if idx <= self.parent.world.state.current_race_index else "  UPCOMING"
            
            calendar_text += f"Round {idx:2d} {status} - {circuit.name if circuit else 'Unknown'}\n"
            calendar_text += f"           {circuit.country}, {circuit.region if circuit else ''}\n\n"
        
        # Show in message box (temporary - should be a proper screen)
        msg = QMessageBox(self)
        msg.setWindowTitle("Season Calendar")
        msg.setText(calendar_text)
        msg.setFont(QFont("Courier New", 10))
        msg.exec()
    
    def manage_team(self):
        """Team management"""
        self.parent.show_team_management()
    
    def car_development(self):
        """Car development"""
        self.parent.show_car_development()
    
    def finances(self):
        """Financial overview"""
        self.parent.show_finances()
    
    def save_game(self):
        """Save current game"""
        if self.parent.world.save_game():
            QMessageBox.information(self, "Save Game", "Game saved successfully!")
        else:
            QMessageBox.warning(self, "Save Game", "Failed to save game.")
    
    def exit_career(self):
        """Exit to main menu"""
        reply = QMessageBox.question(
            self, "Exit Career",
            "Are you sure you want to exit? Make sure to save first!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.parent.show_main_menu()


class TeamManagementScreen(QWidget):
    """Team management - hire/fire drivers and staff"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("TEAM MANAGEMENT")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Budget display
        self.budget_label = QLabel("Budget: €0M")
        self.budget_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.budget_label)
        
        # Tabs for different management areas
        tabs = QTabWidget()
        
        # Current Roster tab
        roster_tab = QWidget()
        roster_layout = QVBoxLayout()
        
        QLabel("CURRENT DRIVERS").setParent(roster_tab)
        self.drivers_table = QTableWidget()
        self.drivers_table.setColumnCount(6)
        self.drivers_table.setHorizontalHeaderLabels([
            "Name", "Salary (€M)", "Contract Years", "Years Left", "Performance", "Action"
        ])
        roster_layout.addWidget(QLabel("CURRENT DRIVERS"))
        roster_layout.addWidget(self.drivers_table)
        
        QLabel("CURRENT STAFF").setParent(roster_tab)
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(6)
        self.staff_table.setHorizontalHeaderLabels([
            "Name", "Role", "Salary (€M)", "Contract Years", "Skill", "Action"
        ])
        roster_layout.addWidget(QLabel("CURRENT STAFF"))
        roster_layout.addWidget(self.staff_table)
        
        roster_tab.setLayout(roster_layout)
        tabs.addTab(roster_tab, "Current Roster")
        
        # Hire Drivers tab
        hire_drivers_tab = QWidget()
        hire_drivers_layout = QVBoxLayout()
        
        self.available_drivers_table = QTableWidget()
        self.available_drivers_table.setColumnCount(7)
        self.available_drivers_table.setHorizontalHeaderLabels([
            "Name", "Age", "Nationality", "Skill", "Aptitude", "Salary (€M)", "Hire"
        ])
        hire_drivers_layout.addWidget(self.available_drivers_table)
        
        hire_drivers_tab.setLayout(hire_drivers_layout)
        tabs.addTab(hire_drivers_tab, "Available Drivers")
        
        # Hire Staff tab
        hire_staff_tab = QWidget()
        hire_staff_layout = QVBoxLayout()
        
        self.available_staff_table = QTableWidget()
        self.available_staff_table.setColumnCount(6)
        self.available_staff_table.setHorizontalHeaderLabels([
            "Name", "Role", "Experience", "Skill", "Salary (€M)", "Hire"
        ])
        hire_staff_layout.addWidget(self.available_staff_table)
        
        hire_staff_tab.setLayout(hire_staff_layout)
        tabs.addTab(hire_staff_tab, "Available Staff")
        
        layout.addWidget(tabs)
        
        btn_back = QPushButton("Back to Hub")
        btn_back.clicked.connect(lambda: self.parent.show_career_hub())
        layout.addWidget(btn_back)
        
        self.setLayout(layout)
    
    def update_display(self):
        """Load and display team roster and available personnel"""
        if not self.parent.world.state:
            return
        
        team_id = self.parent.world.state.player_profile.team_id
        
        # Initialize team if needed
        if team_id not in self.parent.team_manager.active_contracts:
            self.parent.team_manager.initialize_team(team_id)
        
        roster = self.parent.team_manager.get_team_roster(team_id)
        
        # Update budget
        self.budget_label.setText(f"Budget: €{roster['financials'].current_budget:.1f}M")
        
        # Update drivers table
        self.drivers_table.setRowCount(len(roster['drivers']))
        for row, contract in enumerate(roster['drivers']):
            self.drivers_table.setItem(row, 0, QTableWidgetItem(contract.person_name))
            self.drivers_table.setItem(row, 1, QTableWidgetItem(f"{contract.salary_per_year:.1f}"))
            self.drivers_table.setItem(row, 2, QTableWidgetItem(str(contract.contract_years)))
            self.drivers_table.setItem(row, 3, QTableWidgetItem(str(contract.years_remaining)))
            self.drivers_table.setItem(row, 4, QTableWidgetItem("TBD"))  # Add performance tracking
            
            btn_fire = QPushButton("Fire")
            btn_fire.clicked.connect(lambda checked, did=contract.person_id: self.fire_driver(did))
            self.drivers_table.setCellWidget(row, 5, btn_fire)
        
        # Update staff table
        self.staff_table.setRowCount(len(roster['staff'][:10]))  # Show top 10
        for row, contract in enumerate(roster['staff'][:10]):
            self.staff_table.setItem(row, 0, QTableWidgetItem(contract.person_name))
            self.staff_table.setItem(row, 1, QTableWidgetItem(contract.role))
            self.staff_table.setItem(row, 2, QTableWidgetItem(f"{contract.salary_per_year:.1f}"))
            self.staff_table.setItem(row, 3, QTableWidgetItem(str(contract.contract_years)))
            self.staff_table.setItem(row, 4, QTableWidgetItem("TBD"))
            
            btn_fire = QPushButton("Fire")
            btn_fire.clicked.connect(lambda checked, sid=contract.person_id: self.fire_staff(sid))
            self.staff_table.setCellWidget(row, 5, btn_fire)
        
        # Load available drivers
        discipline = self.parent.selected_discipline
        available_drivers = self.parent.team_manager.get_available_drivers(discipline, team_id)
        
        self.available_drivers_table.setRowCount(min(20, len(available_drivers)))
        for row, driver in enumerate(available_drivers[:20]):
            self.available_drivers_table.setItem(row, 0, QTableWidgetItem(driver['name']))
            self.available_drivers_table.setItem(row, 1, QTableWidgetItem(str(driver['age'])))
            self.available_drivers_table.setItem(row, 2, QTableWidgetItem(driver['nationality']))
            self.available_drivers_table.setItem(row, 3, QTableWidgetItem(f"{driver['overall_skill']:.1f}"))
            self.available_drivers_table.setItem(row, 4, QTableWidgetItem(f"{driver['discipline_aptitude']:.1f}"))
            self.available_drivers_table.setItem(row, 5, QTableWidgetItem(f"{driver['asking_salary']:.1f}"))
            
            btn_hire = QPushButton("Hire")
            btn_hire.clicked.connect(lambda checked, did=driver['id'], sal=driver['asking_salary']: self.hire_driver(did, sal))
            self.available_drivers_table.setCellWidget(row, 6, btn_hire)
        
        # Load available staff
        available_staff = self.parent.team_manager.get_available_staff()
        
        self.available_staff_table.setRowCount(min(20, len(available_staff)))
        for row, staff in enumerate(available_staff[:20]):
            self.available_staff_table.setItem(row, 0, QTableWidgetItem(staff['name']))
            self.available_staff_table.setItem(row, 1, QTableWidgetItem(staff['role']))
            self.available_staff_table.setItem(row, 2, QTableWidgetItem(str(staff['experience_years'])))
            self.available_staff_table.setItem(row, 3, QTableWidgetItem(str(staff['skill_level'])))
            self.available_staff_table.setItem(row, 4, QTableWidgetItem(f"{staff['asking_salary']:.2f}"))
            
            btn_hire = QPushButton("Hire")
            btn_hire.clicked.connect(lambda checked, sid=staff['id'], sal=staff['asking_salary']: self.hire_staff(sid, sal))
            self.available_staff_table.setCellWidget(row, 5, btn_hire)
    
    def hire_driver(self, driver_id: int, salary: float):
        """Hire a driver"""
        team_id = self.parent.world.state.player_profile.team_id
        success, message = self.parent.team_manager.hire_driver(
            team_id, driver_id, salary, contract_years=2
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.update_display()
        else:
            QMessageBox.warning(self, "Failed", message)
    
    def fire_driver(self, driver_id: int):
        """Fire a driver"""
        reply = QMessageBox.question(
            self, "Confirm",
            "Are you sure you want to fire this driver? You must pay the buyout clause.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            team_id = self.parent.world.state.player_profile.team_id
            success, message = self.parent.team_manager.fire_driver(team_id, driver_id)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.update_display()
            else:
                QMessageBox.warning(self, "Failed", message)
    
    def hire_staff(self, staff_id: int, salary: float):
        """Hire a staff member"""
        team_id = self.parent.world.state.player_profile.team_id
        success, message = self.parent.team_manager.hire_staff(
            team_id, staff_id, salary, contract_years=3
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.update_display()
        else:
            QMessageBox.warning(self, "Failed", message)
    
    def fire_staff(self, staff_id: int):
        """Fire a staff member"""
        reply = QMessageBox.question(
            self, "Confirm",
            "Are you sure you want to fire this staff member?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            team_id = self.parent.world.state.player_profile.team_id
            success, message = self.parent.team_manager.fire_staff(team_id, staff_id)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.update_display()
            else:
                QMessageBox.warning(self, "Failed", message)


class CarDevelopmentScreen(QWidget):
    """Car development and R&D management"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("CAR DEVELOPMENT")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Car ratings
        ratings_group = QGroupBox("CAR PERFORMANCE")
        ratings_layout = QVBoxLayout()
        
        self.overall_rating = QLabel("Overall: 50.0")
        self.overall_rating.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        ratings_layout.addWidget(self.overall_rating)
        
        self.speed_rating = QLabel("Speed: 50.0")
        ratings_layout.addWidget(self.speed_rating)
        
        self.handling_rating = QLabel("Handling: 50.0")
        ratings_layout.addWidget(self.handling_rating)
        
        self.reliability_rating = QLabel("Reliability: 50.0")
        ratings_layout.addWidget(self.reliability_rating)
        
        ratings_group.setLayout(ratings_layout)
        layout.addWidget(ratings_group)
        
        # Components table
        components_group = QGroupBox("COMPONENTS")
        components_layout = QVBoxLayout()
        
        self.components_table = QTableWidget()
        self.components_table.setColumnCount(5)
        self.components_table.setHorizontalHeaderLabels([
            "Component", "Level", "Progress", "Reliability", "Upgrade"
        ])
        components_layout.addWidget(self.components_table)
        
        components_group.setLayout(components_layout)
        layout.addWidget(components_group)
        
        # Development budget
        budget_layout = QHBoxLayout()
        budget_layout.addWidget(QLabel("Development Budget (€M):"))
        self.budget_input = QTextEdit()
        self.budget_input.setMaximumHeight(30)
        self.budget_input.setPlaceholderText("10.0")
        budget_layout.addWidget(self.budget_input)
        
        btn_set_budget = QPushButton("Set Budget")
        btn_set_budget.clicked.connect(self.set_development_budget)
        budget_layout.addWidget(btn_set_budget)
        
        layout.addLayout(budget_layout)
        
        btn_back = QPushButton("Back to Hub")
        btn_back.clicked.connect(lambda: self.parent.show_career_hub())
        layout.addWidget(btn_back)
        
        self.setLayout(layout)
    
    def update_display(self):
        """Update car development display"""
        if not self.parent.world.state:
            return
        
        team_id = self.parent.world.state.player_profile.team_id
        team = self.parent.db.get_team(team_id)
        
        # Initialize car if needed
        if team_id not in self.parent.car_dev_manager.team_cars:
            self.parent.car_dev_manager.initialize_car(team_id, team.tier, 2025)
        
        car = self.parent.car_dev_manager.team_cars[team_id]
        
        # Update ratings
        self.overall_rating.setText(f"Overall: {car.overall_rating:.1f}")
        self.speed_rating.setText(f"Speed: {car.speed_rating:.1f}")
        self.handling_rating.setText(f"Handling: {car.handling_rating:.1f}")
        self.reliability_rating.setText(f"Reliability: {car.reliability_rating:.1f}")
        
        # Update components table
        components = list(car.components.values())
        self.components_table.setRowCount(len(components))
        
        for row, comp in enumerate(components):
            self.components_table.setItem(row, 0, QTableWidgetItem(comp.component_name.title()))
            self.components_table.setItem(row, 1, QTableWidgetItem(f"{comp.current_level}/{comp.max_level}"))
            
            progress = f"{comp.development_points:.0f}/{comp.points_needed:.0f}"
            self.components_table.setItem(row, 2, QTableWidgetItem(progress))
            
            self.components_table.setItem(row, 3, QTableWidgetItem(f"{comp.reliability:.1f}%"))
            
            btn_upgrade = QPushButton(f"Upgrade (€{comp.upgrade_cost:.1f}M)")
            btn_upgrade.clicked.connect(lambda checked, name=comp.component_name: self.upgrade_component(name))
            self.components_table.setCellWidget(row, 4, btn_upgrade)
    
    def upgrade_component(self, component_name: str):
        """Upgrade a component"""
        team_id = self.parent.world.state.player_profile.team_id
        financials = self.parent.team_manager.team_financials.get(team_id)
        
        if not financials:
            QMessageBox.warning(self, "Error", "Team financials not initialized")
            return
        
        success, message, cost = self.parent.car_dev_manager.upgrade_component(
            team_id, component_name, financials.current_budget
        )
        
        if success:
            financials.current_budget -= cost
            financials.development_costs += cost
            QMessageBox.information(self, "Success", message)
            self.update_display()
        else:
            QMessageBox.warning(self, "Failed", message)
    
    def set_development_budget(self):
        """Set development budget"""
        try:
            budget = float(self.budget_input.toPlainText())
            team_id = self.parent.world.state.player_profile.team_id
            
            car = self.parent.car_dev_manager.team_cars.get(team_id)
            if car:
                car.development_budget = budget
                QMessageBox.information(self, "Success", f"Development budget set to €{budget:.1f}M")
            else:
                QMessageBox.warning(self, "Error", "Car not initialized")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid budget amount")


class FinancesScreen(QWidget):
    """Financial overview and management"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("FINANCIAL OVERVIEW")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Current budget
        self.budget_label = QLabel("Current Budget: €0M")
        self.budget_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(self.budget_label)
        
        # Income breakdown
        income_group = QGroupBox("INCOME")
        income_layout = QVBoxLayout()
        self.prize_money_label = QLabel("Prize Money: €0M")
        self.sponsorship_label = QLabel("Sponsorships: €0M")
        self.manufacturer_label = QLabel("Manufacturer Bonus: €0M")
        income_layout.addWidget(self.prize_money_label)
        income_layout.addWidget(self.sponsorship_label)
        income_layout.addWidget(self.manufacturer_label)
        income_group.setLayout(income_layout)
        layout.addWidget(income_group)
        
        # Expenses breakdown
        expenses_group = QGroupBox("EXPENSES")
        expenses_layout = QVBoxLayout()
        self.driver_salaries_label = QLabel("Driver Salaries: €0M")
        self.staff_salaries_label = QLabel("Staff Salaries: €0M")
        self.development_label = QLabel("Development: €0M")
        self.operational_label = QLabel("Operations: €0M")
        expenses_layout.addWidget(self.driver_salaries_label)
        expenses_layout.addWidget(self.staff_salaries_label)
        expenses_layout.addWidget(self.development_label)
        expenses_layout.addWidget(self.operational_label)
        expenses_group.setLayout(expenses_layout)
        layout.addWidget(expenses_group)
        
        # Projection
        self.projection_label = QLabel("End of Season Projection: €0M")
        self.projection_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(self.projection_label)
        
        btn_back = QPushButton("Back to Hub")
        btn_back.clicked.connect(lambda: self.parent.show_career_hub())
        layout.addWidget(btn_back)
        
        self.setLayout(layout)
    
    def update_display(self):
        """Update financial display"""
        if not self.parent.world.state:
            return
        
        team_id = self.parent.world.state.player_profile.team_id
        
        # Initialize if needed
        if team_id not in self.parent.team_manager.team_financials:
            self.parent.team_manager.initialize_team(team_id)
        
        financials = self.parent.team_manager.team_financials[team_id]
        
        self.budget_label.setText(f"Current Budget: €{financials.current_budget:.1f}M")
        
        self.prize_money_label.setText(f"Prize Money: €{financials.prize_money:.1f}M")
        self.sponsorship_label.setText(f"Sponsorships: €{financials.sponsorship_income:.1f}M")
        self.manufacturer_label.setText(f"Manufacturer Bonus: €{financials.manufacturer_bonus:.1f}M")
        
        self.driver_salaries_label.setText(f"Driver Salaries: €{financials.driver_salaries:.1f}M")
        self.staff_salaries_label.setText(f"Staff Salaries: €{financials.staff_salaries:.1f}M")
        self.development_label.setText(f"Development: €{financials.development_costs:.1f}M")
        self.operational_label.setText(f"Operations: €{financials.operational_costs:.1f}M")
        
        # Calculate projection
        total_income = financials.prize_money + financials.sponsorship_income + financials.manufacturer_bonus
        total_expenses = (financials.driver_salaries + financials.staff_salaries + 
                         financials.development_costs + financials.operational_costs)
        projection = financials.current_budget + total_income - total_expenses
        
        self.projection_label.setText(f"End of Season Projection: €{projection:.1f}M")


class MomentumGame(QMainWindow):
    """Main game window"""
    
    def __init__(self):
        super().__init__()
        
        logger.info("=" * 80)
        logger.info("MOMENTUM Game Starting")
        logger.info("=" * 80)
        
        try:
            with LoggedOperation("Initialize Database"):
                self.db = DatabaseManager()
            
            with LoggedOperation("Initialize Game World"):
                self.world = GameWorld()
            
            with LoggedOperation("Initialize Managers"):
                self.standings_manager = StandingsManager(self.db)
                self.team_manager = TeamManager(self.db)
                self.car_dev_manager = CarDevelopmentManager()
            
            self.selected_discipline = None
            self.init_ui()
            
            logger.info("Game initialization successful")
        
        except Exception as e:
            logger.critical("Failed to initialize game", exception=e)
            QMessageBox.critical(
                None,
                "Initialization Error",
                f"Failed to start MOMENTUM:\n\n{str(e)}\n\nCheck logs/errors_*.log for details"
            )
            raise
    
    def init_ui(self):
        """Initialize the main window"""
        self.setWindowTitle("MOMENTUM - Motorsport Manager")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and stacked layout
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create screens
        self.main_menu = MainMenuScreen(self)
        self.discipline_selection = DisciplineSelectionScreen(self)
        self.team_selection = TeamSelectionScreen(self)
        self.career_hub = CareerHubScreen(self)
        self.standings_screen = StandingsScreen(self)
        self.team_mgmt_screen = TeamManagementScreen(self)
        self.car_dev_screen = CarDevelopmentScreen(self)
        self.finances_screen = FinancesScreen(self)
        
        # Add screens to stack
        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.discipline_selection)
        self.stack.addWidget(self.team_selection)
        self.stack.addWidget(self.career_hub)
        self.stack.addWidget(self.standings_screen)
        self.stack.addWidget(self.team_mgmt_screen)
        self.stack.addWidget(self.car_dev_screen)
        self.stack.addWidget(self.finances_screen)
        
        # Show main menu
        self.show_main_menu()
    
    def show_main_menu(self):
        """Show main menu screen"""
        self.stack.setCurrentWidget(self.main_menu)
    
    def show_discipline_selection(self):
        """Show discipline selection screen"""
        self.stack.setCurrentWidget(self.discipline_selection)
    
    def show_team_selection(self):
        """Show team selection screen"""
        self.team_selection.load_teams()
        self.stack.setCurrentWidget(self.team_selection)
    
    def show_career_hub(self):
        """Show career hub screen"""
        self.career_hub.update_display()
        self.stack.setCurrentWidget(self.career_hub)
    
    def show_race_weekend(self, race_id: int):
        """Show race weekend screen"""
        # Create new race weekend screen (don't cache it)
        race_weekend = RaceWeekendScreen(self, race_id)
        self.stack.addWidget(race_weekend)
        self.stack.setCurrentWidget(race_weekend)
    
    def show_standings(self):
        """Show standings screen"""
        self.standings_screen.update_display()
        self.stack.setCurrentWidget(self.standings_screen)
    
    def show_team_management(self):
        """Show team management screen"""
        self.team_mgmt_screen.update_display()
        self.stack.setCurrentWidget(self.team_mgmt_screen)
    
    def show_car_development(self):
        """Show car development screen"""
        self.car_dev_screen.update_display()
        self.stack.setCurrentWidget(self.car_dev_screen)
    
    def show_finances(self):
        """Show financial overview screen"""
        self.finances_screen.update_display()
        self.stack.setCurrentWidget(self.finances_screen)
    
    def start_career(self, team_id):
        """Start a new career"""
        try:
            logger.info(f"Starting new career with team ID: {team_id}")
            
            # Create new game
            with LoggedOperation("Initialize new career"):
                self.world.new_game("Player")
            
            # Select team
            with LoggedOperation("Select team"):
                if self.world.select_team(team_id):
                    logger.info(f"Team {team_id} selected successfully")
                else:
                    raise RuntimeError("Failed to select team")
            
            # Create championship season
            with LoggedOperation("Create championship season"):
                champ_id = self.world.create_championship_season(
                    discipline=self.selected_discipline,
                    num_races=10
                )
                
                if not champ_id:
                    raise RuntimeError("Failed to create championship")
                
                # Initialize standings
                self.standings_manager.initialize_championship(
                    championship_id=champ_id,
                    discipline=self.selected_discipline,
                    season=self.world.state.calendar_year,
                    total_races=len(self.world.current_season_races)
                )
            
            # Initialize team management and car development
            with LoggedOperation("Initialize team management"):
                team = self.db.get_team(team_id)
                self.team_manager.initialize_team(team_id)
                self.car_dev_manager.initialize_car(team_id, team.tier, self.world.state.calendar_year)
            
            logger.info("Career started successfully")
            
            # Show career hub
            self.show_career_hub()
        
        except Exception as e:
            logger.error("Failed to start career", exception=e, team_id=team_id)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start career:\n\n{str(e)}\n\nCheck logs/errors_*.log for details"
            )



def main():
    """Main entry point"""
    # Setup exception handler first
    setup_exception_handler()
    
    logger.info("Starting MOMENTUM application")
    
    try:
        app = QApplication(sys.argv)
        
        # Set application info
        app.setApplicationName("MOMENTUM")
        app.setOrganizationName("Motorsport Games")
        
        logger.info("Application instance created")
        
        # Apply dark theme
        with LoggedOperation("Apply theme"):
            MomentumTheme.apply_dark_theme(app)
        
        # Create and show main window
        with LoggedOperation("Create main window"):
            game = MomentumGame()
            game.show()
        
        logger.info("Game window shown - entering event loop")
        
        # Run application
        exit_code = app.exec()
        
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code
    
    except Exception as e:
        logger.critical("Fatal error in main()", exception=e)
        logger.generate_crash_report({'location': 'main()'})
        
        # Show error dialog
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"MOMENTUM encountered a fatal error:\n\n{str(e)}\n\n"
            f"Crash report saved to logs folder.\n"
            f"Please send the crash report to the developer."
        )
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
