
from faq_loader import retrieve, reviewed_faq


def test_sdc_fee_followup_retrieves_fee_faq():
    records = reviewed_faq("data/faq_alltiers.json")

    matches = retrieve(
        "And is it free? Software Development Course",
        records,
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-007"


def test_general_course_fee_question_retrieves_fee_faq():
    records = reviewed_faq("data/faq_alltiers.json")

    matches = retrieve(
        "Are CodeYourFuture courses free?",
        records,
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-007"
