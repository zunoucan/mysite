from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Ward(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)  # e.g. "chiyoda"
    name_ja: str                                 # e.g. "千代田区"
    website_url: str
    application_url: Optional[str] = None
    last_scraped_at: Optional[datetime] = None


class HousingListing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ward_code: str = Field(index=True, foreign_key="ward.code")

    # 物件情報
    name: str
    address: str
    building_type: Optional[str] = None          # 集合住宅種別
    floor: Optional[str] = None                  # 階数
    room_number: Optional[str] = None

    # スペック
    floor_area_sqm: Optional[float] = None       # 床面積（m²）
    layout: Optional[str] = None                 # 間取り (1K, 2LDK, etc.)
    year_built: Optional[int] = None
    floor_level: Optional[int] = None            # 所在階

    # 家賃
    rent_yen: Optional[int] = None
    management_fee_yen: Optional[int] = None
    deposit_yen: Optional[int] = None
    key_money_yen: Optional[int] = None

    # 応募
    application_start: Optional[date] = None
    application_end: Optional[date] = None
    move_in_date: Optional[date] = None
    lottery_date: Optional[date] = None

    # 入居者条件（JSON文字列）
    eligibility_conditions: Optional[str] = None

    # ソースリンク
    detail_url: Optional[str] = None
    application_form_url: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
