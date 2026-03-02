"""
Stacker Agent — deal structuring and creative finance engine.

Takes an analyzed Deal and an investor's InvestmentProfile, then structures
the optimal purchase scenario: entity selection, financing strategy,
tax optimization, BRRR modeling, SMSF compliance, JV structuring.

This is the "HOW to buy it" agent — after the Analyst says "WHAT to buy."
"""

from __future__ import annotations

import json
from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.config.settings import get_settings
from nexusprop.models.deal import Deal
from nexusprop.models.investment import (
    DealStructure,
    EntityType,
    ExperienceLevel,
    FinanceStrategy,
    InvestmentGoal,
    InvestmentProfile,
    RiskTolerance,
)


STACKER_SYSTEM_PROMPT = """You are the Property Insights Australia Stacker — an expert Australian property deal structuring agent.

Your role: Take an analyzed deal and an investor profile, then structure the OPTIMAL purchase scenario considering entity, financing, tax, and risk.

YOU MUST CONSIDER:

1. ENTITY SELECTION
   - Personal: Simple, full negative gearing benefit, but highest land tax
   - Family Trust: Flexibility to distribute income, asset protection, but can't distribute losses
   - SMSF: Tax-advantaged (15% in accumulation, 0% in pension), but strict rules:
     * Must use LRBA (Limited Recourse Borrowing)
     * Cannot renovate with borrowed funds
     * Single acquirable asset rule
     * Cannot buy from related parties
     * Must meet sole purpose test
   - Company: 25-30% flat tax rate, no CGT discount, good for development
   - Joint: Useful for couples, tenants in common allows different shares

2. FINANCING STRATEGY
   - Standard IO: Interest-only, maximize deductions, preserve cash
   - Standard PI: Build equity, lower long-term cost
   - BRRR: Buy below market → Renovate → Rent at higher rate → Refinance at new value → Repeat
     * Model: Purchase + Reno Cost vs After Repair Value
     * Forced equity = ARV - (Purchase + Reno)
     * Refinance at 80% of ARV = cash out
   - Equity Release: Cross-collateralise existing property equity
   - Vendor Finance: No bank required, higher interest, creative terms
   - JV: Joint venture, split capital/equity/returns
   - SMSF LRBA: Limited recourse borrowing arrangement
   - Deposit Bond: For off-plan or auction (no cash deposit needed)

3. TAX OPTIMIZATION (Australian)
   - Negative gearing: Investment losses offset PAYG income at marginal rate
   - Depreciation: Building (2.5% p.a.) + Plant & Equipment (diminishing value)
   - Capital Gains Tax: 50% discount after 12 months (individuals/trusts)
   - Land tax thresholds vary by state and entity
   - GST: Applicable on new/substantially renovated properties
   - Stamp duty: Concessions for first home buyers, off-plan purchases

4. RISK ASSESSMENT
   - Interest rate risk: Stress test at +2% and +3%
   - Vacancy risk: Seasonal, location-specific
   - Market risk: Cycle position, oversupply indicators
   - Renovation risk: Cost blowout probability
   - Liquidity risk: Time to sell in current market
   - Concentration risk: Geographic, asset class

5. PROJECTED RETURNS
   - Year 1: Cash flow, tax benefit, total return
   - 5-Year: Capital growth, equity position, cumulative cash flow
   - 10-Year: Portfolio impact, passive income contribution

OUTPUT: Structured JSON with complete deal structure, projected returns,
risk assessment, and actionable next steps.

CRITICAL RULES:
- All calculations must use current Australian market rates
- Always provide interest rate stress testing
- Never guarantee returns — use "projected" or "estimated"
- Flag any compliance issues (SMSF, tax, zoning)
- Be specific about costs — don't handwave stamp duty or legal fees"""


