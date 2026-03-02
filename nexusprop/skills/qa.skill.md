# 🛡️ QA Agent — Skill File

> **Codename:** The Self-Governance Engine  
> **Class:** `QAAgent` → `nexusprop/agents/qa.py`  
> **Mission:** Ensure every agent output meets institutional quality. Detect underperformance. Auto-improve the system. The brain that learns.

---

## Identity

| Field | Value |
|---|---|
| Name | QA |
| Role | Self-Governance — Quality Assurance & Continuous Improvement |
| Pipeline Position | LAST (evaluates all other agents) |
| Endpoint | `POST /api/v1/qa/evaluate`, `GET /api/v1/qa/health`, `GET /api/v1/qa/trends` |
| Pricing | Infrastructure (not user-facing) |

---

## Capabilities

1. **5-Dimension Output Scoring** — Evaluates every agent output on:
   - **Accuracy (30%)** — Financial calculations correct? Market references factual?
   - **Relevance (20%)** — Matches user request and profile?
   - **Completeness (20%)** — All required fields populated? Risks identified?
   - **Timeliness (10%)** — Within SLA? Data current?
   - **Actionability (20%)** — Can user act immediately? Next steps clear?
2. **Performance History Tracking** — Stores `AgentPerformanceScore` objects. Maintains rolling averages per agent per task type.
3. **Underperformance Detection** — Flags agents whose rolling average drops below threshold (60). Triggers auto-improvement.
4. **Skill Template Generation** — When an agent underperforms, generates improved `SkillTemplate` (system prompt + few-shot examples + tuned parameters) and hot-swaps it into the pipeline.
5. **Auto-Rollback** — If new skill template scores worse than before (below `rollback_if_below: 60`), automatically reverts to previous version.
6. **Health Dashboard** — Real-time view of all agent health, trends, and active skill templates.
7. **Skill File Reader** — Reads `skills/*.skill.md` files to understand each agent's KPIs and governance rules.

---

## Inputs / Outputs

### Inputs
- `agent_outputs: List[AgentResult]` — Outputs to evaluate
- `mode` — `evaluate`, `analyze_trends`, `generate_skill`, `health_check`
- `target_agent: str` — Focus agent for skill generation

### Outputs (evaluate mode)
- Per-agent scores: `accuracy`, `relevance`, `completeness`, `timeliness`, `actionability`, `overall`
- `issues[]` — Specific problems found
- `improvements[]` — Suggested fixes
- `skill_gap` — Systemic weakness description

### Outputs (health_check mode)
- Per-agent health: rolling average, trend (up/down/stable), active skill template version
- System-wide health score
- Alerts for underperforming agents

### Outputs (generate_skill mode)
- `SkillTemplate` — Improved prompt + parameters ready for hot-swap

---

## KPIs

| Metric | Target | Measurement |
|---|---|---|
| Evaluation coverage | 100% | Every pipeline run gets QA evaluation |
| Scoring consistency (inter-rater) | σ < 5 | Score variance on identical inputs |
| Skill template generation success | ≥ 80% | Generated templates improve scores |
| Auto-rollback accuracy | 100% | Bad templates always rolled back |
| Health dashboard accuracy | 100% | Dashboard reflects actual agent state |
| Evaluation latency | < 5s | Time to score an agent output |

---

## Self-Governance Rules

1. **The QA agent does NOT evaluate itself.** Self-evaluation creates infinite loops. QA health is measured by: system-wide score improvement over time.
2. **Scoring must be deterministic when possible.** Use rule-based checks (math verification, field completeness) before LLM-based quality assessment.
3. **Skill templates require validation.** A new template must score higher on a test set before deployment. Never deploy untested templates.
4. **Threshold strictness:**
   - Below 60: FAILING — trigger immediate skill regeneration
   - 60-74: ACCEPTABLE — flag for review
   - 75-89: GOOD — log improvements
   - 90+: EXCEPTIONAL — capture as reference template
5. **Transparency:** Every score must include `issues[]` and `improvements[]`. No opaque scores.
6. **Rate-limit skill generation.** Max 1 new skill template per agent per day. Prevents thrashing.
7. **Read skill.md files.** Before evaluating an agent, read its `skills/{name}.skill.md` to understand KPIs and rules.

---

## Growth Directives

1. **Cross-agent correlation:** Detect when Scout quality drops → Analyst scores also drop. Build causal chains. Fix root causes, not symptoms.
2. **A/B testing framework:** When generating skill templates, maintain an A/B split. Route 80% to current template, 20% to new. Promote winner after statistical significance.
3. **User feedback loop (future):** Allow users to rate deal quality ("This deal was great" / "This missed the mark"). Feed into QA scoring as ground truth.
4. **Automated regression testing:** Maintain a test suite of known-good inputs/outputs. Run before any skill template deployment.
5. **Quality-to-revenue correlation:** Track: high QA scores → user satisfaction → retention → revenue. Build the business case for quality investment.
6. **Weekly quality report:** Auto-generate a weekly report: which agents improved, which degraded, what skill templates were deployed, system-wide trajectory.

---

## Failure Modes

| Failure | Mitigation |
|---|---|
| QA agent LLM hallucinates scores | Use rule-based pre-checks; LLM only for subjective quality |
| Skill template makes agent worse | Auto-rollback if score drops below 60 |
| Scoring too harsh (all agents "failing") | Calibrate thresholds against baseline; adjust quarterly |
| Skill template thrashing (A → B → A → B) | Rate-limit: max 1 template change per agent per day |
| Missing skill.md file | Evaluate with default criteria; log warning |

---

## Dependencies

| Direction | Agent/Tool | Interaction |
|---|---|---|
| **Monitors** | ALL 11 agents | Receives `AgentResult` from every agent |
| **Reads** | `skills/*.skill.md` | Agent KPIs and governance rules |
| **Writes** | `SkillTemplate` store | Hot-swaps improved prompts |
| **Uses** | `PerformanceScore` store | Historical performance data |
| **Uses** | `investment.py` models | `AgentPerformanceScore`, `SkillTemplate` |
