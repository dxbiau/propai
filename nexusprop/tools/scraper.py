"""
Scraper utilities — bot-detection-resistant HTTP & browser automation.

Provides both lightweight (httpx) and heavyweight (Playwright) scraping,
with automatic retry, rate limiting, and proxy rotation.
"""

from __future__ import annotations

import asyncio
import random
from typing import Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from nexusprop.config.settings import get_settings

logger = structlog.get_logger(__name__)

# Rotating User-Agents for stealth
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:133.0) Gecko/20100101 Firefox/133.0",
]


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


def _default_headers() -> dict[str, str]:
    return {
        "User-Agent": _random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-AU,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


class ScraperClient:
    """Lightweight async HTTP scraper with stealth headers and retry logic."""

    def __init__(
        self,
        timeout: float = 30.0,
        max_concurrent: int = 5,
        delay_range: tuple[float, float] = (1.0, 3.0),
    ):
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay_range = delay_range
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            settings = get_settings()
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=_default_headers(),
                limits=httpx.Limits(
                    max_connections=settings.max_concurrent_scrapers * 2,
                    max_keepalive_connections=settings.max_concurrent_scrapers,
                ),
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def fetch(self, url: str, headers: Optional[dict] = None) -> str:
        """Fetch a URL and return the HTML content."""
        async with self.semaphore:
            # Random delay for stealth
            delay = random.uniform(*self.delay_range)
            await asyncio.sleep(delay)

            client = await self._get_client()
            merged_headers = {**_default_headers(), **(headers or {})}

            logger.info("scraping_url", url=url)
            response = await client.get(url, headers=merged_headers)
            response.raise_for_status()

            logger.info("scrape_success", url=url, status=response.status_code, size=len(response.text))
            return response.text

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def fetch_json(self, url: str, headers: Optional[dict] = None) -> dict:
        """Fetch a URL and return parsed JSON."""
        async with self.semaphore:
            delay = random.uniform(*self.delay_range)
            await asyncio.sleep(delay)

            client = await self._get_client()
            merged_headers = {**_default_headers(), **(headers or {})}
            merged_headers["Accept"] = "application/json"

            response = await client.get(url, headers=merged_headers)
            response.raise_for_status()
            return response.json()

    async def fetch_many(self, urls: list[str]) -> list[tuple[str, Optional[str]]]:
        """Fetch multiple URLs concurrently. Returns list of (url, html_or_none)."""
        results = []

        async def _fetch_one(url: str):
            try:
                html = await self.fetch(url)
                results.append((url, html))
            except Exception as e:
                logger.warning("scrape_failed", url=url, error=str(e))
                results.append((url, None))

        await asyncio.gather(*[_fetch_one(u) for u in urls])
        return results


class PlaywrightScraper:
    """
    Heavy-duty browser-based scraper for JS-rendered pages and bot-protected sites.

    Uses Playwright for full browser automation — bypass Cloudflare, render SPAs, etc.
    """

    def __init__(self):
        self._browser = None
        self._playwright = None

    async def start(self):
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        logger.info("playwright_browser_started")

    async def stop(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("playwright_browser_stopped")

    async def fetch(
        self,
        url: str,
        wait_selector: Optional[str] = None,
        wait_ms: int = 3000,
        screenshot: bool = False,
    ) -> str:
        """
        Navigate to a URL with a real browser and return the rendered HTML.

        Args:
            url: Target URL
            wait_selector: CSS selector to wait for before extracting HTML
            wait_ms: Additional wait time in ms after page load
            screenshot: If True, save a screenshot for debugging
        """
        if not self._browser:
            await self.start()

        context = await self._browser.new_context(
            user_agent=_random_ua(),
            viewport={"width": 1920, "height": 1080},
            locale="en-AU",
            timezone_id="Australia/Sydney",
        )
        page = await context.new_page()

        try:
            # Stealth: remove webdriver flag
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)

            logger.info("playwright_navigating", url=url)
            await page.goto(url, wait_until="networkidle", timeout=30000)

            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=10000)

            await page.wait_for_timeout(wait_ms)

            html = await page.content()
            logger.info("playwright_success", url=url, size=len(html))

            if screenshot:
                await page.screenshot(path=f"debug_screenshot.png", full_page=True)

            return html
        finally:
            await page.close()
            await context.close()

    async def fetch_with_interaction(
        self,
        url: str,
        actions: list[dict],
    ) -> str:
        """
        Navigate to a page and perform interactions (click, type, scroll) before extracting.

        actions: list of dicts like:
            {"action": "click", "selector": "#load-more"}
            {"action": "type", "selector": "#search", "text": "Sydney"}
            {"action": "scroll", "amount": 3000}
            {"action": "wait", "ms": 2000}
        """
        if not self._browser:
            await self.start()

        context = await self._browser.new_context(
            user_agent=_random_ua(),
            viewport={"width": 1920, "height": 1080},
            locale="en-AU",
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            for act in actions:
                if act["action"] == "click":
                    await page.click(act["selector"])
                elif act["action"] == "type":
                    await page.fill(act["selector"], act["text"])
                elif act["action"] == "scroll":
                    await page.evaluate(f"window.scrollBy(0, {act['amount']})")
                elif act["action"] == "wait":
                    await page.wait_for_timeout(act.get("ms", 1000))

                # Small random delay between actions
                await page.wait_for_timeout(random.randint(300, 800))

            html = await page.content()
            return html
        finally:
            await page.close()
            await context.close()


class ZenRowsScraper:
    """
    ZenRows API-based scraper for heavily protected sites.

    ZenRows handles proxies, CAPTCHAs, and JS rendering server-side.
    """

    BASE_URL = "https://api.zenrows.com/v1/"

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def fetch(
        self,
        url: str,
        js_render: bool = True,
        premium_proxy: bool = False,
    ) -> str:
        """Fetch a URL through ZenRows API."""
        if not self.settings.zenrows_api_key:
            raise ValueError("ZENROWS_API_KEY not configured")

        client = await self._get_client()
        params = {
            "url": url,
            "apikey": self.settings.zenrows_api_key,
            "js_render": str(js_render).lower(),
        }
        if premium_proxy:
            params["premium_proxy"] = "true"
            params["proxy_country"] = "au"

        response = await client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.text

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
