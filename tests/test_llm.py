import json
import urllib.error
from io import BytesIO
from typing import Any

import pytest

from safe_prompt_pme.llm import (
    DemoLlmClient,
    LlmClientError,
    OpenAiCompatibleClient,
    mask_api_key,
)


class FakeResponse:
    def __init__(self, body: dict[str, Any]) -> None:
        self.body = body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        return False

    def read(self) -> bytes:
        return json.dumps(self.body).encode("utf-8")


def test_demo_llm_client_returns_safe_answer_with_tokens() -> None:
    client = DemoLlmClient()

    answer = client.complete(
        "Bonjour, pouvez-vous envoyer la facture [FACTURE_1] à [EMAIL_1] ?"
    )

    assert "[FACTURE_1]" in answer
    assert "[EMAIL_1]" in answer
    assert "sophie.martin" not in answer


def test_mask_api_key_hides_secret() -> None:
    assert mask_api_key("sk-test-123456") == "sk-t••••3456"
    assert mask_api_key("short") == "••••"
    assert mask_api_key("  ") == "aucune clé"


def test_openai_compatible_client_sends_anonymized_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: int) -> FakeResponse:
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {"choices": [{"message": {"content": "Réponse pour [EMAIL_1]"}}]}
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = OpenAiCompatibleClient(api_key="sk-secret", model="test-model")
    answer = client.complete("Envoyer à [EMAIL_1].")

    assert answer == "Réponse pour [EMAIL_1]"
    assert captured["timeout"] == 45
    assert captured["headers"]["Authorization"] == "Bearer sk-secret"
    assert captured["payload"]["model"] == "test-model"
    assert captured["payload"]["messages"][-1]["content"] == "Envoyer à [EMAIL_1]."
    assert "sophie.martin" not in json.dumps(captured["payload"])


def test_openai_compatible_client_rejects_empty_key() -> None:
    client = OpenAiCompatibleClient(api_key="")

    with pytest.raises(LlmClientError, match="clé API"):
        client.complete("[EMAIL_1]")


def test_openai_compatible_client_rejects_invalid_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Any, timeout: int) -> FakeResponse:
        return FakeResponse({"choices": []})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = OpenAiCompatibleClient(api_key="sk-secret")

    with pytest.raises(LlmClientError, match="invalide"):
        client.complete("[EMAIL_1]")


def test_openai_compatible_client_rejects_empty_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Any, timeout: int) -> FakeResponse:
        return FakeResponse({"choices": [{"message": {"content": "  "}}]})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = OpenAiCompatibleClient(api_key="sk-secret")

    with pytest.raises(LlmClientError, match="vide"):
        client.complete("[EMAIL_1]")


def test_openai_compatible_client_formats_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Any, timeout: int) -> FakeResponse:
        raise urllib.error.HTTPError(
            url="https://example.test",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(b'{"error":{"message":"bad key"}}'),
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = OpenAiCompatibleClient(api_key="sk-secret")

    with pytest.raises(LlmClientError, match="bad key"):
        client.complete("[EMAIL_1]")


def test_openai_compatible_client_formats_http_error_without_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Any, timeout: int) -> FakeResponse:
        raise urllib.error.HTTPError(
            url="https://example.test",
            code=500,
            msg="Server error",
            hdrs={},
            fp=BytesIO(b'not json'),
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = OpenAiCompatibleClient(api_key="sk-secret")

    with pytest.raises(LlmClientError, match="500"):
        client.complete("[EMAIL_1]")


def test_openai_compatible_client_formats_url_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Any, timeout: int) -> FakeResponse:
        raise urllib.error.URLError("offline")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = OpenAiCompatibleClient(api_key="sk-secret")

    with pytest.raises(LlmClientError, match="offline"):
        client.complete("[EMAIL_1]")


def test_openai_compatible_client_formats_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Any, timeout: int) -> FakeResponse:
        raise TimeoutError

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = OpenAiCompatibleClient(api_key="sk-secret")

    with pytest.raises(LlmClientError, match="temps"):
        client.complete("[EMAIL_1]")
