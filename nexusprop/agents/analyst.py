"""
Agent B — The Analyst

The cognitive layer. Takes raw Property objects from the Scout and runs
full financial analysis, comparable sales comparison, Bargain Score
calculation, and AI-powered deal assessment.

Output: Deal objects with cash-flow model, Bargain Score, and AI analysis.
"""

from __future__ import annotations

from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.deal import CashFlowModel, Deal, DealType
from nexusprop.models.property import Property
from nexusprop.models.suburb import SuburbProfile
from nexusprop.tools.bargain_scorer import BargainScorer
from nexusprop.tools.comps_engine import CompAnalysis, CompsEngine
from nexusprop.tools.roi_calculator import ROICalculator


ANALYST_SYSTEM_PROMPT = """You are the Property Insights Australia Analyst — an investment-grade Australian property analyst.

Your role: Produce INSTITUTIONAL-GRADE analysis. Not "this house is cheap" — but precise, 
data-backed intelligence that a fund manager would trust.

You will receive:
1. Property details (address, price, features, land size)
2. Suburb-level market data (median prices, growth rates, vacancy)
3. Cash-flow analysis (ROI, yield, monthly cash flow)
4. Bargain Score breakdown with component weights
5. Comparable sales data with $/sqm analysis

YOUR ANALYSIS MUST INCLUDE (Investment Grade Logic):

1. STREET-LEVEL PRICE POSITIONING
   - Price relative to the street's 5-year CAGR (compound annual growth rate)
   - NOT just "below median" — calculate exactly HOW FAR below the growth trajectory
   - Example: "This property is priced 14% below the street's 5-year CAGR of 8.2%"

2. LAND-TO-ASSET RATIO (L/A)
   - Land value as % of total property value
   - Compare to suburb average L/A ratio
   - Higher L/A = better long-term capital growth (land appreciates, buildings depreciate)
   - Example: "L/A ratio is 72%, which is 10% higher than the suburb average of 62%"

3. INFRASTRUCTURE PIPELINE IMPACT
   - What major projects are planned within 5km? (rail, hospital, school, motorway)
   - Historical precedent: what happened to prices near similar completed projects?
   - Example: "Metro West station 2.1km away (2028 completion). Comparable stations added 15-22% to nearby values"

4. CAPITAL GROWTH TRAJECTORY
   - 5-year CAGR for the suburb (house vs unit)
   - Momentum analysis: Is growth accelerating, stable, or decelerating?
   - Rental growth trajectory vs purchase price growth
   - Example: "5-year CAGR: 7.8% (accelerating — last 2 years averaged 9.1%)"

5. CASH-FLOW DEEP DIVE
   - Net yield AFTER all costs (strata, council, water, management, insurance, vacancy)
   - Cash-flow breakeven point (when does the property become CF+ if currently CF-)
   - Sensitivity analysis: What happens if rates go up 1%? Down 1%?
   - Example: "Currently CF- $127/mo. Breakeven at 5.8% interest rate (current: 6.25%)"

6. RISK MATRIX
   - Supply risk: How many new listings / DA approvals in the area?
   - Demand drivers: Population growth, employment, infrastructure
   - Regulatory risk: Upcoming zoning changes, land tax changes
   - Liquidity risk: Average DOM trend (increasing or decreasing?)

7. PRECISE ENTRY PRICE RECOMMENDATION
   - Not a range — give a SPECIFIC suggested entry price
   - Based on: Bargain Score, agent discount patterns, DOM, market conditions
   - Example: "Suggested entry price: $885,000 (8.2% below asking, aligned with street CAGR)"

8. FINAL VERDICT
   - DEAL / FAIR / TRAP — with CONFIDENCE LEVEL (High/Medium/Low)
   - One-sentence summary a fund manager would put in their memo
   - Example: "DEAL (High Confidence) — Mispriced by 14% relative to street CAGR, L/A ratio 72% suggests strong land value upside. Entry at $885k."

FORMAT:
Use structured headings. Lead with numbers. No fluff.
Every claim must reference data. If data is missing, say so.
Australian terminology only (stamp duty, strata, council rates, Section 32)."""


