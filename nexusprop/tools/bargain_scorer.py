"""
Bargain Scorer — the proprietary "Cream" filter.

Calculates the Bargain Score™ for a property by comparing it against
suburb-level data, distress signals, and market conditions.
"""

from __future__ import annotations

from typing import Optional

import structlog

from nexusprop.models.deal import BargainScore, DealType
from nexusprop.models.property import Property, PropertyCondition
from nexusprop.models.suburb import SuburbProfile

logger = structlog.get_logger(__name__)


# Condition adjustment factors (-20 to +10)
CONDITION_ADJUSTMENTS = {
    PropertyCondition.KNOCKDOWN_REBUILD: -20,
    PropertyCondition.RENOVATION_REQUIRED: -10,
    PropertyCondition.UNKNOWN: 0,
    PropertyCondition.FAIR: 0,
    PropertyCondition.GOOD: 5,
    PropertyCondition.EXCELLENT: 10,
}


class BargainScorer:
    """
    Calculates the Bargain Score™ — the single number that tells you
    whether a property is a deal or a trap.

    The score aggregates:
    1. Price Deviation — How far below suburb median
    2. Distress Delta — Adjusted for condition and motivation
    3. Cash Flow Potential — Yield attractiveness
    4. Market Timing — Where we are in the cycle
    5. Days on Market — Staleness signal
    """

    def __init__(self, golden_threshold: float = 85.0):
        self.golden_threshold = golden_threshold

    def score(
        self,
        prop: Property,
        suburb: SuburbProfile,
        net_yield: float = 0,
        days_on_market: Optional[int] = None,
    ) -> BargainScore:
        """
        Calculate the full Bargain Score™ for a property.

        Args:
            prop: The property to score
            suburb: Suburb-level data for comparison
            net_yield: Calculated net yield % from ROI calculator
            days_on_market: How long the listing has been active
        """
        asking_price = prop.effective_price or 0

        # Get suburb median for this property type
        if prop.property_type.value in ("unit", "apartment"):
            suburb_median = suburb.growth.median_unit_price or 0
        else:
            suburb_median = suburb.growth.median_house_price or 0

        # Condition adjustment
        condition_factor = CONDITION_ADJUSTMENTS.get(prop.condition, 0)

        # Market growth
        market_growth = suburb.growth.annual_growth_pct_house or 0

        # Distress score from the property
        distress_score = prop.distress_score

        return BargainScore.calculate(
            asking_price=asking_price,
            suburb_median=suburb_median,
            net_yield=net_yield,
            distress_score=distress_score,
            days_on_market=days_on_market,
            condition_factor=condition_factor,
            market_growth_pct=market_growth,
            golden_threshold=self.golden_threshold,
        )

    def rank_properties(
        self,
        properties: list[tuple[Property, SuburbProfile, float]],
        min_score: float = 0,
    ) -> list[tuple[Property, BargainScore]]:
        """
        Rank a list of properties by Bargain Score.

        Args:
            properties: List of (Property, SuburbProfile, net_yield) tuples
            min_score: Minimum score to include
        """
        scored = []
        for prop, suburb, net_yield in properties:
            bs = self.score(prop, suburb, net_yield)
            if bs.overall_score >= min_score:
                scored.append((prop, bs))

        # Sort descending by score
        scored.sort(key=lambda x: x[1].overall_score, reverse=True)
        return scored

    def find_golden_opportunities(
        self,
        properties: list[tuple[Property, SuburbProfile, float]],
    ) -> list[tuple[Property, BargainScore]]:
        """Find only Golden Opportunity properties (score >= threshold)."""
        return self.rank_properties(properties, min_score=self.golden_threshold)

    def recommend_strategy(
        self,
        prop: Property,
        suburb: SuburbProfile,
        bargain_score: BargainScore,
    ) -> list[DealType]:
        """
        Recommend investment strategies based on the property and market.

        Returns ordered list of recommended strategies.
        """
        strategies = []

        gross_yield = suburb.growth.gross_rental_yield_house or 0
        vacancy = suburb.vacancy_rate_pct or 5

        # BTL — good for stable areas with decent yield
        if gross_yield >= 4.0 and vacancy < 3:
            strategies.append(DealType.BTL)

        # R2SA — good in tourist or CBD areas with short-term demand
        if suburb.cbd_distance_km and suburb.cbd_distance_km < 10:
            strategies.append(DealType.R2SA)

        # BRRR — good for renovation-required properties below median
        if prop.condition in (PropertyCondition.RENOVATION_REQUIRED, PropertyCondition.FAIR):
            if bargain_score.distress_delta > 10:
                strategies.append(DealType.BRRR)

        # HMO — good for large houses near universities/hospitals
        if prop.bedrooms and prop.bedrooms >= 4:
            strategies.append(DealType.HMO)

        # Flip — high distress delta + renovation potential
        if bargain_score.distress_delta > 15 and prop.condition == PropertyCondition.RENOVATION_REQUIRED:
            strategies.append(DealType.FLIP)

        # Subdivision — large land + appropriate zoning
        if prop.land_size_sqm and prop.land_size_sqm > 700 and prop.zoning in ("R2", "R3", "R4"):
            strategies.append(DealType.SUBDIVISION)

        # PLO — good when cash-flow is marginal but growth is strong
        growth = suburb.growth.annual_growth_pct_house or 0
        if growth > 5 and gross_yield < 3.5:
            strategies.append(DealType.PLO)

        # If nothing specific, default to BTL
        if not strategies:
            strategies.append(DealType.BTL)

        return strategies
