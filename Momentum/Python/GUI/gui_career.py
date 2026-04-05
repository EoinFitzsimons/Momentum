"""
Career Mode GUI for Momentum Racing Simulator.

Implements a dedicated career HQ flow:
- Select championship
- Select and lock player team ownership once
- Manage team state between races
- Start the next scheduled race from HQ
"""

import random

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
from GUI.gui_navbar import NavigationBar
from GUI.gui_championship import ChampionshipSelectionDialog, _player_label


PLAYER_ID = "local_player"
BUDGET_WARNING_TITLE = "Insufficient Budget"
SEASON_COMPLETE_TEXT = "Season Complete"

FACILITY_OPTIONS = [
    ("Driver Academy", "driver_academy"),
    ("Simulation Lab", "simulation_lab"),
    ("Data Center", "data_center"),
    ("Marketing Suite", "marketing_suite"),
]

FEINT_BUTTON_BORDER_STYLE = "QPushButton { border: 1px solid rgba(185,242,255,0.24); }"
LOGO_STYLE = "font-size: 26px; font-weight: 700; color: #B9F2FF; letter-spacing: 2px;"


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
        self.setStyleSheet(FEINT_BUTTON_BORDER_STYLE)

        logo = QLabel("MOMENTUM")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(LOGO_STYLE)
        layout.addWidget(logo)

        self.navbar = NavigationBar(self, db_provider=lambda: self.db, title="Career Team Select")
        layout.addWidget(self.navbar)

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
        self.setStyleSheet(FEINT_BUTTON_BORDER_STYLE)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        logo = QLabel("MOMENTUM")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(LOGO_STYLE)
        layout.addWidget(logo)

        self.navbar = NavigationBar(self, db_provider=lambda: self.db, title="Career HQ")
        layout.addWidget(self.navbar)

        self.header_label = QLabel()
        self.header_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #B9F2FF;")
        layout.addWidget(self.header_label)

        self.subheader_label = QLabel()
        self.subheader_label.setStyleSheet("color: #DD2D4A; font-size: 13px;")
        layout.addWidget(self.subheader_label)

        self.kpi_banner_label = QLabel("Budget: - | Team Quality: - | Next Race: - | Drivers: - | Staff: -")
        self.kpi_banner_label.setWordWrap(True)
        layout.addWidget(self.kpi_banner_label)

        top_actions = QHBoxLayout()
        self.start_next_btn = QPushButton("Start Next Race")
        self.start_next_btn.clicked.connect(self.start_next_race)
        top_actions.addWidget(self.start_next_btn)

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
        self.hq_management_group = self._create_hq_management_group()
        self.schedule_group = self._create_schedule_group()
        self.standings_group = self._create_standings_group()
        right_col.addWidget(self.car_group)
        right_col.addWidget(self.hq_management_group)
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
        self.team_quality_label = QLabel("Team Quality: -")
        self.team_attractiveness_label = QLabel("Attractiveness: -")
        v.addWidget(self.team_name_label)
        v.addWidget(self.team_budget_label)
        v.addWidget(self.team_tier_label)
        v.addWidget(self.team_hq_label)
        v.addWidget(self.team_quality_label)
        v.addWidget(self.team_attractiveness_label)
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

    def _create_hq_management_group(self) -> QGroupBox:
        group = QGroupBox("HQ Management")
        v = QVBoxLayout(group)

        self.hq_state_label = QLabel("Run actions to grow quality, attractiveness, and budget.")
        self.hq_state_label.setWordWrap(True)
        v.addWidget(self.hq_state_label)

        self.marketing_btn = QPushButton("Run Marketing Campaign (-EUR 250,000)")
        self.marketing_btn.clicked.connect(self._run_marketing_campaign)
        v.addWidget(self.marketing_btn)

        self.driver_dev_btn = QPushButton("Driver Development (-EUR 180,000)")
        self.driver_dev_btn.clicked.connect(self._run_driver_development)
        v.addWidget(self.driver_dev_btn)

        self.staff_dev_btn = QPushButton("Staff Development (-EUR 220,000)")
        self.staff_dev_btn.clicked.connect(self._run_staff_development)
        v.addWidget(self.staff_dev_btn)

        facility_row = QHBoxLayout()
        self.facility_combo = QComboBox()
        for label, value in FACILITY_OPTIONS:
            self.facility_combo.addItem(label, value)
        facility_row.addWidget(self.facility_combo)

        self.facility_btn = QPushButton("Upgrade Facility (-EUR 400,000)")
        self.facility_btn.clicked.connect(self._run_facility_upgrade)
        facility_row.addWidget(self.facility_btn)
        v.addLayout(facility_row)

        self.hq_action_result_label = QLabel("")
        self.hq_action_result_label.setWordWrap(True)
        v.addWidget(self.hq_action_result_label)

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

        self._ensure_owned_team_staff()

        self._apply_pending_race_income()
        self.owned_team = self.db.get_team(self.owned_team.id)
        if not self.owned_team:
            return

        self._load_team_panel()
        self._load_drivers_panel()
        self._load_staff_panel()
        self._load_car_panel()
        self._load_schedule_panel()
        self._load_standings_panel()
        self._update_kpi_banner()

    def _update_kpi_banner(self):
        if not self.owned_team:
            self.kpi_banner_label.setText("Budget: - | Team Quality: - | Next Race: - | Drivers: - | Staff: -")
            return

        quality_score, _ = self._compute_team_scores()
        drivers = self.db.get_drivers_by_team(self.owned_team.id)
        try:
            staff = self.db.get_staff_by_team(self.owned_team.id)
        except Exception:
            staff = []

        next_race_text = SEASON_COMPLETE_TEXT
        if self.next_race:
            next_race_text = f"R{self.next_race.get('round_number', '?')} {self.next_race.get('track_name', '-') }"

        self.kpi_banner_label.setText(
            f"Budget: EUR {float(self.owned_team.budget or 0.0):,.0f} | "
            f"Team Quality: {quality_score:.1f}/100 | "
            f"Next Race: {next_race_text} | "
            f"Drivers: {len(drivers)} | Staff: {len(staff)}"
        )

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

        quality_score, attractiveness_score = self._compute_team_scores()
        self.team_quality_label.setText(f"Team Quality: {quality_score:.1f} / 100")
        self.team_attractiveness_label.setText(
            f"Attractiveness (for signings): {attractiveness_score:.1f} / 100"
        )
        self.hq_state_label.setText(
            "Higher quality improves race performance. Higher attractiveness helps future "
            "driver/staff recruitment strength."
        )

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
            self.start_next_btn.setText(SEASON_COMPLETE_TEXT)
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
            QMessageBox.information(self, SEASON_COMPLETE_TEXT, "No scheduled races remain.")
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

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
        return max(low, min(high, value))

    def _compute_team_scores(self) -> tuple[float, float]:
        if not self.owned_team:
            return 0.0, 0.0

        facilities = self.db.get_facility_upgrades(self.owned_team.id)
        facility_levels = sum(int(f.get("level", 0) or 0) for f in facilities)
        facility_score = min(22.0, facility_levels * 2.2)

        try:
            staff = self.db.get_staff_by_team(self.owned_team.id)
        except Exception:
            staff = []
        staff_avg = (sum(float(s.rating) for s in staff) / len(staff)) if staff else 50.0
        staff_score = min(18.0, max(0.0, (staff_avg - 50.0) * 0.6))

        ops = float(getattr(self.owned_team, "operations_rating", 50.0) or 50.0)
        quality_score = self._clamp((ops * 0.62) + facility_score + staff_score)

        budget = float(getattr(self.owned_team, "budget", 0.0) or 0.0)
        budget_score = min(28.0, (budget / 6_000_000.0) * 28.0)

        marketing_levels = sum(
            int(f.get("level", 0) or 0)
            for f in facilities
            if "marketing" in str(f.get("facility_name", "")).lower()
        )
        brand_score = min(10.0, marketing_levels * 2.0)

        attractiveness_score = self._clamp((quality_score * 0.65) + budget_score + brand_score)
        return quality_score, attractiveness_score

    def _apply_budget_delta(self, amount: float, category: str, description: str) -> bool:
        if not self.owned_team:
            return False

        current_budget = float(self.owned_team.budget or 0.0)
        new_budget = current_budget + float(amount)
        if new_budget < 0:
            return False

        self.owned_team.budget = new_budget
        updated = self.db.update_team(self.owned_team.id, self.owned_team)
        if not updated:
            return False

        try:
            self.db.add_budget_transaction(self.owned_team.id, category, float(amount), description)
        except Exception:
            pass

        refreshed = self.db.get_team(self.owned_team.id)
        if refreshed is not None:
            self.owned_team = refreshed
        return True

    def _apply_pending_race_income(self):
        if not self.owned_team:
            return

        calendar = self.championship_service.get_championship_calendar(
            self.championship.id,
            self.championship.current_season,
        )
        transactions = self.db.get_budget_transactions(self.owned_team.id)
        existing_refs = {
            str(t.get("description", ""))
            for t in transactions
            if t.get("category") == "race_income"
        }

        tier = str(getattr(self.owned_team, "tier", "TIER_2") or "TIER_2").upper()
        base_income_map = {
            "TOP_TIER": 520000,
            "TIER_1": 460000,
            "TIER_2": 330000,
            "TIER_3": 240000,
        }
        base_income = int(base_income_map.get(tier, 330000))

        quality_score, _ = self._compute_team_scores()
        quality_multiplier = 0.85 + ((quality_score / 100.0) * 0.45)

        for race in calendar:
            if race.get("status") != "completed":
                continue
            race_id = int(race.get("race_id", 0) or 0)
            if race_id <= 0:
                continue
            marker = f"race_income_ref:{race_id}"
            if any(marker in desc for desc in existing_refs):
                continue

            payout = int(base_income * quality_multiplier)
            applied = self._apply_budget_delta(
                payout,
                "race_income",
                f"Race participation income R{race.get('round_number', '?')} ({marker})",
            )
            if applied:
                existing_refs.add(marker)

    def _run_marketing_campaign(self):
        if not self.owned_team:
            return

        cost = 250000
        applied = self._apply_budget_delta(
            -cost,
            "marketing_cost",
            "Marketing campaign spend",
        )
        if not applied:
            QMessageBox.warning(self, BUDGET_WARNING_TITLE, "Not enough budget for marketing campaign.")
            return

        quality_score, _ = self._compute_team_scores()
        revenue = int(random.uniform(0.6, 1.9) * cost * (0.65 + quality_score / 200.0))
        self._apply_budget_delta(
            revenue,
            "marketing_revenue",
            "Marketing campaign return",
        )
        net = revenue - cost
        self.hq_action_result_label.setText(
            f"Marketing complete. Revenue EUR {revenue:,.0f} (net EUR {net:,.0f})."
        )
        self.load_data()

    def _run_driver_development(self):
        if not self.owned_team:
            return

        if not self.selected_driver:
            QMessageBox.warning(self, "No Driver", "Select a race driver before running development.")
            return

        cost = 180000
        applied = self._apply_budget_delta(
            -cost,
            "driver_development",
            f"Driver development for {self.selected_driver.name}",
        )
        if not applied:
            QMessageBox.warning(self, BUDGET_WARNING_TITLE, "Not enough budget for driver development.")
            return

        speed_gain = random.uniform(0.6, 1.8)
        racecraft_gain = random.uniform(0.5, 1.4)
        consistency_gain = random.uniform(0.4, 1.2)

        with self.db.get_connection() as conn:
            conn.execute(
                """
                UPDATE drivers
                SET speed = MIN(100, speed + ?),
                    racecraft = MIN(100, racecraft + ?),
                    consistency = MIN(100, consistency + ?)
                WHERE id = ?
                """,
                (speed_gain, racecraft_gain, consistency_gain, self.selected_driver.id)
            )

        self.hq_action_result_label.setText(
            f"Driver development complete: +{speed_gain:.1f} speed, +{racecraft_gain:.1f} racecraft, "
            f"+{consistency_gain:.1f} consistency."
        )
        self.load_data()

    def _run_staff_development(self):
        if not self.owned_team:
            return

        cost = 220000
        applied = self._apply_budget_delta(
            -cost,
            "staff_development",
            "Staff development program",
        )
        if not applied:
            QMessageBox.warning(self, BUDGET_WARNING_TITLE, "Not enough budget for staff development.")
            return

        try:
            staff = self.db.get_staff_by_team(self.owned_team.id)
        except Exception:
            staff = []

        if not staff:
            self.hq_action_result_label.setText("No staff found. Program completed with no effect.")
            self.load_data()
            return

        boosted = 0
        with self.db.get_connection() as conn:
            for member in staff[: min(8, len(staff))]:
                gain = random.uniform(0.5, 1.6)
                conn.execute(
                    "UPDATE staff_members SET rating = MIN(100, rating + ?) WHERE id = ?",
                    (gain, member.id),
                )
                boosted += 1

        self.hq_action_result_label.setText(
            f"Staff development complete: improved {boosted} staff members."
        )
        self.load_data()

    def _run_facility_upgrade(self):
        if not self.owned_team:
            return

        facility_label = str(self.facility_combo.currentText() or "Facility")
        facility_name = str(self.facility_combo.currentData() or "facility")
        cost = 400000

        applied = self._apply_budget_delta(
            -cost,
            "facility_upgrade",
            f"Facility upgrade: {facility_label}",
        )
        if not applied:
            QMessageBox.warning(self, BUDGET_WARNING_TITLE, "Not enough budget for facility upgrade.")
            return

        self.db.upsert_facility_upgrade(self.owned_team.id, facility_name, float(cost))
        self.owned_team.operations_rating = self._clamp(
            float(getattr(self.owned_team, "operations_rating", 50.0) or 50.0) + random.uniform(0.8, 2.0)
        )
        self.db.update_team(self.owned_team.id, self.owned_team)

        self.hq_action_result_label.setText(
            f"Facility upgraded: {facility_label}. Team operations improved."
        )
        self.load_data()

    def _ensure_owned_team_staff(self):
        """Backfill a minimal staff crew for the owned team when unstaffed."""
        if not self.owned_team:
            return

        try:
            existing_staff = self.db.get_staff_by_team(self.owned_team.id)
        except Exception:
            existing_staff = []
        if existing_staff:
            return

        assigned = 0
        start_season = int(getattr(self.championship, "current_season", 1) or 1)

        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, rating
                FROM staff_members
                WHERE current_team_id IS NULL
                ORDER BY rating DESC, id ASC
                LIMIT 3
                """
            ).fetchall()

            for row in rows:
                staff_id = int(row[0])
                rating = float(row[1] or 50.0)
                annual_salary = round(45_000 + (rating * 2_750), 2)
                contract_length = 2
                conn.execute(
                    """
                    UPDATE staff_members
                    SET current_team_id = ?,
                        annual_salary = ?,
                        contract_length = ?,
                        contract_start_season = ?,
                        contract_end_season = ?
                    WHERE id = ?
                    """,
                    (
                        self.owned_team.id,
                        annual_salary,
                        contract_length,
                        start_season,
                        start_season + contract_length - 1,
                        staff_id,
                    ),
                )
                assigned += 1

        if assigned > 0 and not self.hq_action_result_label.text():
            self.hq_action_result_label.setText(
                f"Auto-staffed HQ with {assigned} core staff members from the market pool."
            )
