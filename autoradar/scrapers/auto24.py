import logging
import re
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)

# auto24.ee brand codes (b parameter) - most common brands
# Full list needs to be scraped from the search form dropdown
BRAND_CODES = {
    "audi": 2,
    "bmw": 4,
    "citroen": 20,
    "dacia": 254,
    "fiat": 14,
    "ford": 7,
    "honda": 1,
    "hyundai": 34,
    "jaguar": 36,
    "kia": 25,
    "land rover": 42,
    "lexus": 35,
    "mazda": 6,
    "mercedes-benz": 12,
    "mini": 144,
    "mitsubishi": 3,
    "nissan": 11,
    "opel": 5,
    "peugeot": 16,
    "porsche": 140,
    "renault": 19,
    "saab": 17,
    "seat": 22,
    "skoda": 40,
    "subaru": 23,
    "suzuki": 41,
    "tesla": 642,
    "toyota": 13,
    "volkswagen": 8,
    "volvo": 10,
}

# Fuel type codes (ak parameter)
FUEL_CODES = {
    "petrol": 1,
    "bensiin": 1,
    "diesel": 2,
    "diisel": 2,
    "lpg": 4,
    "gaas": 4,
    "electric": 6,
    "elektri": 6,
    "hybrid": 5,
    "hübriid": 5,
    "plug-in hybrid": 7,
    "plug-in hübriid": 7,
}

# Transmission codes (f parameter)
TRANSMISSION_CODES = {
    "manual": 1,
    "manuaal": 1,
    "automatic": 2,
    "automaat": 2,
}

# Body type codes (j[] parameter) - verified from auto24.ee form
BODY_TYPE_CODES = {
    "sedan": 1,
    "sedaan": 1,
    "hatchback": 2,
    "luukpära": 2,
    "wagon": 3,
    "universaal": 3,
    "mpv": 4,
    "mahtuniversaal": 4,
    "coupe": 5,
    "kupee": 5,
    "cabriolet": 6,
    "kabriolett": 6,
    "van": 10,
    "kaubik": 10,
}

# Drive type codes (g parameter)
DRIVE_TYPE_CODES = {
    "fwd": 1,
    "esisild": 1,
    "rwd": 2,
    "tagasild": 2,
    "awd": 3,
    "nelik": 3,
    "4wd": 3,
}


