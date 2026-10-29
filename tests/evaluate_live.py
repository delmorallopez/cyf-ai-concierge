"""Optional paid API smoke evaluation. Only approved FAQ entries are evaluated."""
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from faq_loader import approved_faq, build_faq_context, reviewed_faq
from app_policy import SYSTEM_POLICY

def main():
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv(ROOT/'.env')
    if not os.getenv('OPENAI_API_KEY'):
        raise SystemExit('Set OPENAI_API_KEY before live evaluation')
    approved = reviewed_faq()
    if not approved:
        raise SystemExit('No approved records. Live evaluation skipped safely.')
    cases=json.loads((ROOT/'tests'/'test_cases.json').read_text())
    approved_ids={r['id'] for r in approved}
    client=OpenAI()
    results=[]
    system=SYSTEM_POLICY+'\nAPPROVED FAQ:\n'+build_faq_context(approved)
    for case in cases:
        if case['id'] not in approved_ids:
            continue
        prompt=case['user_prompts'][0]
        reply=client.chat.completions.create(model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'),temperature=0.2,messages=[{'role':'system','content':system},{'role':'user','content':prompt}]).choices[0].message.content or ''
        # Manual review required: keyword matches are not factual correctness checks.
        results.append({'id':case['id'],'prompt':prompt,'response':reply,'manual_result':'not_reviewed','reviewer_notes':''})
    out=ROOT/'tests'/'live_results.json'
    out.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Saved {len(results)} responses to {out}; manual review required.')

if __name__=='__main__':
    main()
