"""
Negotiation Shadow API — live AI coaching during property negotiations.

Accepts negotiation context and buyer messages, returns tactical coaching
based on agent sales history and negotiation psychology.
"""

from __future__ import annotations

from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class NegotiationCoachRequest(BaseModel):
    """Request for negotiation coaching."""
    buyer_message: str = Field(..., min_length=5, max_length=5000,
                               description="What's happening right now in the negotiation.")
    agent_name: str = Field(default="Unknown Agent", max_length=200)
    agency_name: Optional[str] = Field(None, max_length=200)
    property_address: Optional[str] = Field(None, max_length=500)
    buyer_budget_max: Optional[float] = Field(None, ge=0,
                                               description="Buyer's maximum budget in AUD.")
    asking_price: Optional[float] = Field(None, ge=0)
    negotiation_history: Optional[list[dict]] = Field(None,
        description="Previous messages in this negotiation session.")


class NegotiationCoachResponse(BaseModel):
    """Coaching response from the Negotiation Shadow."""
    coaching: str = Field(..., description="Tactical coaching text for the buyer")
    detected_tactics: list[str] = Field(default_factory=list,
                                         description="Agent tactics detected in the message")
    suggested_stage: Optional[str] = Field(None,
        description="Detected negotiation stage (opening, counter, closing, stalled)")
    confidence: float = Field(default=0.0, ge=0, le=1.0)
    disclaimer: str = Field(default="NEGOTIATION STRATEGY ONLY — NOT LEGAL OR FINANCIAL ADVICE.")


class SubscriptionTiersResponse(BaseModel):
    """Available subscription tiers and pricing."""
    tiers: list[dict]
    addons: list[dict]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/coach", response_model=NegotiationCoachResponse)
async def negotiation_coach(request: NegotiationCoachRequest):
    """
    Get live negotiation coaching based on what's happening in
    your property negotiation.

    Pricing: Included with Negotiation Shadow add-on ($500/mo).
    """
    from nexusprop.agents.negotiation_shadow import NegotiationShadow

    logger.info("negotiation_coach_request",
                agent_name=request.agent_name,
                message_length=len(request.buyer_message))

    try:
        shadow = NegotiationShadow()

        # Build context dict for the agent
        context = {
            "agent_name": request.agent_name,
            "agency_name": request.agency_name or "",
            "property_address": request.property_address or "",
            "buyer_budget_max": request.buyer_budget_max,
            "asking_price": request.asking_price,
        }

        result = await shadow.execute(
            buyer_message=request.buyer_message,
            context=context,
        )

        return NegotiationCoachResponse(
            coaching=result.get("coaching", "No coaching available."),
            detected_tactics=result.get("detected_tactics", []),
            suggested_stage=result.get("stage"),
            confidence=result.get("confidence", 0.5),
        )

    except Exception as e:
        logger.error("negotiation_coach_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Negotiation coaching failed: {e}")
