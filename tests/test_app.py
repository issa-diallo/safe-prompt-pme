from typing import Any, Literal

from safe_prompt_pme import app


class FakeColumn:
    def __enter__(self) -> "FakeColumn":
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> Literal[False]:
        return False


class FakeStreamlit:
    def __init__(self, *, button_value: bool, checkbox_value: bool = False) -> None:
        self.button_value = button_value
        self.checkbox_value = checkbox_value
        self.calls: list[tuple[str, Any]] = []

    def set_page_config(self, **kwargs: object) -> None:
        self.calls.append(("set_page_config", kwargs))

    def title(self, value: str) -> None:
        self.calls.append(("title", value))

    def subheader(self, value: str) -> None:
        self.calls.append(("subheader", value))

    def markdown(self, value: str) -> None:
        self.calls.append(("markdown", value))

    def text_area(self, label: str, value: str, height: int) -> str:
        self.calls.append(("text_area", label))
        return value

    def checkbox(self, label: str, value: bool, help: str) -> bool:  # noqa: A002
        self.calls.append(("checkbox", label))
        return self.checkbox_value

    def button(self, label: str, type: str) -> bool:  # noqa: A002
        self.calls.append(("button", label))
        return self.button_value

    def columns(self, count: int) -> tuple[FakeColumn, ...]:
        self.calls.append(("columns", count))
        return tuple(FakeColumn() for _ in range(count))

    def code(self, body: str, language: str) -> None:
        self.calls.append(("code", body))

    def info(self, value: str) -> None:
        self.calls.append(("info", value))

    def success(self, value: str) -> None:
        self.calls.append(("success", value))


def test_render_app_waits_for_button_before_running_demo(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(button_value=False)
    monkeypatch.setattr(app, "st", fake_st)

    app.render_app()

    assert ("title", "🛡️ Safe Prompt PME") in fake_st.calls
    assert not any(call[0] == "success" for call in fake_st.calls)


def test_render_app_displays_demo_sections_after_button(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(button_value=True)
    monkeypatch.setattr(app, "st", fake_st)

    app.render_app()

    text_area_labels = [call[1] for call in fake_st.calls if call[0] == "text_area"]
    assert "Original" in text_area_labels
    assert "Anonymisé" in text_area_labels
    assert "Réponse avec tokens" in text_area_labels
    assert "À valider par un humain" in text_area_labels
    assert any(call[0] == "code" and "[EMAIL_1]" in call[1] for call in fake_st.calls)
    assert any(call[0] == "success" for call in fake_st.calls)


def test_render_app_displays_empty_detection_message(monkeypatch: Any) -> None:
    fake_st = FakeStreamlit(button_value=True)
    monkeypatch.setattr(app, "st", fake_st)
    monkeypatch.setattr(app, "DEFAULT_EMAIL_EXAMPLE", "Bonjour, rien à masquer.")

    app.render_app()

    assert any(call[0] == "info" for call in fake_st.calls)
