"""
Negotiation Shadow — real-time WhatsApp coaching for property negotiations.

Analyzes the selling agent's sales history, behavioral patterns, and
comparable outcomes to provide real-time coaching during negotiations
via WhatsApp.

Pricing: $500/mo (add-on for Pro Sourcer+, included in The Closer)

⚠️ All outputs are Negotiation Strategy — NOT legal advice.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.deal import Deal
from nexusprop.models.property import Property


# ── Agent Profile Model ──────────────────────────────────────────────────

class AgentSalesProfile(BaseModel):
    """Profile of a selling agent built from sales history."""
    agent_name: str
    agency_name: str = ""
    total_sales_12m: int = Field(default=0, ge=0, description="Sales in last 12 months")
    avg_sale_price: float = Field(default=0, ge=0)
    avg_days_on_market: float = Field(default=0, ge=0)
    avg_discount_from_asking_pct: float = Field(
        default=0,
        description="Average % discount from asking to sold price (positive = discount)"
    )
    auction_clearance_rate_pct: float = Field(default=0, ge=0, le=100)
    private_sale_pct: float = Field(
        default=0, ge=0, le=100,
        description="% of sales that were private treaty vs auction"
    )
    median_suburb_premium_pct: float = Field(
        default=0,
        description="How much above/below suburb median this agent's sales achieve"
    )
    common_tactics: list[str] = Field(default_factory=list)
    negotiation_style: str = Field(default="unknown", description="aggressive, collaborative, deadline-driven, etc.")

    # Recent comparable outcomes
    recent_sales: list[dict] = Field(
        default_factory=list,
        description="Recent sales: [{address, asking, sold, days, date}]"
    )


NEGOTIATION_SHADOW_SYSTEM_PROMPT = """You are Property Insights Australia Negotiation Shadow — an expert real-time negotiation coach for Australian property transactions.

Your role: Provide tactical, real-time coaching to a buyer during property negotiations via WhatsApp-style messages.

