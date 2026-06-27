"""Constantes métier utilisées par le moteur d'anonymisation.

Toutes les expressions régulières sont volontairement centralisées pour éviter
les valeurs magiques dans le code applicatif.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern


@dataclass(frozen=True, slots=True)
class SensitiveDataPattern:
    """Décrit une famille de données sensibles à remplacer."""

    label: str
    pattern: Pattern[str]


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_FR_PATTERN = re.compile(
    r"(?<!\d)(?:(?:\+33[ .-]?)|0)[1-9](?:[ .-]?\d{2}){4}(?!\d)"
)
INVOICE_PATTERN = re.compile(r"\b(?:F|FAC)-\d{2,4}-\d{3,}\b", re.IGNORECASE)
QUOTE_PATTERN = re.compile(r"\b(?:D|DEV)-\d{2,4}-\d{3,}\b", re.IGNORECASE)
AMOUNT_EUR_PATTERN = re.compile(
    r"\b\d{1,3}(?:[ .]\d{3})*(?:,\d{2})?\s?(?:€|EUR)(?:\s?HT|\s?TTC)?(?=\W|$)"
)
SIRET_PATTERN = re.compile(r"\b\d{3}[ .]?\d{3}[ .]?\d{3}[ .]?\d{5}\b")
IBAN_FR_PATTERN = re.compile(r"\bFR\d{2}(?:[ ]?[A-Z0-9]){23}\b", re.IGNORECASE)

DEFAULT_PATTERNS: tuple[SensitiveDataPattern, ...] = (
    SensitiveDataPattern("EMAIL", EMAIL_PATTERN),
    SensitiveDataPattern("TELEPHONE", PHONE_FR_PATTERN),
    SensitiveDataPattern("IBAN", IBAN_FR_PATTERN),
    SensitiveDataPattern("SIRET", SIRET_PATTERN),
    SensitiveDataPattern("FACTURE", INVOICE_PATTERN),
    SensitiveDataPattern("DEVIS", QUOTE_PATTERN),
    SensitiveDataPattern("MONTANT", AMOUNT_EUR_PATTERN),
)
