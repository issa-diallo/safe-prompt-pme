"""Application Streamlit v1 de Safe Prompt PME."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast

import streamlit as st

from safe_prompt_pme.demo import DemoResult, build_demo_result, format_detected_items
from safe_prompt_pme.llm import (
    DEFAULT_OPENAI_CHAT_COMPLETIONS_URL,
    DEFAULT_OPENAI_MODEL,
    DemoLlmClient,
    LlmClientError,
    OpenAiCompatibleClient,
    mask_api_key,
)

DEFAULT_EMAIL_EXAMPLE = """Bonjour,

Je suis Sophie Martin de ABC Transport.
Pouvez-vous me renvoyer la facture F-2025-1842 de 3 480 €
à sophie.martin@abc-transport.fr ?

Merci."""

PAGE_TITLE = "Safe Prompt PME — V1"
PAGE_ICON = "🛡️"
ProviderMode = Literal["Démo locale", "OpenAI compatible"]


@dataclass(frozen=True, slots=True)
class ProviderSettings:
    """Configuration LLM sélectionnée dans l'interface."""

    mode: ProviderMode
    model: str
    api_url: str
    api_key: str

    @property
    def needs_api_key(self) -> bool:
        return self.mode == "OpenAI compatible"


def render_app() -> None:
    """Affiche l'interface Streamlit v1."""

    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
    _init_session_state()
    _inject_styles()

    st.title("🛡️ Safe Prompt PME")
    st.caption("Anonymiser localement, interroger un LLM, valider humainement.")

    provider_settings = _render_provider_panel()

    left_column, right_column = st.columns((1.05, 0.95))
    with left_column:
        st.markdown("### Texte métier")
        original_text = st.text_area(
            "Email, note CRM ou document à sécuriser",
            value=DEFAULT_EMAIL_EXAMPLE,
            height=260,
        )
        reveal_values = st.checkbox(
            "Afficher les vraies valeurs dans la table locale",
            value=False,
            help="À activer uniquement en démonstration locale contrôlée.",
        )

        has_text = bool(original_text.strip())
        has_required_key = (
            not provider_settings.needs_api_key
            or bool(provider_settings.api_key.strip())
        )
        can_run = has_text and has_required_key
        run_requested = st.button(
            "Sécuriser et générer",
            type="primary",
            use_container_width=True,
            disabled=not can_run,
        )
        if provider_settings.needs_api_key and not provider_settings.api_key.strip():
            st.warning("Ajoutez et enregistrez une clé API pour activer ce provider.")

    with right_column:
        _render_v1_checklist(provider_settings)

    if run_requested:
        client = _build_llm_client(provider_settings)
        try:
            with st.spinner("Anonymisation locale puis appel LLM sécurisé..."):
                st.session_state["last_result"] = build_demo_result(
                    original_text,
                    client,
                )
                st.session_state["validated_answer"] = ""
        except LlmClientError as error:
            st.error(str(error))
            return

    result = st.session_state.get("last_result")
    if isinstance(result, DemoResult):
        _render_result(result, reveal_values=reveal_values)
    else:
        st.info("Collez un texte, configurez le provider, puis lancez la génération.")


