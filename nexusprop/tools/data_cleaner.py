"""
Data Cleaner — transforms raw HTML into structured Property objects.

Uses BeautifulSoup for parsing and Claude for intelligent extraction
of messy, inconsistent listing data from boutique agency sites.
"""

from __future__ import annotations

import re
from typing import Optional

import structlog
from bs4 import BeautifulSoup

from nexusprop.models.property import (
    DistressSignal,
    DISTRESS_KEYWORDS,
    ListingStatus,
    Property,
    PropertyCondition,
    PropertySource,
    PropertyType,
)

logger = structlog.get_logger(__name__)


# ── Price Parsing ─────────────────────────────────────────────────────────────

PRICE_PATTERNS = [
    # "$800k" or "$1.2m" — must come before plain dollar to avoid greedy match
    re.compile(r"\$\s*([\d.]+)\s*(k|m)\b", re.IGNORECASE),
    # "$1,200,000" or "$1200000"
    re.compile(r"\$\s*([\d,]+(?:\.\d{2})?)\s*(?:k|K)?", re.IGNORECASE),
    # "From $800,000"
    re.compile(r"(?:from|price[:\s]*)\s*\$\s*([\d,]+)", re.IGNORECASE),
    # "Offers above $700,000"
    re.compile(r"(?:offers?\s+(?:above|over|from))\s*\$\s*([\d,]+)", re.IGNORECASE),
]


def parse_price(text: str) -> Optional[float]:
    """Extract the first price from text. Returns AUD amount or None."""
    if not text:
        return None

    for pattern in PRICE_PATTERNS:
        match = pattern.search(text)
        if match:
            price_str = match.group(1).replace(",", "")
            try:
                price = float(price_str)
                # Handle shorthand
                if match.lastindex and match.lastindex >= 2:
                    suffix = match.group(2).lower()
                    if suffix == "k":
                        price *= 1_000
                    elif suffix == "m":
                        price *= 1_000_000
                return price
            except ValueError:
                continue

    return None


def parse_price_range(text: str) -> tuple[Optional[float], Optional[float]]:
    """Extract a price range e.g. '$800,000 - $850,000'."""
    range_pattern = re.compile(
        r"\$\s*([\d,]+)\s*[-–—to]+\s*\$\s*([\d,]+)", re.IGNORECASE
    )
    match = range_pattern.search(text)
    if match:
        low = float(match.group(1).replace(",", ""))
        high = float(match.group(2).replace(",", ""))
        return low, high
    return None, None


# ── Bedroom/Bathroom/Car Parsing ─────────────────────────────────────────────

def parse_beds_baths_cars(text: str) -> tuple[Optional[int], Optional[int], Optional[int]]:
    """Extract beds, baths, cars from typical listing format."""
    beds = baths = cars = None

    bed_match = re.search(r"(\d+)\s*(?:bed|br|bedroom)", text, re.IGNORECASE)
    bath_match = re.search(r"(\d+)\s*(?:bath|bathroom)", text, re.IGNORECASE)
    car_match = re.search(r"(\d+)\s*(?:car|garage|parking)", text, re.IGNORECASE)

    if bed_match:
        beds = int(bed_match.group(1))
    if bath_match:
        baths = int(bath_match.group(1))
    if car_match:
        cars = int(car_match.group(1))

    return beds, baths, cars


def parse_land_size(text: str) -> Optional[float]:
    """Extract land size in sqm."""
    patterns = [
        re.compile(r"([\d,]+(?:\.\d+)?)\s*(?:sqm|m²|m2|square\s*met)", re.IGNORECASE),
        re.compile(r"land[:\s]*([\d,]+(?:\.\d+)?)\s*(?:sqm|m²|m2)?", re.IGNORECASE),
    ]
    for p in patterns:
        match = p.search(text)
        if match:
            return float(match.group(1).replace(",", ""))
    return None


# ── Address Parsing ──────────────────────────────────────────────────────────

AU_STATES = ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]


