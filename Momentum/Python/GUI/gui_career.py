"""
Career Mode GUI for Momentum Racing Simulator.

This module keeps career flow separate from championship flow for clarity,
while reusing the stable season/race lifecycle components from
`gui_championship`.
"""

from typing import Any, Dict

from PyQt6.QtWidgets import QDialog, QMessageBox

from GUI.gui_championship import (
    ChampionshipSelectionDialog,
    ChampionshipWindow,
    PreRaceSetupDialog,
)


class CareerSelectionDialog(ChampionshipSelectionDialog):
    """Career-specific entry dialog (backed by championship data model)."""

    def __init__(self, db, parent=None):
        super().__init__(db, parent)
        self.setWindowTitle("Select Career")


class CareerPreRaceSetupDialog(PreRaceSetupDialog):
    """Career pre-race setup with career mode flags in race config."""

    def __init__(self, db, championship, race, track, parent=None):
        super().__init__(db, championship, race, track, parent)
        self.setWindowTitle(
            f"Career Pre-Race Setup - {track.name if track else 'Race'}"
        )

    def get_race_config(self) -> Dict[str, Any]:
        config = super().get_race_config()
        config["mode"] = "career"
        # Career mode owns personnel changes and longer-term management.
        config["personnel_transfers_enabled"] = True
        return config


class CareerWindow(ChampionshipWindow):
    """Career mode window built on top of championship season flow."""

    def __init__(self, championship, parent=None):
        super().__init__(championship, parent)
        self.setWindowTitle(f"Career: {championship.name}")

    def start_next_race(self):
        """Start next race using career pre-race dialog and career config."""
        if not self.next_race_id:
            return

        race = self.db.get_race(self.next_race_id)
        if not race:
            QMessageBox.warning(self, "Error", "Could not load race details.")
            return

        track = self.db.get_track(race.track_id)

        setup_dialog = CareerPreRaceSetupDialog(
            self.db,
            self.championship,
            race,
            track,
            parent=self,
        )

        if setup_dialog.exec() == QDialog.DialogCode.Accepted:
            config = setup_dialog.get_race_config()

            try:
                success, error_msg = self.championship_service.update_race_lifecycle_status(
                    self.next_race_id,
                    "in-progress",
                )

                if not success:
                    QMessageBox.warning(
                        self,
                        "Status Update Failed",
                        f"Could not update race status: {error_msg}",
                    )
                    return

                self.start_race_signal.emit(config)

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update race status: {str(e)}",
                )
