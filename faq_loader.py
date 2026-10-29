"""Load and validate CYF FAQ records. Only approved entries reach the model."""
import json
from pathlib import Path

FAQ_PATH = Path(__file__).resolve().parent / 'data' / 'faq_tier1.json'
REQUIRED = {'id', 'tier', 'category', 'question', 'answer', 'source_urls', 'status', 'review_notes', 'risk_level'}
ALLOWED_STATUSES = {'needs_review', 'reviewed', 'approved', 'rejected'}

def load_all(path=FAQ_PATH):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError('FAQ file must be a JSON list')
    seen = set()
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            raise ValueError(f'Record {index} is not an object')
        missing = REQUIRED - record.keys()
        if missing:
            raise ValueError(f'Record {index} missing: {sorted(missing)}')
        if record['id'] in seen:
            raise ValueError(f'Duplicate ID: {record["id"]}')
        seen.add(record['id'])
        if record['tier'] != 1 or record['status'] not in ALLOWED_STATUSES:
            raise ValueError(f'Invalid tier/status for {record["id"]}')
        if not all(isinstance(record[k], str) and record[k].strip() for k in ('id','category','question','answer')):
            raise ValueError(f'Missing required text for {record["id"]}')
        if not isinstance(record['source_urls'], list) or not all(isinstance(u,str) and u.startswith('https://') for u in record['source_urls']):
            raise ValueError(f'Invalid source URLs for {record["id"]}')
    return data

def approved_faq(path=FAQ_PATH):
    return [record for record in load_all(path) if record['status'] == 'approved']

def build_faq_context(records):
    if not records:
        return 'No CYF FAQ answers have been approved yet.'
    return '\n\n'.join(
        f'ID: {r["id"]}\nQuestion: {r["question"]}\nApproved answer: {r["answer"]}\nSources: {", ".join(r["source_urls"]) or "No URL supplied"}'
        for r in records
    )

def reviewed_faq(path=FAQ_PATH):
    return [
        record for record in load_all(path)
        if record["status"] in {"reviewed", "approved"}
    ]
