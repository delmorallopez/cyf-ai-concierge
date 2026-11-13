
from unittest.mock import patch, MagicMock

from chat_engine import generate_ai_reply


def test_ai_prompt_preserves_faq_uncertainty():
    evidence = [
        {
            "id": "CYF-T1-006",
            "tier": "T1",
            "question": "What level of English is required?",
            "answer": (
                "Intro to Programming requires B2 English. "
                "CYF still needs to confirm the precise "
                "requirement for each stage."
            ),
            "source_urls": [],
        }
    ]

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response"

    with patch("chat_engine.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = (
            mock_response
        )

        generate_ai_reply(
            search_query="What English level do I need?",
            user_role="trainee",
            evidence=evidence,
            history=[],
        )

        call_kwargs = (
            mock_openai.return_value
            .chat.completions.create.call_args.kwargs
        )

    system_message = call_kwargs["messages"][0]["content"]

    assert "Preserve important qualifications" in system_message
    assert "do not present it as definitively confirmed" in system_message
    assert "CYF still needs to confirm" in system_message
