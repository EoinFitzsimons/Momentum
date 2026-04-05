"""Reusable navigation/search bar for Momentum GUI screens."""

from __future__ import annotations

from typing import Callable, Optional, Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QMessageBox,
)


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
    TIER_VALUES = ["TOP_TIER", "TIER_1", "TIER_2", "TIER_3"]

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

    def _selected_filters(self) -> tuple[Optional[str], Optional[str]]:
        discipline = self.discipline_combo.currentData()
        tier = self.tier_combo.currentData()
        return discipline, tier

    def _show_results(self, title: str, rows: list[str]) -> None:
        if not rows:
            QMessageBox.information(self, title, "No results found.")
            return
        msg = "\n".join(rows[:20])
        if len(rows) > 20:
            msg += f"\n... and {len(rows) - 20} more"
        QMessageBox.information(self, title, msg)

    def _search_teams(self) -> None:
        discipline, tier = self._selected_filters()

        db = self._get_db()
        if db is None or not hasattr(db, "get_connection"):
            QMessageBox.warning(self, self.SEARCH_TEAMS_TEXT, "Database is unavailable.")
            return

        try:
            where_parts = []
            params = []
            if discipline:
                where_parts.append("discipline = ?")
                params.append(discipline)
            if tier:
                where_parts.append("tier = ?")
                params.append(tier)

            where_clause = ""
            if where_parts:
                where_clause = "WHERE " + " AND ".join(where_parts)

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
            formatted = [
                f"{name} | {_safe(discipline)} | {_safe(tier)} | HQ: {_safe(hq)}"
                for name, discipline, tier, hq in rows
            ]
            self._show_results("Team Search Results", formatted)
        except Exception as exc:
            QMessageBox.critical(self, self.SEARCH_TEAMS_TEXT, f"Search failed: {exc}")

    def _search_championships(self) -> None:
        discipline, _ = self._selected_filters()

        db = self._get_db()
        if db is None or not hasattr(db, "get_connection"):
            QMessageBox.warning(self, self.SEARCH_CHAMPIONSHIPS_TEXT, "Database is unavailable.")
            return

        try:
            where_clause = "WHERE discipline = ?" if discipline else ""
            params = (discipline,) if discipline else ()
            with db.get_connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT name, discipline, current_season, archived
                    FROM championships
                    {where_clause}
                    ORDER BY archived ASC, current_season DESC, name ASC
                    LIMIT 100
                    """,
                    params,
                ).fetchall()
            formatted = [
                f"{name} | {_safe(discipline)} | Season {int(season or 0)} | {'Archived' if int(archived or 0) else 'Active'}"
                for name, discipline, season, archived in rows
            ]
            self._show_results("Championship Search Results", formatted)
        except Exception as exc:
            QMessageBox.critical(self, self.SEARCH_CHAMPIONSHIPS_TEXT, f"Search failed: {exc}")


def _safe(value: object) -> str:
    text = str(value).strip() if value is not None else "-"
    return text if text else "-"


def _player_label(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    return raw.replace("_", " ").title()
