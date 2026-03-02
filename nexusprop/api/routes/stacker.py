"""
API routes for the Stacker Agent — deal structuring, entity selection, tax optimisation.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from nexusprop.agents.stacker import StackerAgent
from nexusprop.models.investment import InvestmentProfile, DealStructure
from nexusprop.models.deal import Deal

router = APIRouter()

_stacker = StackerAgent()

# Store structured deals for retrieval
_structure_store: dict[str, list[dict]] = {}


class StackRequest(BaseModel):
    deal: dict = Field(..., description="Deal data to structure")
    investor_profile: Optional[dict] = None
    strategies: Optional[list[str]] = None


class StackResponse(BaseModel):
    deal_address: str
    scenario_count: int
    scenarios: list[dict]
    analysis: str
    best_scenario: Optional[dict] = None


@router.post("/structure", response_model=StackResponse)
async def structure_deal(req: StackRequest):
    """Generate 1-3 deal structuring scenarios with entity, financing, tax and risk analysis."""
    try:
        deal = Deal(**req.deal)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid deal data: {e}")

    profile = None
    if req.investor_profile:
        try:
            profile = InvestmentProfile(**req.investor_profile)
        except Exception:
            pass  # proceed without profile

    result = await _stacker.safe_execute(
        deal=deal,
        investor_profile=profile,
        strategies=req.strategies,
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    data = result.data or {}
    scenarios = data.get("scenarios", [])

    # Store for later retrieval
    deal_key = deal.address or str(deal.id)
    _structure_store[deal_key] = scenarios

    # Find best scenario (highest cash-on-cash return)
    best = None
    if scenarios:
        best = max(scenarios, key=lambda s: s.get("cash_on_cash_return", 0))

    return StackResponse(
        deal_address=deal_key,
        scenario_count=len(scenarios),
        scenarios=scenarios,
        analysis=data.get("analysis", ""),
        best_scenario=best,
    )


@router.get("/structures")
async def list_structures():
    """List all stored deal structures."""
    return {
        "count": len(_structure_store),
        "deals": {
            k: {"scenarios": len(v)} for k, v in _structure_store.items()
        },
    }


@router.get("/structures/{deal_key}")
async def get_structure(deal_key: str):
    """Get stored scenarios for a deal."""
    scenarios = _structure_store.get(deal_key)
    if not scenarios:
        raise HTTPException(status_code=404, detail="No structures found for this deal")
    return {"deal_key": deal_key, "scenarios": scenarios}
