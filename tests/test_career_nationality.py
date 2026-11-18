"""The manager's nationality is a country, and the new team is based there."""

from momentum.gui.gui_career import country_name, nationality_code


def test_saved_codes_and_legacy_free_text_both_map_to_a_country():
    assert nationality_code("IRL") == "IRL"
    assert nationality_code("irl") == "IRL"
    assert nationality_code("Ireland") == "IRL"
    assert nationality_code("United Kingdom") == "GBR"
    assert nationality_code("Atlantis") is None
    assert nationality_code("") is None


def test_country_name_reads_back_for_display():
    assert country_name("IRL") == "Ireland"
    assert country_name("Ireland") == "Ireland"
    assert country_name("Atlantis") == "Atlantis"


def test_found_team_dialog_defaults_to_the_managers_country(seeded_db):
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    from momentum.gui.gui_career import FoundTeamDialog

    dialog = FoundTeamDialog(seeded_db["db"], "SINGLE_SEATER", home_country="IRL")
    assert dialog.country_combo.currentData() == "IRL"
    other = FoundTeamDialog(seeded_db["db"], "SINGLE_SEATER", home_country="Ireland")
    assert other.country_combo.currentData() == "IRL"
    assert app is not None


def test_found_team_dialog_has_no_country_when_the_nationality_is_unknown(seeded_db):
    from PyQt6.QtWidgets import QApplication

    QApplication.instance() or QApplication([])
    from momentum.gui.gui_career import FoundTeamDialog

    dialog = FoundTeamDialog(seeded_db["db"], "SINGLE_SEATER", home_country="Atlantis")
    assert dialog.country_combo.currentData() is None
