
from chat_utils import clarify_ambiguous_link


def test_ambiguous_link_requests_clarification():
    history = [
        {
            "role": "user",
            "content": "What's up with the courses?",
        },
        {
            "role": "assistant",
            "content": (
                "You can register for Intro to Digital "
                "and start studying the curriculum immediately."
            ),
        },
        {
            "role": "user",
            "content": "When can I start?",
        },
        {
            "role": "assistant",
            "content": "You can start studying immediately.",
        },
    ]

    result = clarify_ambiguous_link(
        "Share the link pls",
        history,
        "trainee",
    )

    assert result is not None
    assert "registration link" in result.lower()
    assert "curriculum link" in result.lower()


def test_clear_link_request_does_not_need_clarification():
    history = [
        {
            "role": "user",
            "content": "How do I register for Intro to Digital?",
        },
        {
            "role": "assistant",
            "content": "You can register online.",
        },
    ]

    result = clarify_ambiguous_link(
        "Share the link pls",
        history,
        "trainee",
    )

    assert result is None


def test_volunteer_does_not_trigger_trainee_clarification():
    history = [
        {
            "role": "assistant",
            "content": (
                "You can register for Intro to Digital "
                "and study the curriculum."
            ),
        },
    ]

    result = clarify_ambiguous_link(
        "Share the link pls",
        history,
        "volunteer",
    )

    assert result is None


def test_unrelated_question_does_not_trigger_clarification():
    history = [
        {
            "role": "assistant",
            "content": (
                "You can register for Intro to Digital "
                "and study the curriculum."
            ),
        },
    ]

    result = clarify_ambiguous_link(
        "How much does the course cost?",
        history,
        "trainee",
    )

    assert result is None

