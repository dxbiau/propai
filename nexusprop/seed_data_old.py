"""
Seed data for Property Insights Australia.

Realistic Australian property listings and pre-analysed deals, so the
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


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
_now = datetime.utcnow


def _stamp_duty(price: float) -> float:
    return get_settings().calculate_stamp_duty(price)


# ---------------------------------------------------------------------------
# Seed Properties
# ---------------------------------------------------------------------------

def generate_seed_properties() -> list[Property]:
    """Return ~20 realistic Australian property listings."""
    now = _now()
    return [
        # ── NSW ──────────────────────────────────────────────────────
        Property(
            id=uuid4(),
            address="42 Gladstone Avenue",
            suburb="Marrickville",
            state="NSW",
            postcode="2204",
            property_type=PropertyType.HOUSE,
            bedrooms=3,
            bathrooms=1,
            car_spaces=1,
            land_size_sqm=420,
            building_size_sqm=140,
            year_built=1925,
            condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=1_150_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://raywhite.com/marrickville/listing-42-gladstone",
            listing_text="Original condition worker's cottage in prime Inner West location. "
                         "Deceased estate — executor says MUST SELL. DA approved two-storey "
                         "addition. Walk to Marrickville Metro station. R2 zoning with "
                         "potential for granny flat STCA.",
            agent_name="Sarah Chen",
            agent_phone="0412 345 678",
            agency_name="Ray White Marrickville",
            estimated_weekly_rent=650,
            council_rates_annual=1_800,
            water_rates_annual=700,
            zoning="R2",
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="must sell", confidence=0.88, source="listing_text"),
                DistressSignal(keyword="DA approved", confidence=0.70, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(),
            address="7/18 Campbell Street",
            suburb="Parramatta",
            state="NSW",
            postcode="2150",
            property_type=PropertyType.UNIT,
            bedrooms=2,
            bathrooms=1,
            car_spaces=1,
            land_size_sqm=None,
            building_size_sqm=78,
            year_built=2005,
            condition=PropertyCondition.GOOD,
            asking_price=520_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/7-18-campbell",
            listing_text="Modern unit in the heart of Parramatta. Vendor relocating — "
                         "priced to sell quickly. Walking distance to Westfield and train.",
            agent_name="James Patel",
            agent_phone="0423 456 789",
            agency_name="LJ Hooker Parramatta",
            estimated_weekly_rent=480,
            strata_levies_quarterly=1_200,
            council_rates_annual=900,
            water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.85, source="listing_text"),
                DistressSignal(keyword="priced to sell", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(),
            address="155 Hume Highway",
            suburb="Bankstown",
            state="NSW",
            postcode="2200",
            property_type=PropertyType.HOUSE,
            bedrooms=4,
            bathrooms=2,
            car_spaces=2,
            land_size_sqm=650,
            building_size_sqm=180,
            year_built=1975,
            condition=PropertyCondition.FAIR,
            asking_price=1_050_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/155-hume",
            listing_text="Solid brick home on generous block. Development potential "
                         "STCA — R3 medium density zoning. Dual street access. "
                         "All offers considered by mortgagee.",
            agent_name="Michael Nguyen",
            agent_phone="0434 567 890",
            agency_name="Century 21 Bankstown",
            estimated_weekly_rent=680,
            council_rates_annual=1_600,
            water_rates_annual=650,
            zoning="R3",
            distress_signals=[
                DistressSignal(keyword="mortgagee", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="all offers considered", confidence=0.80, source="listing_text"),
                DistressSignal(keyword="development potential", confidence=0.70, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),
        Property(
            id=uuid4(),
            address="3/24 Ocean Street",
            suburb="Bondi",
            state="NSW",
            postcode="2026",
            property_type=PropertyType.APARTMENT,
            bedrooms=1,
            bathrooms=1,
            car_spaces=0,
            building_size_sqm=52,
            year_built=1965,
            condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=780_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/3-24-ocean",
            listing_text="Art deco apartment 200m from Bondi Beach. Needs cosmetic "
                         "renovation. Divorce settlement — vendor says sell THIS WEEK. "
                         "Currently tenanted at $580/week.",
            agent_name="Lisa Wong",
            agent_phone="0445 678 901",
            agency_name="McGrath Bondi",
            estimated_weekly_rent=580,
            current_weekly_rent=580,
            strata_levies_quarterly=1_800,
            council_rates_annual=1_200,
            water_rates_annual=550,
            distress_signals=[
                DistressSignal(keyword="divorce", confidence=0.92, source="listing_text"),
                DistressSignal(keyword="urgent sale", confidence=0.90, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),
        Property(
            id=uuid4(),
            address="88 Victoria Road",
            suburb="Gladesville",
            state="NSW",
            postcode="2111",
            property_type=PropertyType.HOUSE,
            bedrooms=5,
            bathrooms=3,
            car_spaces=2,
            land_size_sqm=720,
            building_size_sqm=280,
            year_built=2010,
            condition=PropertyCondition.EXCELLENT,
            asking_price=2_350_000,
            listing_status=ListingStatus.AUCTION,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/88-victoria",
            listing_text="Prestige family home with harbour glimpses. Resort-style "
                         "pool and landscaped gardens. Vendor downsizing — already "
                         "purchased elsewhere. Must sell before settlement.",
            agent_name="Tom Richards",
            agent_phone="0456 789 012",
            agency_name="Belle Property Hunters Hill",
            estimated_weekly_rent=1_400,
            council_rates_annual=3_200,
            water_rates_annual=900,
            zoning="R2",
            distress_signals=[
                DistressSignal(keyword="downsizing", confidence=0.80, source="listing_text"),
                DistressSignal(keyword="must sell", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=7),
        ),

        # ── VIC ──────────────────────────────────────────────────────
        Property(
            id=uuid4(),
            address="12 Smith Street",
            suburb="Footscray",
            state="VIC",
            postcode="3011",
            property_type=PropertyType.HOUSE,
            bedrooms=3,
            bathrooms=1,
            car_spaces=1,
            land_size_sqm=350,
            building_size_sqm=110,
            year_built=1920,
            condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=780_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/12-smith-footscray",
            listing_text="Character Victorian on generous corner block. Renovator's "
                         "delight in rapidly gentrifying area. 800m to Footscray station "
                         "and shopping. Vendor has relocated to QLD.",
            agent_name="Daniel Kosic",
            agent_phone="0402 111 222",
            agency_name="Jellis Craig Footscray",
            estimated_weekly_rent=520,
            council_rates_annual=1_400,
            water_rates_annual=600,
            zoning="NRZ1",
            distress_signals=[
                DistressSignal(keyword="renovator's delight", confidence=0.75, source="listing_text"),
                DistressSignal(keyword="relocating", confidence=0.82, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(),
            address="5/310 St Kilda Road",
            suburb="Southbank",
            state="VIC",
            postcode="3006",
            property_type=PropertyType.APARTMENT,
            bedrooms=2,
            bathrooms=2,
            car_spaces=1,
            building_size_sqm=85,
            year_built=2018,
            condition=PropertyCondition.EXCELLENT,
            asking_price=620_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/5-310-stkilda",
            listing_text="Stunning city views from level 22. Premium building with pool, "
                         "gym, concierge. Foreign investor liquidation — below purchase "
                         "price. Currently tenanted at $600/week.",
            agent_name="Emily Zhang",
            agent_phone="0413 222 333",
            agency_name="Marshall White Southbank",
            estimated_weekly_rent=600,
            current_weekly_rent=600,
            strata_levies_quarterly=2_100,
            council_rates_annual=1_100,
            water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="liquidation", confidence=0.90, source="listing_text"),
                DistressSignal(keyword="below market", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),
        Property(
            id=uuid4(),
            address="27 Burke Road",
            suburb="Glen Iris",
            state="VIC",
            postcode="3146",
            property_type=PropertyType.HOUSE,
            bedrooms=4,
            bathrooms=2,
            car_spaces=2,
            land_size_sqm=580,
            building_size_sqm=220,
            year_built=1960,
            condition=PropertyCondition.FAIR,
            asking_price=1_680_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/27-burke-gleniris",
            listing_text="Substantial mid-century home in blue-chip Glen Iris. "
                         "Walk to Glen Iris station and Gardiner's Creek trail. "
                         "Price slashed $120K — vendor committed elsewhere.",
            agent_name="Andrew Palmer",
            agent_phone="0424 333 444",
            agency_name="Kay & Burton Glen Iris",
            estimated_weekly_rent=900,
            council_rates_annual=2_400,
            water_rates_annual=750,
            zoning="NRZ1",
            distress_signals=[
                DistressSignal(keyword="price slashed", confidence=0.90, source="listing_text"),
            ],
            created_at=now - timedelta(days=8),
        ),
        Property(
            id=uuid4(),
            address="14 Albert Street",
            suburb="Brunswick",
            state="VIC",
            postcode="3056",
            property_type=PropertyType.TOWNHOUSE,
            bedrooms=3,
            bathrooms=2,
            car_spaces=1,
            land_size_sqm=200,
            building_size_sqm=150,
            year_built=2015,
            condition=PropertyCondition.GOOD,
            asking_price=920_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/14-albert-brunswick",
            listing_text="Low-maintenance townhouse in vibrant Brunswick. "
                         "Minutes from Sydney Road cafes and trams. Vendor says sell — "
                         "all reasonable offers presented.",
            agent_name="Sophie Tran",
            agent_phone="0435 444 555",
            agency_name="Nelson Alexander Brunswick",
            estimated_weekly_rent=620,
            strata_levies_quarterly=600,
            council_rates_annual=1_300,
            water_rates_annual=550,
            distress_signals=[
                DistressSignal(keyword="vendor says sell", confidence=0.82, source="listing_text"),
                DistressSignal(keyword="all offers considered", confidence=0.78, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),

        # ── VIC — Bendigo / Regional ────────────────────────────────
        Property(
            id=uuid4(),
            address="88 High Street",
            suburb="Bendigo",
            state="VIC",
            postcode="3550",
            property_type=PropertyType.HOUSE,
            bedrooms=4,
            bathrooms=2,
            car_spaces=2,
            land_size_sqm=680,
            building_size_sqm=180,
            year_built=1945,
            condition=PropertyCondition.FAIR,
            asking_price=485_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/88-high-bendigo",
            listing_text="Spacious period home on generous block in central Bendigo. "
                         "Character features throughout — high ceilings, timber floors. "
                         "Vendor relocating interstate, motivated to sell. Walk to "
                         "Bendigo Marketplace and train station.",
            agent_name="Mark Thompson",
            agent_phone="0418 555 111",
            agency_name="PRD Bendigo",
            estimated_weekly_rent=420,
            council_rates_annual=1_600,
            water_rates_annual=550,
            zoning="NRZ1",
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.85, source="listing_text"),
                DistressSignal(keyword="motivated to sell", confidence=0.80, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),
        Property(
            id=uuid4(),
            address="15 Quarry Hill Road",
            suburb="Quarry Hill",
            state="VIC",
            postcode="3550",
            property_type=PropertyType.TOWNHOUSE,
            bedrooms=3,
            bathrooms=2,
            car_spaces=1,
            land_size_sqm=250,
            building_size_sqm=145,
            year_built=2019,
            condition=PropertyCondition.GOOD,
            asking_price=395_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/15-quarryhill",
            listing_text="Modern low-maintenance townhouse in quiet Quarry Hill. "
                         "Open plan living, double glazing, split systems. Currently "
                         "tenanted at $380/wk — solid yield. Owner downsizing.",
            agent_name="Lisa O'Connell",
            agent_phone="0421 666 222",
            agency_name="Ray White Bendigo",
            estimated_weekly_rent=380,
            current_weekly_rent=380,
            strata_levies_quarterly=450,
            council_rates_annual=1_200,
            water_rates_annual=480,
            distress_signals=[
                DistressSignal(keyword="downsizing", confidence=0.65, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(),
            address="220 Midland Highway",
            suburb="Epsom",
            state="VIC",
            postcode="3551",
            property_type=PropertyType.COMMERCIAL,
            bedrooms=0,
            bathrooms=2,
            car_spaces=8,
            land_size_sqm=1200,
            building_size_sqm=350,
            year_built=1995,
            condition=PropertyCondition.FAIR,
            asking_price=620_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/220-midland-epsom",
            listing_text="Commercial warehouse/retail on busy Midland Highway corridor. "
                         "Currently leased to hardware supplier at $650/wk — long-term "
                         "tenant. Zoned C1Z. Perfect passive income. Bank forced sale — "
                         "mortgagee in possession.",
            agent_name="Peter Robertson",
            agent_phone="0408 777 333",
            agency_name="Colliers Bendigo",
            estimated_weekly_rent=650,
            current_weekly_rent=650,
            council_rates_annual=3_200,
            water_rates_annual=800,
            zoning="C1Z",
            distress_signals=[
                DistressSignal(keyword="mortgagee in possession", confidence=0.98, source="listing_text"),
                DistressSignal(keyword="bank forced sale", confidence=0.95, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),
        Property(
            id=uuid4(),
            address="Lot 5, McIvor Road",
            suburb="Junortoun",
            state="VIC",
            postcode="3551",
            property_type=PropertyType.ACREAGE,
            bedrooms=5,
            bathrooms=3,
            car_spaces=4,
            land_size_sqm=40_500,  # 10 acres
            building_size_sqm=280,
            year_built=1985,
            condition=PropertyCondition.GOOD,
            asking_price=890_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/lot5-mcivor-junortoun",
            listing_text="Stunning 10-acre lifestyle property just 15 min from Bendigo CBD. "
                         "5BR homestead with in-ground pool, large shed, dam, bore water. "
                         "Fenced paddocks — ideal for horses or hobby farm. Deceased estate, "
                         "family wants quick settlement.",
            agent_name="Rachel Gunn",
            agent_phone="0419 888 444",
            agency_name="Tweed Sutherland First National Bendigo",
            estimated_weekly_rent=680,
            council_rates_annual=2_800,
            water_rates_annual=300,
            zoning="FZ",
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="quick settlement", confidence=0.82, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(),
            address="145 Calder Highway",
            suburb="Kangaroo Flat",
            state="VIC",
            postcode="3555",
            property_type=PropertyType.FARM,
            bedrooms=3,
            bathrooms=1,
            car_spaces=2,
            land_size_sqm=162_000,  # 40 acres
            building_size_sqm=120,
            year_built=1970,
            condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=575_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/145-calder-kflat",
            listing_text="40-acre working farm on Bendigo's outskirts. 3BR weatherboard "
                         "farmhouse needs TLC. Large machinery shed, cattle yards, 2 dams. "
                         "Zoned Farming. Owner retiring — rare affordable entry into "
                         "Goldfields region farming.",
            agent_name="Steve Barker",
            agent_phone="0412 999 555",
            agency_name="Elders Bendigo",
            estimated_weekly_rent=400,
            council_rates_annual=1_800,
            water_rates_annual=250,
            zoning="FZ",
            distress_signals=[
                DistressSignal(keyword="retiring", confidence=0.72, source="listing_text"),
                DistressSignal(keyword="renovation required", confidence=0.80, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(),
            address="3/56 Mitchell Street",
            suburb="Bendigo",
            state="VIC",
            postcode="3550",
            property_type=PropertyType.RETAIL,
            bedrooms=0,
            bathrooms=1,
            car_spaces=2,
            land_size_sqm=None,
            building_size_sqm=95,
            year_built=2008,
            condition=PropertyCondition.GOOD,
            asking_price=310_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/3-56-mitchell-bendigo",
            listing_text="Ground-floor retail shop in Bendigo CBD. Currently vacant — "
                         "previous tenant (café) surrendered lease. High foot traffic "
                         "location near Bendigo Art Gallery. Strata titled. Ideal "
                         "investment or owner-occupier.",
            agent_name="Mark Thompson",
            agent_phone="0418 555 111",
            agency_name="PRD Bendigo",
            estimated_weekly_rent=450,
            strata_levies_quarterly=1_800,
            council_rates_annual=2_100,
            water_rates_annual=400,
            zoning="C1Z",
            distress_signals=[
                DistressSignal(keyword="vacant", confidence=0.70, source="listing_text"),
                DistressSignal(keyword="surrendered lease", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),

        # ── QLD ──────────────────────────────────────────────────────
        Property(
            id=uuid4(),
            address="18 Boundary Street",
            suburb="West End",
            state="QLD",
            postcode="4101",
            property_type=PropertyType.HOUSE,
            bedrooms=3,
            bathrooms=2,
            car_spaces=1,
            land_size_sqm=405,
            building_size_sqm=130,
            year_built=1930,
            condition=PropertyCondition.FAIR,
            asking_price=890_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/18-boundary-westend",
            listing_text="Classic Queenslander on elevated block with city views. "
                         "Character timber home — needs cosmetic update. Deceased estate "
                         "sale. Walk to Davies Park markets and South Bank.",
            agent_name="Chris Morgan",
            agent_phone="0446 555 666",
            agency_name="Place West End",
            estimated_weekly_rent=620,
            council_rates_annual=1_500,
            water_rates_annual=550,
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="needs work", confidence=0.70, source="listing_text"),
            ],
            created_at=now - timedelta(days=3),
        ),
        Property(
            id=uuid4(),
            address="22/45 Wharf Street",
            suburb="Brisbane City",
            state="QLD",
            postcode="4000",
            property_type=PropertyType.APARTMENT,
            bedrooms=1,
            bathrooms=1,
            car_spaces=1,
            building_size_sqm=55,
            year_built=2016,
            condition=PropertyCondition.GOOD,
            asking_price=385_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/22-45-wharf",
            listing_text="River views from Level 18. Fully furnished investment unit. "
                         "Rental guarantee ending — owner can't hold. Moving overseas, "
                         "priced for immediate sale.",
            agent_name="Kate O'Brien",
            agent_phone="0457 666 777",
            agency_name="Harcourts Brisbane",
            estimated_weekly_rent=420,
            current_weekly_rent=420,
            strata_levies_quarterly=1_400,
            council_rates_annual=800,
            water_rates_annual=400,
            distress_signals=[
                DistressSignal(keyword="moving overseas", confidence=0.88, source="listing_text"),
                DistressSignal(keyword="priced to sell", confidence=0.82, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),
        Property(
            id=uuid4(),
            address="6 Palm Avenue",
            suburb="Surfers Paradise",
            state="QLD",
            postcode="4217",
            property_type=PropertyType.UNIT,
            bedrooms=2,
            bathrooms=2,
            car_spaces=1,
            building_size_sqm=90,
            year_built=2012,
            condition=PropertyCondition.GOOD,
            asking_price=540_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/6-palm-surfers",
            listing_text="Ocean views from both bedrooms. Holiday let potential with "
                         "short-stay approval. Fire sale by developer clearing last stock. "
                         "Body corp includes pool, gym, BBQ area.",
            agent_name="Ryan Marshall",
            agent_phone="0468 777 888",
            agency_name="Kollosche Gold Coast",
            estimated_weekly_rent=550,
            current_weekly_rent=None,
            strata_levies_quarterly=1_600,
            council_rates_annual=1_000,
            water_rates_annual=450,
            distress_signals=[
                DistressSignal(keyword="fire sale", confidence=0.92, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(),
            address="33 Station Road",
            suburb="Indooroopilly",
            state="QLD",
            postcode="4068",
            property_type=PropertyType.HOUSE,
            bedrooms=4,
            bathrooms=2,
            car_spaces=2,
            land_size_sqm=810,
            building_size_sqm=210,
            year_built=1985,
            condition=PropertyCondition.GOOD,
            asking_price=1_120_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/33-station-indro",
            listing_text="Spacious family home in sought-after school catchment. Pool, "
                         "side access, room for boat. Motivated seller — relocating for "
                         "work. Bring all offers.",
            agent_name="Mark Jensen",
            agent_phone="0479 888 999",
            agency_name="Ray White Indooroopilly",
            estimated_weekly_rent=720,
            council_rates_annual=1_800,
            water_rates_annual=650,
            zoning="LDR",
            distress_signals=[
                DistressSignal(keyword="motivated seller", confidence=0.85, source="listing_text"),
                DistressSignal(keyword="bring all offers", confidence=0.80, source="listing_text"),
            ],
            created_at=now - timedelta(days=6),
        ),

        # ── SA ───────────────────────────────────────────────────────
        Property(
            id=uuid4(),
            address="9 Henley Beach Road",
            suburb="Mile End",
            state="SA",
            postcode="5031",
            property_type=PropertyType.HOUSE,
            bedrooms=3,
            bathrooms=1,
            car_spaces=2,
            land_size_sqm=450,
            building_size_sqm=120,
            year_built=1910,
            condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=580_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/9-henley-mileend",
            listing_text="Charming character home needing full renovation. Bluestone "
                         "frontage. Close to Adelaide CBD, tram, and Thebarton Oval. "
                         "Handyman special — vendor in aged care, family selling.",
            agent_name="Paul Harris",
            agent_phone="0408 111 333",
            agency_name="Ouwens Casserly Mile End",
            estimated_weekly_rent=450,
            council_rates_annual=1_200,
            water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="handyman special", confidence=0.78, source="listing_text"),
            ],
            created_at=now - timedelta(days=9),
        ),

        # ── WA ───────────────────────────────────────────────────────
        Property(
            id=uuid4(),
            address="44 Stirling Highway",
            suburb="Nedlands",
            state="WA",
            postcode="6009",
            property_type=PropertyType.HOUSE,
            bedrooms=4,
            bathrooms=2,
            car_spaces=2,
            land_size_sqm=680,
            building_size_sqm=200,
            year_built=1955,
            condition=PropertyCondition.FAIR,
            asking_price=1_280_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/44-stirling-nedlands",
            listing_text="Prime river precinct location near UWA. Original condition "
                         "with enormous potential. Subdivision potential STCA R30 zoning. "
                         "Deceased estate — expressions of interest closing Friday.",
            agent_name="Rebecca Stone",
            agent_phone="0419 444 666",
            agency_name="Acton Dalkeith",
            estimated_weekly_rent=750,
            council_rates_annual=2_100,
            water_rates_annual=700,
            zoning="R30",
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="potential subdivision", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=10),
        ),

        # ── TAS ──────────────────────────────────────────────────────
        Property(
            id=uuid4(),
            address="28 Sandy Bay Road",
            suburb="Sandy Bay",
            state="TAS",
            postcode="7005",
            property_type=PropertyType.HOUSE,
            bedrooms=3,
            bathrooms=2,
            car_spaces=2,
            land_size_sqm=650,
            building_size_sqm=160,
            year_built=1935,
            condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=685_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/28-sandybay",
            listing_text="Character home in prestigious Sandy Bay. Needs full renovation "
                         "but solid bones. Walking distance to UTAS and Sandy Bay village. "
                         "Vendor relocating overseas — must sell before March. Elevated "
                         "position with glimpses of the Derwent River.",
            agent_name="Tom Brasher",
            agent_phone="0418 222 333",
            agency_name="Fall Real Estate",
            estimated_weekly_rent=520,
            council_rates_annual=1_600,
            water_rates_annual=550,
            zoning="General Residential",
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.85, source="listing_text"),
                DistressSignal(keyword="must sell", confidence=0.90, source="listing_text"),
            ],
            created_at=now - timedelta(days=5),
        ),
        Property(
            id=uuid4(),
            address="5/12 Elizabeth Street",
            suburb="Launceston",
            state="TAS",
            postcode="7250",
            property_type=PropertyType.UNIT,
            bedrooms=2,
            bathrooms=1,
            car_spaces=1,
            land_size_sqm=None,
            building_size_sqm=85,
            year_built=2010,
            condition=PropertyCondition.GOOD,
            asking_price=345_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.REA,
            source_url="https://example.com/listing/5-12-elizabeth-launceston",
            listing_text="Modern low-maintenance unit in the heart of Launceston. "
                         "Currently tenanted at $390/week — excellent yield. Body corp "
                         "well managed, low levies. Walk to CBD, Cataract Gorge nearby. "
                         "Investor selling — priced to sell quickly.",
            agent_name="Sarah Kingston",
            agent_phone="0407 111 444",
            agency_name="Harcourts Launceston",
            estimated_weekly_rent=390,
            strata_levies_quarterly=450,
            council_rates_annual=1_100,
            water_rates_annual=450,
            current_weekly_rent=390,
            distress_signals=[
                DistressSignal(keyword="priced to sell", confidence=0.82, source="listing_text"),
            ],
            created_at=now - timedelta(days=7),
        ),
        Property(
            id=uuid4(),
            address="156 Main Road",
            suburb="Moonah",
            state="TAS",
            postcode="7009",
            property_type=PropertyType.HOUSE,
            bedrooms=4,
            bathrooms=1,
            car_spaces=2,
            land_size_sqm=800,
            building_size_sqm=130,
            year_built=1960,
            condition=PropertyCondition.FAIR,
            asking_price=475_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/156-main-moonah",
            listing_text="Massive 800sqm block in fast-growing Moonah. 4-bed weatherboard "
                         "home, solid but dated. Zoning allows for dual occupancy STCA. "
                         "Deceased estate — all offers considered. Walking to Moonah "
                         "shopping precinct. 10 mins to Hobart CBD. Development potential.",
            agent_name="James Crawford",
            agent_phone="0412 888 999",
            agency_name="Knight Frank Tasmania",
            estimated_weekly_rent=450,
            council_rates_annual=1_400,
            water_rates_annual=500,
            zoning="General Residential",
            distress_signals=[
                DistressSignal(keyword="deceased estate", confidence=0.95, source="listing_text"),
                DistressSignal(keyword="all offers considered", confidence=0.85, source="listing_text"),
                DistressSignal(keyword="development potential", confidence=0.70, source="listing_text"),
            ],
            created_at=now - timedelta(days=4),
        ),

        # ── More NSW (golden opportunities) ──────────────────────────
        Property(
            id=uuid4(),
            address="17 Railway Parade",
            suburb="Lakemba",
            state="NSW",
            postcode="2195",
            property_type=PropertyType.HOUSE,
            bedrooms=3,
            bathrooms=1,
            car_spaces=1,
            land_size_sqm=500,
            building_size_sqm=100,
            year_built=1950,
            condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=820_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/17-railway-lakemba",
            listing_text="Mortgagee in possession — bank says sell NOW. Fibro cottage "
                         "on large R3 zoned block. Approved DA for 6 townhouses. Massive "
                         "development upside. Walking distance to Lakemba station.",
            agent_name="Hassan Ali",
            agent_phone="0421 555 777",
            agency_name="Laing+Simmons Lakemba",
            estimated_weekly_rent=550,
            council_rates_annual=1_300,
            water_rates_annual=550,
            zoning="R3",
            distress_signals=[
                DistressSignal(keyword="mortgagee in possession", confidence=0.98, source="listing_text"),
                DistressSignal(keyword="DA approved", confidence=0.90, source="listing_text"),
                DistressSignal(keyword="urgent sale", confidence=0.88, source="listing_text"),
            ],
            created_at=now - timedelta(hours=12),
        ),
        Property(
            id=uuid4(),
            address="201/55 Hill Road",
            suburb="Wentworth Point",
            state="NSW",
            postcode="2127",
            property_type=PropertyType.APARTMENT,
            bedrooms=2,
            bathrooms=2,
            car_spaces=1,
            building_size_sqm=82,
            year_built=2019,
            condition=PropertyCondition.EXCELLENT,
            asking_price=590_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/201-55-hill",
            listing_text="Near-new apartment with water views. Premium finishes, "
                         "Miele appliances, stone benchtops. Developer clearing last "
                         "units — fire sale pricing, was $720K. Currently leased at $580/wk.",
            agent_name="Jenny Liu",
            agent_phone="0432 666 888",
            agency_name="Meriton Residential",
            estimated_weekly_rent=580,
            current_weekly_rent=580,
            strata_levies_quarterly=1_500,
            council_rates_annual=950,
            water_rates_annual=500,
            distress_signals=[
                DistressSignal(keyword="fire sale", confidence=0.92, source="listing_text"),
                DistressSignal(keyword="price reduced", confidence=0.88, source="listing_text"),
                DistressSignal(keyword="below market", confidence=0.85, source="listing_text"),
            ],
            created_at=now - timedelta(hours=6),
        ),
        Property(
            id=uuid4(),
            address="8 Macquarie Street",
            suburb="Liverpool",
            state="NSW",
            postcode="2170",
            property_type=PropertyType.DUPLEX,
            bedrooms=6,
            bathrooms=3,
            car_spaces=2,
            land_size_sqm=550,
            building_size_sqm=240,
            year_built=2008,
            condition=PropertyCondition.GOOD,
            asking_price=950_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/8-macquarie-liverpool",
            listing_text="Dual income duplex — both sides currently tenanted. "
                         "Combined rent $1,100/week. Vendor relocating interstate, "
                         "settlement required ASAP. Rare dual-income in Liverpool.",
            agent_name="David Kumar",
            agent_phone="0443 777 999",
            agency_name="First National Liverpool",
            estimated_weekly_rent=1_100,
            current_weekly_rent=1_100,
            council_rates_annual=2_200,
            water_rates_annual=850,
            zoning="R3",
            distress_signals=[
                DistressSignal(keyword="relocating", confidence=0.83, source="listing_text"),
                DistressSignal(keyword="settlement required", confidence=0.80, source="listing_text"),
            ],
            created_at=now - timedelta(days=1),
        ),

        # ── QLD extra ────────────────────────────────────────────────
        Property(
            id=uuid4(),
            address="15 Mango Avenue",
            suburb="Moorooka",
            state="QLD",
            postcode="4105",
            property_type=PropertyType.HOUSE,
            bedrooms=3,
            bathrooms=1,
            car_spaces=2,
            land_size_sqm=607,
            building_size_sqm=100,
            year_built=1955,
            condition=PropertyCondition.RENOVATION_REQUIRED,
            asking_price=650_000,
            listing_status=ListingStatus.ACTIVE,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url="https://example.com/listing/15-mango-moorooka",
            listing_text="Post-war home on large block with dual street access. "
                         "Potential subdivision into 2 lots STCA. Close to Griffith Uni "
                         "and Moorooka station. Bring all offers — won't last.",
            agent_name="Steve Hall",
            agent_phone="0454 888 111",
            agency_name="Place Annerley",
            estimated_weekly_rent=480,
            council_rates_annual=1_300,
            water_rates_annual=500,
            zoning="LMR",
            distress_signals=[
                DistressSignal(keyword="won't last", confidence=0.72, source="listing_text"),
                DistressSignal(keyword="bring all offers", confidence=0.80, source="listing_text"),
                DistressSignal(keyword="potential subdivision", confidence=0.75, source="listing_text"),
            ],
            created_at=now - timedelta(days=2),
        ),
    ]


# ---------------------------------------------------------------------------
# Seed Deals (pre-analysed from seed properties)
# ---------------------------------------------------------------------------

def generate_seed_deals(properties: list[Property]) -> list[Deal]:
    """
    Create pre-analysed Deal objects for the first N seed properties.

    Uses algorithmic analysis — no LLM calls required.
    """
    settings = get_settings()
    deals: list[Deal] = []

    # Suburb medians for reference (approximate 2025 values)
    suburb_medians: dict[str, float] = {
        "Marrickville": 1_500_000,
        "Parramatta": 630_000,
        "Bankstown": 1_200_000,
        "Bondi": 1_100_000,
        "Gladesville": 2_800_000,
        "Footscray": 950_000,
        "Southbank": 720_000,
        "Glen Iris": 2_100_000,
        "Brunswick": 1_100_000,
        "West End": 1_050_000,
        "Brisbane City": 450_000,
        "Surfers Paradise": 650_000,
        "Indooroopilly": 1_300_000,
        "Mile End": 720_000,
        "Nedlands": 1_600_000,
        "Lakemba": 1_100_000,
        "Wentworth Point": 750_000,
        "Liverpool": 1_100_000,
        "Moorooka": 800_000,
    }

    for prop in properties:
        price = prop.asking_price or 0
        if price == 0:
            continue

        suburb_median = suburb_medians.get(prop.suburb, price * 1.15)
        weekly_rent = prop.estimated_weekly_rent or prop.current_weekly_rent or 0

        if weekly_rent == 0:
            continue

        annual_rent = weekly_rent * 52
        stamp_duty = _stamp_duty(price)

        # --- Build CashFlowModel ---
        lvr = settings.default_loan_lvr / 100
        loan_amount = price * lvr
        deposit = price * (1 - lvr)

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
            property_management_pct=7.0,
            council_rates_annual=prop.council_rates_annual or 1_500,
            water_rates_annual=prop.water_rates_annual or 600,
            strata_annual=(prop.strata_levies_quarterly or 0) * 4,
            insurance_annual=1_500,
            maintenance_annual=2_000,
            vacancy_weeks=2,
        )

        # --- Calculate BargainScore ---
        net_yield_val = 0.0
        total_inv = cf.total_investment
        if total_inv > 0:
            net_income = cf.annual_net_income
            net_yield_val = (net_income / total_inv) * 100

        distress_s = prop.distress_score

        bargain = BargainScore.calculate(
            asking_price=price,
            suburb_median=suburb_median,
            net_yield=net_yield_val,
            distress_score=distress_s,
            condition_factor=-10 if prop.condition == PropertyCondition.RENOVATION_REQUIRED else 0,
            market_growth_pct=2.0,
            golden_threshold=settings.golden_opportunity_score,
        )

        # --- Strategy recommendation ---
        strategies = [DealType.BTL]
        if prop.condition == PropertyCondition.RENOVATION_REQUIRED:
            strategies.append(DealType.FLIP)
            strategies.append(DealType.BRRR)
        if prop.land_size_sqm and prop.land_size_sqm > 500:
            strategies.append(DealType.SUBDIVISION)
        if prop.bedrooms and prop.bedrooms >= 4:
            strategies.append(DealType.HMO)
        primary_strategy = strategies[0]

        # --- AI-style analysis text (no LLM needed) ---
        price_diff_pct = ((suburb_median - price) / suburb_median * 100) if suburb_median > 0 else 0
        gross_yield = (annual_rent / price * 100) if price > 0 else 0

        analysis_lines = [
            f"PROPERTY: {prop.address}, {prop.suburb} {prop.state}",
            f"ASKING: ${price:,.0f} | MEDIAN: ${suburb_median:,.0f} ({price_diff_pct:+.1f}% vs median)",
            f"GROSS YIELD: {gross_yield:.1f}% | WEEKLY RENT: ${weekly_rent:,.0f}",
            f"STRATEGY: {primary_strategy.value}",
        ]
        if prop.distress_signals:
            signals_txt = ", ".join(d.keyword for d in prop.distress_signals)
            analysis_lines.append(f"DISTRESS SIGNALS: {signals_txt}")
        if bargain.is_golden_opportunity:
            analysis_lines.append("VERDICT: GOLDEN OPPORTUNITY — strongly consider move.")
        elif bargain.overall_score >= 65:
            analysis_lines.append("VERDICT: Strong deal — worth further investigation.")
        else:
            analysis_lines.append("VERDICT: Fair proposition — proceed with due diligence.")

        # --- Offer range ---
        offer_low = round(price * 0.88, -3)
        offer_mid = round(price * 0.92, -3)
        offer_high = round(price * 0.96, -3)

        # --- Competitive features (beats Deal Sourcer) ---
        # Refurb cost estimation per sqm by condition
        sqm = prop.building_size_sqm or 0
        if prop.condition == PropertyCondition.RENOVATION_REQUIRED:
            refurb_per_sqm = 1_200  # Full reno ~$1,200/sqm AU average
            refurb_cost = round(sqm * refurb_per_sqm) if sqm > 0 else round(price * 0.12)
        elif prop.condition == PropertyCondition.FAIR:
            refurb_per_sqm = 600
            refurb_cost = round(sqm * refurb_per_sqm) if sqm > 0 else round(price * 0.06)
        else:
            refurb_cost = 0

        # After Repair Value: reno spend generates 1.5x value uplift
        arv = round(price + (refurb_cost * 1.5)) if refurb_cost > 0 else 0

        # Flip profit: ARV - Purchase Price - Refurb - Stamp Duty - Legal - Agent
        agent_commission = round(arv * 0.02) if arv > 0 else 0
        flip_profit = round(arv - price - refurb_cost - stamp_duty - 3_000 - agent_commission) if arv > 0 else 0

        # BRRR equity: refinance at 80% of ARV
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
