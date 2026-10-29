# CYF AI Concierge — Tier 1 Content Review

**Prepared:** 26 October 2026  
**Scope:** 23 Tier 1 questions in `data/faq_tier1.json`, cross-checked against the CYF Trainee FAQ supplied in chat and the product manager's 24 October 2026 summary.  
**Status:** Draft for CYF product/content owners and subject matter experts (SMEs). **Nothing in this document represents CYF approval.**

## Purpose and approval rules

This register identifies information that needs verification before the AI Concierge treats it as authoritative. The supplied FAQ is the source of the draft answers, not independent verification of current policy. The chatbot should not determine a person's eligibility, offer immigration/benefits advice, guarantee financial support or employment, or collect ID, immigration or financial documents.

**Workflow:** PM assigns an owner → owner confirms policy and exact wording/URL → engineer updates the JSON answer and `review_notes` → reviewer records approval and date → set `status` to `approved`. Until then, keep `status: needs_review`. Re-review time-sensitive information on an agreed cadence. For urgent safety or safeguarding disclosures, use an approved human escalation route rather than relying on FAQ text alone.

**Risk key:** High = could materially mislead someone about eligibility, legal status, financial support or accessibility; Medium = potentially changeable or incomplete information; Low = straightforward content still needing sign-off.

## Review summary

| Risk | Number | Tier 1 IDs |
|---|---:|---|
| High | 10 | 001–006, 013, 019, 022, 023 |
| Medium | 10 | 008–012, 014–016, 018, 021 |
| Low | 3 | 007, 017, 020 |
| **Total** | **23** | **All Tier 1 records** |

## Detailed Tier 1 review register

