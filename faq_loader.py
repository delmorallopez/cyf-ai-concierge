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

import re

def application_intent(query: str) -> str | None:
    normalized = re.sub(r"[^\w\s]", " ", query.lower())
    normalized = " ".join(normalized.split())

    if normalized in {
        "how do i apply to codeyourfuture",
        "how can i apply to codeyourfuture",
        "how do i apply to cyf",
    }:
        return "CYF-T2-026"

    if normalized in {
        "how do i check my application progress",
        "how can i check my application status",
        "where can i see my application status",
    }:
        return "CYF-T2-027"
    
    if normalized in {
        "how many hours per week do i need to study",
        "how much time do i need to study each week",
        "what is the weekly study commitment",
        "how many hours a week is the course",
    }:
        return "CYF-T2-028"
    
    if normalized in {
        "where can i find trainee support",
        "where can i get help as a trainee",
        "how can i get trainee support",
    }:
        return "CYF-T3-005"

    if normalized in {
        "what career support is available",
        "what job support does cyf provide",
        "how does cyf help me find a job",
    }:
        return "CYF-T1-021"

    if normalized in {
        "what happens after completing the programme",
        "what happens after i finish the programme",
        "what support is available after graduation",
    }:
        return "CYF-T3-013"
    
    if normalized in {
        "can codeyourfuture provide a laptop",
        "can cyf provide a laptop",
        "can i get a laptop from codeyourfuture",
        "does codeyourfuture provide laptops",
        "how can i request a laptop",
        "how do i request a laptop for itp",
    }:
        return "CYF-T3-010"
    
    if normalized in {
        "what is a trainee",
        "what does trainee mean",
        "what is an enrolled trainee",
        "what does it mean to be a trainee",
        "who is considered a trainee",
    }:
        return "CYF-T3-009"
    
    location_phrases = (
        "i live in ",
        "i am living in ",
        "i'm living in ",
        "i'm based in ",
        "can i apply from ",
        "can i join from ",
    )

    if any(phrase in normalized for phrase in location_phrases):
        return "CYF-T1-001"

    return None

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


def eligibility_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    eligibility_terms = (
        "unemployed",
        "unemployment",
        "university degree",
        "degree",
        "age limit",
        "how old",
        "refugee",
        "asylum seeker",
        "asylum seekers",
    )

    if any(term in normalized for term in eligibility_terms):
        return ["CYF-T1-001", "CYF-T1-003"]

    location_terms = (
        "i live in",
        "i am living in",
        "i m living in",
        "i m based in",
        "can i apply from",
        "can i join from",
    )

    if any(term in normalized for term in location_terms):
        return ["CYF-T1-008", "CYF-T1-001"]
    
    # Income verification and supporting documents
    income_proof_terms = (
        "proof of income",
        "prove my income",
        "provide proof",
        "income documents",
        "income verification",
        "payslip",
        "payslips",
        "bank statement",
    )

    if any(term in normalized for term in income_proof_terms):
        return ["CYF-T2-018", "CYF-T1-005"]
    

    # Financial circumstances and income eligibility
    if any(term in normalized for term in (
        "universal credit",
        "benefits",
        "household income",
        "low income",
        "working part time",
        "part time job",
        "partner earns",
        "wife earns",
        "husband earns",
    )):
        return ["CYF-T1-001", "CYF-T1-005"]

    # Income verification questions
    if (
        any(term in normalized for term in (
            "proof of income",
            "prove my income",
            "income documents",
            "payslip",
            "bank statement",
        ))
    ):
        return ["CYF-T2-018", "CYF-T1-005"]

    # Course fees
    if any(term in normalized for term in (
        "pay anything",
        "course fees",
        "course fee",
        "is cyf free",
        "are the courses free",
        "cost of the course",
    )):
        return ["CYF-T1-014"]

    return []


