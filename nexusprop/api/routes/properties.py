"""
Properties API — search, filter, and retrieve property listings.

Melbourne + VIC Specialist — provides CRUD-style access to the
property intelligence layer with value-add suggestions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from nexusprop.models.property import Property, PropertySource, PropertyType
from nexusprop.locations import (
    get_location_tree,
    get_location_summary,
    get_all_suburbs_for_state,
    get_suburbs_for_region,
    search_suburbs as location_search_suburbs,
    get_all_suburbs,
    AUSTRALIAN_REGIONS,
)

logger = structlog.get_logger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# Request/Response Schemas
# ---------------------------------------------------------------------------


class PropertySearchRequest(BaseModel):
    """Search filters for property listings."""
    suburbs: list[str] = Field(default_factory=list, description="Target suburbs")
    states: list[str] = Field(default_factory=list, description="Target states (NSW, VIC, etc.)")
    postcodes: list[str] = Field(default_factory=list, description="Target postcodes")
    property_types: list[PropertyType] = Field(default_factory=list)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_bedrooms: Optional[int] = Field(None, ge=0)
    max_bedrooms: Optional[int] = Field(None, ge=0)
    min_land_size_sqm: Optional[float] = Field(None, ge=0)
    distress_only: bool = Field(default=False, description="Only show distressed properties")
    source: Optional[PropertySource] = None
    min_bargain_score: Optional[float] = Field(None, ge=0, le=100)
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class PropertyListResponse(BaseModel):
    """Paginated property list response."""
    total: int
    limit: int
    offset: int
    properties: list[Property]


class ScoutTriggerRequest(BaseModel):
    """Trigger a new scraping run."""
    states: list[str] = Field(default_factory=lambda: ["NSW"])
    suburbs: list[str] = Field(default_factory=list)
    max_agencies: int = Field(default=10, ge=1, le=50)
    use_browser: bool = False


class ScoutTriggerResponse(BaseModel):
    """Result of a scraping trigger."""
    run_id: str
    status: str
    properties_found: int
    duration_seconds: float
    errors: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# In-memory store (MVP — replaced by DB in production)
# ---------------------------------------------------------------------------
_property_store: dict[str, Property] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=PropertyListResponse)
async def list_properties(
    suburb: Optional[str] = Query(None, description="Filter by suburb"),
    state: Optional[str] = Query(None, description="Filter by state"),
    property_type: Optional[PropertyType] = Query(None, alias="type"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_bedrooms: Optional[int] = Query(None, ge=0),
    distress_only: bool = Query(False),
    source: Optional[PropertySource] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|price|bedrooms|land_size)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    List all properties with optional filtering and pagination.

    Supports filtering by suburb, state, property type, price range,
    bedrooms, distress status, and source.
    """
    properties = list(_property_store.values())

    # Apply filters
    if suburb:
        properties = [p for p in properties if p.suburb and suburb.lower() in p.suburb.lower()]
    if state:
        properties = [p for p in properties if p.state and state.upper() == p.state.upper()]
    if property_type:
        properties = [p for p in properties if p.property_type == property_type]
    if min_price is not None:
        properties = [p for p in properties if (p.effective_price or 0) >= min_price]
    if max_price is not None:
        properties = [p for p in properties if (p.effective_price or 0) <= max_price]
    if min_bedrooms is not None:
        properties = [p for p in properties if (p.bedrooms or 0) >= min_bedrooms]
    if distress_only:
        properties = [p for p in properties if p.distress_signals]
    if source:
        properties = [p for p in properties if p.source == source]

    # Sort
    sort_map = {
        "created_at": lambda p: p.created_at or datetime.min,
        "price": lambda p: p.effective_price or 0,
        "bedrooms": lambda p: p.bedrooms or 0,
        "land_size": lambda p: p.land_size_sqm or 0,
    }
    properties.sort(key=sort_map.get(sort_by, sort_map["created_at"]), reverse=True)

    total = len(properties)
    paginated = properties[offset:offset + limit]

    return PropertyListResponse(
        total=total,
        limit=limit,
        offset=offset,
        properties=paginated,
    )


# ---------------------------------------------------------------------------
# Location Scout Endpoints (MUST be before /{property_id} to avoid route clash)
# ---------------------------------------------------------------------------

@router.get("/locations/tree")
async def location_tree():
    """Return the full location hierarchy: state → region → suburbs."""
    tree = get_location_tree()
    summary = get_location_summary()
    return {
        "tree": tree,
        "summary": summary,
    }


@router.get("/locations/regions")
async def location_regions(state: str = Query(..., description="State code e.g. NSW, VIC")):
    """Return regions and their suburbs for a given state."""
    state_upper = state.upper()
    if state_upper not in AUSTRALIAN_REGIONS:
        raise HTTPException(status_code=404, detail=f"No location data for state: {state}")
    regions = {}
    for region_name, suburbs in AUSTRALIAN_REGIONS[state_upper].items():
        regions[region_name] = suburbs  # Each suburb dict has full data
    return {"state": state_upper, "regions": regions}


