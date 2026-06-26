"""Application Streamlit du MVP Safe Prompt PME."""

from __future__ import annotations

import streamlit as st

from safe_prompt_pme.demo import build_demo_result, format_detected_items
from safe_prompt_pme.llm import DemoLlmClient

DEFAULT_EMAIL_EXAMPLE = """Bonjour,

Je suis Sophie Martin de ABC Transport.
Pouvez-vous me renvoyer la facture F-2025-1842 de 3 480 €
à sophie.martin@abc-transport.fr ?

Merci."""

PAGE_TITLE = "Safe Prompt PME — Démo anonymisation avant LLM"
PAGE_ICON = "🛡️"


def render_app() -> None:
    """Affiche l'interface Streamlit de démonstration."""

    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
    st.title("🛡️ Safe Prompt PME")
    st.subheader("Anonymisation locale avant appel à un LLM")

    st.markdown(
        """
        Cette démo montre le workflow MVP : texte original → anonymisation →
        appel LLM simulé → réinjection locale → validation humaine.

        **Important :** le client LLM de cette démo est local et simulé. Aucune
        donnée n'est envoyée à un fournisseur externe.
        """
    )

    original_text = st.text_area(
        "1. Email ou texte original",
        value=DEFAULT_EMAIL_EXAMPLE,
        height=220,
    )
    reveal_values = st.checkbox(
        "Afficher les vraies valeurs dans la table locale de démo",
        value=False,
        help="À activer uniquement en démonstration locale contrôlée.",
    )

    if st.button("Lancer la démo", type="primary"):
        result = build_demo_result(original_text, DemoLlmClient())
        detected_items = format_detected_items(
            result.mapping,
            reveal_values=reveal_values,
        )

        col_original, col_anonymized = st.columns(2)
        with col_original:
            st.markdown("### 1. Texte original")
            st.text_area("Original", value=result.original_text, height=220)

        with col_anonymized:
            st.markdown("### 2. Version envoyée au LLM")
            st.text_area("Anonymisé", value=result.anonymized_text, height=220)

        st.markdown("### 3. Données détectées — table locale")
        if detected_items:
            st.code("\n".join(detected_items), language="text")
        else:
            st.info("Aucune donnée sensible détectée par les règles du MVP.")

        col_llm, col_final = st.columns(2)
        with col_llm:
            st.markdown("### 4. Réponse LLM simulée")
            st.text_area("Réponse avec tokens", value=result.llm_answer, height=220)

        with col_final:
            st.markdown("### 5. Réponse finale après réinjection locale")
            st.text_area(
                "À valider par un humain",
                value=result.final_answer,
                height=220,
            )

        st.success("Workflow terminé : l'humain peut maintenant valider ou modifier.")


if __name__ == "__main__":
    render_app()
