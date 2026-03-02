"""
Chatbot Agent — Trending Real Estate News & Market Intelligence.

Engages users with curated real estate insights scraped from Australian
property news sources. Provides conversational access to market trends,
suburb insights, and investment intelligence.

Sources:
  • Domain.com.au news
  • realestate.com.au insights
  • Australian Financial Review (Property)
  • CoreLogic monthly updates
  • SQM Research
  • RBA statements & rate decisions

The chatbot combines live-scraped headlines with the platform's own
Australian property intelligence to deliver personalised, actionable conversations.
"""

from __future__ import annotations

import asyncio
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional

import httpx
import structlog

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.tools.scraper import ScraperClient

logger = structlog.get_logger(__name__)


# ── RSS & News Sources ───────────────────────────────────────────────────

NEWS_SOURCES = [
    {
        "name": "Domain News",
        "url": "https://www.domain.com.au/news/feed/",
        "type": "rss",
        "category": "market",
    },
    {
        "name": "Domain Melbourne",
        "url": "https://www.domain.com.au/news/melbourne/feed/",
        "type": "rss",
        "category": "melbourne",
    },
    {
        "name": "RealEstate.com.au Insights",
        "url": "https://www.realestate.com.au/news/feed/",
        "type": "rss",
        "category": "market",
    },
    {
        "name": "CoreLogic Australia",
        "url": "https://www.corelogic.com.au/news-research/feed",
        "type": "rss",
        "category": "data",
    },
    {
        "name": "AFR Property",
        "url": "https://www.afr.com/property/rss",
        "type": "rss",
        "category": "finance",
    },
    {
        "name": "SQM Research",
        "url": "https://sqmresearch.com.au/feed",
        "type": "rss",
        "category": "data",
    },
]

# Australian property keywords for relevance filtering
AU_KEYWORDS = [
    "melbourne", "sydney", "brisbane", "perth", "adelaide", "hobart",
    "darwin", "canberra", "victoria", "nsw", "queensland", "sa", "wa",
    "tasmania", "act", "northern territory",
    "auction", "clearance rate", "stamp duty", "land tax",
    "interest rate", "rba", "reserve bank", "apra",
    "rental", "vacancy", "yield", "capital growth",
    "infrastructure", "metro tunnel", "suburban rail loop", "olympics",
    "cross river rail", "western sydney airport", "metronet", "aukus",
    "apartment", "house price", "median price",
    "first home", "investor", "property market",
]


CHATBOT_SYSTEM_PROMPT = """You are the Property Insights Australia Chatbot — a friendly, knowledgeable real estate market assistant covering all 8 Australian states and territories.

PERSONALITY:
- Warm, professional, and data-driven
- You speak like a trusted property advisor, not a sales bot
- You reference specific suburbs, data points, and trends
- You use Australian property terminology (vendor, settlement, stamp duty, Section 32)

YOUR KNOWLEDGE:
- All 8 Australian states: NSW, VIC, QLD, SA, WA, TAS, NT, ACT
- 260+ suburbs across 47+ regions with detailed market data
- Current market conditions: auction clearance rates, median prices, rental yields
- Major infrastructure: Metro Tunnel, Suburban Rail Loop, Western Sydney Airport,
  Cross River Rail, 2032 Olympics, METRONET, AUKUS submarine program
- Investment strategies: Buy & Hold, BRRR, negative gearing, depreciation
- State-specific regulations: stamp duty brackets, land tax thresholds, FHB grants

WHAT YOU DO:
1. Share trending property news with context and implications
2. Answer user questions about Australian property markets
3. Provide suburb insights powered by our 260+ suburb database
4. Compare states and regions for investment potential
5. Suggest relevant features of the platform (deal analysis, offer generation, etc.)

WHAT YOU DON'T DO:
- Provide financial or legal advice (direct to professionals)
- Guarantee returns or price predictions (use "projected", "historical")
- Make up data (say "I don't have that data" if unsure)

RESPONSE STYLE:
- Keep responses concise (3-6 sentences unless the user asks for detail)
- Lead with the insight, not the preamble
- Use data/numbers where possible
- End with an engaging follow-up question or suggestion
- Emoji sparingly (1-2 per message max)

WHEN SHARING NEWS:
- Summarise the headline in plain English
- Explain what it means for Australian investors
- Rate the impact: 🔴 Major | 🟡 Moderate | 🟢 Minor
- Suggest an action: "Check your portfolio exposure to..." or "Now might be a good time to..."

WHEN YOU DON'T KNOW:
- "I don't have live data on that, but based on our market database..."
- Never fabricate statistics or trends"""


