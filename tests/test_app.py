from typing import Any, Literal

from safe_prompt_pme import app


class FakeContext:
    def __enter__(self) -> "FakeContext":
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> Literal[False]:
        return False


class FakeStreamlit:
    def __init__(
        self,
        *,
        button_values: dict[str, bool] | None = None,
        checkbox_value: bool = False,
        provider_mode: str = "Démo locale",
        text_inputs: dict[str, str] | None = None,
    ) -> None:
        self.button_values = button_values or {}
        self.checkbox_value = checkbox_value
        self.provider_mode = provider_mode
        self.text_inputs = text_inputs or {}
        self.calls: list[tuple[str, Any]] = []
        self.sidebar = FakeContext()
        self.session_state: dict[str, Any] = {}

    def set_page_config(self, **kwargs: object) -> None:
        self.calls.append(("set_page_config", kwargs))

    def title(self, value: str) -> None:
        self.calls.append(("title", value))

    def caption(self, value: str) -> None:
        self.calls.append(("caption", value))

    def subheader(self, value: str) -> None:
        self.calls.append(("subheader", value))

    def markdown(self, value: str, **kwargs: object) -> None:
        self.calls.append(("markdown", value))

    def text_area(self, label: str, value: str, height: int, **kwargs: object) -> str:
        self.calls.append(("text_area", label))
        return value

    def checkbox(self, label: str, value: bool, help: str) -> bool:  # noqa: A002
        self.calls.append(("checkbox", label))
        return self.checkbox_value

    def button(self, label: str, **kwargs: object) -> bool:
        self.calls.append(("button", label))
        return self.button_values.get(label, False)

    def columns(self, spec: int | tuple[float, ...]) -> tuple[FakeContext, ...]:
        self.calls.append(("columns", spec))
        count = spec if isinstance(spec, int) else len(spec)
        return tuple(FakeContext() for _ in range(count))

    def code(self, body: str, language: str) -> None:
        self.calls.append(("code", body))

    def info(self, value: str) -> None:
        self.calls.append(("info", value))

    def success(self, value: str) -> None:
        self.calls.append(("success", value))

    def warning(self, value: str) -> None:
        self.calls.append(("warning", value))

    def error(self, value: str) -> None:
        self.calls.append(("error", value))

    def metric(self, label: str, value: str) -> None:
        self.calls.append(("metric", label, value))

    def selectbox(self, label: str, options: tuple[str, ...], index: int) -> str:
        self.calls.append(("selectbox", label))
        return self.provider_mode

    def text_input(self, label: str, value: str, **kwargs: object) -> str:
        self.calls.append(("text_input", label))
        return self.text_inputs.get(label, value)

    def expander(self, label: str) -> FakeContext:
        self.calls.append(("expander", label))
        return FakeContext()

    def spinner(self, label: str) -> FakeContext:
        self.calls.append(("spinner", label))
        return FakeContext()

    def divider(self) -> None:
        self.calls.append(("divider", None))

    def tabs(self, labels: list[str]) -> tuple[FakeContext, ...]:
        self.calls.append(("tabs", labels))
        return tuple(FakeContext() for _ in labels)

    def write(self, value: str) -> None:
        self.calls.append(("write", value))


def test_render_app_waits_for_button_before_running_demo(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(button_values={})
    monkeypatch.setattr(app, "st", fake_st)

    app.render_app()

    assert ("title", "🛡️ Safe Prompt PME") in fake_st.calls
    assert not any(call[0] == "divider" for call in fake_st.calls)


def test_render_app_displays_demo_sections_after_button(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(button_values={"Sécuriser et générer": True})
    monkeypatch.setattr(app, "st", fake_st)

    app.render_app()

    text_area_labels = [call[1] for call in fake_st.calls if call[0] == "text_area"]
    assert "Texte original" in text_area_labels
    assert "Version envoyée au LLM" in text_area_labels
    assert "Réponse avec tokens" in text_area_labels
    assert "Réponse finale à valider" in text_area_labels
    assert any(call[0] == "code" and "[EMAIL_1]" in call[1] for call in fake_st.calls)


def test_render_app_displays_empty_detection_message(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(button_values={"Sécuriser et générer": True})
    monkeypatch.setattr(app, "st", fake_st)
    monkeypatch.setattr(app, "DEFAULT_EMAIL_EXAMPLE", "Bonjour, rien à masquer.")

    app.render_app()

    assert any(
        call[0] == "info" and "Aucune donnée sensible" in call[1]
        for call in fake_st.calls
    )


def test_render_app_warns_when_api_mode_has_no_saved_key(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(provider_mode="OpenAI compatible")
    monkeypatch.setattr(app, "st", fake_st)

    app.render_app()

    assert any(call[0] == "warning" and "clé API" in call[1] for call in fake_st.calls)
    assert "last_result" not in fake_st.session_state


def test_render_app_can_save_and_clear_api_key(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(
        provider_mode="OpenAI compatible",
        button_values={"Enregistrer": True},
        text_inputs={"Clé API": "sk-user-secret"},
    )
    monkeypatch.setattr(app, "st", fake_st)

    app.render_app()

    assert fake_st.session_state["llm_api_key"] == "sk-user-secret"

    fake_st_clear = FakeStreamlit(
        provider_mode="OpenAI compatible",
        button_values={"Effacer": True},
        text_inputs={"Clé API": "sk-user-secret"},
    )
    fake_st_clear.session_state["llm_api_key"] = "sk-user-secret"
    monkeypatch.setattr(app, "st", fake_st_clear)

    app.render_app()

    assert fake_st_clear.session_state["llm_api_key"] == ""


def test_render_app_displays_llm_errors(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(button_values={"Sécuriser et générer": True})
    monkeypatch.setattr(app, "st", fake_st)

    def raise_llm_error(original_text: str, llm_client: object) -> None:
        raise app.LlmClientError("erreur contrôlée")

    monkeypatch.setattr(app, "build_demo_result", raise_llm_error)

    app.render_app()

    assert ("error", "erreur contrôlée") in fake_st.calls


def test_render_app_records_human_decisions(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(
        button_values={
            "Sécuriser et générer": True,
            "Accepter": True,
            "Rejeter": True,
        }
    )
    monkeypatch.setattr(app, "st", fake_st)

    app.render_app()

    decisions = [entry["decision"] for entry in fake_st.session_state["audit_log"]]
    assert decisions == ["accepté", "rejeté"]
    assert any(call[0] == "write" for call in fake_st.calls)