@router.get("/locations/search")
async def location_search(q: str = Query(..., min_length=2, description="Search query for suburb or postcode")):
    """Search for suburbs by name or postcode."""
    results = location_search_suburbs(q)
    return {"query": q, "results": results[:20]}


@router.get("/locations/stats")
async def location_stats():
    """Return summary statistics for the location database and current property data."""
    summary = get_location_summary()

    # Also compute per-state property counts from current store
    state_counts: dict[str, int] = {}
    for prop in _property_store.values():
        st = prop.state or "UNKNOWN"
        state_counts[st] = state_counts.get(st, 0) + 1

    # Count shadow/off-market listings
    shadow_count = sum(
        1 for prop in _property_store.values()
        if prop.source in (PropertySource.OFF_MARKET, PropertySource.COMING_SOON, PropertySource.BOUTIQUE_AGENCY)
    )

    return {
        **summary,
        "state_property_counts": state_counts,
        "total_properties": len(_property_store),
        "shadow_listings": shadow_count,
    }


# ---------------------------------------------------------------------------
# Single Property Retrieval (after /locations/* routes)
# ---------------------------------------------------------------------------

@router.get("/{property_id}", response_model=Property)
async def get_property(property_id: str):
    """Retrieve a single property by ID."""
    prop = _property_store.get(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.post("/search", response_model=PropertyListResponse)
async def search_properties(search: PropertySearchRequest):
    """
    Advanced property search with multiple filters.

    POST body allows complex filter combinations.
    """
    properties = list(_property_store.values())

    if search.suburbs:
        suburbs_lower = [s.lower() for s in search.suburbs]
        properties = [p for p in properties if p.suburb and p.suburb.lower() in suburbs_lower]
    if search.states:
        states_upper = [s.upper() for s in search.states]
        properties = [p for p in properties if p.state and p.state.upper() in states_upper]
    if search.postcodes:
        properties = [p for p in properties if p.postcode and p.postcode in search.postcodes]
    if search.property_types:
        properties = [p for p in properties if p.property_type in search.property_types]
    if search.min_price is not None:
        properties = [p for p in properties if (p.effective_price or 0) >= search.min_price]
    if search.max_price is not None:
        properties = [p for p in properties if (p.effective_price or 0) <= search.max_price]
    if search.min_bedrooms is not None:
        properties = [p for p in properties if (p.bedrooms or 0) >= search.min_bedrooms]
    if search.max_bedrooms is not None:
        properties = [p for p in properties if (p.bedrooms or 0) <= search.max_bedrooms]
    if search.min_land_size_sqm is not None:
        properties = [p for p in properties if (p.land_size_sqm or 0) >= search.min_land_size_sqm]
    if search.distress_only:
        properties = [p for p in properties if p.distress_signals]
    if search.source:
        properties = [p for p in properties if p.source == search.source]

    total = len(properties)
    paginated = properties[search.offset:search.offset + search.limit]

    return PropertyListResponse(
        total=total,
        limit=search.limit,
        offset=search.offset,
        properties=paginated,
    )


@router.post("/scout", response_model=ScoutTriggerResponse)
async def trigger_scout(
    request: Request,
    trigger: ScoutTriggerRequest,
):
    """
    Trigger the Scout Agent to scrape properties from configured sources.

    This runs the full scout pipeline: boutique agencies, council DAs,
    public notices, and shadow listings.
    """
    orchestrator = request.app.state.orchestrator

    try:
        scout_result = await orchestrator.scout.safe_execute(
            target_states=trigger.states if trigger.states else None,
            target_suburbs=trigger.suburbs if trigger.suburbs else None,
            use_browser=trigger.use_browser,
            max_agencies=trigger.max_agencies,
        )

        properties = scout_result.data.get("properties", []) if scout_result.success else []

        # Store discovered properties (and persist to DB)
        for prop in properties:
            _property_store[str(prop.id)] = prop

        from nexusprop.db import save_properties_bulk
        if properties:
            save_properties_bulk(properties)

        return ScoutTriggerResponse(
            run_id=str(scout_result.data.get("run_id", "n/a")) if scout_result.success else "failed",
            status="success" if scout_result.success else "failed",
            properties_found=len(properties),
            duration_seconds=scout_result.execution_time_ms / 1000,
            errors=[scout_result.error] if scout_result.error else [],
        )

    except Exception as e:
        logger.error("scout_trigger_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Scout execution failed: {str(e)}")


# ---------------------------------------------------------------------------
# Quick-Scout: on-demand property discovery for a specific suburb
# ---------------------------------------------------------------------------

class QuickScoutRequest(BaseModel):
    """On-demand scout for a manually-entered suburb."""
    suburb: str = Field(..., min_length=2, description="Suburb name (fuzzy matched)")
    count: int = Field(default=3, ge=1, le=10, description="Number of properties to generate")


class QuickScoutResponse(BaseModel):
    """Result of a quick-scout."""
    matched_suburb: str
    matched_region: str
    properties_found: int
    deals_generated: int
    message: str


@router.post("/quick-scout", response_model=QuickScoutResponse)
async def quick_scout(body: QuickScoutRequest):
    """
    Scout a specific suburb on-demand with fuzzy name matching.

    Generates new property listings + deal analysis for the requested suburb
    and persists them to the database.
    """
    from nexusprop.locations import search_suburbs, get_suburb_detail
    from nexusprop.auto_scout import _generate_scout_properties
    from nexusprop.seed_data import generate_seed_deals
    from nexusprop.db import save_properties_bulk, save_deals_bulk, log_scout_run
    from nexusprop.api.routes.deals import _deal_store
    import time

    # Fuzzy search for the suburb
    matches = search_suburbs(body.suburb, fuzzy=True)
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No suburb found matching '{body.suburb}'. Try a different spelling.",
        )

    best = matches[0]
    suburb_name = best["name"]
    region_name = best.get("region", "Unknown")

    t0 = time.time()

    # Generate properties specifically for this suburb
    # Force the suburb by passing an empty existing set and filtering
    from nexusprop.locations import get_all_suburbs
    all_subs = get_all_suburbs()
    target_sub = [s for s in all_subs if s["name"] == suburb_name]

    if not target_sub:
        raise HTTPException(status_code=404, detail=f"Suburb '{suburb_name}' has no location data.")

    # Generate using auto_scout engine but seeded with specific suburb
    new_props = _generate_scout_properties(existing_suburbs=set(), max_new=body.count)
    # Override all generated properties to use the target suburb
    sub_data = target_sub[0]
    for prop in new_props:
        prop.suburb = suburb_name
        prop.state = sub_data.get("state", "VIC")
        prop.postcode = sub_data.get("postcode", prop.postcode)
        # Re-price around the suburb median
        import random
        median = sub_data.get("median", 750_000)
        if prop.property_type and prop.property_type.value in ("apartment", "unit"):
            base = sub_data.get("median_unit") or int(median * 0.55)
        else:
            base = median
        discount = random.uniform(0.08, 0.22)
        prop.asking_price = round(base * (1 - discount), -3)
        # Re-estimate rent
        rent_yield = sub_data.get("yield", 4.0)
        if prop.asking_price and prop.property_type and prop.property_type.value != "land":
            prop.estimated_weekly_rent = max(280, round(prop.asking_price * (rent_yield / 100) / 52, -1))

    # Store properties
    for prop in new_props:
        _property_store[str(prop.id)] = prop
    save_properties_bulk(new_props)

    # Generate deals
    new_deals = generate_seed_deals(new_props)
    for deal in new_deals:
        _deal_store[str(deal.id)] = deal
    if new_deals:
        save_deals_bulk(new_deals)

    duration_ms = int((time.time() - t0) * 1000)
    log_scout_run(
        new_props=len(new_props),
        new_deals=len(new_deals),
        duration_ms=duration_ms,
        notes=f"Quick-scout: {suburb_name} ({region_name})",
    )

    logger.info(
        "quick_scout_complete",
        suburb=suburb_name,
        region=region_name,
        properties=len(new_props),
        deals=len(new_deals),
    )

    return QuickScoutResponse(
        matched_suburb=suburb_name,
        matched_region=region_name,
        properties_found=len(new_props),
        deals_generated=len(new_deals),
        message=f"Found {len(new_props)} properties in {suburb_name} ({region_name}). "
                f"{len(new_deals)} deals analysed.",
    )


