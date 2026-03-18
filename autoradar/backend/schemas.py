from datetime import datetime

from pydantic import BaseModel


class FilterParams(BaseModel):
    brand: str | None = None
    model: str | None = None
    model_code: str | None = None
    price_min: int | None = None
    price_max: int | None = None
    year_min: int | None = None
    year_max: int | None = None
    mileage_max: int | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    body_type: str | None = None
    drive_type: str | None = None
    engine_min: int | None = None
    engine_max: int | None = None
    power_min: int | None = None
    power_max: int | None = None
    color: str | None = None
    location: str | None = None
    seller_type: str | None = None
    exclude_keywords: str | None = None  # Comma-separated words to exclude from title


class FilterCreate(BaseModel):
    name: str
    portals: list[str] = ["auto24"]
    params: FilterParams


class FilterUpdate(BaseModel):
    name: str | None = None
    portals: list[str] | None = None
    params: FilterParams | None = None
    is_active: bool | None = None


class FilterResponse(BaseModel):
    id: int
    name: str
    portals: list[str]
    params: dict
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PriceHistoryResponse(BaseModel):
    id: int
    listing_id: int
    old_price: int | None
    new_price: int | None
    changed_at: datetime

    model_config = {"from_attributes": True}


class ListingResponse(BaseModel):
    id: int
    portal: str
    external_id: str
    url: str | None
    title: str | None
    price: int | None
    year: int | None
    mileage: int | None
    fuel_type: str | None
    transmission: str | None
    body_type: str | None
    power_kw: int | None
    drive_type: str | None
    location: str | None
    image_url: str | None
    reg_number: str | None
    first_seen_at: datetime
    notified_at: datetime | None
    price_history: list[PriceHistoryResponse] = []

    model_config = {"from_attributes": True}


class VehicleCheckResponse(BaseModel):
    id: int
    listing_id: int
    reg_number: str | None
    vin: str | None
    transpordiamet_data: dict | None
    lkf_data: dict | None
    checked_at: datetime

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    total_listings: int
    total_notified: int
    active_filters: int
    portal_counts: dict[str, int]
    last_scrape: datetime | None
