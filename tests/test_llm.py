from safe_prompt_pme.llm import DemoLlmClient


def test_demo_llm_client_returns_safe_answer_with_tokens() -> None:
    client = DemoLlmClient()

    answer = client.complete(
        "Bonjour, pouvez-vous envoyer la facture [FACTURE_1] à [EMAIL_1] ?"
    )

    assert "[FACTURE_1]" in answer
    assert "[EMAIL_1]" in answer
    assert "sophie.martin" not in answer
