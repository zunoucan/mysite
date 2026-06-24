"""
スクレイピングスケジューラー
APSchedulerを使って定期的に23区の住宅情報を収集・更新する。
"""
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select

from ..db import engine
from ..models import HousingListing, Ward
from ..scraper import WARD_SCRAPERS
from ..config import settings


scheduler = AsyncIOScheduler(timezone="Asia/Tokyo")


async def scrape_all_wards():
    print(f"[scraper] 全23区スクレイピング開始: {datetime.now()}")
    for ward_code, scraper_factory in WARD_SCRAPERS.items():
        try:
            scraper = scraper_factory()
            listings = await scraper.scrape()
            await scraper.close()
            _upsert_listings(ward_code, listings)
            print(f"[scraper] {ward_code}: {len(listings)}件取得")
        except Exception as e:
            print(f"[scraper] {ward_code} エラー: {e}")


def _upsert_listings(ward_code: str, new_listings: list[HousingListing]):
    with Session(engine) as session:
        # 現行データを無効化
        existing = session.exec(
            select(HousingListing).where(HousingListing.ward_code == ward_code)
        ).all()
        for item in existing:
            item.is_active = False

        # 新データを追加
        for listing in new_listings:
            listing.is_active = True
            listing.updated_at = datetime.now(timezone.utc)
            session.add(listing)

        # Ward の最終更新日時を更新
        ward = session.exec(select(Ward).where(Ward.code == ward_code)).first()
        if ward:
            ward.last_scraped_at = datetime.now(timezone.utc)

        session.commit()


def start_scheduler():
    scheduler.add_job(
        scrape_all_wards,
        "interval",
        hours=settings.scrape_interval_hours,
        id="scrape_all",
        replace_existing=True,
    )
    scheduler.start()
