from safe_prompt_pme.anonymizer import AnonymizationMapping, AnonymizationResult
from safe_prompt_pme.interfaces import LlmClient, TextAnonymizer


class FakeAnonymizer:
    def anonymize(self, text: str) -> AnonymizationResult:
        return AnonymizationResult(text=text, mapping=AnonymizationMapping({}))


class FakeLlmClient:
    def complete(self, prompt: str) -> str:
        return f"Réponse pour: {prompt}"


def test_text_anonymizer_protocol_documents_expected_contract() -> None:
    anonymizer: TextAnonymizer = FakeAnonymizer()

    assert anonymizer.anonymize("texte").text == "texte"


def test_llm_client_protocol_documents_expected_contract() -> None:
    client: LlmClient = FakeLlmClient()

    assert client.complete("[EMAIL_1]") == "Réponse pour: [EMAIL_1]"
