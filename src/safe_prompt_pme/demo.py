"""Workflow de démonstration pour le MVP Streamlit."""

from __future__ import annotations

from dataclasses import dataclass

from safe_prompt_pme.anonymizer import (
    AnonymizationMapping,
    anonymize_text,
    deanonymize_text,
)
from safe_prompt_pme.interfaces import LlmClient

MASKED_VALUE_LABEL = "valeur masquée localement"


@dataclass(frozen=True, slots=True)
class DemoResult:
    """Résultat complet affichable dans l'interface MVP."""

    original_text: str
    anonymized_text: str
    mapping: AnonymizationMapping
    llm_answer: str
    final_answer: str


def build_demo_result(original_text: str, llm_client: LlmClient) -> DemoResult:
    """Construit les 4 zones de démonstration du workflow.

    Le client LLM reçoit uniquement ``anonymized_text``. Le mapping reste local
    et sert seulement à réinjecter les valeurs dans ``final_answer``.
    """

    anonymized = anonymize_text(original_text)
    llm_answer = llm_client.complete(anonymized.text)
    final_answer = deanonymize_text(llm_answer, anonymized.mapping)

    return DemoResult(
        original_text=original_text,
        anonymized_text=anonymized.text,
        mapping=anonymized.mapping,
        llm_answer=llm_answer,
        final_answer=final_answer,
    )


def format_detected_items(
    mapping: AnonymizationMapping,
    *,
    reveal_values: bool = False,
) -> list[str]:
    """Formate les données détectées pour une démo client.

    Par défaut, les vraies valeurs restent masquées même dans l'affichage.
    ``reveal_values=True`` est utile uniquement en démo locale contrôlée.
    """

    return [
        f"{token} → {value if reveal_values else MASKED_VALUE_LABEL}"
        for token, value in mapping.items()
    ]
