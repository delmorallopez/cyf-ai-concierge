
import re

import pytest

from chat_utils import TOPIC_RESPONSES
from faq_loader import reviewed_faq, retrieve


def extract_suggested_questions():
    """Extract questions from all topic response menus."""
    questions = []

    for topic, response in TOPIC_RESPONSES.items():
        matches = re.findall(
            r"(?m)^\s*-\s+(.+\?)\s*$",
            response,
        )

        for question in matches:
            questions.append((topic, question.strip()))

    return questions


SUGGESTED_QUESTIONS = extract_suggested_questions()

EXPECTED_FAQ_IDS = {
    "Can CodeYourFuture provide a laptop?": "CYF-T3-010",
    "How do I request a laptop for ITP?": "CYF-T3-010",
    "What is the Software Development Course?": "CYF-T2-005",
    "How many hours per week do I need to study?": "CYF-T1-011",
    "Where can I find trainee support?": "CYF-T3-005",
    "What career support is available?": "CYF-T1-021",
    "What happens after completing the programme?": "CYF-T3-013",
}


def test_topic_responses_have_suggestions():
    """Every topic must suggest at least one question."""
    assert TOPIC_RESPONSES, "No topics configured"

    for topic, response in TOPIC_RESPONSES.items():
        assert re.search(
            r"(?m)^\s*-\s+.+\?\s*$",
            response,
        ), f"No suggested questions for topic: {topic}"



@pytest.mark.parametrize(
    "question, expected_ids",
    [
        (
            "Is there a Slack community for trainees?",
            ["CYF-T5-001"],
        ),
        (
            "Can I ask volunteers for help with assignments?",
            ["CYF-T5-001"],
        ),
        (
            "What should I do if I'm falling behind?",
            ["CYF-T5-001"],
        ),
        (
            "Can I take a break from the programme?",
            ["CYF-T5-013"],
        ),
        (
            "What happens if I decide to leave the course?",
            ["CYF-T5-013"],
        ),
    ],
)
def test_trainee_support_retrieval(question, expected_ids):
    matches = retrieve(question, reviewed_faq())
    actual_ids = [record["id"] for record in matches]

    assert actual_ids == expected_ids, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_ids}"
        f"\nActual: {actual_ids}"
    )


@pytest.mark.parametrize(
    "question, expected_ids",
    [
        (
            "I'm 45 years old and have never worked in IT. Can I join?",
            ["CYF-T1-001", "CYF-T1-014"],
        ),
        (
            "I have a full-time job and two children. Is the programme suitable for me?",
            ["CYF-T1-001", "CYF-T2-028", "CYF-T1-011"],
        ),
        (
            "I don't speak English very well. Can I still apply?",
            ["CYF-T2-018"],
        ),
    ],
)
def test_complex_eligibility_retrieval(question, expected_ids):
    matches = retrieve(question, reviewed_faq())
    actual_ids = [record["id"] for record in matches]

    assert actual_ids == expected_ids, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_ids}"
        f"\nActual: {actual_ids}"
    )

def test_income_means_testing_retrieval():
    question = (
        "Do I meet the income/means-testing "
        "eligibility criteria?"
    )

    matches = retrieve(question, reviewed_faq())

    assert [r["id"] for r in matches] == ["CYF-T1-005"]


def test_eligibility_rejection_retrieval():
    question = (
        "I was rejected on eligibility "
        "(income, Duolingo, etc.) — what are my options?"
    )

    matches = retrieve(question, reviewed_faq())

    assert [r["id"] for r in matches] == [
        "CYF-T2-029",
    ]


@pytest.mark.parametrize(
    "topic, question",
    SUGGESTED_QUESTIONS,
)
def test_suggested_question_has_faq(topic, question):
    """Every suggested question must retrieve an FAQ."""
    records = reviewed_faq()
    matches = retrieve(question, records)

    assert matches, (
        f"\nTopic: {topic}"
        f"\nQuestion: {question}"
        "\nNo matching reviewed FAQ was retrieved."
    )


