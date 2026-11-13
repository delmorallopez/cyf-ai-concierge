import re

TOPIC_RESPONSES = {
    "cyf courses and learning pathways": (
        "CodeYourFuture offers a learning pathway that includes "
        "Intro to Digital (ITD), Intro to Programming (ITP), "
        "Checkpoint, and the Software Development Course (SDC).\n\n"
        "You can ask me:\n"
        "- Can I skip a course?\n"
        "- What is Intro to Digital?\n"
        "- What is the Software Development Course?\n"
    ),

    "eligibility requirements": (
        "I can help you understand CodeYourFuture's "
        "eligibility requirements.\n\n"
        "You can ask me:\n"
        "- Who can apply to CodeYourFuture?\n"
        "- Do I need the right to work in the UK?\n"
        "- What level of English do I need?"
    ),

    "applications and enrolment": (
        "I can guide you through the CodeYourFuture "
        "application and enrolment process.\n\n"
        "You can ask me:\n"
        "- How do I apply to CodeYourFuture?\n"
        "- What happens after I complete Intro to Digital?\n"
        "- How do I check my application progress?"
    ),

    "course schedules and commitments": (
        "I can help you understand course durations, "
        "study commitments, and schedules.\n\n"
        "You can ask me:\n"
        "- How long does Intro to Programming take?\n"
        "- How many hours per week do I need to study?\n"
        "- When does the next course start?"
    ),

    "laptop support and trainee resources": (
        "I can provide information about laptop support "
        "and resources available to CYF trainees.\n\n"
        "You can ask me:\n"
        "- Can CodeYourFuture provide a laptop?\n"
        "- How do I request a laptop for ITP?\n"
        "- Where can I find trainee support?"
    ),

    "career support and next steps": (
        "I can explain the career support available "
        "through CodeYourFuture.\n\n"
        "You can ask me:\n"
        "- Does CodeYourFuture guarantee a job?\n"
        "- What career support is available?\n"
        "- What happens after completing the programme?"
    ),
}

def repeated_onboarding_followup(
    message: str,
    history: list,
    user_role: str,
) -> str | None:
    """Avoid repeating an already explained volunteer onboarding process."""

    if user_role != "volunteer":
        return None

    normalized = re.sub(r"[^\w\s]", "", message.lower())
    normalized = " ".join(normalized.split())

    vague_followups = {
        "and what happens next",
        "what happens next",
        "and then",
        "what about after that",
    }

    if normalized not in vague_followups:
        return None

    if len(history) < 2:
        return None

    previous_user = next(
        (
            item["content"].lower()
            for item in reversed(history)
            if item["role"] == "user"
        ),
        "",
    )

    previous_assistant = next(
        (
            item["content"].lower()
            for item in reversed(history)
            if item["role"] == "assistant"
        ),
        "",
    )

    onboarding_question = (
        "become a volunteer" in previous_user
        or "sign up" in previous_user
        or "onboarding" in previous_user
    )

    onboarding_already_explained = (
        "welcome session" in previous_assistant
        and "training" in previous_assistant
    )

    if onboarding_question and onboarding_already_explained:
        return (
            "Once you've completed the onboarding steps, "
            "you can begin contributing to your local "
            "CodeYourFuture community. I've already outlined "
            "the main steps, but I can explain any particular "
            "part in more detail."
        )

    return None