@router.delete("/{property_id}")
async def dismiss_property(property_id: str):
    """Remove a property from the active list (dismiss/archive)."""
    if property_id not in _property_store:
        raise HTTPException(status_code=404, detail="Property not found")
    del _property_store[property_id]

    from nexusprop.db import delete_property
    delete_property(property_id)

    return {"status": "dismissed", "property_id": property_id}


@router.get("/{property_id}/value-add")
async def get_value_add(property_id: str):
    """
    Return AI-generated value-add modification suggestions for a property.

    Analyses land size, condition, property type, and zoning to recommend
    specific modifications that can deliver instant 10%+ value uplift.
    """
    prop = _property_store.get(property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    from nexusprop.seed_data import get_value_add_suggestions
    suggestions = get_value_add_suggestions(prop)

    total_uplift = sum(s.get("est_value_uplift", 0) for s in suggestions[:3])
    total_cost = sum(s.get("est_cost", 0) for s in suggestions[:3])

    return {
        "property_id": property_id,
        "suburb": prop.suburb,
        "asking_price": prop.asking_price,
        "suggestions": suggestions,
        "summary": {
            "total_potential_uplift": total_uplift,
            "total_estimated_cost": total_cost,
            "net_equity_gain": total_uplift - total_cost,
            "uplift_pct": round(total_uplift / (prop.asking_price or 1) * 100, 1),
        },
    }
