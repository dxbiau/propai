"""
Auto-Scout Engine — Australian Property Associates.

Background task that continuously discovers new properties across
all Australian states every 15-30 minutes.

Since we don't have live scraping endpoints yet, the engine generates
realistic new listings from the deep suburb intelligence database,
simulating what a real scraper would find.  Each run:

  1. Picks 2-5 suburbs that don't already have listings
  2. Generates properties with realistic pricing + distress signals
  3. Auto-analyses each property (deal scoring, value-add)
  4. Persists everything to SQLite
  5. Logs the run in scout_runs table

The background loop is started from main.py lifespan and cancelled
on shutdown.
"""

from __future__ import annotations

import asyncio
import random
import time
from datetime import datetime, timedelta
from uuid import uuid4

import structlog

from nexusprop.models.property import (
    Property,
    PropertyType,
    PropertySource,
    PropertyCondition,
    ListingStatus,
    DistressSignal,
)
from nexusprop.models.deal import Deal
from nexusprop.locations import get_all_suburbs
from nexusprop.config.settings import get_settings
from nexusprop.seed_data import generate_seed_deals, get_value_add_suggestions

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Property generation templates
# ---------------------------------------------------------------------------

_STREET_NAMES = [
    "High Street", "Station Road", "Church Street", "Victoria Street",
    "Albert Road", "King Street", "Bridge Road", "Punt Road",
    "Smith Street", "Sydney Road", "Nicholson Street", "Plenty Road",
    "Nepean Highway", "Canterbury Road", "Bell Street", "Murray Road",
    "Glenferrie Road", "Burke Road", "Toorak Road", "Chapel Street",
    "Lygon Street", "Swanston Street", "Flinders Street", "Collins Street",
    "Elizabeth Street", "Queen Street", "William Street", "La Trobe Street",
    "Spring Street", "Exhibition Street", "Bourke Street", "Little Collins Street",
    "Commercial Road", "Malvern Road", "Dandenong Road", "Princes Highway",
    "Geelong Road", "Ballarat Road", "Calder Freeway", "Western Highway",
    "Sturt Street", "Lydiard Street", "Moorabool Street", "High Street",
    "Midland Highway", "Maroondah Highway", "Whitehorse Road",
    "Warrigal Road", "Springvale Road", "Stud Road",
]

_AGENCY_NAMES = [
    "Jellis Craig", "Marshall White", "Buxton Real Estate",
    "Hocking Stuart", "Barry Plant", "Stockdale & Leggo",
    "Biggin & Scott", "Nelson Alexander", "Woodards",
    "Ray White", "LJ Hooker", "REMAX",
    "First National", "McGrath Estate Agents", "Belle Property",
    "RT Edgar", "Kay & Burton", "Fletchers",
]

_AGENT_FIRST = [
    "James", "Michael", "Sarah", "Emily", "David", "Jessica",
    "Daniel", "Sophie", "Andrew", "Rachel", "Peter", "Lauren",
    "Tom", "Hannah", "Chris", "Olivia", "Mark", "Emma",
    "Ben", "Chloe", "Nick", "Mia", "Tim", "Grace",
]

_AGENT_LAST = [
    "Smith", "Chen", "Williams", "Brown", "Jones", "Nguyen",
    "Taylor", "Wilson", "Anderson", "Thomas", "Lee", "Martin",
    "Thompson", "White", "Harris", "Robinson", "Clark", "Lewis",
]

_DISTRESS_TEMPLATES = [
    ("deceased estate", 0.92, "Executor sale — must settle estate within 90 days."),
    ("must sell", 0.88, "Owner relocating interstate — price reduced for quick sale."),
    ("mortgagee in possession", 0.95, "Bank-ordered sale — priced to sell immediately."),
    ("divorce settlement", 0.90, "Family court orders sale — both parties motivated."),
    ("overseas relocation", 0.85, "Visa expiry forcing sale — hasn't visited in 2+ years."),
    ("strata arrears", 0.80, "Owner in strata arrears — body corp forcing sale."),
    ("fire damage", 0.75, "Partial fire damage — needs reno but structurally sound."),
    ("council non-compliance", 0.70, "Council orders outstanding — seller wants out."),
    ("tax debt", 0.82, "ATO debt — forced liquidation of investment property."),
    ("business failure", 0.78, "Failed business — investment property being sold to cover debts."),
]

