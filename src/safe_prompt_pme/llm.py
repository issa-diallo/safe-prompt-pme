"""Clients LLM pour démo et futures intégrations."""

from __future__ import annotations


class DemoLlmClient:
    """Client local sans réseau pour démontrer le workflow.

    Il simule une réponse LLM tout en conservant les tokens anonymisés. Cela
    permet de présenter le MVP sans clé API et sans envoyer de données dehors.
    """

    def complete(self, prompt: str) -> str:
        """Retourne une réponse métier simple à partir du prompt anonymisé."""

        if "[FACTURE_1]" in prompt and "[EMAIL_1]" in prompt:
            return (
                "Bonjour,\n\n"
                "Bien sûr, la facture [FACTURE_1] sera envoyée à [EMAIL_1].\n\n"
                "Bien cordialement."
            )

        return (
            "Bonjour,\n\n"
            "J'ai bien reçu votre demande. Je prépare une réponse adaptée "
            "avec les informations disponibles.\n\n"
            "Bien cordialement."
        )
