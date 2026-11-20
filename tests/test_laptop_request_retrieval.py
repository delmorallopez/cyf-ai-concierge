
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


@pytest.mark.parametrize(
    "question, expected_ids",
    [
        (
            "Do I need my own laptop?",
            ["CYF-T1-012", "CYF-T3-010"],
        ),
        (
            "I don't have a computer. Can I join Intro to Digital?",
            ["CYF-T1-012"],
        ),
        (
            "Can CodeYourFuture lend me a laptop?",
            ["CYF-T3-010", "CYF-T1-012"],
        ),
    ],
)
def test_laptop_access_retrieval(question, expected_ids):
    records = reviewed_faq()
    matches = retrieve(question, records)
    actual_ids = [record["id"] for record in matches]

    assert actual_ids == expected_ids, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_ids}"
        f"\nActual: {actual_ids}"
    )


@pytest.mark.parametrize(
    "question, expected_first_id",
    [
        ("Do I have to buy a laptop for CYF?", "CYF-T1-012"),
        (
            "Can I study Intro to Digital without a computer?",
            "CYF-T1-012",
        ),
        ("I don't own a laptop. Can I still apply?", "CYF-T1-012"),
        ("Does CYF offer laptop loans?", "CYF-T3-010"),
        (
            "Can I borrow a computer from CodeYourFuture?",
            "CYF-T3-010",
        ),
    ],
)
def test_laptop_question_variations(question, expected_first_id):
    records = reviewed_faq()
    matches = retrieve(question, records)

    assert matches, f"No FAQ retrieved for: {question}"
    assert matches[0]["id"] == expected_first_id, (
        f"\nQuestion: {question}"
        f"\nExpected first FAQ: {expected_first_id}"
        f"\nActual: {[record['id'] for record in matches]}"
    )
