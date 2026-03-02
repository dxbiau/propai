"""
Suburb profile model — intelligence layer for suburb-level analysis.

Stores historical data, growth metrics, and sentiment for RAG-powered comparisons.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GrowthMetrics(BaseModel):
    """Historical growth data for a suburb."""
    median_house_price: Optional[float] = None
    median_unit_price: Optional[float] = None
    median_weekly_rent_house: Optional[float] = None
    median_weekly_rent_unit: Optional[float] = None
    annual_growth_pct_house: Optional[float] = None
    annual_growth_pct_unit: Optional[float] = None
    five_year_growth_pct: Optional[float] = None
    ten_year_growth_pct: Optional[float] = None
    gross_rental_yield_house: Optional[float] = None
    gross_rental_yield_unit: Optional[float] = None
    days_on_market_avg: Optional[int] = None
    auction_clearance_rate: Optional[float] = Field(None, ge=0, le=100)
    total_listings_current: Optional[int] = None
    total_sales_last_12m: Optional[int] = None


class DemographicSnapshot(BaseModel):
    """Key demographic indicators."""
    population: Optional[int] = None
    median_household_income: Optional[float] = None
    owner_occupied_pct: Optional[float] = None
    renter_pct: Optional[float] = None
    median_age: Optional[float] = None
    family_households_pct: Optional[float] = None


class InfrastructurePipeline(BaseModel):
    """Upcoming infrastructure that may affect property values."""
    project_name: str
    description: str
    estimated_completion: Optional[str] = None
    distance_km: Optional[float] = None
    impact_score: float = Field(ge=-10, le=10, description="Negative = bad, Positive = good")


class SuburbProfile(BaseModel):
    """Comprehensive suburb-level intelligence for deal analysis."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Identity ---
    suburb_name: str = Field(..., description="Suburb name")
    state: str = Field(..., description="State/territory")
    postcode: str = Field(..., pattern=r"^\d{4}$")
    lga: Optional[str] = Field(None, description="Local Government Area")

    # --- Metrics ---
    growth: GrowthMetrics = Field(default_factory=GrowthMetrics)
    demographics: DemographicSnapshot = Field(default_factory=DemographicSnapshot)

    # --- Infrastructure ---
    infrastructure_pipeline: list[InfrastructurePipeline] = Field(default_factory=list)

    # --- School Catchment ---
    top_schools: list[str] = Field(default_factory=list, description="Nearby high-ranking schools")
    school_catchment_premium_pct: Optional[float] = Field(
        None, description="% premium properties get for being in a top school zone"
    )

    # --- Transport ---
    train_station_km: Optional[float] = None
    bus_routes_nearby: Optional[int] = None
    cbd_distance_km: Optional[float] = None

    # --- Sentiment ---
    community_sentiment_score: Optional[float] = Field(
        None, ge=-1, le=1, description="NLP sentiment from community sources"
    )
    gentrification_index: Optional[float] = Field(
        None, ge=0, le=100, description="0=stable, 100=rapid gentrification"
    )

    # --- Supply / Demand ---
    vacancy_rate_pct: Optional[float] = Field(None, ge=0, le=100)
    development_applications_active: Optional[int] = Field(
        None, description="Number of active DAs in the suburb"
    )
    new_supply_pipeline_units: Optional[int] = Field(
        None, description="Upcoming new dwellings (apartments/houses)"
    )

    # --- Embedding for RAG ---
    embedding_text: Optional[str] = Field(
        None, exclude=True,
        description="Concatenated text representation for vector embedding"
    )

    @property
    def investment_attractiveness_score(self) -> float:
        """
        Simple heuristic: higher yield + growth + low vacancy = attractive.
        Score 0–100.
        """
        score = 50.0  # Baseline

        # Yield contribution (up to +20)
        gy = self.growth.gross_rental_yield_house or 0
        score += min(gy * 4, 20)

        # Growth contribution (up to +20)
        ag = self.growth.annual_growth_pct_house or 0
        score += min(ag * 2, 20)

        # Low vacancy bonus (up to +10)
        vr = self.vacancy_rate_pct
        if vr is not None and vr < 2:
            score += 10
        elif vr is not None and vr < 3:
            score += 5

        # Infrastructure bonus
        score += min(len(self.infrastructure_pipeline) * 3, 10)

        return min(round(score, 1), 100.0)

    def build_embedding_text(self) -> str:
        """Build a text blob for vector embedding."""
        parts = [
            f"Suburb: {self.suburb_name}, {self.state} {self.postcode}",
            f"LGA: {self.lga or 'Unknown'}",
        ]
        if self.growth.median_house_price:
            parts.append(f"Median house price: ${self.growth.median_house_price:,.0f}")
        if self.growth.annual_growth_pct_house:
            parts.append(f"Annual growth: {self.growth.annual_growth_pct_house}%")
        if self.growth.gross_rental_yield_house:
            parts.append(f"Gross yield: {self.growth.gross_rental_yield_house}%")
        if self.growth.days_on_market_avg:
            parts.append(f"Avg days on market: {self.growth.days_on_market_avg}")
        if self.vacancy_rate_pct is not None:
            parts.append(f"Vacancy rate: {self.vacancy_rate_pct}%")
        if self.cbd_distance_km:
            parts.append(f"CBD distance: {self.cbd_distance_km}km")
        if self.infrastructure_pipeline:
            projects = ", ".join(p.project_name for p in self.infrastructure_pipeline)
            parts.append(f"Infrastructure: {projects}")

        text = ". ".join(parts)
        self.embedding_text = text
        return text
