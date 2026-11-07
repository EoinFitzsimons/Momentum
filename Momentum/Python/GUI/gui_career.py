"""
Career Mode GUI for Momentum Racing Simulator.

Implements a dedicated career HQ flow:
- Select championship
- Select and lock player team ownership once
- Manage team state between races
- Start the next scheduled race from HQ
"""

import random
from datetime import datetime, timedelta
from types import SimpleNamespace

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QHeaderView,
)
from GUI.themed_messagebox import information, warning

from database.database_manager import DatabaseManager
from services.championship_service import ChampionshipService
from services.career_season_service import CareerSeasonService
from services.tier_service import normalise_tier
from services.upgrade_service import UpgradeService
from GUI.gui_navbar import NavigationBar
from GUI.gui_championship import ChampionshipSelectionDialog, _player_label


PLAYER_ID = "local_player"
WORLD_START_DATE = "2026-01-01"
BUDGET_WARNING_TITLE = "Insufficient Budget"
SEASON_COMPLETE_TEXT = "Season Complete"
NO_SELECTION_TITLE = "No Selection"
SELECTION_ERROR_TITLE = "Selection Error"

FACILITY_OPTIONS = [
    ("Driver Academy", "driver_academy"),
    ("Simulation Lab", "simulation_lab"),
    ("Data Center", "data_center"),
    ("Marketing Suite", "marketing_suite"),
]

FEINT_BUTTON_BORDER_STYLE = "QPushButton { border: 1px solid rgba(185,242,255,0.24); }"


def _style_table(table: QTableWidget, min_height: int, max_height: int | None = None) -> None:
    """Apply the shared card-table look: no row numbers, no grid, zebra rows."""
    vh = table.verticalHeader()
    if vh is not None:
        vh.setVisible(False)
    table.setShowGrid(False)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setMinimumHeight(min_height)
    if max_height is not None:
        table.setMaximumHeight(max_height)

LOGO_STYLE = "font-size: 26px; font-weight: 700; color: #B9F2FF; letter-spacing: 2px;"

CAREER_DISCIPLINE_RACE_COUNTS = {
    "SINGLE_SEATER": 24,
    "PRODUCTION_TOURING": 12,
    "URBAN_STREET": 10,
    "DRAG_ACCELERATION": 14,
    "SPRINT_RALLYCROSS": 12,
    "ENDURANCE": 8,
}


