"""
StateMarketAgent — Per-state market intelligence for all 8 Australian states/territories.

Provides:
  • State-specific market snapshots with real data
  • RBA and macro-economic context per state
  • Key infrastructure projects impacting property values
  • Investment strategy recommendations by state
  • Rental yield heatmaps by corridor
  • State comparison and ranking

This is the "Bloomberg Terminal" intelligence layer — factual data
enriched with AI-generated insights when LLM is available.
"""

from __future__ import annotations

from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.market_data import (
    STATE_MARKET_DATA,
    RBA_DATA,
    WEEKLY_AUCTION_RESULTS,
    PRICE_INDEX_TIMELINE,
    INVESTMENT_INSIGHTS,
    get_national_summary,
    get_state_comparison,
    get_state_data,
    get_rba_snapshot,
    get_investment_insights,
    get_ticker_data,
    get_dashboard_kpis,
)
from nexusprop.locations import AUSTRALIAN_REGIONS, get_regions_for_state

# ── State-level strategy templates ──────────────────────────────────────────

STATE_STRATEGIES: dict[str, dict] = {
    "NSW": {
        "hotspots": ["Parramatta", "Penrith", "Newcastle", "Wollongong", "Liverpool"],
        "strategy": "Focus on Western Sydney Airport corridor (2026) and Metro West stations. "
                     "Inner-west terraces for renovation plays. Hunter Valley for affordability + yield.",
        "risk_factors": ["High entry cost", "Foreign buyer surcharge 8%", "Land tax threshold $1.075M"],
        "infrastructure": [
            "Western Sydney Airport (2026)",
            "Sydney Metro West (2032)",
            "WestConnex M4-M5 Link",
            "Parramatta Light Rail Stage 2",
        ],
    },
    "VIC": {
        "hotspots": ["Footscray", "Werribee", "Geelong", "Pakenham", "Craigieburn"],
        "strategy": "Melbourne's west and north are growth corridors. Suburban Rail Loop will "
                     "transform middle suburbs by 2035. Geelong fast rail expanding commuter belt. "
                     "Regional VIC (Ballarat, Bendigo) offers yield plays under $500K.",
        "risk_factors": ["Oversupply in CBD apartments", "Rising land tax", "Vacancy rate lifting"],
        "infrastructure": [
            "Suburban Rail Loop (2035)",
            "Melbourne Airport Rail (2029)",
            "West Gate Tunnel",
            "Geelong Fast Rail",
        ],
    },
    "QLD": {
        "hotspots": ["Woolloongabba", "Logan", "Ipswich", "Gold Coast", "Sunshine Coast"],
        "strategy": "2032 Olympics is the main catalyst — Woolloongabba (Gabba rebuild), "
                     "Cross River Rail (2025) opening new precincts. Logan and Ipswich for "
                     "yield + growth. Interstate migration #1 driver nationally. "
                     "Gold Coast light rail Stage 4 extending reach.",
        "risk_factors": ["Insurance costs rising (flood/cyclone)", "Body corp levies high coast", "FIRB restrictions"],
        "infrastructure": [
            "2032 Brisbane Olympics",
            "Cross River Rail (2025)",
            "Gold Coast Light Rail Stage 3C",
            "Inland Rail Brisbane–Melbourne",
        ],
    },
    "SA": {
        "hotspots": ["Elizabeth", "Osborne", "Salisbury", "Norwood", "Port Adelaide"],
        "strategy": "AUKUS submarine program (BAE Systems Osborne) creating 30-year jobs pipeline. "
                     "Northern Adelaide surging 18%+. South Road Tunnel transforming outer north. "
                     "Adelaide is cheapest capital — strong yield + growth potential.",
        "risk_factors": ["Smaller market = less liquidity", "Limited infrastructure pipeline", "Ageing housing stock"],
        "infrastructure": [
            "AUKUS Submarine Build (Osborne)",
            "South Road Tunnel (Torrens to Darlington)",
            "Adelaide rail electrification",
            "Lot Fourteen innovation precinct",
        ],
    },
    "WA": {
        "hotspots": ["Armadale", "Rockingham", "Baldivis", "Midland", "Fremantle"],
        "strategy": "Perth is Australia's hottest market — 18.5% growth YoY and accelerating. "
                     "METRONET adding 8 new stations. Mining boom 3.0 driving FIFO demand. "
                     "Armadale line extension (Byford) creating new growth corridor. "
                     "Extremely tight vacancy rates (<1%) mean rents surging.",
        "risk_factors": ["Mining cycle dependency", "Water security concerns", "Isolated market"],
        "infrastructure": [
            "METRONET (8 new stations)",
            "Byford Rail Extension",
            "Westport Outer Harbour",
            "Perth City Deal activation",
        ],
    },
    "TAS": {
        "hotspots": ["Hobart CBD", "Glenorchy", "Launceston", "Devonport"],
        "strategy": "Hobart City Deal transforming waterfront (Macquarie Point). "
                     "Tourism-driven Airbnb yields strong. Launceston revitalising. "
                     "Affordable entry point vs mainland capitals. Limited supply = price support.",
        "risk_factors": ["Small market", "Limited rental supply", "Seasonal tourism dependency"],
        "infrastructure": [
            "Hobart City Deal",
            "Macquarie Point Renewal",
            "Bridgewater Bridge",
            "Launceston City Heart",
        ],
    },
    "NT": {
        "hotspots": ["Darwin CBD", "Palmerston", "Zuccoli"],
        "strategy": "Highest yields nationally (6%+ gross). Darwin City Deal and Middle Arm "
                     "development (gas hub) creating jobs. US Marine rotation boosting demand. "
                     "No stamp duty for FHB <$525K. Defence spending underpinning.",
        "risk_factors": ["Cyclone insurance costs", "Population volatility", "Small transient market"],
        "infrastructure": [
            "Darwin City Deal",
            "Middle Arm Sustainable Development Precinct",
            "Ship Lift and Marine Industry Park",
            "US Force Posture Initiative",
        ],
    },
    "ACT": {
        "hotspots": ["Braddon", "Molonglo Valley", "Belconnen", "Gungahlin"],
        "strategy": "Recession-proof (government incomes). Light Rail Stage 2A (Woden) "
                     "will transform south Canberra. ACT transitioning to land tax "
                     "(no more stamp duty) — reduces purchase barrier. "
                     "Highest average household income in Australia.",
        "risk_factors": ["Government policy dependent", "Controlled land release", "High entry price relative to yield"],
        "infrastructure": [
            "Light Rail Stage 2A (Woden)",
            "Molonglo Valley Stage 3",
            "Canberra Hospital Expansion",
            "New CIT Woden Campus",
        ],
    },
}


