"""
Subscription & Pricing Tiers — Australian Property Associates.

Defines the 4-tier pricing model plus premium add-ons:
  • Explorer (Free)       — Basic suburb data, 3 views/day
  • Investor ($199/mo)    — Full agent stack, 50 analyses/mo
  • Pro Sourcer ($499/mo) — Unlimited, First Look Premium, bulk pipeline
  • The Closer ($2,500/deal) — White-glove, full pipeline + negotiation coaching

Add-Ons:
  • Due Diligence Bot — $99/report
  • Negotiation Shadow — $500/mo
  • First Look Premium — included in Pro Sourcer+
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SubscriptionTier(str, Enum):
    """Pricing tiers for Australian Property Associates."""
    EXPLORER = "explorer"           # Free
    INVESTOR = "investor"           # $199/mo
    PRO_SOURCER = "pro_sourcer"     # $499/mo
    THE_CLOSER = "the_closer"       # $2,500/deal


class AddOn(str, Enum):
    """Premium add-on products."""
    DUE_DILIGENCE_BOT = "due_diligence_bot"       # $99/report
    NEGOTIATION_SHADOW = "negotiation_shadow"       # $500/mo
    FIRST_LOOK_PREMIUM = "first_look_premium"       # Included in Pro Sourcer+


# ── Tier Feature Definitions ──────────────────────────────────────────────

TIER_FEATURES: dict[SubscriptionTier, dict] = {
    SubscriptionTier.EXPLORER: {
        "name": "Explorer",
        "price_aud_monthly": 0,
        "price_display": "Free",
        "analyses_per_month": 3,
        "property_views_per_day": 3,
        "shadow_listings": False,
        "first_look_premium": False,
        "bulk_pipeline": False,
        "offer_generation": False,
        "whatsapp_alerts": False,
        "email_alerts": True,
        "due_diligence_bot": False,
        "negotiation_shadow": False,
        "api_access": False,
        "dedicated_support": False,
        "description": "Get your feet wet — basic suburb data & public comps",
        "features": [
            "3 property views per day",
            "Basic suburb statistics",
            "Public comparable sales",
            "Email-only alerts",
        ],
    },
    SubscriptionTier.INVESTOR: {
        "name": "Investor",
        "price_aud_monthly": 199,
        "price_display": "$199/mo",
        "analyses_per_month": 50,
        "property_views_per_day": -1,  # unlimited
        "shadow_listings": True,
        "first_look_premium": False,
        "bulk_pipeline": False,
        "offer_generation": True,
        "whatsapp_alerts": False,
        "email_alerts": True,
        "due_diligence_bot": False,  # available as add-on
        "negotiation_shadow": False,  # available as add-on
        "api_access": False,
        "dedicated_support": False,
        "description": "Serious investors — full agent stack & financial analysis",
        "features": [
            "50 property analyses per month",
            "Unlimited property views",
            "Shadow Listings from 40+ agencies",
            "Full ROI & cash-flow models",
            "Bargain Score™ ranking",
            "Offer document generation",
            "Email alerts",
            "Due Diligence Bot available ($99/report)",
        ],
    },
    SubscriptionTier.PRO_SOURCER: {
        "name": "Pro Sourcer",
        "price_aud_monthly": 499,
        "price_display": "$499/mo",
        "analyses_per_month": -1,  # unlimited
        "property_views_per_day": -1,
        "shadow_listings": True,
        "first_look_premium": True,
        "bulk_pipeline": True,
        "offer_generation": True,
        "whatsapp_alerts": True,
        "email_alerts": True,
        "due_diligence_bot": True,  # 5 reports/mo included
        "negotiation_shadow": False,  # available as add-on
        "api_access": True,
        "dedicated_support": False,
        "description": "Professional sourcing — unlimited pipeline access",
        "features": [
            "Unlimited property analyses",
            "First Look Premium (15-min head start)",
            "Bulk pipeline runs",
            "WhatsApp + SMS + Email alerts",
            "5 Due Diligence reports/mo included",
            "Investment-grade CAGR & land-to-asset analysis",
            "API access for integrations",
            "Negotiation Shadow available ($500/mo)",
        ],
    },
    SubscriptionTier.THE_CLOSER: {
        "name": "The Closer",
        "price_aud_monthly": 0,  # per-deal pricing
        "price_per_deal": 2500,
        "price_display": "$2,500/deal",
        "analyses_per_month": -1,
        "property_views_per_day": -1,
        "shadow_listings": True,
        "first_look_premium": True,
        "bulk_pipeline": True,
        "offer_generation": True,
        "whatsapp_alerts": True,
        "email_alerts": True,
        "due_diligence_bot": True,  # unlimited
        "negotiation_shadow": True,  # included
        "api_access": True,
        "dedicated_support": True,
        "description": "White-glove — full pipeline, negotiation coaching, done-for-you",
        "features": [
            "Everything in Pro Sourcer",
            "Unlimited Due Diligence reports",
            "Negotiation Shadow (WhatsApp coaching) included",
            "Dedicated account manager",
            "Priority pipeline processing",
            "Custom strategy sessions",
            "Post-acquisition support",
        ],
    },
}


ADDON_PRICING: dict[AddOn, dict] = {
    AddOn.DUE_DILIGENCE_BOT: {
        "name": "Due Diligence Bot",
        "price_display": "$99/report",
        "price_aud": 99,
        "billing": "per_report",
        "description": (
            "AI-powered Section 32 & Contract of Sale analysis. "
            "Flags restrictive covenants, easements, special levies, "
            "encumbrances, and 30+ red-flag categories in minutes."
        ),
        "available_tiers": [
            SubscriptionTier.INVESTOR,
            SubscriptionTier.PRO_SOURCER,
            SubscriptionTier.THE_CLOSER,
        ],
    },
    AddOn.NEGOTIATION_SHADOW: {
        "name": "Negotiation Shadow",
        "price_display": "$500/mo",
        "price_aud": 500,
        "billing": "monthly",
        "description": (
            "Real-time WhatsApp coaching during negotiations. "
            "Powered by agent sales history, comparable outcomes, "
            "and behavioral analysis of the selling agent's patterns."
        ),
        "available_tiers": [
            SubscriptionTier.PRO_SOURCER,
            SubscriptionTier.THE_CLOSER,
        ],
    },
    AddOn.FIRST_LOOK_PREMIUM: {
        "name": "First Look Premium",
        "price_display": "Included in Pro Sourcer+",
        "price_aud": 0,
        "billing": "included",
        "description": (
            "15-minute head start on new listings before they hit "
            "the general feed. See shadow listings first."
        ),
        "available_tiers": [
            SubscriptionTier.PRO_SOURCER,
            SubscriptionTier.THE_CLOSER,
        ],
    },
}


class Subscription(BaseModel):
    """A user's active subscription state."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    tier: SubscriptionTier = SubscriptionTier.EXPLORER
    active_addons: list[AddOn] = Field(default_factory=list)

    # Usage tracking
    analyses_used_this_month: int = Field(default=0, ge=0)
    dd_reports_used_this_month: int = Field(default=0, ge=0)
    property_views_today: int = Field(default=0, ge=0)

    # Billing
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def tier_config(self) -> dict:
        """Get the feature configuration for this subscription tier."""
        return TIER_FEATURES[self.tier]

    @property
    def analyses_remaining(self) -> int:
        """How many analyses remain this month. -1 = unlimited."""
        limit = self.tier_config["analyses_per_month"]
        if limit == -1:
            return -1
        return max(0, limit - self.analyses_used_this_month)

    @property
    def can_analyze(self) -> bool:
        """Whether the user can run another analysis."""
        remaining = self.analyses_remaining
        return remaining == -1 or remaining > 0

    @property
    def can_view_property(self) -> bool:
        """Whether the user can view another property today."""
        limit = self.tier_config["property_views_per_day"]
        return limit == -1 or self.property_views_today < limit

    @property
    def has_shadow_listings(self) -> bool:
        return self.tier_config["shadow_listings"]

    @property
    def has_first_look(self) -> bool:
        return self.tier_config["first_look_premium"]

    @property
    def has_due_diligence(self) -> bool:
        if self.tier_config["due_diligence_bot"]:
            return True
        return AddOn.DUE_DILIGENCE_BOT in self.active_addons

    @property
    def has_negotiation_shadow(self) -> bool:
        if self.tier_config["negotiation_shadow"]:
            return True
        return AddOn.NEGOTIATION_SHADOW in self.active_addons

    @property
    def has_offer_generation(self) -> bool:
        return self.tier_config["offer_generation"]

    @property
    def has_whatsapp_alerts(self) -> bool:
        return self.tier_config["whatsapp_alerts"]

    @property
    def has_bulk_pipeline(self) -> bool:
        return self.tier_config["bulk_pipeline"]

    @property
    def has_api_access(self) -> bool:
        return self.tier_config["api_access"]

    def check_feature(self, feature: str) -> bool:
        """Check if a specific feature is available for this subscription."""
        config = self.tier_config
        return config.get(feature, False)

    def record_analysis(self) -> bool:
        """Record an analysis usage. Returns True if allowed, False if over limit."""
        if not self.can_analyze:
            return False
        self.analyses_used_this_month += 1
        return True

    def record_property_view(self) -> bool:
        """Record a property view. Returns True if allowed."""
        if not self.can_view_property:
            return False
        self.property_views_today += 1
        return True

    def record_dd_report(self) -> bool:
        """Record a Due Diligence report usage."""
        if not self.has_due_diligence:
            return False
        self.dd_reports_used_this_month += 1
        return True
