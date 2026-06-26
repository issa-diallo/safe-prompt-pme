from safe_prompt_pme import AnonymizationMapping, anonymize_text, deanonymize_text


def test_anonymize_email_customer_request_with_local_mapping() -> None:
    original = (
        "Bonjour, je suis Sophie Martin de ABC Transport. "
        "Pouvez-vous me renvoyer la facture F-2025-1842 de 3 480 € "
        "à sophie.martin@abc-transport.fr ?"
    )

    result = anonymize_text(original)

    assert "sophie.martin@abc-transport.fr" not in result.text
    assert "F-2025-1842" not in result.text
    assert "3 480 €" not in result.text
    assert "[EMAIL_1]" in result.text
    assert "[FACTURE_1]" in result.text
    assert "[MONTANT_1]" in result.text
    assert result.mapping["[EMAIL_1]"] == "sophie.martin@abc-transport.fr"
    assert result.mapping["[FACTURE_1]"] == "F-2025-1842"
    assert result.mapping["[MONTANT_1]"] == "3 480 €"


def test_deanonymize_text_reinjects_sensitive_values_locally() -> None:
    mapping = AnonymizationMapping(
        {
            "[PERSONNE_1]": "Sophie Martin",
            "[FACTURE_1]": "F-2025-1842",
            "[EMAIL_1]": "sophie.martin@abc-transport.fr",
        }
    )
    llm_answer = (
        "Bonjour [PERSONNE_1], la facture [FACTURE_1] "
        "sera envoyée à [EMAIL_1]."
    )

    final_answer = deanonymize_text(llm_answer, mapping)

    assert final_answer == (
        "Bonjour Sophie Martin, la facture F-2025-1842 "
        "sera envoyée à sophie.martin@abc-transport.fr."
    )


def test_anonymization_preserves_meaningful_business_context() -> None:
    original = "Relancer Mme Durand pour le devis D-2025-087 de 12 500 € HT."

    result = anonymize_text(original)

    assert "Relancer" in result.text
    assert "devis" in result.text
    assert "[DEVIS_1]" in result.text
    assert "[MONTANT_1]" in result.text
    assert "D-2025-087" not in result.text
    assert "12 500 €" not in result.text


def test_repeated_sensitive_value_reuses_same_token() -> None:
    original = (
        "Envoyer à client@example.com puis confirmer à client@example.com."
    )

    result = anonymize_text(original)

    assert result.text.count("[EMAIL_1]") == 2
    assert "[EMAIL_2]" not in result.text
    assert result.mapping["[EMAIL_1]"] == "client@example.com"


def test_anonymize_french_business_identifiers() -> None:
    original = (
        "Client SIRET 752 631 127 00046, téléphone 06 03 59 86 00, "
        "IBAN FR76 3000 6000 0112 3456 7890 189."
    )

    result = anonymize_text(original)

    assert "[SIRET_1]" in result.text
    assert "[TELEPHONE_1]" in result.text
    assert "[IBAN_1]" in result.text
    assert "752 631 127 00046" not in result.text
    assert "06 03 59 86 00" not in result.text
    assert "FR76 3000 6000 0112 3456 7890 189" not in result.text
