"""
Public Notices Scraper — deceased estates, mortgagee sales, court listings.

Monitors public notices for life events that create motivated sellers:
- Deceased estates (probate notices)
- Mortgagee in possession sales
- Bankruptcy/insolvency notices
- Family court property settlements

These are the highest-distress signals and represent the best buying opportunities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

import structlog

from nexusprop.tools.scraper import ScraperClient

logger = structlog.get_logger(__name__)


class NoticeType(str, Enum):
    DECEASED_ESTATE = "deceased_estate"
    MORTGAGEE_SALE = "mortgagee_sale"
    BANKRUPTCY = "bankruptcy"
    COURT_ORDER = "court_order"
    LIQUIDATION = "liquidation"
    OTHER = "other"


@dataclass
class PublicNotice:
    """A public notice that may indicate a property sale opportunity."""
    notice_type: NoticeType
    title: str
    description: str
    published_date: Optional[datetime] = None
    source_url: str = ""
    source_name: str = ""
    state: str = ""
    suburb: Optional[str] = None
    address: Optional[str] = None
    contact_details: Optional[str] = None
    deadline_date: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)

    @property
    def urgency(self) -> str:
        """How urgent is this notice for property hunters?"""
        if self.notice_type == NoticeType.MORTGAGEE_SALE:
            return "CRITICAL — Mortgagee sales are time-sensitive and below market"
        elif self.notice_type == NoticeType.DECEASED_ESTATE:
            return "HIGH — Estate sales often go below market for quick disposal"
        elif self.notice_type == NoticeType.BANKRUPTCY:
            return "HIGH — Court-ordered sales must proceed"
        elif self.notice_type == NoticeType.COURT_ORDER:
            return "MODERATE — May lead to forced sale"
        return "LOW"


# Sources for public notices in Australia
PUBLIC_NOTICE_SOURCES = [
    {
        "name": "NSW Government Gazette",
        "state": "NSW",
        "url": "https://gazette.legislation.nsw.gov.au/",
        "types": [NoticeType.DECEASED_ESTATE, NoticeType.COURT_ORDER],
    },
    {
        "name": "Victoria Government Gazette",
        "state": "VIC",
        "url": "https://www.gazette.vic.gov.au/",
        "types": [NoticeType.DECEASED_ESTATE, NoticeType.COURT_ORDER],
    },
    {
        "name": "QLD Government Gazette",
        "state": "QLD",
        "url": "https://www.publications.qld.gov.au/gazette",
        "types": [NoticeType.DECEASED_ESTATE],
    },
    {
        "name": "ASIC Published Notices",
        "state": "ALL",
        "url": "https://publishednotices.asic.gov.au/",
        "types": [NoticeType.LIQUIDATION, NoticeType.BANKRUPTCY],
    },
    {
        "name": "Federal Court of Australia",
        "state": "ALL",
        "url": "https://www.fedcourt.gov.au/",
        "types": [NoticeType.BANKRUPTCY, NoticeType.COURT_ORDER],
    },
]


class PublicNoticeScraper:
    """
    Scrapes public notices for deceased estates, mortgagee sales,
    and other events that create motivated sellers.
    """

    def __init__(self):
        self.http = ScraperClient(max_concurrent=2, delay_range=(3.0, 6.0))

    async def scrape_all_sources(
        self,
        target_states: Optional[list[str]] = None,
        notice_types: Optional[list[NoticeType]] = None,
    ) -> list[PublicNotice]:
        """
        Scrape all configured public notice sources.

        Args:
            target_states: Filter by state
            notice_types: Filter by notice type
        """
        logger.info("scraping_public_notices", states=target_states, types=notice_types)

        sources = PUBLIC_NOTICE_SOURCES
        if target_states:
            state_set = {s.upper() for s in target_states}
            state_set.add("ALL")  # Always include national sources
            sources = [s for s in sources if s["state"] in state_set]

        all_notices: list[PublicNotice] = []

        for source in sources:
            try:
                notices = await self._scrape_source(source)
                all_notices.extend(notices)
                logger.info("public_notice_source_scraped", source=source["name"], found=len(notices))
            except Exception as e:
                logger.warning("public_notice_source_failed", source=source["name"], error=str(e))

        # Filter by type if specified
        if notice_types:
            all_notices = [n for n in all_notices if n.notice_type in notice_types]

        logger.info("public_notices_complete", total=len(all_notices))
        return all_notices

    async def _scrape_source(self, source: dict) -> list[PublicNotice]:
        """Scrape a single public notice source."""
        html = await self.http.fetch(source["url"])

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")

        notices = []
        # Generic notice extraction — each source has different HTML
        # The AI extractor can be used for complex sources
        text = soup.get_text(separator="\n", strip=True)

        # Search for property-related keywords in the text
        import re
        property_keywords = [
            r"(?:deceased\s+estate|estate\s+of\s+the\s+late)",
            r"(?:mortgagee\s+(?:in\s+possession|sale))",
            r"(?:bankrupt(?:cy)?|insolvency)",
            r"(?:property\s+(?:for\s+)?sale|real\s+property)",
            r"(?:probate|letters?\s+of\s+administration)",
        ]

        for keyword_pattern in property_keywords:
            matches = re.finditer(keyword_pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]

                # Determine notice type
                notice_type = self._classify_notice(match.group())

                notice = PublicNotice(
                    notice_type=notice_type,
                    title=match.group().strip().title(),
                    description=context.strip(),
                    source_url=source["url"],
                    source_name=source["name"],
                    state=source["state"] if source["state"] != "ALL" else "",
                )
                notices.append(notice)

        return notices

    def _classify_notice(self, text: str) -> NoticeType:
        """Classify a notice based on its text."""
        text_lower = text.lower()
        if "deceased" in text_lower or "estate of the late" in text_lower or "probate" in text_lower:
            return NoticeType.DECEASED_ESTATE
        elif "mortgagee" in text_lower:
            return NoticeType.MORTGAGEE_SALE
        elif "bankrupt" in text_lower or "insolvency" in text_lower:
            return NoticeType.BANKRUPTCY
        elif "liquidat" in text_lower:
            return NoticeType.LIQUIDATION
        elif "court" in text_lower:
            return NoticeType.COURT_ORDER
        return NoticeType.OTHER

    async def cleanup(self):
        await self.http.close()
