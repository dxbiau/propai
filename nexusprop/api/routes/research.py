"""
Personal Research API - paste a link, get everything.

Endpoints for personal property research, climate risk profiling,
and nearby property discovery.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from nexusprop.agents.personal_research import (
    PersonalResearchAgent,
    extract_property_info_from_url,
    find_nearby_suburbs,
)
from nexusprop.climate_risk import (
    get_suburb_climate_risk,
    get_state_climate_summary,
    get_climate_comparison,
    get_national_climate_overview,
    assess_property_climate,
)

router = APIRouter(tags=["Personal Research"])

_agent = PersonalResearchAgent()


# ─── Request Models ──────────────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    """Paste a property URL and get full research."""
    url: str = Field("", description="Property URL from Domain, REA, AllHomes, or any link")
    suburb: Optional[str] = Field(None, description="Override suburb if known")
    state: Optional[str] = Field(None, description="Override state if known")
    postcode: Optional[str] = Field(None, description="Postcode if known")
    property_type: str = Field("house", description="house, unit, apartment, etc.")
    private: bool = Field(False, description="Keep this research private (not added to DB)")
    include_climate: bool = Field(True, description="Include climate risk profiling")
    include_nearby: bool = Field(True, description="Include nearby suburb discovery")
    flood_zone: Optional[bool] = Field(None, description="Is property in a known flood zone?")
    bushfire_zone: Optional[bool] = Field(None, description="Is property in a bushfire zone?")


class ClimateCompareRequest(BaseModel):
    """Compare climate risk across multiple suburbs."""
    suburbs: list[str] = Field(..., description="List of suburb names to compare", min_length=1, max_length=10)


class NearbyRequest(BaseModel):
    """Find nearby suburbs."""
    suburb: str
    state: str
    radius: int = Field(5, ge=1, le=20)


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/research")
async def research_property(req: ResearchRequest):
    """
    Full personal research - paste a property URL and get:
    - URL analysis (source detection, suburb/state extraction)
    - Climate risk profiling (flood, bushfire, cyclone, heat, erosion)
    - Nearby properties in the same region
    - Market data overlay
    - AI-enriched investment analysis
    """
    result = await _agent.execute(req.model_dump())
    return result.to_dict()


@router.post("/parse-url")
async def parse_property_url(url: str = ""):
    """Parse a property URL and extract suburb, state, source info."""
    return extract_property_info_from_url(url)


@router.get("/climate/{suburb}")
async def get_climate_risk(suburb: str):
    """Get detailed climate risk profile for a suburb."""
    return get_suburb_climate_risk(suburb)


@router.get("/climate/state/{state}")
async def get_state_climate(state: str):
    """Get state-level climate risk summary."""
    return get_state_climate_summary(state)


@router.get("/climate/national/overview")
async def national_climate():
    """National climate risk overview for Australian property investment."""
    return get_national_climate_overview()


@router.post("/climate/compare")
async def compare_climate(req: ClimateCompareRequest):
    """Compare climate risk across multiple suburbs side-by-side."""
    return get_climate_comparison(req.suburbs)


@router.post("/climate/assess")
async def assess_climate(
    suburb: str,
    state: str,
    property_type: str = "house",
    flood_zone: Optional[bool] = None,
    bushfire_zone: Optional[bool] = None,
):
    """Full property-specific climate risk assessment with insurance estimate."""
    return assess_property_climate(suburb, state, property_type, flood_zone, bushfire_zone)


@router.post("/nearby")
async def find_nearby(req: NearbyRequest):
    """Find nearby suburbs in the same region with market data."""
    nearby = find_nearby_suburbs(req.suburb, req.state, req.radius)
    return {
        "target": {"suburb": req.suburb, "state": req.state},
        "nearby_count": len(nearby),
        "nearby": nearby,
        "climate_comparison": get_climate_comparison(
            [req.suburb] + [n["suburb"] for n in nearby[:5]]
        ) if nearby else None,
    }
