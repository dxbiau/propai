"""
QA Agent — Self-Governance Engine for Property Insights Australia.

The "brain that learns" — evaluates every agent output, scores quality,
identifies underperformance, and generates improved skill templates.

This is the KEY differentiator: a self-improving AI ecosystem where
each pipeline run makes the next one better.

Architecture:
  1. EVALUATE: Score every agent output on 5 dimensions
  2. STORE: Persist scores to performance database
  3. DETECT: Identify underperforming agents/tasks
  4. IMPROVE: Generate improved prompts/parameters
  5. DEPLOY: Hot-swap improved skills into the pipeline
  6. VERIFY: Confirm improvement or rollback

The QA agent runs AFTER every pipeline execution and also in
scheduled batch mode for trend analysis.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.investment import (
    AgentPerformanceScore,
    SkillTemplate,
)


QA_SYSTEM_PROMPT = """You are the Property Insights Australia QA Agent — the self-governance brain of the platform.

Your role: Evaluate the quality of every agent output and generate improvement recommendations.

EVALUATION DIMENSIONS (each scored 0-100):

1. ACCURACY (30% weight)
   - Are financial calculations correct?
   - Are market references factual?
   - Are comparables genuine and recent?
   - Is the pricing analysis realistic?

2. RELEVANCE (20% weight)
   - Does the output match what the user asked?
   - Is it tailored to their profile and goals?
   - Does it address their experience level appropriately?

3. COMPLETENESS (20% weight)
   - Are all required data fields populated?
   - Is the analysis comprehensive?
   - Are risks properly identified?
   - Are next steps clear and actionable?

4. TIMELINESS (10% weight)
   - Did the agent respond within SLA?
   - Is the data current (not stale)?
   - Are market conditions reflected?

5. ACTIONABILITY (20% weight)
   - Can the user act on this output immediately?
   - Are concrete next steps provided?
   - Are recommendations specific (not vague)?

SCORING GUIDE:
- 90-100: Exceptional — publish without changes
- 75-89: Good — minor improvements possible
- 60-74: Acceptable — notable gaps but usable
- 40-59: Below standard — requires significant improvement
- 0-39: Failing — output should be regenerated

WHEN EVALUATING:
- Check math: Does yield calculation actually match the numbers?
- Check consistency: Do property details match between sections?
- Check Australian accuracy: Correct stamp duty rates, current interest rates?
- Check completeness: Are all advertised features actually provided?
- Check bias: Is the analysis balanced (both pros and cons)?

OUTPUT FORMAT:
{
    "accuracy_score": 85,
    "relevance_score": 90,
    "completeness_score": 75,
    "timeliness_score": 95,
    "actionability_score": 80,
    "overall_score": 84.5,
    "issues": ["Issue 1", "Issue 2"],
    "improvements": ["Suggestion 1", "Suggestion 2"],
    "skill_gap": "description of the systemic gap if any"
}"""


SKILL_GENERATION_PROMPT = """You are an expert prompt engineer for a property investment AI system.

Given an agent's current performance data and identified issues, generate an improved
system prompt that addresses the weaknesses while maintaining the strengths.

The improved prompt must:
1. Fix specific accuracy issues identified
2. Add guardrails for the detected failure modes
3. Include better examples where needed
4. Maintain the agent's core functionality
5. Be Australian property market specific

Return ONLY the improved system prompt text. No explanations."""


class QAAgent(BaseAgent):
    """
    QA Agent — Self-Governance Engine.

    Evaluates every agent output, maintains performance history,
    detects underperformance, and generates improved skill templates.

    The self-improving feedback loop:
    Pipeline Output → QA Evaluation → Score Storage →
    Underperformance Detection → Skill Generation → Hot-Swap → Verify
    """

    def __init__(self):
        super().__init__("QA")
        # In-memory performance store (will be persisted to DB later)
        self._performance_history: list[AgentPerformanceScore] = []
        self._skill_templates: dict[str, SkillTemplate] = {}
        self._performance_thresholds = {
            "min_acceptable": 60.0,
            "target": 80.0,
            "rollback_threshold": 55.0,
        }

    async def execute(
        self,
        agent_outputs: Optional[list[AgentResult]] = None,
        mode: str = "evaluate",
        target_agent: Optional[str] = None,
    ) -> AgentResult:
        """
        Run QA evaluation or self-improvement.

        Args:
            agent_outputs: List of AgentResults to evaluate
            mode: evaluate, analyze_trends, generate_skill, health_check
            target_agent: Specific agent to focus on (for generate_skill mode)
        """
        self.logger.info("qa_started", mode=mode, outputs_count=len(agent_outputs or []))

        handlers = {
            "evaluate": self._evaluate_outputs,
            "analyze_trends": self._analyze_trends,
            "generate_skill": self._generate_skill,
            "health_check": self._health_check,
        }

        handler = handlers.get(mode, self._evaluate_outputs)
        return await handler(agent_outputs=agent_outputs, target_agent=target_agent)

    async def _evaluate_outputs(
        self,
        agent_outputs: Optional[list[AgentResult]] = None,
        target_agent: Optional[str] = None,
    ) -> AgentResult:
        """Evaluate all agent outputs from a pipeline run."""
        if not agent_outputs:
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={"message": "No outputs to evaluate", "scores": []},
            )

        scores: list[dict] = []
        total_tokens = 0
        alerts: list[str] = []

        for output in agent_outputs:
            if not output.success:
                # Failed outputs get a low score automatically
                score = AgentPerformanceScore.calculate(
                    agent_name=output.agent_name,
                    task_type="failed_execution",
                    accuracy=0,
                    relevance=0,
                    completeness=0,
                    timeliness=0,
                    actionability=0,
                    issues=[f"Agent failed: {output.error}"],
                    suggestions=["Investigate root cause of failure"],
                    run_id=output.id,
                )
                self._performance_history.append(score)
                scores.append(score.model_dump(mode="json"))
                alerts.append(f"ALERT: {output.agent_name} FAILED — {output.error}")
                continue

            # Use LLM to evaluate the output quality
            score = await self._evaluate_single(output)
            self._performance_history.append(score)
            scores.append(score.model_dump(mode="json"))

            total_tokens += 0  # Will be set from LLM call

            # Check for underperformance
            if score.overall_score < self._performance_thresholds["min_acceptable"]:
                alerts.append(
                    f"UNDERPERFORMANCE: {output.agent_name} scored {score.overall_score}/100 "
                    f"(threshold: {self._performance_thresholds['min_acceptable']})"
                )

        # Calculate aggregate metrics
        if scores:
            avg_score = sum(s.get("overall_score", 0) for s in scores) / len(scores)
        else:
            avg_score = 0

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "scores": scores,
                "pipeline_avg_score": round(avg_score, 1),
                "agents_evaluated": len(scores),
                "alerts": alerts,
                "underperforming": [
                    s for s in scores
                    if s.get("overall_score", 100) < self._performance_thresholds["min_acceptable"]
                ],
            },
            tokens_used=total_tokens,
        )

    async def _evaluate_single(self, output: AgentResult) -> AgentPerformanceScore:
        """Evaluate a single agent output using LLM + heuristics."""
        # First: heuristic evaluation (fast, no LLM needed)
        heuristic_score = self._heuristic_evaluate(output)

        # Second: LLM evaluation (deeper analysis, if output has data)
        llm_score = None
        llm_tokens = 0
        if output.data and isinstance(output.data, dict):
            try:
                llm_score, llm_tokens = await self._llm_evaluate(output)
            except Exception as e:
                self.logger.warning("llm_evaluation_failed", error=str(e))

        # Blend heuristic and LLM scores
        if llm_score:
            final_score = AgentPerformanceScore.calculate(
                agent_name=output.agent_name,
                task_type=self._infer_task_type(output),
                accuracy=(heuristic_score["accuracy"] * 0.3 + llm_score.get("accuracy_score", 70) * 0.7),
                relevance=(heuristic_score["relevance"] * 0.3 + llm_score.get("relevance_score", 70) * 0.7),
                completeness=(heuristic_score["completeness"] * 0.3 + llm_score.get("completeness_score", 70) * 0.7),
                timeliness=heuristic_score["timeliness"],  # Heuristic-only (timing data)
                actionability=(heuristic_score["actionability"] * 0.3 + llm_score.get("actionability_score", 70) * 0.7),
                issues=llm_score.get("issues", []),
                suggestions=llm_score.get("improvements", []),
                run_id=output.id,
            )
        else:
            final_score = AgentPerformanceScore.calculate(
                agent_name=output.agent_name,
                task_type=self._infer_task_type(output),
                accuracy=heuristic_score["accuracy"],
                relevance=heuristic_score["relevance"],
                completeness=heuristic_score["completeness"],
                timeliness=heuristic_score["timeliness"],
                actionability=heuristic_score["actionability"],
                issues=heuristic_score.get("issues", []),
                suggestions=[],
                run_id=output.id,
            )

        return final_score

    def _heuristic_evaluate(self, output: AgentResult) -> dict:
        """Fast heuristic evaluation without LLM."""
        scores = {
            "accuracy": 70.0,
            "relevance": 70.0,
            "completeness": 70.0,
            "timeliness": 90.0,
            "actionability": 70.0,
            "issues": [],
        }

        data = output.data or {}

        # Timeliness: Based on execution time
        if output.execution_time_ms > 30_000:
            scores["timeliness"] = 40.0
            scores["issues"].append(f"Slow execution: {output.execution_time_ms/1000:.1f}s")
        elif output.execution_time_ms > 15_000:
            scores["timeliness"] = 60.0
        elif output.execution_time_ms > 5_000:
            scores["timeliness"] = 80.0

        # Completeness: Check for expected fields
        if isinstance(data, dict):
            # Check for empty/null values
            empty_count = sum(1 for v in data.values() if v is None or v == "" or v == [])
            total_fields = max(len(data), 1)
            completeness_ratio = 1 - (empty_count / total_fields)
            scores["completeness"] = max(completeness_ratio * 100, 30)

            # Check for deal-specific completeness
            if "deals" in data:
                deals = data["deals"]
                if isinstance(deals, list) and deals:
                    scores["completeness"] += 10
                elif isinstance(deals, list) and not deals:
                    scores["completeness"] -= 20
                    scores["issues"].append("No deals produced")

            # Check for AI analysis presence
            if data.get("ai_analysis") or data.get("coaching") or data.get("analysis"):
                scores["actionability"] += 10
            else:
                scores["actionability"] -= 10

        # Agent-specific heuristics
        if output.agent_name == "Scout":
            props = data.get("properties", [])
            if isinstance(props, list):
                if len(props) >= 10:
                    scores["accuracy"] += 10
                elif len(props) == 0:
                    scores["accuracy"] = 30
                    scores["issues"].append("Scout found zero properties")

        elif output.agent_name == "Analyst":
            deals = data.get("deals", [])
            if isinstance(deals, list):
                for deal_data in deals:
                    if isinstance(deal_data, dict):
                        # Check for reasonable yield
                        cf = deal_data.get("cash_flow", {})
                        if isinstance(cf, dict):
                            gross_yield = cf.get("gross_rental_yield", 0)
                            if gross_yield > 30:
                                scores["accuracy"] -= 15
                                scores["issues"].append(f"Suspiciously high yield: {gross_yield}%")
                            if gross_yield == 0:
                                scores["completeness"] -= 10
                                scores["issues"].append("Zero gross yield — missing rent data?")

        elif output.agent_name == "Stacker":
            structures = data.get("structures", [])
            if isinstance(structures, list) and not structures:
                scores["completeness"] = 30
                scores["issues"].append("Stacker produced zero deal structures")

        # Cap scores
        for key in ["accuracy", "relevance", "completeness", "timeliness", "actionability"]:
            scores[key] = max(0, min(100, scores[key]))

        return scores

    async def _llm_evaluate(self, output: AgentResult) -> tuple[dict, int]:
        """Use LLM for deeper quality evaluation."""
        # Prepare a summary of the output for evaluation
        data_summary = json.dumps(output.data, default=str)[:3000]

        prompt = f"""Evaluate this agent output for quality.

AGENT: {output.agent_name}
EXECUTION TIME: {output.execution_time_ms:.0f}ms
TOKENS USED: {output.tokens_used}

OUTPUT DATA (truncated):
{data_summary}

Score each dimension 0-100 and list specific issues/improvements.
Return ONLY valid JSON:
{{
    "accuracy_score": 0-100,
    "relevance_score": 0-100,
    "completeness_score": 0-100,
    "timeliness_score": 0-100,
    "actionability_score": 0-100,
    "issues": ["specific issue 1", "specific issue 2"],
    "improvements": ["specific improvement 1"],
    "skill_gap": "systemic gap if any, or null"
}}"""

        response, tokens = await self.ask_llm(
            prompt=prompt,
            system=QA_SYSTEM_PROMPT,
            max_tokens=1024,
            temperature=0.2,
        )

        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            result = json.loads(json_str.strip())
            return result, tokens
        except (json.JSONDecodeError, IndexError):
            self.logger.warning("llm_eval_parse_failed", response=response[:200])
            return {}, tokens

    async def _analyze_trends(
        self,
        agent_outputs: Optional[list[AgentResult]] = None,
        target_agent: Optional[str] = None,
    ) -> AgentResult:
        """Analyze performance trends across historical data."""
        # Group scores by agent
        agent_scores: dict[str, list[AgentPerformanceScore]] = {}
        for score in self._performance_history:
            if target_agent and score.agent_name != target_agent:
                continue
            agent_scores.setdefault(score.agent_name, []).append(score)

        trend_report: dict[str, dict] = {}
        underperforming_agents: list[str] = []

        for agent_name, scores in agent_scores.items():
            if not scores:
                continue

            # Calculate averages
            avg_overall = sum(s.overall_score for s in scores) / len(scores)
            recent = scores[-5:]  # Last 5 evaluations
            recent_avg = sum(s.overall_score for s in recent) / len(recent)

            # Trend direction
            if len(scores) >= 3:
                earlier = scores[:-3]
                later = scores[-3:]
                earlier_avg = sum(s.overall_score for s in earlier) / max(len(earlier), 1)
                later_avg = sum(s.overall_score for s in later) / len(later)
                trend = "improving" if later_avg > earlier_avg + 2 else (
                    "declining" if later_avg < earlier_avg - 2 else "stable"
                )
            else:
                trend = "insufficient_data"

            # Common issues
            all_issues = []
            for s in scores:
                all_issues.extend(s.issues_found)
            issue_counts: dict[str, int] = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            top_issues = sorted(issue_counts.items(), key=lambda x: -x[1])[:5]

            trend_report[agent_name] = {
                "evaluations_count": len(scores),
                "avg_overall": round(avg_overall, 1),
                "recent_avg": round(recent_avg, 1),
                "trend": trend,
                "top_issues": [{"issue": i, "count": c} for i, c in top_issues],
                "dimension_averages": {
                    "accuracy": round(sum(s.accuracy_score for s in scores) / len(scores), 1),
                    "relevance": round(sum(s.relevance_score for s in scores) / len(scores), 1),
                    "completeness": round(sum(s.completeness_score for s in scores) / len(scores), 1),
                    "timeliness": round(sum(s.timeliness_score for s in scores) / len(scores), 1),
                    "actionability": round(sum(s.actionability_score for s in scores) / len(scores), 1),
                },
            }

            if recent_avg < self._performance_thresholds["min_acceptable"]:
                underperforming_agents.append(agent_name)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "trend_report": trend_report,
                "underperforming_agents": underperforming_agents,
                "total_evaluations": len(self._performance_history),
                "recommendation": (
                    f"Generate improved skills for: {', '.join(underperforming_agents)}"
                    if underperforming_agents
                    else "All agents performing within acceptable thresholds"
                ),
            },
        )

    async def _generate_skill(
        self,
        agent_outputs: Optional[list[AgentResult]] = None,
        target_agent: Optional[str] = None,
    ) -> AgentResult:
        """Generate an improved skill template for an underperforming agent."""
        if not target_agent:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="target_agent required for skill generation",
            )

        # Get this agent's performance history
        agent_scores = [
            s for s in self._performance_history
            if s.agent_name == target_agent
        ]

        if not agent_scores:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"No performance data for {target_agent}",
            )

        # Collect issues and suggestions
        all_issues = []
        all_suggestions = []
        for score in agent_scores[-10:]:  # Last 10 evaluations
            all_issues.extend(score.issues_found)
            all_suggestions.extend(score.improvement_suggestions)

        avg_score = sum(s.overall_score for s in agent_scores) / len(agent_scores)

        # Get dimension weaknesses
        dim_avgs = {
            "accuracy": sum(s.accuracy_score for s in agent_scores) / len(agent_scores),
            "relevance": sum(s.relevance_score for s in agent_scores) / len(agent_scores),
            "completeness": sum(s.completeness_score for s in agent_scores) / len(agent_scores),
            "timeliness": sum(s.timeliness_score for s in agent_scores) / len(agent_scores),
            "actionability": sum(s.actionability_score for s in agent_scores) / len(agent_scores),
        }
        weakest = sorted(dim_avgs.items(), key=lambda x: x[1])[:2]

        prompt = f"""Generate an improved system prompt for the {target_agent} agent.

CURRENT PERFORMANCE:
- Average Score: {avg_score:.1f}/100
- Weakest Dimensions: {', '.join(f'{k}: {v:.1f}' for k, v in weakest)}
- Common Issues: {'; '.join(set(all_issues[-10:]))}
- Previous Suggestions: {'; '.join(set(all_suggestions[-10:]))}

DIMENSION SCORES:
{json.dumps(dim_avgs, indent=2)}

The improved prompt must:
1. Address the specific weaknesses identified
2. Add guardrails to prevent recurring issues
3. Include better examples for accuracy
4. Improve {weakest[0][0]} specifically (score: {weakest[0][1]:.1f})
5. Maintain all existing capabilities
6. Be specific to Australian property market

Generate the complete improved system prompt."""

        improved_prompt, tokens = await self.ask_llm(
            prompt=prompt,
            system=SKILL_GENERATION_PROMPT,
            max_tokens=4096,
            temperature=0.3,
        )

        # Create skill template
        existing_version = 0
        if target_agent in self._skill_templates:
            existing_version = self._skill_templates[target_agent].version

        skill = SkillTemplate(
            agent_name=target_agent,
            task_type="general",
            version=existing_version + 1,
            system_prompt=improved_prompt,
            avg_score_before=avg_score,
            parameters={
                "weakest_dimensions": dict(weakest),
                "issues_addressed": list(set(all_issues[-5:])),
            },
        )

        self._skill_templates[target_agent] = skill

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "skill": skill.model_dump(mode="json"),
                "target_agent": target_agent,
                "avg_score_before": avg_score,
                "issues_addressed": list(set(all_issues[-5:])),
                "improved_prompt_length": len(improved_prompt),
            },
            tokens_used=tokens,
        )

    async def _health_check(
        self,
        agent_outputs: Optional[list[AgentResult]] = None,
        target_agent: Optional[str] = None,
    ) -> AgentResult:
        """System-wide health check of all agents."""
        # Get trend data
        trends = await self._analyze_trends()

        trend_data = trends.data or {}
        report = trend_data.get("trend_report", {})

        # Overall system health
        all_avgs = [r.get("recent_avg", 0) for r in report.values()]
        system_avg = sum(all_avgs) / max(len(all_avgs), 1) if all_avgs else 0

        # Active skills
        active_skills = {
            k: {"version": v.version, "avg_before": v.avg_score_before}
            for k, v in self._skill_templates.items()
            if v.is_active
        }

        # Determine system health status
        if system_avg >= 80:
            health_status = "HEALTHY"
        elif system_avg >= 60:
            health_status = "ACCEPTABLE"
        elif system_avg >= 40:
            health_status = "DEGRADED"
        else:
            health_status = "CRITICAL"

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "health_status": health_status,
                "system_avg_score": round(system_avg, 1),
                "agents_report": report,
                "active_skills": active_skills,
                "total_evaluations": len(self._performance_history),
                "underperforming": trend_data.get("underperforming_agents", []),
                "recommendations": self._get_health_recommendations(report),
            },
        )

    def _get_health_recommendations(self, report: dict) -> list[str]:
        """Generate health check recommendations."""
        recs = []

        for agent_name, data in report.items():
            if data.get("trend") == "declining":
                recs.append(
                    f"⚠️ {agent_name} is declining — generate improved skill template"
                )
            if data.get("recent_avg", 100) < 60:
                recs.append(
                    f"🔴 {agent_name} below threshold ({data['recent_avg']:.0f}/100) — immediate attention needed"
                )

            # Dimension-specific recommendations
            dims = data.get("dimension_averages", {})
            for dim, score in dims.items():
                if score < 50:
                    recs.append(
                        f"📊 {agent_name}.{dim} critically low ({score:.0f}/100)"
                    )

        if not recs:
            recs.append("✅ All agents performing within acceptable parameters")

        return recs

    def _infer_task_type(self, output: AgentResult) -> str:
        """Infer the task type from the agent output."""
        name = output.agent_name.lower()
        type_map = {
            "scout": "property_discovery",
            "analyst": "deal_analysis",
            "closer": "offer_generation",
            "concierge": "user_matching",
            "livecomps": "comparable_analysis",
            "profiler": "investor_profiling",
            "stacker": "deal_structuring",
            "negotiationshadow": "negotiation_coaching",
            "duediligencebot": "document_analysis",
            "mentor": "education_coaching",
        }
        return type_map.get(name, "unknown")

    def get_agent_skill(self, agent_name: str) -> Optional[SkillTemplate]:
        """Get the current active skill for an agent (for hot-swapping prompts)."""
        return self._skill_templates.get(agent_name)

    def get_performance_summary(self) -> dict:
        """Get a quick summary of all agent performance."""
        summary: dict[str, dict] = {}
        for score in self._performance_history:
            name = score.agent_name
            if name not in summary:
                summary[name] = {"scores": [], "count": 0}
            summary[name]["scores"].append(score.overall_score)
            summary[name]["count"] += 1

        result = {}
        for name, data in summary.items():
            scores = data["scores"]
            result[name] = {
                "count": data["count"],
                "avg": round(sum(scores) / len(scores), 1),
                "min": round(min(scores), 1),
                "max": round(max(scores), 1),
                "recent": round(sum(scores[-3:]) / len(scores[-3:]), 1) if scores else 0,
            }

        return result

    async def evaluate_and_improve(
        self,
        agent_outputs: list[AgentResult],
    ) -> AgentResult:
        """
        Full self-governance cycle: evaluate → detect → improve.

        This is the main entry point called AFTER each pipeline run.
        """
        # Step 1: Evaluate all outputs
        eval_result = await self._evaluate_outputs(agent_outputs=agent_outputs)
        eval_data = eval_result.data or {}

        # Step 2: Check for underperformance
        underperforming = eval_data.get("underperforming", [])

        # Step 3: Generate improved skills for underperformers
        skills_generated = []
        for agent_data in underperforming:
            agent_name = agent_data.get("agent_name", "")
            if agent_name:
                try:
                    skill_result = await self._generate_skill(target_agent=agent_name)
                    if skill_result.success:
                        skills_generated.append(agent_name)
                except Exception as e:
                    self.logger.warning("skill_generation_failed", agent=agent_name, error=str(e))

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "evaluation": eval_data,
                "skills_generated_for": skills_generated,
                "pipeline_health": eval_data.get("pipeline_avg_score", 0),
                "self_governance_cycle": "complete",
            },
        )
