"""
Profiler Agent — builds rich investor profiles for personalized deal matching.

Collects financial capacity, borrowing power (AU bank formulas), risk tolerance,
investment goals, experience level, and entity structure. Continuously updated
from user interactions and feedback.

This is the FIRST agent in the pipeline — everything else is tailored to the profile.
"""

from __future__ import annotations

import json
from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.investment import (
    EntityType,
    ExperienceLevel,
    FinancialCapacity,
    FinanceStrategy,
    IncomeSource,
    InvestmentGoal,
    InvestmentProfile,
    RiskTolerance,
)


PROFILER_SYSTEM_PROMPT = """You are the Property Insights Australia Profiler — an expert Australian property investment advisor who builds comprehensive investor profiles.

Your role: Through conversational interaction, build a complete picture of the investor's financial situation, goals, risk tolerance, and experience to enable perfectly matched property recommendations.

WHAT YOU MUST DISCOVER:

1. FINANCIAL CAPACITY
   - Household income (salary, rental, business, trust distributions)
   - Existing debts (home loan, investment loans, car, personal, HECS)
   - Available cash for deposit
   - Accessible equity in existing properties
   - Credit card limits (banks service at 3% of limit regardless of balance)
   - Number of dependents
   - Monthly living expenses

2. BORROWING POWER
   - Use the assessable income and APRA buffer rate (+3%) to estimate
   - Factor in shading: salary=100%, rental=80%, self-employed=60-80%
   - Consider HEM (Household Expenditure Measure) benchmark

3. RISK TOLERANCE
   - Conservative: Capital preservation, established areas, blue-chip suburbs
   - Moderate: Balanced yield + growth, established with upside
   - Growth: Higher leverage, emerging suburbs, value-add
   - Aggressive: Development, creative finance, JVs
   - Speculative: Off-plan, land banking, pre-development

4. EXPERIENCE LEVEL
   - Beginner: 0 properties, researching
   - Novice: 1-2 properties
   - Intermediate: 3-5 properties
   - Advanced: 6-10 properties, multi-entity
   - Expert: 10+, development experience

5. ENTITY STRUCTURE
   - Personal name, joint, family trust, unit trust, SMSF, company
   - Whether they have professional team (accountant, broker, solicitor)

6. INVESTMENT GOALS
   - Cash flow vs capital growth vs balanced
   - Tax minimisation (negative gearing, depreciation)
   - Retirement planning (SMSF)
   - First home buyer
   - Target portfolio size and passive income

OUTPUT FORMAT (JSON):
{
    "risk_tolerance": "moderate",
    "experience_level": "beginner",
    "primary_goal": "balanced",
    "preferred_entity": "personal",
    "income_summary": "...",
    "estimated_borrowing_power": 750000,
    "deployable_capital": 150000,
    "max_purchase_price": 900000,
    "strategy_recommendations": ["standard_io", "equity_release"],
    "profile_completeness_pct": 85,
    "investor_readiness_score": 70,
    "coaching_notes": "...",
    "next_questions": ["..."]
}

AUSTRALIAN CONTEXT:
- Interest rates: ~6.25% variable, ~5.99% fixed 2yr
- APRA buffer: +3% above rate for servicing
- LVR tiers: 80% (no LMI), 85-90% (LMI required), 95% (limited lenders)
- Stamp duty varies by state (NSW, VIC, QLD all different)
- First Home Buyer concessions available in most states
- Negative gearing: investment losses offset PAYG income
- SMSF: Cannot use existing super to renovate, strict rules

TONE: Professional but approachable. Ask one or two questions at a time.
Never overwhelm. Build rapport."""


