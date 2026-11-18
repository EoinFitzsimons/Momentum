"""Seeded people carry a plain given and family name, whatever the locale."""

import pytest

from momentum.seed import world


@pytest.mark.parametrize(
    "locale, raw, expected",
    [
        ("de_DE", "Univ.Prof. Niels Gregersen B.Eng.", "Niels Gregersen"),
        ("de_DE", "Dipl.-Ing. Mesut Faust MBA.", "Mesut Faust"),
        ("id_ID", "Drs. Panji Mandasari, S.E.", "Panji Mandasari"),
        ("it_IT", "Dott. Sole Vattimo", "Sole Vattimo"),
        ("it_IT", "Sig.ra Sole Vattimo", "Sole Vattimo"),
        ("tr_TR", "Yrd. Doç. Elif Yılmaz", "Elif Yılmaz"),
        ("cs_CZ", "Ing. arch. Pavel Novák Ph.D.", "Pavel Novák"),
        ("hu_HU", "Dr. Biró A. Róbert", "Biró Róbert"),
        ("lv_LV", "Skujiņa, Grēta", "Grēta Skujiņa"),
        ("vi_VN", "Quý cô Thu Phạm", "Thu Phạm"),
        ("ru_RU", "тов. Иван Петров", "Ivan Petrov"),
        ("fr_FR", "Pierre de la Fontaine", "Pierre de la Fontaine"),
        ("es_ES", "Dominga del Río", "Dominga del Río"),
        ("de_DE", "Kay-Uwe Vollbrecht", "Kay-Uwe Vollbrecht"),
        ("sl_SI", "Anja žagar", "Anja Žagar"),
    ],
)
def test_titles_and_qualifications_are_stripped(locale, raw, expected):
    assert world.clean_name(raw, world.fake_for_locale(locale)) == expected


def test_korean_names_are_spaced_family_first():
    assert world.korean_name("류", "현주") == "Ryu Hyeonju"
    assert world.korean_name("이", "지은") == "Lee Jieun"


def test_every_locale_yields_a_two_part_latin_name():
    world.seed_world(3)
    for locale in world.COMMON_LOCALES + ["tr_TR", "id_ID", "cs_CZ", "lv_LV", "vi_VN", "hu_HU"]:
        fake = world.fake_for_locale(locale)
        prefixes, suffixes = world.provider_titles(fake)
        titles = {t.casefold().rstrip(".") for t in prefixes + suffixes}
        for _ in range(60):
            name = world.full_name(fake)
            tokens = name.split()
            assert len(tokens) >= 2, (locale, name)
            assert world.is_latin_script(name), (locale, name)
            for token in tokens:
                assert "." not in token and token.casefold().rstrip(".") not in titles, (locale, name)


def test_same_seed_gives_the_same_names():
    def draw():
        world.seed_world(11)
        return [world.full_name(world.fake_for_locale(loc)) for loc in world.COMMON_LOCALES for _ in range(3)]

    assert draw() == draw()
