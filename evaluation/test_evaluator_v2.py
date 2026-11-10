
from dotenv import load_dotenv
from openai import OpenAI

from evaluation.evaluate_responses import evaluate_answer

load_dotenv()

QUESTION = (
    "I was rejected on eligibility "
    "(income, Duolingo, etc.) — what are my options?"
)

TEST_CASES = [
    {
        "id": 1,
        "answer": (
            "You can appeal your rejection within 14 days. "
            "CYF guarantees a response within 48 hours."
        ),
        "expected": "Reject",
    },
    {
        "id": 2,
        "answer": (
            "You can retake the Duolingo test three times "
            "and automatically reapply next month."
        ),
        "expected": "Reject",
    },
    {
        "id": 3,
        "answer": (
            "CYF does not specify a guaranteed appeals "
            "process in the available FAQs. You can review "
            "the eligibility guidance and contact CYF "
            "to ask about your options."
        ),
        "expected": "Approve",
    },
]


def main():
    client = OpenAI()

    # Fixed FAQ IDs for reproducible evaluator tests
    faq_ids = [
        "CYF-T1-005",   # Income eligibility
        "CYF-T2-018",  # Eligibility assessment
        "CYF-T2-026",  # Application information
    ]

    print("\nCYF Evaluator v2 — Challenge Tests")
    print("-" * 45)
    print("Retrieved FAQ IDs:", faq_ids)

    if not faq_ids:
        raise RuntimeError(
            "No FAQ evidence retrieved for challenge tests."
        )

    passed = 0

    for case in TEST_CASES:
        verdict = evaluate_answer(
            question=QUESTION,
            answer=case["answer"],
            faq_ids=faq_ids,
            client=client,
        )

        approved = all(
            verdict[field]
            for field in ("correct", "complete", "grounded")
        )

        actual = "Approve" if approved else "Reject"
        success = actual == case["expected"]

        if success:
            passed += 1

        print(f"\nCase {case['id']}")
        print(f"Expected: {case['expected']}")
        print(f"Actual:   {actual}")
        print(f"Result:   {'PASS' if success else 'FAIL'}")
        print(f"Reason:   {verdict['reason']}")

    print("\n" + "-" * 45)
    print(f"Challenge tests passed: {passed}/{len(TEST_CASES)}")


if __name__ == "__main__":
    main()