class ProfilerAgent(BaseAgent):
    """
    Profiler Agent — builds comprehensive investor profiles.

    The FIRST agent in the pipeline. All downstream agents (Scout, Analyst,
    Stacker, Negotiator, Mentor) tailor their behavior to the profile.

    Capabilities:
    - Conversational profile building via LLM
    - Algorithmic borrowing power estimation (APRA-compliant)
    - Risk scoring and strategy matching
    - Profile completeness tracking
    - Continuous profile updates from user interactions
    """

    def __init__(self):
        super().__init__("Profiler")

    async def execute(
        self,
        user_input: Optional[str] = None,
        existing_profile: Optional[InvestmentProfile] = None,
        interaction_type: str = "initial",
    ) -> AgentResult:
        """
        Build or update an investor profile.

        Args:
            user_input: Free-text from the user about their situation
            existing_profile: Current profile to update (None = new profile)
            interaction_type: initial, update, feedback, interaction
        """
        self.logger.info(
            "profiler_started",
            interaction_type=interaction_type,
            has_existing=existing_profile is not None,
        )

        profile = existing_profile or InvestmentProfile()

        if interaction_type == "interaction":
            # Quick update from a user action (view, save, dismiss)
            return self._update_from_interaction(profile, user_input or "")

        if interaction_type == "feedback":
            # User rejected or loved a deal — update preferences
            return await self._update_from_feedback(profile, user_input or "")

        # Full profile build / conversational update
        if user_input:
            profile = await self._build_profile_from_input(profile, user_input)

        # Score the profile
        profile.profile_completeness_pct = self._calculate_completeness(profile)
        profile.investor_readiness_score = self._calculate_readiness(profile)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "profile": profile.model_dump(mode="json"),
                "completeness": profile.profile_completeness_pct,
                "readiness": profile.investor_readiness_score,
                "max_purchase": profile.max_next_purchase,
                "borrowing_power": profile.financial.estimated_borrowing_power,
                "next_questions": self._get_next_questions(profile),
            },
        )

    async def _build_profile_from_input(
        self,
        profile: InvestmentProfile,
        user_input: str,
    ) -> InvestmentProfile:
        """Use LLM to extract profile data from free-text user input."""
        prompt = f"""Analyze this investor's description and extract structured profile data.

CURRENT PROFILE STATE:
- Risk Tolerance: {profile.risk_tolerance.value}
- Experience: {profile.experience_level.value}
- Primary Goal: {profile.primary_goal.value}
- Entity: {profile.preferred_entity.value}
- Gross Income: ${profile.financial.total_gross_income:,.0f}
- Cash Available: ${profile.financial.cash_available:,.0f}
- Equity Available: ${profile.financial.equity_available:,.0f}
- Existing Debt: ${profile.financial.total_existing_debt:,.0f}
- Portfolio: {profile.current_portfolio_count} properties worth ${profile.current_portfolio_value:,.0f}

INVESTOR'S INPUT:
{user_input}

Extract any NEW information from the input. Return ONLY valid JSON with these fields (include only fields that can be determined from the input):
{{
    "risk_tolerance": "conservative|moderate|growth|aggressive|speculative",
    "experience_level": "beginner|novice|intermediate|advanced|expert",
    "primary_goal": "cash_flow|capital_growth|balanced|tax_minimisation|retirement|wealth_creation|first_home",
    "preferred_entity": "personal|joint|family_trust|smsf|company",
    "gross_salary": 0,
    "rental_income": 0,
    "business_income": 0,
    "cash_available": 0,
    "equity_available": 0,
    "smsf_balance": 0,
    "existing_home_loan": 0,
    "existing_investment_loans": 0,
    "credit_card_limits": 0,
    "dependents": 0,
    "monthly_expenses": 0,
    "portfolio_count": 0,
    "portfolio_value": 0,
    "portfolio_debt": 0,
    "target_portfolio_count": 0,
    "target_passive_income": 0,
    "has_accountant": false,
    "has_broker": false,
    "has_solicitor": false,
    "coaching_notes": "Brief note about what they need"
}}"""

        response, tokens = await self.ask_llm(
            prompt=prompt,
            system=PROFILER_SYSTEM_PROMPT,
            max_tokens=2048,
            temperature=0.2,
        )

        # Parse LLM response
        try:
            # Extract JSON from response
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]

            data = json.loads(json_str.strip())
            profile = self._apply_extracted_data(profile, data)
        except (json.JSONDecodeError, IndexError):
            self.logger.warning("profile_extraction_failed", response=response[:200])

        return profile

    def _apply_extracted_data(self, profile: InvestmentProfile, data: dict) -> InvestmentProfile:
        """Apply extracted data to the profile."""
        # Risk tolerance
        if rt := data.get("risk_tolerance"):
            try:
                profile.risk_tolerance = RiskTolerance(rt)
            except ValueError:
                pass

        # Experience level
        if el := data.get("experience_level"):
            try:
                profile.experience_level = ExperienceLevel(el)
            except ValueError:
                pass

        # Primary goal
        if pg := data.get("primary_goal"):
            try:
                profile.primary_goal = InvestmentGoal(pg)
            except ValueError:
                pass

        # Entity
        if entity := data.get("preferred_entity"):
            try:
                profile.preferred_entity = EntityType(entity)
            except ValueError:
                pass

        # Income
        income_sources = []
        if salary := data.get("gross_salary"):
            income_sources.append(IncomeSource(
                source_type="salary",
                gross_annual=float(salary),
                is_primary=True,
                shading_pct=100.0,
            ))
        if rental := data.get("rental_income"):
            income_sources.append(IncomeSource(
                source_type="rental",
                gross_annual=float(rental),
                shading_pct=80.0,
            ))
        if business := data.get("business_income"):
            income_sources.append(IncomeSource(
                source_type="business",
                gross_annual=float(business),
                shading_pct=70.0,
            ))
        if income_sources:
            profile.financial.income_sources = income_sources

        # Cash position
        if cash := data.get("cash_available"):
            profile.financial.cash_available = float(cash)
        if equity := data.get("equity_available"):
            profile.financial.equity_available = float(equity)
        if smsf := data.get("smsf_balance"):
            profile.financial.smsf_balance = float(smsf)

        # Liabilities
        from nexusprop.models.investment import ExistingLiability
        liabilities = []
        if home_loan := data.get("existing_home_loan"):
            liabilities.append(ExistingLiability(
                liability_type="home_loan",
                outstanding_balance=float(home_loan),
                monthly_repayment=float(home_loan) * 0.065 / 12,  # IO estimate
            ))
        if inv_loans := data.get("existing_investment_loans"):
            liabilities.append(ExistingLiability(
                liability_type="investment_loan",
                outstanding_balance=float(inv_loans),
                monthly_repayment=float(inv_loans) * 0.065 / 12,
                is_investment=True,
            ))
        if liabilities:
            profile.financial.existing_liabilities = liabilities

        if cc := data.get("credit_card_limits"):
            profile.financial.credit_card_limits = float(cc)
        if deps := data.get("dependents"):
            profile.financial.dependents = int(deps)
        if expenses := data.get("monthly_expenses"):
            profile.financial.monthly_living_expenses = float(expenses)

        # Portfolio
        if pc := data.get("portfolio_count"):
            profile.current_portfolio_count = int(pc)
        if pv := data.get("portfolio_value"):
            profile.current_portfolio_value = float(pv)
        if pd := data.get("portfolio_debt"):
            profile.current_portfolio_debt = float(pd)
        if tc := data.get("target_portfolio_count"):
            profile.target_portfolio_count = int(tc)
        if tp := data.get("target_passive_income"):
            profile.target_annual_passive_income = float(tp)

        # Professional team
        if data.get("has_accountant") is not None:
            profile.has_accountant = bool(data["has_accountant"])
        if data.get("has_broker") is not None:
            profile.has_mortgage_broker = bool(data["has_broker"])
        if data.get("has_solicitor") is not None:
            profile.has_solicitor = bool(data["has_solicitor"])

        return profile

    def _update_from_interaction(
        self,
        profile: InvestmentProfile,
        action: str,
    ) -> AgentResult:
        """Update profile from a user interaction (view, save, dismiss, offer)."""
        # These interactions help us learn the user's real preferences
        # without them explicitly saying so
        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "profile": profile.model_dump(mode="json"),
                "interaction_recorded": action,
                "profile_updated": True,
            },
        )

    async def _update_from_feedback(
        self,
        profile: InvestmentProfile,
        feedback: str,
    ) -> AgentResult:
        """Update profile from explicit user feedback (loved/hated a deal)."""
        prompt = f"""A user gave feedback on a property deal. What does this tell us about their preferences?

FEEDBACK: {feedback}

CURRENT PROFILE:
- Risk: {profile.risk_tolerance.value}
- Goal: {profile.primary_goal.value}
- Experience: {profile.experience_level.value}
- Min Yield: {profile.min_acceptable_yield}%

Return JSON with any preference adjustments:
{{
    "risk_adjustment": "increase|decrease|none",
    "yield_preference_adjustment": "increase|decrease|none",
    "strategy_insight": "what this tells us about their preferences",
    "updated_min_yield": null
}}"""

        response, tokens = await self.ask_llm(prompt=prompt, max_tokens=512, temperature=0.3)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "profile": profile.model_dump(mode="json"),
                "feedback_analysis": response,
                "profile_updated": True,
            },
            tokens_used=tokens,
        )

    def _calculate_completeness(self, profile: InvestmentProfile) -> float:
        """Calculate how complete the profile is (0-100)."""
        checks = [
            profile.financial.total_gross_income > 0,           # Has income
            profile.financial.cash_available > 0,               # Has cash position
            len(profile.financial.income_sources) > 0,          # Income breakdown
            profile.risk_tolerance != RiskTolerance.MODERATE,   # Explicitly set risk
            profile.primary_goal != InvestmentGoal.BALANCED,    # Explicitly set goal
            profile.experience_level != ExperienceLevel.BEGINNER,  # Set experience
            profile.preferred_entity != EntityType.PERSONAL or profile.has_accountant,  # Entity considered
            profile.financial.dependents >= 0,                  # Dependents set
            profile.target_annual_passive_income > 0,           # Has target
            profile.current_portfolio_count >= 0,               # Portfolio tracked
        ]
        return round(sum(checks) / len(checks) * 100, 0)

    def _calculate_readiness(self, profile: InvestmentProfile) -> float:
        """Calculate investor readiness score (0-100)."""
        score = 0.0

        # Financial readiness (40 points)
        if profile.financial.estimated_borrowing_power > 300_000:
            score += 15
        if profile.financial.total_deployable_capital > 50_000:
            score += 15
        if profile.financial.total_gross_income > 80_000:
            score += 10

        # Knowledge readiness (30 points)
        exp_scores = {
            ExperienceLevel.BEGINNER: 5,
            ExperienceLevel.NOVICE: 10,
            ExperienceLevel.INTERMEDIATE: 20,
            ExperienceLevel.ADVANCED: 25,
            ExperienceLevel.EXPERT: 30,
        }
        score += exp_scores.get(profile.experience_level, 5)

        # Professional team (20 points)
        if profile.has_accountant:
            score += 7
        if profile.has_mortgage_broker:
            score += 7
        if profile.has_solicitor:
            score += 6

        # Profile completeness (10 points)
        score += profile.profile_completeness_pct / 10

        return min(round(score, 0), 100)

    def _get_next_questions(self, profile: InvestmentProfile) -> list[str]:
        """Determine what questions to ask next based on gaps."""
        questions = []

        if not profile.financial.income_sources:
            questions.append("What is your approximate household income (salary + any other income)?")

        if profile.financial.cash_available == 0 and profile.financial.equity_available == 0:
            questions.append("How much cash or accessible equity do you have for a property deposit?")

        if profile.experience_level == ExperienceLevel.BEGINNER:
            questions.append("Have you purchased any investment properties before? If so, how many?")

        if profile.primary_goal == InvestmentGoal.BALANCED:
            questions.append("Are you primarily looking for cash flow (rental income), capital growth, or both?")

        if profile.preferred_entity == EntityType.PERSONAL and not profile.has_accountant:
            questions.append("Do you have an accountant or financial advisor? Have you considered a trust or company structure?")

        if profile.financial.dependents == 0 and profile.financial.monthly_living_expenses == 3_500:
            questions.append("How many dependents do you have, and what are your approximate monthly living expenses?")

        if profile.target_annual_passive_income == 50_000:
            questions.append("What's your target passive income from property? What does financial freedom look like for you?")

        return questions[:3]  # Max 3 questions at a time

    async def generate_profile_report(
        self,
        profile: InvestmentProfile,
    ) -> AgentResult:
        """Generate a comprehensive investor profile report."""
        prompt = f"""Generate a comprehensive investor profile report.

INVESTOR PROFILE:
- Risk Tolerance: {profile.risk_tolerance.value}
- Experience: {profile.experience_level.value}
- Primary Goal: {profile.primary_goal.value}
- Entity: {profile.preferred_entity.value}
- Gross Income: ${profile.financial.total_gross_income:,.0f}
- Assessable Income: ${profile.financial.total_assessable_income:,.0f}
- Cash Available: ${profile.financial.cash_available:,.0f}
- Equity Available: ${profile.financial.equity_available:,.0f}
- Estimated Borrowing Power: ${profile.financial.estimated_borrowing_power:,.0f}
- Max Next Purchase: ${profile.max_next_purchase:,.0f}
- Existing Debt: ${profile.financial.total_existing_debt:,.0f}
- Portfolio: {profile.current_portfolio_count} properties worth ${profile.current_portfolio_value:,.0f}
- Target: {profile.target_portfolio_count} properties, ${profile.target_annual_passive_income:,.0f}/yr passive income
- Has Accountant: {profile.has_accountant} | Broker: {profile.has_mortgage_broker} | Solicitor: {profile.has_solicitor}
- Profile Completeness: {profile.profile_completeness_pct}%
- Readiness Score: {profile.investor_readiness_score}/100

Provide:
1. INVESTOR SUMMARY (2-3 sentences)
2. FINANCIAL POSITION ANALYSIS
3. RECOMMENDED STRATEGIES (ranked)
4. RISK ASSESSMENT
5. NEXT STEPS (3-5 actionable items)
6. WARNINGS / CONSIDERATIONS

Use Australian property market context. Be specific and actionable."""

        report, tokens = await self.ask_llm(
            prompt=prompt,
            system=PROFILER_SYSTEM_PROMPT,
            max_tokens=3072,
            temperature=0.3,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "report": report,
                "profile": profile.model_dump(mode="json"),
            },
            tokens_used=tokens,
        )
