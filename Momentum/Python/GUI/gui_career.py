"""
Career Mode GUI for Momentum Racing Simulator.

Implements a dedicated career HQ flow:
- Select championship
- Select and lock player team ownership once
- Manage team state between races
- Start the next scheduled race from HQ
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QHeaderView,
)

from database.database_manager import DatabaseManager
from services.championship_service import ChampionshipService
from GUI.gui_championship import ChampionshipSelectionDialog, _player_label


PLAYER_ID = "local_player"


class CareerSelectionDialog(ChampionshipSelectionDialog):
    """Career-specific entry dialog (backed by championship data model)."""

    def __init__(self, db, parent=None):
        super().__init__(db, parent)
        self.setWindowTitle("Select Career")


class CareerTeamSelectionDialog(QDialog):
    """Select the player-owned team for this career save."""

    def __init__(self, db: DatabaseManager, discipline: str, parent=None):
        super().__init__(parent)
        self.db = db
        self.discipline = discipline
        self.selected_team = None

        self.setWindowTitle("Select Career Team")
        self.resize(900, 520)
        self._setup_ui()
        self._load_teams()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Select Your Team")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #B9F2FF;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Your team is locked for this career. Staff and car "
            "progression happen between races."
        )
        subtitle.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(subtitle)

        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(6)
        self.teams_table.setHorizontalHeaderLabels([
            "Team",
            "Tier",
            "Budget",
            "Drivers",
            "Staff",
            "HQ",
        ])
        self.teams_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.teams_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.teams_table.doubleClicked.connect(self._select_team)
        header = self.teams_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.teams_table)

        buttons = QHBoxLayout()
        select_btn = QPushButton("Confirm Team")
        select_btn.clicked.connect(self._select_team)
        buttons.addWidget(select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _load_teams(self):
        teams = self.db.get_teams_by_discipline(self.discipline)
        self.teams_table.setRowCount(len(teams))

        for row, team in enumerate(teams):
            drivers = self.db.get_drivers_by_team(team.id)
            try:
                staff = self.db.get_staff_by_team(team.id)
            except Exception:
                staff = []

            team_item = QTableWidgetItem(team.name)
            team_item.setData(Qt.ItemDataRole.UserRole, team)
            self.teams_table.setItem(row, 0, team_item)
            self.teams_table.setItem(row, 1, QTableWidgetItem(_player_label(team.tier)))
            self.teams_table.setItem(row, 2, QTableWidgetItem(f"EUR {team.budget:,.0f}"))
            self.teams_table.setItem(row, 3, QTableWidgetItem(str(len(drivers))))
            self.teams_table.setItem(row, 4, QTableWidgetItem(str(len(staff))))
            self.teams_table.setItem(row, 5, QTableWidgetItem(team.headquarters or "-"))

        if teams:
            self.teams_table.selectRow(0)

    def _select_team(self):
        row = self.teams_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Team Selected", "Please select a team.")
            return

        team_item = self.teams_table.item(row, 0)
        if team_item is None:
            QMessageBox.warning(self, "Selection Error", "Could not read selected team.")
            return

        self.selected_team = team_item.data(Qt.ItemDataRole.UserRole)
        if self.selected_team is None:
            QMessageBox.warning(self, "Selection Error", "Could not resolve selected team.")
            return
        self.accept()


class CareerWindow(QMainWindow):
    """Dedicated career HQ screen shown between races."""

    return_to_menu = pyqtSignal()
    start_race_signal = pyqtSignal(dict)

    def __init__(self, championship, parent=None):
        super().__init__(parent)
        self.championship = championship
        self.db = DatabaseManager()
        self.championship_service = ChampionshipService(self.db)
        self.player_id = PLAYER_ID

        self.owned_team = None
        self.selected_driver = None
        self.next_race = None

        self.setWindowTitle(f"Career HQ: {self.championship.name}")
        self.resize(1400, 900)

        self._setup_ui()
        self._resolve_team_ownership()
        self.load_data()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self.header_label = QLabel()
        self.header_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #B9F2FF;")
        layout.addWidget(self.header_label)

        self.subheader_label = QLabel()
        self.subheader_label.setStyleSheet("color: #DD2D4A; font-size: 13px;")
        layout.addWidget(self.subheader_label)

        top_actions = QHBoxLayout()
        self.start_next_btn = QPushButton("Start Next Race")
        self.start_next_btn.clicked.connect(self.start_next_race)
        top_actions.addWidget(self.start_next_btn)

        refresh_btn = QPushButton("Refresh HQ")
        refresh_btn.clicked.connect(self.load_data)
        top_actions.addWidget(refresh_btn)

        back_btn = QPushButton("Return to Menu")
        back_btn.clicked.connect(self._on_return_to_menu)
        top_actions.addWidget(back_btn)

        top_actions.addStretch()
        layout.addLayout(top_actions)

        content = QHBoxLayout()

        left_col = QVBoxLayout()
        self.team_group = self._create_team_group()
        self.driver_group = self._create_driver_group()
        self.staff_group = self._create_staff_group()
        left_col.addWidget(self.team_group)
        left_col.addWidget(self.driver_group)
        left_col.addWidget(self.staff_group)

        right_col = QVBoxLayout()
        self.car_group = self._create_car_group()
        self.schedule_group = self._create_schedule_group()
        self.standings_group = self._create_standings_group()
        right_col.addWidget(self.car_group)
        right_col.addWidget(self.schedule_group)
        right_col.addWidget(self.standings_group)

        content.addLayout(left_col, 1)
        content.addLayout(right_col, 1)
        layout.addLayout(content)

    def _create_team_group(self) -> QGroupBox:
        group = QGroupBox("Team Overview")
        v = QVBoxLayout(group)
        self.team_name_label = QLabel("Team: -")
        self.team_budget_label = QLabel("Budget: -")
        self.team_tier_label = QLabel("Tier: -")
        self.team_hq_label = QLabel("HQ: -")
        v.addWidget(self.team_name_label)
        v.addWidget(self.team_budget_label)
        v.addWidget(self.team_tier_label)
        v.addWidget(self.team_hq_label)
        return group

    def _create_driver_group(self) -> QGroupBox:
        group = QGroupBox("Drivers")
        v = QVBoxLayout(group)
        v.addWidget(QLabel("Race Driver:"))
        self.driver_combo = QComboBox()
        self.driver_combo.currentIndexChanged.connect(self._on_driver_changed)
        v.addWidget(self.driver_combo)
        self.driver_summary_label = QLabel("-")
        self.driver_summary_label.setWordWrap(True)
        v.addWidget(self.driver_summary_label)
        return group

    def _create_staff_group(self) -> QGroupBox:
        group = QGroupBox("Staff")
        v = QVBoxLayout(group)
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(3)
        self.staff_table.setHorizontalHeaderLabels(["Name", "Role", "Rating"])
        sh = self.staff_table.horizontalHeader()
        if sh is not None:
            sh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            sh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.staff_table.setMaximumHeight(210)
        v.addWidget(self.staff_table)
        return group

    def _create_car_group(self) -> QGroupBox:
        group = QGroupBox("Car and Facilities")
        v = QVBoxLayout(group)
        self.car_ops_label = QLabel("Operations Rating: -")
        self.car_strategy_label = QLabel("Strategy Profile: -")
        self.facility_label = QLabel("Facilities: -")
        self.facility_label.setWordWrap(True)
        v.addWidget(self.car_ops_label)
        v.addWidget(self.car_strategy_label)
        v.addWidget(self.facility_label)
        return group

    def _create_schedule_group(self) -> QGroupBox:
        group = QGroupBox("Schedule")
        v = QVBoxLayout(group)
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels(["Round", "Track", "Date", "Status"])
        sh = self.schedule_table.horizontalHeader()
        if sh is not None:
            sh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setMaximumHeight(240)
        v.addWidget(self.schedule_table)
        return group

    def _create_standings_group(self) -> QGroupBox:
        group = QGroupBox("Standings")
        v = QVBoxLayout(group)
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(4)
        self.standings_table.setHorizontalHeaderLabels(["Pos", "Driver", "Team", "Pts"])
        sh = self.standings_table.horizontalHeader()
        if sh is not None:
            sh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            sh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        v.addWidget(self.standings_table)
        return group

    def _resolve_team_ownership(self):
        team_id = self.db.get_player_team_id(self.player_id)
        team = self.db.get_team(team_id) if team_id else None

        if team and team.discipline == self.championship.discipline:
            self.owned_team = team
            return

        dialog = CareerTeamSelectionDialog(self.db, self.championship.discipline, self)
        if dialog.exec() != QDialog.DialogCode.Accepted or dialog.selected_team is None:
            QMessageBox.warning(
                self,
                "Career Team Required",
                "Career mode requires selecting a team first.",
            )
            self._on_return_to_menu()
            return

        self.owned_team = dialog.selected_team
        self.db.assign_team_owner(self.owned_team.id, self.player_id)

    def load_data(self):
        if not self.owned_team:
            return

        self.owned_team = self.db.get_team(self.owned_team.id)
        if not self.owned_team:
            return
        self._load_team_panel()
        self._load_drivers_panel()
        self._load_staff_panel()
        self._load_car_panel()
        self._load_schedule_panel()
        self._load_standings_panel()

    def _load_team_panel(self):
        if not self.owned_team:
            return
        self.header_label.setText(f"Career HQ - {self.championship.name}")
        self.subheader_label.setText(
            f"Discipline: {_player_label(self.championship.discipline)} | "
            f"Season {self.championship.current_season}"
        )

        self.team_name_label.setText(f"Team: {self.owned_team.name}")
        self.team_budget_label.setText(f"Budget: EUR {self.owned_team.budget:,.0f}")
        self.team_tier_label.setText(f"Tier: {_player_label(self.owned_team.tier)}")
        self.team_hq_label.setText(f"HQ: {self.owned_team.headquarters or '-'}")

    def _load_drivers_panel(self):
        if not self.owned_team:
            return
        drivers = self.db.get_drivers_by_team(self.owned_team.id)

        self.driver_combo.clear()
        for driver in drivers:
            self.driver_combo.addItem(driver.name, driver)

        if drivers:
            self.selected_driver = drivers[0]
            self.driver_combo.setCurrentIndex(0)
            self._render_driver_summary(self.selected_driver)
        else:
            self.selected_driver = None
            self.driver_summary_label.setText("No contracted drivers for this team.")

    def _on_driver_changed(self):
        drv = self.driver_combo.currentData()
        self.selected_driver = drv
        if drv:
            self._render_driver_summary(drv)

    def _render_driver_summary(self, drv):
        self.driver_summary_label.setText(
            f"Speed {drv.speed:.0f} | Racecraft {drv.racecraft:.0f} | "
            f"Consistency {drv.consistency:.0f}"
        )

    def _load_staff_panel(self):
        if not self.owned_team:
            return
        try:
            staff = self.db.get_staff_by_team(self.owned_team.id)
        except Exception:
            staff = []

        self.staff_table.setRowCount(len(staff))
        for row, member in enumerate(staff):
            self.staff_table.setItem(row, 0, QTableWidgetItem(str(member.name)))
            self.staff_table.setItem(
                row,
                1,
                QTableWidgetItem(_player_label(member.role)),
            )
            self.staff_table.setItem(row, 2, QTableWidgetItem(f"{float(member.rating):.1f}"))

    def _load_car_panel(self):
        if not self.owned_team:
            return
        self.car_ops_label.setText(
            f"Operations Rating: {self.owned_team.operations_rating:.1f}"
        )
        self.car_strategy_label.setText(
            "Strategy Profile: "
            f"{_player_label(self.owned_team.strategy_profile)}"
        )

        facilities = self.db.get_facility_upgrades(self.owned_team.id)
        if not facilities:
            self.facility_label.setText("Facilities: Baseline package")
            return

        parts = [f"{f['facility_name']} L{f['level']}" for f in facilities]
        self.facility_label.setText("Facilities: " + ", ".join(parts))

    def _load_schedule_panel(self):
        calendar = self.championship_service.get_championship_calendar(
            self.championship.id,
            self.championship.current_season,
        )

        self.schedule_table.setRowCount(len(calendar))
        self.next_race = None

        for row, race in enumerate(calendar):
            self.schedule_table.setItem(row, 0, QTableWidgetItem(f"R{race['round_number']}"))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(str(race['track_name'])))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(str(race['race_date'])))
            self.schedule_table.setItem(row, 3, QTableWidgetItem(_player_label(race['status'])))

            if self.next_race is None and race['status'] == 'scheduled':
                self.next_race = race

        self.start_next_btn.setEnabled(
            self.next_race is not None and self.selected_driver is not None
        )
        if self.next_race is None:
            self.start_next_btn.setText("Season Complete")
        else:
            self.start_next_btn.setText("Start Next Race")

    def _load_standings_panel(self):
        standings = self.championship_service.recalculate_standings(
            self.championship.id,
            self.championship.current_season,
        )

        self.standings_table.setRowCount(len(standings))
        for row, entry in enumerate(standings):
            self.standings_table.setItem(row, 0, QTableWidgetItem(str(entry.position)))
            self.standings_table.setItem(row, 1, QTableWidgetItem(str(entry.driver_name)))
            self.standings_table.setItem(row, 2, QTableWidgetItem(str(entry.team_name)))
            self.standings_table.setItem(row, 3, QTableWidgetItem(str(entry.total_points)))

    def start_next_race(self):
        if not self.next_race:
            QMessageBox.information(self, "Season Complete", "No scheduled races remain.")
            return

        if not self.selected_driver:
            QMessageBox.warning(self, "No Driver", "Select a contracted team driver first.")
            return

        race_id = int(self.next_race['race_id'])
        race_obj = self.db.get_race(race_id)
        if race_obj is None:
            QMessageBox.warning(self, "Race Error", "Could not load next race details.")
            return

        success, error_msg = self.championship_service.update_race_lifecycle_status(
            race_id,
            "in-progress",
        )
        if not success:
            QMessageBox.warning(
                self,
                "Status Update Failed",
                f"Could not update race status: {error_msg}",
            )
            return

        config = {
            "mode": "career",
            "personnel_transfers_enabled": True,
            "championship_id": self.championship.id,
            "race_id": race_obj.id,
            "track_id": race_obj.track_id,
            "driver": self.selected_driver,
            "team": self.owned_team,
            "discipline": self.championship.discipline,
            "weather": race_obj.weather_conditions,
            "tire_strategy": "Medium",
            "laps": race_obj.laps,
        }

        self.start_race_signal.emit(config)

    def _on_return_to_menu(self):
        self.return_to_menu.emit()
