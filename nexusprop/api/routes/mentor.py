"""
API routes for the Mentor Agent — coaching, education, market commentary.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from nexusprop.agents.mentor import MentorAgent
from nexusprop.models.investment import InvestmentProfile

router = APIRouter()

_mentor = MentorAgent()


class MentorRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Your property investment question")
    topic: Optional[str] = Field(
        None,
        description="Topic hint: market_commentary, strategy_education, portfolio_review, "
                    "suburb_deepdive, deal_review, next_steps, general_coaching",
    )
    investor_profile: Optional[dict] = None
    context: Optional[dict] = None


class MentorResponse(BaseModel):
    topic: str
    response: str
    experience_level: str
    follow_up_topics: list[str]


@router.post("/ask", response_model=MentorResponse)
async def ask_mentor(req: MentorRequest):
    """Ask the Mentor agent any property investment question."""
    profile = None
    if req.investor_profile:
        try:
            profile = InvestmentProfile(**req.investor_profile)
        except Exception:
            pass

    result = await _mentor.safe_execute(
        user_input=req.question,
        topic=req.topic,
        investor_profile=profile,
        context=req.context or {},
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    data = result.data or {}

    return MentorResponse(
        topic=data.get("topic", req.topic or "general_coaching"),
        response=data.get("response", ""),
        experience_level=data.get("experience_level", "intermediate"),
        follow_up_topics=data.get("follow_up_topics", []),
    )


class WeeklyBriefRequest(BaseModel):
    investor_profile: Optional[dict] = None
    market_data: Optional[dict] = None
    portfolio: Optional[dict] = None


@router.post("/brief")
async def weekly_brief(req: WeeklyBriefRequest):
    """Generate a personalized weekly market brief."""
    profile = None
    if req.investor_profile:
        try:
            profile = InvestmentProfile(**req.investor_profile)
        except Exception:
            pass

    result = await _mentor.generate_weekly_brief(
        investor_profile=profile,
        market_data=req.market_data or {},
        portfolio_data=req.portfolio or {},
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data


@router.get("/topics")
async def list_topics():
    """List available coaching topics."""
    return {
        "topics": [
            {"key": "market_commentary", "label": "Market Commentary", "description": "Analysis of current Australian property market conditions"},
            {"key": "strategy_education", "label": "Strategy Education", "description": "Learn about BTL, BRRR, R2R, flipping, HMOs, development"},
            {"key": "portfolio_review", "label": "Portfolio Review", "description": "Analysis of your existing portfolio with optimisation suggestions"},
            {"key": "suburb_deepdive", "label": "Suburb Deep Dive", "description": "Detailed analysis of a specific suburb or area"},
            {"key": "deal_review", "label": "Deal Review", "description": "Review and critique a specific deal you're considering"},
            {"key": "next_steps", "label": "Next Steps", "description": "Personalised action plan based on your situation"},
            {"key": "general_coaching", "label": "General Coaching", "description": "Any property investment question"},
        ]
    }
