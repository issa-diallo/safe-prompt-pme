from safe_prompt_pme.demo import build_demo_result, format_detected_items


class FakeLlmClient:
    def complete(self, prompt: str) -> str:
        assert "sophie.martin@abc-transport.fr" not in prompt
        assert "F-2025-1842" not in prompt
        return "Bonjour, la facture [FACTURE_1] sera envoyée à [EMAIL_1]."


def test_build_demo_result_sends_only_anonymized_text_to_llm() -> None:
    original = (
        "Bonjour, pouvez-vous envoyer la facture F-2025-1842 "
        "à sophie.martin@abc-transport.fr ?"
    )

    result = build_demo_result(original, FakeLlmClient())

    assert result.original_text == original
    assert result.anonymized_text == (
        "Bonjour, pouvez-vous envoyer la facture [FACTURE_1] à [EMAIL_1] ?"
    )
    assert result.llm_answer == (
        "Bonjour, la facture [FACTURE_1] sera envoyée à [EMAIL_1]."
    )
    assert result.final_answer == (
        "Bonjour, la facture F-2025-1842 sera envoyée "
        "à sophie.martin@abc-transport.fr."
    )


def test_format_detected_items_hides_real_values_by_default() -> None:
    original = "Envoyer à client@example.com pour 3 480 €."

    result = build_demo_result(original, FakeLlmClient())

    assert format_detected_items(result.mapping) == [
        "[EMAIL_1] → valeur masquée localement",
        "[MONTANT_1] → valeur masquée localement",
    ]


def test_format_detected_items_can_show_values_for_local_demo() -> None:
    original = "Envoyer à client@example.com."

    result = build_demo_result(original, FakeLlmClient())

    assert format_detected_items(result.mapping, reveal_values=True) == [
        "[EMAIL_1] → client@example.com",
    ]