def parse_address_components(address: str) -> dict:
    """
    Parse an Australian address into components.
    Returns dict with suburb, state, postcode (best-effort).
    """
    result = {"suburb": "", "state": "", "postcode": ""}

    # Postcode
    pc_match = re.search(r"\b(\d{4})\b", address)
    if pc_match:
        result["postcode"] = pc_match.group(1)

    # State
    for state in AU_STATES:
        if re.search(rf"\b{state}\b", address, re.IGNORECASE):
            result["state"] = state
            break

    # Suburb — typically the word(s) before the state
    parts = re.split(r",\s*", address)
    if len(parts) >= 2:
        # Last part usually has state + postcode
        # Second-to-last is usually the suburb
        result["suburb"] = parts[-2].strip() if len(parts) >= 2 else parts[0].strip()

    return result


# ── Property Type Detection ──────────────────────────────────────────────────

TYPE_KEYWORDS = {
    PropertyType.HOUSE: ["house", "home", "cottage", "bungalow", "residence"],
    PropertyType.UNIT: ["unit", "flat"],
    PropertyType.APARTMENT: ["apartment", "apt"],
    PropertyType.TOWNHOUSE: ["townhouse", "town house", "terrace"],
    PropertyType.VILLA: ["villa"],
    PropertyType.LAND: ["land", "vacant land", "block"],
    PropertyType.DUPLEX: ["duplex", "dual occupancy"],
    PropertyType.RURAL: ["rural", "acreage", "farm", "farmlet"],
    PropertyType.COMMERCIAL: ["commercial", "retail", "office", "warehouse"],
}


def detect_property_type(text: str) -> PropertyType:
    """Detect property type from listing text."""
    text_lower = text.lower()
    for ptype, keywords in TYPE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return ptype
    return PropertyType.OTHER


# ── Distress Detection ───────────────────────────────────────────────────────

def detect_distress_signals(text: str) -> list[DistressSignal]:
    """Scan listing text for distress keywords and return signals with confidence."""
    if not text:
        return []

    signals = []
    text_lower = text.lower()

    for keyword in DISTRESS_KEYWORDS:
        if keyword.lower() in text_lower:
            # Higher confidence for more specific terms
            if keyword.lower() in ["deceased estate", "mortgagee", "mortgagee in possession"]:
                confidence = 0.95
            elif keyword.lower() in ["must sell", "urgent sale", "fire sale"]:
                confidence = 0.90
            elif keyword.lower() in ["price reduced", "price slashed"]:
                confidence = 0.85
            else:
                confidence = 0.70

            signals.append(DistressSignal(
                keyword=keyword,
                confidence=confidence,
                source="listing_text",
            ))

    return signals


# ── Condition Assessment ─────────────────────────────────────────────────────

def assess_condition(text: str) -> PropertyCondition:
    """Infer property condition from listing text."""
    text_lower = text.lower()

    knockdown = ["knockdown", "knock down", "demolish", "land value"]
    reno = ["renovator", "needs work", "handyman", "TLC", "dated", "original condition", "fixer"]
    fair = ["some updates", "partly renovated", "liveable"]
    good = ["well maintained", "good condition", "updated", "modern"]
    excellent = ["brand new", "luxury", "immaculate", "stunning", "designer", "architecturally"]

    for kw in knockdown:
        if kw in text_lower:
            return PropertyCondition.KNOCKDOWN_REBUILD
    for kw in reno:
        if kw in text_lower:
            return PropertyCondition.RENOVATION_REQUIRED
    for kw in excellent:
        if kw in text_lower:
            return PropertyCondition.EXCELLENT
    for kw in good:
        if kw in text_lower:
            return PropertyCondition.GOOD
    for kw in fair:
        if kw in text_lower:
            return PropertyCondition.FAIR

    return PropertyCondition.UNKNOWN


# ── Main HTML Cleaner ────────────────────────────────────────────────────────

