
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from faq_loader import reviewed_faq

load_dotenv()
client = OpenAI()

BASE_DIR = Path(__file__).resolve().parent

responses = json.loads(
    (BASE_DIR / "experiment_responses.json").read_text(
        encoding="utf-8"
    )
)

faq_by_id = {
    record["id"]: record
    for record in reviewed_faq()
}

results = []

for item in responses:
    evidence = []

    for faq_id in item["retrieved_faq_ids"]:
        record = faq_by_id.get(faq_id)

        if record:
            evidence.append({
                "id": faq_id,
                "question": record["question"],
                "answer": record["answer"],
                "source_urls": record.get("source_urls", []),
            })

    prompt = {
        "question": item["question"],
        "generated_answer": item["answer"],
        "approved_faq_evidence": evidence,
    }

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an independent evaluator of "
                    "CodeYourFuture chatbot responses. "
                    "Use ONLY the provided FAQ evidence. "
                    "Do not assume undocumented CYF policies. "
                    "Evaluate whether the answer is factually "
                    "correct, sufficiently complete, and "
                    "supported by the evidence. "
                    "Return a JSON object with these fields: "
                    "correct (boolean), "
                    "complete (boolean), "
                    "grounded (boolean), "
                    "source_ids (array of FAQ IDs supporting "
                    "the answer), "
                    "issues (array of specific problems), "
                    "reason (short explanation). "
                    "Mark correct=false if the response makes "
                    "a material unsupported or false claim. "
                    "Mark grounded=false if it contains a "
                    "material claim not supported by the FAQs. "
                    "Only include source IDs from the "
                    "provided evidence."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(prompt),
            },
        ],
    )

    verdict = json.loads(
        response.choices[0].message.content
    )

    results.append({
        "response_id": item["response_id"],
        "group": item["group"],
        "evaluation": verdict,
    })

    print(
        f"Response {item['response_id']}: "
        f"correct={verdict['correct']}, "
        f"complete={verdict['complete']}, "
        f"grounded={verdict['grounded']}"
    )

output = BASE_DIR / "experiment_ai_evaluations.json"

output.write_text(
    json.dumps(results, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print(f"\nSaved {len(results)} AI evaluations to {output}")
