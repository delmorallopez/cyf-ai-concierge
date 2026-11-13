"""Shared OpenAI response generation for the CYF AI Concierge."""

import os

from openai import OpenAI

from app_policy import get_system_policy, get_no_match_reply
from faq_loader import build_faq_context


def generate_ai_reply(
    search_query: str,
    user_role: str,
    evidence: list,
    history: list,
) -> str:
    """Generate a CYF answer using retrieved FAQ evidence."""

    recent_history = history[-4:]

    system_message = (
        get_system_policy(user_role)
        + "\nFAQ EVIDENCE:\n"
        + build_faq_context(evidence)
        + "\n\nCONVERSATION RULES:\n"
        + "- Use recent conversation only to understand context.\n"
        + "- Do not treat previous assistant answers as factual evidence.\n"
        + "- Avoid repeating information already explained.\n"
        + "- For vague follow-ups such as 'And what happens next?', "
        "check whether the requested information was already given.\n"
        + "- If the previous answer already covered all relevant FAQ steps, "
        "briefly acknowledge this instead of repeating the same process.\n"
        + "- Never invent additional steps to continue a conversation.\n"
        + "- If the current FAQ evidence is insufficient, say so."
    )

    messages = [{"role": "system", "content": system_message}]

    messages.extend(
        {"role": message["role"], "content": message["content"]}
        for message in recent_history
        if message["role"] in {"user", "assistant"}
    )

    messages.append({"role": "user", "content": search_query})

    response = OpenAI().chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=0.0,
        messages=messages,
    )

    return (
        response.choices[0].message.content
        or get_no_match_reply(user_role)
    )
