import logging

from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


async def check_vehicle_transpordiamet(reg_number: str) -> dict | None:
    """Check vehicle data from Estonian Transport Authority (Transpordiamet).

    Automates eteenindus.mnt.ee to fetch vehicle inspection and registration data.

    Args:
        reg_number: Vehicle registration number (e.g., "123ABC").

    Returns:
        Dict with vehicle data or None if check failed.
    """
    if not reg_number:
        return None

    result = {
        "reg_number": reg_number,
        "ut_valid": None,
        "ut_next_date": None,
        "first_registration": None,
        "registration_date_estonia": None,
        "owners_count": None,
        "raw_text": None,
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = await browser.new_context(
            locale="et-EE",
            timezone_id="Europe/Tallinn",
        )
        page = await context.new_page()

        try:
            # Navigate to vehicle query page
            await page.goto(
                "https://eteenindus.mnt.ee/public/soidukTapisParing.jsf",
                wait_until="domcontentloaded",
                timeout=30000,
            )

            # Find the registration number input and fill it
            reg_input = await page.wait_for_selector(
                'input[id*="registreerimismärk"], input[name*="regMark"], input[type="text"]',
                timeout=10000,
            )
            if reg_input:
                await reg_input.fill(reg_number)

            # Click search button
            search_btn = await page.wait_for_selector(
                'button[type="submit"], input[type="submit"], [class*="btn"]',
                timeout=5000,
            )
            if search_btn:
                await search_btn.click()

            # Wait for results
            await page.wait_for_load_state("networkidle", timeout=15000)

            # Parse the results page
            content = await page.content()
            result["raw_text"] = content[:5000]  # Store first 5000 chars for debugging

            # Try to extract UT (tehnoülevaatus) data
            # The exact selectors depend on the actual page structure
            text = await page.inner_text("body")

            if "kehtiv" in text.lower():
                result["ut_valid"] = True
            elif "kehtetu" in text.lower() or "aegunud" in text.lower():
                result["ut_valid"] = False

            logger.info(f"[transpordiamet] Check completed for {reg_number}")
            return result

        except Exception as e:
            logger.error(f"[transpordiamet] Check failed for {reg_number}: {e}")
            return None

        finally:
            await browser.close()
