
import ast
from pathlib import Path


CHAT_ENGINE = (
    Path(__file__).resolve().parents[1] / "chat_engine.py"
)


def test_ai_prompt_instructs_relevant_links():
    source = CHAT_ENGINE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "generate_ai_reply"
    )

    prompt_text = " ".join(
        node.value
        for node in ast.walk(function)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    ).lower()

    assert "relevant direct url" in prompt_text
    assert "do not invent urls" in prompt_text
