"""
Offer Writer — AI-powered persuasive offer letter generation.

Uses the 6 Principles of Persuasion (Cialdini) to craft compelling
property offers, adapted to the seller's motivation and situation.

⚠️ LEGAL DISCLAIMER: All outputs are Commercial Strategy Drafts,
not legal advice. Always engage a licensed conveyancer/solicitor.
"""

from __future__ import annotations

from typing import Optional

import structlog

from nexusprop.models.offer import (
    OfferCondition,
    OfferDocument,
    OfferGenerationRequest,
    OfferTone,
    SellerMotivation,
)
from nexusprop.models.deal import Deal

logger = structlog.get_logger(__name__)


# ── Persuasion Framework ────────────────────────────────────────────────────

PERSUASION_PRINCIPLES = {
    "reciprocity": "Offer something of value first (flexibility, fast settlement, easy process)",
    "commitment": "Reference shared goals and mutual benefit",
    "social_proof": "Cite market data, comparable sales, and professional analysis",
    "authority": "Position the buyer as serious, pre-approved, and advised",
    "liking": "Build rapport through personal story and genuine appreciation",
    "scarcity": "Create urgency without being pushy — limited time, life circumstances",
}


TONE_TEMPLATES = {
    OfferTone.EMPATHETIC: {
        "opening": "We understand this may be a difficult time, and we appreciate you considering our offer.",
        "style": "warm, understanding, personal",
        "closing": "We genuinely hope to make this transition as smooth as possible for you.",
    },
    OfferTone.PROFESSIONAL: {
        "opening": "Please find enclosed our formal expression of interest for the above property.",
        "style": "formal, business-like, data-driven",
        "closing": "We look forward to your consideration and are available to discuss terms at your convenience.",
    },
    OfferTone.URGENT: {
        "opening": "We are writing to present a firm and unconditional offer, available for immediate acceptance.",
        "style": "direct, decisive, time-sensitive",
        "closing": "This offer is valid for 48 hours and we are prepared to proceed immediately.",
    },
    OfferTone.FAMILY_STORY: {
        "opening": "We fell in love with your home the moment we walked through the door.",
        "style": "emotional, story-driven, personal connection",
        "closing": "We can already picture our family making wonderful memories here, just as you have.",
    },
    OfferTone.INVESTOR_DIRECT: {
        "opening": "We are professional property investors presenting a clean, no-nonsense offer.",
        "style": "efficient, numbers-focused, minimal conditions",
        "closing": "Cash-equivalent settlement. No chains. No delays. Your move.",
    },
}


MOTIVATION_STRATEGIES = {
    SellerMotivation.DESPERATE: {
        "leverage": "high",
        "offer_discount_pct": 15,
        "emphasize": "fast settlement, certainty, problem-solving",
        "conditions": "minimal — remove as many as possible for competitive edge",
    },
    SellerMotivation.MOTIVATED: {
        "leverage": "moderate",
        "offer_discount_pct": 10,
        "emphasize": "flexibility on settlement date, clean offer",
        "conditions": "standard but offer to waive non-essential",
    },
    SellerMotivation.NEUTRAL: {
        "leverage": "low",
        "offer_discount_pct": 5,
        "emphasize": "market data, comparable sales, fair value",
        "conditions": "standard full conditions",
    },
    SellerMotivation.ASPIRATIONAL: {
        "leverage": "minimal",
        "offer_discount_pct": 3,
        "emphasize": "patience, willingness to wait, but grounded in data",
        "conditions": "full conditions, don't overcommit",
    },
    SellerMotivation.UNKNOWN: {
        "leverage": "moderate",
        "offer_discount_pct": 7,
        "emphasize": "balanced approach — data + personal touch",
        "conditions": "standard conditions",
    },
}


