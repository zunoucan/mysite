"""
申請書自動記入サービス
PDF申請書・Webフォームへのユーザー情報自動入力を担う。
"""
import io
from pathlib import Path
from typing import Any
import httpx
from pypdf import PdfReader, PdfWriter


class ApplicantProfile:
    """応募者情報モデル（Androidアプリから受け取るJSON相当）"""
    def __init__(self, data: dict[str, Any]):
        self.full_name: str = data.get("full_name", "")
        self.full_name_kana: str = data.get("full_name_kana", "")
        self.birth_date: str = data.get("birth_date", "")       # YYYY-MM-DD
        self.gender: str = data.get("gender", "")               # 男/女
        self.postal_code: str = data.get("postal_code", "")
        self.address: str = data.get("address", "")
        self.phone: str = data.get("phone", "")
        self.email: str = data.get("email", "")
        self.household_members: int = data.get("household_members", 1)
        self.income_yen: int = data.get("income_yen", 0)
        self.currently_renting: bool = data.get("currently_renting", False)
        self.occupation: str = data.get("occupation", "")
        self.workplace: str = data.get("workplace", "")
        self.extra: dict = data.get("extra", {})


async def fill_pdf_form(pdf_url: str, profile: ApplicantProfile) -> bytes:
    """
    PDFフォームをダウンロードしてユーザー情報を自動記入して返す。
    フォームフィールドがある場合はフィールドに書き込み、
    ない場合はオーバーレイテキストとして描画する。
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(pdf_url)
        resp.raise_for_status()
        pdf_bytes = resp.content

    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # PDFフォームフィールドに値をセット
    field_mapping = _build_field_mapping(profile)
    try:
        writer.update_page_form_field_values(writer.pages[0], field_mapping)
    except Exception:
        # フィールドなし → reportlabでテキストオーバーレイ
        return _overlay_text(pdf_bytes, profile)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def _build_field_mapping(profile: ApplicantProfile) -> dict[str, str]:
    """PDF標準フィールド名 → 値のマッピング（区ごとに異なる名称を正規化）"""
    return {
        # よく使われるフィールド名パターン
        "氏名": profile.full_name,
        "name": profile.full_name,
        "Name": profile.full_name,
        "ふりがな": profile.full_name_kana,
        "kana": profile.full_name_kana,
        "生年月日": profile.birth_date,
        "birth": profile.birth_date,
        "性別": profile.gender,
        "郵便番号": profile.postal_code,
        "postal": profile.postal_code,
        "住所": profile.address,
        "address": profile.address,
        "電話番号": profile.phone,
        "phone": profile.phone,
        "tel": profile.phone,
        "メールアドレス": profile.email,
        "email": profile.email,
        "世帯人数": str(profile.household_members),
        "収入": str(profile.income_yen),
        "勤務先": profile.workplace,
        "職業": profile.occupation,
        **profile.extra,
    }


def _overlay_text(pdf_bytes: bytes, profile: ApplicantProfile) -> bytes:
    """reportlabでPDF上にテキストをオーバーレイ（フォームフィールドなしのケース）"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        import pypdf

        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        c.setFont("Helvetica", 10)
        # 固定座標への書き込みは区ごとに異なるため、ここでは汎用的な位置に記載
        # 実際の運用では各区の申請書テンプレートに合わせた座標マッピングが必要
        c.drawString(100, 700, f"氏名: {profile.full_name}")
        c.drawString(100, 685, f"ふりがな: {profile.full_name_kana}")
        c.drawString(100, 670, f"生年月日: {profile.birth_date}")
        c.drawString(100, 655, f"住所: {profile.address}")
        c.drawString(100, 640, f"電話: {profile.phone}")
        c.save()
        packet.seek(0)

        overlay = pypdf.PdfReader(packet)
        writer = pypdf.PdfWriter()
        base = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        page = base.pages[0]
        page.merge_page(overlay.pages[0])
        writer.add_page(page)
        for p in base.pages[1:]:
            writer.add_page(p)

        out = io.BytesIO()
        writer.write(out)
        return out.getvalue()
    except Exception as e:
        raise RuntimeError(f"PDF overlay failed: {e}") from e
