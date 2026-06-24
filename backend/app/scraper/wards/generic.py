"""
汎用区スクレイパー
専用スクレイパーのない区に使用。ページ構造から住宅情報を推測して抽出する。
"""
import re
from ..base import BaseScraper
from ...models import HousingListing


class GenericWardScraper(BaseScraper):
    def __init__(self, ward_code: str, ward_name: str, listing_url: str):
        super().__init__()
        self.ward_code = ward_code
        self.ward_name = ward_name
        self.base_url = listing_url
        self._listing_url = listing_url

    async def scrape(self) -> list[HousingListing]:
        soup = await self.fetch(self._listing_url)
        if not soup:
            return []

        listings: list[HousingListing] = []

        # リンク集から詳細ページを探す
        detail_links = self._find_housing_links(soup)

        if detail_links:
            for href, anchor_text in detail_links[:20]:  # 最大20件
                detail_soup = await self.fetch(href)
                if not detail_soup:
                    continue
                listing = self._parse_detail_page(detail_soup, href, anchor_text)
                if listing:
                    listings.append(listing)
        else:
            # 一覧ページ自体から直接抽出
            listing = self._parse_detail_page(soup, self._listing_url, self.ward_name + "区立住宅")
            if listing:
                listings.append(listing)

        return listings

    def _find_housing_links(self, soup) -> list[tuple[str, str]]:
        """住宅情報へのリンクを抽出"""
        keywords = ["住宅", "募集", "入居", "申込", "応募"]
        results = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if any(kw in text for kw in keywords) and href:
                full_url = _resolve_url(self._listing_url, href)
                if full_url:
                    results.append((full_url, text))
        return results

    def _parse_detail_page(self, soup, url: str, fallback_name: str) -> HousingListing | None:
        text = soup.get_text(" ", strip=True)

        name = (soup.find("h1") or soup.find("h2"))
        name_str = name.get_text(strip=True) if name else fallback_name

        address = _extract(text, r"所在地[：:\s]+([^\s　]{5,30})")
        layout = _extract(text, r"間取り[：:\s]*([\dLDKS]+)")
        rent = _parse_yen(_extract(text, r"家賃[：:\s]*([\d,，]+)") or "")
        mgmt = _parse_yen(_extract(text, r"管理費[：:\s]*([\d,，]+)") or "")
        floor_area = _parse_float(_extract(text, r"床面積[：:\s]*([\d.]+)") or "")
        floor_level = _parse_int(_extract(text, r"所在階[：:\s]*(\d+)") or "")
        year_built = _parse_int(_extract(text, r"建築年[：:\s]*(\d{4})") or "")
        app_end = _parse_date_str(_extract(text, r"申込(?:締切|期限)[：:\s]*([\d年月日/\-]+)") or "")
        app_start = _parse_date_str(_extract(text, r"申込(?:開始|受付)[：:\s]*([\d年月日/\-]+)") or "")
        conditions = _extract(text, r"入居(?:資格|条件|要件)[：:\s](.{10,200}?)(?=\s{2,}|$)")

        form_link = None
        for a in soup.find_all("a", href=True):
            if any(kw in a.get_text() for kw in ["申込書", "申請書", "様式", "PDF"]):
                form_link = _resolve_url(url, a["href"])
                break

        if not address and not rent:
            return None

        return HousingListing(
            ward_code=self.ward_code,
            name=name_str,
            address=address or "",
            layout=layout,
            rent_yen=rent,
            management_fee_yen=mgmt,
            floor_area_sqm=floor_area,
            floor_level=floor_level,
            year_built=year_built,
            application_start=app_start,
            application_end=app_end,
            eligibility_conditions=conditions,
            detail_url=url,
            application_form_url=form_link,
        )


# ── ユーティリティ ──────────────────────────────────────────────

def _extract(text: str, pattern: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


def _parse_yen(s: str) -> int | None:
    s = re.sub(r"[^\d]", "", s)
    return int(s) if s else None


def _parse_float(s: str) -> float | None:
    try:
        return float(s) if s else None
    except ValueError:
        return None


def _parse_int(s: str) -> int | None:
    try:
        return int(s) if s else None
    except ValueError:
        return None


def _parse_date_str(s: str):
    from datetime import date
    if not s:
        return None
    s = s.replace("年", "-").replace("月", "-").replace("日", "")
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m"):
        try:
            return date(*[int(p) for p in s.split("-")[:3]])
        except Exception:
            pass
    return None


def _resolve_url(base: str, href: str) -> str | None:
    if not href or href.startswith("#") or href.startswith("javascript"):
        return None
    if href.startswith("http"):
        return href
    from urllib.parse import urljoin
    return urljoin(base, href)