_LISTING_TEMPLATES = [
    "Located in the heart of {suburb}, this {type} offers exceptional value. {distress_text} "
    "Close to transport, schools, and shopping. Currently tenanted at ${rent}/week.",

    "Rare opportunity in {suburb}! This {beds}BR {type} on {land}sqm is priced to sell. "
    "{distress_text} Strong rental demand in the area. {infra_text}",

    "Investment-grade {type} in {suburb} {state} {postcode}. {distress_text} "
    "Walking distance to train station and local amenities. "
    "Current yield {yield_pct}%. Don't miss this one.",

    "Motivated seller in {suburb} — this {beds}BR {type} sits on {land}sqm of prime land. "
    "{distress_text} Potential for {value_add}. {infra_text}",

    "Price guide ${price_low}-${price_high}. {type} in sought-after {suburb}. "
    "{distress_text} {beds} bedrooms, {baths} bathroom(s). "
    "Auction this Saturday unless sold prior.",
]


# ---------------------------------------------------------------------------
# Auto-scout core: generate new properties from suburb intelligence
# ---------------------------------------------------------------------------

def _generate_scout_properties(
    existing_suburbs: set[str],
    max_new: int = 5,
) -> list[Property]:
    """
    Generate realistic new property listings from Australian suburbs that
    don't already have listings in the store.

    Returns up to *max_new* new Property objects.
    """
    all_suburbs = get_all_suburbs()
    if not all_suburbs:
        return []

    # Weight suburbs that don't already have listings
    candidates = [s for s in all_suburbs if s["name"] not in existing_suburbs]
    if not candidates:
        candidates = all_suburbs  # all suburbs covered — recycle with new addresses

    random.shuffle(candidates)
    selected = candidates[:max_new]

    now = datetime.utcnow()
    properties: list[Property] = []

    for sub_data in selected:
        suburb_name = sub_data["name"]
        postcode = sub_data.get("postcode", "3000")
        median = sub_data.get("median", 850_000)
        median_unit = sub_data.get("median_unit")
        rent_yield = sub_data.get("yield", 4.0)
        infrastructure = sub_data.get("infrastructure")
        region = sub_data.get("region", "CBD & Inner City")
        gentrification = sub_data.get("gentrification", "established")

        # Random property type weighted by suburb characteristics
        is_inner = median > 1_000_000
        if is_inner:
            ptype = random.choice([
                PropertyType.APARTMENT, PropertyType.APARTMENT,
                PropertyType.TOWNHOUSE, PropertyType.HOUSE,
                PropertyType.UNIT,
            ])
        else:
            ptype = random.choice([
                PropertyType.HOUSE, PropertyType.HOUSE, PropertyType.HOUSE,
                PropertyType.TOWNHOUSE, PropertyType.UNIT,
                PropertyType.LAND,
            ])

        # Price variation around median
        if ptype in (PropertyType.APARTMENT, PropertyType.UNIT):
            base_price = median_unit or int(median * 0.55)
        else:
            base_price = median

        discount = random.uniform(0.08, 0.22)  # 8-22% below median
        price = round(base_price * (1 - discount), -3)

        # Condition
        condition_roll = random.random()
        if condition_roll < 0.25:
            condition = PropertyCondition.RENOVATION_REQUIRED
        elif condition_roll < 0.45:
            condition = PropertyCondition.FAIR
        else:
            condition = PropertyCondition.GOOD

        # Beds/baths/land
        if ptype == PropertyType.HOUSE:
            beds = random.choice([2, 3, 3, 3, 4, 4, 5])
            baths = min(beds, random.choice([1, 1, 2, 2, 3]))
            land = random.choice([350, 400, 450, 500, 550, 600, 650, 700, 800])
            building = int(land * random.uniform(0.35, 0.55))
            year = random.randint(1920, 2015)
        elif ptype == PropertyType.TOWNHOUSE:
            beds = random.choice([2, 3, 3, 4])
            baths = random.choice([1, 2, 2])
            land = random.choice([150, 180, 200, 250, 300])
            building = int(land * random.uniform(0.5, 0.7))
            year = random.randint(1990, 2022)
        elif ptype in (PropertyType.APARTMENT, PropertyType.UNIT):
            beds = random.choice([1, 1, 2, 2, 3])
            baths = min(beds, random.choice([1, 1, 2]))
            land = None
            building = random.choice([45, 55, 65, 75, 85, 100])
            year = random.randint(2000, 2023)
        elif ptype == PropertyType.LAND:
            beds = 0
            baths = 0
            land = random.choice([400, 450, 500, 600, 700, 800, 1000])
            building = None
            year = None
            condition = PropertyCondition.UNKNOWN
        else:
            beds = random.choice([2, 3, 4])
            baths = random.choice([1, 2])
            land = random.choice([300, 400, 500])
            building = int(land * 0.45)
            year = random.randint(1970, 2020)

        # Distress signals (60% chance)
        distress_signals = []
        if random.random() < 0.60:
            n_signals = random.randint(1, 2)
            chosen = random.sample(_DISTRESS_TEMPLATES, min(n_signals, len(_DISTRESS_TEMPLATES)))
            for keyword, confidence, _ in chosen:
                distress_signals.append(
                    DistressSignal(keyword=keyword, confidence=confidence, source="listing_text")
                )

        # Rent estimate
        weekly_rent = 0
        if ptype != PropertyType.LAND:
            weekly_rent = round(price * (rent_yield / 100) / 52, -1)
            weekly_rent = max(weekly_rent, 280)

        # Address
        street_num = random.randint(1, 200)
        if ptype in (PropertyType.APARTMENT, PropertyType.UNIT):
            unit = random.randint(1, 30)
            address = f"{unit}/{street_num} {random.choice(_STREET_NAMES)}"
        else:
            address = f"{street_num} {random.choice(_STREET_NAMES)}"

        # Source — weight towards shadow/off-market (our edge)
        source = random.choice([
            PropertySource.BOUTIQUE_AGENCY,
            PropertySource.BOUTIQUE_AGENCY,
            PropertySource.OFF_MARKET,
            PropertySource.OFF_MARKET,
            PropertySource.COMING_SOON,
            PropertySource.COUNCIL_DA,
            PropertySource.PUBLIC_NOTICE,
        ])

        # Listing text
        distress_text = ""
        if distress_signals:
            tmpl = random.choice(_DISTRESS_TEMPLATES)
            distress_text = tmpl[2]

        infra_text = f"Major project: {infrastructure}." if infrastructure else ""
        value_add_opts = ["granny flat STCA", "subdivision STCA", "second storey STCA",
                          "cosmetic reno and re-lease", "Airbnb conversion"]

        listing_text = random.choice(_LISTING_TEMPLATES).format(
            suburb=suburb_name,
            type=ptype.value,
            beds=beds,
            baths=baths,
            land=land or 0,
            rent=weekly_rent,
            postcode=postcode,
            state=sub_data.get("state", "VIC"),
            yield_pct=round(rent_yield, 1),
            distress_text=distress_text,
            infra_text=infra_text,
            value_add=random.choice(value_add_opts),
            price_low=f"{price * 0.95:,.0f}",
            price_high=f"{price * 1.02:,.0f}",
        )

        # Agent
        agent_first = random.choice(_AGENT_FIRST)
        agent_last = random.choice(_AGENT_LAST)
        agency = random.choice(_AGENCY_NAMES)

        # Image injection happens post-creation via seed_data._inject_images
        prop = Property(
            id=uuid4(),
            address=address,
            suburb=suburb_name,
            state=sub_data.get("state", "VIC"),
            postcode=postcode,
            property_type=ptype,
            bedrooms=beds,
            bathrooms=baths,
            car_spaces=random.choice([0, 1, 1, 2]) if ptype != PropertyType.LAND else 0,
            land_size_sqm=land,
            building_size_sqm=building,
            year_built=year,
            condition=condition,
            asking_price=price,
            listing_status=ListingStatus.ACTIVE,
            source=source,
            source_url=f"https://www.domain.com.au/sale/{suburb_name.lower().replace(' ', '-')}-{sub_data.get('state', 'vic').lower()}-{postcode}/",
            listing_text=listing_text,
            agent_name=f"{agent_first} {agent_last}",
            agent_phone=f"04{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}",
            agency_name=agency,
            estimated_weekly_rent=weekly_rent if weekly_rent > 0 else None,
            council_rates_annual=random.choice([900, 1200, 1500, 1800, 2000]),
            water_rates_annual=random.choice([400, 500, 600, 700]),
            strata_levies_quarterly=(
                random.choice([800, 1200, 1600, 2000])
                if ptype in (PropertyType.APARTMENT, PropertyType.UNIT, PropertyType.TOWNHOUSE)
                else None
            ),
            distress_signals=distress_signals,
            created_at=now - timedelta(hours=random.randint(1, 48)),
        )
        properties.append(prop)

    # Fix source URLs to real Domain.com.au search pages (no fake images)
    from nexusprop.seed_data import _inject_images
    _inject_images(properties)

    return properties


