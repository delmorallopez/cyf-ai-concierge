# CYF AI Concierge — Evaluation Dataset v2

**135 test cases:** 115 paraphrases (5 per each of 23 Tier 1 FAQs), 12 safety cases, and 8 multi-turn conversations. Questions are test prompts, **not new CYF policy claims**.

## Installation

Copy `evaluation_v2.json`, `evaluate_v2_live.py`, and `test_evaluation_v2.py` into your existing project's `tests/` folder. Keep `data/faq_tier1.json`, `faq_loader.py`, `app_policy.py`, `.env` and dependencies from v0.3.

## Offline dataset tests (no API)

```bash
python -m unittest discover -s tests -v
```

## Live evaluation (paid OpenAI API calls)

In your local `.env` set `CYF_DEV_MODE=true` and `OPENAI_API_KEY=...`. Reviewed mode is **for internal testing only**.

```bash
python tests/evaluate_v2_live.py --mode reviewed --limit 10
python tests/evaluate_v2_live.py --mode reviewed --limit 0
```

`--limit 0` evaluates all 135 cases, using **143 API calls** because eight multi-turn cases each have two messages. Review `tests/evaluation_v2_results.json` manually. No automatic factual accuracy scoring is claimed. Avoid putting real personal details into test prompts.

For production-signoff evaluation, use `--mode approved` after authorised CYF approval. The dataset tests do not require any records to be approved.

**Caveats:** Accreditation (CYF-T1-019) and exact English requirements (CYF-T1-006) require confirmation; this test set deliberately probes them. No live URL or policy verification was performed.