class CareerSelectionDialog(ChampionshipSelectionDialog):
    """Career-specific entry dialog backed by dedicated career world tables."""

    def __init__(self, db, parent=None):
        self._selected_discipline = None
        super().__init__(db, parent)
        self.setWindowTitle("Select Career")
        self._ensure_career_tables()
        self._replace_create_button_text()
        self._select_discipline("SINGLE_SEATER")

    def setup_ui(self):
        """Build the career-world entry screen instead of a generic table."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        self.setStyleSheet(
            """
            QDialog { background-color: #202629; }
            QLabel { color: #EAF8FA; }
            QGroupBox { border: 1px solid #405057; border-radius: 8px; margin-top: 10px; padding: 12px; }
            QGroupBox::title { color: #7EE6E0; padding: 0 6px; }
            QPushButton { background-color: #29343A; color: #EAF8FA; border: 1px solid #4B626A; border-radius: 6px; padding: 10px; }
            QPushButton:hover { background-color: #34464D; border-color: #7EE6E0; }
            QPushButton:checked { background-color: #7EE6E0; color: #172023; border-color: #7EE6E0; }
            QTableWidget { background-color: #172023; color: #EAF8FA; gridline-color: #34464D; border: 1px solid #405057; }
            QHeaderView::section { background-color: #29343A; color: #B7D9DB; padding: 7px; border: none; }
            """
        )

        logo = QLabel("MOMENTUM  /  CAREER WORLD")
        logo.setStyleSheet("font-size: 24px; font-weight: 700; color: #7EE6E0; letter-spacing: 2px;")
        layout.addWidget(logo)

        self.career_title = QLabel("Build your racing life")
        self.career_title.setStyleSheet("font-size: 30px; font-weight: 700; color: #F2FBFB;")
        layout.addWidget(self.career_title)

        self.career_subtitle = QLabel(
            "Choose the world you want to inhabit. Your discipline shapes the calendar, the teams, the cars, and the way your career develops."
        )
        self.career_subtitle.setWordWrap(True)
        self.career_subtitle.setStyleSheet("color: #A8C1C4; font-size: 14px;")
        layout.addWidget(self.career_subtitle)

        identity_row = QHBoxLayout()
        self.profile_summary = QLabel("No career save yet")
        self.profile_summary.setStyleSheet(
            "background-color: #29343A; border-left: 4px solid #DD2D4A; padding: 12px; font-size: 14px;"
        )
        self.profile_summary.setWordWrap(True)
        identity_row.addWidget(self.profile_summary, 1)
        self.create_save_btn = QPushButton("Create / Reset World")
        self.create_save_btn.clicked.connect(self.create_championship)
        self.create_save_btn.setMinimumHeight(48)
        identity_row.addWidget(self.create_save_btn)
        layout.addLayout(identity_row)

        discipline_group = QGroupBox("Choose Your Motorsport World")
        discipline_layout = QGridLayout(discipline_group)
        discipline_layout.setSpacing(8)
        self.discipline_buttons = []
        discipline_details = {
            "SINGLE_SEATER": ("OPEN WHEEL", "Precision, aero, politics", "24 rounds"),
            "PRODUCTION_TOURING": ("TOURING", "Close packs, contact, budgets", "12 rounds"),
            "URBAN_STREET": ("STREET", "Style, risk, city circuits", "10 rounds"),
            "DRAG_ACCELERATION": ("DRAG", "Launches, power, pressure", "14 rounds"),
            "SPRINT_RALLYCROSS": ("RALLYCROSS", "Mixed surfaces, short shocks", "12 rounds"),
            "ENDURANCE": ("ENDURANCE", "Stints, reliability, patience", "8 rounds"),
        }
        for index, (discipline, details) in enumerate(discipline_details.items()):
            button = QPushButton(f"{details[0]}\n{details[1]}\n{details[2]}")
            button.setCheckable(True)
            button.setMinimumHeight(78)
            button.setAccessibleName(f"Choose {_player_label(discipline)} career")
            button.clicked.connect(
                lambda checked, value=discipline: self._select_discipline(value)
            )
            self.discipline_buttons.append((discipline, button))
            discipline_layout.addWidget(button, index // 3, index % 3)
        layout.addWidget(discipline_group)

        board_group = QGroupBox("Career Board")
        board_layout = QVBoxLayout(board_group)
        self.board_heading = QLabel("Select a discipline to see its active series")
        self.board_heading.setStyleSheet("font-size: 16px; font-weight: 700; color: #7EE6E0;")
        board_layout.addWidget(self.board_heading)
        self.championships_table = QTableWidget()
        self.championships_table.setColumnCount(5)
        self.championships_table.setHorizontalHeaderLabels(
            ["Series", "World", "Season", "Calendar", "Status"]
        )
        self.championships_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.championships_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.championships_table.doubleClicked.connect(self.select_championship)
        ch = self.championships_table.horizontalHeader()
        if ch is not None:
            ch.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        _style_table(self.championships_table, 200)
        board_layout.addWidget(self.championships_table)
        layout.addWidget(board_group, 1)

        actions = QHBoxLayout()
        self.select_btn = QPushButton("Enter Selected World")
        self.select_btn.clicked.connect(self.select_championship)
        self.select_btn.setMinimumHeight(46)
        actions.addWidget(self.select_btn)
        cancel_btn = QPushButton("Back")
        cancel_btn.clicked.connect(self.reject)
        actions.addWidget(cancel_btn)
        layout.addLayout(actions)

    def _select_discipline(self, discipline: str) -> None:
        self._selected_discipline = discipline
        for value, button in self.discipline_buttons:
            button.setChecked(value == discipline)
        self.board_heading.setText(
            f"{_player_label(discipline)} ecosystem · choose your starting series"
        )
        self.load_championships()

    def _load_profile_summary(self) -> None:
        profile = None
        try:
            with self.db.get_connection() as conn:
                profile = conn.execute(
                    "SELECT player_name, age, nationality, bio FROM career_player_profiles WHERE player_id = ?",
                    (PLAYER_ID,),
                ).fetchone()
        except Exception:
            profile = None
        if profile:
            self.profile_summary.setText(
                f"<b>{profile['player_name']}</b> · {profile['nationality']} · age {profile['age']}<br>"
                f"{profile['bio']}"
            )
        else:
            self.profile_summary.setText(
                "No career save yet. Create your profile to generate a living motorsport world."
            )

    def create_championship(self):
        """Create/reset career world and profile."""
        if self._create_or_reset_career_save():
            self.load_championships()

    def load_championships(self):
        """Load career series from dedicated career tables (not championships table)."""
        self._ensure_career_tables()
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                                SELECT id, name, discipline, tier, season_length, current_season, is_active
                FROM career_championships
                WHERE player_id = ?
                                    AND (? IS NULL OR discipline = ?)
                                ORDER BY discipline, tier, id
                """,
                                (PLAYER_ID, self._selected_discipline, self._selected_discipline),
            ).fetchall()

            self.championships_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                rowd = dict(row)
                self.championships_table.setItem(
                    i, 0, QTableWidgetItem(str(rowd["name"]))
                )
                self.championships_table.setItem(
                    i, 1, QTableWidgetItem(_player_label(rowd["discipline"]))
                )
                self.championships_table.setItem(
                    i, 2, QTableWidgetItem(str(rowd["current_season"]))
                )
                self.championships_table.setItem(
                    i, 3, QTableWidgetItem(f"{int(rowd['season_length'])} rounds")
                )
                status = (
                    "Active" if int(rowd.get("is_active", 1) or 1) == 1 else "Inactive"
                )
                self.championships_table.setItem(i, 4, QTableWidgetItem(status))

                item = self.championships_table.item(i, 0)
                if item is not None:
                    item.setData(Qt.ItemDataRole.UserRole, rowd)
            self._load_profile_summary()

    def _replace_create_button_text(self) -> None:
        for button in self.findChildren(QPushButton):
            if button.text().strip().lower() == "create new championship":
                button.setText("Create New Career Save")
                button.setToolTip("Reset to 1 Jan 2026 and create a new career profile")
            elif button.text().strip().lower() == "delete championship":
                button.setEnabled(False)
                button.setToolTip(
                    "Career championships cannot be deleted individually."
                )

    def select_championship(self):
        """Ensure a valid career world exists and return selected career series."""
        if not self._has_profile(PLAYER_ID):
            information(
                self,
                "Career Save Required",
                "Create a career save first.",
            )
            if not self._create_or_reset_career_save():
                return
            self.load_championships()

        row = self.championships_table.currentRow()
        if row < 0:
            warning(self, NO_SELECTION_TITLE, "Please select a career series.")
            return

        item = self.championships_table.item(row, 0)
        if item is None:
            warning(self, NO_SELECTION_TITLE, "Please select a valid career series.")
            return

        selected = item.data(Qt.ItemDataRole.UserRole)
        if not selected:
            warning(
                self, NO_SELECTION_TITLE, "Could not resolve selected career series."
            )
            return

        self.selected_championship = SimpleNamespace(
            id=int(selected["id"]),
            name=str(selected["name"]),
            discipline=str(selected["discipline"]),
            tier=str(selected["tier"]),
            current_season=int(selected.get("current_season", 1) or 1),
            season_length=int(selected.get("season_length", 1) or 1),
            is_career_series=True,
        )
        self.accept()

    def delete_championship(self):
        """Career championships are protected from per-series deletion."""
        information(
            self,
            "Deletion Disabled",
            "Career championships cannot be deleted individually. Use 'Create New Career Save' to reset career progression.",
        )

    def _create_or_reset_career_save(self) -> bool:
        profile_dialog = CareerProfileDialog(self)
        if profile_dialog.exec() != QDialog.DialogCode.Accepted:
            return False

        profile = profile_dialog.profile_payload()
        self._ensure_career_tables()
        self._upsert_profile(PLAYER_ID, profile)
        self._reset_world_to_start_date(PLAYER_ID, WORLD_START_DATE)
        information(
            self,
            "Career Save Created",
            "Career world reset to 1 Jan 2026. All championships are active and calendars were rebuilt.",
        )
        return True

    def _ensure_career_tables(self) -> None:
        with self.db.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS career_player_profiles (
                    player_id TEXT PRIMARY KEY,
                    player_name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    height_cm REAL NOT NULL,
                    nationality TEXT NOT NULL,
                    bio TEXT DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS career_world_state (
                    player_id TEXT PRIMARY KEY,
                    world_start_date TEXT NOT NULL,
                    initialized_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES career_player_profiles(player_id)
                );

                CREATE TABLE IF NOT EXISTS career_championships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    discipline TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    season_length INTEGER NOT NULL,
                    current_season INTEGER NOT NULL DEFAULT 1,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES career_player_profiles(player_id)
                );

                CREATE TABLE IF NOT EXISTS career_races (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT NOT NULL,
                    career_championship_id INTEGER NOT NULL,
                    track_id INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    round_number INTEGER NOT NULL,
                    race_date TEXT NOT NULL,
                    weather_conditions TEXT NOT NULL DEFAULT 'clear',
                    laps INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'scheduled',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (career_championship_id) REFERENCES career_championships(id),
                    FOREIGN KEY (track_id) REFERENCES tracks(id)
                );

                CREATE TABLE IF NOT EXISTS career_race_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT NOT NULL,
                    career_race_id INTEGER NOT NULL,
                    driver_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    points INTEGER NOT NULL DEFAULT 0,
                    fastest_lap INTEGER NOT NULL DEFAULT 0,
                    dnf_reason TEXT,
                    grid_position INTEGER,
                    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(career_race_id, driver_id),
                    FOREIGN KEY (career_race_id) REFERENCES career_races(id)
                );
                """
            )
            conn.commit()

    def _has_profile(self, player_id: str) -> bool:
        self._ensure_career_tables()
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT player_id FROM career_player_profiles WHERE player_id = ?",
                (player_id,),
            ).fetchone()
            return row is not None

    def _upsert_profile(self, player_id: str, profile: dict) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO career_player_profiles (player_id, player_name, age, height_cm, nationality, bio, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(player_id) DO UPDATE SET
                    player_name = excluded.player_name,
                    age = excluded.age,
                    height_cm = excluded.height_cm,
                    nationality = excluded.nationality,
                    bio = excluded.bio,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    player_id,
                    profile["player_name"],
                    profile["age"],
                    profile["height_cm"],
                    profile["nationality"],
                    profile["bio"],
                ),
            )
            conn.commit()

    def _reset_world_to_start_date(self, player_id: str, world_start_date: str) -> None:
        start_dt = datetime.strptime(world_start_date, "%Y-%m-%d")

        teams = self.db.get_all_teams()
        if not teams:
            raise ValueError(
                "No teams available. Seed team data before starting career mode."
            )

        # Build all active discipline+tier series from team universe.
        series_keys = sorted(
            {
                (
                    str(getattr(team, "discipline", "") or "").upper(),
                    normalise_tier(getattr(team, "tier", "TIER_2")),
                )
                for team in teams
                if str(getattr(team, "discipline", "") or "").strip()
            }
        )

        if not series_keys:
            raise ValueError("Could not derive any discipline/tier series from teams.")

        with self.db.get_connection() as conn:
            career_race_ids = [
                int(row[0])
                for row in conn.execute(
                    "SELECT id FROM career_races WHERE player_id = ?", (player_id,)
                ).fetchall()
            ]
            if career_race_ids:
                placeholders = ",".join("?" for _ in career_race_ids)
                conn.execute(
                    f"DELETE FROM career_race_results WHERE career_race_id IN ({placeholders})",
                    career_race_ids,
                )
            conn.execute("DELETE FROM career_races WHERE player_id = ?", (player_id,))
            conn.execute(
                "DELETE FROM career_championships WHERE player_id = ?", (player_id,)
            )
            # A new world starts with undeveloped cars for every team.
            conn.execute("DELETE FROM team_car_upgrades")
            conn.execute(
                "UPDATE team_ownership SET is_active = 0 WHERE player_id = ?",
                (player_id,),
            )
            conn.execute(
                """
                INSERT INTO career_world_state (player_id, world_start_date, initialized_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(player_id) DO UPDATE SET
                    world_start_date = excluded.world_start_date,
                    initialized_at = CURRENT_TIMESTAMP
                """,
                (player_id, world_start_date),
            )

            for discipline, tier in series_keys:
                season_length = int(CAREER_DISCIPLINE_RACE_COUNTS.get(discipline, 10))
                series_name = (
                    f"{_player_label(discipline)} {_player_label(tier)} Championship"
                )
                cursor = conn.execute(
                    """
                    INSERT INTO career_championships (player_id, name, discipline, tier, season_length, current_season, is_active)
                    VALUES (?, ?, ?, ?, ?, 1, 1)
                    """,
                    (player_id, series_name, discipline, tier, season_length),
                )
                if cursor.lastrowid is None:
                    raise RuntimeError("Failed to create career championship")
                career_championship_id = int(cursor.lastrowid)

                track_ids = self._resolve_track_ids_for_championship(
                    discipline, season_length
                )
                race_date = start_dt
                for round_number, track_id in enumerate(track_ids, start=1):
                    conn.execute(
                        """
                        INSERT INTO career_races (
                            player_id, career_championship_id, track_id, season, round_number,
                            race_date, weather_conditions, laps, status
                        )
                        VALUES (?, ?, ?, 1, ?, ?, 'clear', ?, 'scheduled')
                        """,
                        (
                            player_id,
                            career_championship_id,
                            int(track_id),
                            round_number,
                            race_date.strftime("%Y-%m-%d"),
                            ChampionshipService.default_laps_for_discipline(discipline),
                        ),
                    )
                    race_date += timedelta(days=14)

            conn.commit()

    def _resolve_track_ids_for_championship(
        self, discipline: str, season_length: int
    ) -> list[int]:
        tracks = self.db.get_tracks_by_discipline(discipline)
        if not tracks:
            tracks = self.db.get_all_tracks()
        if not tracks:
            raise ValueError("No tracks available to build a championship calendar.")

        base_ids = [int(track.id) for track in tracks]
        if len(base_ids) >= season_length:
            return base_ids[:season_length]

        expanded: list[int] = []
        while len(expanded) < season_length:
            expanded.extend(base_ids)
        return expanded[:season_length]


class CareerProfileDialog(QDialog):
    """Collect player profile details when creating a new career save."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Career Save")
        self.resize(520, 430)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Create Career Save")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #B9F2FF;")
        layout.addWidget(title)

        subtitle = QLabel(
            "This creates a persistent world starting on 1 Jan 2026 and resets career progression."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(subtitle)

        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Player name")
        form.addRow("Name", self.name_input)

        self.age_input = QSpinBox()
        self.age_input.setRange(16, 90)
        self.age_input.setValue(25)
        form.addRow("Age", self.age_input)

        self.height_input = QSpinBox()
        self.height_input.setRange(140, 230)
        self.height_input.setValue(178)
        self.height_input.setSuffix(" cm")
        form.addRow("Height", self.height_input)

        self.nationality_input = QLineEdit()
        self.nationality_input.setPlaceholderText("Nationality")
        form.addRow("Nationality", self.nationality_input)

        self.bio_input = QPlainTextEdit()
        self.bio_input.setPlaceholderText(
            "Short bio (optional). If empty, one is generated from age, height, and nationality."
        )
        self.bio_input.setMaximumHeight(120)
        form.addRow("Bio", self.bio_input)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        create_btn = QPushButton("Create Save")
        create_btn.clicked.connect(self._accept_if_valid)
        buttons.addWidget(create_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def _accept_if_valid(self) -> None:
        if not self.name_input.text().strip():
            warning(self, "Missing Name", "Please enter a player name.")
            return
        if not self.nationality_input.text().strip():
            warning(self, "Missing Nationality", "Please enter a nationality.")
            return
        self.accept()

    def profile_payload(self) -> dict:
        name = self.name_input.text().strip()
        nationality = self.nationality_input.text().strip()
        age = int(self.age_input.value())
        height_cm = int(self.height_input.value())
        bio = self.bio_input.toPlainText().strip()
        if not bio:
            bio = f"{age}-year-old {nationality} manager, {height_cm} cm tall."
        return {
            "player_name": name,
            "age": age,
            "height_cm": float(height_cm),
            "nationality": nationality,
            "bio": bio,
        }


class CareerTeamSelectionDialog(QDialog):
    """Select the player-owned team for this career save."""

    def __init__(
        self,
        db: DatabaseManager,
        discipline: str | None,
        tier: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.db = db
        self.discipline = discipline
        self.tier = normalise_tier(tier) if tier else None
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
        self.teams_table.setColumnCount(7)
        self.teams_table.setHorizontalHeaderLabels(
            [
                "Team",
                "Discipline",
                "Tier",
                "Budget",
                "Drivers",
                "Staff",
                "HQ",
            ]
        )
        self.teams_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.teams_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.teams_table.doubleClicked.connect(self._select_team)
        header = self.teams_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for col in range(1, 6):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        _style_table(self.teams_table, 240)
        _style_table(self.teams_table, 200)
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
        if self.discipline:
            teams = self.db.get_teams_by_discipline(self.discipline)
        else:
            teams = self.db.get_all_teams()

        if self.tier:
            teams = [
                team
                for team in teams
                if normalise_tier(getattr(team, "tier", "TIER_2")) == self.tier
            ]
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
            self.teams_table.setItem(
                row, 1, QTableWidgetItem(_player_label(team.discipline))
            )
            self.teams_table.setItem(row, 2, QTableWidgetItem(_player_label(team.tier)))
            self.teams_table.setItem(
                row, 3, QTableWidgetItem(f"EUR {team.budget:,.0f}")
            )
            self.teams_table.setItem(row, 4, QTableWidgetItem(str(len(drivers))))
            self.teams_table.setItem(row, 5, QTableWidgetItem(str(len(staff))))
            self.teams_table.setItem(row, 6, QTableWidgetItem(team.headquarters or "-"))

        if teams:
            self.teams_table.selectRow(0)

    def _select_team(self):
        row = self.teams_table.currentRow()
        if row < 0:
            warning(self, "No Team Selected", "Please select a team.")
            return

        team_item = self.teams_table.item(row, 0)
        if team_item is None:
            warning(self, SELECTION_ERROR_TITLE, "Could not read selected team.")
            return

        self.selected_team = team_item.data(Qt.ItemDataRole.UserRole)
        if self.selected_team is None:
            warning(self, SELECTION_ERROR_TITLE, "Could not resolve selected team.")
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
        self.career_season_service = CareerSeasonService(self.db)
        self.upgrade_service = UpgradeService(self.db)
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
        # The page is taller than a small window; scroll rather than clip it.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        central = QWidget()
        scroll.setWidget(central)
        self.setCentralWidget(scroll)
        self.setStyleSheet(FEINT_BUTTON_BORDER_STYLE)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        logo = QLabel("MOMENTUM")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(LOGO_STYLE)
        layout.addWidget(logo)

        self.navbar = NavigationBar(
            self, db_provider=lambda: self.db, title="Career HQ"
        )
        layout.addWidget(self.navbar)

        self.header_label = QLabel()
        self.header_label.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #B9F2FF;"
        )
        layout.addWidget(self.header_label)

        self.subheader_label = QLabel()
        self.subheader_label.setStyleSheet("color: #DD2D4A; font-size: 13px;")
        layout.addWidget(self.subheader_label)

        self.kpi_banner_label = QLabel(
            "Budget: - | Team Quality: - | Next Race: - | Drivers: - | Staff: -"
        )
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
        _style_table(self.staff_table, 160, 260)
        v.addWidget(self.staff_table)
        v.addStretch(1)
        return group

    def _create_car_group(self) -> QGroupBox:
        group = QGroupBox("Car and Facilities")
        v = QVBoxLayout(group)
        self.car_ops_label = QLabel("Operations Rating: -")
        self.car_strategy_label = QLabel("Strategy Profile: -")
        self.car_rating_label = QLabel("Car Development: -")
        self.facility_label = QLabel("Facilities: -")
        self.facility_label.setWordWrap(True)
        v.addWidget(self.car_ops_label)
        v.addWidget(self.car_strategy_label)
        v.addWidget(self.car_rating_label)
        v.addWidget(self.facility_label)

        self.upgrade_table = QTableWidget()
        self.upgrade_table.setColumnCount(3)
        self.upgrade_table.setHorizontalHeaderLabels(["Area", "Level", "Next Cost"])
        self.upgrade_table.setAccessibleName("Car Upgrades")
        uh = self.upgrade_table.horizontalHeader()
        if uh is not None:
            uh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            uh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            uh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        _style_table(self.upgrade_table, 215, 240)
        v.addWidget(self.upgrade_table)

        upgrade_row = QHBoxLayout()
        self.upgrade_combo = QComboBox()
        self.upgrade_combo.setAccessibleName("Upgrade Area")
        upgrade_row.addWidget(self.upgrade_combo)
        self.upgrade_btn = QPushButton("Buy Upgrade")
        self.upgrade_btn.setAccessibleName("Buy Upgrade")
        self.upgrade_btn.clicked.connect(self._run_car_upgrade)
        upgrade_row.addWidget(self.upgrade_btn)
        v.addLayout(upgrade_row)

        self.upgrade_result_label = QLabel("")
        self.upgrade_result_label.setWordWrap(True)
        v.addWidget(self.upgrade_result_label)
        return group

    def _create_hq_management_group(self) -> QGroupBox:
        group = QGroupBox("HQ Management")
        v = QVBoxLayout(group)

        self.hq_state_label = QLabel(
            "Run actions to grow quality, attractiveness, and budget."
        )
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
        self.schedule_table.setHorizontalHeaderLabels(
            ["Round", "Track", "Date", "Status"]
        )
        sh = self.schedule_table.horizontalHeader()
        if sh is not None:
            sh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        _style_table(self.schedule_table, 150)
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
        _style_table(self.standings_table, 150)
        v.addWidget(self.standings_table)
        return group

    def _resolve_team_ownership(self):
        team_id = self.db.get_player_team_id(self.player_id)
        team = self.db.get_team(team_id) if team_id else None

        if team and team.discipline == self.championship.discipline:
            self.owned_team = team
            return

        dialog = CareerTeamSelectionDialog(
            self.db,
            self.championship.discipline,
            getattr(self.championship, "tier", None),
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted or dialog.selected_team is None:
            warning(
                self,
                "Career Team Required",
                "Career mode requires selecting a team first.",
            )
            self._on_return_to_menu()
            return

        self.owned_team = dialog.selected_team
        self.db.assign_team_owner(self.owned_team.id, self.player_id)
        self._sync_selected_series_from_team()

    def _sync_selected_series_from_team(self) -> None:
        """Align selected career series to the owned team's discipline/tier."""
        if not self.owned_team:
            return
        with self.db.get_connection() as conn:
            row = conn.execute(
                """
                SELECT id, name, discipline, tier, season_length, current_season
                FROM career_championships
                WHERE player_id = ? AND discipline = ? AND tier = ? AND is_active = 1
                ORDER BY id
                LIMIT 1
                """,
                (
                    self.player_id,
                    str(self.owned_team.discipline).upper(),
                    normalise_tier(getattr(self.owned_team, "tier", "TIER_2")),
                ),
            ).fetchone()
            if row:
                rowd = dict(row)
                self.championship = SimpleNamespace(**rowd)

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
            self.kpi_banner_label.setText(
                "Budget: - | Team Quality: - | Next Race: - | Drivers: - | Staff: -"
            )
            return

        quality_score, _ = self._compute_team_scores()
        drivers = self.db.get_drivers_by_team(self.owned_team.id)
        try:
            staff = self.db.get_staff_by_team(self.owned_team.id)
        except Exception:
            staff = []

        next_race_text = SEASON_COMPLETE_TEXT
        if self.next_race:
            next_race_text = f"R{self.next_race.get('round_number', '?')} {self.next_race.get('track_name', '-')}"

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
            self.staff_table.setItem(
                row, 2, QTableWidgetItem(f"{float(member.rating):.1f}")
            )

    def _load_car_panel(self):
        if not self.owned_team:
            return
        self.car_ops_label.setText(
            f"Operations Rating: {self.owned_team.operations_rating:.1f}"
        )
        self.car_strategy_label.setText(
            "Strategy Profile: " f"{_player_label(self.owned_team.strategy_profile)}"
        )

        facilities = self.db.get_facility_upgrades(self.owned_team.id)
        if not facilities:
            self.facility_label.setText("Facilities: Baseline package")
        else:
            parts = [f"{f['facility_name']} L{f['level']}" for f in facilities]
            self.facility_label.setText("Facilities: " + ", ".join(parts))

        self._load_upgrade_panel()

    def _load_upgrade_panel(self):
        if not self.owned_team:
            return
        car_rating = self.upgrade_service.car_performance_rating(self.owned_team.id)
        self.car_rating_label.setText(f"Car Development: {car_rating * 100:.0f} / 100")

        rows = self.upgrade_service.get_upgrade_summary(self.owned_team)
        previous = self.upgrade_combo.currentData()
        self.upgrade_combo.blockSignals(True)
        self.upgrade_combo.clear()
        self.upgrade_table.setRowCount(len(rows))
        for idx, entry in enumerate(rows):
            self.upgrade_table.setItem(idx, 0, QTableWidgetItem(str(entry["label"])))
            self.upgrade_table.setItem(
                idx, 1, QTableWidgetItem(f"{entry['level']} / {entry['max_level']}")
            )
            cost = entry["next_cost"]
            self.upgrade_table.setItem(
                idx,
                2,
                QTableWidgetItem("Max" if cost is None else f"EUR {cost:,.0f}"),
            )
            if cost is not None:
                self.upgrade_combo.addItem(
                    f"{entry['label']} L{entry['level'] + 1} (EUR {cost:,.0f})",
                    entry["area"],
                )
        if previous is not None:
            found = self.upgrade_combo.findData(previous)
            if found >= 0:
                self.upgrade_combo.setCurrentIndex(found)
        self.upgrade_combo.blockSignals(False)
        self.upgrade_btn.setEnabled(self.upgrade_combo.count() > 0)

    def _run_car_upgrade(self):
        if not self.owned_team:
            return
        area = self.upgrade_combo.currentData()
        if not area:
            return
        result = self.upgrade_service.purchase_upgrade(
            self.owned_team.id, str(area), actor="player"
        )
        if not result.get("ok"):
            warning(self, BUDGET_WARNING_TITLE, str(result.get("message", "")))
            return
        self.upgrade_result_label.setText(str(result.get("message", "")))
        self.load_data()

    def _load_schedule_panel(self):
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT cr.id AS race_id, cr.round_number, cr.race_date, cr.status, cr.laps,
                       t.name AS track_name
                FROM career_races cr
                LEFT JOIN tracks t ON t.id = cr.track_id
                WHERE cr.player_id = ? AND cr.career_championship_id = ? AND cr.season = ?
                ORDER BY cr.round_number
                """,
                (
                    self.player_id,
                    int(self.championship.id),
                    int(self.championship.current_season),
                ),
            ).fetchall()
        calendar = [dict(r) for r in rows]

        self.schedule_table.setRowCount(len(calendar))
        self.next_race = None

        for row, race in enumerate(calendar):
            self.schedule_table.setItem(
                row, 0, QTableWidgetItem(f"R{race['round_number']}")
            )
            self.schedule_table.setItem(
                row, 1, QTableWidgetItem(str(race["track_name"]))
            )
            self.schedule_table.setItem(
                row, 2, QTableWidgetItem(str(race["race_date"]))
            )
            self.schedule_table.setItem(
                row, 3, QTableWidgetItem(_player_label(race["status"]))
            )

            if self.next_race is None and race["status"] == "scheduled":
                self.next_race = race

        self.start_next_btn.setEnabled(
            self.next_race is not None and self.selected_driver is not None
        )
        if self.next_race is None:
            self.start_next_btn.setText(SEASON_COMPLETE_TEXT)
        else:
            self.start_next_btn.setText("Start Next Race")

    def _load_standings_panel(self):
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                WITH filtered_results AS (
                    SELECT rr.id AS result_id,
                           rr.driver_id,
                           rr.team_id,
                           rr.points,
                           cr.round_number
                    FROM career_race_results rr
                    JOIN career_races cr ON cr.id = rr.career_race_id
                    WHERE cr.player_id = ? AND cr.career_championship_id = ? AND cr.season = ?
                ),
                driver_points AS (
                    SELECT fr.driver_id,
                           COALESCE(SUM(fr.points), 0) AS total_points
                    FROM filtered_results fr
                    GROUP BY fr.driver_id
                ),
                latest_round AS (
                    SELECT fr.driver_id,
                           MAX(fr.round_number) AS latest_round
                    FROM filtered_results fr
                    GROUP BY fr.driver_id
                ),
                latest_team_result AS (
                    SELECT fr.driver_id,
                           MAX(fr.result_id) AS latest_result_id
                    FROM filtered_results fr
                    JOIN latest_round lr
                      ON lr.driver_id = fr.driver_id
                     AND lr.latest_round = fr.round_number
                    GROUP BY fr.driver_id
                ),
                latest_team AS (
                    SELECT fr.driver_id,
                           fr.team_id
                    FROM filtered_results fr
                    JOIN latest_team_result ltr ON ltr.latest_result_id = fr.result_id
                )
                SELECT dp.driver_id AS driver_id,
                       COALESCE(d.name, 'Driver ' || dp.driver_id) AS driver_name,
                       lt.team_id AS team_id,
                       COALESCE(t.name, 'Team ' || lt.team_id) AS team_name,
                       dp.total_points AS total_points
                FROM driver_points dp
                LEFT JOIN latest_team lt ON lt.driver_id = dp.driver_id
                LEFT JOIN drivers d ON d.id = dp.driver_id
                LEFT JOIN teams t ON t.id = lt.team_id
                ORDER BY dp.total_points DESC, driver_name ASC
                """,
                (
                    self.player_id,
                    int(self.championship.id),
                    int(self.championship.current_season),
                ),
            ).fetchall()
        standings = [dict(r) for r in rows]

        self.standings_table.setRowCount(len(standings))
        for row, entry in enumerate(standings):
            self.standings_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.standings_table.setItem(
                row, 1, QTableWidgetItem(str(entry["driver_name"]))
            )
            self.standings_table.setItem(
                row, 2, QTableWidgetItem(str(entry["team_name"]))
            )
            self.standings_table.setItem(
                row, 3, QTableWidgetItem(str(entry["total_points"]))
            )

    def start_next_race(self):
        if not self.next_race:
            result = self.career_season_service.advance_season(
                player_id=self.player_id,
                completed_season=int(
                    getattr(self.championship, "current_season", 1) or 1
                ),
                discipline=str(getattr(self.championship, "discipline", "") or ""),
            )
            if result.get("rolled_over"):
                self._sync_selected_series_from_team()
                self.load_data()

                promoted = int(len(result.get("promoted", [])))
                relegated = int(len(result.get("relegated", [])))
                information(
                    self,
                    SEASON_COMPLETE_TEXT,
                    (
                        "Season finalized and advanced to next year.\n"
                        f"Promoted teams: {promoted} | Relegated teams: {relegated}"
                    ),
                )
            else:
                information(self, SEASON_COMPLETE_TEXT, "No scheduled races remain.")
            return

        if not self.selected_driver:
            warning(self, "No Driver", "Select a contracted team driver first.")
            return

        race_id = int(self.next_race["race_id"])
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT track_id, weather_conditions, laps FROM career_races WHERE id = ?",
                (race_id,),
            ).fetchone()
            if not row:
                warning(self, "Race Error", "Could not load next race details.")
                return
            conn.execute(
                "UPDATE career_races SET status = 'in-progress' WHERE id = ?",
                (race_id,),
            )
            conn.commit()

        race_data = dict(row)

        config = {
            "mode": "career",
            "personnel_transfers_enabled": True,
            "career_championship_id": int(self.championship.id),
            "race_id": race_id,
            "career_race_id": race_id,
            "track_id": int(race_data["track_id"]),
            "driver": self.selected_driver,
            "team": self.owned_team,
            "discipline": self.championship.discipline,
            "tier": str(getattr(self.championship, "tier", "TIER_2") or "TIER_2"),
            "weather": race_data.get("weather_conditions", "clear"),
            "tyre_strategy": "Medium",
            "laps": int(race_data.get("laps", 3) or 3),
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
        staff_avg = (
            (sum(float(s.rating) for s in staff) / len(staff)) if staff else 50.0
        )
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

        attractiveness_score = self._clamp(
            (quality_score * 0.65) + budget_score + brand_score
        )
        return quality_score, attractiveness_score

    def _apply_budget_delta(
        self, amount: float, category: str, description: str
    ) -> bool:
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
            self.db.add_budget_transaction(
                self.owned_team.id, category, float(amount), description
            )
        except Exception:
            pass

        refreshed = self.db.get_team(self.owned_team.id)
        if refreshed is not None:
            self.owned_team = refreshed
        return True

    def _apply_pending_race_income(self):
        """Pay prize and sponsor money for every completed race not yet paid (all teams)."""
        if not self.owned_team:
            return
        try:
            self.upgrade_service.award_pending_income(
                player_id=self.player_id,
                season=int(getattr(self.championship, "current_season", 1) or 1),
            )
        except Exception as ex:
            print(f"[CAREER] Failed to apply race income: {ex}")

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
            warning(
                self, BUDGET_WARNING_TITLE, "Not enough budget for marketing campaign."
            )
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
            warning(
                self, "No Driver", "Select a race driver before running development."
            )
            return

        cost = 180000
        applied = self._apply_budget_delta(
            -cost,
            "driver_development",
            f"Driver development for {self.selected_driver.name}",
        )
        if not applied:
            warning(
                self, BUDGET_WARNING_TITLE, "Not enough budget for driver development."
            )
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
                (speed_gain, racecraft_gain, consistency_gain, self.selected_driver.id),
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
            warning(
                self, BUDGET_WARNING_TITLE, "Not enough budget for staff development."
            )
            return

        try:
            staff = self.db.get_staff_by_team(self.owned_team.id)
        except Exception:
            staff = []

        if not staff:
            self.hq_action_result_label.setText(
                "No staff found. Program completed with no effect."
            )
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
            warning(
                self, BUDGET_WARNING_TITLE, "Not enough budget for facility upgrade."
            )
            return

        self.db.upsert_facility_upgrade(self.owned_team.id, facility_name, float(cost))
        self.owned_team.operations_rating = self._clamp(
            float(getattr(self.owned_team, "operations_rating", 50.0) or 50.0)
            + random.uniform(0.8, 2.0)
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