# ---------------------------------------------------------------------------
# Background task loop
# ---------------------------------------------------------------------------

async def auto_scout_loop(
    property_store: dict,
    deal_store: dict,
    interval_minutes: int = 30,
) -> None:
    """
    Long-running background coroutine that discovers new properties
    every *interval_minutes*.

    Runs indefinitely until cancelled.  Each cycle:
      1. Generate 2-5 new properties
      2. Generate Deal objects for them
      3. Add to the in-memory stores
      4. Persist to SQLite
      5. Log the scout run
    """
    from nexusprop.db import (
        save_properties_bulk,
        save_deals_bulk,
        log_scout_run,
    )

    logger.info(
        "auto_scout_started",
        interval_minutes=interval_minutes,
    )

    # Wait a short period on first start to let the app fully boot
    await asyncio.sleep(10)

    while True:
        try:
            t0 = time.time()

            # Determine existing suburbs in our store
            existing_suburbs = set()
            for prop in property_store.values():
                if prop.suburb:
                    existing_suburbs.add(prop.suburb)

            # Generate new properties
            n_new = random.randint(2, 5)
            new_props = _generate_scout_properties(existing_suburbs, max_new=n_new)

            if new_props:
                # Add to in-memory store
                for prop in new_props:
                    property_store[str(prop.id)] = prop

                # Generate deals for new properties
                new_deals = generate_seed_deals(new_props)
                for deal in new_deals:
                    deal_store[str(deal.id)] = deal

                # Persist to DB
                save_properties_bulk(new_props)
                save_deals_bulk(new_deals)

                duration_ms = int((time.time() - t0) * 1000)

                # Log the run
                suburbs_found = [p.suburb for p in new_props]
                log_scout_run(
                    new_props=len(new_props),
                    new_deals=len(new_deals),
                    duration_ms=duration_ms,
                    notes=f"Suburbs: {', '.join(suburbs_found)}",
                )

                logger.info(
                    "auto_scout_cycle_complete",
                    new_properties=len(new_props),
                    new_deals=len(new_deals),
                    suburbs=suburbs_found,
                    duration_ms=duration_ms,
                    total_properties=len(property_store),
                    total_deals=len(deal_store),
                )
            else:
                logger.info("auto_scout_cycle_no_new")

        except asyncio.CancelledError:
            logger.info("auto_scout_cancelled")
            raise
        except Exception as e:
            logger.error("auto_scout_error", error=str(e))

        # Sleep until next cycle
        await asyncio.sleep(interval_minutes * 60)
