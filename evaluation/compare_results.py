
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def load_json(filename):
    return json.loads(
        (BASE_DIR / filename).read_text(encoding="utf-8")
    )

responses = load_json("generated_responses.json")
ai_evaluations = load_json("ai_evaluations.json")
human_reviews = load_json("human_reviews.json")

ai_by_id = {
    str(item["response_id"]): item["evaluation"]
    for item in ai_evaluations
}

total = len(responses)
reviewed = 0
disagreements = 0
approved = 0
lines = [
    "# CYF AI Concierge — Evaluation Results",
    "",
    f"**Question:** {responses[0]['question']}",
    "",
]

for item in responses:
    response_id = str(item["response_id"])

    if response_id not in human_reviews or response_id not in ai_by_id:
        continue

    reviewed += 1

    human = human_reviews[response_id]
    ai = ai_by_id[response_id]

    human_approved = human["decision"] == "Approve"
    ai_approved = (
        ai["correct"]
        and ai["complete"]
        and ai["grounded"]
    )

    if human_approved:
        approved += 1

    if human_approved != ai_approved:
        disagreements += 1

    lines.extend([
        f"## Response {response_id}",
        "",
        item["answer"],
        "",
        f"- Human: {human['decision']}",
        f"- AI: {'Approve' if ai_approved else 'Reject'}",
        f"- FAQ sources: {', '.join(ai.get('source_ids', []))}",
        f"- AI reason: {ai.get('reason', '')}",
        f"- Human reason: {human.get('reason', '')}",
        "",
    ])

disagreement_rate = (
    disagreements / reviewed * 100 if reviewed else 0
)

summary = [
    "## Summary",
    "",
    f"- Generated responses: {total}",
    f"- Reviewed responses: {reviewed}",
    f"- Human approved: {approved}",
    f"- AI-human disagreements: {disagreements}",
    f"- Disagreement rate: {disagreement_rate:.1f}%",
    "",
]

lines[3:3] = summary

output = BASE_DIR / "evaluation_results.md"
output.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(f"Reviewed: {reviewed}/{total}")
print(f"Human approved: {approved}/{reviewed}")
print(f"AI-human disagreements: {disagreements}")
print(f"Disagreement rate: {disagreement_rate:.1f}%")
print(f"Saved: {output}")
