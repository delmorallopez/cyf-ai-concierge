
from faq_loader import retrieve, reviewed_faq


def test_full_time_work_and_laptop_access_for_itd():
    question = (
        "I work full-time and don't have a laptop. "
        "Can I still join Intro to Digital?"
    )

    records = reviewed_faq()
    matches = retrieve(question, records)
    actual_ids = [record["id"] for record in matches]

    expected_ids = [
        "CYF-T1-012",  # Laptop access
        "CYF-T1-016",  # Intro to Digital format
        "CYF-T1-011",  # Study commitment
    ]

    for faq_id in expected_ids:
        assert faq_id in actual_ids, (
            f"Missing FAQ: {faq_id}\n"
            f"Retrieved: {actual_ids}"
        )
