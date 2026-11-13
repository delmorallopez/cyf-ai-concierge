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
