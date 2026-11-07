"""Reusable navigation/search bar for Momentum GUI screens."""

from __future__ import annotations

from typing import Callable, Optional, Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)
from GUI.themed_messagebox import information, warning, critical
from services.tier_service import TIERS


class SearchResultsDialog(QDialog):
    """Display search results in a sortable table popup."""

    def __init__(
        self,
        title: str,
        headers: list[str],
        rows: list[list[str]],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(980, 560)
        self._build_ui(headers=headers, rows=rows)

    def _build_ui(self, headers: list[str], rows: list[list[str]]) -> None:
        layout = QVBoxLayout(self)

        self.table = QTableWidget()

        _vh = self.table.verticalHeader()

        if _vh is not None:

            _vh.setVisible(False)

        self.table.setShowGrid(False)

        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        self.table.setSortingEnabled(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        for row_idx, row_values in enumerate(rows):
            for col_idx, cell_value in enumerate(row_values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_value)))

        header = self.table.horizontalHeader()
        if header is not None:
            for idx in range(len(headers)):
                if idx == 0:
                    header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Stretch)
                else:
                    header.setSectionResizeMode(
                        idx, QHeaderView.ResizeMode.ResizeToContents
                    )

        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        layout.addWidget(self.table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class NavigationBar(QWidget):
    """Top navigation bar with team/championship search actions."""

    SEARCH_TEAMS_TEXT = "Search Teams"
    SEARCH_CHAMPIONSHIPS_TEXT = "Search Championships"
    ALL_DISCIPLINES_TEXT = "All Disciplines"
    ALL_TIERS_TEXT = "All Tiers"
    DISCIPLINE_VALUES = [
        "SINGLE_SEATER",
        "ENDURANCE",
        "PRODUCTION_TOURING",
        "URBAN_STREET",
        "DRAG_ACCELERATION",
        "SPRINT_RALLYCROSS",
    ]
    TIER_VALUES = list(TIERS)
    SQL_DISCIPLINE_FILTER = "LOWER(REPLACE(discipline, ' ', '_')) = ?"
    SQL_TIER_FILTER = "tier = ?"
    SQL_NAME_FILTER = "LOWER(name) LIKE ?"
    SQL_WHERE_PREFIX = "WHERE "
    SQL_AND = " AND "

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        db_provider: Optional[Callable[[], Any]] = None,
        title: str = "Navigate",
    ):
        super().__init__(parent)
        self._db_provider = db_provider
        self._title = title
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        title_label = QLabel(self._title)
        title_label.setStyleSheet("font-weight: 700;")
        layout.addWidget(title_label)

        discipline_label = QLabel("Discipline:")
        layout.addWidget(discipline_label)

        self.discipline_combo = QComboBox()
        self.discipline_combo.setAccessibleName("Search Discipline Filter")
        self.discipline_combo.addItem(self.ALL_DISCIPLINES_TEXT, None)
        for value in self.DISCIPLINE_VALUES:
            self.discipline_combo.addItem(_player_label(value), value)
        layout.addWidget(self.discipline_combo)

        tier_label = QLabel("Tier:")
        layout.addWidget(tier_label)

        self.tier_combo = QComboBox()
        self.tier_combo.setAccessibleName("Search Tier Filter")
        self.tier_combo.addItem(self.ALL_TIERS_TEXT, None)
        for value in self.TIER_VALUES:
            self.tier_combo.addItem(_player_label(value), value)
        layout.addWidget(self.tier_combo)

        search_label = QLabel("Name:")
        layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setAccessibleName("Search Name Filter")
        self.search_input.setPlaceholderText("Team/championship name contains...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self._search_teams)
        layout.addWidget(self.search_input)

        search_teams_btn = QPushButton(self.SEARCH_TEAMS_TEXT)
        search_teams_btn.clicked.connect(self._search_teams)
        search_teams_btn.setToolTip("Browse teams by discipline and tier")
        search_teams_btn.setAccessibleName(self.SEARCH_TEAMS_TEXT)
        layout.addWidget(search_teams_btn)

        search_champs_btn = QPushButton(self.SEARCH_CHAMPIONSHIPS_TEXT)
        search_champs_btn.clicked.connect(self._search_championships)
        search_champs_btn.setToolTip("Browse championships by discipline")
        search_champs_btn.setAccessibleName(self.SEARCH_CHAMPIONSHIPS_TEXT)
        layout.addWidget(search_champs_btn)

        layout.addStretch()

        hint = QLabel("Tip: Filter by discipline/tier, then browse")
        hint.setStyleSheet("font-size: 11px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(hint)

    def _get_db(self):
        if not callable(self._db_provider):
            return None
        try:
            return self._db_provider()
        except Exception:
            return None

    def _selected_filters(self) -> tuple[Optional[str], Optional[str], str]:
        discipline = self.discipline_combo.currentData()
        tier = self.tier_combo.currentData()
        name_query = str(self.search_input.text() or "").strip()
        return discipline, tier, name_query

    def _show_results(
        self, title: str, headers: list[str], rows: list[list[str]]
    ) -> None:
        if not rows:
            information(self, title, "No results found.")
            return

        dialog = SearchResultsDialog(
            title=title, headers=headers, rows=rows, parent=self
        )
        dialog.exec()

    def _search_teams(self) -> None:
        discipline, tier, name_query = self._selected_filters()

        db = self._get_db()
        if db is None or not hasattr(db, "get_connection"):
            warning(self, self.SEARCH_TEAMS_TEXT, "Database is unavailable.")
            return

        try:
            where_parts = []
            params = []
            if discipline:
                where_parts.append(self.SQL_DISCIPLINE_FILTER)
                params.append(str(discipline).lower())
            if tier:
                where_parts.append(self.SQL_TIER_FILTER)
                params.append(tier)
            if name_query:
                where_parts.append(self.SQL_NAME_FILTER)
                params.append(f"%{name_query.lower()}%")

            where_clause = ""
            if where_parts:
                where_clause = self.SQL_WHERE_PREFIX + self.SQL_AND.join(where_parts)

            with db.get_connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT name, discipline, tier, headquarters
                    FROM teams
                    {where_clause}
                    ORDER BY operations_rating DESC, name ASC
                    LIMIT 100
                    """,
                    tuple(params),
                ).fetchall()
            table_rows = [
                [_safe(name), _safe(discipline), _safe(tier), _safe(hq)]
                for name, discipline, tier, hq in rows
            ]
            self._show_results(
                title="Team Search Results",
                headers=["Team", "Discipline", "Tier", "Headquarters"],
                rows=table_rows,
            )
        except Exception as exc:
            critical(self, self.SEARCH_TEAMS_TEXT, f"Search failed: {exc}")

    def _search_championships(self) -> None:
        discipline, tier, name_query = self._selected_filters()

        db = self._get_db()
        if db is None or not hasattr(db, "get_connection"):
            warning(self, self.SEARCH_CHAMPIONSHIPS_TEXT, "Database is unavailable.")
            return

        try:
            std_where_parts = []
            career_where_parts = []
            params = []

            if discipline:
                std_where_parts.append(self.SQL_DISCIPLINE_FILTER)
                career_where_parts.append(self.SQL_DISCIPLINE_FILTER)
                params.append(str(discipline).lower())
            if tier:
                std_where_parts.append(self.SQL_TIER_FILTER)
                career_where_parts.append(self.SQL_TIER_FILTER)
                params.append(tier)
            if name_query:
                std_where_parts.append(self.SQL_NAME_FILTER)
                career_where_parts.append(self.SQL_NAME_FILTER)
                params.append(f"%{name_query.lower()}%")

            std_where_clause = (
                (self.SQL_WHERE_PREFIX + self.SQL_AND.join(std_where_parts))
                if std_where_parts
                else ""
            )
            career_where_clause = (
                (self.SQL_WHERE_PREFIX + self.SQL_AND.join(career_where_parts))
                if career_where_parts
                else ""
            )

            with db.get_connection() as conn:
                rows = []

                try:
                    std_rows = conn.execute(
                        f"""
                        SELECT name, discipline, tier, current_season, archived, 'Standard' AS source
                        FROM championships
                        {std_where_clause}
                        ORDER BY archived ASC, current_season DESC, name ASC
                        LIMIT 100
                        """,
                        tuple(params),
                    ).fetchall()
                    rows.extend(std_rows)
                except Exception:
                    pass

                try:
                    career_rows = conn.execute(
                        f"""
                        SELECT name, discipline, tier, current_season, 0 AS archived, 'Career' AS source
                        FROM career_championships
                        {career_where_clause}
                        ORDER BY current_season DESC, name ASC
                        LIMIT 100
                        """,
                        tuple(params),
                    ).fetchall()
                    rows.extend(career_rows)
                except Exception:
                    pass

            table_rows = [
                [
                    _safe(name),
                    _safe(discipline),
                    _safe(tier),
                    f"{int(season or 0)}",
                    "Archived" if int(archived or 0) else "Active",
                    _safe(source),
                ]
                for name, discipline, tier, season, archived, source in rows
            ]
            self._show_results(
                title="Championship Search Results",
                headers=[
                    "Championship",
                    "Discipline",
                    "Tier",
                    "Season",
                    "Status",
                    "Source",
                ],
                rows=table_rows,
            )
        except Exception as exc:
            critical(self, self.SEARCH_CHAMPIONSHIPS_TEXT, f"Search failed: {exc}")


def _safe(value: object) -> str:
    text = str(value).strip() if value is not None else "-"
    return text if text else "-"


def _player_label(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    return raw.replace("_", " ").title()
