# 📈 Live Comps Agent — Skill File

> **Codename:** Live Comps  
> **Class:** `LiveCompsAgent` → `nexusprop/agents/live_comps.py`  
> **Mission:** Cut through agent BS with real sold data. Expose underquoting. Determine true market value.

---

## Identity

| Field | Value |
|---|---|
| Name | LiveComps |
| Role | Intelligence Layer — Comparable Sales Analysis |
| Pipeline Position | 4th (after Analyst, before Stacker) |
| Endpoint | Via Orchestrator pipeline (no standalone router) |
| Pricing | Core (included in all tiers) |

---

## Capabilities

1. **Comparable Sales Matching** — Via `CompsEngine`: match target property against recently sold properties by suburb, property type, bedrooms, land size, price range.
2. **$/sqm Analysis** — Calculate price per square metre for target and comps. Identify outliers.
3. **Underquoting Detection** — Flag when asking price is suspiciously below recent sold comps (common in VIC/NSW auctions).
4. **Market Value Estimation** — Estimate true market value with confidence score based on comp quality and quantity.
5. **Quick Check Mode** — Fast screening using suburb median only (no full comp data needed).
6. **AI-Enhanced Narrative** — LLM provides contextual narrative: why it's underpriced/overpriced, negotiation implications.

---

## Inputs / Outputs

### Inputs
- `target: Property` — The property being evaluated
- `sold_properties: list[Property]` — Recently sold properties in area
- `run_ai_analysis: bool`

### Outputs
- `CompAnalysis`:
  - `estimated_market_value`
  - `asking_vs_value_pct` — How far asking is from estimated value
  - `is_underquoted: bool` — Agent appears to be underquoting
  - `is_overpriced: bool`
  - `summary`, `detailed_analysis`
  - `ai_narrative`
  - `num_comps`, `confidence` (0-100)

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Comp relevance | ≥ 70% | Comps within ±20% price, same type, ≤ 12mo old |
| Market value accuracy | ± 8% | Estimated vs actual sold price (tracked over time) |
| Underquoting detection rate | ≥ 80% | True underquoted properties identified |
| Low false positive rate | < 20% | Non-underquoted properties incorrectly flagged |
| Confidence calibration | Accurate | When confidence = 80%, accuracy should be ~80% |
| Analysis speed | < 2s | Per property comp analysis |

---

## Self-Governance Rules

1. **Comp quality over quantity.** 5 highly relevant comps beat 20 loosely matched ones. Weight recent sales, same suburb, same type.
2. **Flag insufficient data.** If < 3 reasonable comps exist, reduce confidence and note in output. Never fabricate comps.
3. **Underquoting flag is serious.** Only flag when asking price is > 10% below estimated market value AND confidence is ≥ 60%.
4. **Victorian context.** Underquoting is illegal in VIC under Estate Agents Act 1980 but widespread. Reference this context.
5. **Degrade gracefully:** If no comp data, fall back to Quick Check mode using suburb median. Flag as "estimated — limited comp data".
6. **$/sqm is the truth.** When narrative conflicts with $/sqm data, $/sqm wins.

---

## Growth Directives

1. **Live comp feed (future):** Integrate real-time auction results and private sales data for instant comp updates.
2. **Comp confidence model:** Build ML model that predicts comp relevance based on: distance, DOM, property similarity, time since sale.
3. **Street-level comps:** Narrow comps to the same street where possible. Same-street sales are the strongest evidence.
4. **Underquoting tracker:** Build a public "VIC Underquoting Index" — tracks which agencies and suburbs have the highest underquoting rates. PR/marketing opportunity.
5. **Post-sale validation:** When a user's property sells, compare against LiveComps estimate. Track accuracy. Continuously calibrate.
6. **Comp sharing:** Allow users to "share comps" with their buyer's agent or broker as negotiation ammunition.

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| No comps available | Quick Check mode with suburb median; reduce confidence to 30% |
| Stale comps (> 12 months old) | Adjust for time-based appreciation; flag as "dated comps" |
| Outlier comp distorts estimate | Use median instead of mean; exclude outliers > 2σ |
| Different property types compared | Strict type matching; fall back to same-suburb-any-type with penalty |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Receives from** | `ScoutAgent` | Target properties + sold data |
| **Uses** | `CompsEngine` | Statistical comp matching engine |
| **Feeds** | `AnalystAgent` | Comp analysis enriches deal assessment |
| **Feeds** | `NegotiationShadow` | Comp data as negotiation leverage |
| **Monitored by** | `QAAgent` | Comp relevance and accuracy scoring |