def location_attendance_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    # Applicants outside the UK
    if any(term in normalized for term in (
        "outside the uk",
        "outside of the uk",
        "outside the united kingdom",
        "outside britain",
    )):
        return [
            "CYF-T1-008",
            "CYF-T1-001",
            "CYF-T1-009",
        ]

    # Online courses
    if any(term in normalized for term in (
        "online only",
        "fully online",
        "online courses",
        "online course",
        "remote learning",
        "study remotely",
    )):
        return [
            "CYF-T1-009",
            "CYF-T1-016",
        ]

    # Missing Saturday classes
    if any(term in normalized for term in (
        "miss a saturday",
        "miss saturday",
        "miss a class",
        "miss classes",
        "absent from class",
        "cannot attend saturday",
    )):
        return [
            "CYF-T1-009",
            "CYF-T1-010",
        ]

    # Attending another CYF region
    if any(term in normalized for term in (
        "different cyf region",
        "another cyf region",
        "different region",
        "another region",
        "change region",
        "switch region",
    )):
        return [
            "CYF-T1-008",
            "CYF-T1-010",
        ]

    # Travelling more than 90 minutes
    if any(term in normalized for term in (
        "two hours from",
        "2 hours from",
        "more than 90 minutes",
        "over 90 minutes",
        "two hours away",
        "2 hours away",
    )):
        return [
            "CYF-T1-001",
            "CYF-T1-008",
        ]

    return []


def application_enquiry_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    if any(term in normalized for term in (
        "how long does the application",
        "application process take",
        "how long to apply",
        "application timeline",
    )):
        return ["CYF-T2-018", "CYF-T2-026"]

    if any(term in normalized for term in (
        "after i submit",
        "after submitting my application",
        "after applying",
        "submitted my application",
    )):
        return ["CYF-T2-026", "CYF-T2-018"]

    if any(term in normalized for term in (
        "apply more than once",
        "apply again",
        "reapply",
        "re application",
    )):
        return ["CYF-T2-026"]

    if any(term in normalized for term in (
        "application is rejected",
        "application was rejected",
        "application rejected",
        "not accepted",
    )):
        return ["CYF-T2-018", "CYF-T2-026"]

    if any(term in normalized for term in (
        "change my application",
        "edit my application",
        "update my application",
        "change application details",
    )):
        return ["CYF-T2-026", "CYF-T2-027"]

    if any(term in normalized for term in (
        "confirmation email",
        "confirmation e mail",
        "no confirmation",
        "haven t received an email",
    )):
        return ["CYF-T2-026", "CYF-T2-027"]

    return []


def learning_pathway_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    # Previous programming knowledge
    if any(term in normalized for term in (
        "know python",
        "know javascript",
        "programming experience",
        "coding experience",
        "know how to code",
        "before joining",
    )):
        return ["CYF-T1-014"]

    # Programming languages taught
    if any(term in normalized for term in (
        "programming languages",
        "languages will i learn",
        "learn python",
        "learn javascript",
        "languages are taught",
    )):
        return ["CYF-T2-005"]

    # Full programme duration
    if any(term in normalized for term in (
        "full cyf programme take",
        "full programme take",
        "entire programme",
        "whole programme",
        "programme duration",
    )):
        return [
            "CYF-T1-018",
            "CYF-T2-005",
        ]

    # Self-paced learning
    if any(term in normalized for term in (
        "my own pace",
        "self paced",
        "study at my pace",
        "flexible learning",
    )):
        return ["CYF-T1-009"]

    # Struggling with coursework
    if any(term in normalized for term in (
        "struggle with",
        "struggling with",
        "fall behind",
        "coursework difficult",
        "need help studying",
    )):
        return [
            "CYF-T3-005",
            "CYF-T5-001",
        ]

    return []



def laptop_support_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    # Laptop specifications
    if any(term in normalized for term in (
        "laptop specifications",
        "laptop specs",
        "minimum laptop",
        "computer requirements",
        "what laptop do i need",
        "laptop requirements",
    )):
        return ["CYF-T2-016"]

    # Tablets and alternative devices
    if any(term in normalized for term in (
        "use a tablet",
        "tablet instead",
        "use an ipad",
        "ipad instead",
        "tablet for the course",
    )):
        return ["CYF-T1-012", "CYF-T3-010"]

    # Laptop problems: no specific repair policy documented
    if any(term in normalized for term in (
        "laptop stops working",
        "laptop stopped working",
        "laptop is broken",
        "laptop broke",
        "laptop not working",
        "laptop damaged",
    )):
        return []

        # Returning a laptop - check first
    if any(term in normalized for term in (
        "return the laptop",
        "return my laptop",
        "send the laptop back",
        "laptop return",
    )):
        return ["CYF-T5-008", "CYF-T3-010"]

    # Keeping a laptop after graduation
    if any(term in normalized for term in (
        "keep the laptop",
        "keep my laptop",
        "laptop after graduation",
        "laptop after the course",
    )):
        return ["CYF-T3-010", "CYF-T5-008"]

    return []


