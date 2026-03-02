"""
API routes for the Profiler Agent — investor profile management.
"""

from __future__ import annotations

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from nexusprop.agents.profiler import ProfilerAgent
from nexusprop.models.investment import InvestmentProfile

router = APIRouter()

# In-memory profile store
_profile_store: dict[str, InvestmentProfile] = {}

# Singleton agent
_profiler = ProfilerAgent()


class ProfileRequest(BaseModel):
    user_input: str = Field(..., min_length=5, description="Tell us about your investment situation")
    profile_id: Optional[str] = None


class ProfileResponse(BaseModel):
    profile_id: str
    completeness: float
    readiness: float
    borrowing_power: float
    max_purchase: float
    next_questions: list[str]
    profile: dict


@router.post("/build", response_model=ProfileResponse)
async def build_profile(req: ProfileRequest):
    """Build or update an investor profile from natural language input."""
    existing = _profile_store.get(req.profile_id) if req.profile_id else None

    result = await _profiler.safe_execute(
        user_input=req.user_input,
        existing_profile=existing,
        interaction_type="initial" if not existing else "update",
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    data = result.data or {}
    profile_data = data.get("profile", {})

    try:
        profile = InvestmentProfile(**profile_data)
    except Exception:
        profile = existing or InvestmentProfile()

    pid = req.profile_id or str(profile.id)
    _profile_store[pid] = profile

    return ProfileResponse(
        profile_id=pid,
        completeness=data.get("completeness", 0),
        readiness=data.get("readiness", 0),
        borrowing_power=data.get("borrowing_power", 0),
        max_purchase=data.get("max_purchase", 0),
        next_questions=data.get("next_questions", []),
        profile=profile_data,
    )


@router.get("/{profile_id}")
async def get_profile(profile_id: str):
    """Get an existing investor profile."""
    profile = _profile_store.get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile.model_dump(mode="json")


@router.get("/")
async def list_profiles():
    """List all profiles (demo mode)."""
    return {
        "count": len(_profile_store),
        "profiles": {
            pid: {
                "readiness": p.investor_readiness_score,
                "completeness": p.profile_completeness_pct,
                "experience": p.experience_level.value,
                "goal": p.primary_goal.value,
                "max_purchase": p.max_next_purchase,
            }
            for pid, p in _profile_store.items()
        },
    }


@router.post("/{profile_id}/report")
async def generate_report(profile_id: str):
    """Generate a comprehensive investor profile report."""
    profile = _profile_store.get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    result = await _profiler.generate_profile_report(profile)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data
