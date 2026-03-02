"""
Agent C — The Closer

The action layer. Takes a Deal and generates a persuasive, legally-safe
offer document using AI-powered letter writing and negotiation strategy.

Uses Cialdini's 6 Principles of Persuasion adapted for Australian
property transactions.

⚠️ All outputs are Commercial Strategy Drafts — NOT legal advice.
"""

from __future__ import annotations

import json
from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.deal import Deal
from nexusprop.models.offer import (
    OfferDocument,
    OfferGenerationRequest,
    OfferTone,
    SellerMotivation,
)
from nexusprop.tools.offer_writer import OfferWriter


CLOSER_SYSTEM_PROMPT = """You are Property Insights Australia Closer — an expert property negotiation strategist for the Australian market.

Your role: Generate a persuasive, professional offer letter and negotiation strategy.

CRITICAL LEGAL GUARDRAIL:
- You are generating a "Commercial Strategy Draft" — NOT legal advice.
- NEVER use language that could be construed as a binding legal document.
- ALWAYS include the disclaimer that a licensed conveyancer/solicitor must review.
- NEVER provide specific legal interpretations of contracts or legislation.
- Frame everything as "commercial strategy" and "negotiation positioning."

PERSUASION FRAMEWORK (Cialdini's 6 Principles):
1. RECIPROCITY: Offer flexibility, fast settlement, easy process for the seller
2. COMMITMENT: Reference mutual goals and previous conversations
3. SOCIAL PROOF: Cite comparable sales data and market analysis
4. AUTHORITY: Position the buyer as serious, pre-approved, professionally advised
5. LIKING: Build genuine rapport — personal story, appreciation of the property
6. SCARCITY: Create appropriate urgency without being manipulative

TONE GUIDANCE:
- EMPATHETIC: For distressed sellers — focus on understanding, ease, support
- PROFESSIONAL: For neutral/aspirational — focus on data, clean terms, efficiency
- FAMILY_STORY: For family homes — focus on emotional connection, legacy
- URGENT: For competitive situations — focus on speed, certainty, commitment
- INVESTOR_DIRECT: For agents/developers — focus on numbers, no nonsense

AUSTRALIAN SPECIFICS:
- Use "Vendor" not "Seller" in formal sections
- Reference "Contract of Sale" or "Section 32" where appropriate
- Settlement periods in Australia are typically 30–90 days
- Standard deposit is 10% (can negotiate 5% with vendor agreement)
- Reference "unconditional finance" as a strength
- Mention "building & pest" inspection conditions as standard

OUTPUT FORMAT:
Return a JSON object with these fields:
{
    "cover_letter": "The full persuasive offer letter text",
    "negotiation_talking_points": ["point 1", "point 2", ...],
    "counter_offer_strategy": "Strategy text for handling counters",
    "recommended_offer_price": 000000,
    "key_persuasion_hooks": ["hook 1", "hook 2"]
}"""