def career_support_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    # CV and professional profile
    if any(term in normalized for term in (
        "prepare my cv",
        "help with my cv",
        "review my cv",
        "cv preparation",
        "cover letter",
        "linkedin profile",
        "portfolio review",
    )):
        return ["CYF-T1-021", "CYF-T3-011"]

    # Interview preparation
    if any(term in normalized for term in (
        "interview preparation",
        "prepare for interviews",
        "prepare for an interview",
        "mock interviews",
        "interview practice",
        "interview support",
    )):
        return ["CYF-T1-021", "CYF-T3-011"]

    # Graduate employment
    if any(term in normalized for term in (
        "companies hire",
        "hire cyf graduates",
        "cyf graduates get jobs",
        "graduates find jobs",
        "employment after cyf",
    )):
        return ["CYF-T3-012", "CYF-T1-021"]

    return []


def trainee_support_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    # Slack community and communication
    if "slack" in normalized and any(
        term in normalized
        for term in ("community", "trainee", "join", "group")
    ):
        return ["CYF-T5-001"]

    # Coursework and assignment support
    if any(term in normalized for term in (
        "help with assignments",
        "help with my assignments",
        "assignment help",
        "help with coursework",
        "ask volunteers for help",
    )):
        return ["CYF-T5-001"]

    # Falling behind with learning
    if any(term in normalized for term in (
        "falling behind",
        "fallen behind",
        "struggling to keep up",
        "behind with coursework",
        "behind on assignments",
    )):
        return ["CYF-T5-001"]

    # Temporary break or deferral
    if any(term in normalized for term in (
        "take a break",
        "pause the programme",
        "pause the course",
        "defer my course",
        "defer the course",
        "temporary break",
    )):
        return ["CYF-T5-013"]

    # Leaving or withdrawing
    if any(term in normalized for term in (
        "decide to leave",
        "leave the course",
        "withdraw from the course",
        "withdraw from cyf",
        "quit the course",
        "stop studying",
    )):
        return ["CYF-T5-013"]

    return []


def complex_eligibility_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    # Adult applicant with no IT experience
    if (
        any(term in normalized for term in (
            "never worked in it",
            "no it experience",
            "no tech experience",
            "no coding experience",
            "never worked in tech",
        ))
        and any(term in normalized for term in (
            "can i join",
            "can i apply",
            "am i eligible",
        ))
    ):
        return ["CYF-T1-001", "CYF-T1-014"]

    # Full-time work and family commitments
    if (
        any(term in normalized for term in (
            "full time job",
            "working full time",
            "work full time",
            "employed full time",
        ))
        and any(term in normalized for term in (
            "children",
            "kids",
            "family",
            "suitable for me",
            "can i join",
        ))
    ):
        return ["CYF-T1-001", "CYF-T2-028", "CYF-T1-011"]

    
    # English proficiency
    if any(term in normalized for term in (
        "don t speak english very well",
        "dont speak english very well",
        "do not speak english very well",
        "my english is not good",
        "poor english",
        "limited english",
        "english fluency",
        "not fluent in english",
    )):
        return ["CYF-T2-018"]


    return []


def eligibility_rejection_intent(question):
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    rejection_terms = (
        "rejected", "rejection", "failed eligibility",
        "not eligible", "ineligible", "didn t qualify",
        "did not qualify"
    )

    if any(term in normalized for term in rejection_terms):
        if any(term in normalized for term in (
            "eligibility", "income", "duolingo",
            "english test", "assessment"
        )):
            return [
                "CYF-T1-005",
                "CYF-T2-018",
                "CYF-T2-026",
            ]

    return []



