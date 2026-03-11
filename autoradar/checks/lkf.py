import logging
import re

from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


async def check_vehicle_lkf(reg_number: str = None, vin: str = None) -> dict | None:
    """Check vehicle accident history from LKF (Liikluskindlustusfond).

    Automates vs.lkf.ee to fetch accident/insurance claim data.

    Args:
        reg_number: Vehicle registration number.
        vin: Vehicle VIN code (alternative to reg_number).

    Returns:
        Dict with accident data or None if check failed.
    """
    if not reg_number and not vin:
        return None

    result = {
        "reg_number": reg_number,
        "vin": vin,
        "accident_count": 0,
        "total_amount": 0,
        "accidents": [],
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
            await page.goto(
                "https://vs.lkf.ee/pls/xlk/!xvv0200.show_form",
                wait_until="domcontentloaded",
                timeout=30000,
            )

            if reg_number:
                # Fill registration number
                reg_input = await page.wait_for_selector(
                    'input[name*="REG"], input[name*="reg"], input[id*="reg"]',
                    timeout=10000,
                )
                if reg_input:
                    await reg_input.fill(reg_number)
            elif vin:
                # Fill VIN
                vin_input = await page.wait_for_selector(
                    'input[name*="VIN"], input[name*="vin"]',
                    timeout=10000,
                )
                if vin_input:
                    await vin_input.fill(vin)

            # Submit
            submit_btn = await page.wait_for_selector(
                'input[type="submit"], button[type="submit"]',
                timeout=5000,
            )
            if submit_btn:
                await submit_btn.click()

            await page.wait_for_load_state("networkidle", timeout=15000)

            # Parse results
            text = await page.inner_text("body")
            result["raw_text"] = text[:5000]

            # Try to count accidents
            # LKF shows a table with accident entries
            rows = await page.query_selector_all("table tr")
            accident_rows = []
            for row in rows:
                row_text = await row.inner_text()
                # Look for rows with dates and amounts (accident entries)
                if re.search(r"\d{2}\.\d{2}\.\d{4}", row_text) and re.search(r"\d+[\.,]\d{2}", row_text):
                    accident_rows.append(row_text)

            result["accident_count"] = len(accident_rows)

            # Parse individual accidents
            for row_text in accident_rows:
                date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", row_text)
                amount_match = re.search(r"(\d[\d\s]*[\.,]\d{2})", row_text)
                accident = {
                    "date": date_match.group(1) if date_match else None,
                    "amount": amount_match.group(1).replace(" ", "") if amount_match else None,
                }
                result["accidents"].append(accident)

                if amount_match:
                    amount_str = amount_match.group(1).replace(" ", "").replace(",", ".")
                    try:
                        result["total_amount"] += float(amount_str)
                    except ValueError:
                        pass

            result["total_amount"] = round(result["total_amount"], 2)
            logger.info(
                f"[lkf] Check completed for {reg_number or vin}: "
                f"{result['accident_count']} accidents"
            )
            return result

        except Exception as e:
            logger.error(f"[lkf] Check failed for {reg_number or vin}: {e}")
            return None

        finally:
            await browser.close()
