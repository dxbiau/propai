"""NexusProp data models package."""

from nexusprop.models.property import Property, PropertySource, PropertyType
from nexusprop.models.suburb import SuburbProfile
from nexusprop.models.deal import Deal, DealType, BargainScore
from nexusprop.models.offer import OfferDocument, SellerMotivation
from nexusprop.models.user import UserProfile, UserPreferences

__all__ = [
    "Property",
    "PropertySource",
    "PropertyType",
    "SuburbProfile",
    "Deal",
    "DealType",
    "BargainScore",
    "OfferDocument",
    "SellerMotivation",
    "UserProfile",
    "UserPreferences",
]
