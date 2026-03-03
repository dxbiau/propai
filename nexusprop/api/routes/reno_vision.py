"""
AI Renovation Vision API — NexusProp

Endpoints for generating AI-powered renovation plans with Bunnings materials lists
and before/after concept renders.
"""

from __future__ import annotations

import asyncio
import base64
import os
from dataclasses import asdict
from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from nexusprop.agents.reno_vision import (
    RenoVisionAgent,
    RenoStyle,
    RenoBudgetTier,
    RenoPackage,
    BUNNINGS_CATALOGUE,
)
from nexusprop.models.property import Property

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class RenoVisionRequest(BaseModel):
    """Request to generate an AI renovation vision for a property."""
    property_id: Optional[str] = Field(None, description="ID of a stored property")
    # Or provide property details directly
    address: Optional[str] = None
    suburb: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    property_type: Optional[str] = Field(None, description="house, unit, townhouse")
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    asking_price: Optional[float] = None
    land_size_sqm: Optional[float] = None
    building_size_sqm: Optional[float] = None
    # Reno settings
    style: RenoStyle = Field(default=RenoStyle.CONTEMPORARY)
    budget_tier: RenoBudgetTier = Field(default=RenoBudgetTier.COSMETIC)
    focus_rooms: Optional[list[str]] = Field(None, description="e.g. ['Kitchen', 'Bathroom', 'Living Room']")
    generate_images: bool = Field(default=False, description="Generate before/after concept renders (slower)")


class QuickRenoRequest(BaseModel):
    """Quick reno estimate from basic property details."""
    suburb: str
    state: str
    property_type: str = "house"
    bedrooms: int = 3
    bathrooms: int = 1
    asking_price: float = 500_000
    style: RenoStyle = RenoStyle.CONTEMPORARY
    budget_tier: RenoBudgetTier = RenoBudgetTier.COSMETIC


class BunningsSearchRequest(BaseModel):
    """Search the Bunnings catalogue."""
    query: str = Field(..., description="e.g. 'matte black tapware', 'interior paint white'")
    category: Optional[str] = Field(None, description="e.g. 'paint', 'kitchen', 'bathroom', 'flooring'")
    max_results: int = Field(default=10, ge=1, le=50)


# ---------------------------------------------------------------------------
# Helper: convert dataclass to dict recursively
# ---------------------------------------------------------------------------

