"""Moteur minimal d'anonymisation et de réinjection locale."""

from __future__ import annotations

from collections.abc import ItemsView
from dataclasses import dataclass
from re import Match
from typing import NewType

from safe_prompt_pme.constants import DEFAULT_PATTERNS, SensitiveDataPattern

Token = NewType("Token", str)


@dataclass(frozen=True, slots=True)
class AnonymizationMapping:
    """Table locale token -> valeur réelle.

    Cette table ne doit pas être envoyée au LLM. Elle sert uniquement à
    réinjecter les valeurs dans l'environnement contrôlé de l'entreprise.
    """

    values: dict[str, str]

    def __getitem__(self, token: str) -> str:
        return self.values[token]

    def items(self) -> ItemsView[str, str]:
        return self.values.items()


@dataclass(frozen=True, slots=True)
class AnonymizationResult:
    """Résultat retourné après anonymisation."""

    text: str
    mapping: AnonymizationMapping


def anonymize_text(
    text: str,
    patterns: tuple[SensitiveDataPattern, ...] = DEFAULT_PATTERNS,
) -> AnonymizationResult:
    """Remplace les données sensibles par des tokens stables par type.

    Exemple: ``sophie@example.com`` devient ``[EMAIL_1]``.
    """

    anonymized_text = text
    mapping: dict[str, str] = {}
    counters: dict[str, int] = {}

    for sensitive_pattern in patterns:
        anonymized_text = _replace_pattern(
            anonymized_text,
            sensitive_pattern,
            counters,
            mapping,
        )

    return AnonymizationResult(
        text=anonymized_text,
        mapping=AnonymizationMapping(mapping),
    )


def deanonymize_text(text: str, mapping: AnonymizationMapping) -> str:
    """Réinjecte localement les valeurs réelles dans un texte généré."""

    deanonymized_text = text
    for token, original_value in mapping.items():
        deanonymized_text = deanonymized_text.replace(token, original_value)
    return deanonymized_text


def _replace_pattern(
    text: str,
    sensitive_pattern: SensitiveDataPattern,
    counters: dict[str, int],
    mapping: dict[str, str],
) -> str:
    """Remplace toutes les occurrences d'un type de donnée sensible."""

    def replacement(match: Match[str]) -> str:
        original_value = match.group(0)
        existing_token = _find_existing_token(mapping, original_value)
        if existing_token is not None:
            return existing_token

        counters[sensitive_pattern.label] = counters.get(sensitive_pattern.label, 0) + 1
        token = f"[{sensitive_pattern.label}_{counters[sensitive_pattern.label]}]"
        mapping[token] = original_value
        return token

    return sensitive_pattern.pattern.sub(replacement, text)


def _find_existing_token(mapping: dict[str, str], original_value: str) -> str | None:
    """Réutilise le même token si la même valeur apparaît plusieurs fois."""

    for token, mapped_value in mapping.items():
        if mapped_value == original_value:
            return token
    return None