class OfferWriter:
    """
    Generates professional, persuasive offer documents.

    Creates the letter text, negotiation talking points, and counter-offer strategy.
    The AI-powered version (via the Closer agent) uses Claude for advanced generation.
    This is the rule-based template engine for fast generation.
    """

    def generate(
        self,
        request: OfferGenerationRequest,
        deal: Optional[Deal] = None,
    ) -> OfferDocument:
        """
        Generate an offer document from the request.

        This is the template-based generator. The Closer agent wraps this
        with AI-powered letter writing for maximum persuasion.
        """
        # Calculate optimal offer price
        offer_price = request.offer_price_override or self._calculate_offer_price(
            asking_price=request.asking_price,
            budget_max=request.buyer_budget_max,
            motivation=request.seller_motivation,
        )

        deposit = round(offer_price * 0.10, 0)  # Standard 10% deposit

        # Build conditions
        conditions = []
        if request.include_conditions:
            doc_template = OfferDocument(
                property_id=request.property_id,
                property_address=request.property_address,
                buyer_name=request.buyer_name,
                offer_price=offer_price,
                deposit_amount=deposit,
            )
            conditions = doc_template.get_standard_conditions()

            # If desperate seller — consider removing conditions for competitive edge
            if request.seller_motivation == SellerMotivation.DESPERATE:
                conditions = [c for c in conditions if not c.is_waivable]

        # Generate letter
        cover_letter = self._generate_letter(request, offer_price, conditions)

        # Negotiation talking points
        talking_points = self._generate_talking_points(request, offer_price, deal)

        # Counter-offer strategy
        counter_strategy = self._generate_counter_strategy(request, offer_price)

        # Walk-away price
        walk_away = min(request.buyer_budget_max, request.asking_price * 1.05)

        return OfferDocument(
            property_id=request.property_id,
            property_address=request.property_address,
            buyer_name=request.buyer_name,
            buyer_entity=request.buyer_entity,
            offer_price=offer_price,
            deposit_amount=deposit,
            settlement_days=request.settlement_days,
            finance_approval_days=21,
            seller_motivation=request.seller_motivation,
            offer_tone=request.preferred_tone,
            conditions=conditions,
            cover_letter=cover_letter,
            negotiation_talking_points=talking_points,
            counter_offer_strategy=counter_strategy,
            walk_away_price=walk_away,
        )

    def _calculate_offer_price(
        self,
        asking_price: float,
        budget_max: float,
        motivation: SellerMotivation,
    ) -> float:
        """Calculate the optimal opening offer price."""
        strategy = MOTIVATION_STRATEGIES.get(motivation, MOTIVATION_STRATEGIES[SellerMotivation.UNKNOWN])
        discount_pct = strategy["offer_discount_pct"]

        offer = asking_price * (1 - discount_pct / 100)
        offer = min(offer, budget_max)
        return round(offer, -3)  # Round to nearest $1000

    def _generate_letter(
        self,
        request: OfferGenerationRequest,
        offer_price: float,
        conditions: list[OfferCondition],
    ) -> str:
        """Generate the offer cover letter using templates."""
        tone = TONE_TEMPLATES.get(request.preferred_tone, TONE_TEMPLATES[OfferTone.PROFESSIONAL])
        strategy = MOTIVATION_STRATEGIES.get(request.seller_motivation, MOTIVATION_STRATEGIES[SellerMotivation.UNKNOWN])

        # Build the letter
        lines = [
            "=" * 60,
            "COMMERCIAL STRATEGY DRAFT — NOT LEGAL ADVICE",
            "This document is generated by NexusProp AI for strategic",
            "purposes only. Engage a licensed solicitor before submission.",
            "=" * 60,
            "",
            f"Date: {__import__('datetime').datetime.now().strftime('%d %B %Y')}",
            "",
            f"RE: Expression of Interest — {request.property_address}",
            "",
            "Dear Vendor,",
            "",
            tone["opening"],
            "",
        ]

        # Personal story if provided
        if request.buyer_story and request.preferred_tone in (OfferTone.FAMILY_STORY, OfferTone.EMPATHETIC):
            lines.extend([
                request.buyer_story,
                "",
            ])

        # The offer
        lines.extend([
            f"We would like to present our offer of ${offer_price:,.0f} "
            f"(AUD) for the above property.",
            "",
            f"Key Terms:",
            f"  • Offer Price: ${offer_price:,.0f}",
            f"  • Deposit: ${request.buyer_budget_max * 0.1:,.0f} (10%)",
            f"  • Settlement: {request.settlement_days} days",
            "",
        ])

        # Conditions
        if conditions:
            lines.append("Subject to the following conditions:")
            for i, cond in enumerate(conditions, 1):
                days_str = f" ({cond.days} days)" if cond.days else ""
                lines.append(f"  {i}. {cond.name}{days_str}")
            lines.append("")

        # Strength signals
        lines.extend([
            "Our position:",
            "  • Finance: Pre-approved and ready to proceed",
            "  • Conveyancer: Engaged and briefed",
            "  • Settlement: Flexible on timing to suit your needs",
            "",
        ])

        # Closing
        lines.extend([
            tone["closing"],
            "",
            "Kind regards,",
            f"{request.buyer_name}",
        ])

        if request.buyer_entity:
            lines.append(f"on behalf of {request.buyer_entity}")

        return "\n".join(lines)

    def _generate_talking_points(
        self,
        request: OfferGenerationRequest,
        offer_price: float,
        deal: Optional[Deal],
    ) -> list[str]:
        """Generate negotiation talking points for the buyer."""
        points = [
            f"Opening position: ${offer_price:,.0f} — leave room to move up.",
            "Lead with your pre-approval: 'We have unconditional finance in place.'",
            "Ask about timeline: 'What settlement date works best for you?'",
        ]

        if request.seller_motivation == SellerMotivation.DESPERATE:
            points.extend([
                "Emphasize SPEED: 'We can settle within 30 days if that helps.'",
                "Offer CERTAINTY: 'We can make this unconditional today.'",
                "Don't show eagerness — let your offer speak.",
            ])
        elif request.seller_motivation == SellerMotivation.MOTIVATED:
            points.extend([
                "Show flexibility: 'We're happy to work around your move-out date.'",
                "Keep it clean: 'Our offer has minimal conditions.'",
            ])

        if deal and deal.bargain_score.is_golden_opportunity:
            points.append(
                f"Internal note: Bargain Score {deal.bargain_score.overall_score}/100 — "
                "this is a strong deal, be prepared to increase if needed."
            )

        # Comparable data
        if deal and deal.comparable_sales_summary:
            points.append(
                f"Use comp data: 'Based on recent sales in {request.property_address.split(',')[0]}, "
                "we believe our offer reflects fair market value.'"
            )

        points.extend([
            f"Absolute maximum: ${request.buyer_budget_max:,.0f} — do NOT exceed this.",
            "If countered, ask: 'What price would you accept today?' — get them to name a number.",
            "If rejected, leave the door open: 'If anything changes, we'd love to hear from you.'",
        ])

        return points

    def _generate_counter_strategy(
        self,
        request: OfferGenerationRequest,
        offer_price: float,
    ) -> str:
        """Generate a counter-offer strategy."""
        gap = request.asking_price - offer_price
        midpoint = offer_price + (gap * 0.4)  # Move 40% of the gap

        return (
            f"COUNTER-OFFER STRATEGY\n"
            f"{'─' * 40}\n"
            f"Opening offer: ${offer_price:,.0f}\n"
            f"Expected counter range: ${offer_price + gap * 0.3:,.0f} – ${request.asking_price:,.0f}\n"
            f"Suggested response: ${midpoint:,.0f} (split the difference, lean your way)\n"
            f"Walk-away price: ${min(request.buyer_budget_max, request.asking_price * 1.05):,.0f}\n"
            f"\n"
            f"Negotiation increments:\n"
            f"  Round 1: ${offer_price:,.0f} (opening)\n"
            f"  Round 2: ${offer_price + gap * 0.25:,.0f} (show good faith)\n"
            f"  Round 3: ${midpoint:,.0f} (final position — 'this is our best and final')\n"
            f"\n"
            f"If they won't budge below asking:\n"
            f"  → Request inclusions (appliances, window coverings, garden shed)\n"
            f"  → Negotiate settlement terms (longer/shorter to suit them)\n"
            f"  → Offer to remove conditions in exchange for price reduction"
        )
