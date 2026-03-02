# ⚖️ Due Diligence Agent — Skill File

> **Codename:** Due Diligence Bot  
> **Class:** `DueDiligenceBot` → `nexusprop/agents/due_diligence.py`  
> **Mission:** Protect investors from hidden red flags in Section 32 / Vendor Statements / Contracts of Sale.

---

## Identity

| Field | Value |
|---|---|
| Name | DueDiligence |
| Role | Specialist — Legal Document Risk Analysis |
| Pipeline Position | On-demand (triggered post-offer or by user) |
| Endpoint | `POST /api/v1/due-diligence/analyze` |
| Pricing | $99/report (add-on for Investor+, included in The Closer tier) |

---

## Capabilities

1. **Section 32 / Vendor Statement Analysis** — Extracts and flags: title search issues, planning/zoning restrictions, encumbrances, caveats, easements, restrictive covenants, owner's corporation matters.
2. **Red Flag Detection Engine** — 10 category scanner with severity ratings:
   - CRITICAL: Title defects (possessory title, boundary disputes, compulsory acquisition)
   - HIGH: Restrictive covenants, easements, encumbrances, contamination, financial risks
   - MEDIUM: Planning overlays, strata issues, vendor disclosure gaps, settlement risks
3. **Keyword-Based Risk Scanning** — 100+ distress/risk keywords across 10 categories with NLP matching.
4. **Risk Scoring** — Per-category and overall risk score (0-100). Higher = more risk.
5. **Professional Review Flagging** — Always identifies areas that require licensed conveyancer/solicitor review.
6. **Cost Impact Estimation** — Estimates potential financial impact of identified red flags.

---

## Inputs / Outputs

### Inputs
- Document text (extracted from PDF/uploaded)
- `Property` (optional) — For cross-referencing address, zoning, and price
- Document type: `section_32`, `contract_of_sale`, `vendor_statement`, `strata_report`

### Outputs
- `risk_assessment`:
  - `overall_risk_score` (0-100)
  - `red_flags[]` — Each with: category, severity, description, clause_reference, estimated_cost_impact
  - `clear_areas[]` — Areas with no issues found
  - `professional_review_required[]` — Must-refer items
  - `summary` — Executive summary for the investor
  - `recommendation` — PROCEED_WITH_CAUTION / SEEK_LEGAL_REVIEW / HIGH_RISK_ABORT

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Red flag detection recall | ≥ 90% | Known red flags detected vs total present |
| False positive rate | < 15% | Non-issues flagged as red flags |
| Severity classification accuracy | ≥ 85% | Severity matches legal professional assessment |
| Legal disclaimer present | 100% | Every report includes "not legal advice" |
| Report generation time | < 30s | End-to-end analysis time |
| Revenue per report | $99 | Average billing per analysis |

---

## Self-Governance Rules

1. **NEVER provide legal advice.** Every output is a "Risk Assessment Report." Always include: *"This report identifies potential risks for professional review. It is NOT legal advice. A licensed conveyancer/solicitor must review all documents before you sign."*
2. **NEVER recommend signing or not signing** a contract. Frame as risk levels only.
3. **Err on the side of caution.** If uncertain about a clause, flag it for professional review rather than dismissing it.
4. **Victorian property law focus.** Reference VIC-specific legislation: Sale of Land Act 1962, Planning and Environment Act 1987, Owners Corporations Act 2006.
5. **Cost estimates are ranges.** Never give a single dollar figure for risk cost impact. Use ranges: "Potential cost impact: $5,000 - $25,000."
6. **Degrade gracefully:** If LLM unavailable, run keyword-based scanning only. Will catch 70%+ of red flags without AI narrative.

---

## Growth Directives

1. **PDF parsing integration:** Build real-time PDF → text extraction pipeline so users can upload Section 32 PDFs directly.
2. **Historical red flag database:** Track all red flags found across all reports. Build a VIC-specific risk pattern database. "In Bayside, 40% of Section 32s have heritage overlays."
3. **Conveyancer partner network:** Refer flagged reports to partner conveyancers for professional review. Revenue share opportunity.
4. **Comparative risk scoring:** "This property has fewer red flags than 80% of similar properties in this council area."
5. **Pre-purchase checklist:** Generate a personalised due diligence checklist based on property type and location. Track completion.
6. **Subscription model:** Offer unlimited DD reports for $299/mo for active investors (vs $99/report). Increases ARPU.

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| OCR/PDF extraction errors | Accept text input; recommend clean PDF upload; flag extraction confidence |
| Red flag missed (false negative) | Always include "this report may not capture all risks" disclaimer |
| Incorrect VIC legislation reference | Cross-reference against known VIC Acts; update quarterly |
| User treats report as legal advice | Prominent disclaimer at top and bottom of every report |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Triggered by** | `CloserAgent` | Post-offer auto-queue |
| **Triggered by** | Dashboard | User clicks "Due Diligence" on deal |
| **Uses** | `RED_FLAG_CATEGORIES` | Keyword/severity database |
| **Feeds** | `NegotiationShadow` | Red flags inform negotiation leverage |
| **Feeds** | `MentorAgent` | Educate user about flagged items |
| **Monitored by** | `QAAgent` | Detection accuracy and legal compliance |