class DataCleaner:
    """
    Transforms raw HTML listings into structured Property objects.

    Works with common real estate HTML structures — handles messy markup
    from boutique agency sites that don't follow any standard.
    """

    def clean_html_to_property(
        self,
        html: str,
        source: PropertySource = PropertySource.BOUTIQUE_AGENCY,
        source_url: str = "",
    ) -> Optional[Property]:
        """
        Parse raw HTML and extract a Property object.

        This is the basic rule-based extractor. For truly messy HTML,
        use the AI-powered extractor via the Scout agent.
        """
        try:
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text(separator=" ", strip=True)

            # Extract what we can
            price = parse_price(text)
            price_low, price_high = parse_price_range(text)
            beds, baths, cars = parse_beds_baths_cars(text)
            land_size = parse_land_size(text)
            prop_type = detect_property_type(text)
            distress = detect_distress_signals(text)
            condition = assess_condition(text)

            # Try to find the address from common selectors
            address = self._extract_address(soup) or "Address Unknown"
            components = parse_address_components(address)

            # Extract images
            images = self._extract_images(soup)

            # Extract agent info
            agent_name, agency_name, agent_phone = self._extract_agent_info(soup)

            return Property(
                address=address,
                suburb=components.get("suburb", ""),
                state=components.get("state", ""),
                postcode=components.get("postcode", "0000"),
                property_type=prop_type,
                bedrooms=beds,
                bathrooms=baths,
                car_spaces=cars,
                land_size_sqm=land_size,
                asking_price=price,
                price_guide_low=price_low,
                price_guide_high=price_high,
                listing_status=ListingStatus.ACTIVE,
                source=source,
                source_url=source_url,
                listing_text=text[:5000],  # Cap text length
                agent_name=agent_name,
                agent_phone=agent_phone,
                agency_name=agency_name,
                condition=condition,
                distress_signals=distress,
                image_urls=images[:20],  # Cap images
                raw_html=html,
            )

        except Exception as e:
            logger.error("html_cleaning_failed", error=str(e), url=source_url)
            return None

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Try common CSS selectors and meta tags for property address."""
        selectors = [
            "h1.property-address",
            "h1.listing-details__summary-title",
            "[data-testid='address']",
            ".property-info__address",
            "h1",
            'meta[property="og:title"]',
        ]
        for sel in selectors:
            if sel.startswith("meta"):
                tag = soup.select_one(sel)
                if tag and tag.get("content"):
                    return tag["content"]
            else:
                tag = soup.select_one(sel)
                if tag and tag.get_text(strip=True):
                    return tag.get_text(strip=True)
        return None

    def _extract_images(self, soup: BeautifulSoup) -> list[str]:
        """Extract property image URLs."""
        images = []
        for img in soup.find_all("img"):
            src = img.get("src", "") or img.get("data-src", "")
            if src and any(kw in src.lower() for kw in ["property", "listing", "photo", "image"]):
                if src.startswith("//"):
                    src = "https:" + src
                if src.startswith("http"):
                    images.append(src)
        return images

    def _extract_agent_info(self, soup: BeautifulSoup) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract agent name, agency, and phone from common selectors."""
        agent_name = None
        agency_name = None
        agent_phone = None

        agent_selectors = [".agent-name", ".listing-agent__name", "[data-testid='agent-name']"]
        for sel in agent_selectors:
            tag = soup.select_one(sel)
            if tag:
                agent_name = tag.get_text(strip=True)
                break

        agency_selectors = [".agency-name", ".listing-agent__agency", "[data-testid='agency-name']"]
        for sel in agency_selectors:
            tag = soup.select_one(sel)
            if tag:
                agency_name = tag.get_text(strip=True)
                break

        # Phone
        phone_match = re.search(r"(?:0[2-9]\d{2}\s?\d{3}\s?\d{3}|04\d{2}\s?\d{3}\s?\d{3})", soup.get_text())
        if phone_match:
            agent_phone = phone_match.group()

        return agent_name, agency_name, agent_phone
