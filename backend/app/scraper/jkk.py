"""
JKK（東京都住宅供給公社）スクレイパー
都営住宅・JKK住宅の募集情報を取得する。
"""
import re
from datetime import date
from ..scraper.base import BaseScraper
from ..models import HousingListing


class JKKScraper(BaseScraper):
    """都営住宅の募集情報スクレイパー"""

    def __init__(self):
        super().__init__()
        self.ward_code = "toei"
        self.base_url = "https://www.jkk.metro.tokyo.lg.jp"
        self._listing_url = "https://www.jkk.metro.tokyo.lg.jp/nyukyo/toei/"

    async def scrape(self) -> list[HousingListing]:
        soup = await self.fetch(self._listing_url)
        if not soup:
            return []

        listings: list[HousingListing] = []
        seen_urls: set[str] = set()

        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if not any(kw in text for kw in ["募集", "入居", "申込"]):
                continue
            full_url = _resolve_url(self.base_url, href)
            if not full_url or full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            detail_soup = await self.fetch(full_url)
            if not detail_soup:
                continue
            listing = self._parse(detail_soup, full_url)
            if listing:
                listings.append(listing)
            if len(listings) >= 30:
                break

        # 詳細ページが見つからなければ一覧ページそのものを解析
        if not listings:
            listing = self._parse(soup, self._listing_url)
            if listing:
                listings.append(listing)

        return listings

    def _parse(self, soup, url: str) -> HousingListing | None:
        text = soup.get_text(" ", strip=True)
        h = soup.find("h1") or soup.find("h2")
        name = h.get_text(strip=True) if h else "都営住宅募集"

        address = _extract(text, r"所在地[：:\s]+([^\s　]{5,40})")
        layout = _extract(text, r"間取り[：:\s]*([\dLDKS]+)")
        rent = _parse_yen(_extract(text, r"家賃[：:\s]*([\d,，]+)") or "")
        floor_area = _parse_float(_extract(text, r"(?:床面積|専有面積)[：:\s]*([\d.]+)") or "")
        app_end = _parse_date(_extract(text, r"申込(?:締切|期限)[：:\s]*([\d年月日/\-]+)") or "")
        app_start = _parse_date(_extract(text, r"申込(?:開始|受付)[：:\s]*([\d年月日/\-]+)") or "")
        conditions = _extract(text, r"(?:入居資格|申込資格)[：:\s](.{10,300}?)(?=\s{2,}|$)")

        if app_end and app_end < date.today():
            return None

        form_link = None
        for a in soup.find_all("a", href=True):
            if any(kw in a.get_text() for kw in ["申込書", "PDF", "様式"]):
                form_link = _resolve_url(self.base_url, a["href"])
                break

        if not name and not address:
            return None

        return HousingListing(
            ward_code=self.ward_code,
            name=name,
            address=address or "",
            layout=layout,
            rent_yen=rent,
            floor_area_sqm=floor_area,
            application_start=app_start,
            application_end=app_end,
            eligibility_conditions=conditions,
            detail_url=url,
            application_form_url=form_link,
        )


class JKKOwnScraper(JKKScraper):
    """JKK住宅（公社住宅）の募集情報スクレイパー"""

    def __init__(self):
        super().__init__()
        self.ward_code = "jkk"
        self._listing_url = "https://www.jkk.metro.tokyo.lg.jp/chintai/boshu/"


class URScraper(BaseScraper):
    """UR都市機構の賃貸住宅募集スクレイパー（東京エリア）"""

    def __init__(self):
        super().__init__()
        self.ward_code = "ur"
        self.base_url = "https://www.ur-net.go.jp"
        self._listing_url = "https://www.ur-net.go.jp/chintai/tokyo/"

    async def scrape(self) -> list[HousingListing]:
        soup = await self.fetch(self._listing_url)
        if not soup:
            return []

        listings: list[HousingListing] = []
        seen_urls: set[str] = set()

        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if not any(kw in text for kw in ["物件", "団地", "住宅", "募集"]):
                continue
            full_url = _resolve_url(self.base_url, href)
            if not full_url or full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            detail_soup = await self.fetch(full_url)
            if not detail_soup:
                continue
            listing = self._parse_ur(detail_soup, full_url)
            if listing:
                listings.append(listing)
            if len(listings) >= 30:
                break

        return listings

    def _parse_ur(self, soup, url: str) -> HousingListing | None:
        text = soup.get_text(" ", strip=True)
        h = soup.find("h1") or soup.find("h2")
        name = h.get_text(strip=True) if h else "UR賃貸住宅"

        address = _extract(text, r"(?:所在地|住所)[：:\s]+([^\s　]{5,40})")
        layout = _extract(text, r"間取り[：:\s]*([\dLDKSR]+)")
        rent = _parse_yen(_extract(text, r"(?:家賃|賃料)[：:\s]*([\d,，]+)") or "")
        floor_area = _parse_float(_extract(text, r"(?:床面積|専有面積)[：:\s]*([\d.]+)") or "")
        mgmt = _parse_yen(_extract(text, r"(?:管理費|共益費)[：:\s]*([\d,，]+)") or "")

        if not address and not rent:
            return None

        return HousingListing(
            ward_code=self.ward_code,
            name=name,
            address=address or "",
            layout=layout,
            rent_yen=rent,
            management_fee_yen=mgmt,
            floor_area_sqm=floor_area,
            detail_url=url,
        )


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


def _parse_date(s: str):
    if not s:
        return None
    s = s.replace("年", "-").replace("月", "-").replace("日", "")
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            parts = [int(p) for p in re.split(r"[-/]", s) if p][:3]
            return date(*parts)
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
