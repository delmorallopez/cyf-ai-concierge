
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from faq_loader import reviewed_faq

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

EVALUATOR_POLICY = """
You are an independent evaluator of CodeYourFuture
AI Concierge responses.

Evaluate the answer using ONLY the approved FAQ evidence.

Evaluate three criteria:

CORRECTNESS:
- Mark correct=false if the answer contains materially
  false or unsupported policy claims.
- Do not assume appeals, retakes, reconsideration,
  deadlines, or reapplication rights exist unless
  supported by the FAQ evidence.
- Distinguish confirmed policies from suggestions
  to contact CYF to ask about available options.

COMPLETENESS:
- Judge completeness relative to the user's question.
- Concise and useful answers can be complete.
- Do not require unrelated application details.
- Do not penalise answers for omitting information
  that the FAQs do not establish.
- Explaining uncertainty and providing reasonable
  next steps may be sufficient.

GROUNDING:
- Every material factual claim about CYF policies
  must be supported by the provided FAQ evidence.
- Suggestions to contact CYF are not claims that
  a particular procedure exists.

CONSISTENCY:
- Read the answer carefully before identifying
  missing information.
- Never claim something is missing if the answer
  explicitly includes it.
- Only report issues that materially affect
  the answer.

Return a JSON object with exactly these fields:
{
  "correct": true,
  "complete": true,
  "grounded": true,
  "source_ids": [],
  "issues": [],
  "reason": "Short explanation"
}

Use booleans for correct, complete and grounded.
Only include source IDs from the provided FAQ evidence.
"""


def evaluate_answer(question, answer, faq_ids, client=None):
    """
    Evaluate one generated answer using approved FAQ evidence.

    Returns a dictionary containing the AI verdict.
    """
    if client is None:
        client = OpenAI()

    faq_by_id = {
        record["id"]: record
        for record in reviewed_faq()
    }

    evidence = []

    for faq_id in faq_ids:
        record = faq_by_id.get(faq_id)

        if record:
            evidence.append({
                "id": faq_id,
                "question": record["question"],
                "answer": record["answer"],
                "source_urls": record.get("source_urls", []),
            })

    if not evidence:
        raise ValueError(
            "No approved FAQ evidence found for evaluation."
        )

    prompt = {
        "question": question,
        "generated_answer": answer,
        "approved_faq_evidence": evidence,
    }

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": EVALUATOR_POLICY,
            },
            {
                "role": "user",
                "content": json.dumps(
                    prompt,
                    ensure_ascii=False,
                ),
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Evaluator returned an empty response."
        )

    verdict = json.loads(content)

    required_fields = (
        "correct",
        "complete",
        "grounded",
        "source_ids",
        "issues",
        "reason",
    )

    for field in required_fields:
        if field not in verdict:
            raise ValueError(
                f"Evaluator response missing field: {field}"
            )

    return verdict


def main():
    input_file = BASE_DIR / "experiment_responses.json"
    output_file = (
        BASE_DIR / "experiment_ai_evaluations_v2.json"
    )

    responses = json.loads(
        input_file.read_text(encoding="utf-8")
    )

    client = OpenAI()
    results = []

    for item in responses:
        verdict = evaluate_answer(
            question=item["question"],
            answer=item["answer"],
            faq_ids=item["retrieved_faq_ids"],
            client=client,
        )

        results.append({
            "response_id": item["response_id"],
            "group": item["group"],
            "evaluation": verdict,
        })

        print(
            f"{item['group']} — "
            f"Response {item['response_id']}: "
            f"correct={verdict['correct']}, "
            f"complete={verdict['complete']}, "
            f"grounded={verdict['grounded']}"
        )

    output_file.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"\nSaved {len(results)} evaluations "
        f"to {output_file}"
    )


if __name__ == "__main__":
    main()
