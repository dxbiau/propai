"""
Council Development Application (DA) Scraper.

Monitors council planning portals to find Development Applications
that signal upcoming property activity — subdivision, demolition,
new builds, and conversions.

These are PRE-MARKET signals: properties that will likely be listed
or flipped before they appear on any portal.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import structlog

from nexusprop.tools.scraper import ScraperClient, PlaywrightScraper

logger = structlog.get_logger(__name__)


@dataclass
class DevelopmentApplication:
    """A Development Application from a council planning portal."""
    da_number: str
    address: str
    suburb: str
    state: str
    postcode: str
    description: str
    applicant: Optional[str] = None
    lodged_date: Optional[datetime] = None
    determined_date: Optional[datetime] = None
    status: str = "pending"  # pending, approved, rejected, withdrawn
    estimated_value: Optional[float] = None
    da_type: str = "other"  # subdivision, demolition, new_build, renovation, change_of_use
    council: str = ""
    source_url: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def is_investment_signal(self) -> bool:
        """Is this DA likely to indicate an investment opportunity?"""
        signal_types = {"subdivision", "demolition", "new_build", "change_of_use"}
        return self.da_type in signal_types

    @property
    def signal_strength(self) -> str:
        """How strong a property signal is this DA?"""
        desc_lower = self.description.lower()
        if any(kw in desc_lower for kw in ["subdivision", "subdivide", "lot boundary"]):
            return "STRONG — Likely subdivision or sale"
        if any(kw in desc_lower for kw in ["demolition", "demolish"]):
            return "STRONG — Knockdown rebuild or development"
        if any(kw in desc_lower for kw in ["dual occupancy", "duplex", "secondary dwelling"]):
            return "MODERATE — Value-add potential"
        if any(kw in desc_lower for kw in ["renovation", "alteration", "extension"]):
            return "WEAK — Renovation (existing owner)"
        return "NEUTRAL"


# DA type detection keywords
DA_TYPE_KEYWORDS = {
    "subdivision": ["subdivision", "subdivide", "lot boundary", "strata subdivision", "torrens title"],
    "demolition": ["demolition", "demolish", "knockdown"],
    "new_build": ["new dwelling", "new house", "construction of", "erection of"],
    "renovation": ["renovation", "alteration", "extension", "addition", "modification"],
    "change_of_use": ["change of use", "boarding house", "dual occupancy", "secondary dwelling", "granny flat"],
}


def classify_da_type(description: str) -> str:
    """Classify a DA based on its description text."""
    desc_lower = description.lower()
    for da_type, keywords in DA_TYPE_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return da_type
    return "other"


class CouncilDAScraper:
    """
    Scrapes council Development Application portals.

    Currently supports:
    - NSW councils (via ePlanning portal patterns)
    - VIC councils (via planning register patterns)
    - QLD councils (via development.i patterns)

    Each council has slightly different HTML structure, but the
    AI extractor handles the variation.
    """

    def __init__(self):
        self.http = ScraperClient(max_concurrent=3, delay_range=(2.0, 5.0))
        self.browser = PlaywrightScraper()

    async def scrape_council(
        self,
        council_url: str,
        council_name: str,
        state: str,
        suburb_filter: Optional[str] = None,
        use_browser: bool = True,
    ) -> list[DevelopmentApplication]:
        """
        Scrape a council DA portal and return structured DA data.

        Args:
            council_url: URL of the council's DA tracker/register
            council_name: Name of the council
            state: State (NSW, VIC, QLD, etc.)
            suburb_filter: Optional suburb to filter results
            use_browser: Use Playwright (most council sites need JS rendering)
        """
        logger.info("scraping_council_da", council=council_name, url=council_url)

        try:
            if use_browser:
                await self.browser.start()
                html = await self.browser.fetch(
                    council_url,
                    wait_ms=5000,  # Council sites are slow
                )
            else:
                html = await self.http.fetch(council_url)

            das = self._parse_das(html, council_name, state)

            # Filter by suburb if specified
            if suburb_filter:
                das = [da for da in das if suburb_filter.lower() in da.suburb.lower()]

            # Filter to investment-relevant DAs only
            das = [da for da in das if da.is_investment_signal]

            logger.info("council_da_scraped", council=council_name, das_found=len(das))
            return das

        except Exception as e:
            logger.error("council_da_scrape_failed", council=council_name, error=str(e))
            return []

    def _parse_das(
        self,
        html: str,
        council_name: str,
        state: str,
    ) -> list[DevelopmentApplication]:
        """Parse DA data from HTML — generic parser with common patterns."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        das = []

        # Common DA table patterns
        rows = soup.select("tr.da-row, tr.application-row, .da-item, .application-item")

        if not rows:
            # Try generic table rows
            tables = soup.select("table")
            for table in tables:
                rows = table.select("tr")[1:]  # Skip header
                break

        for row in rows:
            try:
                text = row.get_text(separator=" ", strip=True)

                # Extract DA number
                da_num_match = re.search(r"(DA[\s-]?\d{2,}[\s/-]?\d{2,}(?:[\s/-]?\d+)?)", text, re.IGNORECASE)
                da_number = da_num_match.group(1) if da_num_match else f"DA-{len(das)+1}"

                # Extract address
                addr_match = re.search(r"(\d+[A-Za-z]?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Crescent|Cres|Way|Boulevard|Blvd))", text)
                address = addr_match.group(1) if addr_match else ""

                # Extract suburb
                suburb = ""
                postcode = ""
                pc_match = re.search(r"\b(\d{4})\b", text)
                if pc_match:
                    postcode = pc_match.group(1)

                # Extract description
                description = text[:300]

                # Classify DA type
                da_type = classify_da_type(description)

                # Extract estimated value
                value_match = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", text)
                estimated_value = float(value_match.group(1).replace(",", "")) if value_match else None

                da = DevelopmentApplication(
                    da_number=da_number,
                    address=address or "Address not parsed",
                    suburb=suburb,
                    state=state,
                    postcode=postcode,
                    description=description,
                    da_type=da_type,
                    estimated_value=estimated_value,
                    council=council_name,
                )

                das.append(da)

            except Exception as e:
                logger.debug("da_parse_row_failed", error=str(e))
                continue

        return das

    async def cleanup(self):
        await self.http.close()
        await self.browser.stop()
