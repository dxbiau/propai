"""
Seed data — Australian Property Associates — National Coverage.

80+ realistic property listings and pre-analysed deals across all 8 states.
Covers all capital cities + key regional centres nationwide.
Each deal includes VALUE-ADD intelligence: suggested modifications,
estimated uplift, and before/after value scenarios.

Bloomberg Terminal dashboard shows data immediately on a fresh start.
No external APIs or LLMs required.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from nexusprop.models.property import (
    Property,
    PropertyType,
    PropertySource,
    PropertyCondition,
    ListingStatus,
    DistressSignal,
)
from nexusprop.models.deal import (
    Deal,
    DealType,
    CashFlowModel,
    BargainScore,
)
from nexusprop.config.settings import get_settings

_now = datetime.utcnow


def _stamp_duty(price: float) -> float:
    return get_settings().calculate_stamp_duty(price)


# ---------------------------------------------------------------------------
# Property Images — Curated Unsplash photos by property type
# High-quality royalty-free images matched to Australian property styles.
# These are enhanced via the Photo Enhancement Agent pipeline at display time.
# ---------------------------------------------------------------------------

_IMAGES_BY_TYPE: dict[str, list[str]] = {
    "house": [
        "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=800&h=500&fit=crop&q=80",
    ],
    "apartment": [
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=500&fit=crop&q=80",
    ],
    "townhouse": [
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1625602812206-5ec545ca1231?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1600047509358-9dc75507daeb?w=800&h=500&fit=crop&q=80",
    ],
    "unit": [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=500&fit=crop&q=80",
    ],
    "villa": [
        "https://images.unsplash.com/photo-1613977257363-707ba9348227?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop&q=80",
    ],
    "retail": [
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=800&h=500&fit=crop&q=80",
    ],
    "commercial": [
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=500&fit=crop&q=80",
    ],
    "industrial": [
        "https://images.unsplash.com/photo-1565610222536-ef125c59da2e?w=800&h=500&fit=crop&q=80",
    ],
    "warehouse": [
        "https://images.unsplash.com/photo-1565610222536-ef125c59da2e?w=800&h=500&fit=crop&q=80",
    ],
    "land": [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=500&fit=crop&q=80",
        "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=800&h=500&fit=crop&q=80",
    ],
    "rural": [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=500&fit=crop&q=80",
    ],
    "farm": [
        "https://images.unsplash.com/photo-1500076656116-558758c991c1?w=800&h=500&fit=crop&q=80",
    ],
    "acreage": [
        "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=800&h=500&fit=crop&q=80",
    ],
    "duplex": [
        "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=800&h=500&fit=crop&q=80",
    ],
}
_DEFAULT_IMAGES: list[str] = [
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&h=500&fit=crop&q=80",
]


# Map state code to Domain.com.au / realestate.com.au URL slug
_STATE_SLUG = {
    "NSW": "nsw", "VIC": "vic", "QLD": "qld", "SA": "sa",
    "WA": "wa", "TAS": "tas", "NT": "nt", "ACT": "act",
}


def _make_domain_url(suburb: str, postcode: str, state: str = "VIC") -> str:
    """Build a real Domain.com.au search URL for a suburb."""
    slug = suburb.lower().replace(" ", "-")
    st = _STATE_SLUG.get(state.upper(), state.lower())
    return f"https://www.domain.com.au/sale/{slug}-{st}-{postcode}/"


def _make_realestate_url(suburb: str, postcode: str, state: str = "VIC") -> str:
    """Build a real realestate.com.au search URL for a suburb."""
    slug = suburb.lower().replace(" ", "+")
    st = _STATE_SLUG.get(state.upper(), state.lower())
    return f"https://www.realestate.com.au/buy/in-{slug},+{st}+{postcode}/list-1"


def _inject_images(properties: list) -> None:
    """Assign curated property photos by type and fix source URLs."""
    # Track index per type to cycle through available images
    _type_counters: dict[str, int] = {}

    for prop in properties:
        ptype = prop.property_type.value if hasattr(prop.property_type, 'value') else str(prop.property_type)
        images = _IMAGES_BY_TYPE.get(ptype, _DEFAULT_IMAGES)

        if images:
            idx = _type_counters.get(ptype, 0)
            prop.image_urls = [images[idx % len(images)]]
            _type_counters[ptype] = idx + 1
        else:
            prop.image_urls = list(_DEFAULT_IMAGES)

        # Fix source_url to real listing search page
        if not prop.source_url or "example.com" in (prop.source_url or ""):
            prop.source_url = _make_domain_url(prop.suburb, prop.postcode, prop.state or "VIC")


# ═══════════════════════════════════════════════════════════════════
# VALUE-ADD INTELLIGENCE — per-suburb modification suggestions
# The killer feature: "how do we add value and get an instant 10%+ uplift"
# ═══════════════════════════════════════════════════════════════════

VALUE_ADD_PLAYBOOK: dict[str, dict] = {
    # Format: condition_type → {mods: [list of modifications], est_cost, est_uplift_pct, timeframe_weeks}
    "cosmetic_refresh": {
        "mods": ["Fresh interior paint (neutral tones)", "New carpet/polished timber floors",
                 "Modern light fixtures", "Updated kitchen splashback", "Pressure wash exterior"],
        "est_cost_range": (15_000, 30_000),
        "est_uplift_pct": (8, 12),
        "timeframe_weeks": 3,
        "label": "COSMETIC REFRESH",
    },
    "kitchen_bathroom_reno": {
        "mods": ["Full kitchen replacement (stone benchtop, soft-close, integrated appliances)",
                 "Main bathroom gut + rebuild (frameless shower, floating vanity)",
                 "Ensuite addition if space permits", "Laundry upgrade"],
        "est_cost_range": (40_000, 75_000),
        "est_uplift_pct": (12, 20),
        "timeframe_weeks": 8,
        "label": "KITCHEN & BATH UPGRADE",
    },
    "extension_second_storey": {
        "mods": ["Second storey addition (2BR + BA)", "Structural engineering + council approval",
                 "New roof + insulation", "Open-plan living extension"],
        "est_cost_range": (180_000, 350_000),
        "est_uplift_pct": (25, 45),
        "timeframe_weeks": 24,
        "label": "SECOND STOREY / EXTENSION",
    },
    "granny_flat_addition": {
        "mods": ["Detached granny flat 60m² (1BR + kitchenette + BA)",
                 "Separate utility connection", "Private entry + courtyard",
                 "Council permit (VicSmart if compliant)"],
        "est_cost_range": (120_000, 180_000),
        "est_uplift_pct": (15, 25),
        "timeframe_weeks": 16,
        "label": "GRANNY FLAT / DPU",
    },
    "subdivision_potential": {
        "mods": ["Engage town planner for feasibility", "Survey + title re-establishment",
                 "Council pre-application meeting", "Create 2 titles from 1",
                 "Build or sell vacant lot"],
        "est_cost_range": (30_000, 80_000),
        "est_uplift_pct": (30, 60),
        "timeframe_weeks": 26,
        "label": "SUBDIVISION",
    },
    "commercial_conversion": {
        "mods": ["Change of use application to council", "Fit-out for commercial/mixed-use",
                 "Separate metering for utilities", "Disability access compliance"],
        "est_cost_range": (50_000, 120_000),
        "est_uplift_pct": (15, 30),
        "timeframe_weeks": 16,
        "label": "COMMERCIAL CONVERSION",
    },
    "airbnb_r2sa_setup": {
        "mods": ["Furniture package (mid-range styling)", "Professional photography",
                 "Smart lock + keyless entry", "Listing optimisation (Airbnb + Stayz)",
                 "Linen service setup", "Welcome pack + local guide"],
        "est_cost_range": (8_000, 20_000),
        "est_uplift_pct": (40, 80),  # income uplift vs standard rent
        "timeframe_weeks": 2,
        "label": "R2SA / AIRBNB CONVERSION",
    },
    "facade_streetscape": {
        "mods": ["New front fence + gate", "Landscaped front garden",
                 "Rendered/painted facade", "New front door + portico",
                 "Driveway reseal", "External lighting"],
        "est_cost_range": (10_000, 25_000),
        "est_uplift_pct": (5, 10),
        "timeframe_weeks": 2,
        "label": "STREET APPEAL UPGRADE",
    },
}


def get_value_add_suggestions(prop: Property) -> list[dict]:
    """Return ranked value-add suggestions for a property."""
    suggestions = []
    price = prop.asking_price or 0

    # Always suggest cosmetic refresh for reno properties
    if prop.condition in (PropertyCondition.RENOVATION_REQUIRED, PropertyCondition.FAIR):
        suggestions.append({
            **VALUE_ADD_PLAYBOOK["cosmetic_refresh"],
            "est_cost": sum(VALUE_ADD_PLAYBOOK["cosmetic_refresh"]["est_cost_range"]) // 2,
            "est_value_uplift": round(price * sum(VALUE_ADD_PLAYBOOK["cosmetic_refresh"]["est_uplift_pct"]) / 200),
        })
        suggestions.append({
            **VALUE_ADD_PLAYBOOK["kitchen_bathroom_reno"],
            "est_cost": sum(VALUE_ADD_PLAYBOOK["kitchen_bathroom_reno"]["est_cost_range"]) // 2,
            "est_value_uplift": round(price * sum(VALUE_ADD_PLAYBOOK["kitchen_bathroom_reno"]["est_uplift_pct"]) / 200),
        })

    # Subdivision if large land
    if prop.land_size_sqm and prop.land_size_sqm >= 550:
        suggestions.append({
            **VALUE_ADD_PLAYBOOK["subdivision_potential"],
            "est_cost": sum(VALUE_ADD_PLAYBOOK["subdivision_potential"]["est_cost_range"]) // 2,
            "est_value_uplift": round(price * sum(VALUE_ADD_PLAYBOOK["subdivision_potential"]["est_uplift_pct"]) / 200),
        })

    # Granny flat if land >= 400sqm and house
    if prop.land_size_sqm and prop.land_size_sqm >= 400 and prop.property_type in (
        PropertyType.HOUSE, PropertyType.VILLA
    ):
        suggestions.append({
            **VALUE_ADD_PLAYBOOK["granny_flat_addition"],
            "est_cost": sum(VALUE_ADD_PLAYBOOK["granny_flat_addition"]["est_cost_range"]) // 2,
            "est_value_uplift": round(price * sum(VALUE_ADD_PLAYBOOK["granny_flat_addition"]["est_uplift_pct"]) / 200),
        })

    # R2SA for inner-city apartments/units
    if prop.property_type in (PropertyType.APARTMENT, PropertyType.UNIT) and price < 700_000:
        suggestions.append({
            **VALUE_ADD_PLAYBOOK["airbnb_r2sa_setup"],
            "est_cost": sum(VALUE_ADD_PLAYBOOK["airbnb_r2sa_setup"]["est_cost_range"]) // 2,
            "est_value_uplift": round(price * 0.10),  # 10% income uplift estimate for valuation
        })

    # Street appeal always applies to houses
    if prop.property_type in (PropertyType.HOUSE, PropertyType.TOWNHOUSE, PropertyType.VILLA):
        suggestions.append({
            **VALUE_ADD_PLAYBOOK["facade_streetscape"],
            "est_cost": sum(VALUE_ADD_PLAYBOOK["facade_streetscape"]["est_cost_range"]) // 2,
            "est_value_uplift": round(price * sum(VALUE_ADD_PLAYBOOK["facade_streetscape"]["est_uplift_pct"]) / 200),
        })

    # Extension for houses with enough land
    if prop.land_size_sqm and prop.land_size_sqm >= 350 and prop.property_type == PropertyType.HOUSE:
        if prop.bedrooms and prop.bedrooms <= 3:
            suggestions.append({
                **VALUE_ADD_PLAYBOOK["extension_second_storey"],
                "est_cost": sum(VALUE_ADD_PLAYBOOK["extension_second_storey"]["est_cost_range"]) // 2,
                "est_value_uplift": round(price * sum(VALUE_ADD_PLAYBOOK["extension_second_storey"]["est_uplift_pct"]) / 200),
            })

    # Sort by ROI (uplift / cost ratio)
    for s in suggestions:
        cost = s.get("est_cost", 1)
        s["roi_ratio"] = round(s.get("est_value_uplift", 0) / cost, 1) if cost > 0 else 0
    suggestions.sort(key=lambda x: x["roi_ratio"], reverse=True)

    return suggestions[:5]  # Top 5


# ═══════════════════════════════════════════════════════════════════
# SEED PROPERTIES — ALL OF AUSTRALIA
# ═══════════════════════════════════════════════════════════════════

def generate_seed_properties() -> list[Property]:
    """Return 80+ realistic property listings across ALL Australian states."""
    now = _now()
    properties = [

        # ── MELBOURNE CBD & INNER CITY (3) ─────────────────────────
        Property(
            id=uuid4(), address="1402/318 Russell Street", suburb="Melbourne CBD",
            state="VIC", postcode="3000", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=68,
            year_built=2018, condition=PropertyCondition.GOOD,
            asking_price=520_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/1402-318-russell",
            listing_text="Modern high-rise apartment near Queen Vic Market. Vendor relocating "
                         "to Singapore — MUST SELL before visa expiry. Uninterrupted city views, "
                         "14th floor, full gym + pool. Currently tenanted at $520/week. "
                         "Walk to 5 tram routes. The new Metro Tunnel stations now open 800m away.",
            agent_name="Jessica Lin", agent_phone="0412 888 901",
            agency_name="Jellis Craig Melbourne",
            estimated_weekly_rent=520, council_rates_annual=900, water_rates_annual=500,
            strata_levies_quarterly=1_800,
            distress_signals=[
                DistressSignal(keyword="must sell", confidence=0.92, source="listing_text"),
                DistressSignal(keyword="relocating overseas", confidence=0.88, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(), address="3/42 Cardigan Street", suburb="Carlton",
            state="VIC", postcode="3053", property_type=PropertyType.TOWNHOUSE,
            bedrooms=3, bathrooms=2, car_spaces=1, land_size_sqm=120,
            building_size_sqm=135, year_built=2012, condition=PropertyCondition.GOOD,
            asking_price=1_080_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/3-42-cardigan",
            listing_text="Architecturally designed townhouse in blue-chip Carlton. Double "
                         "height ceilings, north-facing courtyard. Body corp dispute resolved — "
                         "seller motivated to exit quickly. Walk to Lygon Street, University of "
                         "Melbourne. Strong rental demand from academics and professionals.",
            agent_name="Marco Rossi", agent_phone="0423 111 222",
            agency_name="Marshall White Carlton",
            estimated_weekly_rent=780, council_rates_annual=1_400, water_rates_annual=600,
            strata_levies_quarterly=800,
            distress_signals=[
                DistressSignal(keyword="motivated seller", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),
        Property(
            id=uuid4(), address="8/15 Harbour Esplanade", suburb="Docklands",
            state="VIC", postcode="3008", property_type=PropertyType.APARTMENT,
            bedrooms=1, bathrooms=1, car_spaces=1, building_size_sqm=55,
            year_built=2015, condition=PropertyCondition.GOOD,
            asking_price=420_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.COMING_SOON,
            source_url="https://example.com/listing/8-15-harbour",
            listing_text="Waterfront Docklands apartment with marina views. "
                         "Overseas investor — has not visited in 3 years. Strata manager "
                         "reports owner in arrears. Bargain entry into blue-chip waterfront locale. "
                         "New Docklands Primary School opening 2026. Harbour Esplanade redesign underway.",
            agent_name="David Chen", agent_phone="0434 222 333",
            agency_name="Barry Plant Docklands",
            estimated_weekly_rent=420, council_rates_annual=750, water_rates_annual=450,
            strata_levies_quarterly=1_600,
            distress_signals=[
                DistressSignal(keyword="overseas investor", confidence=0.80, source="listing_text"),
                DistressSignal(keyword="strata arrears", confidence=0.90, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),

        # ── INNER NORTH (5) ───────────────────────────────────────
        Property(
            id=uuid4(), address="87 Scotchmer Street", suburb="Fitzroy",
            state="VIC", postcode="3065", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=0, land_size_sqm=280,
            building_size_sqm=120, year_built=1890, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=1_150_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/87-scotchmer",
            listing_text="Original Victorian terrace in one of Melbourne's most sought-after "
                         "streets. Deceased estate — executors instruct sale at ANY PRICE. "
                         "Heritage overlay HO334 — add second storey STCA. "
                         "Walk to Brunswick Street, Edinburgh Gardens. Reno and profit potential immense.",
            agent_name="Tom McKenzie", agent_phone="0445 333 444",
            agency_name="Nelson Alexander Fitzroy",
            estimated_weekly_rent=650, council_rates_annual=2_200, water_rates_annual=700,
            zoning="NRZ1",
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="any price", confidence=0.90, source="listing_text"),
                DistressSignal(keyword="heritage overlay", confidence=0.60, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),
        Property(
            id=uuid4(), address="22 Helen Street", suburb="Northcote",
            state="VIC", postcode="3070", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=620,
            building_size_sqm=180, year_built=1960, condition=PropertyCondition.FAIR,
            asking_price=1_180_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/22-helen",
            listing_text="Californian bungalow on prime 620m² block with rear lane access. "
                         "GRZ1 zoning — subdivision potential for 2 dwellings STCA. "
                         "Vendor is builder going through divorce — priced for quick sale. "
                         "Walk to Northcote Plaza, High Street cafes. School zone: Northcote High.",
            agent_name="Sarah Park", agent_phone="0456 444 555",
            agency_name="Jellis Craig Northcote",
            estimated_weekly_rent=780, council_rates_annual=2_000, water_rates_annual=700,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="divorce", confidence=0.88, source="listing_text"),
                DistressSignal(keyword="quick sale", confidence=0.82, source="listing_text"),
                DistressSignal(keyword="subdivision potential", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(), address="4/66 High Street", suburb="Preston",
            state="VIC", postcode="3072", property_type=PropertyType.UNIT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=72,
            year_built=1990, condition=PropertyCondition.GOOD,
            asking_price=530_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.OFF_MARKET,
            source_url="https://example.com/listing/4-66-high",
            listing_text="Neat brick unit in Preston's booming High Street corridor. "
                         "Near Preston Market redevelopment — $1.3B transformation. "
                         "Vendor is teacher relocating to regional VIC. Currently tenanted $450/wk. "
                         "Bell station 400m. Strong rental demand from young professionals.",
            agent_name="Amy Tran", agent_phone="0467 555 666",
            agency_name="Harcourts Preston",
            estimated_weekly_rent=450, council_rates_annual=900, water_rates_annual=500,
            strata_levies_quarterly=600,
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.82, source="listing_text"),
            ],
            created_at=now - timedelta(days=7),
        ),
        Property(
            id=uuid4(), address="156 Lygon Street", suburb="Brunswick",
            state="VIC", postcode="3056", property_type=PropertyType.RETAIL,
            bedrooms=0, bathrooms=1, car_spaces=0, building_size_sqm=95,
            year_built=1935, condition=PropertyCondition.FAIR,
            asking_price=820_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/156-lygon",
            listing_text="Prime Lygon Street retail shop with residential conversion potential. "
                         "Heritage shopfront, 4m pressed-tin ceilings. Current tenant "
                         "café lease expires April 2026 — renegotiate or convert to "
                         "mixed-use (shop + 2 apartments upstairs). Commercial yield 5.5% net.",
            agent_name="Nick Grasso", agent_phone="0478 666 777",
            agency_name="Biggin Scott Brunswick",
            estimated_weekly_rent=850, council_rates_annual=2_800, water_rates_annual=500,
            zoning="C1Z",
            distress_signals=[],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(), address="33 Anderson Street", suburb="Coburg",
            state="VIC", postcode="3058", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=1, land_size_sqm=520,
            building_size_sqm=130, year_built=1950, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=870_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/33-anderson",
            listing_text="Solid brick home on 520m² in the Coburg revival zone. "
                         "GRZ1 — dual occupancy potential. Mortgagee in possession — "
                         "bank says sell by auction. Walk to Coburg station (Upfield line). "
                         "Level crossing removal complete — station precinct transformed.",
            agent_name="Daniel Kostic", agent_phone="0489 777 888",
            agency_name="Ray White Coburg",
            estimated_weekly_rent=580, council_rates_annual=1_600, water_rates_annual=650,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="mortgagee", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="bank says sell", confidence=0.92, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),

        # ── INNER WEST (4) ────────────────────────────────────────
        Property(
            id=uuid4(), address="18 Droop Street", suburb="Footscray",
            state="VIC", postcode="3011", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=450,
            building_size_sqm=110, year_built=1940, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=740_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/18-droop",
            listing_text="Worker's cottage on 450m² in Footscray's gentrification epicentre. "
                         "Metro Tunnel western portal 600m away — will revolutionise this suburb. "
                         "DA approved for rear granny flat (plans included). Deceased estate — "
                         "family wants FAST settlement. Reno + granny flat = instant equity.",
            agent_name="Luke Barbato", agent_phone="0401 888 999",
            agency_name="Jas Stephens Footscray",
            estimated_weekly_rent=550, council_rates_annual=1_500, water_rates_annual=600,
            zoning="GRZ2",
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="DA approved", confidence=0.80, source="listing_text"),
                DistressSignal(keyword="fast settlement", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),
        Property(
            id=uuid4(), address="9 Anderson Street", suburb="Yarraville",
            state="VIC", postcode="3013", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=1, land_size_sqm=550,
            building_size_sqm=165, year_built=1920, condition=PropertyCondition.FAIR,
            asking_price=1_020_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/9-anderson-yrv",
            listing_text="Grand Edwardian home in Yarraville village. 550m² block with "
                         "rear lane access — subdivision feasibility confirmed by town planner. "
                         "West Gate Tunnel project nearing completion = faster CBD access. "
                         "Vendor upgrading to country property. Solid rental at $680/wk.",
            agent_name="Kate Murphy", agent_phone="0412 999 000",
            agency_name="Village Real Estate",
            estimated_weekly_rent=680, council_rates_annual=2_100, water_rates_annual=700,
            zoning="NRZ1",
            distress_signals=[
                DistressSignal(keyword="subdivision feasibility", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=8),
        ),
        Property(
            id=uuid4(), address="11/45 Mason Street", suburb="Newport",
            state="VIC", postcode="3015", property_type=PropertyType.UNIT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=78,
            year_built=2005, condition=PropertyCondition.GOOD,
            asking_price=560_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.OFF_MARKET,
            source_url="https://example.com/listing/11-45-mason",
            listing_text="Low-maintenance brick unit in Newport. Owner emigrating to NZ — "
                         "wants unconditional sale. Walking distance to Newport station + "
                         "Williamstown Road café strip. Newport Station Precinct Uplift "
                         "underway. Currently tenanted at $460/wk.",
            agent_name="Jane Walsh", agent_phone="0423 000 111",
            agency_name="Sweeney Estate Agents",
            estimated_weekly_rent=460, council_rates_annual=950, water_rates_annual=500,
            strata_levies_quarterly=700,
            distress_signals=[
                DistressSignal(keyword="emigrating", confidence=0.85, source="listing_text"),
                DistressSignal(keyword="unconditional", confidence=0.78, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(), address="22 Essex Street", suburb="Maidstone",
            state="VIC", postcode="3012", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=600,
            building_size_sqm=105, year_built=1955, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=680_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.COUNCIL_DA,
            source_url="https://example.com/listing/22-essex",
            listing_text="Original condition home on massive 600m² in Maidstone — Melbourne's "
                         "next Footscray. Maribyrnong Defence Site redevelopment (10,000 homes) "
                         "will transform this area. GRZ2 zoning. Build 3 townhouses STCA. "
                         "Elderly vendor moving to aged care. Below replacement cost.",
            agent_name="Mario Petroni", agent_phone="0434 111 222",
            agency_name="YPA Maidstone",
            estimated_weekly_rent=500, council_rates_annual=1_400, water_rates_annual=600,
            zoning="GRZ2",
            distress_signals=[
                DistressSignal(keyword="elderly vendor", confidence=0.82, source="listing_text"),
                DistressSignal(keyword="aged care", confidence=0.85, source="listing_text"),
                DistressSignal(keyword="below replacement cost", confidence=0.78, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),

        # ── WESTERN GROWTH CORRIDOR (3) ───────────────────────────
        Property(
            id=uuid4(), address="14 Woodland Drive", suburb="Werribee",
            state="VIC", postcode="3030", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=500,
            building_size_sqm=185, year_built=2019, condition=PropertyCondition.EXCELLENT,
            asking_price=590_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/14-woodland",
            listing_text="Near-new 4BR family home in Werribee's Riverwalk Estate. "
                         "Vendor transferred to Sydney — MUST SELL within 6 weeks. "
                         "Tenanted at $480/wk with lease until March 2027. "
                         "Werribee Employment Precinct P15B will create 60,000 jobs nearby.",
            agent_name="Raj Patel", agent_phone="0445 222 333",
            agency_name="OBrien Real Estate",
            estimated_weekly_rent=480, council_rates_annual=1_600, water_rates_annual=600,
            distress_signals=[
                DistressSignal(keyword="must sell", confidence=0.90, source="listing_text"),
                DistressSignal(keyword="transferred", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(), address="8 Railway Crescent", suburb="Sunshine",
            state="VIC", postcode="3020", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=1, land_size_sqm=480,
            building_size_sqm=115, year_built=1965, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=620_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/8-railway-sun",
            listing_text="Unrenovated home 300m from Sunshine Super Hub — the convergence "
                         "of Metro Tunnel + Airport Rail Link. This precinct will be "
                         "Melbourne's next major transport interchange. GRZ1 zoning. "
                         "Vendor in financial difficulty — accepting all reasonable offers.",
            agent_name="Ali Hassan", agent_phone="0456 333 444",
            agency_name="Real Estate HQ Sunshine",
            estimated_weekly_rent=450, council_rates_annual=1_400, water_rates_annual=550,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="financial difficulty", confidence=0.88, source="listing_text"),
                DistressSignal(keyword="all reasonable offers", confidence=0.82, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(), address="LOT 2214 Tarneit Road", suburb="Tarneit",
            state="VIC", postcode="3029", property_type=PropertyType.LAND,
            bedrooms=0, bathrooms=0, car_spaces=0, land_size_sqm=420,
            year_built=None, condition=PropertyCondition.UNKNOWN,
            asking_price=350_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/lot-2214-tarneit",
            listing_text="Titled land in Tarneit West PSP area — ready to build. "
                         "Developer lot release — priced below comparable titled blocks. "
                         "Build a 4BR dual-income home for $280K. Total package under $630K. "
                         "Tarneit train station 1.5km. Wyndham fastest growing LGA in VIC.",
            agent_name="Priya Sharma", agent_phone="0467 444 555",
            agency_name="Stockdale & Leggo",
            estimated_weekly_rent=0, council_rates_annual=1_200, water_rates_annual=400,
            distress_signals=[],
            created_at=now - timedelta(days=10),
        ),

        # ── INNER EAST (3) ────────────────────────────────────────
        Property(
            id=uuid4(), address="15/288 Riversdale Road", suburb="Hawthorn",
            state="VIC", postcode="3122", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=85,
            year_built=1928, condition=PropertyCondition.FAIR,
            asking_price=650_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/15-288-riversdale",
            listing_text="Art deco apartment block in leafy Hawthorn. Vendor is interstate "
                         "executor — deceased estate, priced to sell this month. "
                         "Original condition — reno to create premium Hawthorn finish. "
                         "Walk to Glenferrie Road, Swinburne, tram. Boroondara council area.",
            agent_name="Philippa Grey", agent_phone="0478 555 666",
            agency_name="Kay & Burton",
            estimated_weekly_rent=520, council_rates_annual=1_200, water_rates_annual=550,
            strata_levies_quarterly=900,
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="priced to sell", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(), address="42 Station Street", suburb="Box Hill",
            state="VIC", postcode="3128", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=2, car_spaces=2, land_size_sqm=680,
            building_size_sqm=160, year_built=1970, condition=PropertyCondition.FAIR,
            asking_price=1_100_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/42-station-bh",
            listing_text="680m² block in Box Hill Metropolitan Activity Centre zone. "
                         "RGZ1 zoning — develop up to 4 storeys STCA. "
                         "Box Hill Hospital expansion, new tram extension planned. "
                         "Current home is solid but dated. Development upside enormous. "
                         "Vendor retiring to Queensland.",
            agent_name="Kevin Huo", agent_phone="0489 666 777",
            agency_name="McGrath Box Hill",
            estimated_weekly_rent=680, council_rates_annual=1_800, water_rates_annual=700,
            zoning="RGZ1",
            distress_signals=[
                DistressSignal(keyword="retiring", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),
        Property(
            id=uuid4(), address="7 Chestnut Avenue", suburb="Bayswater",
            state="VIC", postcode="3153", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=750,
            building_size_sqm=120, year_built=1968, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=680_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/7-chestnut-bw",
            listing_text="750m² block with massive subdivision potential in Bayswater. "
                         "Level crossing removal has transformed the suburb. NRZ — "
                         "rear lot subdivision feasible. Original condition — "
                         "reno front home + build rear townhouse. Vendor lost tenant, "
                         "can't service mortgage. URGENT SALE.",
            agent_name="Tony Nguyen", agent_phone="0401 777 888",
            agency_name="First National Bayswater",
            estimated_weekly_rent=520, council_rates_annual=1_500, water_rates_annual=600,
            zoning="NRZ1",
            distress_signals=[
                DistressSignal(keyword="can't service mortgage", confidence=0.92, source="listing_text"),
                DistressSignal(keyword="urgent sale", confidence=0.90, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),

        # ── INNER SOUTH (2) ───────────────────────────────────────
        Property(
            id=uuid4(), address="6/22 Park Street", suburb="South Yarra",
            state="VIC", postcode="3141", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=72,
            year_built=1975, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=620_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/6-22-park-sy",
            listing_text="Unrenovated apartment in prestige South Yarra. Toorak Road shops, "
                         "proximity to Chapel Street retail precinct. Vendor elderly, "
                         "moving to nursing home — power of attorney sale. Reno to premium "
                         "finish = instant 15-20% uplift. Current condition drags price down.",
            agent_name="Charlotte Mills", agent_phone="0412 000 123",
            agency_name="Marshall White South Yarra",
            estimated_weekly_rent=480, council_rates_annual=1_100, water_rates_annual=500,
            strata_levies_quarterly=1_000,
            distress_signals=[
                DistressSignal(keyword="power of attorney", confidence=0.92, source="listing_text"),
                DistressSignal(keyword="nursing home", confidence=0.88, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(), address="48 Mitford Street", suburb="St Kilda",
            state="VIC", postcode="3182", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=0, land_size_sqm=320,
            building_size_sqm=180, year_built=1905, condition=PropertyCondition.FAIR,
            asking_price=1_280_000, listing_status=ListingStatus.AUCTION,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/48-mitford-sk",
            listing_text="Grand Edwardian residence in St Kilda — one of Melbourne's most "
                         "desirable beachside suburbs. 4 large bedrooms, original period "
                         "features. R2SA/Airbnb goldmine location — Acland Street 200m, beach 300m. "
                         "Vendor inherited, does not want property. Auction reserve low.",
            agent_name="Hugo Bancroft", agent_phone="0423 123 456",
            agency_name="Buxton Real Estate",
            estimated_weekly_rent=800, council_rates_annual=2_400, water_rates_annual=700,
            zoning="NRZ1",
            distress_signals=[
                DistressSignal(keyword="inherited", confidence=0.85, source="listing_text"),
                DistressSignal(keyword="does not want property", confidence=0.88, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),

        # ── SOUTH EAST (3) ────────────────────────────────────────
        Property(
            id=uuid4(), address="34 Walker Street", suburb="Dandenong",
            state="VIC", postcode="3175", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=580,
            building_size_sqm=105, year_built=1960, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=520_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/34-walker-dand",
            listing_text="Entry-level house on 580m² in Revitalised Central Dandenong. "
                         "$290M government renewal project transforming suburb. GRZ1 — "
                         "dual occupancy potential. Mortgagee in possession. "
                         "Walk to Dandenong Market, Dandenong station.",
            agent_name="Singh Paramjit", agent_phone="0434 234 567",
            agency_name="Ray White Dandenong",
            estimated_weekly_rent=420, council_rates_annual=1_300, water_rates_annual=550,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="mortgagee", confidence=0.95, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),
        Property(
            id=uuid4(), address="12 Panorama Drive", suburb="Berwick",
            state="VIC", postcode="3806", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=600,
            building_size_sqm=210, year_built=2010, condition=PropertyCondition.GOOD,
            asking_price=720_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/12-panorama-bw",
            listing_text="Spacious family home in Berwick with room for granny flat. "
                         "Vendor relocating overseas for work contract. Tenanted at $550/wk. "
                         "Walk to Casey Grammar, Berwick Village. "
                         "600m² block — DPU/granny flat feasible for dual income.",
            agent_name="Emily Tucker", agent_phone="0445 345 678",
            agency_name="Barry Plant Berwick",
            estimated_weekly_rent=550, council_rates_annual=1_700, water_rates_annual=650,
            distress_signals=[
                DistressSignal(keyword="relocating overseas", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),
        Property(
            id=uuid4(), address="LOT 445 Heritage Boulevard", suburb="Pakenham",
            state="VIC", postcode="3810", property_type=PropertyType.LAND,
            bedrooms=0, bathrooms=0, car_spaces=0, land_size_sqm=450,
            year_built=None, condition=PropertyCondition.UNKNOWN,
            asking_price=310_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/lot-445-pakenham",
            listing_text="Titled block in Pakenham East PSP. Ready to build. "
                         "Build 4BR for $300K = total package $610K. Rent at $480/wk. "
                         "Pakenham East growth corridor — population doubling by 2035. "
                         "Pakenham Level Crossing Removals and Metro Trains Cranbourne-Pakenham corridor upgrades.",
            agent_name="Chris Waters", agent_phone="0456 456 789",
            agency_name="Stockdale & Leggo Pakenham",
            estimated_weekly_rent=0, council_rates_annual=1_100, water_rates_annual=400,
            distress_signals=[],
            created_at=now - timedelta(days=12),
        ),

        # ── NORTHERN GROWTH (2) ───────────────────────────────────
        Property(
            id=uuid4(), address="27 Craigieburn Road", suburb="Craigieburn",
            state="VIC", postcode="3064", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=480,
            building_size_sqm=195, year_built=2020, condition=PropertyCondition.EXCELLENT,
            asking_price=600_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/27-craigieburn",
            listing_text="As-new display home in Craigieburn. Builder went into liquidation — "
                         "administrator sale. Premium fixtures, stone benchtops, "
                         "ducted heating/cooling. Tenantable at $520/wk immediately. "
                         "Craigieburn Central 2 mins. Hume Freeway 5 mins to city.",
            agent_name="Michael Pham", agent_phone="0467 567 890",
            agency_name="Raine & Horne",
            estimated_weekly_rent=520, council_rates_annual=1_500, water_rates_annual=600,
            distress_signals=[
                DistressSignal(keyword="administrator sale", confidence=0.92, source="listing_text"),
                DistressSignal(keyword="liquidation", confidence=0.90, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(), address="55 Dalton Road", suburb="Thomastown",
            state="VIC", postcode="3074", property_type=PropertyType.DUPLEX,
            bedrooms=6, bathrooms=3, car_spaces=4, land_size_sqm=700,
            building_size_sqm=240, year_built=2015, condition=PropertyCondition.GOOD,
            asking_price=850_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.OFF_MARKET,
            source_url="https://example.com/listing/55-dalton-thom",
            listing_text="Dual-income duplex — 2 × 3BR units on one title. "
                         "Combined rent $920/wk. Vendor wants to consolidate portfolio — "
                         "selling to fund larger development. Each unit has separate entry, "
                         "own laundry, courtyard. Walk to Thomastown station.",
            agent_name="Steve Kakos", agent_phone="0478 678 901",
            agency_name="LJ Hooker Thomastown",
            estimated_weekly_rent=920, council_rates_annual=2_200, water_rates_annual=800,
            distress_signals=[],
            created_at=now - timedelta(days=7),
        ),

        # ── BAYSIDE & PENINSULA (2) ───────────────────────────────
        Property(
            id=uuid4(), address="3 Beach Road", suburb="Frankston",
            state="VIC", postcode="3199", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=1, land_size_sqm=550,
            building_size_sqm=110, year_built=1960, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=620_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/3-beach-frank",
            listing_text="Original beachside home 200m from Frankston foreshore. "
                         "Frankston MAC + Health & Education Precinct transforming suburb. "
                         "550m² block — subdivision potential. Heritage-free. "
                         "Vendor bankrupt — trustee sale. Last comparable sold $780K renovated.",
            agent_name="Brooke Henderson", agent_phone="0489 789 012",
            agency_name="OBrien Frankston",
            estimated_weekly_rent=480, council_rates_annual=1_400, water_rates_annual=550,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="bankrupt", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="trustee sale", confidence=0.92, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),
        Property(
            id=uuid4(), address="15 The Boulevard", suburb="Mornington",
            state="VIC", postcode="3931", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=700,
            building_size_sqm=200, year_built=1985, condition=PropertyCondition.FAIR,
            asking_price=880_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/15-blvd-morn",
            listing_text="Family home in Mornington village on generous 700m² block. "
                         "Walk to Main Street shops, Mornington Pier. "
                         "High R2SA potential — Mornington Peninsula holiday rental goldmine. "
                         "Vendor downsizing. Cosmetic reno + Airbnb setup = significantly "
                         "higher yield than standard rental.",
            agent_name="Lisa Wang", agent_phone="0401 890 123",
            agency_name="RT Edgar Mornington",
            estimated_weekly_rent=650, council_rates_annual=1_900, water_rates_annual=650,
            distress_signals=[
                DistressSignal(keyword="downsizing", confidence=0.70, source="listing_text"),
            ],
            created_at=now - timedelta(days=9),
        ),

        # ── GEELONG & SURF COAST (4) ──────────────────────────────
        Property(
            id=uuid4(), address="88 Moorabool Street", suburb="Geelong",
            state="VIC", postcode="3220", property_type=PropertyType.COMMERCIAL,
            bedrooms=0, bathrooms=2, car_spaces=3, building_size_sqm=180,
            year_built=1920, condition=PropertyCondition.FAIR,
            asking_price=680_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/88-moorabool",
            listing_text="Heritage commercial building on Geelong's main street. "
                         "Geelong City Deal $370M transformation underway. "
                         "Currently leased as office — vendor wants to exit commercial. "
                         "Mixed-use conversion potential: ground floor retail + 2 apartments above. "
                         "5.6% net yield on current lease.",
            agent_name="Peter Collins", agent_phone="0412 901 234",
            agency_name="Buxton Geelong",
            estimated_weekly_rent=730, council_rates_annual=3_200, water_rates_annual=600,
            distress_signals=[],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(), address="12 Heales Street", suburb="Norlane",
            state="VIC", postcode="3214", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=1, land_size_sqm=600,
            building_size_sqm=100, year_built=1955, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=380_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/12-heales-norl",
            listing_text="Affordable entry in Norlane — early gentrification suburb in Northern Geelong. "
                         "600m² block, GRZ1. Community Renewal Program driving change. "
                         "Mortgagee in possession. Reno cost ~$40K for a $100K+ value uplift. "
                         "Comparable renovated homes selling at $520K+.",
            agent_name="Angela Marino", agent_phone="0423 012 345",
            agency_name="Hayeswinckle",
            estimated_weekly_rent=360, council_rates_annual=1_200, water_rates_annual=500,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="mortgagee", confidence=0.95, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),
        Property(
            id=uuid4(), address="7 Caravan Court", suburb="Armstrong Creek",
            state="VIC", postcode="3217", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=400,
            building_size_sqm=190, year_built=2022, condition=PropertyCondition.EXCELLENT,
            asking_price=620_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/7-caravan-ac",
            listing_text="Near-new home in Armstrong Creek — Geelong's fastest growing suburb. "
                         "Town Centre planned for 70,000 residents. Builder vendor — "
                         "display home contract ended. Premium fixtures + landscaping. "
                         "Tenantable at $520/wk. V/Line to Southern Cross 55 mins.",
            agent_name="Josh Fleming", agent_phone="0434 123 456",
            agency_name="Maxwell Collins",
            estimated_weekly_rent=520, council_rates_annual=1_600, water_rates_annual=600,
            distress_signals=[],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(), address="22 Corio Bay Road", suburb="Corio",
            state="VIC", postcode="3214", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=650,
            building_size_sqm=110, year_built=1960, condition=PropertyCondition.FAIR,
            asking_price=430_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/22-corio-bay",
            listing_text="Solid brick home on 650m² in Corio — Northern Geelong growth area. "
                         "GRZ1 zoning. Granny flat potential on rear of block. "
                         "Current rent $380/wk. Vendor has 4 IPs — selling to reduce debt. "
                         "Northern Geelong Growth Area Plan will bring rail upgrade.",
            agent_name="Sandra Kozlovic", agent_phone="0445 234 567",
            agency_name="Barry Plant Geelong",
            estimated_weekly_rent=380, council_rates_annual=1_200, water_rates_annual=500,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="selling to reduce debt", confidence=0.80, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),

        # ── BENDIGO & GOLDFIELDS (3) ──────────────────────────────
        Property(
            id=uuid4(), address="45 Mitchell Street", suburb="Bendigo",
            state="VIC", postcode="3550", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=700,
            building_size_sqm=170, year_built=1910, condition=PropertyCondition.FAIR,
            asking_price=490_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/45-mitchell-bend",
            listing_text="Grand Victorian-era home in central Bendigo on 700m² block. "
                         "Walk to Bendigo Hospital ($630M expansion) + GovHub. "
                         "Heritage overlay — maintain facade, modernise interior. "
                         "Vendor elderly, children managing sale from Melbourne. "
                         "V/Line fast rail to Melbourne 90 mins.",
            agent_name="Craig Torney", agent_phone="0456 345 678",
            agency_name="McKean McGregor",
            estimated_weekly_rent=450, council_rates_annual=1_500, water_rates_annual=550,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="elderly vendor", confidence=0.78, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(), address="8 Parker Street", suburb="Kangaroo Flat",
            state="VIC", postcode="3555", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=800,
            building_size_sqm=110, year_built=1965, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=395_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/8-parker-kf",
            listing_text="Original brick home on massive 800m² in Kangaroo Flat. "
                         "Subdivision potential — retain front, build rear townhouse. "
                         "Executor sale — elderly vendor passed. Tenanted at $350/wk. "
                         "Bendigo rail to Melbourne. Kangaroo Flat Marketplace 1km.",
            agent_name="Glenn Anderson", agent_phone="0467 456 789",
            agency_name="PRD Bendigo",
            estimated_weekly_rent=350, council_rates_annual=1_200, water_rates_annual=500,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="executor sale", confidence=0.90, source="listing_text"),
                DistressSignal(keyword="deceased", confidence=0.92, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(), address="16 Eaglehawk Road", suburb="Eaglehawk",
            state="VIC", postcode="3556", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=1, land_size_sqm=650,
            building_size_sqm=95, year_built=1950, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=350_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.OFF_MARKET,
            source_url="https://example.com/listing/16-eaglehawk-rd",
            listing_text="Budget entry to Greater Bendigo on 650m² block. "
                         "Early gentrification area — 5km from Bendigo CBD. "
                         "Reno cost $35K estimated for $80K+ value uplift. "
                         "Current rent $320/wk = 4.7% gross yield AS-IS. "
                         "Vendor in financial hardship — agent says make offer.",
            agent_name="Wayne Harris", agent_phone="0478 567 890",
            agency_name="Tweed Sutherland",
            estimated_weekly_rent=320, council_rates_annual=1_000, water_rates_annual=450,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="financial hardship", confidence=0.88, source="listing_text"),
                DistressSignal(keyword="make offer", confidence=0.82, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),

        # ── BALLARAT & CENTRAL HIGHLANDS (2) ──────────────────────
        Property(
            id=uuid4(), address="33 Sturt Street", suburb="Ballarat",
            state="VIC", postcode="3350", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=1, car_spaces=2, land_size_sqm=750,
            building_size_sqm=155, year_built=1890, condition=PropertyCondition.FAIR,
            asking_price=460_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/33-sturt-ball",
            listing_text="Stunning period home on 750m² in central Ballarat. "
                         "Walk to GovHub + Station Precinct redevelopment. "
                         "Heritage facade — modernise interior for premium rental. "
                         "V/Line fast rail to Melbourne 70 mins. "
                         "Federation University campus nearby. Vendor downsizing to unit.",
            agent_name="Wendy Richards", agent_phone="0489 678 901",
            agency_name="PRD Ballarat",
            estimated_weekly_rent=430, council_rates_annual=1_400, water_rates_annual=550,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="downsizing", confidence=0.70, source="listing_text"),
            ],
            created_at=now - timedelta(days=7),
        ),
        Property(
            id=uuid4(), address="LOT 88 Delacombe Drive", suburb="Delacombe",
            state="VIC", postcode="3356", property_type=PropertyType.LAND,
            bedrooms=0, bathrooms=0, car_spaces=0, land_size_sqm=500,
            year_built=None, condition=PropertyCondition.UNKNOWN,
            asking_price=220_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/lot-88-delacombe",
            listing_text="Titled 500m² block in Delacombe Town Centre development. "
                         "Build 4BR home for $280K. Total package $500K. "
                         "Rent at $420/wk = 4.4% yield on build cost. "
                         "Ballarat fastest growing city in regional VIC.",
            agent_name="Andrew Knight", agent_phone="0401 789 012",
            agency_name="Jellis Craig Ballarat",
            estimated_weekly_rent=0, council_rates_annual=1_000, water_rates_annual=400,
            distress_signals=[],
            created_at=now - timedelta(days=14),
        ),

        # ── GIPPSLAND (2) ─────────────────────────────────────────
        Property(
            id=uuid4(), address="18 Church Street", suburb="Traralgon",
            state="VIC", postcode="3844", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=650,
            building_size_sqm=120, year_built=1970, condition=PropertyCondition.FAIR,
            asking_price=340_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/18-church-trar",
            listing_text="Affordable family home in Traralgon — Gippsland's service hub. "
                         "SEC revival + Gippsland Logistics Precinct creating jobs. "
                         "Current rent $350/wk = 5.3% gross yield. "
                         "650m² block with granny flat potential. "
                         "V/Line to Melbourne 2hrs. Vendor relocating for FIFO work.",
            agent_name="Brett Lawson", agent_phone="0412 890 123",
            agency_name="Latrobe Valley Real Estate",
            estimated_weekly_rent=350, council_rates_annual=1_200, water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.80, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(), address="5 Railway Street", suburb="Warragul",
            state="VIC", postcode="3820", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=2, car_spaces=1, land_size_sqm=450,
            building_size_sqm=130, year_built=2008, condition=PropertyCondition.GOOD,
            asking_price=510_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/5-railway-warr",
            listing_text="Modern home in Warragul — the Gippsland commuter belt. "
                         "V/Line to Melbourne 90 mins. Walk to Warragul CBD + schools. "
                         "Warragul-Drouin growth corridor booming. "
                         "Tenanted at $440/wk. Vendor upgrading to acreage.",
            agent_name="Hannah Reid", agent_phone="0423 901 234",
            agency_name="Strzelecki Realty",
            estimated_weekly_rent=440, council_rates_annual=1_300, water_rates_annual=550,
            distress_signals=[],
            created_at=now - timedelta(days=8),
        ),

        # ── HUME & NORTH EAST VIC (2) ─────────────────────────────
        Property(
            id=uuid4(), address="22 Wyndham Street", suburb="Shepparton",
            state="VIC", postcode="3630", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=1, car_spaces=2, land_size_sqm=750,
            building_size_sqm=140, year_built=1955, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=340_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/22-wyndham-shep",
            listing_text="Solid brick home on 750m² in central Shepparton. "
                         "GV Health $229M hospital redevelopment + SAM museum revitalisation. "
                         "Subdivision potential. Reno + subdivide rear = huge upside. "
                         "Current rent $340/wk = 5.2% AS-IS. Mortgagee — bank says sell.",
            agent_name="Paul Hocking", agent_phone="0434 012 345",
            agency_name="Nutrien Harcourts",
            estimated_weekly_rent=340, council_rates_annual=1_200, water_rates_annual=500,
            zoning="GRZ1",
            distress_signals=[
                DistressSignal(keyword="mortgagee", confidence=0.95, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),
        Property(
            id=uuid4(), address="9 High Street", suburb="Wodonga",
            state="VIC", postcode="3690", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=600,
            building_size_sqm=115, year_built=1975, condition=PropertyCondition.FAIR,
            asking_price=420_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/9-high-wodonga",
            listing_text="Well-positioned home in Wodonga near Junction Place precinct. "
                         "Rail bypass complete — no more freight trains through town. "
                         "Vendor retired farmer moving to coast. Steady rental $390/wk. "
                         "Border town advantage — NSW workers, VIC cost of living.",
            agent_name="Kevin Mitchell", agent_phone="0445 123 456",
            agency_name="First National Wodonga",
            estimated_weekly_rent=390, council_rates_annual=1_300, water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="retired", confidence=0.70, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),

        # ═══════════════════════════════════════════════════════════
        # NSW — SYDNEY & REGIONAL (8)
        # ═══════════════════════════════════════════════════════════

        Property(
            id=uuid4(), address="12/88 Liverpool Street", suburb="Sydney CBD",
            state="NSW", postcode="2000", property_type=PropertyType.APARTMENT,
            bedrooms=1, bathrooms=1, car_spaces=0, building_size_sqm=52,
            year_built=2016, condition=PropertyCondition.GOOD,
            asking_price=680_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/12-88-liverpool",
            listing_text="Inner city apartment near Town Hall. Overseas investor liquidating "
                         "Australian portfolio — 3 units being sold simultaneously. "
                         "Tenanted at $650/wk. Walk to George Street light rail. "
                         "Sydney Metro West will add further connectivity 2032.",
            agent_name="Michelle Tang", agent_phone="0412 555 111",
            agency_name="Ray White City South",
            estimated_weekly_rent=650, council_rates_annual=800, water_rates_annual=500,
            strata_levies_quarterly=1_900,
            distress_signals=[
                DistressSignal(keyword="liquidating portfolio", confidence=0.90, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(), address="45 King Street", suburb="Newtown",
            state="NSW", postcode="2042", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=0, land_size_sqm=240,
            building_size_sqm=110, year_built=1910, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=1_450_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/45-king-newtown",
            listing_text="Original Victorian terrace on King Street. Deceased estate — "
                         "executors seeking quick sale. Heritage listed facade, rear extension "
                         "potential STCA. Walk to Newtown station, King Street restaurants. "
                         "One of Sydney's most sought-after inner-west addresses.",
            agent_name="James Pratt", agent_phone="0423 666 222",
            agency_name="BresicWhitney Newtown",
            estimated_weekly_rent=850, council_rates_annual=2_000, water_rates_annual=700,
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="quick sale", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),
        Property(
            id=uuid4(), address="78 Wentworth Avenue", suburb="Parramatta",
            state="NSW", postcode="2150", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=2, car_spaces=1, building_size_sqm=85,
            year_built=2020, condition=PropertyCondition.GOOD,
            asking_price=620_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.OFF_MARKET,
            source_url="https://example.com/listing/78-wentworth-parra",
            listing_text="Near-new apartment in Parramatta CBD. Sydney Metro West station "
                         "400m away — transformative infrastructure. Parramatta Light Rail operational. "
                         "Tenanted at $580/wk. Owner facing margin call on share portfolio.",
            agent_name="David Park", agent_phone="0434 777 333",
            agency_name="Laing+Simmons Parramatta",
            estimated_weekly_rent=580, council_rates_annual=900, water_rates_annual=500,
            strata_levies_quarterly=1_500,
            distress_signals=[
                DistressSignal(keyword="margin call", confidence=0.88, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(), address="15 Railway Parade", suburb="Penrith",
            state="NSW", postcode="2750", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=580,
            building_size_sqm=155, year_built=2005, condition=PropertyCondition.GOOD,
            asking_price=750_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/15-railway-penrith",
            listing_text="Spacious family home near Penrith station. Western Sydney Airport "
                         "(2026) will transform this corridor. Tenanted at $600/wk. "
                         "Walk to Westfield Penrith. Vendor upgrading to acreage in Blue Mountains.",
            agent_name="Sarah Collins", agent_phone="0445 888 444",
            agency_name="McGrath Penrith",
            estimated_weekly_rent=600, council_rates_annual=1_600, water_rates_annual=600,
            distress_signals=[],
            created_at=now - timedelta(days=10),
        ),
        Property(
            id=uuid4(), address="8 Hunter Street", suburb="Newcastle",
            state="NSW", postcode="2300", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=75,
            year_built=2019, condition=PropertyCondition.GOOD,
            asking_price=580_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/8-hunter-newcastle",
            listing_text="Inner-city apartment in revitalised Newcastle East. Hunter Street "
                         "transformation creating cafe and retail precinct. Light rail at door. "
                         "Strong rental demand from university students and professionals. "
                         "Tenanted at $480/wk. Vendor divorcing — needs settlement funds.",
            agent_name="Luke Harris", agent_phone="0456 999 555",
            agency_name="Robinson Property Newcastle",
            estimated_weekly_rent=480, council_rates_annual=1_100, water_rates_annual=550,
            strata_levies_quarterly=1_200,
            distress_signals=[
                DistressSignal(keyword="divorcing", confidence=0.92, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),

        # ═══════════════════════════════════════════════════════════
        # QLD — BRISBANE, GOLD COAST & REGIONAL (8)
        # ═══════════════════════════════════════════════════════════

        Property(
            id=uuid4(), address="2205/120 Mary Street", suburb="Brisbane CBD",
            state="QLD", postcode="4000", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=2, car_spaces=1, building_size_sqm=78,
            year_built=2022, condition=PropertyCondition.GOOD,
            asking_price=580_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/2205-120-mary",
            listing_text="Near-new apartment in Brisbane CBD. Cross River Rail opening 2025 "
                         "will add Roma Street station 200m away. Queen's Wharf casino and "
                         "entertainment precinct opening next door. City views. "
                         "Currently tenanted at $620/wk. 2032 Olympic city — buy NOW.",
            agent_name="Chris Wong", agent_phone="0412 111 666",
            agency_name="Place Estate Agents",
            estimated_weekly_rent=620, council_rates_annual=1_000, water_rates_annual=500,
            strata_levies_quarterly=1_400,
            distress_signals=[],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(), address="18 Vulture Street", suburb="Woolloongabba",
            state="QLD", postcode="4102", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=1, land_size_sqm=405,
            building_size_sqm=100, year_built=1940, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=820_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.OFF_MARKET,
            source_url="https://example.com/listing/18-vulture-woolloongabba",
            listing_text="Post-war Queenslander on 405m² — 2032 Olympic zone ground zero. "
                         "Gabba rebuild will transform this entire precinct. Cross River Rail "
                         "station 300m walk. Reno + hold strategy with subdivision potential STCA. "
                         "Deceased estate — family wants quick resolution.",
            agent_name="Amanda Lee", agent_phone="0423 222 777",
            agency_name="Ray White Woolloongabba",
            estimated_weekly_rent=620, council_rates_annual=1_800, water_rates_annual=600,
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="quick resolution", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),
        Property(
            id=uuid4(), address="55 Gold Coast Highway", suburb="Surfers Paradise",
            state="QLD", postcode="4217", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=2, car_spaces=1, building_size_sqm=90,
            year_built=2015, condition=PropertyCondition.GOOD,
            asking_price=650_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/55-gc-hwy-surfers",
            listing_text="Ocean-view apartment in Surfers Paradise with pool and gym. "
                         "Gold Coast Light Rail Stage 3C will add station nearby. "
                         "Strong Airbnb potential — $280/night peak season. "
                         "Owner retiring and downsizing to hinterland.",
            agent_name="Tiffany Blake", agent_phone="0434 333 888",
            agency_name="Kollosche",
            estimated_weekly_rent=580, council_rates_annual=1_200, water_rates_annual=500,
            strata_levies_quarterly=1_800,
            distress_signals=[
                DistressSignal(keyword="retiring", confidence=0.65, source="listing_text"),
            ],
            created_at=now - timedelta(days=7),
        ),
        Property(
            id=uuid4(), address="12 Station Road", suburb="Logan Central",
            state="QLD", postcode="4114", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=600,
            building_size_sqm=100, year_built=1985, condition=PropertyCondition.FAIR,
            asking_price=480_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/12-station-logan",
            listing_text="Affordable house in Logan — SEQ's highest-yield corridor. "
                         "600m² block with granny flat potential STCA. "
                         "Tenanted at $480/wk = 5.2% gross yield. "
                         "Logan Metro enhancement creating jobs. Interstate migration flooding area. "
                         "Mortgagee sale — bank instructed disposal.",
            agent_name="Wayne Nguyen", agent_phone="0445 444 999",
            agency_name="LJ Hooker Logan",
            estimated_weekly_rent=480, council_rates_annual=1_300, water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="mortgagee sale", confidence=0.95, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),
        Property(
            id=uuid4(), address="77 Brisbane Road", suburb="Ipswich",
            state="QLD", postcode="4305", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=1, car_spaces=2, land_size_sqm=800,
            building_size_sqm=130, year_built=1960, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=420_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/77-brisbane-rd-ipswich",
            listing_text="Solid Queenslander on 800m² in central Ipswich. "
                         "Subdivision potential for 2 lots STCA. "
                         "Springfield employment corridor nearby. "
                         "Ipswich CBD revitalisation underway. "
                         "Vendor in financial distress — bank says sell within 30 days.",
            agent_name="Greg Murphy", agent_phone="0456 555 000",
            agency_name="Purplebricks Ipswich",
            estimated_weekly_rent=420, council_rates_annual=1_400, water_rates_annual=500,
            zoning="Low-Medium Density Residential",
            distress_signals=[
                DistressSignal(keyword="financial distress", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="sell within 30 days", confidence=0.90, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),

        # ═══════════════════════════════════════════════════════════
        # SA — ADELAIDE (5)
        # ═══════════════════════════════════════════════════════════

        Property(
            id=uuid4(), address="22 The Parade", suburb="Norwood",
            state="SA", postcode="5067", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=2, car_spaces=1, land_size_sqm=420,
            building_size_sqm=145, year_built=1920, condition=PropertyCondition.GOOD,
            asking_price=950_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/22-parade-norwood",
            listing_text="Character bluestone home on The Parade — Adelaide's premier strip. "
                         "Beautifully renovated. Walk to cafes, shops, and parklands. "
                         "Adelaide market surging 14%+ YoY. Tenanted at $680/wk. "
                         "Owner relocating to London for work.",
            agent_name="Sophie Martin", agent_phone="0412 666 111",
            agency_name="Ouwens Casserly",
            estimated_weekly_rent=680, council_rates_annual=1_800, water_rates_annual=600,
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.80, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(), address="8 Victoria Road", suburb="Elizabeth",
            state="SA", postcode="5112", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=700,
            building_size_sqm=100, year_built=1968, condition=PropertyCondition.FAIR,
            asking_price=380_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/8-victoria-elizabeth",
            listing_text="Affordable home near Edinburgh Defence Precinct — AUKUS submarine "
                         "program creating 30+ years of jobs. Elizabeth is Adelaide's hottest "
                         "growth suburb — 18% YoY. 700m² block with subdivision potential. "
                         "Tenanted at $400/wk = 5.5% gross yield. Bank-instructed sale.",
            agent_name="Ben Cooper", agent_phone="0423 777 222",
            agency_name="LJ Hooker Elizabeth",
            estimated_weekly_rent=400, council_rates_annual=1_200, water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="bank-instructed", confidence=0.92, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(), address="5 Commercial Road", suburb="Osborne",
            state="SA", postcode="5017", property_type=PropertyType.HOUSE,
            bedrooms=2, bathrooms=1, car_spaces=1, land_size_sqm=550,
            building_size_sqm=80, year_built=1955, condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=480_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.OFF_MARKET,
            source_url="https://example.com/listing/5-commercial-osborne",
            listing_text="Reno opportunity in Osborne — ground zero for AUKUS submarine build. "
                         "BAE Systems shipyard 1km away. Massive workforce demand incoming. "
                         "550m² — subdivision STCA. Defence housing demand will be explosive. "
                         "Vendor deceased estate — executors accepting offers.",
            agent_name="Mark Stevens", agent_phone="0434 888 333",
            agency_name="Harcourts Port Adelaide",
            estimated_weekly_rent=380, council_rates_annual=1_100, water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),

        # ═══════════════════════════════════════════════════════════
        # WA — PERTH (5)
        # ═══════════════════════════════════════════════════════════

        Property(
            id=uuid4(), address="33 Hay Street", suburb="Subiaco",
            state="WA", postcode="6008", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=2, car_spaces=2, land_size_sqm=450,
            building_size_sqm=160, year_built=2005, condition=PropertyCondition.GOOD,
            asking_price=1_100_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/33-hay-subiaco",
            listing_text="Premium Subiaco home near the Subi East redevelopment. "
                         "Perth's hottest market — 18.5% growth YoY. Walk to Subiaco train. "
                         "Tenanted at $750/wk. Owner FIFO worker moving to Queensland.",
            agent_name="Ryan O'Brien", agent_phone="0412 999 444",
            agency_name="Acton Dalkeith",
            estimated_weekly_rent=750, council_rates_annual=2_200, water_rates_annual=700,
            distress_signals=[
                DistressSignal(keyword="moving", confidence=0.65, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),
        Property(
            id=uuid4(), address="18 Star Street", suburb="Armadale",
            state="WA", postcode="6112", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=680,
            building_size_sqm=140, year_built=2010, condition=PropertyCondition.GOOD,
            asking_price=420_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/18-star-armadale",
            listing_text="Modern family home in Armadale — Perth's fastest growing affordable "
                         "corridor. METRONET Byford Extension will add station nearby. "
                         "22% growth YoY. Tenanted at $500/wk = 6.2% yield. "
                         "Vendor divorcing — forced sale, accepting offers below asking.",
            agent_name="Jade Williams", agent_phone="0423 000 555",
            agency_name="Professionals Armadale",
            estimated_weekly_rent=500, council_rates_annual=1_400, water_rates_annual=600,
            distress_signals=[
                DistressSignal(keyword="forced sale", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="divorcing", confidence=0.92, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),
        Property(
            id=uuid4(), address="5 Adelaide Terrace", suburb="Fremantle",
            state="WA", postcode="6160", property_type=PropertyType.TOWNHOUSE,
            bedrooms=3, bathrooms=2, car_spaces=1, land_size_sqm=180,
            building_size_sqm=125, year_built=2018, condition=PropertyCondition.GOOD,
            asking_price=780_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/5-adelaide-fremantle",
            listing_text="Modern townhouse in Fremantle near the harbour. "
                         "Fremantle Port Inner Harbour renewal will transform area. "
                         "Walk to Cappuccino Strip, markets, and beach. "
                         "Perth market surging. Tenanted at $600/wk.",
            agent_name="Emma Davies", agent_phone="0434 111 666",
            agency_name="Caporn Young",
            estimated_weekly_rent=600, council_rates_annual=1_800, water_rates_annual=600,
            strata_levies_quarterly=900,
            distress_signals=[],
            created_at=now - timedelta(days=8),
        ),

        # ═══════════════════════════════════════════════════════════
        # TAS — HOBART & LAUNCESTON (3)
        # ═══════════════════════════════════════════════════════════

        Property(
            id=uuid4(), address="42 Davey Street", suburb="Hobart CBD",
            state="TAS", postcode="7000", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=72,
            year_built=2017, condition=PropertyCondition.GOOD,
            asking_price=480_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/42-davey-hobart",
            listing_text="Inner-city apartment near Salamanca Place. Hobart City Deal "
                         "transforming waterfront. Macquarie Point renewal 500m away. "
                         "Strong tourism-driven Airbnb potential. "
                         "Current tenant at $480/wk. Owner relocating to mainland.",
            agent_name="Tom Fletcher", agent_phone="0412 222 888",
            agency_name="Knight Frank Tasmania",
            estimated_weekly_rent=480, council_rates_annual=1_200, water_rates_annual=500,
            strata_levies_quarterly=1_100,
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(), address="15 George Street", suburb="Launceston",
            state="TAS", postcode="7250", property_type=PropertyType.HOUSE,
            bedrooms=3, bathrooms=1, car_spaces=2, land_size_sqm=550,
            building_size_sqm=110, year_built=1935, condition=PropertyCondition.FAIR,
            asking_price=420_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/15-george-launceston",
            listing_text="Character home near UTAS Inveresk Campus. Launceston City Heart "
                         "project creating buzz. Steady rental at $420/wk. "
                         "Subdivision potential on 550m² STCA. Vendor is retiring farmer.",
            agent_name="Penny Hart", agent_phone="0423 333 999",
            agency_name="Harcourts Launceston",
            estimated_weekly_rent=420, council_rates_annual=1_300, water_rates_annual=550,
            distress_signals=[
                DistressSignal(keyword="retiring", confidence=0.65, source="listing_text"),
            ],
            created_at=now - timedelta(days=9),
        ),

        # ═══════════════════════════════════════════════════════════
        # NT — DARWIN (2)
        # ═══════════════════════════════════════════════════════════

        Property(
            id=uuid4(), address="8 Mitchell Street", suburb="Darwin CBD",
            state="NT", postcode="0800", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=70,
            year_built=2014, condition=PropertyCondition.GOOD,
            asking_price=340_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.OFF_MARKET,
            source_url="https://example.com/listing/8-mitchell-darwin",
            listing_text="CBD apartment with harbour views. Darwin City Deal and Middle Arm "
                         "development creating jobs. No stamp duty for owner-occupiers <$525K. "
                         "Highest yields nationally — tenanted at $420/wk = 6.4% gross. "
                         "Defence spending and gas projects underpinning. FIFO vendor returning south.",
            agent_name="Jack Morrison", agent_phone="0434 444 000",
            agency_name="Elders Real Estate Darwin",
            estimated_weekly_rent=420, council_rates_annual=1_500, water_rates_annual=600,
            strata_levies_quarterly=1_400,
            distress_signals=[
                DistressSignal(keyword="returning south", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(), address="22 Temple Terrace", suburb="Palmerston",
            state="NT", postcode="0830", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=700,
            building_size_sqm=150, year_built=2008, condition=PropertyCondition.GOOD,
            asking_price=430_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/22-temple-palmerston",
            listing_text="Spacious family home in Palmerston — Darwin's growth hub. "
                         "Near Palmerston Regional Hospital. US Marine presence boosting demand. "
                         "Tenanted at $520/wk = 6.3% yield. "
                         "Vendor accepting offers — relocating to Brisbane.",
            agent_name="Steve Tran", agent_phone="0445 555 111",
            agency_name="Raine & Horne Darwin",
            estimated_weekly_rent=520, council_rates_annual=1_600, water_rates_annual=650,
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.78, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),

        # ═══════════════════════════════════════════════════════════
        # ACT — CANBERRA (3)
        # ═══════════════════════════════════════════════════════════

        Property(
            id=uuid4(), address="15 Lonsdale Street", suburb="Braddon",
            state="ACT", postcode="2612", property_type=PropertyType.APARTMENT,
            bedrooms=2, bathrooms=1, car_spaces=1, building_size_sqm=75,
            year_built=2019, condition=PropertyCondition.GOOD,
            asking_price=550_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/15-lonsdale-braddon",
            listing_text="Modern apartment on Lonsdale Street — Canberra's hippest strip. "
                         "Light Rail Stage 1 at doorstep. Walk to ANU, Civic, and cafes. "
                         "Strong public servant rental demand. Tenanted at $520/wk. "
                         "ACT transitioning to land tax — no more stamp duty barrier.",
            agent_name="Rebecca Lee", agent_phone="0412 888 222",
            agency_name="Luton Properties Braddon",
            estimated_weekly_rent=520, council_rates_annual=1_400, water_rates_annual=550,
            strata_levies_quarterly=1_200,
            distress_signals=[],
            created_at=now - timedelta(days=7),
        ),
        Property(
            id=uuid4(), address="8 Anketell Street", suburb="Tuggeranong",
            state="ACT", postcode="2900", property_type=PropertyType.HOUSE,
            bedrooms=4, bathrooms=2, car_spaces=2, land_size_sqm=600,
            building_size_sqm=170, year_built=1990, condition=PropertyCondition.GOOD,
            asking_price=680_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/8-anketell-tuggeranong",
            listing_text="Family home in Tuggeranong on 600m². Government worker rental demand. "
                         "Recession-proof Canberra incomes. Tenanted at $560/wk. "
                         "Vendor public servant posted overseas on DFAT assignment.",
            agent_name="Michael Chen", agent_phone="0423 999 333",
            agency_name="Independent Property Group",
            estimated_weekly_rent=560, council_rates_annual=1_600, water_rates_annual=600,
            distress_signals=[
                DistressSignal(keyword="posted overseas", confidence=0.80, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(), address="LOT 45 John Gorton Drive", suburb="Molonglo Valley",
            state="ACT", postcode="2611", property_type=PropertyType.LAND,
            bedrooms=0, bathrooms=0, car_spaces=0, land_size_sqm=450,
            year_built=None, condition=PropertyCondition.UNKNOWN,
            asking_price=480_000, listing_status=ListingStatus.ACTIVE,
            source=PropertySource.COMING_SOON,
            source_url="https://example.com/listing/lot45-molonglo",
            listing_text="Titled block in Molonglo Valley Stage 3 — Canberra's premium "
                         "growth corridor. 30,000+ residents planned. Build 4BR home for ~$350K. "
                         "Light Rail Stage 2 extension planned through area.",
            agent_name="Karen O'Neill", agent_phone="0434 000 666",
            agency_name="Geocon",
            estimated_weekly_rent=0, council_rates_annual=1_000, water_rates_annual=400,
            distress_signals=[],
            created_at=now - timedelta(days=12),
        ),
    ]

    _inject_images(properties)
    return properties


# ═══════════════════════════════════════════════════════════════════
# SEED DEALS — Pre-analysed with Value-Add Intelligence
# ═══════════════════════════════════════════════════════════════════

def generate_seed_deals(properties: list[Property]) -> list[Deal]:
    """
    Create pre-analysed Deal objects for all seed properties.
    Includes value-add suggestions and deal-closing intelligence.
    Uses algorithmic analysis — no LLM calls required.
    """
    settings = get_settings()
    deals: list[Deal] = []

    # National suburb medians (from locations.py data + market research)
    suburb_medians: dict[str, float] = {
        # VIC
        "Melbourne CBD": 1_100_000, "Carlton": 1_350_000, "Docklands": 880_000,
        "Fitzroy": 1_450_000, "Northcote": 1_300_000, "Preston": 950_000,
        "Brunswick": 1_100_000, "Coburg": 1_000_000,
        "Footscray": 870_000, "Yarraville": 1_100_000, "Newport": 1_000_000,
        "Maidstone": 820_000,
        "Werribee": 560_000, "Sunshine": 720_000, "Tarneit": 580_000,
        "Hawthorn": 2_200_000, "Box Hill": 1_250_000, "Bayswater": 780_000,
        "South Yarra": 1_550_000, "St Kilda": 1_300_000,
        "Dandenong": 600_000, "Berwick": 700_000, "Pakenham": 560_000,
        "Craigieburn": 570_000, "Thomastown": 600_000,
        "Frankston": 720_000, "Mornington": 880_000,
        "Geelong": 690_000, "Norlane": 420_000, "Armstrong Creek": 620_000, "Corio": 460_000,
        "Bendigo": 530_000, "Kangaroo Flat": 430_000, "Eaglehawk": 410_000,
        "Ballarat": 490_000, "Delacombe": 420_000,
        "Traralgon": 380_000, "Warragul": 530_000,
        "Shepparton": 390_000, "Wodonga": 460_000,
        # NSW
        "Sydney CBD": 1_200_000, "Newtown": 1_650_000, "Parramatta": 750_000,
        "Penrith": 820_000, "Newcastle": 720_000,
        # QLD
        "Brisbane CBD": 680_000, "Woolloongabba": 950_000, "Surfers Paradise": 780_000,
        "Logan Central": 550_000, "Ipswich": 480_000,
        # SA
        "Norwood": 1_100_000, "Elizabeth": 420_000, "Osborne": 550_000,
        # WA
        "Subiaco": 1_350_000, "Armadale": 480_000, "Fremantle": 950_000,
        # TAS
        "Hobart CBD": 580_000, "Launceston": 480_000,
        # NT
        "Darwin CBD": 420_000, "Palmerston": 500_000,
        # ACT
        "Braddon": 650_000, "Tuggeranong": 780_000, "Molonglo Valley": 580_000,
    }

    # Per-suburb growth rate (negative = declining market = buyer opportunity)
    suburb_growth: dict[str, float] = {
        # VIC
        "Melbourne CBD": 1.8, "Carlton": 2.2, "Docklands": 2.0,
        "Fitzroy": 2.3, "Northcote": 3.0, "Preston": 4.2,
        "Brunswick": 2.8, "Coburg": 3.5,
        "Footscray": 4.5, "Yarraville": 3.5, "Newport": 3.5,
        "Maidstone": 4.8,
        "Werribee": 5.2, "Sunshine": 4.5, "Tarneit": 5.5,
        "Hawthorn": 1.6, "Box Hill": 2.8, "Bayswater": 4.2,
        "South Yarra": 1.8, "St Kilda": 2.5,
        "Dandenong": 5.0, "Berwick": 4.2, "Pakenham": 5.8,
        "Craigieburn": 5.2, "Thomastown": 5.0,
        "Frankston": 4.5, "Mornington": 3.5,
        "Geelong": 4.2, "Norlane": 6.5, "Armstrong Creek": 5.5, "Corio": 6.0,
        "Bendigo": 4.0, "Kangaroo Flat": 5.0, "Eaglehawk": 5.2,
        "Ballarat": 4.5, "Delacombe": 5.5,
        "Traralgon": 4.0, "Warragul": 4.5,
        "Shepparton": 4.5, "Wodonga": 4.2,
        # NSW
        "Sydney CBD": 2.5, "Newtown": 3.2, "Parramatta": 5.8,
        "Penrith": 7.5, "Newcastle": 6.2,
        # QLD
        "Brisbane CBD": 8.5, "Woolloongabba": 12.0, "Surfers Paradise": 7.8,
        "Logan Central": 10.5, "Ipswich": 9.2,
        # SA
        "Norwood": 8.5, "Elizabeth": 18.0, "Osborne": 14.5,
        # WA
        "Subiaco": 12.5, "Armadale": 22.0, "Fremantle": 15.5,
        # TAS
        "Hobart CBD": 3.5, "Launceston": 4.8,
        # NT
        "Darwin CBD": 2.0, "Palmerston": 3.5,
        # ACT
        "Braddon": 3.8, "Tuggeranong": 3.2, "Molonglo Valley": 6.5,
    }

    for prop in properties:
        price = prop.asking_price or 0
        if price == 0:
            continue

        suburb_median = suburb_medians.get(prop.suburb, price * 1.15)
        weekly_rent = prop.estimated_weekly_rent or prop.current_weekly_rent or 0

        # Skip land lots for deal analysis (no rent)
        if weekly_rent == 0:
            continue

        annual_rent = weekly_rent * 52
        stamp_duty = _stamp_duty(price)

        lvr = settings.default_loan_lvr / 100
        loan_amount = price * lvr
        deposit = price * (1 - lvr)

        is_commercial = prop.property_type.value in ('commercial', 'retail', 'warehouse', 'industrial')

        cf = CashFlowModel(
            purchase_price=price,
            stamp_duty=stamp_duty,
            legal_costs=3_000,
            building_inspection=600,
            pest_inspection=400,
            renovation_cost=50_000 if prop.condition == PropertyCondition.RENOVATION_REQUIRED else 0,
            deposit_pct=100 - settings.default_loan_lvr,
            loan_amount=loan_amount,
            interest_rate_pct=settings.default_interest_rate,
            loan_term_years=30,
            weekly_rent=weekly_rent,
            annual_gross_income=annual_rent,
            property_management_pct=4.0 if is_commercial else 7.0,
            council_rates_annual=prop.council_rates_annual or 1_500,
            water_rates_annual=prop.water_rates_annual or 600,
            strata_annual=(prop.strata_levies_quarterly or 0) * 4,
            insurance_annual=2_500 if is_commercial else 1_500,
            maintenance_annual=1_000 if is_commercial else 2_000,
            vacancy_weeks=4 if is_commercial else 2,
        )

        # BargainScore
        net_yield_val = 0.0
        total_inv = cf.total_investment
        if total_inv > 0:
            net_income = cf.annual_net_income
            net_yield_val = (net_income / total_inv) * 100

        distress_s = prop.distress_score
        days_on_market = (datetime.utcnow() - prop.created_at).days if prop.created_at else 0
        growth = suburb_growth.get(prop.suburb, 2.0)

        bargain = BargainScore.calculate(
            asking_price=price,
            suburb_median=suburb_median,
            net_yield=net_yield_val,
            distress_score=distress_s,
            days_on_market=days_on_market,
            condition_factor=-10 if prop.condition == PropertyCondition.RENOVATION_REQUIRED else 0,
            market_growth_pct=growth,
            golden_threshold=settings.golden_opportunity_score,
        )

        # Strategy recommendation
        is_reno = prop.condition == PropertyCondition.RENOVATION_REQUIRED
        is_large_land = prop.land_size_sqm and prop.land_size_sqm > 500
        is_hmo_candidate = prop.bedrooms and prop.bedrooms >= 4

        strategies: list[DealType] = []
        if is_reno:
            strategies.extend([DealType.FLIP, DealType.BRRR, DealType.BTL])
        elif is_commercial:
            strategies.append(DealType.BTL)
        else:
            strategies.append(DealType.BTL)

        if is_large_land:
            strategies.append(DealType.SUBDIVISION)
        if is_hmo_candidate and not is_commercial:
            strategies.append(DealType.HMO)
        if prop.property_type == PropertyType.DUPLEX:
            strategies.insert(0, DealType.R2SA)
        if prop.property_type in (PropertyType.APARTMENT, PropertyType.UNIT) and price < 700_000:
            strategies.append(DealType.R2SA)

        seen = set()
        strategies = [s for s in strategies if not (s in seen or seen.add(s))]
        primary_strategy = strategies[0]

        # AI-style analysis text
        price_diff_pct = ((suburb_median - price) / suburb_median * 100) if suburb_median > 0 else 0
        gross_yield = (annual_rent / price * 100) if price > 0 else 0

        # Value-add intelligence
        value_add = get_value_add_suggestions(prop)
        value_add_text = ""
        if value_add:
            top = value_add[0]
            value_add_text = (
                f"\n\nVALUE-ADD OPPORTUNITY: {top['label']}\n"
                f"Estimated Cost: ${top['est_cost']:,.0f}\n"
                f"Estimated Value Uplift: ${top['est_value_uplift']:,.0f}\n"
                f"ROI Multiple: {top['roi_ratio']}x\n"
                f"Modifications: {', '.join(top['mods'][:3])}"
            )

        analysis_lines = [
            f"PROPERTY: {prop.address}, {prop.suburb} {prop.state} {prop.postcode}",
            f"ASKING: ${price:,.0f} | MEDIAN: ${suburb_median:,.0f} ({price_diff_pct:+.1f}% vs median)",
            f"GROSS YIELD: {gross_yield:.1f}% | WEEKLY RENT: ${weekly_rent:,.0f}",
            f"STRATEGY: {primary_strategy.value}",
        ]
        if prop.distress_signals:
            signals_txt = ", ".join(d.keyword for d in prop.distress_signals)
            analysis_lines.append(f"DISTRESS SIGNALS: {signals_txt}")
        if bargain.is_golden_opportunity:
            analysis_lines.append("⭐ VERDICT: GOLDEN OPPORTUNITY — strongly consider immediate action.")
        elif bargain.overall_score >= 65:
            analysis_lines.append("✅ VERDICT: Strong deal — worth further investigation.")
        else:
            analysis_lines.append("ℹ️ VERDICT: Fair proposition — proceed with due diligence.")
        if value_add_text:
            analysis_lines.append(value_add_text)

        # Offer range
        offer_low = round(price * 0.88, -3)
        offer_mid = round(price * 0.92, -3)
        offer_high = round(price * 0.96, -3)

        # Refurb cost estimation
        sqm = prop.building_size_sqm or 0
        if prop.condition == PropertyCondition.RENOVATION_REQUIRED:
            refurb_per_sqm = 1_200
            refurb_cost = round(sqm * refurb_per_sqm) if sqm > 0 else round(price * 0.12)
        elif prop.condition == PropertyCondition.FAIR:
            refurb_per_sqm = 600
            refurb_cost = round(sqm * refurb_per_sqm) if sqm > 0 else round(price * 0.06)
        else:
            refurb_cost = 0

        arv = round(price + (refurb_cost * 1.5)) if refurb_cost > 0 else 0
        agent_commission = round(arv * 0.02) if arv > 0 else 0
        flip_profit = round(arv - price - refurb_cost - stamp_duty - 3_000 - agent_commission) if arv > 0 else 0
        brrr_equity = round(arv * 0.80 - loan_amount) if arv > 0 else 0
        brrr_equity = max(brrr_equity, 0)

        deal = Deal(
            id=uuid4(),
            property=prop,
            suburb_median_price=suburb_median,
            deal_type=primary_strategy,
            recommended_strategies=strategies,
            cash_flow=cf,
            bargain_score=bargain,
            ai_analysis="\n".join(analysis_lines),
            comparable_sales_summary=(
                f"Recent median in {prop.suburb}: ${suburb_median:,.0f}. "
                f"This property is {abs(price_diff_pct):.1f}% "
                f"{'below' if price_diff_pct > 0 else 'above'} median."
            ),
            recommended_offer_price=offer_mid,
            offer_range_low=offer_low,
            offer_range_high=offer_high,
            estimated_refurb_cost=refurb_cost,
            after_repair_value=arv,
            flip_profit=flip_profit,
            brrr_equity_gain=brrr_equity,
            created_at=prop.created_at,
        )
        deals.append(deal)

    return deals
