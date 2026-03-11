import logging

from telegram import Bot
from telegram.constants import ParseMode

from backend.config import settings

logger = logging.getLogger(__name__)


def format_listing_message(listing: dict, check_data: dict | None = None) -> str:
    """Format a car listing as a Telegram message.

    Args:
        listing: Dict with listing data (from DB or CarListing).
        check_data: Optional vehicle check data.

    Returns:
        Formatted message string with HTML markup.
    """
    portal_display = {
        "auto24": "auto24.ee",
        "autoportaal": "autoportaal.ee",
        "veego": "veego.ee",
        "autodiiler": "autodiiler.ee",
    }

    portal = portal_display.get(listing.get("portal", ""), listing.get("portal", ""))
    title = listing.get("title", "Tundmatu auto")
    price = listing.get("price")
    year = listing.get("year")
    mileage = listing.get("mileage")
    fuel_type = listing.get("fuel_type")
    transmission = listing.get("transmission")
    location = listing.get("location")
    url = listing.get("url", "")

    lines = [f"<b>UUS KUULUTUS — {portal}</b>", ""]

    lines.append(f"<b>{title}</b>")

    # Price
    if price:
        lines.append(f"Hind: <b>{price:,} EUR</b>".replace(",", " "))

    # Details line
    details = []
    if year:
        details.append(str(year))
    if mileage:
        details.append(f"{mileage:,} km".replace(",", " "))
    if fuel_type:
        details.append(fuel_type.capitalize())
    if transmission:
        details.append(transmission.capitalize())
    if details:
        lines.append(" | ".join(details))

    if location:
        lines.append(f"Asukoht: {location}")

    # Vehicle check results
    if check_data:
        lines.append("")
        lines.append("<b>Taustauring:</b>")

        ta_data = check_data.get("transpordiamet_data")
        if ta_data:
            ut_status = ta_data.get("ut_valid", "teadmata")
            ut_next = ta_data.get("ut_next_date", "")
            if ut_status:
                status_icon = "OK" if ut_status else "!"
                lines.append(f"  {status_icon} UT: {ut_next if ut_next else 'info puudu'}")

        lkf_data = check_data.get("lkf_data")
        if lkf_data:
            accidents = lkf_data.get("accident_count", 0)
            if accidents == 0:
                lines.append("  OK LKF: kahjujuhtumeid ei ole")
            else:
                total = lkf_data.get("total_amount", "teadmata")
                lines.append(f"  ! LKF: {accidents} kahjujuhtum(it), kokku {total} EUR")

    # Link
    if url:
        lines.append("")
        lines.append(f'<a href="{url}">Vaata kuulutust</a>')

    return "\n".join(lines)


async def send_listing_notification(listing: dict, check_data: dict | None = None):
    """Send a Telegram notification about a new listing.

    Args:
        listing: Dict with listing data.
        check_data: Optional vehicle check data.
    """
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram not configured, skipping notification")
        return

    bot = Bot(token=settings.telegram_bot_token)
    message = format_listing_message(listing, check_data)

    try:
        image_url = listing.get("image_url")
        if image_url and image_url.startswith("http"):
            try:
                await bot.send_photo(
                    chat_id=settings.telegram_chat_id,
                    photo=image_url,
                    caption=message,
                    parse_mode=ParseMode.HTML,
                )
                return
            except Exception:
                # Photo failed, send as text
                pass

        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
        )
        logger.info(f"Notification sent for {listing.get('title', 'unknown')}")

    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")


async def send_status_message(text: str):
    """Send a status/info message to Telegram."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return

    bot = Bot(token=settings.telegram_bot_token)
    try:
        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"Failed to send status message: {e}")