def _package_to_dict(package: RenoPackage) -> dict:
    """Convert a RenoPackage dataclass to a JSON-serialisable dict."""
    d = asdict(package)
    # Convert enums to strings
    d["style"] = package.style.value
    d["budget_tier"] = package.budget_tier.value
    return d


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/generate")
async def generate_reno_vision(
    request: Request,
    body: RenoVisionRequest,
):
    """
    Generate a complete AI renovation vision for a property.

    Returns a full renovation plan with:
    - Room-by-room transformation ideas in the chosen style
    - Real Bunnings materials list with SKUs and current pricing
    - Total project cost breakdown (materials + labour)
    - Estimated property value uplift and ROI on renovation
    - Before/after image prompts (and optionally generated renders)
    """
    # Resolve property
    prop = None

    if body.property_id:
        from nexusprop.api.routes.properties import _property_store
        prop = _property_store.get(body.property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
    else:
        # Build from request fields
        if not body.suburb or not body.state:
            raise HTTPException(
                status_code=422,
                detail="Provide either property_id or suburb + state"
            )
        prop = Property(
            address=body.address or f"Property in {body.suburb}",
            suburb=body.suburb,
            state=body.state,
            postcode=body.postcode or "0000",
            property_type=body.property_type or "house",
            bedrooms=body.bedrooms,
            bathrooms=body.bathrooms,
            asking_price=body.asking_price,
            land_size_sqm=body.land_size_sqm,
            building_size_sqm=body.building_size_sqm,
        )

    agent = RenoVisionAgent()

    try:
        result = await agent.safe_execute(
            prop=prop,
            style=body.style,
            budget_tier=body.budget_tier,
            focus_rooms=body.focus_rooms,
            purchase_price=body.asking_price or (prop.asking_price if prop else None),
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=f"Reno vision failed: {result.error}")

        package: RenoPackage = result.data["package"]
        package_dict = _package_to_dict(package)

        # Optionally generate before/after images
        if body.generate_images:
            package_dict = await _add_concept_images(package_dict)

        return {
            "success": True,
            "package": package_dict,
            "summary": {
                "tagline": package.tagline,
                "total_project_cost": package.total_project_cost,
                "total_materials_cost": package.total_materials_cost,
                "total_labour_estimate": package.total_labour_estimate,
                "estimated_value_uplift_pct": package.estimated_value_uplift_pct,
                "estimated_value_uplift_aud": package.estimated_value_uplift_aud,
                "roi_on_reno": package.roi_on_reno,
                "rooms_count": len(package.rooms),
                "total_bunnings_items": sum(len(r["materials"]) for r in package_dict["rooms"]),
            },
            "bunnings_partnership_note": package.partnership_note,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("reno_vision_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-estimate")
async def quick_reno_estimate(body: QuickRenoRequest):
    """
    Quick renovation cost estimate without full AI analysis.

    Returns estimated costs for cosmetic, refresh, and transform tiers
    based on property size and type — useful for quick deal screening.
    """
    # Heuristic estimates based on property type and size
    base_costs = {
        "house": {
            RenoBudgetTier.COSMETIC:   (3_500, 7_500),
            RenoBudgetTier.REFRESH:    (10_000, 20_000),
            RenoBudgetTier.TRANSFORM:  (25_000, 50_000),
        },
        "unit": {
            RenoBudgetTier.COSMETIC:   (2_000, 5_000),
            RenoBudgetTier.REFRESH:    (7_000, 15_000),
            RenoBudgetTier.TRANSFORM:  (15_000, 35_000),
        },
        "townhouse": {
            RenoBudgetTier.COSMETIC:   (3_000, 6_500),
            RenoBudgetTier.REFRESH:    (9_000, 18_000),
            RenoBudgetTier.TRANSFORM:  (20_000, 45_000),
        },
    }

    prop_type = body.property_type.lower() if body.property_type else "house"
    if prop_type not in base_costs:
        prop_type = "house"

    # Scale by bedrooms
    bed_multiplier = 1.0 + (body.bedrooms - 3) * 0.15

    estimates = {}
    for tier, (low, high) in base_costs[prop_type].items():
        adj_low = round(low * bed_multiplier / 500) * 500
        adj_high = round(high * bed_multiplier / 500) * 500
        uplift_pct = {"cosmetic": 5.0, "refresh": 12.0, "transform": 22.0}[tier.value]
        uplift_aud = round(body.asking_price * uplift_pct / 100)
        roi = round(uplift_aud / ((adj_low + adj_high) / 2), 2)
        estimates[tier.value] = {
            "cost_range": f"${adj_low:,}–${adj_high:,}",
            "cost_low": adj_low,
            "cost_high": adj_high,
            "estimated_value_uplift_pct": uplift_pct,
            "estimated_value_uplift_aud": uplift_aud,
            "roi_on_reno": roi,
            "description": {
                "cosmetic": "Paint, hardware, fixtures, garden tidy — maximum bang for buck",
                "refresh":  "Kitchen/bath refresh, new flooring, lighting upgrade",
                "transform": "Full kitchen/bath renovation, decking, landscaping",
            }[tier.value],
        }

    return {
        "property": f"{body.suburb} {body.state} — {body.bedrooms}bed {prop_type}",
        "asking_price": body.asking_price,
        "estimates": estimates,
        "recommended_tier": "cosmetic" if body.asking_price < 400_000 else "refresh",
        "note": "Use /reno-vision/generate for a full AI plan with Bunnings materials list",
    }


@router.get("/styles")
async def list_styles():
    """List available renovation styles with descriptions."""
    return {
        "styles": [
            {"value": "coastal",      "label": "Coastal",       "description": "Light blues, whites, natural timber, rattan, linen textures"},
            {"value": "hamptons",     "label": "Hamptons",      "description": "White shaker cabinets, navy accents, brass hardware, herringbone floors"},
            {"value": "scandinavian", "label": "Scandinavian",  "description": "White walls, light oak, minimal clutter, functional elegance"},
            {"value": "industrial",   "label": "Industrial",    "description": "Exposed brick, matte black fixtures, concrete look, Edison bulbs"},
            {"value": "contemporary", "label": "Contemporary",  "description": "Clean lines, neutral palette, statement lighting, quality fixtures"},
            {"value": "classic",      "label": "Classic",       "description": "Timeless neutrals, traditional profiles, quality materials"},
            {"value": "farmhouse",    "label": "Farmhouse",     "description": "Shiplap, warm whites, vintage hardware, open shelving"},
        ],
        "budget_tiers": [
            {"value": "cosmetic",   "label": "Cosmetic Refresh",    "range": "$2,000–$8,000",   "description": "Paint, hardware, fixtures, garden tidy"},
            {"value": "refresh",    "label": "Full Refresh",        "range": "$8,000–$20,000",  "description": "Kitchen/bath refresh, flooring, lighting"},
            {"value": "transform",  "label": "Full Transformation", "range": "$20,000–$50,000", "description": "Full kitchen/bath reno, decking, landscaping"},
        ],
    }


@router.post("/bunnings/search")
async def search_bunnings_catalogue(body: BunningsSearchRequest):
    """
    Search the Bunnings product catalogue.

    Returns matching products with SKUs, current pricing, and direct Bunnings URLs.
    When a formal Bunnings API partnership is established, this will return live inventory.
    """
    query = body.query.lower()
    category_filter = body.category.lower() if body.category else None

    results = []
    for cat_key, products in BUNNINGS_CATALOGUE.items():
        for product in products:
            # Category filter
            if category_filter and product["category"] != category_filter:
                continue
            # Text match
            searchable = f"{product['name']} {product['brand']} {product['category']} {product['subcategory']} {cat_key}".lower()
            if any(word in searchable for word in query.split()):
                results.append({
                    "sku": product["sku"],
                    "name": product["name"],
                    "brand": product["brand"],
                    "price": product["price"],
                    "unit": product["unit"],
                    "category": product["category"],
                    "subcategory": product["subcategory"],
                    "url": product["url"],
                    "catalogue_key": cat_key,
                })

    # Sort by relevance (exact brand/name match first)
    results.sort(key=lambda p: (
        0 if any(w in p["name"].lower() for w in query.split()) else 1
    ))

    return {
        "query": body.query,
        "total": len(results),
        "results": results[:body.max_results],
        "partnership_note": (
            "Bunnings product data sourced from curated catalogue (March 2026 RRP). "
            "Click any URL for live pricing at Bunnings.com.au"
        ),
    }


@router.get("/bunnings/categories")
async def list_bunnings_categories():
    """List all available Bunnings product categories in the catalogue."""
    categories: dict[str, list[str]] = {}
    for cat_key, products in BUNNINGS_CATALOGUE.items():
        for p in products:
            cat = p["category"]
            sub = p["subcategory"]
            if cat not in categories:
                categories[cat] = []
            if sub not in categories[cat]:
                categories[cat].append(sub)

    return {
        "categories": categories,
        "total_products": sum(len(v) for v in BUNNINGS_CATALOGUE.values()),
        "total_categories": len(categories),
    }


@router.get("/bunnings/product/{sku}")
async def get_bunnings_product(sku: str):
    """Get a specific Bunnings product by SKU."""
    for cat_key, products in BUNNINGS_CATALOGUE.items():
        for product in products:
            if product["sku"].upper() == sku.upper():
                return {
                    "found": True,
                    "product": {**product, "catalogue_key": cat_key},
                    "bunnings_url": product["url"],
                }
    raise HTTPException(status_code=404, detail=f"Product SKU '{sku}' not found in catalogue")


# ---------------------------------------------------------------------------
# Image generation helper
# ---------------------------------------------------------------------------

async def _add_concept_images(package_dict: dict) -> dict:
    """
    Generate before/after concept renders for each room using OpenAI DALL-E.
    Images are returned as base64 data URIs.
    """
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI()

        for room in package_dict.get("rooms", [])[:3]:  # limit to first 3 rooms
            after_prompt = room.get("after_prompt", "")
            if not after_prompt:
                continue

            style = package_dict.get("style", "contemporary")
            full_prompt = (
                f"Interior design render, {style} style Australian home, {after_prompt}. "
                f"Professional real estate photography, bright natural light, clean and elegant, "
                f"high-end renovation, photorealistic. No people, no text."
            )

            try:
                response = await client.images.generate(
                    model="dall-e-3",
                    prompt=full_prompt[:1000],
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                room["concept_render_url"] = image_url
                room["concept_render_prompt"] = full_prompt[:200]
            except Exception as img_err:
                logger.warning("concept_render_failed", room=room.get("room_name"), error=str(img_err))
                room["concept_render_url"] = None

    except Exception as e:
        logger.warning("image_generation_skipped", error=str(e))

    return package_dict
