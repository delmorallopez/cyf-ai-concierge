
import pytest

from faq_loader import retrieve, reviewed_faq


@pytest.mark.parametrize(
    "question, expected_id",
    [
        (
            "I have done all the steps for the eligibility. "
            "How do I join the correct Slack workspace?",
            "CYF-T5-005",
        ),
        (
            "Where is my Slack invitation after signing "
            "the Trainee Agreement?",
            "CYF-T5-005",
        ),
        (
            "How do I join the correct Slack workspace?",
            "CYF-T5-005",
        ),
        (
            "How can I get support with my coursework?",
            "CYF-T5-001",
        ),
        (
            "What is Slack, and how does it work?",
            "CYF-T3-004",
        ),
    ],
)
def test_slack_workspace_retrieval(question, expected_id):
    records = reviewed_faq()
    matches = retrieve(question, records)

    assert matches, f"No FAQ retrieved for: {question}"
    assert matches[0]["id"] == expected_id
