"""Deterministic offline coverage tests: one case per Tier 1 FAQ + approval gating."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from faq_loader import load_all, approved_faq, build_faq_context

CASES = json.loads((ROOT/'tests'/'test_cases.json').read_text(encoding='utf-8'))

class TestFAQ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_all()
        cls.by_id = {r['id']:r for r in cls.records}

     
    def test_all_tiers_and_unique_records(self):
        from collections import Counter

        # Total FAQ records
        self.assertEqual(len(self.records), 86)

        # Check for duplicate IDs
        ids = [record["id"] for record in self.records]
        self.assertEqual(len(ids), len(set(ids)))

        # Validate records per tier
        tier_counts = Counter(
            record["tier"] for record in self.records
        )

        self.assertEqual(
            dict(tier_counts),
            {
                1: 23,
                2: 28,
                3: 15,
                4: 7,
                5: 13,
            }
        )

    def test_unapproved_records_are_excluded(self):
        self.assertEqual(approved_faq(), [])
        self.assertNotIn('Question:', build_faq_context(approved_faq()))

    def test_approval_gate_with_temporary_fixture(self):
        sample = [dict(self.records[0]), dict(self.records[1])]
        sample[0]['status'] = 'approved'
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'faq.json'
            path.write_text(json.dumps(sample),encoding='utf-8')
            approved = approved_faq(path)
            self.assertEqual([r['id'] for r in approved], [sample[0]['id']])
            context = build_faq_context(approved)
            self.assertIn(sample[0]['question'], context)
            self.assertNotIn(sample[1]['question'], context)

    def test_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'faq.json'
            path.write_text(json.dumps([self.records[0], self.records[0]]),encoding='utf-8')
            with self.assertRaises(ValueError):
                load_all(path)


def make_case_test(case):
    def test(self):
        record = self.by_id[case['id']]
        self.assertEqual(record['tier'], 1)
        self.assertEqual(record['question'], case['canonical_question'])
        self.assertTrue(record['answer'].strip())
        self.assertIn(record['status'], ('needs_review','reviewed','approved','rejected'))
        self.assertGreaterEqual(len(case['user_prompts']), 2)
        self.assertTrue(case['expected_topics'])
        self.assertIn(case['expected_behavior'], ('answer_if_approved','escalate_if_unverified'))
    return test

for case in CASES:
    setattr(TestFAQ, 'test_' + case['id'].lower().replace('-','_'), make_case_test(case))

if __name__ == '__main__':
    unittest.main()
