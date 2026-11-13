"""Regression tests for Streamlit role isolation."""

from streamlit.testing.v1 import AppTest
from pathlib import Path

def test_switching_roles_clears_conversation_history():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(app_path, default_timeout=10)
    at.run()

    assert not at.exception

    # Select trainee.
    trainee_button = next(
        button for button in at.button
        if "trainee" in button.label.lower()
    )
    trainee_button.click().run()

    assert not at.exception
    assert at.session_state["user_role"] == "trainee"

    # Simulate an existing trainee conversation.
    at.session_state["messages"] = [
        {
            "role": "user",
            "content": "How long is the Software Development Course?",
        },
        {
            "role": "assistant",
            "content": "The course lasts 12 weeks.",
        },
    ]

    at.run()
    assert not at.exception
    assert len(at.session_state["messages"]) == 2

    # Switch roles.
    switch_button = next(
        button for button in at.button
        if button.label == "Switch role"
    )
    switch_button.click().run()

    assert not at.exception
    assert at.session_state["user_role"] is None
    assert at.session_state["messages"] == []

    # Select volunteer.
    volunteer_button = next(
        button for button in at.button
        if "volunteer" in button.label.lower()
    )
    volunteer_button.click().run()

    assert not at.exception
    assert at.session_state["user_role"] == "volunteer"
    assert at.session_state["messages"] == []
