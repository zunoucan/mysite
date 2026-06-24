"""新宿区 区立住宅スクレイパー"""
import re
from datetime import date
from ..base import BaseScraper
from ...models import HousingListing


class ShinjukuScraper(BaseScraper):
    ward_code = "shinjuku"
    ward_name = "新宿区"
    base_url = "https://www.city.shinjuku.lg.jp"
    listing_path = "/seikatsu/hoken/jyutaku/kukoukyojutaku/index.html"

    async def scrape(self) -> list[HousingListing]:
        soup = await self.fetch(self.base_url + self.listing_path)
        if not soup:
            return []

        listings: list[HousingListing] = []
        # 新宿区の住宅ページは表形式で掲載
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:  # ヘッダー行をスキップ
                cells = row.find_all(["td", "th"])
                if len(cells) < 4:
                    continue
                try:
                    name = cells[0].get_text(strip=True)
                    address = cells[1].get_text(strip=True)
                    layout = cells[2].get_text(strip=True)
                    rent_text = cells[3].get_text(strip=True)
                    rent = _parse_yen(rent_text)
                    link_tag = cells[0].find("a")
                    detail_url = (self.base_url + link_tag["href"]) if link_tag else None

                    if name:
                        listings.append(HousingListing(
                            ward_code=self.ward_code,
                            name=name,
                            address=address,
                            layout=layout,
                            rent_yen=rent,
                            detail_url=detail_url,
                        ))
                except (IndexError, TypeError, KeyError):
                    continue

        return listings


def _parse_yen(text: str) -> int | None:
    m = re.search(r"[\d,]+", text.replace("，", ","))
    if m:
        return int(m.group().replace(",", ""))
    return None