class Auto24Scraper(BaseScraper):
    """Scraper for auto24.ee - Estonia's largest car portal."""

    PORTAL_NAME = "auto24"
    BASE_URL = "https://www.auto24.ee/kasutatud/nimekiri.php"

    def build_search_url(self, params: dict) -> str:
        """Build auto24.ee search URL from filter parameters.

        Supported params:
            brand, model_code, price_min, price_max, year_min, year_max,
            mileage_max, fuel_type, transmission, body_type, drive_type,
            engine_min, engine_max, power_min, power_max, color, location,
            seller_type, sort_by
        """
        query = {}

        # Category: passenger cars + SUVs (101102) or vans (103)
        # Default to cars+SUVs; caller can override for vans
        query["a"] = params.get("category", "101102")

        # Brand
        brand = params.get("brand", "").lower()
        if brand and brand in BRAND_CODES:
            query["b"] = BRAND_CODES[brand]

        # Model (needs brand-specific model code)
        model_code = params.get("model_code")
        if model_code:
            query["bw"] = model_code

        # Year range (f1=from, f2=to)
        if params.get("year_min"):
            query["f1"] = params["year_min"]
        if params.get("year_max"):
            query["f2"] = params["year_max"]

        # Price range (g1=from, g2=to)
        if params.get("price_min"):
            query["g1"] = params["price_min"]
        if params.get("price_max"):
            query["g2"] = params["price_max"]

        # Mileage max (l2)
        if params.get("mileage_max"):
            query["l2"] = params["mileage_max"]

        # Fuel type (h[])
        fuel = params.get("fuel_type", "").lower()
        if fuel and fuel in FUEL_CODES:
            query["h[]"] = FUEL_CODES[fuel]

        # Transmission (i[])
        trans = params.get("transmission", "").lower()
        if trans and trans in TRANSMISSION_CODES:
            query["i[]"] = TRANSMISSION_CODES[trans]

        # Body type (j[])
        body = params.get("body_type", "").lower()
        if body and body in BODY_TYPE_CODES:
            query["j[]"] = BODY_TYPE_CODES[body]

        # Drive type (p[])
        drive = params.get("drive_type", "").lower()
        if drive and drive in DRIVE_TYPE_CODES:
            query["p[]"] = DRIVE_TYPE_CODES[drive]

        # Power (kW) (k1=from, k2=to)
        if params.get("power_min"):
            query["k1"] = params["power_min"]
        if params.get("power_max"):
            query["k2"] = params["power_max"]

        # Sort by date added newest first
        query["ae"] = "1"

        return f"{self.BASE_URL}?{urlencode(query)}"

    async def _scrape_category(self, params: dict, page) -> list[CarListing]:
        """Scrape a single auto24 category page."""
        url = self.build_search_url(params)
        logger.info(f"[auto24] Scraping: {url}")

        try:
            await self._random_delay(1.0, 2.5)
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            if not response or response.status != 200:
                logger.warning(f"[auto24] Got status {response.status if response else 'None'}")
                return []

            try:
                await page.wait_for_selector(
                    "#usedVehiclesSearchResult-flex, .result-row, .no-results",
                    timeout=15000,
                )
            except Exception:
                logger.debug("[auto24] Selector wait timed out, parsing current page content")

            await self._random_delay(0.5, 1.5)
            html = await page.content()
            return self._parse_listings(html)
        except Exception as e:
            logger.error(f"[auto24] Category scrape error: {e}")
            return []

    async def scrape(self, params: dict) -> list[CarListing]:
        """Scrape auto24.ee listings matching the given parameters.

        Scrapes both passenger cars+SUVs (a=101102) and vans (a=103).
        """
        page = await self._new_page()
        listings = []

        try:
            # Scrape cars + SUVs
            car_params = {**params, "category": "101102"}
            listings.extend(await self._scrape_category(car_params, page))

            # Scrape vans (kaubikud)
            van_params = {**params, "category": "103"}
            listings.extend(await self._scrape_category(van_params, page))

            # Client-side filtering for exclude keywords and mileage backup
            mileage_max = params.get("mileage_max")
            exclude_keywords = [kw.strip().lower() for kw in params.get("exclude_keywords", "").split(",") if kw.strip()] if params.get("exclude_keywords") else []
            if exclude_keywords or mileage_max:
                filtered = []
                for car in listings:
                    if mileage_max and car.mileage and car.mileage > mileage_max:
                        continue
                    if exclude_keywords and car.title:
                        if any(kw in car.title.lower() for kw in exclude_keywords):
                            continue
                    filtered.append(car)
                listings = filtered

            logger.info(f"[auto24] Found {len(listings)} listings total (cars+SUVs+vans)")

        except Exception as e:
            logger.error(f"[auto24] Scraping error: {e}")
        finally:
            await page.close()

        return listings

    def _parse_listings(self, html: str) -> list[CarListing]:
        """Parse car listings from auto24.ee HTML."""
        soup = BeautifulSoup(html, "lxml")
        listings = []

        rows = soup.select(".result-row")
        if not rows:
            # Try alternative selector
            rows = soup.select('[class*="result-row"]')

        for row in rows:
            try:
                listing = self._parse_single_listing(row)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.debug(f"[auto24] Failed to parse row: {e}")
                continue

        return listings

    def _parse_single_listing(self, row) -> CarListing | None:
        """Parse a single listing row from auto24.ee."""
        # Extract link and ID
        link_el = row.select_one("a[href]")
        if not link_el:
            return None

        href = link_el.get("href", "")
        if not href:
            return None

        # Build full URL
        if href.startswith("/"):
            url = f"https://www.auto24.ee{href}"
        elif not href.startswith("http"):
            url = f"https://www.auto24.ee/{href}"
        else:
            url = href

        # Extract external ID from URL
        # URLs look like: /kasutatud/12345678 or /used/12345678
        external_id = self._extract_id(url)
        if not external_id:
            return None

        # Model / title
        model_el = row.select_one(".model")
        title_parts = []

        # Try to get brand from broader context
        brand_el = row.select_one(".make") or row.select_one("span.make")
        if brand_el:
            title_parts.append(brand_el.get_text(strip=True))

        if model_el:
            title_parts.append(model_el.get_text(strip=True))

        # Engine info
        engine_el = row.select_one(".engine")
        engine_text = engine_el.get_text(strip=True) if engine_el else None
        if engine_text:
            title_parts.append(engine_text)

        title = " ".join(title_parts) if title_parts else "Unknown"

        # Price
        price = self._parse_price(row)

        # Year
        year = self._parse_field_int(row, ".year", "year")

        # Mileage
        mileage = self._parse_mileage(row)

        # Transmission
        trans_el = row.select_one(".transmission") or row.select_one('[class*="transmission"]')
        transmission = trans_el.get_text(strip=True) if trans_el else None

        # Fuel type from engine text (e.g., "2.0 TDI" -> diesel)
        fuel_type = self._guess_fuel_from_engine(engine_text) if engine_text else None

        # Location
        location_el = row.select_one(".location") or row.select_one('[class*="location"]')
        location = location_el.get_text(strip=True) if location_el else None

        # Image - auto24.ee uses background-image on span.thumb, not <img> tags.
        # The <img> tags in listing rows are icons (fuel.png, priority_star.svg, etc.)
        image_url = None
        thumb_el = row.select_one("span.thumb[style]") or row.select_one(".thumb[style]")
        if thumb_el:
            style = thumb_el.get("style", "")
            bg_match = re.search(r"background-image:\s*url\(['\"]?([^'\")\s]+)['\"]?\)", style)
            if bg_match:
                image_url = bg_match.group(1)
        if not image_url:
            # Fallback: try to find an <img> that is an actual car photo, not an icon
            for img_el in row.select("img"):
                src = img_el.get("data-src") or img_el.get("src") or ""
                if src and "/images/icons/" not in src and not src.endswith(".svg") and "data:image" not in src:
                    image_url = src
                    break

        return CarListing(
            portal="auto24",
            external_id=external_id,
            url=url,
            title=title,
            price=price,
            year=year,
            mileage=mileage,
            fuel_type=fuel_type,
            transmission=transmission,
            image_url=image_url,
            location=location,
            raw_data={"engine": engine_text},
        )

    def _extract_id(self, url: str) -> str | None:
        """Extract listing ID from auto24.ee URL."""
        # Patterns: /soidukid/1234567, /kasutatud/1234567, /used/1234567
        match = re.search(r"/(?:soidukid|kasutatud|used)/(\d+)", url)
        if match:
            return match.group(1)
        # Fallback: any long number sequence in URL
        match = re.search(r"/(\d{5,})", url)
        if match:
            return match.group(1)
        return None

    def _parse_price(self, row) -> int | None:
        """Extract price as integer from a listing row.

        auto24.ee price text starts with a currency symbol (first char stripped).
        Price is in a span.price element, often nested inside another span.
        """
        # Primary: span.price (confirmed selector)
        el = row.select_one("span.price")
        if el:
            text = el.get_text(strip=True)
            # Strip leading currency symbol
            if text and not text[0].isdigit():
                text = text[1:]
            return self._text_to_int(text)

        # Fallback selectors
        for selector in [".price", '[class*="price"]']:
            el = row.select_one(selector)
            if el:
                text = el.get_text(strip=True)
                return self._text_to_int(text)

        # Last resort: look for currency sign
        for span in row.select("span"):
            text = span.get_text(strip=True)
            if "€" in text or "EUR" in text:
                return self._text_to_int(text)

        return None

    def _parse_mileage(self, row) -> int | None:
        """Extract mileage as integer."""
        el = row.select_one(".mileage") or row.select_one('[class*="mileage"]')
        if el:
            text = el.get_text(strip=True)
            return self._text_to_int(text)
        return None

    def _parse_field_int(self, row, selector: str, class_name: str) -> int | None:
        """Extract an integer field by CSS selector or class attribute."""
        el = row.select_one(selector) or row.select_one(f'[class*="{class_name}"]')
        if el:
            text = el.get_text(strip=True)
            return self._text_to_int(text)
        return None

    @staticmethod
    def _text_to_int(text: str) -> int | None:
        """Convert text like '14 500 €' or '87 000 km' to int.

        Handles non-breaking spaces (\xa0) which auto24.ee uses in mileage.
        """
        # Replace non-breaking spaces and remove everything except digits
        cleaned = text.replace("\xa0", "")
        digits = re.sub(r"[^\d]", "", cleaned)
        if digits:
            return int(digits)
        return None

    @staticmethod
    def _guess_fuel_from_engine(engine_text: str) -> str | None:
        """Try to guess fuel type from engine description."""
        text = engine_text.lower()
        if any(kw in text for kw in ["tdi", "cdi", "hdi", "d4d", "dci", "diesel", "diisel"]):
            return "diesel"
        if any(kw in text for kw in ["tsi", "tfsi", "turbo", "gti", "bensiin", "petrol"]):
            return "petrol"
        if "electric" in text or "elektri" in text or "ev" in text:
            return "electric"
        if "hybrid" in text or "hübriid" in text:
            return "hybrid"
        return None
