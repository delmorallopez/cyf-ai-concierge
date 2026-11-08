
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_json(filename):
    return json.loads(
        (BASE_DIR / filename).read_text(encoding="utf-8")
    )


responses = load_json("experiment_responses.json")
ai_results = load_json("experiment_ai_evaluations.json")
human_reviews = load_json("experiment_human_reviews.json")

ai_by_key = {
    f"{item['group']}:{item['response_id']}": item["evaluation"]
    for item in ai_results
}

summary = {}
lines = [
    "# CYF AI Concierge — A/B Evaluation Results",
    "",
    f"**Question:** {responses[0]['question']}",
    "",
]

for group in ("baseline", "with_examples"):
    group_responses = [
        item for item in responses
        if item["group"] == group
    ]

    reviewed = 0
    human_approved = 0
    ai_approved = 0
    disagreements = 0

    lines.extend([f"## {group}", ""])

    for item in group_responses:
        key = f"{group}:{item['response_id']}"

        if key not in human_reviews or key not in ai_by_key:
            raise RuntimeError(f"Missing evaluation: {key}")

        human = human_reviews[key]
        ai = ai_by_key[key]

        human_pass = human["decision"] == "Approve"
        ai_pass = all(
            ai[field]
            for field in ("correct", "complete", "grounded")
        )

        reviewed += 1
        human_approved += int(human_pass)
        ai_approved += int(ai_pass)
        disagreements += int(human_pass != ai_pass)

        lines.extend([
            f"### Response {item['response_id']}",
            "",
            item["answer"],
            "",
            f"- Human: {human['decision']}",
            f"- Human reason: {human.get('reason', '')}",
            f"- AI: {'Approve' if ai_pass else 'Reject'}",
            f"- AI reason: {ai.get('reason', '')}",
            f"- Supporting FAQs: {', '.join(ai.get('source_ids', []))}",
            "",
        ])

    summary[group] = {
        "reviewed": reviewed,
        "human_approved": human_approved,
        "ai_approved": ai_approved,
        "disagreements": disagreements,
    }


print("\nCYF AI Concierge — A/B Evaluation")
print("-" * 48)

for group, result in summary.items():
    n = result["reviewed"]

    print(f"\n{group}")
    print(
        f"  Human approval: "
        f"{result['human_approved']}/{n} "
        f"({result['human_approved'] / n:.0%})"
    )
    print(
        f"  AI approval: "
        f"{result['ai_approved']}/{n} "
        f"({result['ai_approved'] / n:.0%})"
    )
    print(
        f"  AI-human disagreement: "
        f"{result['disagreements']}/{n} "
        f"({result['disagreements'] / n:.0%})"
    )


baseline = summary["baseline"]
examples = summary["with_examples"]

improvement = (
    examples["human_approved"] / examples["reviewed"]
    - baseline["human_approved"] / baseline["reviewed"]
) * 100

print(
    f"\nHuman approval difference: "
    f"{improvement:+.1f} percentage points"
)

total_disagreements = sum(
    item["disagreements"] for item in summary.values()
)
total_reviews = sum(
    item["reviewed"] for item in summary.values()
)

print(
    f"Overall AI-human disagreement: "
    f"{total_disagreements}/{total_reviews} "
    f"({total_disagreements / total_reviews:.1%})"
)

report = [
    "## Summary",
    "",
    "| Metric | Baseline | With examples |",
    "|---|---:|---:|",
]

for label, field in (
    ("Human approved", "human_approved"),
    ("AI approved", "ai_approved"),
    ("AI-human disagreements", "disagreements"),
):
    report.append(
        f"| {label} | "
        f"{baseline[field]}/{baseline['reviewed']} | "
        f"{examples[field]}/{examples['reviewed']} |"
    )

report.extend([
    "",
    f"**Human approval difference:** {improvement:+.1f} percentage points",
    "",
    f"**Overall AI-human disagreement:** "
    f"{total_disagreements}/{total_reviews}",
    "",
])

output = BASE_DIR / "experiment_results.md"
output.write_text(
    "\n".join(lines[:4] + report + lines[4:]),
    encoding="utf-8",
)

print(f"\nReport saved to: {output}")