def retrieve(question, faq_records, limit=4):
    """Return ranked FAQ evidence with explicit intent routing."""

    if not question.strip():
        return []

    normalized = " ".join(
    re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    if any(term in normalized for term in (
        "means testing",
        "means tested",
        "income eligibility",
        "income criteria",
        "income threshold",
        "financial eligibility",
        "do i meet the income",
    )):
        matches = [
            record for record in faq_records
            if record["id"] == "CYF-T1-005"
        ]
        if matches:
            return matches[:limit]
        
    # Normalize the user's question
    normalized = " ".join(
        re.sub(r"[^\w\s]", " ", question.lower()).split()
    )

    normalized = " ".join(
    re.sub(r"[^\w\s£]", " ", question.lower()).split()
    )

    income_terms = (
        "income", "salary", "earns", "earning",
        "makes", "paid", "wage"
    )

    household_terms = (
        "wife", "husband", "partner", "spouse",
        "household", "family"
    )

    if (
        any(term in normalized.split() for term in income_terms)
        and any(term in normalized.split() for term in household_terms)
    ):
        for record in faq_records:
            if record["id"] == "CYF-T1-001":
                return [record]

   
    rejection_ids = eligibility_rejection_intent(question)

    if rejection_ids:
        matches = [
            record
            for faq_id in rejection_ids
            for record in faq_records
            if record["id"] == faq_id
        ]
        if matches:
            return matches[:limit]
        
    career_ids = career_support_intent(question)

    if career_ids:
        matches = [
            record
            for faq_id in career_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        if matches:
            return matches[:limit]
        
    complex_ids = complex_eligibility_intent(question)

    if complex_ids:
        matches = [
            record
            for faq_id in complex_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        if matches:
            return matches[:limit]
        
    laptop_ids = laptop_support_intent(question)

    if laptop_ids:
        matches = [
            record
            for faq_id in laptop_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        if matches:
            return matches[:limit]
        
    trainee_ids = trainee_support_intent(question)

    if trainee_ids:
        matches = [
            record
            for faq_id in trainee_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        if matches:
            return matches[:limit]
        
    learning_ids = learning_pathway_intent(question)

    if learning_ids:
        matches = [
            record
            for faq_id in learning_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        if matches:
            return matches[:limit]

    attendance_ids = location_attendance_intent(question)

    if attendance_ids:
        matches = [
            record
            for faq_id in attendance_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        if matches:
            return matches[:limit]
        
    enquiry_ids = application_enquiry_intent(question)

    if enquiry_ids:
        matches = [
            record
            for faq_id in enquiry_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        if matches:
            return matches[:limit]
        
    eligibility_ids = eligibility_intent(question)

    if eligibility_ids:
        matches = [
            record
            for faq_id in eligibility_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        if matches:
            return matches[:limit]
        
    # Retrieve multiple FAQs for general trainee support
    if normalized in {
        "where can i find trainee support",
        "how can i get support as a trainee",
        "where can trainees get help",
    }:
        support_ids = [
            "CYF-T3-005",
            "CYF-T5-001",
            "CYF-T3-006",
        ]

        matches = [
            record
            for faq_id in support_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        return matches[:limit]


        # Questions about working while attending CYF classes
    if (
        any(term in normalized for term in (
            "working",
            "work full time",
            "work part time",
            "have a job",
            "employed",
        ))
        and any(term in normalized for term in (
            "class",
            "course",
            "study",
            "attend",
        ))
    ) or normalized in {
        "when are the classes",
        "what days are the classes",
        "are classes on saturdays",
        "what time do classes start",
    }:
        schedule_ids = [
            "CYF-T1-010",
            "CYF-T1-011",
            "CYF-T1-009",
        ]

        matches = [
            record
            for faq_id in schedule_ids
            for record in faq_records
            if record["id"] == faq_id
        ]

        return matches[:limit]
    

    # Existing explicit intent routing
    target_id = application_intent(question)

    if target_id:
        for record in faq_records:
            if record["id"] == target_id:
                return [record]

    # Keep the rest of your existing retrieval logic below.
    # 2. Handle existing intent routing
    routed = _intent_target(question, faq_records)

    if routed:
        return routed[:limit]

    # 3. Tokenise the question
    q = tokens(question)

    if not q:
        return []

    # 4. Rank FAQ records by similarity
    ranked = []

    for record in faq_records:
        title = tokens(record["question"])

        overlap = len(q & title)
        precision = overlap / len(q)
        coverage = overlap / max(1, len(title))

        similarity = SequenceMatcher(
            None,
            question.lower(),
            record["question"].lower()
        ).ratio()

        score = (
            0.65 * precision
            + 0.25 * coverage
            + 0.10 * similarity
        )

        if overlap and (precision >= 0.4 or overlap >= 2):
            ranked.append((score, record))

    # 5. Sort by highest score
    ranked.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # 6. Reject weak matches
    if not ranked or ranked[0][0] < 0.36:
        return []

    # 7. Return the best matching FAQs
    best = ranked[0][0]

    return [
        record
        for score, record in ranked
        if score >= max(0.36, best - 0.15)
    ][:limit]

