"""
Deals API — analysis, scoring, and deal intelligence.

Wraps the Analyst agent to provide financial analysis and Bargain Score calculations
for individual properties or bulk analysis runs.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from nexusprop.models.deal import Deal, DealType, BargainScore
from nexusprop.models.property import Property
from nexusprop.config.settings import get_settings

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class AnalyzePropertyRequest(BaseModel):
    """Request to analyse a single property."""
    property_id: str = Field(..., description="ID of a stored property")
    strategy: DealType = Field(default=DealType.BTL, description="Investment strategy")
    suburb_median: Optional[float] = Field(None, ge=0, description="Suburb median for comps")
    weekly_rent_estimate: Optional[float] = Field(None, ge=0)
    renovation_cost: Optional[float] = Field(None, ge=0)


class AnalyzeUrlRequest(BaseModel):
    """Request to analyse a property directly from URL."""
    url: str = Field(..., description="Property listing URL")
    strategy: DealType = Field(default=DealType.BTL)
    suburb_median: Optional[float] = None
    weekly_rent_estimate: Optional[float] = None


class BulkAnalyzeRequest(BaseModel):
    """Run analysis on all stored properties."""
    strategy: DealType = Field(default=DealType.BTL)
    max_properties: int = Field(default=50, ge=1, le=200)
    min_bargain_score: float = Field(default=0, ge=0, le=100)


class DealResponse(BaseModel):
    """Single deal analysis response."""
    deal: Deal
    bargain_score: Optional[BargainScore] = None
    is_golden: bool = False
    recommended_strategy: Optional[str] = None


class DealListResponse(BaseModel):
    """Multiple deals response."""
    total: int
    golden_count: int
    deals: list[Deal]
    average_bargain_score: Optional[float] = None


class QuickROIResponse(BaseModel):
    """Quick ROI screening result."""
    property_id: str
    purchase_price: float
    weekly_rent: float
    gross_yield: float
    estimated_net_yield: float
    monthly_cash_flow: float
    stamp_duty: float
    verdict: str


# ---------------------------------------------------------------------------
# In-memory deal store (MVP)
# ---------------------------------------------------------------------------
_deal_store: dict[str, Deal] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=DealListResponse)
async def list_deals(
    strategy: Optional[DealType] = Query(None),
    min_score: float = Query(0, ge=0, le=100),
    golden_only: bool = Query(False),
    sort_by: str = Query("bargain_score", pattern="^(bargain_score|roi|cash_flow|price)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    List all analysed deals with filtering.

    Supports filtering by strategy, minimum bargain score,
    and golden opportunities only.
    """
    deals = list(_deal_store.values())

    if strategy:
        deals = [d for d in deals if d.deal_type == strategy]
    if min_score > 0:
        deals = [d for d in deals if d.bargain_score and d.bargain_score.overall_score >= min_score]
    if golden_only:
        threshold = get_settings().golden_opportunity_score
        deals = [d for d in deals if d.bargain_score and d.bargain_score.overall_score >= threshold]

    # Sort
    sort_funcs = {
        "bargain_score": lambda d: d.bargain_score.overall_score if d.bargain_score else 0,
        "roi": lambda d: d.cash_flow.roi if d.cash_flow else 0,
        "cash_flow": lambda d: d.cash_flow.monthly_cash_flow if d.cash_flow else 0,
        "price": lambda d: d.property.effective_price or 0,
    }
    deals.sort(key=sort_funcs.get(sort_by, sort_funcs["bargain_score"]), reverse=True)

    total = len(deals)
    golden_count = sum(
        1 for d in deals
        if d.bargain_score and d.bargain_score.overall_score >= get_settings().golden_opportunity_score
    )
    avg_score = (
        sum(d.bargain_score.overall_score for d in deals if d.bargain_score) / len(deals)
        if deals else None
    )

    paginated = deals[offset:offset + limit]

    return DealListResponse(
        total=total,
        golden_count=golden_count,
        deals=paginated,
        average_bargain_score=round(avg_score, 1) if avg_score else None,
    )


