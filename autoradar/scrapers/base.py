import asyncio
import logging
import os
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logger = logging.getLogger(__name__)

# Realistic User-Agent strings for Estonian users
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


@dataclass
class CarListing:
    """Represents a single car listing from any portal."""

    portal: str
    external_id: str
    url: str
    title: str
    price: int | None = None
    year: int | None = None
    mileage: int | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    body_type: str | None = None
    engine_volume: int | None = None
    power_kw: int | None = None
    drive_type: str | None = None
    color: str | None = None
    location: str | None = None
    seller_type: str | None = None
    image_url: str | None = None
    reg_number: str | None = None
    raw_data: dict = field(default_factory=dict)


class BaseScraper(ABC):
    """Base class for all portal scrapers."""

    PORTAL_NAME: str = ""

    def __init__(self):
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._playwright = None

    @staticmethod
    def _find_chromium() -> str | None:
        """Find installed Chromium executable."""
        # Check Playwright's default cache locations
        cache_dir = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", Path.home() / ".cache" / "ms-playwright"))
        if cache_dir.exists():
            # Find any chromium installation (sorted descending to get newest)
            for chromium_dir in sorted(cache_dir.glob("chromium-*"), reverse=True):
                chrome_path = chromium_dir / "chrome-linux" / "chrome"
                if chrome_path.exists():
                    return str(chrome_path)
        return None

    async def start(self):
        """Initialize the browser."""
        self._playwright = await async_playwright().start()

        launch_kwargs = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        }

        # Use pre-installed chromium if Playwright's expected version doesn't exist
        chromium_path = self._find_chromium()
        if chromium_path:
            launch_kwargs["executable_path"] = chromium_path

        self._browser = await self._playwright.chromium.launch(**launch_kwargs)
        await self._create_context()
        logger.info(f"[{self.PORTAL_NAME}] Browser started")

    async def _create_context(self):
        """Create a browser context with stealth settings."""
        ua = random.choice(USER_AGENTS)
        self._context = await self._browser.new_context(
            user_agent=ua,
            viewport={"width": 1920, "height": 1080},
            locale="et-EE",
            timezone_id="Europe/Tallinn",
            java_script_enabled=True,
        )
        # Stealth: override webdriver detection
        await self._context.add_init_script("""
            // Remove webdriver flag
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

            // Override plugins to look realistic
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['et-EE', 'et', 'en-US', 'en'],
            });

            // Override platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32',
            });

            // Chrome runtime mock
            window.chrome = { runtime: {} };
        """)

    async def stop(self):
        """Close the browser."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info(f"[{self.PORTAL_NAME}] Browser stopped")

    async def _new_page(self) -> Page:
        """Create a new page in the current context."""
        page = await self._context.new_page()
        return page

    async def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Wait a random amount of time to mimic human behavior."""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)

    @abstractmethod
    async def scrape(self, params: dict) -> list[CarListing]:
        """Scrape listings matching the given search parameters.

        Args:
            params: Search parameters dict, e.g.:
                {
                    "brand": "bmw",
                    "model": "3",
                    "price_min": 0,
                    "price_max": 15000,
                    "year_min": 2015,
                    "year_max": 2024,
                    "fuel_type": "diesel",
                    "transmission": "automatic",
                    ...
                }

        Returns:
            List of CarListing objects found.
        """
        ...

    @abstractmethod
    def build_search_url(self, params: dict) -> str:
        """Build the search URL from parameters."""
        ...