class AnalystAgent(BaseAgent):
    """
    Agent B — The Analyst.

    Takes Property objects from the Scout and produces fully analyzed Deal objects
    with ROI calculations, Bargain Scores, and AI-powered market assessments.
    """

    def __init__(self):
        super().__init__("Analyst")
        self.roi_calculator = ROICalculator()
        self.bargain_scorer = BargainScorer(
            golden_threshold=self.settings.golden_opportunity_score
        )
        self.comps_engine = CompsEngine()

    async def execute(
        self,
        properties: list[Property],
        suburb_profiles: Optional[dict[str, SuburbProfile]] = None,
        sold_data: Optional[dict[str, list[Property]]] = None,
        strategy: DealType = DealType.BTL,
        run_ai_analysis: bool = True,
    ) -> AgentResult:
        """
        Analyze a batch of properties and produce Deal objects.

        Args:
            properties: List of Property objects from the Scout
            suburb_profiles: Dict of suburb_name -> SuburbProfile
            sold_data: Dict of suburb_name -> list of recently sold properties
            strategy: Default investment strategy to analyze
            run_ai_analysis: Whether to use AI for deep analysis
        """
        self.logger.info("analyst_run_started", count=len(properties))

        deals: list[Deal] = []
        total_tokens = 0
        errors = []

        for prop in properties:
            try:
                deal, tokens = await self._analyze_property(
                    prop=prop,
                    suburb_profiles=suburb_profiles or {},
                    sold_data=sold_data or {},
                    strategy=strategy,
                    run_ai=run_ai_analysis,
                )
                if deal:
                    deals.append(deal)
                    total_tokens += tokens
            except Exception as e:
                errors.append(f"{prop.address}: {str(e)}")
                self.logger.warning("property_analysis_failed", address=prop.address, error=str(e))

        # Sort by Bargain Score
        deals.sort(key=lambda d: d.bargain_score.overall_score, reverse=True)

        # Flag golden opportunities
        golden = [d for d in deals if d.is_golden_opportunity]

        self.logger.info(
            "analyst_run_completed",
            total_deals=len(deals),
            golden_opportunities=len(golden),
            errors=len(errors),
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "deals": deals,
                "golden_opportunities": golden,
                "total_analyzed": len(properties),
                "deals_found": len(deals),
                "golden_count": len(golden),
                "errors": errors,
            },
            tokens_used=total_tokens,
        )

    async def analyze_single(
        self,
        prop: Property,
        suburb: Optional[SuburbProfile] = None,
        sold_properties: Optional[list[Property]] = None,
        strategy: DealType = DealType.BTL,
    ) -> AgentResult:
        """Analyze a single property in detail."""
        suburb_profiles = {prop.suburb: suburb} if suburb else {}
        sold_data = {prop.suburb: sold_properties} if sold_properties else {}

        deal, tokens = await self._analyze_property(
            prop=prop,
            suburb_profiles=suburb_profiles,
            sold_data=sold_data,
            strategy=strategy,
            run_ai=True,
        )

        if deal:
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={"deal": deal},
                tokens_used=tokens,
            )
        return AgentResult(
            agent_name=self.name,
            success=False,
            error="Failed to analyze property",
        )

    async def _analyze_property(
        self,
        prop: Property,
        suburb_profiles: dict[str, SuburbProfile],
        sold_data: dict[str, list[Property]],
        strategy: DealType,
        run_ai: bool,
    ) -> tuple[Optional[Deal], int]:
        """Full analysis pipeline for a single property."""
        tokens = 0

        # Get or create suburb profile
        suburb = suburb_profiles.get(prop.suburb) or self._create_default_suburb(prop)

        # 1. ROI Calculation
        roi_result = self.roi_calculator.calculate(prop, strategy=strategy)

        # 2. Bargain Score
        bargain_score = self.bargain_scorer.score(
            prop=prop,
            suburb=suburb,
            net_yield=roi_result.net_yield,
        )

        # 3. Comparable Sales Analysis
        comps_summary = ""
        sold_props = sold_data.get(prop.suburb, [])
        if sold_props:
            comp_analysis = self.comps_engine.analyze(prop, sold_props)
            comps_summary = comp_analysis.summary

        # 4. Strategy Recommendation
        recommended_strategies = self.bargain_scorer.recommend_strategy(prop, suburb, bargain_score)
        if strategy not in recommended_strategies:
            recommended_strategies.insert(0, strategy)

        # 5. Optimal Offer Price
        offer_range = self._calculate_offer_range(prop, bargain_score, suburb)

        # 6. AI Analysis (optional — uses Claude for deep insights)
        ai_analysis = ""
        # Use OpenAI (pre-configured) or any available LLM — not just Anthropic
        import os
        _has_llm = bool(os.environ.get("OPENAI_API_KEY") or self.settings.anthropic_api_key or self.settings.use_ollama)
        if run_ai and _has_llm:
            ai_analysis, ai_tokens = await self._run_ai_analysis(
                prop, suburb, roi_result, bargain_score, comps_summary
            )
            tokens += ai_tokens

        # Build Deal object
        deal = Deal(
            property=prop,
            suburb_median_price=suburb.growth.median_house_price or 0,
            deal_type=strategy,
            recommended_strategies=recommended_strategies,
            cash_flow=roi_result.cash_flow_model,
            bargain_score=bargain_score,
            ai_analysis=ai_analysis,
            comparable_sales_summary=comps_summary,
            recommended_offer_price=offer_range[1],  # midpoint
            offer_range_low=offer_range[0],
            offer_range_high=offer_range[2],
        )

        return deal, tokens

    async def _run_ai_analysis(
        self,
        prop: Property,
        suburb: SuburbProfile,
        roi_result,
        bargain_score,
        comps_summary: str,
    ) -> tuple[str, int]:
        """Run investment-grade AI analysis using Claude."""
        # Calculate derived metrics for the prompt
        land_value_est = 0
        land_to_asset_ratio = 0
        if prop.land_size_sqm and prop.effective_price:
            # Estimate land value (rough: suburb median / avg land size * this land size)
            avg_land_sqm = 500  # Default assumption
            if suburb.growth.median_house_price and avg_land_sqm > 0:
                land_per_sqm = (suburb.growth.median_house_price * 0.65) / avg_land_sqm
                land_value_est = land_per_sqm * prop.land_size_sqm
                land_to_asset_ratio = (land_value_est / prop.effective_price) * 100 if prop.effective_price > 0 else 0

        # CAGR estimate from suburb growth
        annual_growth = suburb.growth.annual_growth_pct_house or 0
        cagr_5yr = annual_growth  # Simplified — in production pull from time-series

        # Price per sqm
        price_per_sqm_land = (prop.effective_price / prop.land_size_sqm) if (prop.effective_price and prop.land_size_sqm and prop.land_size_sqm > 0) else 0
        price_per_sqm_building = (prop.effective_price / prop.building_size_sqm) if (prop.effective_price and prop.building_size_sqm and prop.building_size_sqm > 0) else 0

        prompt = f"""INVESTMENT-GRADE ANALYSIS REQUEST

PROPERTY:
- Address: {prop.address}, {prop.suburb} {prop.state} {prop.postcode}
- Type: {prop.property_type.value} | {prop.bedrooms or '?'}BR {prop.bathrooms or '?'}BA {prop.car_spaces or '?'}Car
- Asking Price: ${prop.effective_price or 0:,.0f}
- Land Size: {prop.land_size_sqm or 'Unknown'}m² | Building: {prop.building_size_sqm or 'Unknown'}m²
- Price per m² (land): ${price_per_sqm_land:,.0f}/m²
- Price per m² (building): ${price_per_sqm_building:,.0f}/m²
- Year Built: {prop.year_built or 'Unknown'}
- Condition: {prop.condition.value}
- Zoning: {prop.zoning or 'Unknown'}
- Distress Signals: {', '.join(s.keyword for s in prop.distress_signals) or 'None detected'}
- Listing Text: {(prop.listing_text or '')[:800]}

SUBURB MARKET DATA ({prop.suburb}):
- Median House Price: ${suburb.growth.median_house_price or 0:,.0f}
- 5-Year CAGR (estimated): {cagr_5yr:.1f}%
- Annual Growth: {suburb.growth.annual_growth_pct_house or 0}%
- Gross Rental Yield: {suburb.growth.gross_rental_yield_house or 0}%
- Vacancy Rate: {suburb.vacancy_rate_pct or 'Unknown'}%
- Days on Market (avg): {suburb.growth.days_on_market_avg or 'Unknown'}
- Population: {suburb.demographics.population or 'Unknown'}
- Median Household Income: ${suburb.demographics.median_household_income or 0:,.0f}

LAND-TO-ASSET ANALYSIS:
- Estimated Land Value: ${land_value_est:,.0f}
- Land-to-Asset Ratio: {land_to_asset_ratio:.1f}%
- Suburb Average L/A Ratio: ~62% (estimated)

FINANCIAL ANALYSIS:
- Gross Rental Yield: {roi_result.gross_rental_yield}%
- Net Yield: {roi_result.net_yield}%
- ROI: {roi_result.roi}%
- Monthly Cash Flow: ${roi_result.monthly_cash_flow:,.0f}
- Cash Flow Positive: {'Yes' if roi_result.is_cash_flow_positive else 'No'}
- Total Investment Required: ${roi_result.total_investment:,.0f}
- Annual Expenses: ${roi_result.cash_flow_model.annual_expenses:,.0f}
- Annual Mortgage: ${roi_result.cash_flow_model.annual_mortgage_repayment:,.0f}

BARGAIN SCORE: {bargain_score.overall_score}/100
- Price Deviation Score: {bargain_score.price_deviation_score}/100 (35% weight)
- Distress Delta: {bargain_score.distress_delta:+.1f}% below median
- Cash Flow Score: {bargain_score.cash_flow_score}/100 (25% weight)
- Market Timing Score: {bargain_score.market_timing_score}/100 (15% weight)
- Golden Opportunity: {'YES ⭐' if bargain_score.is_golden_opportunity else 'No'}

COMPARABLE SALES:
{comps_summary or 'No comparable sales data available — use suburb-level data for positioning.'}

Produce your Investment-Grade Analysis. Follow the structured format in your system prompt.
Lead with the numbers. Be precise. Give a specific entry price recommendation."""

        return await self.ask_llm(
            prompt=prompt,
            system=ANALYST_SYSTEM_PROMPT,
            max_tokens=3072,
            temperature=0.2,  # Lower temperature for factual, precise analysis
        )

    def _calculate_offer_range(
        self,
        prop: Property,
        bargain_score,
        suburb: SuburbProfile,
    ) -> tuple[float, float, float]:
        """Calculate recommended offer range (low, mid, high)."""
        asking = prop.effective_price or 0
        if asking == 0:
            return (0, 0, 0)

        # Base discount depends on bargain score
        if bargain_score.overall_score >= 85:
            # Golden opportunity — offer close to asking (it's already a bargain)
            low_pct, mid_pct, high_pct = 0.92, 0.95, 0.98
        elif bargain_score.overall_score >= 65:
            # Good deal — moderate negotiation
            low_pct, mid_pct, high_pct = 0.85, 0.90, 0.95
        elif bargain_score.overall_score >= 40:
            # Fair — heavier negotiation needed
            low_pct, mid_pct, high_pct = 0.80, 0.85, 0.90
        else:
            # Overpriced — aggressive lowball or walk away
            low_pct, mid_pct, high_pct = 0.75, 0.80, 0.85

        # Adjust for distress
        if prop.has_distress_signals:
            low_pct -= 0.05

        return (
            round(asking * low_pct, -3),
            round(asking * mid_pct, -3),
            round(asking * high_pct, -3),
        )

    def _create_default_suburb(self, prop: Property) -> SuburbProfile:
        """Create a default suburb profile when one isn't available."""
        return SuburbProfile(
            suburb_name=prop.suburb,
            state=prop.state,
            postcode=prop.postcode,
        )
