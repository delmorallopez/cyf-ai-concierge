
from faq_loader import retrieve, reviewed_faq


def test_uk_benefits_course_eligibility():
    records = reviewed_faq()

    matches = retrieve(
        "Can I take this course if I am on UK benefits?",
        records,
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-004"


def test_universal_credit_course_eligibility():
    records = reviewed_faq()

    matches = retrieve(
        "Can I join CodeYourFuture while receiving Universal Credit?",
        records,
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-004"


def test_low_income_question_still_works():
    records = reviewed_faq()

    matches = retrieve(
        "How does CodeYourFuture measure low income?",
        records,
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-005"

