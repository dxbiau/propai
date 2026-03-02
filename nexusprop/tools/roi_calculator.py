"""
ROI Calculator — full Australian property cash-flow & return modelling.

Handles stamp duty, strata, council rates, vacancy, management fees,
interest-only & P&I repayments, and all strategy-specific calculations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from nexusprop.config.settings import get_settings
from nexusprop.models.deal import CashFlowModel, DealType
from nexusprop.models.property import Property


@dataclass
class ROIResult:
    """Complete ROI analysis result."""
    gross_rental_yield: float
    net_yield: float
    roi: float
    cash_on_cash_return: float
    monthly_cash_flow: float
    annual_net_income: float
    total_investment: float
    is_cash_flow_positive: bool
    years_to_break_even: Optional[float]
    cash_flow_model: CashFlowModel


class ROICalculator:
    """
    Full-featured property ROI calculator for Australian investors.

    Supports BTL, R2SA, BRRR, HMO, Flip, and Subdivision strategies.
    """

    def __init__(self):
        self.settings = get_settings()

    def calculate(
        self,
        prop: Property,
        strategy: DealType = DealType.BTL,
        weekly_rent_override: Optional[float] = None,
        renovation_cost: float = 0,
        after_repair_value: Optional[float] = None,
        interest_rate: Optional[float] = None,
        deposit_pct: Optional[float] = None,
        rooms_for_hmo: int = 0,
        r2sa_nightly_rate: float = 0,
        r2sa_occupancy_pct: float = 70,
    ) -> ROIResult:
        """
        Calculate complete ROI for a property under a given strategy.

        Args:
            prop: The property to analyze
            strategy: Investment strategy
            weekly_rent_override: Override estimated rent
            renovation_cost: Estimated renovation cost
            after_repair_value: Post-renovation value (for BRRR/Flip)
            interest_rate: Override default interest rate
            deposit_pct: Override default deposit %
            rooms_for_hmo: Number of lettable rooms for HMO strategy
            r2sa_nightly_rate: Nightly rate for R2SA strategy
            r2sa_occupancy_pct: Expected occupancy for R2SA
        """
        rate = interest_rate or self.settings.default_interest_rate
        dep_pct = deposit_pct or (100 - self.settings.default_loan_lvr)
        purchase_price = prop.effective_price or 0

        # Calculate weekly rent based on strategy
        weekly_rent = self._calculate_weekly_rent(
            prop=prop,
            strategy=strategy,
            weekly_rent_override=weekly_rent_override,
            rooms_for_hmo=rooms_for_hmo,
            r2sa_nightly_rate=r2sa_nightly_rate,
            r2sa_occupancy_pct=r2sa_occupancy_pct,
        )

        annual_gross_income = weekly_rent * 52

        # Stamp duty
        stamp_duty = self.settings.calculate_stamp_duty(purchase_price)

        # Loan
        loan_amount = purchase_price * (1 - dep_pct / 100)

        # Build cash-flow model
        cf = CashFlowModel(
            purchase_price=purchase_price,
            stamp_duty=stamp_duty,
            renovation_cost=renovation_cost,
            deposit_pct=dep_pct,
            loan_amount=loan_amount,
            interest_rate_pct=rate,
            weekly_rent=weekly_rent,
            annual_gross_income=annual_gross_income,
            council_rates_annual=prop.council_rates_annual or self._estimate_council_rates(purchase_price),
            water_rates_annual=prop.water_rates_annual or 800,
            strata_annual=(prop.strata_levies_quarterly or 0) * 4,
            property_management_pct=self._management_fee_pct(strategy),
            vacancy_weeks=self._vacancy_weeks(strategy),
            insurance_annual=self._estimate_insurance(purchase_price, strategy),
            maintenance_annual=self._estimate_maintenance(purchase_price, prop.year_built),
        )

        # Break-even calculation
        total_inv = cf.total_investment
        if cf.annual_net_income > 0:
            years_to_break_even = total_inv / cf.annual_net_income
        else:
            years_to_break_even = None

        # For Flip strategy, calculate differently
        if strategy == DealType.FLIP and after_repair_value:
            return self._calculate_flip(
                cf=cf,
                after_repair_value=after_repair_value,
                renovation_cost=renovation_cost,
                stamp_duty=stamp_duty,
            )

        return ROIResult(
            gross_rental_yield=cf.gross_rental_yield,
            net_yield=cf.net_yield,
            roi=cf.roi,
            cash_on_cash_return=cf.cash_on_cash_return,
            monthly_cash_flow=cf.monthly_cash_flow,
            annual_net_income=cf.annual_net_income,
            total_investment=cf.total_investment,
            is_cash_flow_positive=cf.is_cash_flow_positive,
            years_to_break_even=years_to_break_even,
            cash_flow_model=cf,
        )

    def _calculate_weekly_rent(
        self,
        prop: Property,
        strategy: DealType,
        weekly_rent_override: Optional[float],
        rooms_for_hmo: int,
        r2sa_nightly_rate: float,
        r2sa_occupancy_pct: float,
    ) -> float:
        """Calculate expected weekly rent based on strategy."""
        if weekly_rent_override:
            return weekly_rent_override

        base_rent = prop.estimated_weekly_rent or prop.current_weekly_rent or 0

        if strategy == DealType.HMO and rooms_for_hmo > 0:
            # HMO: charge per room, typically 60–70% of a 1BR equivalent
            return rooms_for_hmo * (base_rent * 0.35)

        elif strategy == DealType.R2SA:
            # R2SA: nightly rate × occupancy
            if r2sa_nightly_rate > 0:
                return (r2sa_nightly_rate * 7) * (r2sa_occupancy_pct / 100)
            # Estimate: 2x standard rent at 70% occupancy
            return base_rent * 2 * 0.7

        return base_rent

    def _calculate_flip(
        self,
        cf: CashFlowModel,
        after_repair_value: float,
        renovation_cost: float,
        stamp_duty: float,
    ) -> ROIResult:
        """Calculate ROI for a flip/BRRR strategy."""
        total_cost = cf.purchase_price + renovation_cost + stamp_duty + cf.legal_costs
        gross_profit = after_repair_value - total_cost

        # Selling costs (agent commission ~2% + marketing ~$5k)
        selling_costs = after_repair_value * 0.025 + 5000
        net_profit = gross_profit - selling_costs

        # Assume 6-month hold
        holding_costs_6m = cf.annual_expenses / 2
        net_profit -= holding_costs_6m

        total_investment = cf.total_investment
        roi = (net_profit / total_investment * 100) if total_investment > 0 else 0

        return ROIResult(
            gross_rental_yield=0,
            net_yield=0,
            roi=round(roi, 2),
            cash_on_cash_return=round(roi, 2),
            monthly_cash_flow=round(net_profit / 6, 2),
            annual_net_income=round(net_profit * 2, 2),  # Annualized
            total_investment=total_investment,
            is_cash_flow_positive=net_profit > 0,
            years_to_break_even=0.5 if net_profit > 0 else None,
            cash_flow_model=cf,
        )

    def _estimate_council_rates(self, purchase_price: float) -> float:
        """Estimate annual council rates as a percentage of property value."""
        pct = self.settings.council_rate_estimate_pct / 100
        return round(purchase_price * pct, 2)

    def _management_fee_pct(self, strategy: DealType) -> float:
        """Property management fee varies by strategy."""
        fees = {
            DealType.BTL: 7.0,
            DealType.HMO: 10.0,
            DealType.R2SA: 15.0,    # Higher management for SA
            DealType.BRRR: 7.0,
            DealType.PLO: 5.0,
            DealType.FLIP: 0,       # No ongoing management
        }
        return fees.get(strategy, 7.0)

    def _vacancy_weeks(self, strategy: DealType) -> float:
        """Expected vacancy weeks per year by strategy."""
        vacancies = {
            DealType.BTL: 2.0,
            DealType.HMO: 3.0,
            DealType.R2SA: 0,       # Already factored into occupancy
            DealType.BRRR: 4.0,     # Vacancy during reno
            DealType.FLIP: 0,
        }
        return vacancies.get(strategy, 2.0)

    def _estimate_insurance(self, purchase_price: float, strategy: DealType) -> float:
        """Estimate annual insurance cost."""
        base = max(purchase_price * 0.002, 1200)
        if strategy == DealType.HMO:
            base *= 1.5  # Higher insurance for HMO
        elif strategy == DealType.R2SA:
            base *= 1.3
        return round(base, 2)

    def _estimate_maintenance(self, purchase_price: float, year_built: Optional[int]) -> float:
        """Estimate annual maintenance (1–2% of value, higher for older properties)."""
        base = purchase_price * 0.01
        if year_built and year_built < 1980:
            base *= 1.5
        elif year_built and year_built < 2000:
            base *= 1.2
        return round(max(base, 2000), 2)


def quick_roi(
    purchase_price: float,
    weekly_rent: float,
    interest_rate: float = 6.25,
    deposit_pct: float = 20,
) -> dict:
    """
    Quick-and-dirty ROI calculation for fast filtering.

    Returns a simple dict — use the full ROICalculator for detailed analysis.

    Returns zeros for all metrics if ``purchase_price`` or ``deposit_pct``
    are not positive, rather than producing nonsensical or misleading numbers.
    """
    if purchase_price <= 0 or deposit_pct <= 0:
        return {
            "gross_yield": 0.0,
            "net_yield": 0.0,
            "monthly_cash_flow": 0.0,
            "is_positive": False,
            "annual_net": 0.0,
        }

    annual_rent = weekly_rent * 52
    gross_yield = (annual_rent / purchase_price * 100) if purchase_price > 0 else 0

    loan_amount = purchase_price * (1 - deposit_pct / 100)
    annual_interest = loan_amount * (interest_rate / 100)
    deposit = purchase_price * (deposit_pct / 100)

    # Simple expenses estimate: interest + mgmt (7%) + council rates + insurance + maintenance
    expenses = annual_interest + (annual_rent * 0.07) + 3_000 + 1_500 + 2_000
    net_income = annual_rent - expenses
    net_yield = (net_income / deposit * 100) if deposit > 0 else 0.0
    monthly_cf = net_income / 12

    return {
        "gross_yield": round(gross_yield, 2),
        "net_yield": round(net_yield, 2),
        "monthly_cash_flow": round(monthly_cf, 2),
        "is_positive": monthly_cf > 0,
        "annual_net": round(net_income, 2),
    }
