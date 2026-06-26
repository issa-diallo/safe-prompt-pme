"""Interfaces publiques pour les intégrations LLM et métiers."""

from __future__ import annotations

from typing import Protocol

from safe_prompt_pme.anonymizer import AnonymizationResult


class TextAnonymizer(Protocol):
    """Contrat minimal d'un composant qui anonymise du texte."""

    def anonymize(self, text: str) -> AnonymizationResult:
        """Retourne le texte masqué et le mapping local."""


class LlmClient(Protocol):
    """Contrat pour envoyer uniquement le texte anonymisé au LLM."""

    def complete(self, prompt: str) -> str:
        """Retourne la réponse du modèle."""
