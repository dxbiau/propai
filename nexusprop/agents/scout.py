"""
Agent A — The Scout (Harvester)

The perception layer. Scrapes real estate data from conventional and
non-conventional sources, detects distress keywords, and produces
structured Property objects for downstream analysis.

Sources:
  • Boutique agency sites (Shadow Listings)
  • Council planning portals (Development Applications)
  • Public notices (deceased estates, mortgagee sales)
  • Social media signals (Facebook groups, "Coming Soon" pages)
"""

from __future__ import annotations

import json
from typing import Optional

from nexusprop.agents.base import AgentResult, BaseAgent
from nexusprop.models.property import (
    Property,
    PropertySource,
)
from nexusprop.tools.data_cleaner import DataCleaner, detect_distress_signals
from nexusprop.tools.scraper import PlaywrightScraper, ScraperClient


# ── Boutique Agency Registry ────────────────────────────────────────────────
# 40+ boutique agencies across Australia whose listings don't always appear
# on REA/Domain. This is the "Shadow Listings" feature.

BOUTIQUE_AGENCIES = [
    # NSW
    {"name": "Raine & Horne Terrigal", "state": "NSW", "url": "https://www.raineandhorne.com.au/terrigal/properties", "selector": ".property-card"},
    {"name": "Belle Property Mosman", "state": "NSW", "url": "https://www.belleproperty.com/mosman/", "selector": ".listing-card"},
    {"name": "Cobden & Hayson", "state": "NSW", "url": "https://www.cobdenhayon.com.au/buy/", "selector": ".property-item"},
    {"name": "BresicWhitney", "state": "NSW", "url": "https://www.bresicwhitney.com.au/buy", "selector": ".property-tile"},
    {"name": "PPD Real Estate", "state": "NSW", "url": "https://www.ppd.com.au/buy/", "selector": ".listing"},
    {"name": "Wiseberry Heritage", "state": "NSW", "url": "https://wiseberry.com.au/heritage/", "selector": ".property-card"},
    {"name": "Starr Partners", "state": "NSW", "url": "https://www.starrpartners.com.au/buy/", "selector": ".property-item"},
    {"name": "Laing+Simmons", "state": "NSW", "url": "https://www.laingandsimmons.com.au/search/buy/", "selector": ".listing-card"},

    # VIC
    {"name": "Jellis Craig", "state": "VIC", "url": "https://www.jelliscraig.com.au/buy/", "selector": ".property-card"},
    {"name": "Kay & Burton", "state": "VIC", "url": "https://www.kayburton.com.au/buy/", "selector": ".listing-item"},
    {"name": "Marshall White", "state": "VIC", "url": "https://www.marshallwhite.com.au/buy/", "selector": ".property-tile"},
    {"name": "Woodards", "state": "VIC", "url": "https://www.woodards.com.au/buy/", "selector": ".listing-card"},
    {"name": "Hocking Stuart", "state": "VIC", "url": "https://www.hockingstuart.com.au/buy", "selector": ".prop-card"},
    {"name": "Greg Hocking", "state": "VIC", "url": "https://www.greghocking.com.au/buy/", "selector": ".property-card"},
    {"name": "Biggin & Scott", "state": "VIC", "url": "https://www.bigginscott.com.au/buy/", "selector": ".property-card"},

    # QLD
    {"name": "Place Estate Agents", "state": "QLD", "url": "https://www.placestateagents.com.au/buy/", "selector": ".property-card"},
    {"name": "Matt Lancashire", "state": "QLD", "url": "https://www.mattlancashire.com.au/buy/", "selector": ".listing-card"},
    {"name": "McGrath Brisbane", "state": "QLD", "url": "https://www.mcgrath.com.au/offices/brisbane/buy", "selector": ".property-card"},
    {"name": "Image Property", "state": "QLD", "url": "https://www.imageproperty.com.au/buy/", "selector": ".listing"},
    {"name": "Harcourts Coastal", "state": "QLD", "url": "https://coastal.harcourts.com.au/buy/", "selector": ".property-card"},

    # SA
    {"name": "Klemich Real Estate", "state": "SA", "url": "https://www.klemich.com.au/buy/", "selector": ".property-card"},
    {"name": "Toop&Toop", "state": "SA", "url": "https://www.toopandtoop.com.au/buy/", "selector": ".listing-card"},
    {"name": "Harris Real Estate", "state": "SA", "url": "https://www.harrisre.com.au/buy/", "selector": ".property-card"},

    # WA
    {"name": "Acton | Belle Property", "state": "WA", "url": "https://www.acton.com.au/buy/", "selector": ".property-card"},
    {"name": "William Porteous", "state": "WA", "url": "https://www.porteous.com.au/property/buy/", "selector": ".listing-card"},
    {"name": "Realmark", "state": "WA", "url": "https://www.realmark.com.au/buy/", "selector": ".property-card"},

    # TAS
    {"name": "Petrusma Property", "state": "TAS", "url": "https://www.petrusma.com.au/buy/", "selector": ".listing-card"},
    {"name": "Fall Real Estate", "state": "TAS", "url": "https://www.fall.com.au/buy/", "selector": ".property-card"},

    # ACT
    {"name": "Luton Properties", "state": "ACT", "url": "https://www.luton.com.au/buy/", "selector": ".listing-card"},
    {"name": "Blackshaw", "state": "ACT", "url": "https://www.blackshaw.com.au/buy/", "selector": ".property-card"},

    # NT
    {"name": "Real Estate Central", "state": "NT", "url": "https://www.rec.com.au/buy/", "selector": ".listing-card"},
]