class StateMarketAgent(BaseAgent):
    """
    Per-state market intelligence agent.

    Provides comprehensive market data, strategy recommendations,
    infrastructure impact analysis, and investment insights for
    any Australian state or territory.
    """

    def __init__(self):
        super().__init__("StateMarket")

    async def execute(
        self,
        state: Optional[str] = None,
        include_rba: bool = True,
        include_auction: bool = True,
    ) -> AgentResult:
        """
        Get comprehensive market intelligence for a state or nationally.

        Args:
            state: State code (e.g. "NSW", "VIC"). None = national summary.
            include_rba: Include RBA/macro data.
            include_auction: Include weekly auction results.
        """
        self.logger.info("state_market_query", state=state)

        if state and state.upper() in STATE_MARKET_DATA:
            result = self._state_report(state.upper(), include_rba, include_auction)
        else:
            result = self._national_report(include_rba, include_auction)

        return AgentResult(
            agent_name=self.name,
            success=True,
            data=result,
        )

    async def get_state_comparison(self) -> AgentResult:
        """Rank all states by key metrics for investor comparison."""
        comparison = get_state_comparison()
        return AgentResult(
            agent_name=self.name,
            success=True,
            data={"comparison": comparison},
        )

    async def get_investment_strategy(self, state: str) -> AgentResult:
        """Get investment strategy for a specific state."""
        state = state.upper()
        strategy = STATE_STRATEGIES.get(state)
        if not strategy:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Unknown state: {state}",
            )

        market = STATE_MARKET_DATA.get(state, {})
        regions = get_regions_for_state(state)

        # Build AI prompt for enriched strategy (if LLM available)
        prompt = (
            f"You are a senior property investment analyst specialising in {state}.\n"
            f"Market data: median house ${market.get('median_house', 0):,.0f}, "
            f"growth {market.get('annual_growth_pct', 0):.1f}%, "
            f"yield {market.get('gross_rental_yield_pct', 0):.1f}%.\n"
            f"Hotspots: {', '.join(strategy['hotspots'])}.\n"
            f"Infrastructure: {', '.join(strategy['infrastructure'])}.\n\n"
            f"Provide 3 specific actionable investment strategies for {state} in 2024-2025."
        )

        ai_insight = None
        try:
            text, tokens = await self.ask_llm(prompt, max_tokens=1024, temperature=0.4)
            if text:
                ai_insight = text
        except Exception:
            pass

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "state": state,
                "strategy": strategy,
                "market_snapshot": market,
                "regions": list(regions.keys()) if regions else [],
                "ai_insight": ai_insight,
            },
        )

    def _state_report(
        self, state: str, include_rba: bool, include_auction: bool
    ) -> dict:
        """Build comprehensive report for a single state."""
        market = get_state_data(state)
        strategy = STATE_STRATEGIES.get(state, {})
        regions = get_regions_for_state(state)

        report = {
            "state": state,
            "market_data": market,
            "strategy": strategy,
            "regions": list(regions.keys()) if regions else [],
            "suburb_count": sum(len(v) for v in regions.values()) if regions else 0,
            "kpis": get_dashboard_kpis(),
        }

        if include_rba:
            report["rba"] = get_rba_snapshot()

        if include_auction:
            capital_map = {
                "NSW": "Sydney", "VIC": "Melbourne", "QLD": "Brisbane",
                "SA": "Adelaide", "WA": "Perth", "TAS": "Hobart",
                "NT": "Darwin", "ACT": "Canberra",
            }
            city = capital_map.get(state)
            if city:
                for result in WEEKLY_AUCTION_RESULTS:
                    if result["city"] == city:
                        report["auction_results"] = result
                        break

        report["insights"] = get_investment_insights()

        return report

    def _national_report(self, include_rba: bool, include_auction: bool) -> dict:
        """Build national summary report."""
        report = {
            "national_summary": get_national_summary(),
            "state_comparison": get_state_comparison(),
            "ticker": get_ticker_data(),
            "kpis": get_dashboard_kpis(),
            "insights": get_investment_insights(),
        }

        if include_rba:
            report["rba"] = get_rba_snapshot()

        if include_auction:
            report["auction_results"] = WEEKLY_AUCTION_RESULTS

        report["price_index"] = PRICE_INDEX_TIMELINE

        return report
