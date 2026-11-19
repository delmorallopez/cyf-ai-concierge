
import pytest

from faq_loader import retrieve, reviewed_faq


@pytest.mark.parametrize(
    "question, expected_id",
    [
        (
            "What is the registration link for Intro to Digital?",
            "CYF-T1-018",
        ),
        (
            "Where is the Intro to Digital curriculum?",
            "CYF-T3-001",
        ),
        (
            "Where is the Intro to Programming curriculum?",
            "CYF-T3-001",
        ),
        (
            "What is the Software Development Course curriculum link?",
            "CYF-T3-001",
        ),
    ],
)
def test_course_link_retrieval(question, expected_id):
    matches = retrieve(question, reviewed_faq())

    assert matches
    assert matches[0]["id"] == expected_id


def test_itp_registration_does_not_route_to_itd_registration():
    matches = retrieve(
        "What is the registration link for Intro to Programming?",
        reviewed_faq(),
    )

    assert all(
        record["id"] != "CYF-T1-018"
        for record in matches
    )



def test_start_itd_now_includes_curriculum_evidence():
    matches = retrieve(
        "Can I start Intro to Digital now?",
        reviewed_faq(),
    )

    ids = [record["id"] for record in matches]

    assert ids[:2] == [
        "CYF-T1-016",
        "CYF-T3-001",
    ]



def test_itd_registration_question_without_link_keyword():
    matches = retrieve(
        "How do I register for Intro to Digital?",
        reviewed_faq(),
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-018"
