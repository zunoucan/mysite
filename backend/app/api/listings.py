from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..models import HousingListing, Ward
from ..db import get_session

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/", response_model=list[HousingListing])
async def get_listings(
    ward_code: Optional[str] = Query(None, description="区コード (e.g. shinjuku)"),
    min_rent: Optional[int] = Query(None),
    max_rent: Optional[int] = Query(None),
    layout: Optional[str] = Query(None, description="間取り (1K, 2LDK 等)"),
    min_area: Optional[float] = Query(None, description="最小床面積(m²)"),
    active_only: bool = Query(True),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    session: Session = Depends(get_session),
):
    stmt = select(HousingListing)
    if ward_code:
        stmt = stmt.where(HousingListing.ward_code == ward_code)
    if active_only:
        stmt = stmt.where(HousingListing.is_active == True)
    if min_rent is not None:
        stmt = stmt.where(HousingListing.rent_yen >= min_rent)
    if max_rent is not None:
        stmt = stmt.where(HousingListing.rent_yen <= max_rent)
    if layout:
        stmt = stmt.where(HousingListing.layout == layout)
    if min_area is not None:
        stmt = stmt.where(HousingListing.floor_area_sqm >= min_area)
    stmt = stmt.offset(offset).limit(limit)
    return session.exec(stmt).all()


@router.get("/{listing_id}", response_model=HousingListing)
async def get_listing(listing_id: int, session: Session = Depends(get_session)):
    listing = session.get(HousingListing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.get("/wards/", response_model=list[Ward])
async def get_wards(session: Session = Depends(get_session)):
    return session.exec(select(Ward)).all()
