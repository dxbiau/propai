"""
Comparable Sales (Comps) Engine — real-time comparable analysis.

Compares a target property against recently sold properties in the same
suburb/area to determine "Real Value" vs "Asking Value."
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import structlog

from nexusprop.models.property import Property, PropertyType

logger = structlog.get_logger(__name__)


@dataclass
class CompProperty:
    """A comparable sold property."""
    address: str
    suburb: str
    sold_price: float
    sold_date: datetime
    bedrooms: int
    bathrooms: int
    car_spaces: int
    land_size_sqm: Optional[float]
    building_size_sqm: Optional[float]
    property_type: PropertyType
    days_on_market: Optional[int] = None
    source_url: Optional[str] = None


@dataclass
class CompAnalysis:
    """Results of a comparable sales analysis."""
    target_address: str
    target_asking_price: float
    estimated_market_value: float
    comps_median: float
    comps_average: float
    price_per_sqm_median: Optional[float]
    asking_vs_value_pct: float  # Positive = overpriced, Negative = underpriced
    is_underquoted: bool
    is_overpriced: bool
    num_comps: int
    comps: list[CompProperty]
    confidence: float  # 0-1, based on comp quality
    summary: str
    detailed_analysis: str


class CompsEngine:
    """
    Comparable Sales Analysis Engine.

    Finds and analyzes recently sold properties to determine the real
    market value of a target property, cutting through agent BS.
    """

    def __init__(
        self,
        max_radius_km: float = 2.0,
        max_age_months: int = 6,
    ):
        self.max_radius_km = max_radius_km
        self.max_age_months = max_age_months

    def analyze(
        self,
        target: Property,
        sold_properties: list[Property],
    ) -> CompAnalysis:
        """
        Analyze comparable sales for a target property.

        Args:
            target: The property being analyzed
            sold_properties: List of recently sold properties in the area
        """
        asking = target.effective_price or 0

        # Filter and score comps
        comps = self._find_best_comps(target, sold_properties)

        if not comps:
            return CompAnalysis(
                target_address=target.address,
                target_asking_price=asking,
                estimated_market_value=asking,
                comps_median=0,
                comps_average=0,
                price_per_sqm_median=None,
                asking_vs_value_pct=0,
                is_underquoted=False,
                is_overpriced=False,
                num_comps=0,
                comps=[],
                confidence=0,
                summary="Insufficient comparable sales data.",
                detailed_analysis="No comparable sales found in the area.",
            )

        # Calculate stats
        prices = [c.sold_price for c in comps]
        prices.sort()

        median_price = self._median(prices)
        avg_price = sum(prices) / len(prices)

        # Price per sqm
        sqm_prices = []
        for c in comps:
            if c.land_size_sqm and c.land_size_sqm > 0:
                sqm_prices.append(c.sold_price / c.land_size_sqm)
        price_per_sqm = self._median(sqm_prices) if sqm_prices else None

        # Estimated value — weighted median
        estimated_value = median_price

        # Compare asking vs estimated
        if estimated_value > 0:
            asking_vs_value = ((asking - estimated_value) / estimated_value) * 100
        else:
            asking_vs_value = 0

        is_underquoted = asking_vs_value < -5  # Asking 5%+ below comps
        is_overpriced = asking_vs_value > 10   # Asking 10%+ above comps

        # Confidence based on number and quality of comps
        confidence = min(len(comps) / 10, 1.0)

        # Generate summary
        summary = self._generate_summary(
            target, asking, estimated_value, asking_vs_value,
            is_underquoted, is_overpriced, len(comps)
        )

        detailed = self._generate_detailed(target, comps, estimated_value, price_per_sqm)

        return CompAnalysis(
            target_address=target.address,
            target_asking_price=asking,
            estimated_market_value=round(estimated_value, 0),
            comps_median=round(median_price, 0),
            comps_average=round(avg_price, 0),
            price_per_sqm_median=round(price_per_sqm, 0) if price_per_sqm else None,
            asking_vs_value_pct=round(asking_vs_value, 1),
            is_underquoted=is_underquoted,
            is_overpriced=is_overpriced,
            num_comps=len(comps),
            comps=comps,
            confidence=round(confidence, 2),
            summary=summary,
            detailed_analysis=detailed,
        )

    def _find_best_comps(
        self,
        target: Property,
        sold_properties: list[Property],
    ) -> list[CompProperty]:
        """Find and rank the best comparable properties."""
        cutoff = datetime.utcnow() - timedelta(days=self.max_age_months * 30)
        comps = []

        for sp in sold_properties:
            if not sp.sold_price or not sp.sold_date:
                continue
            if sp.sold_date < cutoff:
                continue

            # Similarity scoring
            similarity = self._similarity_score(target, sp)
            if similarity < 0.3:
                continue

            comps.append(CompProperty(
                address=sp.address,
                suburb=sp.suburb,
                sold_price=sp.sold_price,
                sold_date=sp.sold_date,
                bedrooms=sp.bedrooms or 0,
                bathrooms=sp.bathrooms or 0,
                car_spaces=sp.car_spaces or 0,
                land_size_sqm=sp.land_size_sqm,
                building_size_sqm=sp.building_size_sqm,
                property_type=sp.property_type,
                source_url=sp.source_url,
            ))

        # Sort by similarity (recency + bedroom match + type match)
        comps.sort(key=lambda c: c.sold_date, reverse=True)
        return comps[:15]  # Top 15 comps

    def _similarity_score(self, target: Property, comp: Property) -> float:
        """Score 0–1 how similar the comp is to the target."""
        score = 0.0
        max_score = 0.0

        # Same suburb (mandatory for high score)
        max_score += 30
        if comp.suburb.lower() == target.suburb.lower():
            score += 30
        elif comp.postcode == target.postcode:
            score += 15

        # Same property type
        max_score += 20
        if comp.property_type == target.property_type:
            score += 20

        # Bedroom match
        max_score += 20
        if target.bedrooms and comp.bedrooms:
            diff = abs(target.bedrooms - comp.bedrooms)
            if diff == 0:
                score += 20
            elif diff == 1:
                score += 10
            elif diff == 2:
                score += 3

        # Land size match (within 30%)
        max_score += 15
        if target.land_size_sqm and comp.land_size_sqm:
            ratio = min(target.land_size_sqm, comp.land_size_sqm) / max(target.land_size_sqm, comp.land_size_sqm)
            score += ratio * 15

        # Recency bonus
        max_score += 15
        if comp.sold_date:
            days_ago = (datetime.utcnow() - comp.sold_date).days
            if days_ago < 30:
                score += 15
            elif days_ago < 90:
                score += 10
            elif days_ago < 180:
                score += 5

        return score / max_score if max_score > 0 else 0

    @staticmethod
    def _median(values: list[float]) -> float:
        if not values:
            return 0
        s = sorted(values)
        n = len(s)
        mid = n // 2
        if n % 2 == 0:
            return (s[mid - 1] + s[mid]) / 2
        else:
            return s[mid]

    def _generate_summary(
        self,
        target: Property,
        asking: float,
        estimated: float,
        diff_pct: float,
        is_underquoted: bool,
        is_overpriced: bool,
        num_comps: int,
    ) -> str:
        """Generate a human-readable comp summary."""
        addr = target.address

        if is_underquoted:
            return (
                f"⚠️ UNDERQUOTED: {addr} is listed at ${asking:,.0f} but comparable sales "
                f"suggest a value of ${estimated:,.0f} ({abs(diff_pct):.1f}% below comps). "
                f"Expect competition — this is likely a bait price strategy. "
                f"Based on {num_comps} comparable sales."
            )
        elif is_overpriced:
            return (
                f"🔴 OVERPRICED: {addr} is listed at ${asking:,.0f} but comparable sales "
                f"suggest a value of ${estimated:,.0f} ({diff_pct:.1f}% above comps). "
                f"Room for negotiation. Based on {num_comps} comparable sales."
            )
        else:
            return (
                f"✅ FAIRLY PRICED: {addr} at ${asking:,.0f} is in line with comparable "
                f"sales (median ${estimated:,.0f}, {diff_pct:+.1f}%). "
                f"Based on {num_comps} comparable sales."
            )

    def _generate_detailed(
        self,
        target: Property,
        comps: list[CompProperty],
        estimated: float,
        price_per_sqm: Optional[float],
    ) -> str:
        """Generate a detailed comparable sales analysis."""
        lines = [
            f"COMPARABLE SALES ANALYSIS — {target.address}",
            f"{'=' * 60}",
            f"Target: {target.bedrooms or '?'}BR {target.property_type.value} | "
            f"Asking: ${target.effective_price or 0:,.0f} | "
            f"Estimated Value: ${estimated:,.0f}",
        ]

        if price_per_sqm:
            lines.append(f"Median price/m²: ${price_per_sqm:,.0f}")

        lines.append(f"\n{'─' * 60}")
        lines.append(f"{'Address':<35} {'Sold Price':>12} {'Date':>12} {'BR':>4}")
        lines.append(f"{'─' * 60}")

        for c in comps[:10]:
            addr = c.address[:33]
            lines.append(
                f"{addr:<35} ${c.sold_price:>10,.0f} "
                f"{c.sold_date.strftime('%d/%m/%Y'):>12} "
                f"{c.bedrooms:>4}"
            )

        lines.append(f"{'─' * 60}")
        return "\n".join(lines)
