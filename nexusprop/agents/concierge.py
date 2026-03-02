"""
The Concierge Agent — hyper-personalized property matching & notifications.

Learns the user's "vibe" — knows what they love, hate, and care about.
Sends Golden Opportunity alerts via WhatsApp/SMS/Email.

No more irrelevant listings. Only deals that match YOUR criteria.
"""

from __future__ import annotations

from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.deal import Deal
from nexusprop.models.property import Property
from nexusprop.models.user import UserProfile


CONCIERGE_SYSTEM_PROMPT = """You are Property Insights Australia Concierge — a hyper-personalized property advisor.

You know your client's preferences deeply:
- What they love (high ceilings, north-facing, quiet streets)
- What they hate (busy roads, no parking, dark rooms)
- Their budget range and investment strategy
- Their preferred suburbs and property types

Your job: Evaluate a property against the user's preferences and explain WHY
this property is relevant to THEM specifically.

Be concise, warm, and specific. Reference their actual preferences.
Max 3-4 sentences for the notification message.

Example: "Hey Sarah! 🏡 A 4BR house just dropped in Paddington at $1.2M —
that's $100k below median. High ceilings ✅, north-facing living ✅,
no body corp ✅. Bargain Score 89/100. Want me to draft an offer?"
"""


class ConciergeAgent(BaseAgent):
    """
    The Concierge — matches deals to users and sends personalized notifications.
    """

    def __init__(self):
        super().__init__("Concierge")

    async def execute(
        self,
        deals: list[Deal],
        users: list[UserProfile],
    ) -> AgentResult:
        """
        Match deals to users and generate personalized notifications.

        Args:
            deals: List of analyzed deals from the Analyst
            users: List of active user profiles
        """
        self.logger.info("concierge_matching", deals=len(deals), users=len(users))

        notifications: list[dict] = []
        total_tokens = 0

        for user in users:
            if not user.is_active:
                continue

            matched_deals = self._match_deals_to_user(deals, user)

            for deal in matched_deals:
                try:
                    message, tokens = await self._generate_notification(user, deal)
                    total_tokens += tokens

                    notifications.append({
                        "user_id": str(user.id),
                        "user_name": user.name,
                        "deal_id": str(deal.id),
                        "property_address": deal.property.address,
                        "bargain_score": deal.bargain_score.overall_score,
                        "channel": user.preferences.notification_channel.value,
                        "message": message,
                        "phone": user.phone or user.whatsapp_number,
                        "email": user.email,
                    })
                except Exception as e:
                    self.logger.warning(
                        "notification_generation_failed",
                        user=user.name,
                        deal=deal.property.address,
                        error=str(e),
                    )

        self.logger.info("concierge_completed", notifications=len(notifications))

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "notifications": notifications,
                "total_matched": len(notifications),
            },
            tokens_used=total_tokens,
        )

    def _match_deals_to_user(self, deals: list[Deal], user: UserProfile) -> list[Deal]:
        """Filter and rank deals for a specific user's preferences."""
        prefs = user.preferences
        matched = []

        for deal in deals:
            prop = deal.property
            score = 0

            # Golden opportunity only filter
            if prefs.golden_opportunity_only and not deal.is_golden_opportunity:
                continue

            # Minimum bargain score
            if deal.bargain_score.overall_score < prefs.property.min_bargain_score:
                continue

            # Budget check
            price = prop.effective_price or 0
            if price < prefs.budget.min_price or price > prefs.budget.max_price:
                continue

            # Property type check
            if prefs.property.property_types and prop.property_type not in prefs.property.property_types:
                continue

            # Location check
            if prefs.location.suburbs:
                if prop.suburb.lower() not in [s.lower() for s in prefs.location.suburbs]:
                    continue
            if prefs.location.states:
                if prop.state.upper() not in [s.upper() for s in prefs.location.states]:
                    continue
            if prefs.location.postcodes:
                if prop.postcode not in prefs.location.postcodes:
                    continue

            # Bedroom check
            if prefs.property.min_bedrooms and (prop.bedrooms or 0) < prefs.property.min_bedrooms:
                continue

            # Deal breakers
            if prefs.property.no_strata and prop.strata_levies_quarterly:
                continue
            if prefs.property.no_flood_zone and prop.flood_zone:
                continue
            if prefs.property.no_bushfire_zone and prop.bushfire_zone:
                continue
            if prefs.property.no_heritage and prop.heritage_listed:
                continue

            # Yield check
            if prefs.property.min_gross_yield:
                if deal.cash_flow.gross_rental_yield < prefs.property.min_gross_yield:
                    continue

            # Already viewed / dismissed
            if prop.id in user.properties_dismissed:
                continue

            # Loves check (bonus scoring)
            if prefs.property.loves and prop.listing_text:
                text_lower = prop.listing_text.lower()
                for love in prefs.property.loves:
                    if love.lower() in text_lower:
                        score += 10

            # Hates check (penalty)
            if prefs.property.hates and prop.listing_text:
                text_lower = prop.listing_text.lower()
                for hate in prefs.property.hates:
                    if hate.lower() in text_lower:
                        score -= 20

            if score >= -10:  # Allow some minor hate matches
                matched.append(deal)

        # Sort by bargain score
        matched.sort(key=lambda d: d.bargain_score.overall_score, reverse=True)

        # Respect max notifications
        max_notifs = prefs.max_notifications_per_day
        return matched[:max_notifs]

    async def _generate_notification(
        self,
        user: UserProfile,
        deal: Deal,
    ) -> tuple[str, int]:
        """Generate a personalized notification message using AI."""
        prop = deal.property
        prefs = user.preferences

        # Build preference context
        loves_str = ", ".join(prefs.property.loves) if prefs.property.loves else "not specified"
        hates_str = ", ".join(prefs.property.hates) if prefs.property.hates else "not specified"

        prompt = f"""Generate a short, personalized property alert for {user.name}.

USER PREFERENCES:
- Budget: ${prefs.budget.min_price:,.0f} – ${prefs.budget.max_price:,.0f}
- Loves: {loves_str}
- Hates: {hates_str}
- Looking for: {', '.join(pt.value for pt in prefs.property.property_types)}
- Suburbs: {', '.join(prefs.location.suburbs) or 'Any'}
- Strategy: {', '.join(s.value for s in prefs.preferred_strategies)}

PROPERTY MATCH:
- {prop.address}, {prop.suburb} {prop.state}
- {prop.bedrooms}BR {prop.bathrooms}BA {prop.car_spaces or 0}Car {prop.property_type.value}
- Price: ${prop.effective_price or 0:,.0f}
- Bargain Score: {deal.bargain_score.overall_score}/100
- {deal.bargain_score.summary}
- Net Yield: {deal.cash_flow.net_yield}%
- Monthly Cash Flow: ${deal.cash_flow.monthly_cash_flow:,.0f}

Generate a brief WhatsApp-style message (max 280 chars for SMS compatibility).
Be warm but professional. Highlight features that match their loves.
End with a call-to-action."""

        if self.settings.anthropic_api_key:
            return await self.ask_llm(
                prompt=prompt,
                system=CONCIERGE_SYSTEM_PROMPT,
                max_tokens=256,
                temperature=0.6,
            )
        else:
            # Fallback template
            msg = (
                f"🏡 {user.name}! New match in {prop.suburb}: "
                f"{prop.bedrooms}BR {prop.property_type.value} at ${prop.effective_price or 0:,.0f}. "
                f"Bargain Score {deal.bargain_score.overall_score}/100. "
                f"Yield {deal.cash_flow.gross_rental_yield}%. "
                f"Reply YES for full analysis."
            )
            return msg, 0