class StackerAgent(BaseAgent):
    """
    Stacker Agent — structures deals into optimal investment scenarios.

    Given a Deal (from the Analyst) and an InvestmentProfile (from the Profiler),
    generates 1-3 structured deal scenarios with different strategies, entities,
    and financing approaches — each with projected returns and risk assessment.
    """

    def __init__(self):
        super().__init__("Stacker")
        self.settings = get_settings()

    async def execute(
        self,
        deal: Deal,
        profile: Optional[InvestmentProfile] = None,
        strategies: Optional[list[FinanceStrategy]] = None,
        include_brrr: bool = True,
        include_smsf: bool = False,
    ) -> AgentResult:
        """
        Structure a deal into 1-3 investment scenarios.

        Args:
            deal: Analyzed deal from the Analyst agent
            profile: Investor profile from the Profiler agent
            strategies: Specific strategies to model (None = auto-select)
            include_brrr: Whether to include BRRR analysis
            include_smsf: Whether to include SMSF analysis
        """
        self.logger.info(
            "stacker_started",
            property_address=deal.property.address,
            asking_price=deal.property.effective_price,
            has_profile=profile is not None,
        )

        profile = profile or InvestmentProfile()

        # Determine strategies to model
        if not strategies:
            strategies = self._select_strategies(deal, profile, include_brrr, include_smsf)

        # Build structures for each strategy
        structures: list[DealStructure] = []
        for strategy in strategies[:3]:  # Max 3 scenarios
            structure = self._build_structure(deal, profile, strategy)
            structures.append(structure)

        # Get AI analysis for context and recommendations
        ai_analysis = ""
        tokens = 0
        if structures:
            ai_analysis, tokens = await self._generate_analysis(deal, profile, structures)

        # Rank by total return
        structures.sort(key=lambda s: s.total_return_year1_pct, reverse=True)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "structures": [s.model_dump(mode="json") for s in structures],
                "recommended": structures[0].model_dump(mode="json") if structures else None,
                "ai_analysis": ai_analysis,
                "strategies_modeled": [s.strategy.value for s in structures],
                "deal_id": str(deal.id),
            },
            tokens_used=tokens,
        )

    def _select_strategies(
        self,
        deal: Deal,
        profile: InvestmentProfile,
        include_brrr: bool,
        include_smsf: bool,
    ) -> list[FinanceStrategy]:
        """Auto-select the best strategies based on deal and profile."""
        strategies = []

        # Standard IO is always an option
        strategies.append(FinanceStrategy.STANDARD_IO)

        # BRRR if property needs work and investor is experienced
        prop = deal.property
        if include_brrr and prop.condition in {"renovation_required", "fair", "knockdown_rebuild"}:
            if profile.experience_level in {ExperienceLevel.INTERMEDIATE, ExperienceLevel.ADVANCED, ExperienceLevel.EXPERT}:
                strategies.append(FinanceStrategy.BRRR)

        # Equity release if they have an existing portfolio
        if profile.financial.equity_available > 50_000:
            strategies.append(FinanceStrategy.EQUITY_RELEASE)

        # SMSF if balance warrants it
        if include_smsf and profile.financial.smsf_balance > 200_000:
            strategies.append(FinanceStrategy.SMSF_LRBA)

        # JV for larger deals they can't afford alone
        price = prop.effective_price or 0
        if price > profile.max_next_purchase * 1.2:
            strategies.append(FinanceStrategy.JOINT_VENTURE)

        # Vendor finance for very motivated sellers
        if prop.has_distress_signals and profile.risk_tolerance in {RiskTolerance.AGGRESSIVE, RiskTolerance.SPECULATIVE}:
            strategies.append(FinanceStrategy.VENDOR_FINANCE)

        return strategies[:3]

    def _build_structure(
        self,
        deal: Deal,
        profile: InvestmentProfile,
        strategy: FinanceStrategy,
    ) -> DealStructure:
        """Build a complete deal structure for a given strategy."""
        prop = deal.property
        purchase_price = prop.effective_price or 0
        weekly_rent = prop.estimated_weekly_rent or prop.current_weekly_rent or deal.cash_flow.weekly_rent or 0

        # Entity selection
        entity = self._select_entity(profile, strategy, purchase_price)

        # LVR and deposit
        lvr = self._calculate_lvr(profile, strategy)
        deposit = purchase_price * (1 - lvr / 100)
        loan_amount = purchase_price * (lvr / 100)

        # Stamp duty
        stamp_duty = self.settings.calculate_stamp_duty(purchase_price)

        # Interest rate
        rate = self.settings.default_interest_rate
        if strategy == FinanceStrategy.SMSF_LRBA:
            rate += 0.5  # SMSF loans typically higher
        elif strategy == FinanceStrategy.VENDOR_FINANCE:
            rate += 2.0  # Vendor finance premium

        # Annual income
        annual_income = weekly_rent * 52

        # Annual expenses
        management_fee = annual_income * 0.07
        io_repayment = loan_amount * (rate / 100)
        council = prop.council_rates_annual or (purchase_price * 0.003)
        water = prop.water_rates_annual or 1_200
        strata = (prop.strata_levies_quarterly or 0) * 4
        insurance = 1_500
        maintenance = 2_000
        vacancy_cost = weekly_rent * 2  # 2 weeks vacancy

        annual_expenses = (
            io_repayment + management_fee + council + water
            + strata + insurance + maintenance + vacancy_cost
        )
        annual_cashflow = annual_income - annual_expenses

        # Gross yield
        gross_yield = (annual_income / purchase_price * 100) if purchase_price > 0 else 0

        # Net yield
        total_capital = deposit + stamp_duty + 3_000  # legal costs
        net_yield = (annual_cashflow / total_capital * 100) if total_capital > 0 else 0

        # Depreciation estimate
        depreciation = self._estimate_depreciation(prop, purchase_price)

        # Tax benefit (negative gearing)
        if annual_cashflow < 0:
            # Marginal tax rate estimate
            marginal_rate = self._estimate_marginal_rate(profile)
            tax_saving = abs(annual_cashflow + depreciation) * marginal_rate
        else:
            tax_saving = depreciation * self._estimate_marginal_rate(profile) * 0.5

        # After-tax cashflow
        after_tax_cf = annual_cashflow + tax_saving

        # 5-year growth projection
        growth_rate = self._estimate_growth_rate(prop)

        # BRRR specifics
        reno_budget = 0.0
        arv = 0.0
        forced_equity = 0.0
        if strategy == FinanceStrategy.BRRR:
            reno_budget = self._estimate_renovation_cost(prop, purchase_price)
            arv = purchase_price + (reno_budget * 1.5)  # 150% value uplift on reno spend
            forced_equity = arv - purchase_price - reno_budget

        # SMSF compliance
        smsf_compliant = strategy == FinanceStrategy.SMSF_LRBA
        smsf_lrba = strategy == FinanceStrategy.SMSF_LRBA

        # Risk assessment
        risk_rating, risk_factors, mitigations = self._assess_risk(deal, profile, strategy, lvr)

        # Strategy name
        strategy_names = {
            FinanceStrategy.STANDARD_IO: "Standard Interest-Only",
            FinanceStrategy.STANDARD_PI: "Principal & Interest",
            FinanceStrategy.BRRR: "BRRR (Buy-Rehab-Rent-Refinance-Repeat)",
            FinanceStrategy.EQUITY_RELEASE: "Equity Release",
            FinanceStrategy.SMSF_LRBA: "SMSF Limited Recourse Borrowing",
            FinanceStrategy.JOINT_VENTURE: "Joint Venture",
            FinanceStrategy.VENDOR_FINANCE: "Vendor Finance",
        }

        return DealStructure(
            deal_id=deal.id,
            property_id=prop.id,
            strategy=strategy,
            entity_type=entity,
            strategy_name=strategy_names.get(strategy, strategy.value),
            purchase_price=purchase_price,
            deposit_required=round(deposit, 0),
            deposit_source="equity_release" if strategy == FinanceStrategy.EQUITY_RELEASE else "cash",
            loan_amount=round(loan_amount, 0),
            lvr_pct=lvr,
            interest_rate_pct=rate,
            loan_type="interest_only",
            stamp_duty=round(stamp_duty, 0),
            legal_costs=3_000,
            renovation_budget=round(reno_budget, 0),
            projected_weekly_rent=round(weekly_rent, 0),
            projected_annual_income=round(annual_income, 0),
            projected_annual_expenses=round(annual_expenses, 0),
            projected_annual_cashflow=round(annual_cashflow, 0),
            projected_gross_yield_pct=round(gross_yield, 2),
            projected_net_yield_pct=round(net_yield, 2),
            projected_5yr_capital_growth_pct=round(growth_rate * 5, 1),
            projected_5yr_equity_gain=round(purchase_price * (growth_rate * 5 / 100), 0),
            estimated_annual_depreciation=round(depreciation, 0),
            estimated_tax_benefit=round(tax_saving, 0),
            effective_after_tax_cashflow=round(after_tax_cf, 0),
            risk_rating=risk_rating,
            risk_factors=risk_factors,
            mitigation_strategies=mitigations,
            smsf_compliant=smsf_compliant,
            smsf_lrba_required=smsf_lrba,
            after_repair_value=round(arv, 0),
            forced_equity_gain=round(forced_equity, 0),
        )

    def _select_entity(
        self,
        profile: InvestmentProfile,
        strategy: FinanceStrategy,
        purchase_price: float,
    ) -> EntityType:
        """Select the optimal entity for this deal."""
        if strategy == FinanceStrategy.SMSF_LRBA:
            return EntityType.SMSF

        # If user has a preferred entity, respect it
        if profile.preferred_entity != EntityType.PERSONAL:
            return profile.preferred_entity

        # Auto-select based on goal and portfolio size
        if profile.primary_goal == InvestmentGoal.TAX_MINIMISATION:
            return EntityType.PERSONAL  # Maximize negative gearing benefit

        if profile.current_portfolio_count >= 3:
            return EntityType.FAMILY_TRUST  # Asset protection at scale

        if profile.primary_goal in {InvestmentGoal.SUBDIVISION, InvestmentGoal.WEALTH_CREATION}:
            if purchase_price > 1_000_000:
                return EntityType.COMPANY

        return EntityType.PERSONAL

    def _calculate_lvr(self, profile: InvestmentProfile, strategy: FinanceStrategy) -> float:
        """Calculate appropriate LVR for this strategy."""
        if strategy == FinanceStrategy.SMSF_LRBA:
            return 70.0  # SMSF max LVR typically 70-80%
        if strategy == FinanceStrategy.VENDOR_FINANCE:
            return 80.0
        if profile.risk_tolerance in {RiskTolerance.CONSERVATIVE}:
            return 70.0
        if profile.risk_tolerance in {RiskTolerance.AGGRESSIVE, RiskTolerance.SPECULATIVE}:
            return 90.0  # LMI territory
        return profile.max_acceptable_lvr

    def _estimate_depreciation(self, prop, purchase_price: float) -> float:
        """Estimate annual depreciation deduction."""
        # Building allowance: 2.5% p.a. for buildings built after 1985
        year_built = prop.year_built or 2000
        if year_built >= 1985:
            building_cost = purchase_price * 0.4  # ~40% of price is building
            building_depreciation = building_cost * 0.025  # 2.5% p.a.
        else:
            building_depreciation = 0

        # Plant & equipment: ~$5-15k p.a. for first 5 years
        if prop.condition in {"excellent", "good"}:
            plant_depreciation = 8_000
        elif prop.condition in {"fair"}:
            plant_depreciation = 5_000
        else:
            plant_depreciation = 3_000  # New renos have higher depreciation

        return building_depreciation + plant_depreciation

    def _estimate_marginal_rate(self, profile: InvestmentProfile) -> float:
        """Estimate marginal tax rate from income."""
        income = profile.financial.total_gross_income
        # 2024-25 Australian tax rates
        if income <= 18_200:
            return 0.0
        elif income <= 45_000:
            return 0.19
        elif income <= 120_000:
            return 0.325
        elif income <= 180_000:
            return 0.37
        else:
            return 0.45

    def _estimate_growth_rate(self, prop) -> float:
        """Estimate annual capital growth rate based on property attributes."""
        # Base rate: Australian long-run average ~6.5% p.a.
        base = 5.5

        # State adjustments
        state_adj = {
            "NSW": 1.0, "VIC": 0.5, "QLD": 1.5, "SA": 1.0,
            "WA": 0.5, "TAS": 0.0, "NT": -0.5, "ACT": 0.5,
        }
        base += state_adj.get(prop.state, 0)

        # Property type
        if prop.property_type.value in {"house", "duplex"}:
            base += 0.5  # Houses outperform units historically
        elif prop.property_type.value in {"unit", "apartment"}:
            base -= 0.5

        # Land size premium
        if prop.land_size_sqm and prop.land_size_sqm > 600:
            base += 0.5

        return base

    def _estimate_renovation_cost(self, prop, purchase_price: float) -> float:
        """Estimate renovation cost for BRRR strategy."""
        if prop.condition == "knockdown_rebuild":
            return purchase_price * 0.5
        elif prop.condition == "renovation_required":
            return min(purchase_price * 0.15, 80_000)
        elif prop.condition == "fair":
            return min(purchase_price * 0.08, 40_000)
        return min(purchase_price * 0.05, 25_000)  # Cosmetic reno

    def _assess_risk(
        self,
        deal: Deal,
        profile: InvestmentProfile,
        strategy: FinanceStrategy,
        lvr: float,
    ) -> tuple[str, list[str], list[str]]:
        """Assess risk for this deal structure."""
        risk_factors = []
        mitigations = []
        risk_score = 0

        # LVR risk
        if lvr > 90:
            risk_factors.append("High LVR (>90%) — negative equity risk if market dips")
            mitigations.append("Consider reducing LVR to 80% to avoid LMI and buffer against market correction")
            risk_score += 3
        elif lvr > 80:
            risk_factors.append("LVR >80% — Lenders Mortgage Insurance (LMI) applies")
            mitigations.append("LMI can be capitalized into the loan; consider 80% LVR if possible")
            risk_score += 1

        # Interest rate risk
        prop = deal.property
        price = prop.effective_price or 0
        rent = prop.estimated_weekly_rent or 0
        io_at_plus_3 = (price * lvr / 100) * (self.settings.default_interest_rate + 3) / 100
        annual_income = rent * 52
        if io_at_plus_3 > annual_income * 0.9:
            risk_factors.append("Interest rate stress: +3% rate rise would consume >90% of rental income")
            mitigations.append("Lock in fixed rate for 2-3 years; maintain cash buffer of 6 months expenses")
            risk_score += 2

        # Vacancy risk
        vacancy = prop.vacancy_rate_pct or 0
        if vacancy > 3:
            risk_factors.append(f"High vacancy rate ({vacancy}%) in this area")
            mitigations.append("Diversify tenant appeal; consider furnished or Airbnb if zoning permits")
            risk_score += 1

        # Strategy-specific risks
        if strategy == FinanceStrategy.BRRR:
            risk_factors.append("Renovation cost blowout risk (typically 10-30% over budget)")
            mitigations.append("Get 3 builder quotes; add 20% contingency; use fixed-price contracts")
            risk_score += 2

        if strategy == FinanceStrategy.SMSF_LRBA:
            risk_factors.append("SMSF compliance risk — strict ATO rules, potential penalties")
            mitigations.append("Engage SMSF-specialist accountant and solicitor; use bare trust structure")
            risk_score += 2

        if strategy == FinanceStrategy.VENDOR_FINANCE:
            risk_factors.append("Vendor finance — higher interest rate, non-standard contract terms")
            mitigations.append("Engage experienced solicitor; include clear put/call option terms")
            risk_score += 2

        # Concentration risk
        if profile.current_portfolio_count > 3 and deal.property.state == "NSW":
            risk_factors.append("Geographic concentration — majority of portfolio in one state")
            mitigations.append("Consider diversifying into QLD or SA for geographic spread")
            risk_score += 1

        # Rating
        if risk_score >= 6:
            rating = "very_high"
        elif risk_score >= 4:
            rating = "high"
        elif risk_score >= 2:
            rating = "moderate"
        else:
            rating = "low"

        return rating, risk_factors, mitigations

    async def _generate_analysis(
        self,
        deal: Deal,
        profile: InvestmentProfile,
        structures: list[DealStructure],
    ) -> tuple[str, int]:
        """Generate AI analysis comparing the deal structures."""
        prompt = f"""Compare these deal structuring options for an Australian property investor.

PROPERTY:
- Address: {deal.property.address}, {deal.property.suburb} {deal.property.state}
- Price: ${deal.property.effective_price or 0:,.0f}
- Type: {deal.property.property_type.value} | {deal.property.bedrooms or '?'}BR
- Bargain Score: {deal.bargain_score.overall_score}/100
- Condition: {deal.property.condition.value if hasattr(deal.property.condition, 'value') else deal.property.condition}

INVESTOR:
- Experience: {profile.experience_level.value}
- Goal: {profile.primary_goal.value}
- Risk: {profile.risk_tolerance.value}
- Max Budget: ${profile.max_next_purchase:,.0f}
- Borrowing Power: ${profile.financial.estimated_borrowing_power:,.0f}

SCENARIOS:
"""
        for i, s in enumerate(structures, 1):
            prompt += f"""
Scenario {i}: {s.strategy_name}
  Entity: {s.entity_type.value}
  LVR: {s.lvr_pct}% | Deposit: ${s.deposit_required:,.0f}
  Annual Cashflow: ${s.projected_annual_cashflow:,.0f}
  Gross Yield: {s.projected_gross_yield_pct}%
  Tax Benefit: ${s.estimated_tax_benefit:,.0f}
  After-Tax CF: ${s.effective_after_tax_cashflow:,.0f}
  Total Return Yr1: {s.total_return_year1_pct}%
  Risk: {s.risk_rating}
"""

        prompt += """
Provide:
1. RECOMMENDED SCENARIO and why
2. KEY RISKS to highlight
3. 3 SPECIFIC ACTION ITEMS for this investor
4. Any COMPLIANCE WARNINGS

Keep it practical and Australian-specific."""

        return await self.ask_llm(
            prompt=prompt,
            system=STACKER_SYSTEM_PROMPT,
            max_tokens=2048,
            temperature=0.3,
        )
