import logging

from sqlalchemy.orm import Session

from backend.database import Listing, VehicleCheck
from checks.lkf import check_vehicle_lkf
from checks.transpordiamet import check_vehicle_transpordiamet

logger = logging.getLogger(__name__)


async def run_vehicle_check(db: Session, listing_id: int) -> VehicleCheck | None:
    """Run background check for a specific listing.

    Args:
        db: Database session.
        listing_id: ID of the listing to check.

    Returns:
        VehicleCheck record or None if check failed.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        logger.warning(f"Listing {listing_id} not found")
        return None

    reg_number = listing.reg_number
    if not reg_number:
        logger.info(f"No reg number for listing {listing_id}, skipping check")
        return None

    # Check if already checked
    existing = (
        db.query(VehicleCheck).filter(VehicleCheck.listing_id == listing_id).first()
    )
    if existing:
        logger.info(f"Listing {listing_id} already checked")
        return existing

    logger.info(f"Running vehicle check for listing {listing_id}, reg: {reg_number}")

    ta_data = await check_vehicle_transpordiamet(reg_number)
    lkf_data = await check_vehicle_lkf(reg_number=reg_number)

    check = VehicleCheck(
        listing_id=listing_id,
        reg_number=reg_number,
        transpordiamet_data=ta_data,
        lkf_data=lkf_data,
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    logger.info(f"Vehicle check saved for listing {listing_id}")
    return check
