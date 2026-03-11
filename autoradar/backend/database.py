from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from backend.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class SearchFilter(Base):
    __tablename__ = "search_filters"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    portals = Column(JSONB, default=list)  # ["auto24", "autoportaal", ...]
    params = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    portal = Column(String(50), nullable=False)
    external_id = Column(String(100), nullable=False)
    url = Column(Text)
    title = Column(String(500))
    price = Column(Integer)
    year = Column(Integer)
    mileage = Column(Integer)
    fuel_type = Column(String(50))
    transmission = Column(String(50))
    body_type = Column(String(50))
    engine_volume = Column(Integer)  # cm³
    power_kw = Column(Integer)
    drive_type = Column(String(50))
    color = Column(String(50))
    location = Column(String(100))
    seller_type = Column(String(50))
    image_url = Column(Text)
    reg_number = Column(String(20))
    raw_data = Column(JSONB)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    notified_at = Column(DateTime, nullable=True)

    vehicle_checks = relationship("VehicleCheck", back_populates="listing")

    __table_args__ = (UniqueConstraint("portal", "external_id", name="uq_portal_external_id"),)


class VehicleCheck(Base):
    __tablename__ = "vehicle_checks"

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    reg_number = Column(String(20))
    vin = Column(String(50))
    transpordiamet_data = Column(JSONB)
    lkf_data = Column(JSONB)
    checked_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="vehicle_checks")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
