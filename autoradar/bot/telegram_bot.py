import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from backend.config import settings
from backend.database import Listing, SearchFilter, SessionLocal

logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "<b>Autoradar</b> - kasutatud autode kuulutuste monitor\n\n"
        "Jälgin auto24.ee, autoportaal.ee, veego.ee ja autodiiler.ee portaale "
        "ja annan sulle teada, kui leidub uus kuulutus sinu otsingukriteeriumitele.\n\n"
        "<b>Käsud:</b>\n"
        "/filters - vaata aktiivseid filtreid\n"
        "/stats - statistika\n"
        "/pause - peata teavitused\n"
        "/resume - jätka teavitusi\n",
        parse_mode="HTML",
    )


async def cmd_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /filters command - show active search filters."""
    db = SessionLocal()
    try:
        filters = db.query(SearchFilter).filter(SearchFilter.is_active.is_(True)).all()

        if not filters:
            await update.message.reply_text("Aktiivseid filtreid ei ole. Lisa filtreid web UI kaudu.")
            return

        lines = ["<b>Aktiivsed filtrid:</b>\n"]
        for f in filters:
            portals = ", ".join(f.portals) if f.portals else "kõik"
            params = f.params or {}
            details = []
            if params.get("brand"):
                details.append(params["brand"].upper())
            if params.get("price_max"):
                details.append(f"kuni {params['price_max']} EUR")
            if params.get("year_min"):
                details.append(f"alates {params['year_min']}")

            detail_str = ", ".join(details) if details else "kõik autod"
            status = "ON" if f.is_active else "OFF"
            lines.append(f"  {status} <b>{f.name}</b>: {detail_str} ({portals})")

        await update.message.reply_text("\n".join(lines), parse_mode="HTML")
    finally:
        db.close()


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show statistics."""
    db = SessionLocal()
    try:
        total_listings = db.query(Listing).count()
        notified = db.query(Listing).filter(Listing.notified_at.isnot(None)).count()
        active_filters = db.query(SearchFilter).filter(SearchFilter.is_active.is_(True)).count()

        # Per-portal counts
        portal_counts = {}
        for portal in ["auto24", "autoportaal", "veego", "autodiiler"]:
            count = db.query(Listing).filter(Listing.portal == portal).count()
            if count > 0:
                portal_counts[portal] = count

        lines = [
            "<b>Autoradar statistika</b>\n",
            f"Aktiivseid filtreid: {active_filters}",
            f"Kuulutusi kokku: {total_listings}",
            f"Teavitusi saadetud: {notified}",
        ]

        if portal_counts:
            lines.append("\n<b>Portaalide kaupa:</b>")
            for portal, count in sorted(portal_counts.items()):
                lines.append(f"  {portal}: {count}")

        await update.message.reply_text("\n".join(lines), parse_mode="HTML")
    finally:
        db.close()


async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pause command."""
    # Store pause state in context
    context.bot_data["paused"] = True
    await update.message.reply_text("Teavitused peatatud. Kasuta /resume jätkamiseks.")


async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resume command."""
    context.bot_data["paused"] = False
    await update.message.reply_text("Teavitused jätkavad!")


def is_paused(context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if notifications are paused."""
    return context.bot_data.get("paused", False)


def create_bot_application() -> Application | None:
    """Create and configure the Telegram bot application."""
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot disabled")
        return None

    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("filters", cmd_filters))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))

    return app
