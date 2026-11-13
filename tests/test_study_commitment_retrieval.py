from faq_loader import retrieve, reviewed_faq


def test_sdc_weekly_study_commitment():
    records = reviewed_faq()

    matches = retrieve(
        "How many hours per week do I need to study? "
        "Software Development Course",
        records,
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-011"


def test_general_weekly_study_commitment():
    records = reviewed_faq()

    matches = retrieve(
        "What is the weekly study commitment?",
        records,
    )

    assert matches
    assert matches[0]["id"] == "CYF-T1-011"
