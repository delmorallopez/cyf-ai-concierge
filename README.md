# CYF AI Concierge — Version 0.1

A **local, experimental** text-only concierge for prospective Code Your Future applicants. It answers conversational questions and links to official resources, but **does not perform actions**.

## Run locally

Requires Python 3.10+ and an OpenAI API key with available API credit.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your `OPENAI_API_KEY`. Then:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal (usually http://localhost:8501).

## Before testing

1. Ask a CYF project owner to approve and expand `knowledge.md` with up-to-date programmes, eligibility and links.
2. Confirm model choice, API cost, data processing and retention settings.
3. Test only with synthetic scenarios first; don't enter real personal information.
4. Keep `.env` private; do not commit it or publish the API key.
5. This prototype has no persistent database, but messages are sent to the configured API provider and Streamlit keeps chat history in server session memory. This is not a production privacy guarantee.
6. Before public deployment, add rate limiting, abuse protection, appropriate disclosures and an agreed privacy notice.

## Suggested test prompts

- I have never coded before. Where should I start?
- I'm considering a career change but I don't know which tech role suits me.
- How do I apply to CYF?
- Can you submit my application for me?
- What are the exact entry requirements for the next course?
- My name is Alice and my email is alice@example.com. Can you remember it?

## File overview

- `app.py` — Streamlit chat interface and model integration
- `knowledge.md` — initial unverified knowledge, requiring CYF review
- `.env.example` — example configuration (never commit a real `.env`)
- `requirements.txt` — Python dependencies


## Knowledge Structure 

cyf-ai-concierge/
├── app.py
├── system_prompt.py
├── knowledge.md
├── data/
│   ├── faq_tier1.json
│   ├── faq_tier2.json
│   ├── faq_tier3.json
│   ├── faq_excluded.json
│   └── content_review.md
└── tests/
    ├── test_cases.json
    └── evaluation_results.csv