# ── News Article Model ──────────────────────────────────────────────────

class NewsArticle:
    """Represents a scraped news article."""

    def __init__(
        self,
        title: str,
        link: str,
        source: str,
        published: Optional[datetime] = None,
        summary: str = "",
        category: str = "market",
    ):
        self.title = title
        self.link = link
        self.source = source
        self.published = published or datetime.utcnow()
        self.summary = summary
        self.category = category
        self.au_relevance = self._calc_au_relevance()

    def _calc_au_relevance(self) -> float:
        """Score 0-1 how relevant this article is to Australian property."""
        text = f"{self.title} {self.summary}".lower()
        hits = sum(1 for kw in AU_KEYWORDS if kw in text)
        # National market articles get a base score
        return min(1.0, 0.3 + (hits * 0.1))

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "link": self.link,
            "source": self.source,
            "published": self.published.isoformat() if self.published else None,
            "summary": self.summary,
            "category": self.category,
            "au_relevance": round(self.au_relevance, 2),
        }


class ChatbotAgent(BaseAgent):
    """
    Chatbot Agent — trending real estate news & conversational market intelligence.

    Features:
    1. Scrapes RSS feeds from 6+ Australian real estate news sources
    2. Filters and ranks articles by Australian property relevance
    3. Caches articles (refreshed every 30 minutes)
    4. Generates contextual responses combining news + platform intelligence
    5. Maintains conversation history for contextual follow-ups
    """

    def __init__(self):
        super().__init__("Chatbot")
        self._scraper = ScraperClient(max_concurrent=3, delay_range=(0.5, 1.5))
        self._news_cache: list[NewsArticle] = []
        self._cache_updated: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=30)
        self._conversations: dict[str, list[dict]] = {}  # session_id → messages

    async def execute(
        self,
        user_message: str,
        session_id: str = "default",
        include_news: bool = True,
    ) -> AgentResult:
        """
        Process a user message and return a contextual response.

        Args:
            user_message: The user's chat message
            session_id: Conversation session identifier
            include_news: Whether to fetch/include trending news context
        """
        self.logger.info(
            "chatbot_message_received",
            session=session_id,
            message_len=len(user_message),
        )

        # 1. Refresh news cache if stale
        news_context = ""
        trending = []
        if include_news:
            await self._refresh_news_cache()
            trending = self._get_trending(limit=5)
            news_context = self._format_news_context(trending)

        # 2. Build conversation history
        history = self._conversations.get(session_id, [])
        history.append({"role": "user", "content": user_message})

        # 3. Build the prompt
        prompt = self._build_prompt(user_message, news_context, history)

        # 4. Get LLM response
        response_text, tokens = await self.ask_llm(
            prompt=prompt,
            system=CHATBOT_SYSTEM_PROMPT,
            max_tokens=1024,
            temperature=0.6,
        )

        # 5. Handle no-LLM fallback
        if '"error"' in response_text and "No LLM available" in response_text:
            response_text = self._fallback_response(user_message, trending)
            tokens = 0

        # 6. Update conversation history
        history.append({"role": "assistant", "content": response_text})
        # Keep last 20 messages per session
        self._conversations[session_id] = history[-20:]

        self.logger.info(
            "chatbot_response_generated",
            session=session_id,
            response_len=len(response_text),
            tokens=tokens,
            news_articles=len(trending),
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "response": response_text,
                "trending_news": [a.to_dict() for a in trending],
                "session_id": session_id,
                "conversation_length": len(self._conversations.get(session_id, [])),
            },
            tokens_used=tokens,
        )

    # ── News Scraping ───────────────────────────────────────────────────

    async def _refresh_news_cache(self):
        """Refresh the news cache if TTL expired."""
        if (
            self._cache_updated
            and datetime.utcnow() - self._cache_updated < self._cache_ttl
        ):
            return  # Cache still fresh

        self.logger.info("chatbot_refreshing_news_cache")
        articles: list[NewsArticle] = []

        tasks = [self._fetch_rss(source) for source in NEWS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                articles.extend(result)
            elif isinstance(result, Exception):
                self.logger.warning("rss_fetch_failed", error=str(result))

        # Sort by VIC relevance, then recency
        articles.sort(key=lambda a: (a.au_relevance, a.published or datetime.min), reverse=True)

        # De-duplicate by title similarity
        seen_titles: set[str] = set()
        unique: list[NewsArticle] = []
        for article in articles:
            normalised = re.sub(r"[^a-z0-9]", "", article.title.lower())
            if normalised not in seen_titles:
                seen_titles.add(normalised)
                unique.append(article)

        self._news_cache = unique[:50]  # Keep top 50
        self._cache_updated = datetime.utcnow()

        self.logger.info(
            "chatbot_news_cache_refreshed",
            total_fetched=len(articles),
            unique_cached=len(self._news_cache),
        )

    async def _fetch_rss(self, source: dict) -> list[NewsArticle]:
        """Fetch and parse an RSS feed."""
        articles: list[NewsArticle] = []
        try:
            client = await self._scraper._get_client()
            resp = await client.get(source["url"], timeout=15.0)
            resp.raise_for_status()

            root = ET.fromstring(resp.text)

            # Standard RSS 2.0
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                summary = (item.findtext("description") or "").strip()
                pub_date_str = item.findtext("pubDate") or ""

                if not title:
                    continue

                # Strip HTML from summary
                summary = re.sub(r"<[^>]+>", "", summary)[:300]

                published = self._parse_rss_date(pub_date_str)

                articles.append(
                    NewsArticle(
                        title=title,
                        link=link,
                        source=source["name"],
                        published=published,
                        summary=summary,
                        category=source.get("category", "market"),
                    )
                )

            # Atom format fallback
            if not articles:
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.findall(".//atom:entry", ns):
                    title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
                    link_el = entry.find("atom:link", ns)
                    link = link_el.get("href", "") if link_el is not None else ""
                    summary = (entry.findtext("atom:summary", namespaces=ns) or "").strip()
                    summary = re.sub(r"<[^>]+>", "", summary)[:300]

                    if title:
                        articles.append(
                            NewsArticle(
                                title=title,
                                link=link,
                                source=source["name"],
                                summary=summary,
                                category=source.get("category", "market"),
                            )
                        )

        except Exception as e:
            self.logger.warning(
                "rss_parse_failed",
                source=source["name"],
                url=source["url"],
                error=str(e),
            )

        return articles[:10]  # Max 10 per source

    def _parse_rss_date(self, date_str: str) -> Optional[datetime]:
        """Parse common RSS date formats."""
        if not date_str:
            return None

        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.replace(tzinfo=None) if dt.tzinfo else dt
            except ValueError:
                continue
        return None

    # ── Response Building ───────────────────────────────────────────────

    def _get_trending(self, limit: int = 5) -> list[NewsArticle]:
        """Get top trending articles, preferring VIC-relevant and recent."""
        now = datetime.utcnow()
        recent = [
            a for a in self._news_cache
            if a.published and (now - a.published) < timedelta(days=3)
        ]
        # Fall back to all cached if nothing recent
        pool = recent if recent else self._news_cache
        return pool[:limit]

    def _format_news_context(self, articles: list[NewsArticle]) -> str:
        """Format news articles into LLM context."""
        if not articles:
            return "No trending news available at the moment."

        lines = ["TRENDING PROPERTY NEWS (Melbourne & Australia):"]
        for i, a in enumerate(articles, 1):
            date = a.published.strftime("%d %b") if a.published else "Recent"
            lines.append(f"\n{i}. [{date}] {a.title} — {a.source}")
            if a.summary:
                lines.append(f"   Summary: {a.summary[:150]}")
            lines.append(f"   Link: {a.link}")
            lines.append(f"   AU Relevance: {a.au_relevance:.0%}")

        return "\n".join(lines)

    def _build_prompt(
        self,
        user_message: str,
        news_context: str,
        history: list[dict],
    ) -> str:
        """Build the full prompt with conversation context."""
        parts = []

        # Recent conversation context (last 6 messages)
        recent_history = history[-7:-1]  # Exclude current message
        if recent_history:
            parts.append("CONVERSATION HISTORY:")
            for msg in recent_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                parts.append(f"{role}: {msg['content'][:200]}")
            parts.append("")

        # News context
        if news_context:
            parts.append(news_context)
            parts.append("")

        # Platform context
        parts.append(
            "PLATFORM CONTEXT: You are part of Property Insights Melbourne — "
            "a Bloomberg Terminal-style dashboard with 12 AI agents covering: "
            "property scouting, deal analysis, offer generation, investor profiling, "
            "deal structuring, negotiation coaching, due diligence, portfolio mentoring, "
            "and self-governance QA. We cover 134 suburbs across 15 Melbourne/VIC regions."
        )
        parts.append("")

        # User message
        parts.append(f"USER MESSAGE: {user_message}")

        return "\n".join(parts)

    def _fallback_response(
        self,
        user_message: str,
        trending: list[NewsArticle],
    ) -> str:
        """Generate a response when no LLM is available."""
        msg_lower = user_message.lower()

        # Check for news request
        if any(kw in msg_lower for kw in ["news", "trending", "headline", "latest", "update"]):
            if trending:
                lines = ["Here are the latest property news headlines:\n"]
                for i, a in enumerate(trending[:3], 1):
                    lines.append(f"{i}. **{a.title}** — _{a.source}_")
                    if a.summary:
                        lines.append(f"   {a.summary[:120]}")
                    lines.append(f"   [Read more]({a.link})")
                    lines.append("")
                lines.append(
                    "Want me to dive deeper into any of these? "
                    "Or ask about a specific suburb or investment topic!"
                )
                return "\n".join(lines)
            return (
                "I'm having trouble fetching the latest news right now. "
                "In the meantime, I can help with Melbourne suburb insights, "
                "investment strategies, or market analysis. What interests you?"
            )

        # Check for suburb query
        if any(kw in msg_lower for kw in ["suburb", "area", "where should", "best suburb"]):
            return (
                "Great question! Melbourne's market varies hugely by suburb. "
                "Our platform covers 134 suburbs across 15 regions — from "
                "inner-city Richmond to regional Ballarat. Try using the **Scout** "
                "button on the dashboard to search any VIC suburb and get instant "
                "market data including median prices, yields, and growth rates. "
                "Which area are you most interested in?"
            )

        # Check for investment strategy
        if any(kw in msg_lower for kw in ["invest", "strategy", "brrr", "yield", "cash flow", "growth"]):
            return (
                "Investment strategy depends on your goals and financial position. "
                "Our platform's **Profiler** agent can build your investor profile "
                "and recommend strategies (Buy & Hold, BRRR, negative gearing, etc.) "
                "tailored to your situation. Meanwhile, our **Analyst** agent scores "
                "every deal with a Bargain Score out of 100. Deals scoring 80+ are "
                "flagged as Golden Opportunities. What's your primary goal — "
                "cash flow, capital growth, or tax minimisation?"
            )

        # Default friendly response
        if trending:
            top = trending[0]
            return (
                f"Hey! I'm your Melbourne property market assistant. "
                f"The latest buzz: **{top.title}** ({top.source}). "
                f"I can chat about trending news, suburb insights, investment "
                f"strategies, or help you navigate our 12-agent deal analysis pipeline. "
                f"What would you like to explore?"
            )

        return (
            "Hey! I'm your Melbourne property market assistant. I can help with:\n\n"
            "📰 **Trending News** — Latest property headlines\n"
            "🏘️ **Suburb Insights** — Data on 134 VIC suburbs\n"
            "📊 **Market Analysis** — Yields, growth, auction clearance rates\n"
            "💡 **Investment Strategy** — BRRR, negative gearing, and more\n\n"
            "What would you like to explore?"
        )

    # ── News Endpoint Helpers ───────────────────────────────────────────

    async def get_trending_news(self, limit: int = 10) -> list[dict]:
        """Public method: get trending news articles."""
        await self._refresh_news_cache()
        trending = self._get_trending(limit=limit)
        return [a.to_dict() for a in trending]

    async def get_news_summary(self) -> AgentResult:
        """Generate an AI-powered summary of current trending news."""
        await self._refresh_news_cache()
        trending = self._get_trending(limit=8)

        if not trending:
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={
                    "summary": "No trending news available at the moment.",
                    "articles": [],
                },
            )

        news_context = self._format_news_context(trending)
        prompt = (
            f"{news_context}\n\n"
            "Generate a brief Melbourne market intelligence briefing (3-5 paragraphs) "
            "that summarises these headlines and explains what they mean for Melbourne "
            "property investors. Focus on actionable insights. Rate overall market "
            "sentiment: Bullish / Neutral / Bearish."
        )

        summary, tokens = await self.ask_llm(
            prompt=prompt,
            system=CHATBOT_SYSTEM_PROMPT,
            max_tokens=800,
            temperature=0.5,
        )

        if '"error"' in summary and "No LLM available" in summary:
            lines = ["**Melbourne Market Pulse** 📊\n"]
            for a in trending[:5]:
                lines.append(f"• **{a.title}** — _{a.source}_")
            lines.append(
                "\n_LLM unavailable for detailed analysis. "
                "Headlines sourced from Domain, REA, CoreLogic & AFR._"
            )
            summary = "\n".join(lines)
            tokens = 0

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "summary": summary,
                "articles": [a.to_dict() for a in trending],
                "sentiment": "neutral",
            },
            tokens_used=tokens,
        )

    def clear_session(self, session_id: str):
        """Clear conversation history for a session."""
        self._conversations.pop(session_id, None)
