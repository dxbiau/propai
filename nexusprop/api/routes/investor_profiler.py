"""
Investor Profiler API — personalised investment thesis generation.

Conducts an intelligent onboarding interview and produces a concrete
investment thesis that drives all subsequent agent behaviour.
"""

from __future__ import annotations

from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger("investor_profiler_api")
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class ProfilerChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    conversation_history: list[dict] = Field(
        default_factory=list,
        description="Previous messages: [{role: 'user'|'assistant', content: '...'}]"
    )
    session_id: Optional[str] = Field(None, description="Session ID for continuity")


class ThesisGenerationRequest(BaseModel):
    profile_data: dict = Field(..., description="Collected profile data from interview")
    session_id: Optional[str] = None


class ThesisUpdateRequest(BaseModel):
    update_request: str = Field(..., description="What the user wants to change")
    existing_thesis: dict = Field(..., description="Current investment thesis")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/chat", summary="Conduct investor profiling interview")
async def profiler_chat(req: ProfilerChatRequest):
    """
    Conduct an intelligent investor onboarding interview.

    Asks targeted questions to understand the investor's goals, finances,
    experience, and preferences. Returns a conversational response and
    signals when enough data has been collected to generate a thesis.
    """
    from nexusprop.agents.investor_profiler import InvestorProfilerAgent

    try:
        agent = InvestorProfilerAgent()
        result = await agent.execute(
            user_message=req.message,
            conversation_history=req.conversation_history,
            mode="interview",
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return {
            "response": result.data.get("response", ""),
            "stage": result.data.get("stage", ""),
            "ready_for_thesis": result.data.get("ready_for_thesis", False),
            "extracted_profile": result.data.get("extracted_profile", {}),
            "next_step": result.data.get("next_step", "continue_interview"),
            "tokens_used": result.tokens_used,
        }
    except Exception as e:
        logger.error("profiler_chat_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-thesis", summary="Generate personalised investment thesis")
async def generate_thesis(req: ThesisGenerationRequest):
    """
    Generate a comprehensive investment thesis from collected profile data.

    Produces specific, actionable recommendations including:
    - Target markets (states and suburbs)
    - Property criteria (type, size, price range)
    - Strategy recommendation (BTL, BRRR, HMO, etc.)
    - Financial targets (yield, growth, cash flow)
    - Risk assessment and mitigation strategies
    - Concrete next actions with timelines
    """
    from nexusprop.agents.investor_profiler import InvestorProfilerAgent

    try:
        agent = InvestorProfilerAgent()
        result = await agent.execute(
            user_message="",
            profile_data=req.profile_data,
            mode="generate_thesis",
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return {
            "thesis": result.data.get("thesis", {}),
            "thesis_summary": result.data.get("thesis_summary", ""),
            "search_filters": result.data.get("search_filters", {}),
            "next_actions": result.data.get("next_actions", []),
        }
    except Exception as e:
        logger.error("thesis_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-thesis", summary="Update existing investment thesis")
async def update_thesis(req: ThesisUpdateRequest):
    """
    Update an existing investment thesis based on new investor input.

    Allows investors to refine their thesis as their goals, finances,
    or market conditions change.
    """
    from nexusprop.agents.investor_profiler import InvestorProfilerAgent

    try:
        agent = InvestorProfilerAgent()
        result = await agent.execute(
            user_message=req.update_request,
            profile_data=req.existing_thesis,
            mode="update_thesis",
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return {
            "thesis": result.data.get("thesis", {}),
            "updated": result.data.get("updated", False),
        }
    except Exception as e:
        logger.error("thesis_update_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies", summary="Get all available investment strategies")
async def get_strategies():
    """Return all supported investment strategies with descriptions."""
    return {
        "strategies": [
            {
                "id": "btl",
                "name": "Buy & Hold (BTL)",
                "description": "Purchase and hold long-term for capital growth and rental income",
                "best_for": "Long-term wealth building, negative gearing benefits",
                "capital_required": "medium",
                "complexity": "low",
                "typical_yield_pct": "3-5%",
                "typical_growth_pct": "5-10% p.a.",
                "australian_context": "Most common strategy. Suits PAYG investors with high marginal tax rates for negative gearing benefits.",
            },
            {
                "id": "brrr",
                "name": "BRRR (Buy, Renovate, Rent, Refinance, Repeat)",
                "description": "Buy below market, add value through renovation, refinance at new value to recycle capital",
                "best_for": "Forced equity creation, capital recycling, faster portfolio growth",
                "capital_required": "medium-high",
                "complexity": "medium",
                "typical_yield_pct": "5-7% post-renovation",
                "typical_growth_pct": "Immediate 15-25% forced equity + market growth",
                "australian_context": "Highly effective in markets with undersupply of renovated stock. Requires builder relationships and project management skills.",
            },
            {
                "id": "hmo",
                "name": "HMO / Co-living",
                "description": "Rent individual rooms rather than the whole property",
                "best_for": "Maximum yield, urban markets with high rental demand",
                "capital_required": "medium",
                "complexity": "high",
                "typical_yield_pct": "8-12%",
                "typical_growth_pct": "4-7% p.a.",
                "australian_context": "Growing strategy in Sydney, Melbourne, Brisbane. Council approval required in most LGAs. Strong demand from students, young professionals.",
            },
            {
                "id": "subdivision",
                "name": "Subdivision / Development",
                "description": "Subdivide land or develop multiple dwellings for profit",
                "best_for": "Large capital gains, experienced investors",
                "capital_required": "high",
                "complexity": "very_high",
                "typical_yield_pct": "N/A (development profit)",
                "typical_growth_pct": "20-40% profit on cost",
                "australian_context": "Requires R2/R3 zoning, council DA approval, builder relationships. Significant holding costs during development.",
            },
            {
                "id": "off_plan",
                "name": "Off-the-Plan",
                "description": "Purchase before construction for depreciation benefits and potential capital growth",
                "best_for": "Depreciation benefits, lower entry price, SMSF investors",
                "capital_required": "low-medium",
                "complexity": "medium",
                "typical_yield_pct": "4-6%",
                "typical_growth_pct": "Variable — settlement risk if market falls",
                "australian_context": "Strong depreciation schedule (Division 43 + Division 40). Settlement risk in oversupplied markets. Stamp duty concessions in some states.",
            },
            {
                "id": "r2sa",
                "name": "Rent-to-Serviced Accommodation (R2SA)",
                "description": "Lease a property and sublease as short-term accommodation (Airbnb/corporate)",
                "best_for": "High cash flow without ownership capital",
                "capital_required": "low",
                "complexity": "high",
                "typical_yield_pct": "15-25% on invested capital",
                "typical_growth_pct": "N/A (no ownership)",
                "australian_context": "Requires landlord permission and council approval. Strong in tourist areas and CBDs. Regulatory risk from council restrictions.",
            },
        ]
    }
