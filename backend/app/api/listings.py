from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlmodel import Session, select

from ..models import HousingListing, Ward
from ..db import get_session

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/", response_model=list[HousingListing])
async def get_listings(
    ward_code: Optional[str] = Query(None, description="区コード (e.g. shinjuku, jkk, toei, ur)"),
    source_type: Optional[str] = Query(None, description="ward|toei|jkk|ur"),
    min_rent: Optional[int] = Query(None),
    max_rent: Optional[int] = Query(None),
    layout: Optional[str] = Query(None, description="間取り (1K, 2LDK 等)"),
    min_area: Optional[float] = Query(None, description="最小床面積(m²)"),
    active_only: bool = Query(True),
    sort_by: Optional[str] = Query(None, description="rent_asc|rent_desc|end_date_asc|area_desc|new"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    session: Session = Depends(get_session),
):
    WARD_CODES = {"toei", "jkk", "ur"}
    stmt = select(HousingListing)

    if ward_code:
        stmt = stmt.where(HousingListing.ward_code == ward_code)
    elif source_type:
        if source_type == "ward":
            stmt = stmt.where(HousingListing.ward_code.notin_(WARD_CODES))
        elif source_type in WARD_CODES:
            stmt = stmt.where(HousingListing.ward_code == source_type)

    if active_only:
        today = date.today()
        stmt = stmt.where(HousingListing.is_active == True)
        stmt = stmt.where(
            or_(HousingListing.application_end == None,
                HousingListing.application_end >= today)
        )
    if min_rent is not None:
        stmt = stmt.where(HousingListing.rent_yen >= min_rent)
    if max_rent is not None:
        stmt = stmt.where(HousingListing.rent_yen <= max_rent)
    if layout:
        stmt = stmt.where(HousingListing.layout == layout)
    if min_area is not None:
        stmt = stmt.where(HousingListing.floor_area_sqm >= min_area)

    if sort_by == "rent_asc":
        stmt = stmt.order_by(HousingListing.rent_yen.asc())
    elif sort_by == "rent_desc":
        stmt = stmt.order_by(HousingListing.rent_yen.desc())
    elif sort_by == "end_date_asc":
        stmt = stmt.order_by(HousingListing.application_end.asc())
    elif sort_by == "area_desc":
        stmt = stmt.order_by(HousingListing.floor_area_sqm.desc())
    else:
        stmt = stmt.order_by(HousingListing.created_at.desc())

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
