from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import Listing, VehicleCheck, get_db
from backend.schemas import ListingResponse, VehicleCheckResponse
from checks.runner import run_vehicle_check

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.get("", response_model=list[ListingResponse])
def list_listings(
    portal: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Listing)
    if portal:
        query = query.filter(Listing.portal == portal)
    return (
        query.order_by(Listing.first_seen_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(404, "Listing not found")
    return listing


@router.get("/{listing_id}/check", response_model=VehicleCheckResponse | None)
def get_listing_check(listing_id: int, db: Session = Depends(get_db)):
    check = (
        db.query(VehicleCheck)
        .filter(VehicleCheck.listing_id == listing_id)
        .order_by(VehicleCheck.checked_at.desc())
        .first()
    )
    return check


@router.post("/{listing_id}/check", response_model=VehicleCheckResponse)
async def trigger_vehicle_check(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(404, "Listing not found")

    check = await run_vehicle_check(db, listing_id)
    if not check:
        raise HTTPException(400, "Vehicle check failed - reg number may be missing")
    return check
