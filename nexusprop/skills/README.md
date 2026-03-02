# Agent Skill Files — Property Insights Melbourne

Each `.md` file in this directory defines one agent's **self-governance charter**:
who it is, what it owns, how it measures itself, and what growth looks like.

## How It Works

1. The **QA Agent** reads these skill files at startup.
2. Every agent output is scored against its skill file's KPIs.
3. Under-performing agents trigger automatic prompt improvement via `SkillTemplate`.
4. Growth directives push each agent toward measurable business outcomes.

## File Naming Convention

```
{agent_name}.skill.md   →   e.g. scout.skill.md
```

## Skill File Structure

| Section | Purpose |
|---|---|
| **Identity** | Name, role, one-line mission |
| **Capabilities** | What the agent can do |
| **Inputs / Outputs** | Data contracts |
| **KPIs** | Measurable performance targets |
| **Self-Governance Rules** | When to escalate, retry, or degrade |
| **Growth Directives** | How the agent evolves toward revenue |
| **Failure Modes** | Known failure patterns and mitigations |
| **Dependencies** | Upstream/downstream agents and tools |

---

*Property Insights Melbourne — Self-Governing Agentic Intelligence Stack*
