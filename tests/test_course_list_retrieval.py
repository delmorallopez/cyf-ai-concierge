
import pytest

from faq_loader import retrieve, reviewed_faq


@pytest.mark.parametrize(
    "question",
    [
        "What courses does CYF have?",
        "What courses does CodeYourFuture offer?",
        "Which courses are available?",
        "Can you list the CYF courses?",
    ],
)
def test_course_list_retrieval(question):
    matches = retrieve(question, reviewed_faq())

    assert matches
    assert matches[0]["id"] == "CYF-T1-015"


def test_specific_course_retrieval_unchanged():
    matches = retrieve(
        "What is the Intro to Digital course?",
        reviewed_faq(),
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-016"


def test_course_fees_retrieval_unchanged():
    matches = retrieve(
        "Are your courses free?",
        reviewed_faq(),
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-007"