def _init_session_state() -> None:
    st.session_state.setdefault("llm_api_key", "")
    st.session_state.setdefault("provider_mode", "Démo locale")
    st.session_state.setdefault("model", DEFAULT_OPENAI_MODEL)
    st.session_state.setdefault("api_url", DEFAULT_OPENAI_CHAT_COMPLETIONS_URL)
    st.session_state.setdefault("audit_log", [])


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f7f8f5; }
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            background: #f7f8f5;
            color: #151712;
        }
        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] p,
        [data-testid="stMain"] label,
        [data-testid="stMain"] span {
            color: #151712;
        }
        [data-testid="stSidebar"] { background: #101315; color: #f4f1e8; }
        [data-testid="stSidebar"] * { color: inherit; }
        [data-testid="stSidebar"] input { color: #141414; }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2dfd2;
            border-radius: 8px;
            padding: 12px 14px;
        }
        div[data-testid="stMetric"] * {
            color: #1d2119 !important;
        }
        .safe-prompt-panel {
            border: 1px solid #d7d2c1;
            background: #fffef9;
            color: #1d2119;
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        .safe-prompt-panel strong {
            color: #151712;
        }
        .safe-prompt-status {
            background: #ffffff;
            border: 1px solid #ded9c8;
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        .safe-prompt-status-label {
            color: #4e554b;
            font-size: 0.82rem;
            line-height: 1.2;
            margin-bottom: 8px;
        }
        .safe-prompt-status-value {
            color: #1d2433;
            font-size: 1.28rem;
            line-height: 1.25;
            font-weight: 650;
            overflow-wrap: anywhere;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_provider_panel() -> ProviderSettings:
    with st.sidebar:
        st.markdown("## Provider LLM")
        st.caption("Clé API locale, masquée et stockée uniquement en session.")
        mode = cast(
            ProviderMode,
            st.selectbox(
                "Mode",
                options=("Démo locale", "OpenAI compatible"),
                index=0
                if st.session_state["provider_mode"] == "Démo locale"
                else 1,
            ),
        )
        st.session_state["provider_mode"] = mode

        model = st.text_input("Modèle", value=str(st.session_state["model"]))
        st.session_state["model"] = model.strip() or DEFAULT_OPENAI_MODEL

        with st.expander("Endpoint avancé"):
            api_url = st.text_input("URL API", value=str(st.session_state["api_url"]))
            st.session_state["api_url"] = (
                api_url.strip() or DEFAULT_OPENAI_CHAT_COMPLETIONS_URL
            )

        if mode == "OpenAI compatible":
            entered_key = st.text_input(
                "Clé API",
                value=str(st.session_state["llm_api_key"]),
                type="password",
                placeholder="sk-...",
            )
            save_column, clear_column = st.columns(2)
            with save_column:
                if st.button("Enregistrer", use_container_width=True):
                    st.session_state["llm_api_key"] = entered_key.strip()
            with clear_column:
                if st.button("Effacer", use_container_width=True):
                    st.session_state["llm_api_key"] = ""
            active_key = str(st.session_state["llm_api_key"])
            st.caption(f"Clé active : {mask_api_key(active_key)}")
        else:
            st.session_state["llm_api_key"] = ""
            st.success("Mode démo : aucun appel réseau, aucune clé requise.")

    return ProviderSettings(
        mode=mode,
        model=str(st.session_state["model"]),
        api_url=str(st.session_state["api_url"]),
        api_key=str(st.session_state["llm_api_key"]),
    )


def _render_v1_checklist(provider_settings: ProviderSettings) -> None:
    st.markdown("### Contrôles v1")
    _render_status_tile("Données envoyées", "Texte anonymisé uniquement")
    _render_status_tile("Mapping sensible", "Local")
    provider_label = (
        "API utilisateur"
        if provider_settings.needs_api_key
        else "Démo sans réseau"
    )
    _render_status_tile("Provider", provider_label)
    st.markdown(
        """
        <div class="safe-prompt-panel">
        <strong>Principe de sécurité</strong><br>
        La table token → vraie valeur n'est jamais envoyée au LLM. Elle sert
        seulement à reconstruire la réponse finale avant validation humaine.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_status_tile(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="safe-prompt-status">
            <div class="safe-prompt-status-label">{label}</div>
            <div class="safe-prompt-status-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_llm_client(
    settings: ProviderSettings,
) -> DemoLlmClient | OpenAiCompatibleClient:
    if settings.mode == "Démo locale":
        return DemoLlmClient()
    return OpenAiCompatibleClient(
        api_key=settings.api_key,
        model=settings.model,
        api_url=settings.api_url,
    )


def _render_result(result: DemoResult, *, reveal_values: bool) -> None:
    st.divider()
    st.markdown("## Résultat sécurisé")

    detected_items = format_detected_items(result.mapping, reveal_values=reveal_values)
    original_tab, anonymized_tab, llm_tab, validation_tab, journal_tab = st.tabs(
        ["Original", "Anonymisé", "LLM", "Validation", "Journal"]
    )

    with original_tab:
        st.text_area("Texte original", value=result.original_text, height=240)

    with anonymized_tab:
        st.text_area("Version envoyée au LLM", value=result.anonymized_text, height=240)
        st.markdown("#### Table locale")
        if detected_items:
            st.code("\n".join(detected_items), language="text")
        else:
            st.info("Aucune donnée sensible détectée par les règles v1.")

    with llm_tab:
        st.text_area("Réponse avec tokens", value=result.llm_answer, height=240)

    with validation_tab:
        final_answer = st.text_area(
            "Réponse finale à valider",
            value=result.final_answer,
            height=260,
        )
        accept_column, reject_column = st.columns(2)
        with accept_column:
            if st.button("Accepter", type="primary", use_container_width=True):
                _append_audit_event("accepté", final_answer)
                st.session_state["validated_answer"] = final_answer
                st.success("Réponse validée localement.")
        with reject_column:
            if st.button("Rejeter", use_container_width=True):
                _append_audit_event("rejeté", final_answer)
                st.warning("Réponse rejetée. Aucun envoi automatique n'est effectué.")

    with journal_tab:
        audit_log = st.session_state.get("audit_log", [])
        if audit_log:
            for entry in reversed(audit_log[-10:]):
                st.write(f"{entry['timestamp']} — {entry['decision']}")
        else:
            st.info("Aucune décision enregistrée dans cette session.")


def _append_audit_event(decision: str, answer: str) -> None:
    st.session_state["audit_log"].append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "decision": decision,
            "answer_length": len(answer),
        }
    )


if __name__ == "__main__":
    render_app()
