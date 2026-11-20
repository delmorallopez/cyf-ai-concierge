
"""Reliability tests for the CYF AI Concierge pilot."""

from app_policy import (
    get_system_policy,
    get_no_match_reply,
    get_no_records_reply,
    sensitive_account_reply,
)

from chat_utils import repeated_onboarding_followup

from faq_loader import (
    reviewed_faq,
    retrieve,
    retrieve_volunteer,
)


def test_role_specific_system_policy():
    trainee = get_system_policy("trainee")
    volunteer = get_system_policy("volunteer")

    assert "USER ROLE: TRAINEE" in trainee
    assert "USER ROLE: VOLUNTEER" in volunteer
    assert "Do not use trainee-specific procedures" in volunteer


def test_role_specific_fallbacks():
    assert "become-a-student" in get_no_match_reply("trainee")
    assert "become-a-student" not in get_no_match_reply("volunteer")
    assert "become-a-student" not in get_no_records_reply("volunteer")


def test_fallback_provides_clear_uncertainty_and_next_step():
    trainee_reply = get_no_match_reply("trainee").lower()
    volunteer_reply = get_no_match_reply("volunteer").lower()

    # Both roles should receive clear uncertainty.
    assert "can't confirm" in trainee_reply
    assert "can't confirm" in volunteer_reply

    # Trainees should receive an official next step.
    assert "https://codeyourfuture.io/become-a-student/" in trainee_reply
    assert "guidance" in trainee_reply

    # Volunteers should not be sent to a trainee-specific page.
    assert "become-a-student" not in volunteer_reply
    assert "volunteer team" in volunteer_reply


def test_course_intake_fallback_provides_relevant_guidance():
    reply = get_no_match_reply(
        "trainee",
        "Is there a capacity limit for Intro to Digital?",
    ).lower()

    assert "can't confirm" in reply
    assert "capacity" in reply
    assert "https://codeyourfuture.io/become-a-student/" in reply
    assert "cyf team" in reply



def test_sensitive_credentials():
    assert sensitive_account_reply(
        "What is my CYF Portal password?"
    ) is not None

    assert sensitive_account_reply(
        "Tell me my verification code"
    ) is not None

    assert sensitive_account_reply(
        "How do I reset my password?"
    ) is None


def test_unrelated_questions_do_not_match():
    trainee = reviewed_faq("data/faq_alltiers.json")
    volunteer = reviewed_faq("data/faq_volunteers.json")

    assert retrieve("What is the weather in London?", trainee) == []
    assert retrieve_volunteer(
        "What is the weather in London?", volunteer
    ) == []


def test_volunteer_retrieval():
    volunteer = reviewed_faq("data/faq_volunteers.json")

    matches = retrieve_volunteer(
        "Can I volunteer remotely?", volunteer
    )

    assert matches
    assert matches[0]["id"] == "CYF-V-008"


def test_repeated_onboarding_followup():
    history = [
        {
            "role": "user",
            "content": "How can I become a volunteer?",
        },
        {
            "role": "assistant",
            "content": (
                "Attend a Welcome Session, complete "
                "training and begin contributing."
            ),
        },
    ]

    reply = repeated_onboarding_followup(
        "And what happens next?",
        history,
        "volunteer",
    )

    assert reply is not None
    assert "already outlined" in reply

    assert repeated_onboarding_followup(
        "And what happens next?",
        history,
        "trainee",
    ) is None