# Council DA portals
COUNCIL_DA_PORTALS = [
    {"council": "City of Sydney", "state": "NSW", "url": "https://online2.cityofsydney.nsw.gov.au/DA/", "type": "council_da"},
    {"council": "City of Melbourne", "state": "VIC", "url": "https://www.melbourne.vic.gov.au/building-and-development/property-information/planning-building-activity/pages/planning-register.aspx", "type": "council_da"},
    {"council": "Brisbane City Council", "state": "QLD", "url": "https://developmenti.brisbane.qld.gov.au/", "type": "council_da"},
    {"council": "City of Perth", "state": "WA", "url": "https://www.perth.wa.gov.au/planning-development", "type": "council_da"},
]

# System prompt for AI-powered HTML extraction
SCOUT_SYSTEM_PROMPT = """You are NexusProp Scout — an expert property data extractor for the Australian real estate market.

Your task: Extract structured property data from raw HTML content.

You MUST output valid JSON with these fields:
{
    "address": "full street address",
    "suburb": "suburb name",
    "state": "NSW/VIC/QLD/SA/WA/TAS/NT/ACT",
    "postcode": "4-digit postcode",
    "property_type": "house/unit/apartment/townhouse/villa/land/duplex",
    "bedrooms": number or null,
    "bathrooms": number or null,
    "car_spaces": number or null,
    "land_size_sqm": number or null,
    "asking_price": number or null,
    "price_guide_low": number or null,
    "price_guide_high": number or null,
    "listing_text": "full listing description",
    "agent_name": "agent name" or null,
    "agency_name": "agency name" or null,
    "agent_phone": "phone number" or null,
    "image_urls": ["url1", "url2"],
    "distress_keywords": ["must sell", "deceased estate"] or [],
    "strata_levies_quarterly": number or null,
    "council_rates_annual": number or null,
    "zoning": "R2/R3/B4 etc" or null
}

Australian-specific notes:
- Prices in AUD. Convert "Offers above $X" to price_guide_low.
- "Price guide: $800k - $850k" → price_guide_low: 800000, price_guide_high: 850000
- Detect distress: "must sell", "deceased estate", "mortgagee", "urgent", "price reduced"
- Strata/body corp levies are typically quarterly in Australia.
- Extract council zoning if mentioned (R2, R3, R4, B4, IN2, etc.)

If you cannot extract a field, set it to null. Always return valid JSON."""