class CloserAgent(BaseAgent):
    """
    Agent C — The Closer.

    Generates AI-powered persuasive offer documents that maximize
    the buyer's chances of securing the property at the best price.
    """

    def __init__(self):
        super().__init__("Closer")
        self.template_writer = OfferWriter()

    async def execute(
        self,
        request: OfferGenerationRequest,
        deal: Optional[Deal] = None,
    ) -> AgentResult:
        """
        Generate a complete offer document.

        Args:
            request: The offer generation request with buyer and property details
            deal: Optional Deal object with full analysis for context
        """
        self.logger.info(
            "closer_generating_offer",
            address=request.property_address,
            asking=request.asking_price,
            buyer=request.buyer_name,
        )

        total_tokens = 0

        # Generate base offer document from template engine
        offer_doc = self.template_writer.generate(request, deal)

        # If we have AI access, enhance the letter with Claude
        if self.settings.anthropic_api_key:
            try:
                enhanced_doc, tokens = await self._ai_enhance_offer(request, deal, offer_doc)
                if enhanced_doc:
                    offer_doc = enhanced_doc
                    total_tokens += tokens
            except Exception as e:
                self.logger.warning("ai_enhancement_failed", error=str(e))
                # Fall back to template-generated document

        self.logger.info(
            "closer_offer_generated",
            address=request.property_address,
            offer_price=offer_doc.offer_price,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "offer_document": offer_doc,
                "offer_price": offer_doc.offer_price,
                "deposit": offer_doc.deposit_amount,
                "settlement_days": offer_doc.settlement_days,
            },
            tokens_used=total_tokens,
        )

    async def generate_counter_response(
        self,
        original_offer: OfferDocument,
        counter_price: float,
        counter_conditions: Optional[str] = None,
    ) -> AgentResult:
        """
        Generate a response to a seller's counter-offer.

        Args:
            original_offer: The original offer document
            counter_price: The seller's counter-offer price
            counter_conditions: Any additional conditions from the seller
        """
        self.logger.info(
            "generating_counter_response",
            original=original_offer.offer_price,
            counter=counter_price,
        )

        prompt = f"""The seller has countered our offer. Generate a strategic response.

ORIGINAL OFFER:
- Our Price: ${original_offer.offer_price:,.0f}
- Their Asking: (see letter context)
- Settlement: {original_offer.settlement_days} days
- Our maximum budget: ${original_offer.walk_away_price or 'Not set':,.0f}

SELLER'S COUNTER:
- Counter Price: ${counter_price:,.0f}
- Additional Conditions: {counter_conditions or 'None specified'}

GAP ANALYSIS:
- Gap: ${counter_price - original_offer.offer_price:,.0f}
- As % of our offer: {((counter_price - original_offer.offer_price) / original_offer.offer_price * 100):.1f}%

Generate:
1. A RECOMMENDED RESPONSE PRICE — split the difference in our favor
2. A RESPONSE LETTER (brief, strategic, 2-3 paragraphs)
3. Key TALKING POINTS for the phone call
4. WALK-AWAY ASSESSMENT — should we continue or walk?

Return as JSON with keys: response_price, response_letter, talking_points, walk_away_assessment"""

        response_text, tokens = await self.ask_llm(
            prompt=prompt,
            system=CLOSER_SYSTEM_PROMPT,
            max_tokens=2048,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "counter_response": response_text,
                "original_offer": original_offer.offer_price,
                "counter_price": counter_price,
            },
            tokens_used=tokens,
        )

    async def _ai_enhance_offer(
        self,
        request: OfferGenerationRequest,
        deal: Optional[Deal],
        template_doc: OfferDocument,
    ) -> tuple[Optional[OfferDocument], int]:
        """Use Claude to enhance the offer letter with persuasive AI-generated content."""

        deal_context = ""
        if deal:
            deal_context = f"""
DEAL ANALYSIS:
- Bargain Score: {deal.bargain_score.overall_score}/100
- {deal.bargain_score.summary}
- Net Yield: {deal.cash_flow.net_yield}%
- Monthly Cash Flow: ${deal.cash_flow.monthly_cash_flow:,.0f}
- Recommended Strategies: {', '.join(s.value for s in deal.recommended_strategies)}
- Comparable Sales: {deal.comparable_sales_summary or 'Not available'}
"""

        motivation_context = {
            SellerMotivation.DESPERATE: "The seller appears DESPERATE (mortgagee/deceased/divorce). They need certainty and speed more than top dollar.",
            SellerMotivation.MOTIVATED: "The seller is MOTIVATED but not desperate. They want a clean, hassle-free sale.",
            SellerMotivation.NEUTRAL: "The seller appears to be NEUTRAL — testing the market. We need strong data to justify our price.",
            SellerMotivation.ASPIRATIONAL: "The seller has ASPIRATIONAL pricing — they're hoping for above-market. Patience and data are our weapons.",
            SellerMotivation.UNKNOWN: "Seller motivation is UNKNOWN. Use a balanced approach.",
        }

        prompt = f"""Generate a persuasive property offer letter and negotiation strategy.

PROPERTY: {request.property_address}
ASKING PRICE: ${request.asking_price:,.0f}
OUR OFFER: ${template_doc.offer_price:,.0f} ({((request.asking_price - template_doc.offer_price) / request.asking_price * 100):.1f}% below asking)

BUYER: {request.buyer_name}
{f'ENTITY: {request.buyer_entity}' if request.buyer_entity else ''}
BUDGET MAX: ${request.buyer_budget_max:,.0f}
{f'BUYER STORY: {request.buyer_story}' if request.buyer_story else ''}

SELLER MOTIVATION: {motivation_context.get(request.seller_motivation, 'Unknown')}
TONE: {request.preferred_tone.value} — {request.preferred_tone.value}
{deal_context}

CONDITIONS:
{chr(10).join(f'- {c.name} ({c.days} days)' for c in template_doc.conditions)}

SETTLEMENT: {request.settlement_days} days

Generate the complete offer package as JSON. Make the letter compelling, human, and strategic.
Apply all 6 Cialdini principles naturally. DO NOT make it feel templated.

IMPORTANT: Include the legal disclaimer that this is a Commercial Strategy Draft, not legal advice."""

        try:
            response_text, tokens = await self.ask_llm(
                prompt=prompt,
                system=CLOSER_SYSTEM_PROMPT,
                max_tokens=4096,
                temperature=0.5,  # Slightly higher for creative writing
            )

            # Parse the AI response
            json_str = response_text.strip()
            if "```" in json_str:
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                json_str = json_str.strip()

            data = json.loads(json_str)

            # Update the template document with AI-generated content
            if "cover_letter" in data:
                template_doc.cover_letter = data["cover_letter"]
            if "negotiation_talking_points" in data:
                template_doc.negotiation_talking_points = data["negotiation_talking_points"]
            if "counter_offer_strategy" in data:
                template_doc.counter_offer_strategy = data["counter_offer_strategy"]

            self.logger.info("ai_offer_enhancement_success")
            return template_doc, tokens

        except json.JSONDecodeError:
            # If JSON parsing fails, use the raw text as the letter
            template_doc.cover_letter = response_text
            return template_doc, tokens

        except Exception as e:
            self.logger.warning("ai_offer_enhancement_failed", error=str(e))
            return None, 0
