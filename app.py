"""CYF AI Concierge: public-information pilot backed by reviewed/approved FAQs."""
import os
import re

import streamlit as st
from dotenv import load_dotenv


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

from chat_utils import TOPIC_RESPONSES, repeated_onboarding_followup, clarify_ambiguous_link
from chat_engine import generate_ai_reply


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


    # Handle short conversational messages without FAQ retrieval.
    acknowledgements = {
        "ok",
        "okay",
        "cool",
        "great",
        "got it",
        "understood",
        "alright",
    }

    thanks = {
        "thanks",
        "thank you",
        "thank you so much",
        "thx",
        "tks",
    }

    followup_introductions = {
        "one more thing",
        "ah one more thing",
        "oh one more thing",
        "i have another question",
        "can i ask another question",
    }

    if normalized in acknowledgements:
        return "Great! Let me know if you have any other questions."

    if normalized in thanks:
        return "You're welcome! Happy to help."

    if normalized in followup_introductions:
        return "Of course! What else would you like to know?"


    # Handle clearly unrelated questions without FAQ retrieval.
    # Keep patterns narrow to avoid blocking CYF-related questions.
    out_of_scope_patterns = (
        r"\b(?:weather|temperature|forecast)\b",
        r"\b(?:train|bus|flight)\s+ticket\s+(?:price|cost)\b",
        r"\bhow much does a (?:train|bus|flight) ticket cost\b",
    )

    if (
        not re.search(
            r"\b(?:cyf|codeyourfuture|course|class|volunteer)\b",
            normalized,
        )
        and any(
            re.search(pattern, normalized)
            for pattern in out_of_scope_patterns
        )
    ):
        return (
            "I can help with CodeYourFuture courses, applications, "
            "eligibility and volunteering, but I can't answer "
            "general weather or travel-price questions. "
            "What would you like to know about CodeYourFuture?"
        )

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


    # Resolve questions about starting immediately using the
    # previous assistant response.
    if user_role == "trainee":
        start_now_question = re.fullmatch(
            r"(?:can|could)\s+i\s+start"
            r"(?:\s+like)?\s+(?:right\s+)?now\s*[?!.]*",
            prompt.strip(),
            re.I,
        )

        if start_now_question:
            previous_assistant = next(
                (
                    message["content"]
                    for message in reversed(history)
                    if message["role"] == "assistant"
                ),
                "",
            )

            # Only infer ITD when the assistant explicitly
            # identifies it as the starting point.
            itd_starting_context = (
                re.search(
                    r"\b(?:courses?\s+start\s+with|"
                    r"start\s+with|begin\s+with)\s+"
                    r"Intro to Digital\b",
                    previous_assistant,
                    re.I,
                )
                or re.search(
                    r"\b(?:sign up for|register for)\s+"
                    r"Intro to Digital\b",
                    previous_assistant,
                    re.I,
                )
            )

            if itd_starting_context:
                return "Can I start Intro to Digital now?"


    # Explicit topic changes should not inherit previous context.
    if re.search(
        r"\b(new topic|different question|unrelated question)\b",
        prompt,
        re.I,
    ):
        return prompt


    # Resolve answers to a previous link clarification.
    if user_role == "trainee":
        previous_assistant = next(
            (
                message["content"]
                for message in reversed(history)
                if message["role"] == "assistant"
            ),
            "",
        )

        clarification_pattern = (
            r"Do you mean the "
            r"(Intro to Digital|Intro to Programming|"
            r"Software Development Course)"
            r" registration link or the curriculum link"
        )

        clarification_match = re.search(
            clarification_pattern,
            previous_assistant,
            re.I,
        )

        if clarification_match:
            course = clarification_match.group(1)

            normalized = re.sub(
                r"[^\w\s]", " ", prompt.lower()
            ).strip()

            if normalized in {
                "the curriculum",
                "curriculum",
                "curriculum link",
                "the curriculum link",
            }:
                return f"Where is the {course} curriculum link?"

            if normalized in {
                "registration",
                "the registration",
                "registration link",
                "the registration link",
                "sign up",
                "sign up link",
            }:
                return f"What is the registration link for {course}?"



    # Resolve short link requests using the previous conversation.
    if user_role == "trainee":
        link_followup = re.fullmatch(
            r"(?:can you\s+|could you\s+)?"
            r"(?:(?:share|send|give|show)\s+)?"
            r"(?:(?:me|us)\s+)?"
            r"(?:(?:the|a)\s+)?"
            r"link"
            r"(?:\s+(?:pls|please))?\s*[?!.]*",
            prompt.strip(),
            re.I,
        )

        if link_followup:
            # Prefer the previous user question for identifying intent.
            course_pattern = (
                r"\b(Intro to Digital|ITD|"
                r"Intro to Programming|ITP|"
                r"Software Development Course|SDC|"
                r"Checkpoint)\b"
            )

            course_match = re.search(
                course_pattern,
                previous,
                re.I,
            )

            if course_match:
                course = course_match.group(0)

                if re.search(
                    r"\b(register|registration|sign[\s-]?up)\b",
                    previous,
                    re.I,
                ):
                    return f"What is the registration link for {course}?"

                if re.search(
                    r"\b(curriculum|course content|course materials)\b",
                    previous,
                    re.I,
                ):
                    return f"Where is the {course} curriculum link?"




    # Resolve short registration questions using recent course context.
    if user_role == "trainee":
        registration_followup = re.fullmatch(
            r"(?:ok(?:ay)?[,\s]+)?"
            r"how\s+do\s+i\s+(?:register|sign\s+up)\s*\??",
            prompt.strip(),
            re.I,
        )

        if registration_followup:
            course_pattern = (
                r"\b(Intro to Digital|Intro to Programming|"
                r"Software Development Course|"
                r"ITD|ITP|SDC|Checkpoint)\b"
            )

            # Search backwards, ignoring small-talk messages.
            for message in reversed(history[-10:]):
                content = message["content"]

                course_match = re.search(
                    course_pattern,
                    content,
                    re.I,
                )

                if course_match:
                    course = course_match.group(1)

                    course_names = {
                        "itd": "Intro to Digital",
                        "itp": "Intro to Programming",
                        "sdc": "Software Development Course",
                    }

                    course = course_names.get(
                        course.lower(),
                        course,
                    )

                    return f"How do I register for {course}?"


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



    # Inherit course context only when the question clearly
    # refers to the previous topic or is a short course follow-up.
    followup_pattern = (
        r"\b(?:"
        r"it|its|they|them|their|that|this|those|"
        r"what about|how about|and|"
        r"can i start|could i start|"
        r"requirements|eligible|eligibility|"
        r"free|duration"
        r")\b"
    )

    course_question_pattern = (
        r"\b(?:"
        r"how long(?:\s+does\s+it)?|"
        r"how much(?:\s+does\s+it)?|"
        r"how many(?:\s+(?:hours|weeks|months))?"
        r")\s*(?:\?|$)"
    )

    is_short_followup = (
        len(prompt.split()) <= 8
        and (
            re.search(followup_pattern, prompt, re.I) is not None
            or re.search(course_question_pattern, prompt, re.I) is not None
        )
    )


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


        elif (
            clarification_reply := clarify_ambiguous_link(
                prompt,
                st.session_state.messages[:-1],
                st.session_state.user_role,
            )
        ) is not None:
            reply = clarification_reply


        elif not records:
            reply = get_no_records_reply(st.session_state.user_role)


        else:
            # 3. Retrieve relevant FAQ records
            if st.session_state.user_role == "volunteer":
                matches = retrieve_volunteer(search_query, records)
            else:
                matches = retrieve(search_query, records)

            if not matches:
                reply = get_no_match_reply(
                    st.session_state.user_role,
                    search_query,
                )


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
                        reply = generate_ai_reply(
                            search_query=search_query,
                            user_role=st.session_state.user_role,
                            evidence=evidence,
                            history=st.session_state.messages[:-1],
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