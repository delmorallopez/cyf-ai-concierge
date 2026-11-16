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
        + "- Preserve important qualifications, conditions, exceptions, "
        "and uncertainty stated in the FAQ evidence.\n"


        + "- When the FAQ describes a process, service, or programme, "
        "preserve the essential actions, responsibilities, "
        "eligibility conditions, and explicit exclusions.\n"
        + "- If the FAQ explains what a service is NOT intended for, "
        "include that distinction when relevant to the user's question.\n"
        
        + "- Answer the user's question directly, then include a short "
        "summary of essential next steps or responsibilities when "
        "the FAQ provides them.\n"
        + "- When a FAQ lists multiple mandatory trainee responsibilities, "
        "cover each distinct responsibility rather than summarising "
        "them as general advice.\n"
        + "- Prefer a short list for processes or responsibilities "
        "when that makes the answer easier to follow.\n"



        "- When explaining technical requirements or minimum "
        "specifications, preserve all mandatory constraints, "
        "including exclusions, compatibility requirements, "
        "and security restrictions.\n"
        "- Do not omit requirements that could cause a user "
        "to purchase unsuitable equipment or make an "
        "incorrect eligibility decision.\n"
        + "- If the FAQ says a requirement needs confirmation, "
        "do not present it as definitively confirmed.\n"
        + "- For eligibility, legal status, financial support, or "
        "course requirements, clearly distinguish confirmed information "
        "from information that CYF still needs to verify.\n"
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
