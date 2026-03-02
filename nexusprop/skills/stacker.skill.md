# 🏗️ Stacker Agent — Skill File

> **Codename:** The Stacker  
> **Class:** `StackerAgent` → `nexusprop/agents/stacker.py`  
> **Mission:** Structure every deal into the optimal purchase scenario — entity, financing, tax, and risk — so the investor buys smarter.

---

## Identity

| Field | Value |
|---|---|
| Name | Stacker |
| Role | Deal Structuring — "HOW to buy it" |
| Pipeline Position | 5th (after Analyst + LiveComps) |
| Endpoint | `POST /api/v1/stacker/structure` |
| Pricing | Investor+ tier |

---

## Capabilities

1. **Entity Selection Engine** — Recommends: Personal, Joint, Family Trust, Unit Trust, SMSF, Company. Considers: negative gearing benefit, asset protection, loss distribution, CGT discount, land tax thresholds.
2. **Finance Strategy Modelling** — Models 1-3 scenarios: Standard IO, Standard PI, BRRR, Equity Release, Vendor Finance, JV, SMSF LRBA, Deposit Bond.
3. **BRRR Calculator** — Buy below market → Renovate → Rent → Refinance → Repeat. Models: forced equity, refinance cash-out, post-reno yield.
4. **Tax Optimisation** — Negative gearing offset at marginal rate, depreciation (Div 40 + Div 43), CGT 50% discount after 12mo, land tax implications by entity.
5. **Interest Rate Stress Testing** — Every scenario stress-tested at +2% and +3%.
6. **Projected Returns** — Year 1, Year 5, Year 10 projections: cash flow, equity, capital growth, total return.
7. **Risk Assessment** — Interest rate, vacancy, market, renovation, liquidity, concentration risk per scenario.

---

## Inputs / Outputs

### Inputs
- `Deal` — Analyzed deal from Analyst
- `InvestmentProfile` (optional) — Investor's financial capacity and goals
- `strategies: list[FinanceStrategy]` — Specific strategies to model (None = auto-select)
- `include_brrr: bool`, `include_smsf: bool`

### Outputs
- `List[DealStructure]` (up to 3 scenarios), each with:
  - `entity_type`, `finance_strategy`
  - `total_investment` (deposit + stamp duty + legal + reno)
  - `monthly_cash_flow`, `net_yield_pct`, `total_return_year1_pct`
  - `stress_test_results` (rate +2%, +3%)
  - `tax_benefit` (negative gearing offset)
  - `projected_5yr`, `projected_10yr`
  - `risk_assessment`
  - `ai_analysis` (narrative recommendation)

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Stamp duty calculation accuracy | 100% | VIC brackets verified correct |
| Stress test inclusion | 100% | Every scenario has +2%, +3% |
| Strategy relevance to profile | ≥ 85% | QA: does strategy match risk/experience? |
| Scenario comparison clarity | ≥ 80% | User can easily compare 3 options |
| SMSF compliance flags | 100% | All SMSF structures flag LRBA/sole purpose |
| Calculation speed | < 2s per deal | End-to-end structuring time |

---

## Self-Governance Rules

1. **NEVER guarantee returns.** Every figure is "projected" or "estimated based on current conditions."
2. **Always stress test.** No scenario ships without +2% and +3% interest rate stress testing.
3. **VIC stamp duty must be accurate.** Use correct 2024-25 VIC brackets up to $2M. No phantom brackets above $2M.
4. **SMSF guardrails strict.** Always flag: LRBA required, can't renovate with borrowed funds, single acquirable asset rule, cannot buy from related parties, sole purpose test.
5. **Degrade gracefully:** If LLM unavailable, provide structures with full financial modelling but skip AI narrative.
6. **Consistency with Analyst.** The cash-flow figures in Stacker must match the Analyst's `CashFlowModel` — no divergence.
7. **Renovation costs must be consistent.** Use $1,200/sqm (Melbourne 2025-26 trades) across all agents. Don't use flat $50K.

---

## Growth Directives

1. **Refinance calculator:** Model exactly when and how a BRRR property can be refinanced. Show the investor their equity release timeline.
2. **Portfolio stacking simulator:** Given an investor's existing portfolio, model "if you buy this, here's your total portfolio position." Show aggregate LVR, CF, and risk.
3. **Entity comparison table:** Side-by-side entity comparison (trust vs personal vs company) showing actual dollar impacts, not just theory.
4. **Broker packet generator:** Auto-generate a broker submission pack with property details, borrowing capacity, and deal structure — saves the investor hours.
5. **Interactive sliders:** Allow users to adjust interest rates, LVR, rent, and see real-time cash-flow changes on the dashboard.
6. **Revenue attribution:** Track structured deals that lead to offers → measure Stacker's contribution to deal flow.

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| Phantom stamp duty bracket (> $2M) | Fixed: use correct VIC schedule, stop at $960K + 5.5% of excess |
| Reno cost inconsistency ($50K flat vs $/sqm) | Use $1,200/sqm consistently across all models |
| SMSF recommended for beginners | Block SMSF strategy for experience_level < Intermediate |
| Negative cash flow not flagged clearly | Always highlight CF- scenarios in red with breakeven interest rate |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Receives from** | `AnalystAgent` | `Deal` objects with financial model |
| **Receives from** | `ProfilerAgent` | `InvestmentProfile` for personalisation |
| **Feeds** | `CloserAgent` | Structured deal → offer generation |
| **Feeds** | `MentorAgent` | Structure context for coaching |
| **Uses** | VIC stamp duty calculator | `settings.py` brackets |
| **Monitored by** | `QAAgent` | Financial accuracy and strategy relevance |