| ID | Priority | Issue to verify / decision needed | Suggested owner | Status |
|---|---|---|---|---|
| CYF-T1-001 | High | Distinguish **suitability** (mission/population) from formal **eligibility** for ITP onward; confirm whether the 90-minute travel rule applies to online ITD. | Admissions / programme | Pending |
| CYF-T1-002 | High | Approve wording that right to work is not required for course entry; clearly separate training admission from future employment rights. No individual immigration advice. | Admissions / legal-policy | Pending |
| CYF-T1-003 | High | FAQ says people without visa/ID can study, but certified Duolingo test requires identity checks. Confirm how applicants without ID proceed and a human contact route. | Admissions / safeguarding | Pending |
| CYF-T1-004 | High | FAQ's benefits answer contains the incomplete phrase “If people find while on our courses…”. Verify benefits, working while studying and any expense/benefit interaction; do not give personal benefits advice. | Programme / pastoral | Pending |
| CYF-T1-005 | High | Confirm definition of low income (60% of regional median after tax/housing, household-size adjustment), calculation guidance and whether it varies by region; chatbot must not assess eligibility itself. | Admissions / eligibility | Pending |
| CYF-T1-006 | High | FAQ says **B2 for ITP** in one answer and **B2 for SDC** in another. Confirm stage-specific requirement, accepted tests and public wording. | Admissions / English assessment | Pending |
| CYF-T1-007 | Low | Confirm that all listed CYF courses remain free and whether any ancillary costs require explanation. | Programme / PM | Pending |
| CYF-T1-008 | Medium | Confirm six current regions, active delivery and the applicability of the 90-minute rule to different courses. | Regional operations / admissions | Pending |
| CYF-T1-009 | Medium | Confirm ITD online/optional workshops and Saturday in-person expectations from ITP onward, including regional exceptions and remote provision. | Programme delivery | Pending |
| CYF-T1-010 | Medium | Validate current Wednesday/Saturday schedules, time zones, holidays and regional exceptions; avoid hard-coded schedules without review date. | Programme delivery | Pending |
| CYF-T1-011 | Medium | FAQ says 20 hours independent + 8 hours class per week, while listed Saturday times are 10:00–17:00. Clarify the discrepancy and which courses the 28-hour commitment applies to. | Programme delivery | Pending |
| CYF-T1-012 | Medium | Confirm laptop availability, timing of eligibility to request, and canonical Signpost URL: `cyf-signposts.netlify.app` vs `signposts.codeyourfuture.io`. | IT / pastoral | Pending |
| CYF-T1-013 | High | Verify reimbursement eligibility by course/stage, expense limits, advance-payment requirement, childcare/internet rules and benefits-related statement; confirm pastoral escalation. Avoid promising funding. | Finance / pastoral | Pending |
| CYF-T1-014 | Medium | “96% have little or no coding experience” is undated. Obtain source and reporting period or remove statistic from chatbot response. | Impact / communications | Pending |
| CYF-T1-015 | Medium | Confirm distinction between Basic Online Skills and the ITD → ITP → Checkpoint → SDC pathway; verify current names, order and progression requirements. | Curriculum / admissions | Pending |
| CYF-T1-016 | Medium | Confirm ITD 20–40 study hours within a 28-day window, optional workshops, and whether `course1.codeyourfuture.io/sign-up` is the current sign-up URL. | ITD programme / admissions | Pending |
| CYF-T1-017 | Low | Confirm beginner-friendly wording without implying that no coding experience automatically qualifies someone for ITP or later courses. | Programme / PM | Pending |
| CYF-T1-018 | Medium | **No standalone sign-up FAQ answer was supplied.** Draft answer synthesises ITD sign-up and progression information; obtain approved step-by-step journey and canonical URL. | Admissions / PM | Pending |
| CYF-T1-019 | High | **No substantive accreditation answer was supplied.** Confirm whether courses are formally accredited, by whom, and how badges/certificates differ; do not infer accreditation from badges. | Programme leadership / compliance | Pending |
| CYF-T1-020 | Low | Confirm approved “no job guarantee” wording; do not imply guaranteed placement or hiring by partners. | Employability / communications | Pending |
| CYF-T1-021 | Medium | Verify current employment partner names and outcome claims; FAQ cites approximately 70% employment and 5-month / 9–10-month timelines without dated evidence. | Employability / impact | Pending |
| CYF-T1-022 | High | Confirm reasonable-adjustment form is appropriate for **prospective** applicants (FAQ calls it a trainee form); resolve conflicting ITP/SDC duration allowances (13 vs 16 weeks), and agree human support route. | Accessibility / pastoral | Pending |
| CYF-T1-023 | High | Verify accessibility form and process for prospective applicants, plus how venue accessibility is confirmed without publishing private venue addresses. | Accessibility / regional operations | Pending |

## Cross-cutting content and safety decisions

### A. Policies requiring explicit SME sign-off

1. **Eligibility, low income and geography:** Keep ITD access distinct from formal eligibility for ITP onward. Do not let the chatbot tell users they are definitely eligible or ineligible.
2. **Immigration and ID:** FAQ says legal status does not prevent taking courses, but certified testing has ID requirements. Route individual circumstances to an approved CYF human contact; never request documents in chat.
3. **English:** Resolve B2 threshold and stage before making definitive statements.
4. **Benefits and expenses:** Repair the truncated sentence; check claims that reimbursements do not count as income for benefits. Avoid personal financial/benefits advice.
5. **Accessibility:** Confirm that published forms and reasonable-adjustment options apply to people who have not yet enrolled.

### B. Links to verify