@pytest.mark.parametrize("question", [
    "My wife makes £30k/year",
    "My husband earns £25,000",
    "Our household income is £35k",
    "My partner's salary is £40,000",
])
def test_household_income_routes_to_eligibility(question):
    matches = retrieve(question, reviewed_faq())

    assert matches
    assert matches[0]["id"] == "CYF-T1-001"


@pytest.mark.parametrize(
    "question, expected_id",
    EXPECTED_FAQ_IDS.items(),
)
def test_suggested_question_retrieves_correct_faq(
    question,
    expected_id,
):
    records = reviewed_faq()
    matches = retrieve(question, records)

    assert matches, f"No FAQ retrieved for: {question}"

    actual_id = matches[0]["id"]

    assert actual_id == expected_id, (
        f"\nQuestion: {question}"
        f"\nExpected FAQ: {expected_id}"
        f"\nActual FAQ: {actual_id}"
    )


@pytest.mark.parametrize(
    "question, expected_id",
    [
        (
        "I'm currently receiving Universal Credit. Can I apply?",
        "CYF-T1-004",
        ),
        (
            "Do I need to provide proof of my income?",
            "CYF-T2-018",
        ),
        (
            "Do I have to pay anything for the courses?",
            "CYF-T1-007",
        ),
        (
            "Can I apply if I'm working part-time?",
            "CYF-T1-001",
        ),
    ],
)
def test_financial_circumstances_retrieval(question, expected_id):
    matches = retrieve(question, reviewed_faq())

    assert matches, f"No FAQ retrieved for: {question}"

    assert matches[0]["id"] == expected_id, (
        f"Question: {question}\n"
        f"Expected: {expected_id}\n"
        f"Received: {matches[0]['id']}"
    )


@pytest.mark.parametrize("question", [
    "I live in Turkey. Can I get in your course?",
    "I live in Spain. Can I apply?",
    "Can I join from Germany?",
    "I'm based in France. Am I eligible?",
    "I'm based in Cape Town. Can I apply?",
])
def test_location_eligibility(question):
    matches = retrieve(question, reviewed_faq())

    assert matches, f"No FAQ retrieved for: {question}"

    actual_ids = [record["id"] for record in matches]

    assert actual_ids[:2] == [
        "CYF-T1-008",
        "CYF-T1-001",
    ], (
        f"Question: {question}\n"
        f"Retrieved: {actual_ids}"
    )


@pytest.mark.parametrize("question", [
    "I'm working. When do I have to go to classes?",
    "Can I study at CYF while working full-time?",
    "I'm employed. When are the classes?",
])
def test_working_and_class_schedule(question):
    matches = retrieve(question, reviewed_faq())

    actual_ids = [record["id"] for record in matches]

    assert actual_ids == [
        "CYF-T1-010",
        "CYF-T1-011",
        "CYF-T1-009",
    ], (
        f"Question: {question}\n"
        f"Retrieved: {actual_ids}"
    )


def test_suggested_questions_are_unique():
    """Avoid duplicate questions across topic menus."""
    questions = [
        question.lower()
        for _, question in SUGGESTED_QUESTIONS
    ]

    assert len(questions) == len(set(questions)), (
        "Duplicate suggested questions found."
    )



@pytest.mark.parametrize(
    "question, expected_ids",
    [
        (
            "How long does the application process take?",
            ["CYF-T2-018", "CYF-T2-026"],
        ),
        (
            "What happens after I submit my application?",
            ["CYF-T2-026", "CYF-T2-018"],
        ),
        (
            "Can I apply more than once?",
            ["CYF-T2-026"],
        ),
        (
            "What should I do if my application is rejected?",
            ["CYF-T2-029"],
        ),
        (
            "Can I change my application details after submitting?",
            ["CYF-T2-026", "CYF-T2-027"],
        ),
        (
            "I haven't received a confirmation email. What should I do?",
            ["CYF-T2-026", "CYF-T2-027"],
        ),
    ],
)
def test_application_enquiry_retrieval(question, expected_ids):
    matches = retrieve(question, reviewed_faq())
    actual_ids = [record["id"] for record in matches]

    assert actual_ids == expected_ids, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_ids}"
        f"\nActual: {actual_ids}"
    )


