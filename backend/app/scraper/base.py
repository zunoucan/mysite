from abc import ABC, abstractmethod
from typing import Optional
import httpx
from bs4 import BeautifulSoup

from ..models import HousingListing


class BaseScraper(ABC):
    """各区スクレイパーの基底クラス"""

    ward_code: str
    ward_name: str
    base_url: str

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "TokyoHousingApp/1.0 (info@example.com)"},
            follow_redirects=True,
        )

    async def fetch(self, url: str) -> Optional[BeautifulSoup]:
        try:
            resp = await self.client.get(url)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            print(f"[{self.ward_code}] fetch error {url}: {e}")
            return None

    @abstractmethod
    async def scrape(self) -> list[HousingListing]:
        """住宅情報一覧を取得して返す"""
        ...

    async def close(self):
        await self.client.aclose()
