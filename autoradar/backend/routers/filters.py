from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SearchFilter, get_db
from backend.schemas import FilterCreate, FilterResponse, FilterUpdate

router = APIRouter(prefix="/api/filters", tags=["filters"])


@router.get("", response_model=list[FilterResponse])
def list_filters(active_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(SearchFilter)
    if active_only:
        query = query.filter(SearchFilter.is_active.is_(True))
    return query.order_by(SearchFilter.created_at.desc()).all()


@router.post("", response_model=FilterResponse, status_code=201)
def create_filter(data: FilterCreate, db: Session = Depends(get_db)):
    f = SearchFilter(
        name=data.name,
        portals=data.portals,
        params=data.params.model_dump(exclude_none=True),
        is_active=True,
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


@router.get("/{filter_id}", response_model=FilterResponse)
def get_filter(filter_id: int, db: Session = Depends(get_db)):
    f = db.query(SearchFilter).filter(SearchFilter.id == filter_id).first()
    if not f:
        raise HTTPException(404, "Filter not found")
    return f


@router.put("/{filter_id}", response_model=FilterResponse)
def update_filter(filter_id: int, data: FilterUpdate, db: Session = Depends(get_db)):
    f = db.query(SearchFilter).filter(SearchFilter.id == filter_id).first()
    if not f:
        raise HTTPException(404, "Filter not found")
    if data.name is not None:
        f.name = data.name
    if data.portals is not None:
        f.portals = data.portals
    if data.params is not None:
        f.params = data.params.model_dump(exclude_none=True)
    if data.is_active is not None:
        f.is_active = data.is_active
    db.commit()
    db.refresh(f)
    return f


@router.delete("/{filter_id}", status_code=204)
def delete_filter(filter_id: int, db: Session = Depends(get_db)):
    f = db.query(SearchFilter).filter(SearchFilter.id == filter_id).first()
    if not f:
        raise HTTPException(404, "Filter not found")
    db.delete(f)
    db.commit()