@pytest.mark.parametrize(
    "question, expected_ids",
    [
        (
            "Do I need to know Python or JavaScript before joining?",
            ["CYF-T1-014"],
        ),
        (
            "What programming languages will I learn?",
            ["CYF-T2-030"],
        ),
        (
            "How long does the full CYF programme take?",
            ["CYF-T1-018", "CYF-T2-005"],
        ),
        (
            "Can I study at my own pace?",
            ["CYF-T1-009"],
        ),
        (
            "What happens if I struggle with the coursework?",
            ["CYF-T3-005", "CYF-T5-001"],
        ),
    ],
)
def test_learning_pathway_retrieval(question, expected_ids):
    matches = retrieve(question, reviewed_faq())
    actual_ids = [record["id"] for record in matches]

    assert actual_ids == expected_ids, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_ids}"
        f"\nActual: {actual_ids}"
    )


@pytest.mark.parametrize(
    "question, expected_ids",
    [
        (
            "Can I use a tablet instead of a laptop?",
            ["CYF-T1-012", "CYF-T3-010"],
        ),
        (
            "What laptop specifications do I need?",
            ["CYF-T2-016"],
        ),
        (
            "Do I have to return the laptop after the course?",
            ["CYF-T5-008", "CYF-T3-010"],
        ),
        (
            "Can I keep the laptop after graduation?",
            ["CYF-T3-010", "CYF-T5-008"],
        ),
    ],
)
def test_laptop_support_retrieval(question, expected_ids):
    matches = retrieve(question, reviewed_faq())
    actual_ids = [record["id"] for record in matches]

    assert actual_ids == expected_ids, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_ids}"
        f"\nActual: {actual_ids}"
    )


@pytest.mark.parametrize(
    "question, expected_ids",
    [
        (
            "Will CYF help me prepare my CV?",
            ["CYF-T1-021", "CYF-T3-011"],
        ),
        (
            "Does CYF provide interview preparation?",
            ["CYF-T1-021", "CYF-T3-011"],
        ),
        (
            "Do companies hire CYF graduates?",
            ["CYF-T3-012", "CYF-T1-021"],
        ),
    ],
)
def test_career_support_retrieval(question, expected_ids):
    matches = retrieve(question, reviewed_faq())
    actual_ids = [record["id"] for record in matches]

    assert actual_ids == expected_ids, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_ids}"
        f"\nActual: {actual_ids}"
    )


@pytest.mark.parametrize(
    "question, expected_ids",
    [
        (
            "Can I join CYF if I live outside the UK?",
            ["CYF-T1-008", "CYF-T1-001", "CYF-T1-009"],
        ),
        (
            "Are there any online-only courses?",
            ["CYF-T1-009", "CYF-T1-016"],
        ),
        (
            "What happens if I miss a Saturday class?",
            ["CYF-T1-009", "CYF-T1-010"],
        ),
        (
            "Can I attend classes in a different CYF region?",
            ["CYF-T1-008", "CYF-T1-010"],
        ),
        (
            "I live two hours from London. Can I still apply?",
            ["CYF-T1-001", "CYF-T1-008"],
        ),
    ],
)
def test_location_attendance_retrieval(question, expected_ids):
    matches = retrieve(question, reviewed_faq())

    actual_ids = [record["id"] for record in matches]

    assert actual_ids == expected_ids, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_ids}"
        f"\nActual: {actual_ids}"
    )
