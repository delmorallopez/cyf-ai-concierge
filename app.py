"""CYF AI Concierge: public-information pilot backed by reviewed/approved FAQs."""
import os
import re

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


from app_policy import (
    get_system_policy,
    get_no_match_reply,
    get_no_records_reply,
    controlled_reply,
    sensitive_account_reply,
)


from faq_loader import (
    approved_faq,
    reviewed_faq,
    build_faq_context,
    retrieve,
    retrieve_volunteer,
)

from chat_utils import TOPIC_RESPONSES, repeated_onboarding_followup

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

   


def contextual_query(prompt: str, history: list, user_role: str = "trainee") -> str:
    """Resolve short follow-ups using the previous user question."""

    # Only use previous user messages, never assistant-generated text.
    previous = next(
        (
            message["content"]
            for message in reversed(history)
            if message["role"] == "user"
        ),
        "",
    )

    if not previous:
        return prompt

    # Explicit topic changes should not inherit previous context.
    if re.search(
        r"\b(new topic|different question|unrelated question)\b",
        prompt,
        re.I,
    ):
        return prompt

    # Keep the previous course when the user asks a short follow-up.
    courses = (
        r"ITP|ITD|SDC|Intro to Programming|"
        r"Intro to Digital|Software Development Course"
    )

    previous_course = re.search(
        rf"\b({courses})\b",
        previous,
        re.I,
    )

    current_course = re.search(
        rf"\b({courses})\b",
        prompt,
        re.I,
    )

    is_short_followup = len(prompt.split()) <= 8

    if (
        user_role == "trainee"
        and is_short_followup
        and previous_course
        and not current_course
    ):
        return f"{prompt} {previous_course.group(0)}"

    # Add role context to short volunteer follow-ups.
    if (
        user_role == "volunteer"
        and is_short_followup
        and re.search(
            r"\b(it|that|this|what about|and|how about)\b",
            prompt,
            re.I,
        )
    ):
        return f"{prompt} volunteering at CodeYourFuture"

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


chat_placeholder = (
    "Ask about volunteering at CodeYourFuture"
    if st.session_state.user_role == "volunteer"
    else "Ask about CodeYourFuture courses"
)

if prompt := st.chat_input(chat_placeholder):


    # Save the user's message
    
    search_query = contextual_query(
        prompt,
        st.session_state.messages,
        st.session_state.user_role,
    )


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
        

        elif (
            followup_reply := repeated_onboarding_followup(
                prompt,
                st.session_state.messages[:-1],
                st.session_state.user_role,
            )
        ) is not None:
            reply = followup_reply


        elif sensitive_account_reply(prompt) is not None:
            reply = sensitive_account_reply(prompt)

        elif not records:
            reply = get_no_records_reply(st.session_state.user_role)


        else:
            # 3. Retrieve relevant FAQ records
            if st.session_state.user_role == "volunteer":
                matches = retrieve_volunteer(search_query, records)
            else:
                matches = retrieve(search_query, records)


            if not matches:
                reply = get_no_match_reply(st.session_state.user_role)

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

                        # Include recent conversation for natural follow-up responses.
                        # FAQ evidence remains the only source of CYF-specific facts.
                        recent_history = st.session_state.messages[:-1][-4:]

                        conversation_messages = [
                            {
                                "role": "system",
                                "content": (
                                    get_system_policy(st.session_state.user_role)
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

                                ),
                            },
                        ]

                        conversation_messages.extend(
                            {
                                "role": message["role"],
                                "content": message["content"],
                            }
                            for message in recent_history
                            if message["role"] in {"user", "assistant"}
                        )

                        conversation_messages.append(
                            {
                                "role": "user",
                                "content": search_query,
                            }
                        )

                        response = OpenAI().chat.completions.create(
                            model=os.getenv(
                                "OPENAI_MODEL",
                                "gpt-4.1-mini"
                            ),
                            temperature=0.0,
                            messages=conversation_messages,
                        )

                       
                        reply = (
                            response.choices[0].message.content
                            or get_no_match_reply(st.session_state.user_role)
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