@router.get("/quick-roi", response_model=QuickROIResponse)
async def quick_roi_get(
    purchase_price: float = Query(..., ge=0, description="Purchase price AUD"),
    weekly_rent: float = Query(..., ge=0, description="Weekly rent AUD"),
    state: str = Query("NSW", description="State for stamp duty"),
):
    """Quick ROI screening via GET — instant yield and cash flow calc."""
    return await _quick_roi_calc(purchase_price, weekly_rent, state)


@router.get("/{deal_id}", response_model=Deal)
async def get_deal(deal_id: str):
    """Retrieve a single deal by ID."""
    deal = _deal_store.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.post("/analyze", response_model=DealResponse)
async def analyze_property(
    request: Request,
    body: AnalyzePropertyRequest,
):
    """
    Run the Analyst agent on a single stored property.

    Performs full financial analysis: ROI, yield, cash flow, Bargain Score,
    comparable sales analysis, and strategy recommendation.
    """
    from nexusprop.api.routes.properties import _property_store

    prop = _property_store.get(body.property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found — scout it first")

    orchestrator = request.app.state.orchestrator

    try:
        analyst_result = await orchestrator.analyst.safe_execute(
            properties=[prop],
            strategy=body.strategy,
        )

        if not analyst_result.success:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {analyst_result.error}")

        deals: list[Deal] = analyst_result.data.get("deals", [])
        if not deals:
            raise HTTPException(status_code=422, detail="No deals generated from analysis")

        deal = deals[0]
        _deal_store[str(deal.id)] = deal

        from nexusprop.db import save_deal
        save_deal(deal)

        settings = get_settings()
        is_golden = deal.bargain_score and deal.bargain_score.overall_score >= settings.golden_opportunity_score

        return DealResponse(
            deal=deal,
            bargain_score=deal.bargain_score,
            is_golden=is_golden,
            recommended_strategy=deal.deal_type.value if deal.deal_type else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("analyze_property_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-url", response_model=DealResponse)
async def analyze_from_url(
    request: Request,
    body: AnalyzeUrlRequest,
):
    """
    Analyse a property directly from a listing URL.

    Runs Scout (single URL) → Analyst → returns Deal.
    """
    orchestrator = request.app.state.orchestrator

    try:
        # Use orchestrator's single-property analysis
        result = await orchestrator.analyze_single_property(
            url=body.url,
            strategy=body.strategy,
        )

        if not result.get("deal"):
            raise HTTPException(status_code=422, detail="Could not analyse property from URL")

        deal = result["deal"]
        _deal_store[str(deal.id)] = deal

        from nexusprop.db import save_deal
        save_deal(deal)

        settings = get_settings()
        is_golden = deal.bargain_score and deal.bargain_score.overall_score >= settings.golden_opportunity_score

        return DealResponse(
            deal=deal,
            bargain_score=deal.bargain_score,
            is_golden=is_golden,
            recommended_strategy=deal.deal_type.value if deal.deal_type else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("analyze_url_failed", url=body.url, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-analyze", response_model=DealListResponse)
async def bulk_analyze(
    request: Request,
    body: BulkAnalyzeRequest,
):
    """
    Run the Analyst on all stored properties in bulk.

    Analyses up to `max_properties` from the property store and
    returns scored deals sorted by Bargain Score.
    """
    from nexusprop.api.routes.properties import _property_store

    properties = list(_property_store.values())[:body.max_properties]

    if not properties:
        return DealListResponse(total=0, golden_count=0, deals=[])

    orchestrator = request.app.state.orchestrator

    try:
        analyst_result = await orchestrator.analyst.safe_execute(
            properties=properties,
            strategy=body.strategy,
        )

        if not analyst_result.success:
            raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {analyst_result.error}")

        deals: list[Deal] = analyst_result.data.get("deals", [])

        # Filter by minimum score
        if body.min_bargain_score > 0:
            deals = [d for d in deals if d.bargain_score and d.bargain_score.overall_score >= body.min_bargain_score]

        # Store all deals
        for deal in deals:
            _deal_store[str(deal.id)] = deal

        from nexusprop.db import save_deals_bulk
        if deals:
            save_deals_bulk(deals)

        settings = get_settings()
        golden_count = sum(
            1 for d in deals
            if d.bargain_score and d.bargain_score.overall_score >= settings.golden_opportunity_score
        )

        # Sort by bargain score descending
        deals.sort(
            key=lambda d: d.bargain_score.overall_score if d.bargain_score else 0,
            reverse=True,
        )

        avg_score = (
            sum(d.bargain_score.overall_score for d in deals if d.bargain_score) / len(deals)
            if deals else None
        )

        return DealListResponse(
            total=len(deals),
            golden_count=golden_count,
            deals=deals,
            average_bargain_score=round(avg_score, 1) if avg_score else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("bulk_analyze_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-roi", response_model=QuickROIResponse)
async def quick_roi(
    purchase_price: float = Query(..., ge=0, description="Purchase price AUD"),
    weekly_rent: float = Query(..., ge=0, description="Weekly rent AUD"),
    state: str = Query("NSW", description="State for stamp duty"),
):
    """
    Quick ROI screening — no property required.

    Instant gross yield, estimated net yield, and monthly cash flow
    calculation for any price/rent combination.
    """
    return await _quick_roi_calc(purchase_price, weekly_rent, state)


async def _quick_roi_calc(purchase_price: float, weekly_rent: float, state: str) -> QuickROIResponse:
    """Shared quick-ROI calculation logic."""
    from nexusprop.config.settings import get_settings, STAMP_DUTY_BRACKETS

    settings = get_settings()

    # Calculate stamp duty for the requested state
    brackets = STAMP_DUTY_BRACKETS.get(state.upper(), STAMP_DUTY_BRACKETS.get("NSW"))
    stamp_duty = 0.0
    prev_threshold = 0.0
    for threshold, rate, base in brackets:
        if purchase_price <= prev_threshold:
            break
        taxable = min(purchase_price, threshold) - prev_threshold
        if taxable > 0:
            if base > 0 and prev_threshold == 0:
                stamp_duty = base + (purchase_price - prev_threshold) * rate
                break
            stamp_duty += taxable * rate
        prev_threshold = threshold
    stamp_duty = round(stamp_duty, 2)

    annual_rent = weekly_rent * 52
    gross_yield = (annual_rent / purchase_price * 100) if purchase_price > 0 else 0

    deposit_pct = 20.0
    deposit = purchase_price * (deposit_pct / 100)
    loan_amount = purchase_price * (1 - deposit_pct / 100)
    interest_rate = settings.default_interest_rate
    annual_interest = loan_amount * (interest_rate / 100)

    # Simple expenses estimate
    expenses = annual_interest + (annual_rent * 0.07) + 3000 + 1500 + 2000
    net_income = annual_rent - expenses
    total_cash_in = deposit + stamp_duty + 3000  # deposit + stamp + legals
    net_yield = (net_income / total_cash_in * 100) if total_cash_in > 0 else 0
    monthly_cf = net_income / 12

    verdict = "PASS"
    if gross_yield < 4.0:
        verdict = "WEAK — below 4% gross yield"
    elif gross_yield < 5.5:
        verdict = "MARGINAL — monitor closely"
    elif gross_yield >= 7.0:
        verdict = "STRONG — potential golden opportunity"

    return QuickROIResponse(
        property_id="quick-check",
        purchase_price=purchase_price,
        weekly_rent=weekly_rent,
        gross_yield=round(gross_yield, 2),
        estimated_net_yield=round(net_yield, 2),
        monthly_cash_flow=round(monthly_cf, 2),
        stamp_duty=stamp_duty,
        verdict=verdict,
    )