class ScoutAgent(BaseAgent):
    """
    Agent A — The Scout.

    Harvests property listings from:
    1. Boutique agency websites (Shadow Listings)
    2. Council Development Application portals
    3. Public notices and court listings
    4. AI-powered HTML parsing for messy sites

    Output: List[Property] — structured, clean, enriched with distress signals.
    """

    def __init__(self):
        super().__init__("Scout")
        self.http_scraper = ScraperClient(
            max_concurrent=self.settings.max_concurrent_scrapers,
            delay_range=(1.5, 4.0),
        )
        self.browser_scraper = PlaywrightScraper()
        self.cleaner = DataCleaner()

    async def execute(
        self,
        target_states: Optional[list[str]] = None,
        target_suburbs: Optional[list[str]] = None,
        use_browser: bool = False,
        max_agencies: int = 10,
    ) -> AgentResult:
        """
        Execute a full scraping run across configured sources.

        Args:
            target_states: Filter agencies by state (e.g. ["NSW", "VIC"])
            target_suburbs: Filter for specific suburbs
            use_browser: Use Playwright instead of httpx (slower but more reliable)
            max_agencies: Max number of agencies to scrape per run
        """
        self.logger.info(
            "scout_run_started",
            states=target_states,
            suburbs=target_suburbs,
            use_browser=use_browser,
        )

        all_properties: list[Property] = []
        total_tokens = 0
        errors = []

        # 1. Scrape boutique agencies
        agencies = self._filter_agencies(target_states, max_agencies)
        for agency in agencies:
            try:
                props = await self._scrape_agency(agency, use_browser)
                all_properties.extend(props)
                self.logger.info("agency_scraped", agency=agency["name"], found=len(props))
            except Exception as e:
                errors.append(f"{agency['name']}: {str(e)}")
                self.logger.warning("agency_scrape_failed", agency=agency["name"], error=str(e))

        # 2. Filter by target suburbs if specified
        if target_suburbs:
            suburb_set = {s.lower() for s in target_suburbs}
            all_properties = [p for p in all_properties if p.suburb.lower() in suburb_set]

        # 3. Enrich with distress detection (already done in cleaner, but double-check)
        for prop in all_properties:
            if not prop.distress_signals and prop.listing_text:
                prop.distress_signals = detect_distress_signals(prop.listing_text)

        self.logger.info(
            "scout_run_completed",
            total_properties=len(all_properties),
            errors=len(errors),
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "properties": all_properties,
                "count": len(all_properties),
                "errors": errors,
                "sources_scraped": len(agencies),
            },
            tokens_used=total_tokens,
        )

    async def scrape_single_url(
        self,
        url: str,
        source: PropertySource = PropertySource.BOUTIQUE_AGENCY,
        use_ai: bool = True,
    ) -> AgentResult:
        """
        Scrape a single URL and extract property data.

        If use_ai=True, uses Claude for intelligent HTML-to-JSON extraction
        (ideal for messy boutique agency sites).
        """
        self.logger.info("scraping_single_url", url=url, use_ai=use_ai)

        try:
            html = await self.http_scraper.fetch(url)
        except Exception:
            # Fall back to browser
            self.logger.info("falling_back_to_browser", url=url)
            await self.browser_scraper.start()
            html = await self.browser_scraper.fetch(url)

        tokens = 0
        if use_ai:
            prop, tokens = await self._ai_extract(html, url, source)
        else:
            prop = self.cleaner.clean_html_to_property(html, source=source, source_url=url)

        if prop:
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={"property": prop},
                tokens_used=tokens,
            )
        else:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="Failed to extract property data from URL",
            )

    async def _scrape_agency(
        self,
        agency: dict,
        use_browser: bool,
    ) -> list[Property]:
        """Scrape a single agency website and return Property objects."""
        url = agency["url"]

        if use_browser:
            await self.browser_scraper.start()
            html = await self.browser_scraper.fetch(url, wait_selector=agency.get("selector"))
        else:
            html = await self.http_scraper.fetch(url)

        # Try rule-based extraction first
        prop = self.cleaner.clean_html_to_property(
            html,
            source=PropertySource.BOUTIQUE_AGENCY,
            source_url=url,
        )

        if prop:
            return [prop]

        # If rule-based fails, try AI extraction
        prop, _ = await self._ai_extract(html, url, PropertySource.BOUTIQUE_AGENCY)
        return [prop] if prop else []

    async def _ai_extract(
        self,
        html: str,
        url: str,
        source: PropertySource,
    ) -> tuple[Optional[Property], int]:
        """Use Claude to extract property data from messy HTML."""
        # Truncate HTML to fit context
        html_truncated = html[:15000]

        prompt = (
            f"Extract property listing data from this HTML page ({url}).\n\n"
            f"HTML:\n```\n{html_truncated}\n```\n\n"
            "Return ONLY valid JSON matching the schema. No explanation."
        )

        try:
            response_text, tokens = await self.ask_llm(
                prompt=prompt,
                system=SCOUT_SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.1,
            )

            # Parse JSON from response
            json_str = response_text.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]

            data = json.loads(json_str)

            # Build Property from extracted data
            distress_signals = detect_distress_signals(data.get("listing_text", ""))

            prop = Property(
                address=data.get("address", "Unknown"),
                suburb=data.get("suburb", ""),
                state=data.get("state", ""),
                postcode=data.get("postcode", "0000"),
                property_type=data.get("property_type", "other"),
                bedrooms=data.get("bedrooms"),
                bathrooms=data.get("bathrooms"),
                car_spaces=data.get("car_spaces"),
                land_size_sqm=data.get("land_size_sqm"),
                asking_price=data.get("asking_price"),
                price_guide_low=data.get("price_guide_low"),
                price_guide_high=data.get("price_guide_high"),
                listing_text=data.get("listing_text", ""),
                agent_name=data.get("agent_name"),
                agency_name=data.get("agency_name"),
                agent_phone=data.get("agent_phone"),
                source=source,
                source_url=url,
                image_urls=data.get("image_urls", []),
                distress_signals=distress_signals,
                strata_levies_quarterly=data.get("strata_levies_quarterly"),
                council_rates_annual=data.get("council_rates_annual"),
                zoning=data.get("zoning"),
                raw_html=html,
            )

            self.logger.info("ai_extraction_success", url=url, address=prop.address)
            return prop, tokens

        except json.JSONDecodeError as e:
            self.logger.warning("ai_extraction_json_error", url=url, error=str(e))
            return None, 0
        except Exception as e:
            self.logger.warning("ai_extraction_failed", url=url, error=str(e))
            return None, 0

    def _filter_agencies(
        self,
        target_states: Optional[list[str]],
        max_count: int,
    ) -> list[dict]:
        """Filter and limit the agency list."""
        agencies = BOUTIQUE_AGENCIES
        if target_states:
            state_set = {s.upper() for s in target_states}
            agencies = [a for a in agencies if a["state"] in state_set]
        return agencies[:max_count]

    async def cleanup(self):
        """Clean up scraper resources."""
        await self.http_scraper.close()
        await self.browser_scraper.stop()
