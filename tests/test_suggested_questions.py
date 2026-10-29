
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
            response
        )

        for question in matches:
            questions.append((topic, question.strip()))

    return questions


SUGGESTED_QUESTIONS = extract_suggested_questions()

EXPECTED_FAQ_IDS = {
    "Can CodeYourFuture provide a laptop?": "CYF-T3-010",
    "How do I request a laptop for ITP?": "CYF-T3-010",
    "What is the Software Development Course?": "CYF-T2-005",
    "How many hours per week do I need to study?": "CYF-T2-028",
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
            response
        ), f"No suggested questions for topic: {topic}"


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


@pytest.mark.parametrize("question", [
    "I live in Turkey. Can I get in your course?",
    "I live in Spain. Can I apply?",
    "Can I join from Germany?",
    "I'm based in France. Am I eligible?",
])
def test_location_eligibility(question):
    matches = retrieve(question, reviewed_faq())

    assert matches, f"No FAQ retrieved for: {question}"
    assert matches[0]["id"] == "CYF-T1-001"    


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
