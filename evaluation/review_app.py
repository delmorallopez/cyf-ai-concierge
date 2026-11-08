
import json
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

RESPONSES_FILE = BASE_DIR / "generated_responses.json"
REVIEWS_FILE = BASE_DIR / "human_reviews.json"

st.set_page_config(
    page_title="CYF Human Evaluation",
    page_icon="🧪",
    layout="centered",
)

st.title("CYF AI Concierge — Human Evaluation")
st.caption("Blind review: AI evaluator decisions are hidden.")

responses = json.loads(
    RESPONSES_FILE.read_text(encoding="utf-8")
)

if REVIEWS_FILE.exists():
    reviews = json.loads(
        REVIEWS_FILE.read_text(encoding="utf-8")
    )
else:
    reviews = {}

pending = [
    item for item in responses
    if str(item["response_id"]) not in reviews
]

st.progress(
    (len(responses) - len(pending)) / len(responses)
)

st.write(
    f"Reviewed: {len(responses) - len(pending)} "
    f"of {len(responses)}"
)

if not pending:
    st.success("All responses have been reviewed!")
    st.info(
        "Human reviews saved. You can now compare "
        "them with the AI evaluations."
    )
    st.stop()

item = pending[0]
response_id = str(item["response_id"])

st.divider()

st.subheader(f"Response {response_id}")

st.markdown("**Question**")
st.write(item["question"])

st.markdown("**Generated answer**")
st.info(item["answer"])

with st.form(key=f"review_{response_id}"):
    decision = st.radio(
        "Your decision",
        ["Approve", "Reject"],
        horizontal=True,
    )

    reason = st.text_area(
        "Reason (required if rejected)",
        placeholder=(
            "Incorrect information, missing eligibility "
            "criteria, unsupported claim..."
        ),
    )

    submitted = st.form_submit_button(
        "Save review and continue",
        type="primary",
    )

    if submitted:
        if decision == "Reject" and not reason.strip():
            st.error(
                "Please provide a reason for rejection."
            )
        else:
            reviews[response_id] = {
                "decision": decision,
                "reason": reason.strip(),
            }

            REVIEWS_FILE.write_text(
                json.dumps(
                    reviews,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            st.rerun()
