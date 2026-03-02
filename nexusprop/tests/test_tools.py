"""
Tests for Australian Property Associates tools - ROI Calculator, Bargain Scorer, Data Cleaner, Comps Engine.

Unit tests for the core computation layer.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from nexusprop.tools.data_cleaner import (
    DataCleaner,
    parse_price,
    parse_beds_baths_cars,
    parse_land_size,
    detect_distress_signals,
    detect_property_type,
    parse_address_components,
)
from nexusprop.tools.roi_calculator import ROICalculator, quick_roi
from nexusprop.tools.bargain_scorer import BargainScorer
from nexusprop.tools.comps_engine import CompsEngine
from nexusprop.tools.offer_writer import OfferWriter
from nexusprop.models.property import Property, PropertyType, PropertySource, PropertyCondition
from nexusprop.models.suburb import SuburbProfile, GrowthMetrics
from nexusprop.models.offer import OfferGenerationRequest, OfferTone, SellerMotivation
from nexusprop.models.deal import DealType


# ═══════════════════════════════════════════════════════════════════
# HELPER: build a valid Property with all required fields
# ═══════════════════════════════════════════════════════════════════

def _prop(**overrides) -> Property:
    """Create a Property with sensible defaults; override any field."""
    defaults = dict(
        address="123 Test St, Sydney NSW 2000",
        suburb="Sydney",
        state="NSW",
        postcode="2000",
        property_type=PropertyType.HOUSE,
    )
    defaults.update(overrides)
    return Property(**defaults)


# ═══════════════════════════════════════════════════════════════════
# DATA CLEANER TESTS
# ═══════════════════════════════════════════════════════════════════


class TestDataCleaner:
    """Data cleaner (parsing) tests — module-level functions."""

    def test_parse_price_simple(self):
        """Parse a simple price string."""
        assert parse_price("$650,000") == 650_000

    def test_parse_price_guide(self):
        """Parse price guide format."""
        result = parse_price("Price Guide $600,000 - $650,000")
        assert result is not None
        assert result > 0

    def test_parse_price_millions(self):
        """Parse million dollar format."""
        result = parse_price("$1.2M")
        assert result == 1_200_000

    def test_parse_price_none(self):
        """Return None for unparseable price."""
        assert parse_price("Contact Agent") is None
        assert parse_price("") is None

    def test_parse_beds_baths_cars(self):
        """Extract bed/bath/car numbers."""
        beds, baths, cars = parse_beds_baths_cars("3 bed 2 bath 1 car")
        assert beds == 3
        assert baths == 2
        assert cars == 1

    def test_parse_land_size(self):
        """Parse land size in sqm."""
        assert parse_land_size("450 sqm") == 450
        assert parse_land_size("450m²") == 450
        assert parse_land_size("450sqm") == 450

    def test_detect_distress_signals(self):
        """Detect distress keywords in listing text."""
        text = "Mortgagee in possession. Must be sold. Deceased estate."
        signals = detect_distress_signals(text)
        assert len(signals) >= 2

    def test_no_distress_signals(self):
        """No distress signals in normal listing."""
        text = "Beautiful family home in quiet street. Recently renovated."
        signals = detect_distress_signals(text)
        assert len(signals) == 0

    def test_detect_property_type(self):
        """Detect property type from description."""
        assert detect_property_type("Charming 3 bedroom house") == PropertyType.HOUSE
        assert detect_property_type("Modern 2 bedroom apartment") == PropertyType.APARTMENT
        assert detect_property_type("Vacant land for sale") == PropertyType.LAND

    def test_parse_address_components(self):
        """Parse Australian address into components."""
        result = parse_address_components("45 George St, Sydney NSW 2000")
        assert result.get("suburb") or result.get("state") or result.get("postcode")


# ═══════════════════════════════════════════════════════════════════
# ROI CALCULATOR TESTS
# ═══════════════════════════════════════════════════════════════════


class TestROICalculator:
    """ROI Calculator tests."""

    @pytest.fixture
    def calculator(self):
        return ROICalculator()

    def test_gross_yield_calculation(self, calculator):
        """Gross yield = weekly_rent * 52 / price * 100."""
        prop = _prop(asking_price=600_000, estimated_weekly_rent=550)
        result = calculator.calculate(prop=prop, strategy=DealType.BTL)
        expected_yield = (550 * 52) / 600_000 * 100
        assert abs(result.gross_rental_yield - expected_yield) < 0.5

    def test_quick_roi(self):
        """Quick ROI screening function."""
        result = quick_roi(500_000, 500)
        assert result["gross_yield"] > 0
        assert result["monthly_cash_flow"] is not None

    def test_negative_cash_flow(self, calculator):
        """Identify negative cash flow scenarios."""
        prop = _prop(asking_price=1_500_000, estimated_weekly_rent=500)
        result = calculator.calculate(prop=prop, strategy=DealType.BTL)
        # High price, low rent — should be negative cash flow
        assert result.monthly_cash_flow < 0

    def test_stamp_duty_calculation(self, calculator):
        """Stamp duty is calculated in the cash-flow model."""
        prop = _prop(asking_price=600_000, estimated_weekly_rent=500)
        result = calculator.calculate(prop=prop, strategy=DealType.BTL)
        assert result.cash_flow_model.stamp_duty > 0

    def test_zero_price_handling(self, calculator):
        """Handle zero price gracefully."""
        try:
            prop = _prop(asking_price=0, estimated_weekly_rent=500)
            result = calculator.calculate(prop=prop, strategy=DealType.BTL)
            assert result is not None
        except (ValueError, ZeroDivisionError):
            pass  # Acceptable to raise


# ═══════════════════════════════════════════════════════════════════
# BARGAIN SCORER TESTS
# ═══════════════════════════════════════════════════════════════════


class TestBargainScorer:
    """Bargain Scorer tests."""

    @pytest.fixture
    def scorer(self):
        return BargainScorer()

    @pytest.fixture
    def suburb(self):
        return SuburbProfile(
            suburb_name="Test Suburb",
            state="NSW",
            postcode="2000",
            growth=GrowthMetrics(median_house_price=600_000),
        )

    def test_score_property(self, scorer, suburb):
        """Score a property with basic data."""
        prop = _prop(asking_price=500_000, estimated_weekly_rent=550, bedrooms=3)
        result = scorer.score(prop=prop, suburb=suburb)
        # Property is 17% below median — should score well
        assert result.overall_score > 0
        assert result.overall_score <= 100

    def test_below_median_scores_higher(self, scorer, suburb):
        """Properties below suburb median should score higher."""
        below = _prop(address="10 Below St, Sydney NSW 2000", asking_price=400_000)
        at = _prop(address="10 At St, Sydney NSW 2000", asking_price=600_000)

        score_below = scorer.score(prop=below, suburb=suburb)
        score_at = scorer.score(prop=at, suburb=suburb)

        assert score_below.price_deviation_score > score_at.price_deviation_score

    def test_strategy_recommendation(self, scorer, suburb):
        """Recommend an investment strategy."""
        prop = _prop(
            asking_price=500_000,
            bedrooms=4,
            bathrooms=2,
            land_size_sqm=600,
        )
        bs = scorer.score(prop=prop, suburb=suburb)
        strategies = scorer.recommend_strategy(prop=prop, suburb=suburb, bargain_score=bs)
        assert isinstance(strategies, list)

    def test_rank_properties(self, scorer, suburb):
        """Rank multiple properties by Bargain Score."""
        properties = [
            (_prop(address="10 Cheap St, Sydney NSW 2000", asking_price=300_000), suburb, 0.0),
            (_prop(address="10 Medium St, Sydney NSW 2000", asking_price=500_000), suburb, 0.0),
            (_prop(address="10 Expensive St, Sydney NSW 2000", asking_price=800_000), suburb, 0.0),
        ]
        ranked = scorer.rank_properties(properties=properties)
        assert len(ranked) == 3
        # Cheapest should rank highest (most below median)
        assert ranked[0][0].address == "10 Cheap St, Sydney NSW 2000"


# ═══════════════════════════════════════════════════════════════════
# COMPS ENGINE TESTS
# ═══════════════════════════════════════════════════════════════════


class TestCompsEngine:
    """Comparable sales engine tests."""

    @pytest.fixture
    def engine(self):
        return CompsEngine()

    def test_find_comps(self, engine):
        """Find comparable sales for a property."""
        subject = _prop(
            address="10 Subject St, Parramatta NSW 2150",
            suburb="Parramatta",
            postcode="2150",
            bedrooms=3,
            asking_price=700_000,
        )
        sold = [
            _prop(
                address=f"1{i} Sold St, Parramatta NSW 2150",
                suburb="Parramatta",
                postcode="2150",
                bedrooms=3,
                sold_price=650_000 + i * 20_000,
                sold_date=datetime.utcnow() - timedelta(days=30 + i * 10),
            )
            for i in range(5)
        ]

        analysis = engine.analyze(subject, sold)
        assert analysis is not None
        assert analysis.num_comps > 0

    def test_empty_sold_data(self, engine):
        """Handle case with no sold data gracefully."""
        subject = _prop(
            address="10 Subject St, Nowhere NSW 2999",
            suburb="Nowhere",
            postcode="2999",
            bedrooms=3,
            asking_price=500_000,
        )
        analysis = engine.analyze(subject, [])
        assert analysis is not None
        assert analysis.estimated_market_value == 500_000 or analysis.num_comps == 0


# ═══════════════════════════════════════════════════════════════════
# OFFER WRITER TESTS
# ═══════════════════════════════════════════════════════════════════


class TestOfferWriter:
    """Offer writer tests."""

    @pytest.fixture
    def writer(self):
        return OfferWriter()

    def test_generate_offer_document(self, writer):
        """Generate a full offer document."""
        request = OfferGenerationRequest(
            property_id=uuid4(),
            property_address="10 Test St, Sydney NSW 2000",
            asking_price=600_000,
            buyer_name="John Smith",
            buyer_budget_max=600_000,
            preferred_tone=OfferTone.PROFESSIONAL,
        )
        doc = writer.generate(request)
        assert doc.offer_price > 0
        assert len(doc.cover_letter) > 0
        assert "John Smith" in doc.cover_letter or "Test St" in doc.cover_letter

    def test_counter_strategy(self, writer):
        """Generated document includes a counter-offer strategy."""
        request = OfferGenerationRequest(
            property_id=uuid4(),
            property_address="10 Test St, Sydney NSW 2000",
            asking_price=600_000,
            buyer_name="Jane Doe",
            buyer_budget_max=620_000,
            preferred_tone=OfferTone.PROFESSIONAL,
        )
        doc = writer.generate(request)
        assert len(doc.counter_offer_strategy) > 0

    def test_all_tones_available(self, writer):
        """All 5 offer tones produce output."""
        tones = [
            OfferTone.EMPATHETIC,
            OfferTone.PROFESSIONAL,
            OfferTone.URGENT,
            OfferTone.FAMILY_STORY,
            OfferTone.INVESTOR_DIRECT,
        ]
        for tone in tones:
            request = OfferGenerationRequest(
                property_id=uuid4(),
                property_address="Test",
                asking_price=550_000,
                buyer_name="Test Buyer",
                buyer_budget_max=600_000,
                preferred_tone=tone,
            )
            doc = writer.generate(request)
            assert len(doc.cover_letter) > 0, f"Tone '{tone.value}' produced empty output"
