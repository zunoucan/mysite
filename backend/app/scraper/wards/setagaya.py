"""世田谷区 区立住宅スクレイパー"""
import re
from ..base import BaseScraper
from ...models import HousingListing


class SetagayaScraper(BaseScraper):
    ward_code = "setagaya"
    ward_name = "世田谷区"
    base_url = "https://www.city.setagaya.lg.jp"
    listing_path = "/mokuji/sumai/001/d00187239.html"

    async def scrape(self) -> list[HousingListing]:
        soup = await self.fetch(self.base_url + self.listing_path)
        if not soup:
            return []

        listings: list[HousingListing] = []
        content = soup.find("div", class_="content-main") or soup.find("main") or soup

        for section in content.find_all(["section", "div"], class_=re.compile(r"housing|jutaku|article")):
            title_tag = section.find(["h2", "h3", "h4"])
            name = title_tag.get_text(strip=True) if title_tag else ""
            if not name:
                continue

            texts = section.get_text(" ", strip=True)
            address = _extract_pattern(texts, r"所在地[：:]\s*(.+?)(?:\s|　|$)")
            layout = _extract_pattern(texts, r"間取り[：:]\s*([\w]+)")
            rent_text = _extract_pattern(texts, r"家賃[：:]\s*([\d,]+)")
            rent = int(rent_text.replace(",", "")) if rent_text else None
            floor_area = _extract_float(texts, r"床面積[：:]\s*([\d.]+)")

            link = section.find("a")
            detail_url = (self.base_url + link["href"]) if link and link.get("href", "").startswith("/") else None

            listings.append(HousingListing(
                ward_code=self.ward_code,
                name=name,
                address=address or "",
                layout=layout,
                rent_yen=rent,
                floor_area_sqm=floor_area,
                detail_url=detail_url,
            ))

        return listings


def _extract_pattern(text: str, pattern: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


def _extract_float(text: str, pattern: str) -> float | None:
    m = re.search(pattern, text)
    try:
        return float(m.group(1)) if m else None
    except ValueError:
        return None
