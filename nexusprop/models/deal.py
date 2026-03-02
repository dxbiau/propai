"""
Deal model — the output of the Analyst agent.

A Deal wraps a Property with financial analysis, Bargain Score, and strategy classification.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field

from nexusprop.models.property import Property


class DealType(str, Enum):
    """Australian property investment strategy types."""
    BTL = "BTL"       # Buy-to-Let
    R2SA = "R2SA"     # Rent-to-Serviced Accommodation
    FLIP = "FLIP"     # Buy, renovate, sell
    BRRR = "BRRR"     # Buy, Rehab, Rent, Refinance, Repeat
    HMO = "HMO"      # House in Multiple Occupation
    PLO = "PLO"       # Purchase Lease Option
    SUBDIVISION = "SUBDIVISION"
    DEVELOPMENT = "DEVELOPMENT"
    LAND_BANK = "LAND_BANK"
    OWNER_OCCUPIER = "OWNER_OCCUPIER"


class CashFlowModel(BaseModel):
    """Full cash-flow breakdown for a deal."""

    # --- Purchase Costs ---
    purchase_price: float = Field(..., ge=0)
    stamp_duty: float = Field(default=0, ge=0)
    legal_costs: float = Field(default=3_000, ge=0)
    building_inspection: float = Field(default=600, ge=0)
    pest_inspection: float = Field(default=400, ge=0)
    other_purchase_costs: float = Field(default=0, ge=0)

    # --- Renovation (if applicable) ---
    renovation_cost: float = Field(default=0, ge=0)

    # --- Financing ---
    deposit_pct: float = Field(default=20.0, ge=0, le=100)
    loan_amount: float = Field(default=0, ge=0)
    interest_rate_pct: float = Field(default=6.25, ge=0, le=30)
    loan_term_years: int = Field(default=30, ge=1, le=40)

    # --- Income ---
    weekly_rent: float = Field(default=0, ge=0)
    annual_gross_income: float = Field(default=0, ge=0)

    # --- Expenses ---
    property_management_pct: float = Field(default=7.0, ge=0, le=30)
    council_rates_annual: float = Field(default=0, ge=0)
    water_rates_annual: float = Field(default=0, ge=0)
    strata_annual: float = Field(default=0, ge=0)
    insurance_annual: float = Field(default=1_500, ge=0)
    maintenance_annual: float = Field(default=2_000, ge=0)
    vacancy_weeks: float = Field(default=2, ge=0, le=52)
    other_expenses_annual: float = Field(default=0, ge=0)

    # --- Growth assumption for ROI ---
    capital_growth_rate_pct: float = Field(default=5.0, ge=0, le=30, description="Estimated annual capital growth %")

    @computed_field
    @property
    def total_purchase_cost(self) -> float:
        return (
            self.purchase_price
            + self.stamp_duty
            + self.legal_costs
            + self.building_inspection
            + self.pest_inspection
            + self.other_purchase_costs
        )

    @computed_field
    @property
    def total_investment(self) -> float:
        """Total capital required including reno."""
        deposit = self.purchase_price * (self.deposit_pct / 100)
        return deposit + self.stamp_duty + self.legal_costs + self.renovation_cost + self.building_inspection + self.pest_inspection

    @computed_field
    @property
    def annual_mortgage_repayment(self) -> float:
        """Interest-only annual repayment."""
        return self.loan_amount * (self.interest_rate_pct / 100)

    @computed_field
    @property
    def annual_expenses(self) -> float:
        management_fee = self.annual_gross_income * (self.property_management_pct / 100)
        vacancy_cost = (self.weekly_rent * self.vacancy_weeks)
        return (
            self.annual_mortgage_repayment
            + management_fee
            + self.council_rates_annual
            + self.water_rates_annual
            + self.strata_annual
            + self.insurance_annual
            + self.maintenance_annual
            + vacancy_cost
            + self.other_expenses_annual
        )

    @computed_field
    @property
    def annual_operating_expenses(self) -> float:
        """Operating expenses EXCLUDING mortgage payments."""
        management_fee = self.annual_gross_income * (self.property_management_pct / 100)
        vacancy_cost = (self.weekly_rent * self.vacancy_weeks)
        return (
            management_fee
            + self.council_rates_annual
            + self.water_rates_annual
            + self.strata_annual
            + self.insurance_annual
            + self.maintenance_annual
            + vacancy_cost
            + self.other_expenses_annual
        )

    @computed_field
    @property
    def annual_net_income(self) -> float:
        return self.annual_gross_income - self.annual_expenses

    @computed_field
    @property
    def gross_rental_yield(self) -> float:
        """GR% = (Annual Rent / Purchase Price) × 100"""
        if self.purchase_price == 0:
            return 0.0
        return round((self.annual_gross_income / self.purchase_price) * 100, 2)

    @computed_field
    @property
    def net_yield(self) -> float:
        """Net Yield% = (Annual Rent − Operating Expenses excl. mortgage) / Purchase Price × 100"""
        if self.purchase_price == 0:
            return 0.0
        net_operating_income = self.annual_gross_income - self.annual_operating_expenses
        return round((net_operating_income / self.purchase_price) * 100, 2)

    @computed_field
    @property
    def roi(self) -> float:
        """ROI% = (Annual Cash Flow + Est. Annual Capital Growth) / Total Cash Invested × 100"""
        if self.total_investment == 0:
            return 0.0
        annual_capital_growth = self.purchase_price * (self.capital_growth_rate_pct / 100)
        return round(((self.annual_net_income + annual_capital_growth) / self.total_investment) * 100, 2)

    @computed_field
    @property
    def cash_on_cash_return(self) -> float:
        """Cash-on-Cash = (Annual Cash Flow after mortgage) / Total Cash Invested × 100"""
        if self.total_investment == 0:
            return 0.0
        return round((self.annual_net_income / self.total_investment) * 100, 2)

    @computed_field
    @property
    def monthly_cash_flow(self) -> float:
        return round(self.annual_net_income / 12, 2)

    @computed_field
    @property
    def is_cash_flow_positive(self) -> bool:
        return self.annual_net_income > 0


class BargainScore(BaseModel):
    """
    The proprietary Bargain Score™ — how "good" the deal is.

    Combines price deviation from median, distress signals, market conditions,
    and cash-flow potential into a single 0–100 score.
    """

    overall_score: float = Field(ge=0, le=100, description="The Bargain Score™ 0–100")

    # --- Components ---
    price_deviation_score: float = Field(
        ge=0, le=100,
        description="How far below suburb median (higher = bigger discount)"
    )
    distress_delta: float = Field(
        description="% below median, adjusted for condition"
    )
    cash_flow_score: float = Field(
        ge=0, le=100,
        description="Cash-flow attractiveness"
    )
    market_timing_score: float = Field(
        ge=0, le=100,
        description="Market cycle timing favorability"
    )
    condition_adjustment: float = Field(
        default=0,
        description="Adjustment factor for property condition (-20 to +10)"
    )

    # --- Signal ---
    is_golden_opportunity: bool = Field(
        default=False,
        description="True if score >= golden_opportunity_score threshold"
    )
    summary: str = Field(default="", description="Human-readable deal summary")

    @classmethod
    def calculate(
        cls,
        asking_price: float,
        suburb_median: float,
        net_yield: float,
        distress_score: float,
        days_on_market: Optional[int] = None,
        condition_factor: float = 0,
        market_growth_pct: float = 0,
        golden_threshold: float = 85,
    ) -> BargainScore:
        """Factory method to calculate the Bargain Score from inputs."""

        # Price deviation (0–100)
        if suburb_median > 0:
            price_diff_pct = ((suburb_median - asking_price) / suburb_median) * 100
        else:
            price_diff_pct = 0
        price_deviation_score = max(0, min(price_diff_pct * 3, 100))

        # Distress delta
        distress_delta = price_diff_pct + condition_factor

        # Cash flow score (0–100)
        cash_flow_score = max(0, min(net_yield * 10, 100))

        # Market timing (0–100) — favor flat/declining markets for buyers
        if market_growth_pct < 0:
            market_timing_score = min(80 + abs(market_growth_pct) * 2, 100)
        elif market_growth_pct < 3:
            market_timing_score = 60
        else:
            market_timing_score = max(40 - market_growth_pct * 2, 0)

        # Days on market bonus
        dom_bonus = 0
        if days_on_market and days_on_market > 90:
            dom_bonus = min((days_on_market - 90) / 10, 10)

        # Weights
        overall = (
            price_deviation_score * 0.35
            + cash_flow_score * 0.25
            + distress_score * 0.20
            + market_timing_score * 0.15
            + dom_bonus * 0.05
            + condition_factor
        )
        overall = max(0, min(round(overall, 1), 100))

        # Summary
        if overall >= golden_threshold:
            summary = f"🏆 GOLDEN OPPORTUNITY — Bargain Score {overall}/100. {distress_delta:+.1f}% below median."
        elif overall >= 65:
            summary = f"✅ Strong Deal — Bargain Score {overall}/100. Worth investigating."
        elif overall >= 40:
            summary = f"⚠️ Fair Deal — Bargain Score {overall}/100. Proceed with caution."
        else:
            summary = f"❌ Below Threshold — Bargain Score {overall}/100. Likely overpriced."

        return cls(
            overall_score=overall,
            price_deviation_score=round(price_deviation_score, 1),
            distress_delta=round(distress_delta, 1),
            cash_flow_score=round(cash_flow_score, 1),
            market_timing_score=round(market_timing_score, 1),
            condition_adjustment=condition_factor,
            is_golden_opportunity=overall >= golden_threshold,
            summary=summary,
        )


class Deal(BaseModel):
    """
    A fully analyzed deal — the output of the Analyst agent.

    Contains the property, cash-flow model, bargain score, and strategy recommendation.
    """

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Core ---
    property: Property
    suburb_median_price: float = Field(ge=0, description="Current suburb median for this property type")

    # --- Analysis ---
    deal_type: DealType = DealType.BTL
    recommended_strategies: list[DealType] = Field(default_factory=list)
    cash_flow: CashFlowModel
    bargain_score: BargainScore

    # --- AI Insight ---
    ai_analysis: str = Field(
        default="",
        description="Opus 4.6 generated analysis — deal or trap?"
    )
    comparable_sales_summary: str = Field(
        default="",
        description="Summary of comparable recent sales"
    )

    # --- Action ---
    recommended_offer_price: Optional[float] = Field(None, ge=0)
    offer_range_low: Optional[float] = Field(None, ge=0)
    offer_range_high: Optional[float] = Field(None, ge=0)

    # --- Competitive Features (beats Deal Sourcer) ---
    estimated_refurb_cost: float = Field(default=0, ge=0, description="Estimated renovation cost AUD")
    after_repair_value: float = Field(default=0, ge=0, description="ARV after renovation AUD")
    flip_profit: float = Field(default=0, description="Estimated flip profit after all costs")
    brrr_equity_gain: float = Field(default=0, ge=0, description="Forced equity from BRRR strategy")

    @computed_field
    @property
    def is_golden_opportunity(self) -> bool:
        return self.bargain_score.is_golden_opportunity

    @computed_field
    @property
    def price_per_sqm(self) -> Optional[float]:
        """Price per square meter — THE key metric for spotting value (competitor's top feature)."""
        price = self.property.effective_price
        sqm = self.property.building_size_sqm or self.property.land_size_sqm
        if price and sqm and sqm > 0:
            return round(price / sqm, 0)
        return None

    @computed_field
    @property
    def land_to_asset_ratio(self) -> Optional[float]:
        """Land value as % of total price — higher = better long-term growth."""
        price = self.property.effective_price
        land = self.property.land_size_sqm
        building = self.property.building_size_sqm
        if price and land and building and building > 0:
            # Rough estimate: land proportion based on size ratios
            land_pct = min(land / (land + building * 3), 0.85)
            return round(land_pct * 100, 1)
        return None

    @computed_field
    @property
    def payback_period_months(self) -> Optional[float]:
        """Months to recoup total investment from net cash flow. Deal Sourcer has this."""
        if self.cash_flow.monthly_cash_flow <= 0:
            return None  # Negative cash flow = never pays back from cash flow alone
        return round(self.cash_flow.total_investment / self.cash_flow.monthly_cash_flow, 1)

    @computed_field
    @property
    def bmv_pct(self) -> float:
        """Below Market Value percentage — how far below suburb median."""
        if self.suburb_median_price <= 0:
            return 0.0
        price = self.property.effective_price or 0
        return round(((self.suburb_median_price - price) / self.suburb_median_price) * 100, 1)

    @computed_field
    @property
    def uplift_value_pct(self) -> float:
        """Potential value uplift from renovation (refurb to ARV)."""
        price = self.property.effective_price or 0
        if self.after_repair_value > 0 and price > 0:
            return round(((self.after_repair_value - price) / price) * 100, 1)
        return 0.0

    @computed_field
    @property
    def headline(self) -> str:
        prop = self.property
        price_str = f"${prop.effective_price:,.0f}" if prop.effective_price else "Price TBC"
        sqm_str = f" | ${self.price_per_sqm:,.0f}/m²" if self.price_per_sqm else ""
        return (
            f"{prop.bedrooms or '?'}BR {prop.property_type.value.title()} "
            f"in {prop.suburb} — {price_str}{sqm_str} — "
            f"Bargain Score: {self.bargain_score.overall_score}/100"
        )
