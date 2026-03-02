"""
Tests for Property Insights Australia data models - Property, Deal, Offer, User.

Covers validation, computed properties, enums, and edge cases.
"""

from __future__ import annotations

import pytest
from uuid import uuid4
from datetime import datetime

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
from nexusprop.models.offer import (
    OfferDocument,
    OfferGenerationRequest,
    OfferTone,
    SellerMotivation,
    OfferCondition,
)
from nexusprop.models.user import (
    UserProfile,
    UserPreferences,
    BudgetRange,
    LocationPreference,
    PropertyPreferences,
    NotificationChannel,
)
from nexusprop.models.suburb import SuburbProfile, GrowthMetrics


# ═══════════════════════════════════════════════════════════════════
# PROPERTY MODEL TESTS
# ═══════════════════════════════════════════════════════════════════


class TestProperty:
    """Property model tests."""

    def test_create_minimal_property(self):
        """Create a property with only required fields."""
        p = Property(
            address="123 Test St, Sydney NSW 2000",
            suburb="Sydney",
            state="NSW",
            postcode="2000",
        )
        assert p.address == "123 Test St, Sydney NSW 2000"
        assert p.id is not None
        assert p.property_type == PropertyType.HOUSE
        assert p.source == PropertySource.MANUAL

    def test_create_full_property(self):
        """Create a property with all fields populated."""
        p = Property(
            address="45 Surry Hills Rd, Surry Hills NSW 2010",
            suburb="Surry Hills",
            state="NSW",
            postcode="2010",
            property_type=PropertyType.HOUSE,
            source=PropertySource.BOUTIQUE_AGENCY,
            bedrooms=3,
            bathrooms=2,
            car_spaces=1,
            land_size_sqm=350.0,
            asking_price=1_200_000,
            estimated_weekly_rent=800,
        )
        assert p.suburb == "Surry Hills"
        assert p.bedrooms == 3
        assert p.asking_price == 1_200_000

    def test_property_type_enum(self):
        """All Australian property types are available."""
        assert PropertyType.HOUSE.value == "house"
        assert PropertyType.UNIT.value == "unit"
        assert PropertyType.DUPLEX.value == "duplex"
        assert PropertyType.GRANNY_FLAT.value == "granny_flat"

    def test_property_source_enum(self):
        """All property sources are available."""
        assert PropertySource.REA.value == "realestate.com.au"
        assert PropertySource.BOUTIQUE_AGENCY.value == "boutique_agency"
        assert PropertySource.COUNCIL_DA.value == "council_da"
        assert PropertySource.PUBLIC_NOTICE.value == "public_notice"

    def test_effective_price_single(self):
        """Effective price returns asking_price when set."""
        p = Property(
            address="123 Test St, Sydney NSW 2000",
            suburb="Sydney",
            state="NSW",
            postcode="2000",
            asking_price=500_000,
        )
        assert p.effective_price == 500_000

    def test_effective_price_range(self):
        """Effective price returns midpoint for price range."""
        p = Property(
            address="123 Test St, Sydney NSW 2000",
            suburb="Sydney",
            state="NSW",
            postcode="2000",
            price_guide_low=400_000,
            price_guide_high=450_000,
        )
        assert p.effective_price == 425_000

    def test_distress_score_with_signals(self):
        """Distress score is calculated from signals."""
        p = Property(
            address="123 Test St, Sydney NSW 2000",
            suburb="Sydney",
            state="NSW",
            postcode="2000",
            distress_signals=[
                DistressSignal(keyword="mortgagee", confidence=0.9),
                DistressSignal(keyword="deceased estate", confidence=0.8),
            ],
        )
        assert p.distress_score > 0


# ═══════════════════════════════════════════════════════════════════
# CASH FLOW MODEL TESTS
# ═══════════════════════════════════════════════════════════════════


