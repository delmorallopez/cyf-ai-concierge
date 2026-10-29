"""Offline checks for second evaluation dataset; run from project root."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = json.loads((ROOT / "evaluation_v2.json").read_text(encoding="utf-8"))
FAQ = json.loads((ROOT.parent / "data" / "faq_tier1.json").read_text(encoding="utf-8"))

class EvaluationDatasetTests(unittest.TestCase):
    def test_unique_case_ids(self):
        ids = [x["case_id"] for x in CASES]
        self.assertEqual(len(ids), len(set(ids)))
    def test_five_paraphrases_per_faq(self):
        ids = {r["id"] for r in FAQ}
        for faq_id in ids:
            self.assertEqual(5, sum(x["faq_id"] == faq_id and x["type"] == "paraphrase" for x in CASES))
    def test_all_faq_ids_exist(self):
        ids = {r["id"] for r in FAQ}
        self.assertTrue(all(x["faq_id"] in ids for x in CASES if x["faq_id"]))
    def test_safety_and_multiturn(self):
        self.assertEqual(12, sum(x["type"] == "safety" for x in CASES))
        self.assertEqual(8, sum(x["type"] == "multi_turn" for x in CASES))
    def test_valid_messages(self):
        for case in CASES:
            self.assertTrue(case["user_messages"])
            self.assertTrue(all(isinstance(m, str) and m.strip() for m in case["user_messages"]))
            self.assertTrue(case["expected_behavior"].strip())

if __name__ == "__main__":
    unittest.main()
