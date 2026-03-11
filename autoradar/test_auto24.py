"""Standalone test script for auto24.ee scraper.

Run: python test_auto24.py

Tests if the scraper can successfully fetch and parse listings from auto24.ee.
"""

import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Add project root to path
sys.path.insert(0, ".")

from scrapers.auto24 import Auto24Scraper


async def main():
    scraper = Auto24Scraper()

    print("=" * 60)
    print("Auto24.ee Scraper Test")
    print("=" * 60)

    # Test 1: Build URL
    test_params = {
        "brand": "bmw",
        "price_max": 15000,
        "year_min": 2015,
        "fuel_type": "diisel",
    }
    url = scraper.build_search_url(test_params)
    print(f"\nTest URL: {url}")

    # Test 2: Scrape
    print("\nStarting browser...")
    await scraper.start()

    try:
        print("Scraping BMW diesel, max 15000 EUR, from 2015...")
        listings = await scraper.scrape(test_params)

        print(f"\nFound {len(listings)} listings:")
        print("-" * 60)

        for i, car in enumerate(listings[:10], 1):
            print(f"\n{i}. {car.title}")
            if car.price:
                print(f"   Hind: {car.price:,} EUR".replace(",", " "))
            if car.year:
                print(f"   Aasta: {car.year}")
            if car.mileage:
                print(f"   Läbisõit: {car.mileage:,} km".replace(",", " "))
            if car.transmission:
                print(f"   Käigukast: {car.transmission}")
            if car.fuel_type:
                print(f"   Kütus: {car.fuel_type}")
            print(f"   URL: {car.url}")
            print(f"   ID: {car.external_id}")

        if len(listings) > 10:
            print(f"\n... ja veel {len(listings) - 10} kuulutust")

        # Test 3: No-params scrape (all cars, sorted by newest)
        print("\n" + "=" * 60)
        print("Test 2: All newest cars (no filter)...")
        all_params = {"sort_by": "3"}
        all_listings = await scraper.scrape(all_params)
        print(f"Found {len(all_listings)} listings")

    finally:
        await scraper.stop()

    print("\n" + "=" * 60)
    if listings:
        print("SUCCESS! Scraper works!")
    else:
        print("WARNING: No listings found. Site may be blocking or selectors may need updating.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
