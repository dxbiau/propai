"""
Property model — the core entity in Australian Property Associates.

Every scraped listing, shadow listing, and off-market signal becomes a Property.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class PropertyType(str, Enum):
    HOUSE = "house"
    UNIT = "unit"
    APARTMENT = "apartment"
    TOWNHOUSE = "townhouse"
    VILLA = "villa"
    LAND = "land"
    RURAL = "rural"
    FARM = "farm"
    ACREAGE = "acreage"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    RETAIL = "retail"
    WAREHOUSE = "warehouse"
    DUPLEX = "duplex"
    GRANNY_FLAT = "granny_flat"
    OTHER = "other"


class PropertySource(str, Enum):
    """Where the listing was discovered."""
    REA = "realestate.com.au"
    DOMAIN = "domain.com.au"
    BOUTIQUE_AGENCY = "boutique_agency"
    COUNCIL_DA = "council_da"
    PUBLIC_NOTICE = "public_notice"
    SOCIAL_MEDIA = "social_media"
    COMING_SOON = "coming_soon"
    OFF_MARKET = "off_market"
    AUCTION_RESULT = "auction_result"
    MANUAL = "manual"


class PropertyCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    RENOVATION_REQUIRED = "renovation_required"
    KNOCKDOWN_REBUILD = "knockdown_rebuild"
    UNKNOWN = "unknown"


class ListingStatus(str, Enum):
    ACTIVE = "active"
    UNDER_OFFER = "under_offer"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"
    PRE_MARKET = "pre_market"
    OFF_MARKET = "off_market"
    AUCTION = "auction"


class DistressSignal(BaseModel):
    """Detected distress indicators from listing text / public records."""
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"keyword": "must sell", "confidence": 0.92, "source": "listing_text"},
                {"keyword": "deceased estate", "confidence": 0.98, "source": "public_notice"},
                {"keyword": "mortgagee", "confidence": 0.95, "source": "listing_text"},
            ]
        }
    )

    keyword: str = Field(..., description="The distress keyword detected")
    confidence: float = Field(ge=0, le=1, description="Confidence 0–1")
    source: str = Field(default="listing_text", description="Where the signal was found")


# Common distress keywords for Australian market
DISTRESS_KEYWORDS: list[str] = [
    "must sell",
    "motivated seller",
    "deceased estate",
    "mortgagee",
    "mortgagee in possession",
    "urgent sale",
    "price reduced",
    "price slashed",
    "vendor says sell",
    "bring all offers",
    "all offers considered",
    "divorce",
    "settlement required",
    "relocating",
    "moving overseas",
    "downsizing",
    "liquidation",
    "fire sale",
    "below market",
    "priced to sell",
    "won't last",
    "needs work",
    "handyman special",
    "renovator's delight",
    "development potential",
    "STCA",  # Subject to Council Approval
    "DA approved",
    "potential subdivision",
]


class Property(BaseModel):
    """Core property entity — every listing in the Australian Property Associates system."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Location ---
    address: str = Field(..., min_length=5, description="Full street address")
    suburb: str = Field(..., description="Suburb name")
    state: str = Field(..., description="Australian state/territory")
    postcode: str = Field(..., pattern=r"^\d{4}$", description="4-digit AU postcode")
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # --- Property Details ---
    property_type: PropertyType = PropertyType.HOUSE
    bedrooms: Optional[int] = Field(None, ge=0, le=50)
    bathrooms: Optional[int] = Field(None, ge=0, le=20)
    car_spaces: Optional[int] = Field(None, ge=0, le=20)
    land_size_sqm: Optional[float] = Field(None, ge=0, description="Land area in m²")
    building_size_sqm: Optional[float] = Field(None, ge=0, description="Floor area in m²")
    year_built: Optional[int] = Field(None, ge=1800, le=2030)
    condition: PropertyCondition = PropertyCondition.UNKNOWN

    # --- Pricing ---
    asking_price: Optional[float] = Field(None, ge=0, description="Listed/asking price AUD")
    price_guide_low: Optional[float] = Field(None, ge=0)
    price_guide_high: Optional[float] = Field(None, ge=0)
    sold_price: Optional[float] = Field(None, ge=0)
    sold_date: Optional[datetime] = None

    # --- Listing Info ---
    listing_status: ListingStatus = ListingStatus.ACTIVE
    source: PropertySource = PropertySource.MANUAL
    source_url: Optional[str] = None
    listing_text: Optional[str] = Field(None, description="Full listing description")
    agent_name: Optional[str] = None
    agent_phone: Optional[str] = None
    agency_name: Optional[str] = None

    # --- Australian-Specific ---
    strata_levies_quarterly: Optional[float] = Field(None, ge=0, description="Strata/body corp levies per quarter AUD")
    council_rates_annual: Optional[float] = Field(None, ge=0, description="Council rates per year AUD")
    water_rates_annual: Optional[float] = Field(None, ge=0, description="Water rates per year AUD")
    zoning: Optional[str] = Field(None, description="Council zoning code e.g. R2, R3, B4")
    flood_zone: Optional[bool] = None
    bushfire_zone: Optional[bool] = None
    heritage_listed: Optional[bool] = None

    # --- Rental Data ---
    estimated_weekly_rent: Optional[float] = Field(None, ge=0)
    current_weekly_rent: Optional[float] = Field(None, ge=0, description="If tenanted")
    vacancy_rate_pct: Optional[float] = Field(None, ge=0, le=100)

    # --- Distress Signals ---
    distress_signals: list[DistressSignal] = Field(default_factory=list)

    # --- Images ---
    image_urls: list[str] = Field(default_factory=list)

    # --- Metadata ---
    raw_html: Optional[str] = Field(None, exclude=True, description="Original scraped HTML")
    tags: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def has_distress_signals(self) -> bool:
        return len(self.distress_signals) > 0

    @computed_field
    @property
    def distress_score(self) -> float:
        """Aggregate distress score 0–100 based on signal count and confidence."""
        if not self.distress_signals:
            return 0.0
        avg_confidence = sum(s.confidence for s in self.distress_signals) / len(self.distress_signals)
        count_factor = min(len(self.distress_signals) / 5, 1.0)  # Cap at 5 signals
        return round(avg_confidence * count_factor * 100, 1)

    @computed_field
    @property
    def effective_price(self) -> Optional[float]:
        """Best available price — sold > asking > midpoint of guide."""
        if self.sold_price:
            return self.sold_price
        if self.asking_price:
            return self.asking_price
        if self.price_guide_low and self.price_guide_high:
            return (self.price_guide_low + self.price_guide_high) / 2
        return self.price_guide_low or self.price_guide_high

    @computed_field
    @property
    def annual_holding_costs(self) -> float:
        """Estimated total annual holding costs (strata + council + water)."""
        strata = (self.strata_levies_quarterly or 0) * 4
        council = self.council_rates_annual or 0
        water = self.water_rates_annual or 0
        return strata + council + water