| Purpose | URL in supplied FAQ | Check |
|---|---|---|
| ITD registration | https://course1.codeyourfuture.io/sign-up | Current entry point and whether sign-up is always open |
| General student information | https://codeyourfuture.io/become-a-student/ | Correct route for prospective students |
| Regions | https://codeyourfuture.io/regions/ | Current locations and distance policy |
| ITD curriculum | https://itd.codeyourfuture.io/ | Current course material |
| Course catalogue | https://curriculum.codeyourfuture.io/ | Current programme pages |
| Laptop/trainee support | https://cyf-signposts.netlify.app/ | Compare with alternative below |
| Laptop/trainee support | https://signposts.codeyourfuture.io/ | Choose canonical link |
| Accessibility request | https://docs.google.com/forms/d/e/1FAIpQLSfKTuY10bVm5R8Hu3w5xYQJfISMHA231g6n0nCERctrpm7Dng/viewform | Accessible to applicants or trainees only? |
| Expenses policy | https://docs.google.com/document/d/1UuPLflvuSED3XczbzGzgj2utwzXbWP-fxKMkqLaqHo4/edit | Current version and limits |
| Course calendar | https://curriculum.codeyourfuture.io/calendar | Live and current? Do not use undated pasted calendar |
| Safeguarding | https://codeyourfuture.io/about/safeguarding/ | Approved escalation wording |
| Code of Conduct | https://codeyourfuture.io/about/code-of-conduct/ | Approved complaints/reporting route |

URLs are transcribed from supplied material, **not independently tested or verified**.

### C. Content to exclude or constrain in the prospective-student chatbot

- **Undated figures:** 96% beginner statistic, ~70% employment, estimated job timelines until sourced and approved.
- **Dynamic facts:** Intake dates, cohort status, deadlines, class locations and staff contacts without a current authoritative source.
- **Internal logistics:** Lunch budgets, private venue addresses, internal Slack instructions and laptop-return procedures unless explicitly within approved scope.
- **Sensitive processes:** Do not collect passports, ARC/ID copies, bank details, benefit evidence or immigration documents. Direct users to CYF's approved secure process.
- **Human escalation:** Personal eligibility decisions, visa/legal questions, benefits disputes, application account issues, safeguarding and complaints need a verified human route.

## Proposed answer-handling rules for the MVP

- Answer using **approved** FAQ records only; if not approved or absent, say what is unknown and link to a verified official page or human support route.
- Give a direct answer first and provide a relevant official link immediately when useful.
- Separate **what the FAQ says** from any current status the chatbot cannot verify.
- Never claim that finishing ITD guarantees admission to ITP, that a course guarantees employment, or that a person meets formal eligibility criteria.
- Do not invent course dates, funding decisions, English thresholds, accreditations, venue addresses or contact details.
- For safeguarding or immediate safety concerns, direct to the approved safeguarding channel; do not attempt to investigate in chat.

## Product manager decisions requested

1. Confirm that the initial public chatbot scope is **Tier 1**, with Tier 2 added after sign-off, and Tier 5 kept out of scope.
2. Name a content owner and an approver for each policy area, and identify a canonical FAQ source.
3. Confirm approved escalation/contact paths for admissions, pastoral, accessibility, immigration-related queries and safeguarding.
4. Resolve the high-risk items first, especially **001–006, 013, 019, 022 and 023**.
5. Decide the review frequency for course dates, links, schedules, expenses and outcomes.
6. Approve a standard wording for unanswered questions and sensitive-data handling.

## Approval log

| Date | FAQ ID / topic | Decision and approved wording or URL | Approver | JSON updated? |
|---|---|---|---|---|
| _Pending_ | _Pending_ | _Pending_ | _Pending_ | No |

## Engineering acceptance criteria

- [ ] Every one of the 23 Tier 1 JSON entries has an identified review owner.
- [ ] Every high-risk issue has a documented CYF decision or is withheld from authoritative answers.
- [ ] All public-facing URLs are checked and a canonical link is selected where duplicates exist.
- [ ] All approved answers have an approver and review date recorded.
- [ ] JSON `status` changes to `approved` **only after** approval.
- [ ] Tests cover beginner questions, eligibility uncertainty, English, benefits, laptops, privacy, accessibility, deadlines, human escalation and multi-turn conversations.
- [ ] Regression tests confirm that the chatbot does not use excluded or unapproved content as settled policy.
