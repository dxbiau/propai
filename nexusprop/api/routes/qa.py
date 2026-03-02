"""
API routes for the QA Agent — self-governance, performance monitoring, skill evolution.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from nexusprop.agents.qa import QAAgent

router = APIRouter()

_qa = QAAgent()


class EvaluateRequest(BaseModel):
    pipeline_results: dict = Field(..., description="Dict of agent_name -> result data")


@router.post("/evaluate")
async def evaluate_pipeline(req: EvaluateRequest):
    """Evaluate pipeline outputs and trigger self-improvement if needed."""
    result = await _qa.safe_execute(
        mode="evaluate",
        pipeline_results=req.pipeline_results,
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data


@router.get("/health")
async def health_check():
    """System-wide agent health dashboard."""
    result = await _qa.safe_execute(mode="health_check")

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data


@router.get("/trends")
async def performance_trends():
    """Analyse performance trends across all agents."""
    result = await _qa.safe_execute(mode="analyze_trends")

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data


@router.get("/summary")
async def performance_summary():
    """Get a quick performance summary for all agents."""
    return _qa.get_performance_summary()


@router.post("/improve/{agent_name}")
async def generate_skill(agent_name: str):
    """Generate an improved skill template for a specific agent."""
    result = await _qa.safe_execute(
        mode="generate_skill",
        agent_name=agent_name,
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data


@router.get("/skill/{agent_name}")
async def get_skill(agent_name: str):
    """Get the current skill template for an agent (if evolved)."""
    skill = _qa.get_agent_skill(agent_name)
    if not skill:
        return {"agent": agent_name, "skill": None, "message": "No evolved skill — using base prompt"}
    return {"agent": agent_name, "skill": skill.model_dump(mode="json")}


@router.post("/evaluate-and-improve")
async def full_governance_cycle(req: EvaluateRequest):
    """Run the full self-governance cycle: evaluate → detect trends → improve weak agents."""
    result = await _qa.evaluate_and_improve(req.pipeline_results)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return result.data