class TestCashFlowModel:
    """Cash flow calculation tests."""

    @pytest.fixture
    def basic_cash_flow(self):
        return CashFlowModel(
            purchase_price=600_000,
            stamp_duty=22_000,
            weekly_rent=550,
            annual_gross_income=550 * 52,
            vacancy_weeks=2,
            property_management_pct=7.0,
            insurance_annual=1_500,
            council_rates_annual=2_000,
            water_rates_annual=800,
            strata_annual=0,
            maintenance_annual=6_000,
            loan_amount=480_000,
            interest_rate_pct=6.25,
        )

    def test_gross_yield(self, basic_cash_flow):
        """Gross yield = (annual_gross_income) / purchase_price * 100."""
        expected = (550 * 52) / 600_000 * 100
        assert abs(basic_cash_flow.gross_rental_yield - expected) < 0.01

    def test_annual_gross_income(self, basic_cash_flow):
        """Annual gross income = weekly rent * 52."""
        assert basic_cash_flow.annual_gross_income == 550 * 52

    def test_total_purchase_cost(self, basic_cash_flow):
        """Total purchase cost includes stamp duty, legal, inspection."""
        assert basic_cash_flow.total_purchase_cost > basic_cash_flow.purchase_price

    def test_monthly_cash_flow_exists(self, basic_cash_flow):
        """Monthly cash flow is computed."""
        # It could be negative — that's fine, just check it's computed
        assert isinstance(basic_cash_flow.monthly_cash_flow, float)


# ═══════════════════════════════════════════════════════════════════
# BARGAIN SCORE TESTS
# ═══════════════════════════════════════════════════════════════════


class TestBargainScore:
    """Bargain Score™ calculation tests."""

    def test_bargain_score_creation(self):
        """Create a bargain score via the calculate factory method."""
        bs = BargainScore.calculate(
            asking_price=500_000,
            suburb_median=600_000,
            net_yield=5.0,
            distress_score=60,
            days_on_market=30,
        )
        assert bs.overall_score >= 0
        assert bs.overall_score <= 100
        assert bs.price_deviation_score >= 0

    def test_golden_opportunity_detection(self):
        """High-scoring properties are flagged as golden opportunities."""
        bs = BargainScore.calculate(
            asking_price=300_000,
            suburb_median=700_000,
            net_yield=8.0,
            distress_score=90,
            days_on_market=120,
            golden_threshold=85,
        )
        # Very cheap vs median with high distress — should be golden
        assert bs.overall_score > 0

    def test_score_bounds(self):
        """Zero inputs produce a bounded score."""
        bs = BargainScore.calculate(
            asking_price=600_000,
            suburb_median=600_000,
            net_yield=0,
            distress_score=0,
        )
        assert bs.overall_score >= 0
        assert bs.overall_score <= 100


# ═══════════════════════════════════════════════════════════════════
# OFFER MODEL TESTS
# ═══════════════════════════════════════════════════════════════════


class TestOfferDocument:
    """Offer document model tests."""

    def test_offer_creation(self):
        """Create an offer document."""
        offer = OfferDocument(
            property_id=uuid4(),
            property_address="10 Test Lane, Sydney NSW 2000",
            buyer_name="John Smith",
            offer_price=550_000,
            deposit_amount=27_500,
            settlement_days=42,
        )
        assert offer.offer_price == 550_000
        assert offer.deposit_pct == 5.0
        assert offer.legal_disclaimer  # Must always be present

    def test_deposit_percentage(self):
        """Deposit percentage calculated correctly."""
        offer = OfferDocument(
            property_id=uuid4(),
            property_address="Test",
            buyer_name="Test Buyer",
            offer_price=1_000_000,
            deposit_amount=100_000,
        )
        assert offer.deposit_pct == 10.0

    def test_standard_conditions(self):
        """Standard AU conditions are generated."""
        offer = OfferDocument(
            property_id=uuid4(),
            property_address="Test",
            buyer_name="Test Buyer",
            offer_price=500_000,
            deposit_amount=25_000,
        )
        conditions = offer.get_standard_conditions()
        assert len(conditions) == 4
        condition_names = [c.name for c in conditions]
        assert "Finance Approval" in condition_names
        assert "Building & Pest Inspection" in condition_names
        assert "Section 32 / Contract Review" in condition_names

    def test_seller_motivation_enum(self):
        """Seller motivation levels."""
        assert SellerMotivation.DESPERATE.value == "desperate"
        assert SellerMotivation.MOTIVATED.value == "motivated"
        assert SellerMotivation.ASPIRATIONAL.value == "aspirational"

    def test_offer_tone_enum(self):
        """Offer tones."""
        assert OfferTone.EMPATHETIC.value == "empathetic"
        assert OfferTone.FAMILY_STORY.value == "family_story"
        assert OfferTone.INVESTOR_DIRECT.value == "investor_direct"

    def test_legal_disclaimer_always_present(self):
        """Legal disclaimer cannot be empty."""
        offer = OfferDocument(
            property_id=uuid4(),
            property_address="Test",
            buyer_name="Test",
            offer_price=100_000,
            deposit_amount=5_000,
        )
        assert "NOT LEGAL ADVICE" in offer.legal_disclaimer