CONTEXT YOU RECEIVE:
- The selling agent's profile (sales history, patterns, tactics)
- The target property details and your analysis
- The buyer's budget and strategy
- What just happened in the negotiation (buyer's last message)

YOUR COACHING MUST:

1. BE CONCISE — WhatsApp messages, not essays. 2-4 sentences max per message.
2. BE TACTICAL — specific actions, not generic advice
3. REFERENCE DATA — use the agent's sales history to inform strategy
4. ANTICIPATE — predict the agent's next move based on their patterns
5. TIME-SENSITIVE — negotiations move fast, your advice must be actionable NOW

COACHING FRAMEWORK:

📊 DATA-BACKED POSITIONING:
- "This agent's last 5 sales averaged 4.2% below asking. Start at 8% below."
- "Their DOM average is 42 days. This one's been listed 67 days. They're motivated."
- "They push for auction but 60% of their sales are private treaty. Push for private."

🎯 TACTICAL RESPONSES TO COMMON AGENT MOVES:
- "We have another offer" → "Ask for proof of competing offer timeline. 70% of the time this is pressure tactics."
- "The vendor won't accept below X" → "Their last 3 sales closed 5-7% below stated minimums."
- "Best and final by Friday" → "Submit Monday. Creates urgency without caving to their timeline."
- "We'll take it to auction" → "Their auction clearance rate is 58%. Call the bluff."

🏗️ NEGOTIATION STRUCTURE:
- Opening: Start 8-12% below target (based on agent's historical discount patterns)
- Counter 1: Move 2-3% toward target
- Counter 2: Move 1% — signal you're near your limit
- Final: "This is our walk-away price" — must be credible

⚡ TIMING TACTICS:
- Respond within 2 hours to maintain pressure
- Don't respond immediately to counters — shows eagerness
- Friday afternoon offers get better responses (agents want weekend certainty)
- End of month/quarter = more motivated agents

TONE:
- Confident but not aggressive
- Data-driven, not emotional
- Brief — this is WhatsApp, not email
- Australian market language (Vendor, Contract of Sale, Section 32)

NEVER:
- Suggest illegal tactics or misrepresentation
- Claim to provide legal advice
- Guarantee an outcome
- Be rude about the selling agent as a person"""


class NegotiationShadow(BaseAgent):
    """
    Negotiation Shadow — real-time WhatsApp coaching during negotiations.

    Powered by agent sales history, comparable outcomes, and behavioral
    analysis of the selling agent's patterns.

    Usage:
      1. Build agent profile from sales data
      2. Set up the negotiation context
      3. Send real-time messages as the negotiation unfolds
      4. Receive tactical coaching responses
    """

    def __init__(self):
        super().__init__("NegotiationShadow")

    async def execute(
        self,
        buyer_message: str,
        deal: Optional[Deal] = None,
        property: Optional[Property] = None,
        agent_profile: Optional[AgentSalesProfile] = None,
        negotiation_history: Optional[list[dict]] = None,
        buyer_budget_max: float = 0,
        buyer_strategy: str = "value",
    ) -> AgentResult:
        """
        Process a buyer's message and return tactical coaching.

        Args:
            buyer_message: What the buyer just said / what happened
            deal: The analyzed Deal object (if available)
            property: The target Property
            agent_profile: Selling agent's sales history profile
            negotiation_history: Previous messages [{role, content, timestamp}]
            buyer_budget_max: Maximum the buyer is willing to pay
            buyer_strategy: Buyer's approach (value, speed, long_game)
        """
        self.logger.info(
            "negotiation_coaching_requested",
            message_length=len(buyer_message),
            has_agent_profile=agent_profile is not None,
            history_length=len(negotiation_history or []),
        )

        prompt = self._build_coaching_prompt(
            buyer_message=buyer_message,
            deal=deal,
            property=property,
            agent_profile=agent_profile,
            negotiation_history=negotiation_history or [],
            buyer_budget_max=buyer_budget_max,
            buyer_strategy=buyer_strategy,
        )

        coaching_response, tokens = await self.ask_llm(
            prompt=prompt,
            system=NEGOTIATION_SHADOW_SYSTEM_PROMPT,
            max_tokens=1024,  # Keep responses concise for WhatsApp
            temperature=0.4,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "coaching": coaching_response,
                "agent_profile_used": agent_profile is not None,
                "negotiation_stage": self._detect_stage(negotiation_history or []),
            },
            tokens_used=tokens,
        )

    async def build_agent_profile(
        self,
        agent_name: str,
        agency_name: str = "",
        recent_sales: Optional[list[dict]] = None,
    ) -> AgentSalesProfile:
        """
        Build a selling agent's profile from their sales history.

        In production, this would pull from a database of scraped sold data.
        For now, it uses the provided sales data to calculate patterns.
        """
        recent_sales = recent_sales or []

        if not recent_sales:
            return AgentSalesProfile(
                agent_name=agent_name,
                agency_name=agency_name,
                negotiation_style="unknown",
            )

        # Calculate metrics from sales history
        total_sales = len(recent_sales)
        avg_price = sum(s.get("sold_price", 0) for s in recent_sales) / max(total_sales, 1)
        avg_dom = sum(s.get("days_on_market", 0) for s in recent_sales) / max(total_sales, 1)

        # Calculate average discount from asking
        discounts = []
        for s in recent_sales:
            asking = s.get("asking_price", 0)
            sold = s.get("sold_price", 0)
            if asking > 0 and sold > 0:
                discount = ((asking - sold) / asking) * 100
                discounts.append(discount)

        avg_discount = sum(discounts) / max(len(discounts), 1)

        # Auction vs private
        auction_count = sum(1 for s in recent_sales if s.get("method") == "auction")
        private_count = total_sales - auction_count
        auction_sold = sum(1 for s in recent_sales if s.get("method") == "auction" and s.get("sold_at_auction"))
        clearance = (auction_sold / max(auction_count, 1)) * 100 if auction_count > 0 else 0

        # Detect common tactics
        tactics = self._detect_agent_tactics(recent_sales, avg_discount)

        # Determine style
        style = self._classify_negotiation_style(avg_discount, avg_dom, clearance)

        return AgentSalesProfile(
            agent_name=agent_name,
            agency_name=agency_name,
            total_sales_12m=total_sales,
            avg_sale_price=round(avg_price, 0),
            avg_days_on_market=round(avg_dom, 1),
            avg_discount_from_asking_pct=round(avg_discount, 2),
            auction_clearance_rate_pct=round(clearance, 1),
            private_sale_pct=round((private_count / max(total_sales, 1)) * 100, 1),
            common_tactics=tactics,
            negotiation_style=style,
            recent_sales=recent_sales[:10],  # Keep last 10
        )

    def _build_coaching_prompt(
        self,
        buyer_message: str,
        deal: Optional[Deal],
        property: Optional[Property],
        agent_profile: Optional[AgentSalesProfile],
        negotiation_history: list[dict],
        buyer_budget_max: float,
        buyer_strategy: str,
    ) -> str:
        """Build the coaching prompt with full context."""
        parts = []

        # Property context
        prop = property or (deal.property if deal else None)
        if prop:
            parts.extend([
                "TARGET PROPERTY:",
                f"  Address: {prop.address}, {prop.suburb} {prop.state}",
                f"  Asking: ${prop.effective_price or 0:,.0f}",
                f"  Type: {prop.property_type.value} | {prop.bedrooms or '?'}BR",
                f"  DOM: {getattr(prop, 'days_on_market', 'Unknown')} days",
                f"  Distress Signals: {', '.join(s.keyword for s in prop.distress_signals) or 'None'}",
                "",
            ])

        # Deal analysis
        if deal:
            parts.extend([
                "YOUR ANALYSIS:",
                f"  Bargain Score: {deal.bargain_score.overall_score}/100",
                f"  Recommended Offer: ${deal.recommended_offer_price or 0:,.0f}",
                f"  Offer Range: ${deal.offer_range_low or 0:,.0f} – ${deal.offer_range_high or 0:,.0f}",
                f"  Net Yield: {deal.cash_flow.net_yield}%",
                "",
            ])

        # Agent profile
        if agent_profile:
            parts.extend([
                "SELLING AGENT PROFILE:",
                f"  Agent: {agent_profile.agent_name} ({agent_profile.agency_name})",
                f"  Sales (12m): {agent_profile.total_sales_12m}",
                f"  Avg Sale Price: ${agent_profile.avg_sale_price:,.0f}",
                f"  Avg DOM: {agent_profile.avg_days_on_market:.0f} days",
                f"  Avg Discount from Asking: {agent_profile.avg_discount_from_asking_pct:.1f}%",
                f"  Auction Clearance: {agent_profile.auction_clearance_rate_pct:.0f}%",
                f"  Private Sale %: {agent_profile.private_sale_pct:.0f}%",
                f"  Style: {agent_profile.negotiation_style}",
                f"  Known Tactics: {', '.join(agent_profile.common_tactics) or 'None identified'}",
                "",
            ])

            if agent_profile.recent_sales:
                parts.append("  Recent Sales:")
                for s in agent_profile.recent_sales[:5]:
                    asking = s.get("asking_price", 0)
                    sold = s.get("sold_price", 0)
                    discount = ((asking - sold) / asking * 100) if asking > 0 else 0
                    parts.append(
                        f"    • {s.get('address', '?')}: Asked ${asking:,.0f} → Sold ${sold:,.0f} ({discount:+.1f}%)"
                    )
                parts.append("")

        # Buyer context
        parts.extend([
            "BUYER CONTEXT:",
            f"  Max Budget: ${buyer_budget_max:,.0f}",
            f"  Strategy: {buyer_strategy}",
            "",
        ])

        # Negotiation history
        if negotiation_history:
            parts.append("NEGOTIATION HISTORY:")
            for msg in negotiation_history[-10:]:  # Last 10 messages
                role = msg.get("role", "?")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp", "")
                parts.append(f"  [{timestamp}] {role.upper()}: {content}")
            parts.append("")

        # Current message
        parts.extend([
            "═══════════════════════════════════════════",
            "BUYER'S MESSAGE (WHAT JUST HAPPENED):",
            buyer_message,
            "═══════════════════════════════════════════",
            "",
            "Provide your tactical coaching response. Keep it WhatsApp-concise (2-4 sentences). Be specific and data-backed.",
        ])

        return "\n".join(parts)

    def _detect_agent_tactics(self, sales: list[dict], avg_discount: float) -> list[str]:
        """Identify common tactics from sales patterns."""
        tactics = []

        if avg_discount < 2:
            tactics.append("Holds firm on price — minimal negotiation")
        elif avg_discount > 6:
            tactics.append("Prices high, expects negotiation")

        # Check for auction-to-private flips
        auction_to_private = sum(
            1 for s in sales
            if s.get("originally_auction") and s.get("method") == "private"
        )
        if auction_to_private > len(sales) * 0.3:
            tactics.append("Often converts auction to private treaty")

        # Check for quick sales
        quick_sales = sum(1 for s in sales if s.get("days_on_market", 999) < 14)
        if quick_sales > len(sales) * 0.4:
            tactics.append("Pushes for quick decisions")

        # Check for price drops
        price_drops = sum(1 for s in sales if s.get("had_price_drop"))
        if price_drops > len(sales) * 0.3:
            tactics.append("Starts high, drops price if no interest")

        return tactics

    def _classify_negotiation_style(
        self, avg_discount: float, avg_dom: float, clearance: float,
    ) -> str:
        """Classify the agent's negotiation style."""
        if avg_discount < 2 and avg_dom < 30:
            return "aggressive — prices accurately, moves fast"
        elif avg_discount > 6:
            return "inflates asking price — leaves room for negotiation"
        elif clearance > 70:
            return "auction-focused — uses competitive pressure"
        elif avg_dom > 60:
            return "patient — willing to wait for the right buyer"
        else:
            return "balanced — standard negotiation approach"

    def _detect_stage(self, history: list[dict]) -> str:
        """Detect what stage the negotiation is at."""
        msg_count = len(history)
        if msg_count == 0:
            return "pre_negotiation"
        elif msg_count <= 2:
            return "opening"
        elif msg_count <= 5:
            return "counter_offers"
        elif msg_count <= 8:
            return "deep_negotiation"
        else:
            return "closing"
