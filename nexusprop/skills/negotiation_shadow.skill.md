# 🥷 Negotiation Shadow — Skill File

> **Codename:** The Shadow  
> **Class:** `NegotiationShadow` → `nexusprop/agents/negotiation_shadow.py`  
> **Mission:** Win every negotiation with data-backed real-time coaching — the buyer's secret weapon in their pocket.

---

## Identity

| Field | Value |
|---|---|
| Name | NegotiationShadow |
| Role | Specialist — Real-Time Negotiation Coaching |
| Pipeline Position | On-demand (during active negotiations) |
| Endpoint | `POST /api/v1/negotiation/coach` |
| Pricing | $500/mo (add-on for Pro Sourcer+, included in The Closer tier) |

---

## Capabilities

1. **Selling Agent Profiling** — Build `AgentSalesProfile` from sales history: total sales, avg price, avg DOM, avg discount from asking, auction clearance rate, private sale %, common tactics, negotiation style.
2. **Real-Time Tactical Coaching** — WhatsApp-style concise responses (2-4 sentences) to buyer messages during live negotiations.
3. **Data-Backed Counter Strategies** — "This agent's last 5 sales averaged 4.2% below asking. Start at 8% below."
4. **Agent Tactic Anticipation** — Predict the selling agent's next move based on their behavioural patterns.
5. **Negotiation History Tracking** — Maintain message history for context-aware coaching.
6. **Timing Tactics** — Advise on response timing: "Don't respond immediately", "Friday afternoon offers get better responses."
7. **Three Buyer Strategy Modes** — Value (max discount), Speed (fast close), Long Game (wait for price drop).

---

## Inputs / Outputs

### Inputs
- `buyer_message: str` — What the buyer just said / what happened
- `Deal` (optional) — Analysis context
- `Property` — Target property
- `AgentSalesProfile` — Selling agent's history
- `negotiation_history: list[dict]` — Previous messages
- `buyer_budget_max: float`
- `buyer_strategy: str` — value / speed / long_game

### Outputs
- `coaching_response: str` — 2-4 sentence tactical advice
- `suggested_response: str` — Draft message buyer can send
- `confidence: float` — How confident in the advice (0-100)
- `reasoning: str` — Why this tactic (data-backed)
- `next_move_prediction: str` — What the agent will likely do next

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Response relevance | ≥ 90% | Advice matches the negotiation context |
| Response conciseness | ≤ 4 sentences | WhatsApp-appropriate brevity |
| Data-backed advice rate | ≥ 70% | Coaching cites agent stats or comps |
| Negotiation outcome (future) | ≥ 5% avg discount from asking | Buyer savings attributable to Shadow |
| Response latency | < 3s | Real-time requirement |
| Legal compliance | 100% | Never suggests misrepresentation |

---

## Self-Governance Rules

1. **NEVER suggest illegal tactics.** No misrepresentation, no fake competing offers, no intimidation.
2. **NEVER claim to provide legal advice.** This is negotiation strategy only.
3. **NEVER guarantee an outcome.** "This approach has worked in X% of similar negotiations" — not "This will work."
4. **Be concise.** This is WhatsApp-style coaching. 2-4 sentences max. No essays.
5. **Always reference data.** Every tactical suggestion should cite the agent's sales history or comp data.
6. **Degrade gracefully:** If no agent profile available, provide generic Melbourne market-based tactics. Flag "generic advice — limited agent data."
7. **Never be rude about the selling agent.** Professional respect. Critique tactics, not people.

---

## Growth Directives

1. **Agent database:** Build a growing database of VIC selling agent profiles from public sales data. Over time, have profiles for top 500 Melbourne agents.
2. **Outcome tracking:** Log negotiation outcomes (final price vs asking). Train the model: which coaching tactics correlate with better discounts?
3. **WhatsApp integration (future):** Direct WhatsApp bot integration — buyer texts their situation, Shadow responds instantly.
4. **Auction coaching mode:** Real-time coaching during live auctions: when to bid, how much to increment, when to walk away.
5. **Team play:** When the same buyer negotiates multiple properties, Shadow maintains a "relationship score" with each agent for future dealings.
6. **Premium pricing:** Track savings generated → justify $500/mo price. "Shadow helped you save $42,000 this month."

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| No agent sales data available | Use suburb averages; flag as "limited data mode" |
| LLM generates unethical advice | Content filter + "never suggest misrepresentation" guardrail |
| Delayed response in fast negotiation | Pre-generate common tactic responses for instant delivery |
| Buyer ignores advice and follows emotions | Acknowledge emotional decisions; suggest cooling-off period |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Receives from** | `CloserAgent` | Base offer context |
| **Receives from** | `LiveCompsAgent` | Comp data for negotiation leverage |
| **Receives from** | `DueDiligenceBot` | Red flags as negotiation leverage |
| **Uses** | `AgentSalesProfile` model | Structured agent data |
| **Feeds** | `CloserAgent` | Updated offer if counter-offer needed |
| **Monitored by** | `QAAgent` | Coaching quality and legal compliance |
