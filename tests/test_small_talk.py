
import ast
import re
from pathlib import Path


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def load_greeting_response():
    """Load the greeting function without importing Streamlit."""
    tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))

    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "get_greeting_response"
    )

    namespace = {
        "re": re,
        "GREETINGS": set(),
        "CAPABILITY_QUESTIONS": set(),
        "TOPIC_RESPONSES": {},
    }

    exec(
        compile(
            ast.Module(body=[function], type_ignores=[]),
            str(APP_PATH),
            "exec",
        ),
        namespace,
    )

    return namespace["get_greeting_response"]


def test_small_talk_messages_get_natural_responses():
    respond = load_greeting_response()

    for message in [
        "ok",
        "okay",
        "cool",
        "thanks",
        "ah one more thing",
    ]:
        reply = respond(message, "trainee")
        assert isinstance(reply, str), message
        assert reply.strip(), message


def test_small_talk_works_for_volunteers():
    respond = load_greeting_response()

    assert respond("ok", "volunteer")
    assert respond("one more thing", "volunteer")


def test_real_questions_are_not_swallowed():
    respond = load_greeting_response()

    assert respond("Ok, how do I register?", "trainee") is None
    assert respond("Thanks, when does the course start?", "trainee") is None
    assert respond("Cool, can I volunteer?", "volunteer") is None