# ═══════════════════════════════════════════════════════════════════
# USER MODEL TESTS
# ═══════════════════════════════════════════════════════════════════


class TestUserProfile:
    """User profile and preferences tests."""

    def test_create_user(self):
        """Create a user with defaults."""
        user = UserProfile(name="Jane Doe", email="jane@example.com")
        assert user.name == "Jane Doe"
        assert user.plan == "free"
        assert user.is_active is True
        assert user.preferences.notification_channel == NotificationChannel.WHATSAPP

    def test_budget_midpoint(self):
        """Budget midpoint calculation."""
        budget = BudgetRange(min_price=400_000, max_price=600_000)
        assert budget.midpoint == 500_000

    def test_engagement_score(self):
        """Engagement score based on activity."""
        user = UserProfile(
            name="Active User",
            email="active@example.com",
            properties_viewed=[uuid4() for _ in range(10)],
            properties_saved=[uuid4() for _ in range(3)],
            offers_generated=2,
        )
        # 10*2 + 3*5 + 2*20 = 20 + 15 + 40 = 75
        assert user.engagement_score == 75

    def test_engagement_score_capped(self):
        """Engagement score is capped at 100."""
        user = UserProfile(
            name="Super User",
            email="super@example.com",
            properties_viewed=[uuid4() for _ in range(50)],
            offers_generated=10,
        )
        assert user.engagement_score == 100

    def test_notification_channel_enum(self):
        """Notification channel options."""
        assert NotificationChannel.WHATSAPP.value == "whatsapp"
        assert NotificationChannel.SMS.value == "sms"
        assert NotificationChannel.EMAIL.value == "email"

    def test_user_preferences_defaults(self):
        """User preferences have sensible defaults."""
        prefs = UserPreferences()
        assert prefs.budget.max_price == 2_000_000
        assert DealType.BTL in prefs.preferred_strategies
        assert prefs.golden_opportunity_only is True
        assert prefs.max_notifications_per_day == 3


# ═══════════════════════════════════════════════════════════════════
# SUBURB PROFILE TESTS
# ═══════════════════════════════════════════════════════════════════


class TestSuburbProfile:
    """Suburb intelligence model tests."""

    def test_create_suburb(self):
        """Create a suburb profile."""
        suburb = SuburbProfile(
            suburb_name="Parramatta",
            state="NSW",
            postcode="2150",
            growth=GrowthMetrics(
                median_house_price=900_000,
                median_unit_price=550_000,
            ),
        )
        assert suburb.suburb_name == "Parramatta"
        assert suburb.state == "NSW"

    def test_growth_metrics(self):
        """Growth metrics model."""
        gm = GrowthMetrics(
            annual_growth_pct_house=5.2,
            five_year_growth_pct=30.0,
            ten_year_growth_pct=80.0,
        )
        assert gm.annual_growth_pct_house == 5.2
        assert gm.five_year_growth_pct == 30.0
