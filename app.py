"""CYF AI Concierge: public-information pilot backed by reviewed/approved FAQs."""
import os
import re

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from app_policy import (
    get_system_policy,
    NO_MATCH_REPLY,
    NO_RECORDS_REPLY,
    controlled_reply,
)

from faq_loader import (
    approved_faq,
    reviewed_faq,
    build_faq_context,
    retrieve,
    retrieve_volunteer,
)

from chat_utils import TOPIC_RESPONSES

load_dotenv()
st.set_page_config(page_title="CYF AI Concierge", page_icon="💬")
st.title("CYF AI Concierge Model B")
st.caption("Information pilot · Not an official application or eligibility decision")


dev_mode = os.getenv("CYF_DEV_MODE", "").lower() == "true"

if st.session_state.get("user_role") == "volunteer":
    faq_path = "data/faq_volunteers.json"
else:
    faq_path = "data/faq_alltiers.json"

records = (
    reviewed_faq(faq_path)
    if dev_mode
    else approved_faq(faq_path)
)

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


def get_greeting_response(message: str, user_role: str) -> str | None:
    normalized = re.sub(r"[^\w\s]", "", message.lower()).strip()
    normalized = " ".join(normalized.split())

    # Handle greetings
    if normalized in GREETINGS:
        if user_role == "volunteer":
            return (
                "Hello! 👋 Welcome to the CodeYourFuture AI Concierge. "
                "I can help you with volunteering opportunities, "
                "eligibility, onboarding, volunteer roles, "
                "and supporting trainees. "
                "What would you like to know?"
            )

        return (
            "Hello! 👋 Welcome to the CodeYourFuture AI Concierge. "
            "I can help you with course information, eligibility, "
            "applications, and trainee support. "
            "What would you like to know?"
        )

    # Handle questions about chatbot capabilities
    if normalized in CAPABILITY_QUESTIONS:
        if user_role == "volunteer":
            return (
                "I'm the CodeYourFuture AI Concierge! 👋 "
                "I can help you with:\n\n"
                "- Volunteer eligibility and requirements\n"
                "- Volunteering opportunities and roles\n"
                "- Registration and onboarding\n"
                "- Slack and volunteer communication\n"
                "- Supporting trainees and reviewing code\n"
                "- Volunteer training and resources\n\n"
                "What would you like to know about volunteering?"
            )

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

    # Handle predefined topic responses
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



# Initialise conversation state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialise user role
if "user_role" not in st.session_state:
    st.session_state.user_role = None


# Ask the user to select their role
if st.session_state.user_role is None:
    st.subheader("Welcome to CodeYourFuture!")

    st.write(
        "To help you find the right information, "
        "please tell us who you are."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🎓 I'm a trainee",
            use_container_width=True
        ):
            st.session_state.user_role = "trainee"
            st.rerun()

    with col2:
        if st.button(
            "🤝 I'm a volunteer",
            use_container_width=True
        ):
            st.session_state.user_role = "volunteer"
            st.rerun()

    st.stop()


# Display the selected role
st.caption(
    f"Current role: {st.session_state.user_role.capitalize()}"
)

# Allow users to switch roles
if st.button("Switch role"):
    st.session_state.user_role = None
    st.session_state.messages = []
    st.rerun()

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
        greeting_reply = get_greeting_response(
            prompt,
            st.session_state.user_role
        )

        if greeting_reply is not None:
            reply = greeting_reply

        # 2. Check whether FAQ records are available
        elif not records:
            reply = NO_RECORDS_REPLY

        else:
            # 3. Retrieve relevant FAQ records
            if st.session_state.user_role == "volunteer":
                matches = retrieve_volunteer(search_query, records)
            else:
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
                                        get_system_policy(st.session_state.user_role)
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