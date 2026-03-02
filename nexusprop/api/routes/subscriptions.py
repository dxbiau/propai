"""
Subscription API — pricing tiers, features, and usage tracking.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter
from pydantic import BaseModel, Field

from nexusprop.models.subscription import (
    SubscriptionTier,
    AddOn,
    TIER_FEATURES,
    ADDON_PRICING,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class TierInfo(BaseModel):
    name: str
    slug: str
    price_display: str
    features: dict


class AddonInfo(BaseModel):
    name: str
    slug: str
    price_display: str
    description: str


class SubscriptionTiersResponse(BaseModel):
    tiers: list[TierInfo]
    addons: list[AddonInfo]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

TIER_PRICING_DISPLAY = {
    SubscriptionTier.EXPLORER: "Free",
    SubscriptionTier.INVESTOR: "$199/month",
    SubscriptionTier.PRO_SOURCER: "$499/month",
    SubscriptionTier.THE_CLOSER: "$2,500/deal",
}

ADDON_DISPLAY = {
    AddOn.DUE_DILIGENCE_BOT: {
        "price_display": "$99/report",
        "description": "AI-powered Section 32 & Contract of Sale red-flag analysis.",
    },
    AddOn.NEGOTIATION_SHADOW: {
        "price_display": "$500/month",
        "description": "Live WhatsApp-style negotiation coaching with agent profiling.",
    },
    AddOn.FIRST_LOOK_PREMIUM: {
        "price_display": "$49/month",
        "description": "24-hour early access to new listings before general release.",
    },
}


@router.get("/tiers", response_model=SubscriptionTiersResponse)
async def get_subscription_tiers():
    """Return all available subscription tiers, features, and add-on pricing."""
    tiers = []
    for tier in SubscriptionTier:
        tiers.append(TierInfo(
            name=tier.value.replace("_", " ").title(),
            slug=tier.value,
            price_display=TIER_PRICING_DISPLAY[tier],
            features=TIER_FEATURES.get(tier, {}),
        ))

    addons = []
    for addon in AddOn:
        info = ADDON_DISPLAY.get(addon, {})
        addons.append(AddonInfo(
            name=addon.value.replace("_", " ").title(),
            slug=addon.value,
            price_display=info.get("price_display", "Contact us"),
            description=info.get("description", ""),
        ))

    return SubscriptionTiersResponse(tiers=tiers, addons=addons)
