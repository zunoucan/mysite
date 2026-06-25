"""
汎用区スクレイパー（精度改善版）
区のページから住宅募集情報を正確に抽出する。
"""
import re
from datetime import date as _date
from urllib.parse import urljoin
from ..base import BaseScraper
from ...models import HousingListing

# ナビゲーション・一般情報ページを除外するキーワード
_SKIP_LINK_TEXTS = {
    "トップページ", "ホーム", "HOME", "お問い合わせ", "サイトマップ",
    "受付時間", "アクセス", "個人情報", "プライバシー", "よくある質問",
    "FAQ", "戻る", "ページ先頭", "印刷", "文字サイズ", "検索",
    "メニュー", "カレンダー", "更新情報", "ニュース", "リンク集",
}

# 有効な住宅募集ページのURL特徴
_LISTING_URL_HINTS = [
    "boshu", "nyukyo", "jutaku", "sumai", "jyutaku", "moushikomi",
    "kouei", "kuei", "koe", "chintai", "r0", "r1", "r2", "r3", "r4", "r5",
    "r6", "r7", "r8", "令和",
]

# 名前として不正なパターン
_INVALID_NAME_PATTERNS = [
    "トップページ", "お問い合わせ", "受付時間", "HOME", "サイトマップ",
    "戸数", "ページ", "メニュー", "リンク", "情報提供", "窓口",
    "センター名", "組織", "一覧へ",
]


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
        detail_links = self._find_housing_links(soup)

        if detail_links:
            seen: set[str] = set()
            for href, anchor_text in detail_links[:25]:
                if href in seen:
                    continue
                seen.add(href)
                detail_soup = await self.fetch(href)
                if not detail_soup:
                    continue
                listing = self._parse_detail_page(detail_soup, href, anchor_text)
                if listing:
                    listings.append(listing)
        else:
            listing = self._parse_detail_page(
                soup, self._listing_url,
                f"{self.ward_name}区立住宅募集"
            )
            if listing:
                listings.append(listing)

        return listings

    def _find_housing_links(self, soup) -> list[tuple[str, str]]:
        """住宅情報の詳細ページへのリンクだけを抽出"""
        housing_kws = {"募集", "入居", "申込", "応募", "公募", "一般", "区営", "区立", "令和"}
        results: list[tuple[str, str]] = []

        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]

            # テキストが短すぎる・長すぎるリンクはスキップ
            if len(text) < 4 or len(text) > 60:
                continue
            # 明らかにナビゲーション系はスキップ
            if any(skip in text for skip in _SKIP_LINK_TEXTS):
                continue
            # 住宅関連キーワードを含む
            if not any(kw in text for kw in housing_kws):
                continue

            full_url = _resolve_url(self._listing_url, href)
            if not full_url:
                continue
            # URLにも住宅関連ヒントがあれば優先度高
            results.append((full_url, text))

        # URLに住宅ヒントが含まれるリンクを優先
        def _score(item: tuple[str, str]) -> int:
            url, _ = item
            return sum(1 for h in _LISTING_URL_HINTS if h in url.lower())

        results.sort(key=_score, reverse=True)
        return results

    def _parse_detail_page(self, soup, url: str, fallback_name: str) -> HousingListing | None:
        text = soup.get_text(" ", strip=True)

        # ページ名取得（h1 or h2）
        h_tag = soup.find("h1") or soup.find("h2")
        raw_name = h_tag.get_text(strip=True) if h_tag else fallback_name
        if any(p in raw_name for p in _INVALID_NAME_PATTERNS):
            raw_name = fallback_name

        # 住所抽出（複数パターン）
        address = (
            _extract(text, r"所在地[：:\s]+([^\s　\n]{5,40})")
            or _extract(text, r"住所[：:\s]+([^\s　\n]{5,40})")
            or _extract(text, r"物件所在地[：:\s]+([^\s　\n]{5,40})")
            or _extract(text, r"((?:[東京都]?[千代田中央港新宿文京台東墨田江東品川目黒大田世田谷渋谷中野杉並豊島北荒川板橋練馬足立葛飾江戸川]区|東京都)[^\s\n]{3,30})")
        )
        if not _is_valid_address(address):
            address = None

        # 間取り
        layout = _extract(text, r"間取り[：:\s]*([\dLDKSR]+)")

        # 家賃（異常値を除外）
        rent_raw = _extract(text, r"家賃[：:\s]*([\d,，万]+(?:円)?)")
        rent = _parse_yen(rent_raw or "")
        if rent and (rent < 1000 or rent > 1_000_000):
            rent = None

        mgmt = _parse_yen(_extract(text, r"(?:管理費|共益費)[：:\s]*([\d,，]+)") or "")
        floor_area = _parse_float(_extract(text, r"(?:床|専有)面積[：:\s]*([\d.]+)") or "")
        floor_level = _parse_int(_extract(text, r"所在階[：:\s]*(\d+)") or "")
        year_built = _parse_int(_extract(text, r"建築年[：:\s]*(\d{4})") or "")

        # 応募日程
        app_end = _parse_date_str(
            _extract(text, r"申込(?:締切|期限)[：:\s]*([\d年月日/\-]+)") or
            _extract(text, r"締切[：:\s]*([\d年月日/\-]+)") or ""
        )
        app_start = _parse_date_str(
            _extract(text, r"申込(?:開始|受付)[：:\s]*([\d年月日/\-]+)") or ""
        )

        # 締切済みはスキップ
        if app_end and app_end < _date.today():
            return None

        # 入居条件・優遇入居者
        conditions = (
            _extract(text, r"入居(?:資格|条件|要件)[：:\s](.{10,200}?)(?=\s{2,}|$)")
            or _extract(text, r"(?:優遇|優先)(?:入居者?|対象)[：:\s](.{5,100})(?=[\s。]|$)")
        )

        # 先着順・抽選を判定 → building_type に格納
        if "先着" in text:
            selection = "先着順"
        elif "抽選" in text:
            selection = "抽選"
        else:
            selection = None

        # 申込書PDFリンク
        form_link = None
        for a in soup.find_all("a", href=True):
            if any(kw in a.get_text() for kw in ["申込書", "申請書", "様式", "PDF"]):
                form_link = _resolve_url(url, a["href"])
                break

        # データがほぼ何もない場合は除外
        if not address and not rent and not layout:
            return None

        return HousingListing(
            ward_code=self.ward_code,
            name=raw_name,
            address=address or "",
            building_type=selection,       # 先着順 or 抽選
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


# ── バリデーション ────────────────────────────────────────────────

def _is_valid_address(s: str | None) -> bool:
    if not s or len(s) < 4:
        return False
    # 受付時間・電話番号・郵便番号など除外
    if re.match(r"^[〒0-9\-（(]", s):
        return False
    if any(bad in s for bad in ["受付", "時間", "電話", "FAX", "http", "www", "@"]):
        return False
    # 数字または地名キーワードを含む
    return bool(re.search(r"\d", s)) or any(kw in s for kw in ["丁目", "番地", "番", "号", "区", "町", "村"])


# ── ユーティリティ ──────────────────────────────────────────────

def _extract(text: str, pattern: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


def _parse_yen(s: str) -> int | None:
    if not s:
        return None
    # 「〇万円」形式
    man = re.search(r"([\d.]+)万", s)
    if man:
        try:
            return int(float(man.group(1)) * 10000)
        except ValueError:
            pass
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
    if not s:
        return None
    s = s.replace("年", "-").replace("月", "-").replace("日", "").strip()
    for _ in range(1):
        try:
            parts = [int(p) for p in re.split(r"[-/]", s) if p][:3]
            if len(parts) == 3:
                return _date(*parts)
        except Exception:
            pass
    return None


def _resolve_url(base: str, href: str) -> str | None:
    if not href or href.startswith("#") or href.startswith("javascript"):
        return None
    if href.startswith("http"):
        return href
    return urljoin(base, href)
