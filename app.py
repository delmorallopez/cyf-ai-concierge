"""CYF AI Concierge: public-information pilot backed by reviewed/approved FAQs."""
import os
import re

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from app_policy import SYSTEM_POLICY, NO_MATCH_REPLY, NO_RECORDS_REPLY, controlled_reply
from faq_loader import approved_faq, reviewed_faq, build_faq_context, retrieve
from chat_utils import TOPIC_RESPONSES

load_dotenv()
st.set_page_config(page_title="CYF AI Concierge", page_icon="💬")
st.title("CodeYourFuture AI Concierge")
st.caption("Information pilot · Not an official application or eligibility decision")

dev_mode = os.getenv("CYF_DEV_MODE", "").lower() == "true"
records = reviewed_faq() if dev_mode else approved_faq()
if dev_mode:
    st.warning("DEVELOPMENT MODE: Answers use reviewed but not officially approved CYF content.")
if not records:
    st.warning("No FAQ answers are available in this mode.")

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "hiya",
    "good morning",
    "good afternoon",
    "good evening",
}

CAPABILITY_QUESTIONS = {
    "what do you do",
    "what can you do",
    "how can you help me",
    "what can i ask you",
    "who are you",
}

def get_greeting_response(message: str) -> str | None:
    normalized = re.sub(
        r"[^\w\s]", "",
        message.lower()
    ).strip()

    normalized = " ".join(normalized.split())

    if normalized in GREETINGS:
        return (
            "Hello! 👋 Welcome to the CodeYourFuture AI Concierge. "
            "I can help you with course information, eligibility, "
            "applications, and trainee support. "
            "What would you like to know?"
        )

    if normalized in CAPABILITY_QUESTIONS:
        return (
            "I'm the CodeYourFuture AI Concierge! 👋 "
            "I can help you with:\n\n"
            "- CYF courses and learning pathways\n"
            "- Eligibility requirements\n"
            "- Applications and enrolment\n"
            "- Course schedules and commitments\n"
            "- Laptop support and trainee resources\n"
            "- Career support and next steps\n\n"
            "What would you like to know about CodeYourFuture?"
        )
    
    if normalized in TOPIC_RESPONSES:
        return TOPIC_RESPONSES[normalized]

    return None


def contextual_query(prompt, history):
    """Resolve short follow-ups from the previous user topic without exposing chat history."""
    followup = bool(re.search(r"\b(it|that|this|they|those)\b", prompt.lower())) or len(prompt.split()) <= 6
    if not followup:
        return prompt
    previous = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
    if not previous:
        return prompt
    # Prefer the explicit course in the previous question; avoid arbitrary context.
    course = re.search(r"\b(ITP|ITD|SDC|Intro to Programming|Intro to Digital|Software Development Course)\b", previous, re.I)
    if course and not re.search(r"\b(ITP|ITD|SDC|Intro to Programming|Intro to Digital|Software Development Course)\b", prompt, re.I):
        return f"{prompt} {course.group(0)}"
    return prompt


if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about CodeYourFuture courses"):

    # Save the user's message
    search_query = contextual_query(prompt, st.session_state.messages)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        # 1. Handle greetings before FAQ retrieval
        greeting_reply = get_greeting_response(prompt)

        if greeting_reply is not None:
            reply = greeting_reply

        # 2. Check whether FAQ records are available
        elif not records:
            reply = NO_RECORDS_REPLY

        else:
            # 3. Retrieve relevant FAQ records
            matches = retrieve(search_query, records)

            if not matches:
                reply = NO_MATCH_REPLY

            else:
                # 4. Check whether the answer needs special handling
                controlled = controlled_reply(matches[0])

                if controlled is not None:
                    reply = controlled

                # 5. Check OpenAI API configuration
                elif not os.getenv("OPENAI_API_KEY"):
                    reply = (
                        "An OpenAI API key is required "
                        "to run this pilot."
                    )

                else:
                    # 6. Build evidence from retrieved FAQs
                    evidence = [
                        r for r in matches
                        if controlled_reply(r) is None
                    ]

                    # 7. Generate a grounded answer using OpenAI
                    try:
                        response = OpenAI().chat.completions.create(
                            model=os.getenv(
                                "OPENAI_MODEL",
                                "gpt-4.1-mini"
                            ),
                            temperature=0.0,
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        SYSTEM_POLICY
                                        + "\nFAQ EVIDENCE:\n"
                                        + build_faq_context(evidence)
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": search_query
                                }
                            ],
                        )

                        reply = (
                            response.choices[0].message.content
                            or NO_MATCH_REPLY
                        )

                    except Exception as error:
                        print(
                            f"OpenAI request error type: "
                            f"{type(error).__name__}",
                            flush=True
                        )

                        reply = (
                            "The assistant is temporarily unavailable. "
                            "Please try again later."
                        )

        # 8. Display the assistant's response
        st.markdown(reply)

    # 9. Save the assistant's response
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })