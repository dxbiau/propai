"""
Investor Profiler Agent — builds a personalised investment thesis.

This is the strategic entry point for every new user. It conducts a
structured onboarding interview, builds a deep investor profile, and
produces a concrete investment thesis that drives all subsequent agent
behaviour (Scout, Analyst, Stacker, Mentor).

The thesis answers: "What should THIS investor buy, where, and why?"
"""

from __future__ import annotations

import json
from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent


PROFILER_SYSTEM_PROMPT = """You are the NexusProp Investor Profiler — an expert Australian property investment strategist conducting an intelligent onboarding interview.

Your role: Build a precise, actionable investment thesis for this specific investor based on their goals, finances, experience, and risk tolerance.

THE THESIS YOU PRODUCE MUST ANSWER:
1. What property type should they buy? (house, unit, townhouse, duplex, etc.)
2. What states/regions should they target? (specific, not generic)
3. What price range is optimal for their borrowing capacity?
4. What strategy should they use? (BTL, BRRR, HMO, subdivision, etc.)
5. What yield/growth balance should they target?
6. What are their 3 biggest risks and how to mitigate them?
7. What should their next 3 concrete actions be?

AUSTRALIAN MARKET CONTEXT (2026):
- National median dwelling: $980,343
- Sydney houses: $1,587,709 | Brisbane: $1,131,329 | Perth: $983,068 | Melbourne: $1,050,000
- Perth & Brisbane leading growth (8-10% forecast 2026)
- Rental vacancy: 1.2-1.6% nationally (extremely tight)
- Interest rates: RBA cash rate 4.10% (Feb 2026 cut from 4.35%)
- Investor lending: Highest share of new loans since 2017
- APRA serviceability buffer: 3% above loan rate

STRATEGY GUIDE:
- Buy & Hold (BTL): Best for long-term wealth, negative gearing benefits
- BRRR: Buy below market → Renovate → Rent → Refinance → Repeat (forced equity)
- HMO/Co-living: Higher yield per property, more management intensive
- Subdivision: Development profit, requires capital and experience
- Off-the-plan: Lower entry, depreciation benefits, settlement risk
- Commercial: Higher yields, longer leases, different risk profile

EXPERIENCE LEVELS:
- Beginner (0 props): Focus on simplicity, single strategy, strong cash flow
- Novice (1-2 props): Introduce equity leverage, refine strategy
- Intermediate (3-5 props): Portfolio optimisation, entity structures
- Advanced (6-10 props): Development, commercial, creative finance
- Expert (10+): Portfolio exits, syndication, wealth transition

TONE: Warm, expert, direct. Ask one question at a time. Build rapport.
Always acknowledge their situation before asking the next question.
When you have enough information, produce the investment thesis in JSON format."""


THESIS_EXTRACTION_PROMPT = """Based on this investor profile, produce a comprehensive investment thesis as JSON.

INVESTOR PROFILE:
{profile_summary}

Produce a JSON object with this exact structure:
{{
    "investor_name": "string or null",
    "experience_level": "beginner|novice|intermediate|advanced|expert",
    "primary_goal": "capital_growth|cash_flow|balanced|retirement|fhb",
    "risk_tolerance": "conservative|moderate|aggressive",
    "budget": {{
        "max_purchase_price": number,
        "deposit_available": number,
        "monthly_surplus": number,
        "estimated_borrowing_power": number
    }},
    "strategy": {{
        "primary": "btl|brrr|hmo|subdivision|off_plan|commercial",
        "secondary": "btl|brrr|hmo|subdivision|off_plan|commercial|null",
        "rationale": "string"
    }},
    "target_markets": [
        {{
            "state": "NSW|VIC|QLD|SA|WA|TAS|NT|ACT",
            "regions": ["suburb or region name"],
            "rationale": "string"
        }}
    ],
    "property_criteria": {{
        "types": ["house|unit|townhouse|duplex|villa|land"],
        "min_bedrooms": number,
        "max_bedrooms": number,
        "min_yield_pct": number,
        "min_growth_forecast_pct": number,
        "max_strata_quarterly": number or null,
        "prefer_land": boolean,
        "value_add_required": boolean
    }},
    "financial_targets": {{
        "target_gross_yield_pct": number,
        "target_net_yield_pct": number,
        "max_monthly_shortfall": number,
        "target_5yr_growth_pct": number,
        "target_portfolio_value_5yr": number
    }},
    "key_risks": [
        {{"risk": "string", "mitigation": "string"}}
    ],
    "next_actions": [
        {{"action": "string", "timeline": "string", "priority": "high|medium|low"}}
    ],
    "thesis_summary": "2-3 sentence summary of the investment thesis",
    "search_filters": {{
        "states": ["NSW", "VIC"],
        "max_price": number,
        "min_price": number,
        "property_types": ["house", "unit"],
        "min_yield": number,
        "min_bedrooms": number
    }}
}}

Be specific. Use real Australian suburb names. Give concrete numbers."""


class InvestorProfilerAgent(BaseAgent):
    """
    Investor Profiler Agent — builds a personalised investment thesis.

    Conducts an intelligent onboarding interview and produces a concrete
    investment thesis that drives all subsequent agent behaviour.
    """

    def __init__(self):
        super().__init__("InvestorProfiler")

    async def execute(
        self,
        user_message: str,
        conversation_history: Optional[list[dict]] = None,
        profile_data: Optional[dict] = None,
        mode: str = "interview",  # interview | generate_thesis | update_thesis
    ) -> AgentResult:
        """
        Run the investor profiling process.

        Args:
            user_message: The user's latest message
            conversation_history: Previous messages in the conversation
            profile_data: Existing profile data (for updates)
            mode: interview (conversational), generate_thesis (produce thesis from data),
                  update_thesis (update existing thesis)
        """
        self.logger.info("profiler_started", mode=mode, msg_len=len(user_message))

        if mode == "generate_thesis":
            return await self._generate_thesis(profile_data or {})
        elif mode == "update_thesis":
            return await self._update_thesis(user_message, profile_data or {})
        else:
            return await self._conduct_interview(user_message, conversation_history or [])

    async def _conduct_interview(
        self,
        user_message: str,
        history: list[dict],
    ) -> AgentResult:
        """Conduct the onboarding interview conversationally."""
        # Build messages for the LLM
        messages_context = ""
        if history:
            for msg in history[-10:]:  # Last 10 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages_context += f"\n{role.upper()}: {content}"

        # Determine what stage of the interview we're at
        stage = self._determine_interview_stage(history)

        prompt = f"""CONVERSATION HISTORY:
{messages_context if messages_context else "This is the start of the conversation."}

USER'S LATEST MESSAGE: {user_message}

INTERVIEW STAGE: {stage}

{self._get_stage_instructions(stage)}

Respond naturally and conversationally. Ask ONE focused question.
If you have enough information to produce a thesis (all key areas covered),
end your response with: [READY_FOR_THESIS]"""

        response, tokens = await self.ask_llm(
            prompt=prompt,
            system=PROFILER_SYSTEM_PROMPT,
            max_tokens=1024,
            temperature=0.5,
        )

        # Check if ready to generate thesis
        ready_for_thesis = "[READY_FOR_THESIS]" in response
        clean_response = response.replace("[READY_FOR_THESIS]", "").strip()

        # Extract any profile data mentioned in the conversation
        extracted_data = self._extract_profile_data(history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": clean_response},
        ])

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "response": clean_response,
                "stage": stage,
                "ready_for_thesis": ready_for_thesis,
                "extracted_profile": extracted_data,
                "next_step": "generate_thesis" if ready_for_thesis else "continue_interview",
            },
            tokens_used=tokens,
        )

    async def _generate_thesis(self, profile_data: dict) -> AgentResult:
        """Generate a full investment thesis from collected profile data."""
        profile_summary = json.dumps(profile_data, indent=2)

        prompt = THESIS_EXTRACTION_PROMPT.format(profile_summary=profile_summary)

        thesis = await self.ask_llm_json(
            prompt=prompt,
            system=PROFILER_SYSTEM_PROMPT,
            max_tokens=3000,
            temperature=0.2,
        )

        if "error" in thesis:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Failed to generate thesis: {thesis.get('error')}",
            )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "thesis": thesis,
                "thesis_summary": thesis.get("thesis_summary", ""),
                "search_filters": thesis.get("search_filters", {}),
                "next_actions": thesis.get("next_actions", []),
            },
        )

    async def _update_thesis(self, user_message: str, existing_thesis: dict) -> AgentResult:
        """Update an existing thesis based on new user input."""
        prompt = f"""The investor wants to update their investment thesis.

EXISTING THESIS:
{json.dumps(existing_thesis, indent=2)}

INVESTOR'S UPDATE REQUEST: {user_message}

Update the thesis based on their request and return the complete updated thesis JSON.
Keep all unchanged fields the same. Only modify what they've asked to change.
Return the full thesis JSON."""

        updated_thesis = await self.ask_llm_json(
            prompt=prompt,
            system=PROFILER_SYSTEM_PROMPT,
            max_tokens=3000,
            temperature=0.2,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "thesis": updated_thesis,
                "updated": True,
            },
        )

    def _determine_interview_stage(self, history: list[dict]) -> str:
        """Determine what stage of the interview we're at."""
        if not history:
            return "greeting"

        # Count user messages to gauge progress
        user_messages = [m for m in history if m.get("role") == "user"]
        count = len(user_messages)

        if count == 0:
            return "greeting"
        elif count <= 2:
            return "goals_and_experience"
        elif count <= 4:
            return "finances"
        elif count <= 6:
            return "strategy_preferences"
        elif count <= 8:
            return "location_preferences"
        else:
            return "finalising"

    def _get_stage_instructions(self, stage: str) -> str:
        """Get instructions for the current interview stage."""
        instructions = {
            "greeting": """Welcome them warmly. Introduce yourself as their NexusProp Investment Strategist.
Ask about their primary goal: Are they looking for capital growth, rental income, or both?
Keep it friendly and brief.""",

            "goals_and_experience": """You need to understand:
- How many investment properties do they currently own?
- What's their main goal? (financial freedom, retirement, passive income, wealth building)
- What's their timeline? (when do they want to achieve this goal?)
Ask about ONE of these if not yet answered.""",

            "finances": """You need to understand their financial position:
- What's their maximum budget for the next purchase?
- How much deposit/equity do they have available?
- Are they currently employed? (PAYG or self-employed)
- What's their approximate annual income?
Ask about ONE of these if not yet answered.""",

            "strategy_preferences": """You need to understand their strategy preferences:
- Do they prefer capital growth or rental yield?
- Are they comfortable with renovation/value-add projects?
- Do they want positively or negatively geared properties?
- What's their risk tolerance? (conservative, moderate, aggressive)
Ask about ONE of these if not yet answered.""",

            "location_preferences": """You need to understand their location preferences:
- Do they have preferred states or cities?
- Are they open to interstate investing?
- Do they prefer metropolitan, regional, or coastal markets?
- Any areas they want to avoid?
Ask about ONE of these if not yet answered.""",

            "finalising": """You have enough information to produce a thesis.
Summarise what you've learned about them and confirm the key points.
Then indicate you're ready to generate their personalised investment thesis.
End with [READY_FOR_THESIS]""",
        }
        return instructions.get(stage, "Continue the interview naturally.")

    def _extract_profile_data(self, history: list[dict]) -> dict:
        """Extract key profile data points from conversation history."""
        # Simple extraction — in production this would use NLP
        full_text = " ".join([m.get("content", "") for m in history]).lower()
        data = {}

        # Experience level
        if "0 properties" in full_text or "first property" in full_text or "no properties" in full_text:
            data["experience_level"] = "beginner"
        elif "1 property" in full_text or "one property" in full_text:
            data["experience_level"] = "novice"
        elif any(f"{n} properties" in full_text for n in ["2", "3", "4", "5", "two", "three", "four", "five"]):
            data["experience_level"] = "intermediate"

        # Goals
        if any(k in full_text for k in ["capital growth", "grow", "appreciation"]):
            data["primary_goal"] = "capital_growth"
        elif any(k in full_text for k in ["cash flow", "rental income", "passive income", "yield"]):
            data["primary_goal"] = "cash_flow"

        # Risk
        if any(k in full_text for k in ["conservative", "safe", "low risk"]):
            data["risk_tolerance"] = "conservative"
        elif any(k in full_text for k in ["aggressive", "high risk", "maximum"]):
            data["risk_tolerance"] = "aggressive"
        else:
            data["risk_tolerance"] = "moderate"

        return data
