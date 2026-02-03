"""
Locale mapping utilities for Faker based on country codes.

- Uses the canonical country list from data.countries
- Provides best-effort mapping to sensible locales
- Falls back deterministically when no mapping is available
"""
from __future__ import annotations

from typing import Dict, List

from data.countries import COUNTRIES

# Preferred locale pool for deterministic fallback
FALLBACK_LOCALES: List[str] = [
    "en_US", "en_GB", "en_CA", "en_AU",
    "fr_FR", "fr_CA",
    "es_ES", "es_MX",
    "pt_BR", "pt_PT",
    "de_DE", "it_IT",
    "nl_NL", "pl_PL", "ru_RU",
    "sv_SE", "no_NO", "da_DK", "fi_FI",
    "cs_CZ", "sk_SK", "hu_HU", "ro_RO",
    "tr_TR", "el_GR", "uk_UA",
    "ja_JP", "ko_KR", "zh_CN", "zh_TW",
    "th_TH", "vi_VN", "id_ID", "ms_MY",
    "hi_IN", "bn_BD", "ar_SA", "he_IL", "fa_IR"
]

# Explicit overrides for major locales
COUNTRY_TO_LOCALE_OVERRIDES: Dict[str, str] = {
    "USA": "en_US", "CAN": "en_CA", "GBR": "en_GB", "AUS": "en_AU", "NZL": "en_GB",
    "IRL": "en_GB", "IND": "hi_IN", "PAK": "en_GB",
    "FRA": "fr_FR", "BEL": "fr_FR", "CHE": "de_DE", "DEU": "de_DE", "GER": "de_DE", "AUT": "de_DE",
    "ITA": "it_IT", "ESP": "es_ES", "MEX": "es_MX", "ARG": "es_ES", "CHL": "es_ES", "COL": "es_ES",
    "PRT": "pt_PT", "BRA": "pt_BR",
    "NLD": "nl_NL", "SWE": "sv_SE", "FIN": "fi_FI", "NOR": "no_NO", "DNK": "da_DK", "ISL": "en_GB",
    "POL": "pl_PL", "CZE": "cs_CZ", "SVK": "sk_SK", "HUN": "hu_HU", "ROU": "ro_RO",
    "UKR": "uk_UA", "RUS": "ru_RU",
    "TUR": "tr_TR", "GRC": "el_GR",
    "JPN": "ja_JP", "KOR": "ko_KR", "CHN": "zh_CN", "TWN": "zh_TW",
    "THA": "th_TH", "VNM": "vi_VN", "IDN": "id_ID", "MYS": "ms_MY", "SGP": "en_GB",
    "ISR": "he_IL", "IRN": "fa_IR",
    "EGY": "ar_SA", "SAU": "ar_SA", "ARE": "ar_SA", "QAT": "ar_SA", "KWT": "ar_SA",
    "ZAF": "en_GB"
}

# Language groupings (best-effort)
ENGLISH_CODES = {
    "GBR", "USA", "CAN", "AUS", "NZL", "IRL", "SGP", "IND", "PAK", "NGA", "GHA", "KEN",
    "ZAF", "ZMB", "ZWE", "TZA", "UGA", "RWA", "ETH", "CMR", "JAM", "TTO", "BRB",
    "BHS", "ATG", "DMA", "GRD", "KNA", "LCA", "VCT", "BEL", "NLD"
}
FRENCH_CODES = {
    "FRA", "BEL", "CHE", "CAN", "LUX", "CIV", "SEN", "MLI", "NER", "TCD", "BEN",
    "BFA", "GIN", "CMR", "GAB", "COG", "COD", "CAF", "TGO", "MDG", "RWA", "BDI"
}
SPANISH_CODES = {
    "ESP", "MEX", "ARG", "CHL", "COL", "PER", "BOL", "ECU", "URY", "PRY",
    "VEN", "CRI", "CUB", "DOM", "GTM", "HND", "NIC", "PAN", "SLV"
}
PORTUGUESE_CODES = {"PRT", "BRA", "AGO", "MOZ", "CPV", "GNB", "STP", "TLS"}
ARABIC_CODES = {
    "DZA", "MAR", "TUN", "LBY", "EGY", "SDN", "SAU", "ARE", "QAT", "KWT", "OMN", "YEM",
    "JOR", "IRQ", "SYR", "LBN", "BHR"
}


def get_locale_for_country(country_code: str) -> str:
    """Return best-effort locale for a given country code."""
    if not country_code:
        return "en_US"

    if country_code in COUNTRY_TO_LOCALE_OVERRIDES:
        return COUNTRY_TO_LOCALE_OVERRIDES[country_code]

    if country_code in ENGLISH_CODES:
        return "en_GB"
    if country_code in FRENCH_CODES:
        return "fr_FR"
    if country_code in SPANISH_CODES:
        return "es_ES"
    if country_code in PORTUGUESE_CODES:
        return "pt_PT"
    if country_code in ARABIC_CODES:
        return "ar_SA"

    # Deterministic fallback based on code hash
    index = abs(hash(country_code)) % len(FALLBACK_LOCALES)
    return FALLBACK_LOCALES[index]


def get_all_country_codes() -> List[str]:
    """Return all canonical country codes used by the project."""
    return list(COUNTRIES.keys())
