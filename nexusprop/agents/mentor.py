"""
Mentor Agent — education, coaching, and portfolio intelligence.

Provides market commentary, strategy education, portfolio reviews,
suburb deep-dives, and investment coaching tailored to the investor's
experience level and goals.

This is the "LEARN & GROW" agent — after the deal pipeline runs,
the Mentor ensures the investor understands WHY and WHAT to do next.
"""

from __future__ import annotations

import json
from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.deal import Deal
from nexusprop.models.investment import (
    ExperienceLevel,
    InvestmentProfile,
    Portfolio,
)


MENTOR_SYSTEM_PROMPT = """You are the Property Insights Australia Mentor — a world-class Australian property investment educator and portfolio strategist.

Your role: Educate, coach, and provide strategic portfolio guidance tailored to the investor's experience level and goals.

EXPERIENCE-BASED COACHING:

BEGINNER (0 properties):
- Explain everything — assume no prior knowledge
- Use analogies and examples
- Focus on fundamentals: yield, LVR, cash flow, capital growth
- Warn about common beginner mistakes
- Encourage them to build their team (broker, accountant, solicitor)

NOVICE (1-2 properties):
- They know basics — focus on strategy refinement
- Help them understand their first property's performance
- Introduce more advanced concepts: negative gearing, depreciation, equity release
- Guide on portfolio diversification

INTERMEDIATE (3-5 properties):
- Strategy-focused coaching
- Portfolio optimization: rebalancing, equity recycling
- Entity structure optimization
- Tax planning deep-dives
- Risk management across the portfolio

ADVANCED (6-10 properties):
- High-level strategic discussion
- Development opportunities
- Multi-entity management
- Succession planning
- Market cycle positioning
- Joint ventures and syndication

EXPERT (10+):
- Peer-level discussion
- Commercial opportunities
- Portfolio exits and restructuring 
- Wealth transition planning
- Market macro analysis

COACHING TOPICS:

1. MARKET COMMENTARY
   - Current cycle position (boom, correction, recovery, growth)
   - Interest rate outlook and impact
   - Supply/demand dynamics by state/region
   - Regulatory changes (APRA, lending, tax)
   - Where the smart money is moving

2. STRATEGY EDUCATION
   - Buy & Hold: Long-term wealth building
   - BRRR: Forced equity creation
   - HMO: Maximizing yield per room
   - R2SA: Serviced accommodation cash flow
   - Subdivision: Development profits
   - Creative finance: Vendor finance, options, JVs

3. PORTFOLIO REVIEW
   - Current portfolio health check
   - Diversification analysis
   - Equity position and recycling opportunities
   - Cash flow optimization
   - Risk concentration assessment
   - Next property strategy recommendation

4. SUBURB DEEP-DIVES
   - Demographics and growth drivers
   - Infrastructure projects
   - Supply pipeline
   - Rental demand indicators
   - Historical performance
   - Investment thesis for/against

TONE:
- Encouraging but honest — no sugarcoating
- Data-driven with Australian market context
- Appropriate complexity for their level
- Proactive — suggest things they haven't asked about
- Always actionable — every insight has a "so what"

CRITICAL:
- This is education, NOT financial advice
- Always recommend professional advice for complex decisions
- Use current Australian market data and rates
- Reference real suburbs, real infrastructure projects, real trends"""


