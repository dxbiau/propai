"""
Market Data API — national market intelligence endpoints.

Bloomberg Terminal-grade data for the Australian property market.
"""

from fastapi import APIRouter

from nexusprop.market_data import (
    get_national_summary,
    get_state_comparison,
    get_state_data,
    get_rba_snapshot,
    get_investment_insights,
    get_ticker_data,
    get_dashboard_kpis,
    STATE_MARKET_DATA,
    WEEKLY_AUCTION_RESULTS,
    PRICE_INDEX_TIMELINE,
)

router = APIRouter(tags=["Market Data"])


@router.get("/national")
async def national_summary():
    """National property market summary with all KPIs."""
    return {
        "summary": get_national_summary(),
        "kpis": get_dashboard_kpis(),
        "ticker": get_ticker_data(),
    }


@router.get("/rba")
async def rba_snapshot():
    """RBA and macro-economic data snapshot."""
    return get_rba_snapshot()


@router.get("/states")
async def state_comparison():
    """Compare all states side-by-side."""
    return {
        "comparison": get_state_comparison(),
        "states": list(STATE_MARKET_DATA.keys()),
    }


@router.get("/states/{state}")
async def state_detail(state: str):
    """Detailed market data for a specific state."""
    state = state.upper()
    data = get_state_data(state)
    if not data:
        return {"error": f"Unknown state: {state}"}
    return {
        "state": state,
        "data": data,
    }


@router.get("/auctions")
async def auction_results():
    """Weekly auction clearance results for all capitals."""
    return {"results": WEEKLY_AUCTION_RESULTS}


@router.get("/price-index")
async def price_index():
    """National price index timeline (indexed to 100 = Jan 2020)."""
    return {"timeline": PRICE_INDEX_TIMELINE}


@router.get("/insights")
async def investment_insights():
    """Curated investment insights and actionable recommendations."""
    return {"insights": get_investment_insights()}


@router.get("/ticker")
async def ticker_data():
    """Real-time ticker data for the terminal header."""
    return {"ticker": get_ticker_data()}
