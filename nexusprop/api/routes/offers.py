"""
Offers API — AI-powered offer generation and negotiation strategy.

Wraps the Closer agent to produce persuasive, legally-safe commercial
strategy drafts for property offers.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from nexusprop.models.offer import (
    OfferDocument,
    OfferGenerationRequest,
    OfferTone,
    SellerMotivation,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class GenerateOfferRequest(BaseModel):
    """API request to generate an offer."""
    deal_id: str = Field(..., description="ID of an analysed deal")
    buyer_name: str = Field(..., description="Full legal name of buyer")
    buyer_entity: Optional[str] = Field(None, description="Company/trust name")
    buyer_budget_max: float = Field(..., ge=0)
    buyer_story: Optional[str] = Field(None, description="Personal story for empathetic tone")
    tone: OfferTone = Field(default=OfferTone.PROFESSIONAL)
    motivation_override: Optional[SellerMotivation] = None
    offer_price_override: Optional[float] = Field(None, ge=0)
    settlement_days: int = Field(default=42, ge=14, le=180)
    include_conditions: bool = True


class GenerateOfferFromUrlRequest(BaseModel):
    """Generate an offer for a property from URL (one-shot pipeline)."""
    url: str = Field(..., description="Property listing URL")
    buyer_name: str
    buyer_entity: Optional[str] = None
    buyer_budget_max: float = Field(..., ge=0)
    buyer_story: Optional[str] = None
    tone: OfferTone = Field(default=OfferTone.PROFESSIONAL)
    settlement_days: int = Field(default=42, ge=14, le=180)


class CounterOfferRequest(BaseModel):
    """Request to generate a counter-offer strategy."""
    original_offer_id: str
    seller_counter_price: float = Field(..., ge=0)
    seller_counter_conditions: Optional[str] = None
    buyer_max_budget: float = Field(..., ge=0)
    additional_context: Optional[str] = None


class OfferResponse(BaseModel):
    """Generated offer response."""
    offer: OfferDocument
    ai_enhanced: bool = False
    suggested_price: float
    discount_from_asking_pct: Optional[float] = None


class CounterOfferResponse(BaseModel):
    """Counter-offer strategy response."""
    original_offer_price: float
    seller_counter: float
    recommended_response_price: float
    strategy: str
    talking_points: list[str]
    walk_away_recommended: bool


# ---------------------------------------------------------------------------
# In-memory offer store (MVP)
# ---------------------------------------------------------------------------
_offer_store: dict[str, OfferDocument] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/")
async def list_offers(
    limit: int = 50,
    offset: int = 0,
):
    """List all generated offers."""
    offers = list(_offer_store.values())
    offers.sort(key=lambda o: o.created_at, reverse=True)
    total = len(offers)
    paginated = offers[offset:offset + limit]
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "offers": [o.model_dump(mode="json") for o in paginated],
    }


@router.get("/{offer_id}")
async def get_offer(offer_id: str):
    """Retrieve a single generated offer."""
    offer = _offer_store.get(offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer.model_dump(mode="json")


@router.post("/generate", response_model=OfferResponse)
async def generate_offer(
    request: Request,
    body: GenerateOfferRequest,
):
    """
    Generate a persuasive offer document for an analysed deal.

    Uses the Closer agent with Cialdini's 6 Principles of Persuasion
    to craft buyer-advantage offer letters with legal safety guardrails.
    """
    from nexusprop.api.routes.deals import _deal_store

    deal = _deal_store.get(body.deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found — analyse the property first")

    orchestrator = request.app.state.orchestrator
    asking_price = deal.property.effective_price or 0

    offer_request = OfferGenerationRequest(
        property_id=deal.property.id,
        property_address=deal.property.address,
        asking_price=asking_price,
        buyer_name=body.buyer_name,
        buyer_entity=body.buyer_entity,
        buyer_budget_max=body.buyer_budget_max,
        buyer_story=body.buyer_story,
        seller_motivation=body.motivation_override or SellerMotivation.UNKNOWN,
        preferred_tone=body.tone,
        include_conditions=body.include_conditions,
        offer_price_override=body.offer_price_override,
        settlement_days=body.settlement_days,
    )

    try:
        closer_result = await orchestrator.closer.safe_execute(
            request=offer_request,
            deal=deal,
        )

        if not closer_result.success:
            raise HTTPException(status_code=500, detail=f"Offer generation failed: {closer_result.error}")

        offer: OfferDocument = closer_result.data.get("offer")
        if not offer:
            raise HTTPException(status_code=422, detail="No offer generated")

        _offer_store[str(offer.id)] = offer

        from nexusprop.db import save_offer
        save_offer(offer)

        discount_pct = None
        if asking_price > 0:
            discount_pct = round(((asking_price - offer.offer_price) / asking_price) * 100, 1)

        return OfferResponse(
            offer=offer,
            ai_enhanced=closer_result.data.get("ai_enhanced", False),
            suggested_price=offer.offer_price,
            discount_from_asking_pct=discount_pct,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("offer_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/counter-strategy", response_model=CounterOfferResponse)
async def counter_offer_strategy(
    request: Request,
    body: CounterOfferRequest,
):
    """
    Generate a counter-offer strategy when the seller responds.

    Analyses the seller's counter against your budget and deal analysis
    to recommend a response strategy.
    """
    original = _offer_store.get(body.original_offer_id)
    if not original:
        raise HTTPException(status_code=404, detail="Original offer not found")

    orchestrator = request.app.state.orchestrator

    try:
        from nexusprop.tools.offer_writer import OfferWriter
        writer = OfferWriter()

        strategy = writer.generate_counter_strategy(
            original_offer=original.offer_price,
            seller_counter=body.seller_counter_price,
            buyer_max=body.buyer_max_budget,
            walk_away_price=original.walk_away_price,
        )

        # Calculate recommended response
        gap = body.seller_counter_price - original.offer_price
        response_price = original.offer_price + (gap * 0.4)  # Move 40% towards seller
        walk_away = response_price > body.buyer_max_budget

        if walk_away:
            response_price = body.buyer_max_budget

        return CounterOfferResponse(
            original_offer_price=original.offer_price,
            seller_counter=body.seller_counter_price,
            recommended_response_price=round(response_price, 0),
            strategy=strategy.get("strategy", "Hold firm and re-present with stronger justification"),
            talking_points=strategy.get("talking_points", [
                "Reference comparable sales to justify your position",
                "Highlight any property defects discovered in inspection",
                "Offer faster settlement as a concession instead of higher price",
            ]),
            walk_away_recommended=walk_away,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("counter_strategy_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{offer_id}")
async def delete_offer(offer_id: str):
    """Delete a generated offer."""
    if offer_id not in _offer_store:
        raise HTTPException(status_code=404, detail="Offer not found")
    del _offer_store[offer_id]

    from nexusprop.db import delete_offer as db_delete_offer
    db_delete_offer(offer_id)

    return {"status": "deleted", "offer_id": offer_id}
