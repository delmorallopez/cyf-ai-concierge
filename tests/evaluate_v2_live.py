"""Paid API evaluation for reviewed FAQs in development mode; never auto-approves."""
import argparse
import json
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from faq_loader import load_all, approved_faq, build_faq_context
from app_policy import SYSTEM_POLICY

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['reviewed', 'approved'], default='reviewed')
    parser.add_argument('--limit', type=int, default=10, help='Limit API calls during first run; 0 means all cases')
    args = parser.parse_args()
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv(ROOT / '.env')
    if not os.getenv('OPENAI_API_KEY'):
        raise SystemExit('Set OPENAI_API_KEY in .env')
    if args.mode == 'reviewed' and os.getenv('CYF_DEV_MODE', '').lower() != 'true':
        raise SystemExit('Set CYF_DEV_MODE=true to evaluate reviewed content (local testing only).')
    records = ([r for r in load_all() if r['status'] in ('reviewed', 'approved')]
               if args.mode == 'reviewed' else approved_faq())
    if not records:
        raise SystemExit('No eligible FAQ records for selected mode.')
    cases = json.loads((ROOT / 'tests' / 'evaluation_v2.json').read_text(encoding='utf-8'))
    if args.limit > 0:
        cases = cases[:args.limit]
    client = OpenAI()
    system = SYSTEM_POLICY + '\n' + (
        'DEVELOPMENT EVALUATION ONLY: the following FAQ records are self-reviewed, NOT officially approved. '
        'Use them as provisional test content; never imply CYF has signed them off.\n'
        if args.mode == 'reviewed' else 'APPROVED FAQ:\n') + build_faq_context(records)
    results = []
    for i, case in enumerate(cases, 1):
        messages = [{'role': 'system', 'content': system}]
        for user_text in case['user_messages']:
            messages.append({'role': 'user', 'content': user_text})
            reply = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
                temperature=0.2, messages=messages
            ).choices[0].message.content or ''
            messages.append({'role': 'assistant', 'content': reply})
        results.append({**case, 'responses': [m['content'] for m in messages if m['role'] == 'assistant'],
                        'manual_result': 'not_reviewed', 'reviewer_notes': ''})
        print(f'[{i}/{len(cases)}] {case["case_id"]}')
    dest = ROOT / 'tests' / 'evaluation_v2_results.json'
    dest.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Saved {len(results)} cases to {dest}. Manual review required; API charges may apply.')

if __name__ == '__main__':
    main()
