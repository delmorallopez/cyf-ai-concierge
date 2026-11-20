
import pytest

from faq_loader import reviewed_faq, retrieve


@pytest.mark.parametrize(
    "question",
    [
        (
            "If I complete Intro to Digital, am I automatically "
            "accepted onto Intro to Programming?"
        ),
        "Does finishing Intro to Digital guarantee a place in ITP?",
        "What do I need to do after Intro to Digital to join ITP?",
    ],
)
def test_itd_to_itp_progression_retrieval(question):
    records = reviewed_faq()
    matches = retrieve(question, records)

    ids = [record["id"] for record in matches]

    assert "CYF-T2-013" in ids, (
        f"\nQuestion: {question}"
        f"\nExpected CYF-T2-013 in retrieved evidence"
        f"\nActual: {ids}"
    )
