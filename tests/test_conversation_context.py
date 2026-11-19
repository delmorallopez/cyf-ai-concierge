"""Tests for conversation-context handling in the Streamlit app."""

import ast
import re
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def load_contextual_query():
    """Load only contextual_query without executing Streamlit."""
    source = APP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "contextual_query"
    )

    module = ast.Module(body=[function], type_ignores=[])
    namespace = {"re": re}

    exec(compile(module, str(APP_PATH), "exec"), namespace)
    return namespace["contextual_query"]


contextual_query = load_contextual_query()


def test_trainee_followup_keeps_course():
    history = [
        {
            "role": "user",
            "content": "How long is the Software Development Course?",
        },
        {
            "role": "assistant",
            "content": "It lasts 12 weeks.",
        },
    ]

    result = contextual_query(
        "And is it free?",
        history,
        "trainee",
    )

    assert "Software Development Course" in result


def test_explicit_topic_change_does_not_inherit_course():
    history = [
        {
            "role": "user",
            "content": "How long is the Software Development Course?",
        }
    ]

    result = contextual_query(
        "Different question: how can I volunteer?",
        history,
        "trainee",
    )

    assert result == "Different question: how can I volunteer?"


def test_volunteer_followup_adds_role_context():
    history = [
        {
            "role": "user",
            "content": "Can I volunteer remotely?",
        }
    ]

    result = contextual_query(
        "What about the minimum commitment?",
        history,
        "volunteer",
    )

    assert "volunteering at CodeYourFuture" in result


def test_no_history_returns_original_question():
    result = contextual_query(
        "How can I volunteer?",
        [],
        "volunteer",
    )

    assert result == "How can I volunteer?"


def test_trainee_history_not_added_to_volunteer_query():
    history = [
        {
            "role": "user",
            "content": "How long is the Software Development Course?",
        }
    ]

    result = contextual_query(
        "What about the minimum commitment?",
        history,
        "volunteer",
    )

    assert "Software Development Course" not in result



def test_registration_link_followup():
    history = [
        {
            "role": "user",
            "content": "How do I register for Intro to Digital?",
        },
        {
            "role": "assistant",
            "content": "You can sign up for Intro to Digital online.",
        },
    ]

    result = contextual_query(
        "Share the link pls",
        history,
        "trainee",
    )

    assert "Intro to Digital" in result
    assert "registration" in result.lower()
    assert "link" in result.lower()


def test_curriculum_link_followup():
    history = [
        {
            "role": "user",
            "content": "Where can I find the Intro to Programming curriculum?",
        },
        {
            "role": "assistant",
            "content": "The ITP curriculum is available online.",
        },
    ]

    result = contextual_query(
        "The link?",
        history,
        "trainee",
    )

    assert "Intro to Programming" in result
    assert "curriculum" in result.lower()
    assert "link" in result.lower()


def test_start_now_followup():
    history = [
        {
            "role": "user",
            "content": "What is Intro to Digital?",
        },
        {
            "role": "assistant",
            "content": (
                "Intro to Digital is CYF's introductory course. "
                "You can start studying the open curriculum immediately."
            ),
        },
    ]

    result = contextual_query(
        "Can I start like now?",
        history,
        "trainee",
    )

    assert "Intro to Digital" in result
    assert "start" in result.lower()



def test_ambiguous_link_followup_needs_clarification():
    history = [
        {
            "role": "user",
            "content": "What's up with the courses?",
        },
        {
            "role": "assistant",
            "content": (
                "You can register for Intro to Digital "
                "and start studying the curriculum immediately."
            ),
        },
        {
            "role": "user",
            "content": "When can I start?",
        },
        {
            "role": "assistant",
            "content": "You can start studying immediately.",
        },
    ]

    result = contextual_query(
        "Share the link pls",
        history,
        "trainee",
    )

    assert result == "Share the link pls"


def test_answer_to_link_clarification():
    history = [
        {
            "role": "user",
            "content": "Share the link pls",
        },
        {
            "role": "assistant",
            "content": (
                "Do you mean the Intro to Digital registration link "
                "or the curriculum link where you can start studying?"
            ),
        },
    ]

    result = contextual_query(
        "The curriculum",
        history,
        "trainee",
    )

    assert result == "Where is the Intro to Digital curriculum link?"



def test_registration_answer_to_link_clarification():
    history = [
        {
            "role": "user",
            "content": "Share the link pls",
        },
        {
            "role": "assistant",
            "content": (
                "Do you mean the Intro to Digital registration link "
                "or the curriculum link where you can start studying?"
            ),
        },
    ]

    result = contextual_query(
        "Registration",
        history,
        "trainee",
    )

    assert result == "What is the registration link for Intro to Digital?"
