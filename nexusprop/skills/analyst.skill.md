# 📊 Analyst Agent — Skill File

> **Codename:** Agent B — The Analyst  
> **Class:** `AnalystAgent` → `nexusprop/agents/analyst.py`  
> **Mission:** Produce institutional-grade financial analysis that a fund manager would trust.

---

## Identity

| Field | Value |
|---|---|
| Name | Analyst |
| Role | Cognitive Layer — Financial Analysis & Deal Scoring |
| Pipeline Position | 3rd (after Scout) |
| Endpoint | `POST /api/v1/deals/analyze` |
| Pricing | Core (included in all tiers) |

---

## Capabilities

1. **Cash Flow Modelling** — Full `CashFlowModel` computation: gross yield, net yield, ROI, cash-on-cash return, monthly cash flow, annual net income (interest-only mortgage, management fees, council rates, insurance, vacancy, maintenance).
2. **Bargain Score Engine** — Weighted multi-factor scoring (0-100): price vs median (30%), yield (20%), growth (15%), DOM discount (15%), infrastructure (10%), distress (10%). Golden Opportunity threshold: ≥ 80.
3. **Comparable Sales Analysis** — Via `CompsEngine`: $/sqm comparison, estimated market value, underquoting detection, confidence level.
4. **AI-Powered Deal Assessment** — LLM generates: street-level price positioning, L/A ratio analysis, infrastructure pipeline impact, capital growth trajectory, risk matrix, entry price recommendation, DEAL/FAIR/TRAP verdict.
5. **Strategy-Specific Analysis** — Model deals as BTL (buy-to-let), BRRR, flip, development, or HMO.
6. **Batch Processing** — Analyse multiple properties in a single pipeline run, sorted by Bargain Score.

---

## Inputs / Outputs

### Inputs
- `List[Property]` — From Scout or user upload
- `SuburbProfile` dict — From `locations.py` (median prices, growth, vacancy, infra)
- `List[Property]` — Sold data for comps analysis
- `DealType` — Investment strategy (BTL default)
- `run_ai_analysis: bool` — Whether to invoke LLM narrative

### Outputs
- `List[Deal]` — Sorted by Bargain Score, each containing:
  - `CashFlowModel` (all financial metrics)
  - `BargainScore` (weighted component breakdown)
  - `CompAnalysis` (market value estimate, underquoting flag)
  - `ai_analysis` (narrative text)
  - `is_golden_opportunity` flag

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Financial calculation accuracy | 100% | Spot-check yield/ROI against manual calc |
| Bargain Score calibration | σ < 8 | Score standard deviation across similar properties |
| Golden Opportunity precision | ≥ 75% | % of flagged deals that are truly undervalued |
| AI analysis quality (QA score) | ≥ 80/100 | QA agent evaluation on 5 dimensions |
| Analysis throughput | ≥ 40 deals/min | Batch processing speed |
| Comp match relevance | ≥ 70% | Comps within ±20% price, same suburb, ≤ 12mo |

---

## Self-Governance Rules

1. **NEVER guarantee returns.** Use "projected", "estimated", "based on current data". Every financial figure must be labeled as an estimate.
2. **Differentiate metrics correctly:**
   - `net_yield` = (Annual Rent − Operating Expenses excl. mortgage) / Purchase Price × 100
   - `cash_on_cash_return` = Annual Cash Flow after mortgage / Total Cash Invested × 100
   - `roi` = (Cash Flow + Equity Growth + Capital Appreciation) / Total Cash Invested × 100
3. **Flag missing data.** If suburb profile, comps, or key property fields are unavailable, reduce confidence level and note gaps in analysis.
4. **Use current VIC market rates:** Interest 6.25%, LVR 80%, management 7%, vacancy 2.5%, council rates 0.35%, insurance $1,800/yr.
5. **Degrade gracefully:** If LLM is unavailable, return Deal with full financial model but skip AI narrative. Set `ai_analysis = "AI analysis unavailable — financial model only"`.
6. **Escalate to QA** if Bargain Score distribution becomes bimodal (clustering at extremes) — suggests calibration drift.

---

## Growth Directives

1. **Sensitivity modelling:** Add interest rate stress testing (±1%, ±2%) to every deal analysis. Show "what if rates hit 8%?" scenarios.
2. **Depreciation schedules:** Integrate ATO depreciation estimates (Division 40 + Division 43) into net return calculations.
3. **Market cycle overlay:** Position each deal within the Melbourne property cycle (boom/correction/recovery/growth). Adjust confidence accordingly.
4. **Portfolio-aware scoring:** When a user has a profile, adjust Bargain Score weights based on their goals (cash-flow seekers weight yield higher; growth seekers weight capital growth higher).
5. **Automated re-analysis:** When market data updates (new median, rate change), auto-re-analyse saved deals and notify if Bargain Score changed ≥ 5 points.
6. **Conversion tracking:** Log which analyzed deals lead to offer generation → track Analyst-to-Closer conversion rate.

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| Identical net_yield/ROI/cash_on_cash formulas | CRITICAL — must differentiate (see rule #2) |
| Suburb profile not found | Use nearest comparable suburb's data; flag as "estimated" |
| Zero comps available | Skip comp analysis; rely on suburb median; reduce confidence |
| LLM hallucinates infrastructure | Cross-reference against `locations.py` infrastructure data |
| Extreme Bargain Score (0 or 100) | Clamp to [5, 95]; flag for human review |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Receives from** | `ScoutAgent` | `List[Property]` to analyse |
| **Uses** | `ROICalculator` | Cash flow computation engine |
| **Uses** | `BargainScorer` | Weighted scoring algorithm |
| **Uses** | `CompsEngine` | Comparable sales matching |
| **Feeds** | `StackerAgent` | Passes `Deal` objects for structuring |
| **Feeds** | `LiveCompsAgent` | Comp data enrichment |
| **Feeds** | `ConciergeAgent` | Golden Opportunity notifications |
| **Monitored by** | `QAAgent` | 5-dimension quality scoring |
