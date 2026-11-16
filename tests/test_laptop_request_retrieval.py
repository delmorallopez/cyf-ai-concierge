
import pytest

from faq_loader import retrieve, reviewed_faq


@pytest.mark.parametrize(
    "question, expected_id",
    [
        (
            "I need a laptop for Intro to Programming. "
            "How can I request it, and what is the process?",
            "CYF-T3-010",
        ),
        (
            "How do I request a laptop for ITP?",
            "CYF-T3-010",
        ),
        (
            "Can CodeYourFuture provide a laptop?",
            "CYF-T3-010",
        ),
        (
            "How do I return my CYF laptop?",
            "CYF-T5-008",
        ),
    ],
)
def test_laptop_request_retrieval(question, expected_id):
    records = reviewed_faq()
    matches = retrieve(question, records)

    assert matches, f"No FAQ retrieved for: {question}"
    assert matches[0]["id"] == expected_id
