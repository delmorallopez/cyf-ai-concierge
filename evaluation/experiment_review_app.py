
import json
import random
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

RESPONSES_FILE = BASE_DIR / "experiment_responses.json"
REVIEWS_FILE = BASE_DIR / "experiment_human_reviews.json"
ORDER_FILE = BASE_DIR / "experiment_review_order.json"

st.set_page_config(
    page_title="CYF Blind Evaluation",
    page_icon="🧪",
    layout="centered",
)

st.title("CYF AI Concierge — Blind Evaluation")
st.caption("Review answers without knowing their experiment group.")

responses = json.loads(
    RESPONSES_FILE.read_text(encoding="utf-8")
)

# Each response needs a unique identifier across groups.
response_by_key = {
    f"{item['group']}:{item['response_id']}": item
    for item in responses
}

# Generate a random order once and persist it.
if ORDER_FILE.exists():
    review_order = json.loads(
        ORDER_FILE.read_text(encoding="utf-8")
    )
else:
    review_order = list(response_by_key.keys())
    random.shuffle(review_order)

    ORDER_FILE.write_text(
        json.dumps(review_order, indent=2),
        encoding="utf-8",
    )

# Load previous human reviews, if any.
if REVIEWS_FILE.exists():
    reviews = json.loads(
        REVIEWS_FILE.read_text(encoding="utf-8")
    )
else:
    reviews = {}

pending = [
    key for key in review_order
    if key not in reviews
]

total = len(review_order)
completed = total - len(pending)

st.progress(completed / total)
st.write(f"Reviewed: {completed} of {total}")

if not pending:
    st.success("All 20 responses have been reviewed!")
    st.info("Your human evaluations have been saved.")
    st.stop()

key = pending[0]
item = response_by_key[key]

st.divider()
st.subheader(f"Review {completed + 1} of {total}")

st.markdown("**Question**")
st.write(item["question"])

st.markdown("**Generated answer**")
st.info(item["answer"])

with st.form(key=f"review_{completed}"):
    decision = st.radio(
        "Your decision",
        ["Approve", "Reject"],
        horizontal=True,
    )

    reason = st.text_area(
        "Reason (required if rejected)",
        placeholder="Missing information, unsupported claims...",
    )

    submitted = st.form_submit_button(
        "Save review and continue",
        type="primary",
    )

    if submitted:
        if decision == "Reject" and not reason.strip():
            st.error("Please explain why you rejected the answer.")
        else:
            reviews[key] = {
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
