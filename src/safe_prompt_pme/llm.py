"""Clients LLM pour démo et intégrations API."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_TIMEOUT_SECONDS = 45


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


class LlmClientError(RuntimeError):
    """Erreur contrôlée pour affichage utilisateur sans exposer la clé API."""


@dataclass(frozen=True, slots=True)
class OpenAiCompatibleClient:
    """Client minimal pour l'API Chat Completions compatible OpenAI.

    Le client reçoit uniquement le prompt déjà anonymisé. La clé API reste dans
    la session Streamlit ou dans l'environnement local de l'utilisateur.
    """

    api_key: str
    model: str = DEFAULT_OPENAI_MODEL
    api_url: str = DEFAULT_OPENAI_CHAT_COMPLETIONS_URL
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def complete(self, prompt: str) -> str:
        """Appelle le provider avec le texte anonymisé et retourne le contenu."""

        if not self.api_key.strip():
            msg = "La clé API est vide."
            raise LlmClientError(msg)

        request = urllib.request.Request(
            self.api_url,
            data=json.dumps(self._payload(prompt)).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(  # noqa: S310 - URL configurable côté app.
                request,
                timeout=self.timeout_seconds,
            ) as response:
                raw_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            raise LlmClientError(_format_http_error(error)) from error
        except urllib.error.URLError as error:
            message = f"Provider LLM inaccessible : {error.reason}"
            raise LlmClientError(message) from error
        except TimeoutError as error:
            raise LlmClientError("Le provider LLM n'a pas répondu à temps.") from error

        return _extract_chat_completion_content(raw_body)

    def _payload(self, prompt: str) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu aides une PME à répondre à un message. "
                        "Conserve strictement les tokens anonymisés comme "
                        "[EMAIL_1], [FACTURE_1] ou [MONTANT_1]."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }


def mask_api_key(api_key: str) -> str:
    """Masque une clé API pour l'afficher sans l'exposer."""

    cleaned_api_key = api_key.strip()
    if not cleaned_api_key:
        return "aucune clé"
    if len(cleaned_api_key) <= 8:
        return "••••"
    return f"{cleaned_api_key[:4]}••••{cleaned_api_key[-4:]}"


def _extract_chat_completion_content(raw_body: str) -> str:
    try:
        payload = json.loads(raw_body)
        content = payload["choices"][0]["message"]["content"]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as error:
        msg = "Réponse LLM invalide ou vide."
        raise LlmClientError(msg) from error

    if not isinstance(content, str) or not content.strip():
        msg = "Réponse LLM vide."
        raise LlmClientError(msg)
    return content


def _format_http_error(error: urllib.error.HTTPError) -> str:
    try:
        body = error.read().decode("utf-8")
        payload = json.loads(body)
        provider_message = payload.get("error", {}).get("message")
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        provider_message = None

    if provider_message:
        return f"Erreur provider LLM ({error.code}) : {provider_message}"
    return f"Erreur provider LLM ({error.code})."