class MentorAgent(BaseAgent):
    """
    Mentor Agent — education, coaching, and portfolio intelligence.

    Provides tailored coaching based on the investor's experience level:
    - Market commentary and cycle analysis
    - Strategy education (BRRR, HMO, R2SA, subdivision)
    - Portfolio health checks and optimization
    - Suburb deep-dives with investment thesis
    - Next-step recommendations
    """

    def __init__(self):
        super().__init__("Mentor")

    async def execute(
        self,
        topic: str = "general",
        user_input: Optional[str] = None,
        profile: Optional[InvestmentProfile] = None,
        portfolio: Optional[Portfolio] = None,
        deals: Optional[list[Deal]] = None,
        context: Optional[dict] = None,
    ) -> AgentResult:
        """
        Provide coaching on a requested topic.

        Args:
            topic: market_commentary, strategy_education, portfolio_review,
                   suburb_deepdive, deal_review, general
            user_input: Specific question or context from the user
            profile: Investor profile for personalization
            portfolio: Current portfolio for review
            deals: Recent deals for context
            context: Additional context dict
        """
        self.logger.info(
            "mentor_started",
            topic=topic,
            has_profile=profile is not None,
            has_portfolio=portfolio is not None,
        )

        profile = profile or InvestmentProfile()

        # Route to appropriate handler
        handlers = {
            "market_commentary": self._market_commentary,
            "strategy_education": self._strategy_education,
            "portfolio_review": self._portfolio_review,
            "suburb_deepdive": self._suburb_deepdive,
            "deal_review": self._deal_review,
            "next_steps": self._next_steps,
        }

        handler = handlers.get(topic, self._general_coaching)
        prompt = handler(
            user_input=user_input or "",
            profile=profile,
            portfolio=portfolio,
            deals=deals,
            context=context or {},
        )

        response, tokens = await self.ask_llm(
            prompt=prompt,
            system=MENTOR_SYSTEM_PROMPT,
            max_tokens=3072,
            temperature=0.4,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "coaching": response,
                "topic": topic,
                "experience_level": profile.experience_level.value,
                "coaching_type": self._determine_coaching_type(profile),
            },
            tokens_used=tokens,
        )

    def _market_commentary(self, user_input: str, profile: InvestmentProfile,
                           portfolio: Optional[Portfolio], deals: Optional[list[Deal]],
                           context: dict) -> str:
        """Generate market commentary prompt."""
        return f"""Provide current Australian property market commentary for a {profile.experience_level.value}-level investor.

INVESTOR CONTEXT:
- Goal: {profile.primary_goal.value}
- Risk Tolerance: {profile.risk_tolerance.value}
- Portfolio: {profile.current_portfolio_count} properties
- Preferred States: {', '.join(context.get('preferred_states', ['NSW', 'VIC', 'QLD'])) if context else 'NSW, VIC, QLD'}

{f'SPECIFIC QUESTION: {user_input}' if user_input else ''}

Cover:
1. Current market cycle position (national + state-level)
2. Interest rate outlook and what it means for investors
3. Top 3 opportunities in the current market
4. Top 3 risks to watch
5. Specific recommendation for THIS investor given their profile

Remember to match complexity to their {profile.experience_level.value} experience level.
Use February 2026 Australian market context."""

    def _strategy_education(self, user_input: str, profile: InvestmentProfile,
                            portfolio: Optional[Portfolio], deals: Optional[list[Deal]],
                            context: dict) -> str:
        """Generate strategy education prompt."""
        strategy = context.get("strategy", user_input or "BRRR")
        return f"""Teach this {profile.experience_level.value}-level investor about the {strategy} strategy in the Australian market.

INVESTOR CONTEXT:
- Experience: {profile.experience_level.value}
- Goal: {profile.primary_goal.value}
- Budget: ${profile.max_next_purchase:,.0f}
- Risk: {profile.risk_tolerance.value}

{f'SPECIFIC QUESTION: {user_input}' if user_input else ''}

Cover:
1. What is the {strategy} strategy? (complexity appropriate to their level)
2. How it works step-by-step in Australia
3. Typical numbers / worked example with Australian property
4. Key risks and how to mitigate them
5. Who this strategy is best suited for
6. Requirements (capital, experience, team)
7. Common mistakes to avoid
8. How to get started with their budget

Use real Australian examples. Be specific about numbers, rates, and costs.
If they're a beginner, use simple language. If advanced, dive deep into mechanics."""

    def _portfolio_review(self, user_input: str, profile: InvestmentProfile,
                          portfolio: Optional[Portfolio], deals: Optional[list[Deal]],
                          context: dict) -> str:
        """Generate portfolio review prompt."""
        portfolio_summary = ""
        if portfolio and portfolio.properties:
            portfolio_summary = f"""
CURRENT PORTFOLIO:
- Total Value: ${portfolio.total_value:,.0f}
- Total Debt: ${portfolio.total_debt:,.0f}
- Total Equity: ${portfolio.total_equity:,.0f}
- Portfolio LVR: {portfolio.portfolio_lvr_pct}%
- Weekly Rent: ${portfolio.total_weekly_rent:,.0f}
- Annual Income: ${portfolio.total_annual_income:,.0f}
- Avg Gross Yield: {portfolio.avg_gross_yield_pct}%
- Properties: {portfolio.property_count}

INDIVIDUAL PROPERTIES:"""
            for i, p in enumerate(portfolio.properties, 1):
                portfolio_summary += f"""
  {i}. {p.address}, {p.suburb} {p.state}
     - Type: {p.property_type} | Entity: {p.entity.value}
     - Value: ${p.current_value:,.0f} | Debt: ${p.outstanding_loan:,.0f}
     - LVR: {p.lvr_pct}% | Equity: ${p.equity:,.0f}
     - Rent: ${p.weekly_rent:,.0f}/wk | Yield: {p.gross_yield_pct}%"""

        return f"""Conduct a comprehensive portfolio review for this {profile.experience_level.value}-level investor.

INVESTOR PROFILE:
- Goal: {profile.primary_goal.value}
- Risk: {profile.risk_tolerance.value}
- Target: {profile.target_portfolio_count} properties, ${profile.target_annual_passive_income:,.0f}/yr passive income
- Borrowing Power: ${profile.financial.estimated_borrowing_power:,.0f}
- Deployable Capital: ${profile.financial.total_deployable_capital:,.0f}

{portfolio_summary if portfolio_summary else 'No portfolio data provided — provide general guidance on building a portfolio.'}

{f'SPECIFIC QUESTION: {user_input}' if user_input else ''}

Provide:
1. PORTFOLIO HEALTH SCORE (1-10) with explanation
2. DIVERSIFICATION ANALYSIS (geographic, asset class, entity)
3. EQUITY RECYCLING OPPORTUNITIES (if any)
4. CASH FLOW OPTIMIZATION (where to improve)
5. RISK ASSESSMENT (concentration, LVR, market exposure)
6. NEXT PROPERTY RECOMMENDATION (strategy, location, price range, entity)
7. 3-YEAR ROADMAP to reach their target

Be specific. Use numbers. Reference real Australian markets."""

    def _suburb_deepdive(self, user_input: str, profile: InvestmentProfile,
                         portfolio: Optional[Portfolio], deals: Optional[list[Deal]],
                         context: dict) -> str:
        """Generate suburb deep-dive prompt."""
        suburb = context.get("suburb", user_input or "unknown suburb")
        state = context.get("state", "NSW")
        return f"""Provide a comprehensive investment deep-dive for {suburb}, {state} — tailored for a {profile.experience_level.value}-level investor.

INVESTOR CONTEXT:
- Goal: {profile.primary_goal.value}
- Budget: ${profile.max_next_purchase:,.0f}
- Strategy: {profile.preferred_strategies[0].value if profile.preferred_strategies else 'standard_io'}

Cover:
1. SUBURB SNAPSHOT
   - Demographics, population growth, median age
   - Median house/unit prices and recent trends
   - Rental yields (gross)
   - Vacancy rates
   - Days on market

2. GROWTH DRIVERS
   - Infrastructure projects (rail, road, hospitals, schools)
   - Employment hubs and commute times
   - Population migration patterns
   - Council development plans

3. SUPPLY ANALYSIS
   - Current development pipeline
   - DA approvals
   - Land availability
   - Oversupply risk assessment

4. INVESTMENT THESIS
   - Bull case (why to buy here)
   - Bear case (why to avoid)
   - Best property type for this suburb
   - Best streets / pockets
   - Entry price range for the strategy

5. COMPARABLE SUBURBS
   - Similar suburbs that are cheaper (arbitrage opportunities)
   - Suburbs that were like this 5 years ago and have since grown

6. VERDICT: BUY / WATCH / AVOID with confidence level

Use current Australian data. Be specific about projects and trends."""

    def _deal_review(self, user_input: str, profile: InvestmentProfile,
                     portfolio: Optional[Portfolio], deals: Optional[list[Deal]],
                     context: dict) -> str:
        """Generate deal review coaching prompt."""
        deal_context = ""
        if deals:
            for d in deals[:3]:
                deal_context += f"""
DEAL: {d.property.address}, {d.property.suburb} {d.property.state}
- Price: ${d.property.effective_price or 0:,.0f}
- Type: {d.property.property_type.value} | {d.property.bedrooms or '?'}BR
- Bargain Score: {d.bargain_score.overall_score}/100
- Gross Yield: {d.cash_flow.gross_rental_yield}%
- Net Yield: {d.cash_flow.net_yield}%
- Monthly Cashflow: ${d.cash_flow.monthly_cash_flow:,.0f}
- Golden: {'YES' if d.is_golden_opportunity else 'No'}
- Distress: {', '.join(s.keyword for s in d.property.distress_signals) or 'None'}
"""

        return f"""Review these deals for a {profile.experience_level.value}-level investor and provide coaching.

INVESTOR: {profile.primary_goal.value} strategy, {profile.risk_tolerance.value} risk, ${profile.max_next_purchase:,.0f} budget

{deal_context if deal_context else 'No specific deals — provide general deal evaluation coaching.'}

{f'QUESTION: {user_input}' if user_input else ''}

For each deal:
1. VERDICT: Strong Buy / Buy / Hold / Pass / Strong Pass
2. WHY — the key numbers that drive the verdict
3. WATCH OUT — specific risks for THIS deal
4. IF BUYING — the next 3 steps to take
5. TEACHING MOMENT — what this deal teaches about investing

Adapt the depth to their {profile.experience_level.value} level."""

    def _next_steps(self, user_input: str, profile: InvestmentProfile,
                    portfolio: Optional[Portfolio], deals: Optional[list[Deal]],
                    context: dict) -> str:
        """Generate personalized next steps."""
        return f"""Based on this investor's profile, what should they do THIS WEEK and THIS MONTH?

PROFILE:
- Experience: {profile.experience_level.value}
- Goal: {profile.primary_goal.value}
- Risk: {profile.risk_tolerance.value}
- Borrowing Power: ${profile.financial.estimated_borrowing_power:,.0f}
- Cash Available: ${profile.financial.cash_available:,.0f}
- Portfolio: {profile.current_portfolio_count} properties
- Target: {profile.target_portfolio_count} properties, ${profile.target_annual_passive_income:,.0f}/yr
- Has Accountant: {profile.has_accountant} | Broker: {profile.has_mortgage_broker} | Solicitor: {profile.has_solicitor}
- Readiness Score: {profile.investor_readiness_score}/100
- Completeness: {profile.profile_completeness_pct}%

{f'QUESTION: {user_input}' if user_input else ''}

Provide:
1. THIS WEEK (3 specific actions)
2. THIS MONTH (3 specific actions)
3. 90-DAY PLAN (milestone targets)
4. BIGGEST RISK right now and how to mitigate it
5. BIGGEST OPPORTUNITY right now and how to capture it

Be extremely specific. Not "research the market" but "search for 3BR houses in [specific suburb] under $[amount]."
Adjust for their experience — beginners need team-building, experts need deal-specific actions."""

    def _general_coaching(self, user_input: str, profile: InvestmentProfile,
                          portfolio: Optional[Portfolio], deals: Optional[list[Deal]],
                          context: dict) -> str:
        """General coaching for unstructured questions."""
        return f"""An investor with {profile.experience_level.value} experience has a question.

PROFILE:
- Goal: {profile.primary_goal.value}
- Risk: {profile.risk_tolerance.value}
- Budget: ${profile.max_next_purchase:,.0f}
- Portfolio: {profile.current_portfolio_count} properties

QUESTION: {user_input or 'Give me your best investing advice for the current Australian market.'}

Provide a thorough, practical answer. Match complexity to their level.
Always use Australian market context. Be actionable."""

    def _determine_coaching_type(self, profile: InvestmentProfile) -> str:
        """Determine what type of coaching this investor needs most."""
        if profile.experience_level == ExperienceLevel.BEGINNER:
            return "foundational"
        elif profile.experience_level == ExperienceLevel.NOVICE:
            return "strategy_building"
        elif profile.experience_level == ExperienceLevel.INTERMEDIATE:
            return "optimization"
        elif profile.experience_level == ExperienceLevel.ADVANCED:
            return "advanced_strategy"
        return "peer_discussion"

    async def generate_weekly_brief(
        self,
        profile: InvestmentProfile,
        portfolio: Optional[Portfolio] = None,
        recent_deals: Optional[list[Deal]] = None,
        market_data: Optional[dict] = None,
    ) -> AgentResult:
        """Generate a personalized weekly market brief."""
        prompt = f"""Generate a personalized weekly property investment brief for February 2026.

INVESTOR:
- Experience: {profile.experience_level.value}
- Goal: {profile.primary_goal.value}
- Risk: {profile.risk_tolerance.value}
- Portfolio: {profile.current_portfolio_count} properties worth ${profile.current_portfolio_value:,.0f}
- Target: ${profile.target_annual_passive_income:,.0f}/yr passive income

{f'PORTFOLIO LVR: {portfolio.portfolio_lvr_pct}%' if portfolio else ''}
{f'RECENT DEALS FOUND: {len(recent_deals)}' if recent_deals else ''}

Generate a brief that includes:
1. MARKET PULSE — 3 key things that happened this week in Australian property
2. YOUR PORTFOLIO — brief health check status
3. OPPORTUNITIES — top areas/strategies for your profile right now
4. WATCH LIST — emerging trends to monitor
5. TIP OF THE WEEK — one actionable educational nugget

Keep it concise — this is a weekly email brief, not an essay. Use bullet points.
Personalize to their {profile.experience_level.value} level."""

        response, tokens = await self.ask_llm(
            prompt=prompt,
            system=MENTOR_SYSTEM_PROMPT,
            max_tokens=2048,
            temperature=0.5,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "brief": response,
                "type": "weekly_brief",
                "experience_level": profile.experience_level.value,
            },
            tokens_used=tokens,
        )
