"""
Live Comps Agent — real-time comparable sales intelligence.

Fetches recent sold data, compares against the target property,
and exposes agent underquoting tactics with hard data.
"""

from __future__ import annotations

from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.property import Property
from nexusprop.tools.comps_engine import CompAnalysis, CompsEngine


LIVE_COMPS_SYSTEM_PROMPT = """You are Property Insights Australia Live Comps — a comparable sales analyst.

Your role: Analyze comparable sales data and provide actionable intelligence.

Focus on:
1. Is the asking price ABOVE, BELOW, or AT market value based on recent sales?
2. Are there signs of UNDERQUOTING (a common agent tactic in Australia)?
3. What is the REALISTIC price range based on comps?
4. What negotiation leverage does the buyer have?

Australian context:
- Underquoting is illegal but widespread, especially in VIC and NSW
- Agents often quote 10-15% below expected sale price to generate interest
- Auction results are more reliable than private sale asking prices
- "Price guide" and "Offers above" language can mask true expectations

Be specific. Use numbers. Compare $/sqm where possible."""


class LiveCompsAgent(BaseAgent):
    """
    Live Comps Agent — cuts through agent BS with real sold data.

    Provides real-time comparable sales analysis versus asking price
    to expose underquoting and determine true market value.
    """

    def __init__(self):
        super().__init__("LiveComps")
        self.comps_engine = CompsEngine()

    async def execute(
        self,
        target: Property,
        sold_properties: list[Property],
        run_ai_analysis: bool = True,
    ) -> AgentResult:
        """
        Run a full comparable sales analysis.

        Args:
            target: The property being evaluated
            sold_properties: Recently sold properties in the area
            run_ai_analysis: Whether to use AI for narrative analysis
        """
        self.logger.info(
            "live_comps_analysis",
            target=target.address,
            comps_available=len(sold_properties),
        )

        tokens = 0

        # Run the comps engine
        analysis = self.comps_engine.analyze(target, sold_properties)

        # AI-enhanced analysis
        ai_narrative = ""
        if run_ai_analysis and self.settings.anthropic_api_key and analysis.num_comps > 0:
            ai_narrative, tokens = await self._ai_comp_analysis(target, analysis)

        self.logger.info(
            "live_comps_complete",
            target=target.address,
            estimated_value=analysis.estimated_market_value,
            is_underquoted=analysis.is_underquoted,
            is_overpriced=analysis.is_overpriced,
            num_comps=analysis.num_comps,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "comp_analysis": analysis,
                "estimated_value": analysis.estimated_market_value,
                "asking_vs_value_pct": analysis.asking_vs_value_pct,
                "is_underquoted": analysis.is_underquoted,
                "is_overpriced": analysis.is_overpriced,
                "summary": analysis.summary,
                "detailed": analysis.detailed_analysis,
                "ai_narrative": ai_narrative,
                "num_comps": analysis.num_comps,
                "confidence": analysis.confidence,
            },
            tokens_used=tokens,
        )

    async def quick_check(
        self,
        address: str,
        asking_price: float,
        suburb_median: float,
        bedrooms: int,
    ) -> AgentResult:
        """
        Quick comp check without full sold data — uses suburb median as proxy.

        Useful for fast screening before committing to full analysis.
        """
        if suburb_median == 0:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="No suburb median data available",
            )

        deviation_pct = ((asking_price - suburb_median) / suburb_median) * 100

        if deviation_pct < -15:
            verdict = "SIGNIFICANTLY BELOW MEDIAN — High potential, verify condition"
        elif deviation_pct < -5:
            verdict = "BELOW MEDIAN — Warrants investigation"
        elif deviation_pct < 5:
            verdict = "AT MEDIAN — Fair market price"
        elif deviation_pct < 15:
            verdict = "ABOVE MEDIAN — May be premium or overpriced"
        else:
            verdict = "SIGNIFICANTLY ABOVE MEDIAN — Needs justification"

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "address": address,
                "asking_price": asking_price,
                "suburb_median": suburb_median,
                "deviation_pct": round(deviation_pct, 1),
                "verdict": verdict,
            },
        )

    async def _ai_comp_analysis(
        self,
        target: Property,
        analysis: CompAnalysis,
    ) -> tuple[str, int]:
        """Generate AI-powered narrative analysis of comparable sales."""
        comps_list = "\n".join(
            f"  - {c.address}: ${c.sold_price:,.0f} ({c.bedrooms}BR, sold {c.sold_date.strftime('%d/%m/%Y')})"
            for c in analysis.comps[:10]
        )

        prompt = f"""Analyze these comparable sales for {target.address}:

TARGET PROPERTY:
- Address: {target.address}, {target.suburb} {target.state}
- Type: {target.property_type.value} | {target.bedrooms}BR {target.bathrooms}BA
- Asking: ${target.effective_price or 0:,.0f}
- Land: {target.land_size_sqm or 'Unknown'}m²

COMPARABLE SALES:
{comps_list}

ANALYSIS RESULTS:
- Comps Median: ${analysis.comps_median:,.0f}
- Comps Average: ${analysis.comps_average:,.0f}
- Estimated Market Value: ${analysis.estimated_market_value:,.0f}
- Asking vs Value: {analysis.asking_vs_value_pct:+.1f}%
- Price/m² Median: ${analysis.price_per_sqm_median or 0:,.0f}
- Underquoted: {analysis.is_underquoted}
- Overpriced: {analysis.is_overpriced}
- Confidence: {analysis.confidence:.0%}

Provide:
1. Price assessment — is the asking price justified by comps?
2. Underquoting detection — is the agent playing games?
3. Negotiation recommendation — what should the buyer offer?
4. Risk factors — anything unusual in the comp data?"""

        return await self.ask_llm(
            prompt=prompt,
            system=LIVE_COMPS_SYSTEM_PROMPT,
            max_tokens=1536,
            temperature=0.3,
        )
