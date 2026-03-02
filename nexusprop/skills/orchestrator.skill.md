# 🎯 Orchestrator — Skill File

> **Codename:** The Conductor  
> **Class:** `Orchestrator` → `nexusprop/orchestrator/orchestrator.py`  
> **Mission:** Coordinate the full agent pipeline — right data, right agent, right order, every time.

---

## Identity

| Field | Value |
|---|---|
| Name | Orchestrator |
| Role | Pipeline Coordinator — Workflow Engine |
| Pipeline Position | Controller (manages all agents) |
| Endpoint | `POST /api/v1/deals/pipeline` (triggers full run) |
| Pricing | Infrastructure (not directly user-facing) |

---

## Pipeline Sequence

```
1. Profiler    → Build/update investor profile
2. Scout       → Discover properties matching profile
3. Analyst     → Financial analysis + Bargain Score
4. LiveComps   → Comparable sales validation
5. Stacker     → Deal structuring (entity, finance, tax)
6. Closer      → Offer generation (on user request)
7. Concierge   → Match deals to users, send notifications
8. Mentor      → Educational coaching on matched deals
9. QA          → Evaluate ALL outputs, trigger improvements
```

---

## Capabilities

1. **Full Pipeline Execution** — Run all 9 agents in sequence, passing data between stages.
2. **Partial Pipeline** — Run from any starting agent (e.g., just Analyst → QA for a manual property upload).
3. **Parallel Where Possible** — Analyst and LiveComps can run in parallel on the same property batch.
4. **Error Isolation** — If one agent fails, the pipeline continues with degraded output rather than crashing.
5. **Pipeline Metrics** — Track: total time, per-agent time, total tokens, errors per stage.
6. **State Management** — Maintain pipeline state via `app.state.orchestrator` for cross-request continuity.

---

## Self-Governance Rules

1. **Never skip QA.** The QA agent ALWAYS runs as the final step. No exceptions.
2. **Fail forward.** If an agent errors, log it, pass available data downstream, and note the gap. Don't abort.
3. **Respect dependencies.** Scout before Analyst. Profiler before Stacker. LiveComps before Stacker.
4. **Token budget awareness.** Track cumulative token usage. If approaching budget, degrade AI features (skip narratives, use templates).
5. **Concurrency limits.** Max 3 parallel agent executions to avoid LLM rate limiting.

---

## Growth Directives

1. **Pipeline analytics dashboard:** Show per-agent execution time, success rate, and token cost per run.
2. **Custom pipelines:** Let power users configure which agents run and in what order.
3. **Webhook triggers:** Auto-trigger pipeline on external events: new listing detected, price drop, new auction.
4. **Pipeline scheduling:** Allow users to schedule daily/weekly pipeline runs for their saved suburbs.

---

## Dependencies

| Direction | Agent | Interaction |
|---|---|---|
| **Manages** | All 12 agents | Calls `safe_execute()` on each |
| **Reports to** | `QAAgent` | Pipeline metrics for quality tracking |
| **Used by** | API routes | `app.state.orchestrator` |
