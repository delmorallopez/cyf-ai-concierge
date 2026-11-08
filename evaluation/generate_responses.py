
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from faq_loader import retrieve, reviewed_faq
from app_policy import SYSTEM_POLICY

# Load the API key
load_dotenv()
client = OpenAI()

BASE_DIR = Path(__file__).resolve().parent

QUESTION = (
    "I was rejected on eligibility "
    "(income, Duolingo, etc.) — what are my options?"
)

NUMBER_OF_RESPONSES = 10

# Retrieve relevant approved FAQ evidence
matches = retrieve(QUESTION, reviewed_faq())

if not matches:
    raise RuntimeError(
        "No FAQ matches found for the test question."
    )

faq_context = "\n\n".join(
    f"FAQ ID: {record['id']}\n"
    f"Question: {record['question']}\n"
    f"Answer: {record['answer']}"
    for record in matches
)

# Load good and bad examples
examples = (BASE_DIR / "examples.md").read_text(
    encoding="utf-8"
)


def generate_group(group_name, include_examples):
    results = []

    for i in range(NUMBER_OF_RESPONSES):
        messages = [
            {
                "role": "system",
                "content": SYSTEM_POLICY,
            },
            {
                "role": "system",
                "content": (
                    "Approved FAQ context:\n"
                    + faq_context
                ),
            },
        ]

        if include_examples:
            messages.append({
                "role": "system",
                "content": (
                    "The following are examples of good "
                    "and bad chatbot responses. "
                    "Use them as behavioural guidance, "
                    "but use the approved FAQs as the "
                    "authority for factual claims.\n\n"
                    + examples
                ),
            })

        messages.append({
            "role": "user",
            "content": QUESTION,
        })

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.7,
            messages=messages,
        )

        answer = (
            response.choices[0].message.content or ""
        )

        results.append({
            "response_id": i + 1,
            "group": group_name,
            "question": QUESTION,
            "retrieved_faq_ids": [
                record["id"] for record in matches
            ],
            "answer": answer,
        })

        print(
            f"{group_name}: "
            f"{i + 1}/{NUMBER_OF_RESPONSES}"
        )

    return results


# Generate 10 responses without examples
baseline = generate_group(
    "baseline",
    include_examples=False,
)

# Generate 10 responses with examples
with_examples = generate_group(
    "with_examples",
    include_examples=True,
)

# Save all 20 responses
output = BASE_DIR / "experiment_responses.json"

output.write_text(
    json.dumps(
        baseline + with_examples,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

print(f"\nSaved 20 responses to {output}")
