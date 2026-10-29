"""Load, validate, and search the CYF FAQ knowledge base."""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

FAQ_PATH = Path(__file__).resolve().parent / "data" / "faq_alltiers.json"
REQUIRED = {"id", "tier", "category", "question", "answer", "source_urls", "status", "review_notes", "risk_level"}
ALLOWED_STATUSES = {"needs_review", "reviewed", "approved", "rejected"}
ALLOWED_RESPONSES = {"answer", "restricted", "handoff"}
ALLOWED_RISKS = {"low", "medium", "high"}


def load_all(path=FAQ_PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("FAQ file must contain a JSON list")
    seen = set()
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            raise ValueError(f"Record {index} must be an object")
        missing = REQUIRED - record.keys()
        if missing:
            raise ValueError(f"Record {index} missing fields: {sorted(missing)}")
        rid = record["id"]
        if not isinstance(rid, str) or not rid.strip() or rid in seen:
            raise ValueError(f"Invalid or duplicate FAQ ID: {rid!r}")
        seen.add(rid)
        if type(record["tier"]) is not int or record["tier"] not in range(1, 6):
            raise ValueError(f"Invalid tier for {rid}")
        if record["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status for {rid}")
        if record.get("response_type", "answer") not in ALLOWED_RESPONSES:
            raise ValueError(f"Invalid response_type for {rid}")
        if record["risk_level"] not in ALLOWED_RISKS:
            raise ValueError(f"Invalid risk_level for {rid}")
        for field in ("category", "question", "answer", "review_notes"):
            if not isinstance(record[field], str) or not record[field].strip():
                raise ValueError(f"Missing {field} for {rid}")
        urls = record["source_urls"]
        if not isinstance(urls, list) or any(not isinstance(u, str) or not u.startswith("https://") for u in urls):
            raise ValueError(f"Invalid source_urls for {rid}")
    return data


def approved_faq(path=FAQ_PATH):
    return [r for r in load_all(path) if r["status"] == "approved"]


def reviewed_faq(path=FAQ_PATH):
    return [r for r in load_all(path) if r["status"] in {"reviewed", "approved"}]


def build_faq_context(records):
    if not records:
        return "No matching CYF FAQ evidence is available."
    return "\n\n".join(
        f'ID: {r["id"]}\nTier: {r["tier"]}\nQuestion: {r["question"]}\n'
        f'Answer: {r["answer"]}\nSources: {", ".join(r["source_urls"]) or "Not provided"}'
        for r in records
    )


STOPWORDS = set("a an the i is are was were do does did to for of in on at and or my me your you we our can could would should what how where when why with this that it from have has about more tell please cyf codeyourfuture course courses years really already know some".split())
ALIASES = {
    "itd": "intro digital", "itp": "intro programming", "sdc": "software development",
    "coding": "programming", "code": "programming", "programmer": "programming",
    "skipping": "skip", "skipped": "skip", "bypass": "skip", "avoid": "skip",
    "enrollment": "enrol", "enrolled": "enrol", "enroll": "enrol",
    "signup": "register", "registration": "register",
    "classes": "class", "trainees": "trainee", "laptops": "laptop",
    "jobs": "job", "employment": "job", "guaranteed": "guarantee", "promise": "guarantee",
    "duration": "long", "weeks": "week", "results": "result",
}


def tokens(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    expanded = []
    for word in words:
        expanded.extend(ALIASES.get(word, word).split())
    return {w for w in expanded if w not in STOPWORDS and len(w) > 1}


def _intent_target(question, records):
    """Route a few high-impact, unambiguous intents to their exact reviewed FAQ."""
    q = question.lower()
    targets = []
    if re.search(r"\b(skip|skipping|bypass|need to do|need|have to do|mandatory)\b", q) and re.search(r"\b(itd|intro to digital|course|programming|coding)\b", q):
        targets.append("CYF-T2-001")
    if re.search(r"\b(guarantee|guaranteed|promise|promised)\b", q) and re.search(r"\b(job|employment|work|google|hired)\b", q):
        targets.append("CYF-T1-020")
    if re.search(r"\b(how long|duration|how many weeks|how much time)\b", q) and re.search(r"\b(itp|intro to programming)\b", q):
        targets.append("CYF-T2-003")
    if re.search(r"\b(duolingo|english test)\b", q) and re.search(r"\b(portal|missing|not showing|not appearing|recognis|recogniz)\w*", q):
        targets.append("CYF-T5-003")
    if re.search(r"\b(portal)\b", q) and re.search(r"\b(email|login|log in|recognis|recogniz)\w*", q):
        targets.append("CYF-T5-004")
    if re.search(r"\b(address|location|where exactly)\b", q) and re.search(r"\b(venue|saturday|class)\b", q):
        targets.append("CYF-T4-005")
    indexed = {r["id"]: r for r in records}
    return [indexed[rid] for rid in targets if rid in indexed]


def retrieve(question, faq_records, limit=4):
    """Return ranked evidence; conservative on weak matches, no external dependencies."""
    if not question.strip():
        return []
    routed = _intent_target(question, faq_records)
    if routed:
        return routed[:limit]
    q = tokens(question)
    if not q:
        return []
    ranked = []
    for record in faq_records:
        title = tokens(record["question"])
        overlap = len(q & title)
        precision = overlap / len(q)
        coverage = overlap / max(1, len(title))
        similarity = SequenceMatcher(None, question.lower(), record["question"].lower()).ratio()
        score = 0.65 * precision + 0.25 * coverage + 0.10 * similarity
        if overlap and (precision >= 0.4 or overlap >= 2):
            ranked.append((score, record))
    ranked.sort(key=lambda item: item[0], reverse=True)
    if not ranked or ranked[0][0] < 0.36:
        return []
    best = ranked[0][0]
    return [r for score, r in ranked if score >= max(0.36, best - 0.15)][:limit]
