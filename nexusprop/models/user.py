"""
User profile & preferences — the Concierge's memory.

Stores the user's "vibe" — what they love, hate, and care about.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from nexusprop.models.deal import DealType
from nexusprop.models.property import PropertyType


class NotificationChannel(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    NONE = "none"


class BudgetRange(BaseModel):
    min_price: float = Field(default=0, ge=0)
    max_price: float = Field(default=2_000_000, ge=0)

    @property
    def midpoint(self) -> float:
        return (self.min_price + self.max_price) / 2


class LocationPreference(BaseModel):
    suburbs: list[str] = Field(default_factory=list, description="Preferred suburbs")
    states: list[str] = Field(default_factory=list, description="Preferred states")
    postcodes: list[str] = Field(default_factory=list, description="Preferred postcodes")
    max_cbd_distance_km: Optional[float] = None
    max_train_station_km: Optional[float] = None


class PropertyPreferences(BaseModel):
    """What the user wants (and doesn't want) in a property."""

    # --- Basics ---
    property_types: list[PropertyType] = Field(default_factory=lambda: [PropertyType.HOUSE])
    min_bedrooms: Optional[int] = Field(None, ge=0)
    max_bedrooms: Optional[int] = Field(None, ge=0)
    min_bathrooms: Optional[int] = Field(None, ge=0)
    min_car_spaces: Optional[int] = Field(None, ge=0)
    min_land_size_sqm: Optional[float] = Field(None, ge=0)

    # --- Loves (positive signals) ---
    loves: list[str] = Field(
        default_factory=list,
        description="Features the user loves e.g. 'high ceilings', 'north-facing', 'pool'"
    )

    # --- Hates (negative signals) ---
    hates: list[str] = Field(
        default_factory=list,
        description="Features the user hates e.g. 'busy road', 'no garage', 'north-facing windows'"
    )

    # --- Deal Breakers ---
    no_strata: bool = Field(default=False, description="Exclude strata properties")
    no_flood_zone: bool = Field(default=True, description="Exclude flood zone properties")
    no_bushfire_zone: bool = Field(default=False, description="Exclude bushfire zone")
    no_heritage: bool = Field(default=False, description="Exclude heritage listed")
    require_parking: bool = Field(default=False)

    # --- Investment Criteria ---
    min_gross_yield: Optional[float] = Field(None, ge=0, description="Minimum gross rental yield %")
    min_net_yield: Optional[float] = Field(None, ge=0, description="Minimum net yield %")
    min_bargain_score: float = Field(default=65, ge=0, le=100)


class UserPreferences(BaseModel):
    """Complete user preference profile — the Concierge's brain."""

    budget: BudgetRange = Field(default_factory=BudgetRange)
    location: LocationPreference = Field(default_factory=LocationPreference)
    property: PropertyPreferences = Field(default_factory=PropertyPreferences)
    preferred_strategies: list[DealType] = Field(
        default_factory=lambda: [DealType.BTL],
        description="Investment strategies the user is interested in"
    )

    # --- Notification Preferences ---
    notification_channel: NotificationChannel = NotificationChannel.WHATSAPP
    golden_opportunity_only: bool = Field(
        default=True,
        description="Only notify for Golden Opportunity deals"
    )
    max_notifications_per_day: int = Field(default=3, ge=0, le=50)
    quiet_hours_start: Optional[str] = Field(None, description="HH:MM — no notifications after this")
    quiet_hours_end: Optional[str] = Field(None, description="HH:MM — notifications resume")


class UserProfile(BaseModel):
    """A NexusProp user."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Identity ---
    name: str
    email: str
    phone: Optional[str] = Field(None, description="Australian mobile e.g. +614xxxxxxxx")
    whatsapp_number: Optional[str] = None

    # --- Preferences ---
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    # --- Subscription ---
    plan: str = Field(default="free", description="free | pro | elite")
    is_active: bool = True

    # --- Learning ---
    properties_viewed: list[UUID] = Field(default_factory=list)
    properties_saved: list[UUID] = Field(default_factory=list)
    properties_dismissed: list[UUID] = Field(default_factory=list)
    offers_generated: int = Field(default=0, ge=0)

    @property
    def engagement_score(self) -> float:
        """How engaged the user is — used for churn prediction."""
        return min(
            len(self.properties_viewed) * 2
            + len(self.properties_saved) * 5
            + self.offers_generated * 20,
            100,
        )
