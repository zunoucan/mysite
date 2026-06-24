"""
自動申請サービス（プレミアム機能）
Playwright を使ってWebフォームへの自動送信を行う。
現在は各区のフォームURLと送信フィールドのマッピングが必要。
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .form_filler import ApplicantProfile


class SubmissionMethod(str, Enum):
    WEB_FORM = "web_form"       # Webフォーム送信
    PDF_MAIL = "pdf_mail"       # PDF生成 → メール（半自動）
    PDF_DOWNLOAD = "pdf_download"  # PDF生成 → ダウンロード（手動郵送）


@dataclass
class SubmissionResult:
    success: bool
    method: SubmissionMethod
    message: str
    receipt_number: Optional[str] = None
    pdf_bytes: Optional[bytes] = None


# 各区の申請方法マッピング
WARD_SUBMISSION_CONFIG: dict[str, dict] = {
    "shinjuku": {
        "method": SubmissionMethod.WEB_FORM,
        "form_url": "https://www.city.shinjuku.lg.jp/application/",
        "fields": {
            "name": "applicant_name",
            "kana": "applicant_kana",
            "birth": "birth_date",
            "address": "current_address",
            "phone": "phone_number",
        },
        "submit_button": "input[type=submit]",
    },
    "setagaya": {
        "method": SubmissionMethod.PDF_DOWNLOAD,
        "form_url": "https://www.city.setagaya.lg.jp/documents/form.pdf",
    },
    # 他の区は調査後に追加
}

# デフォルト：PDF生成のみ（郵送・窓口申請が多い区向け）
DEFAULT_SUBMISSION: dict = {
    "method": SubmissionMethod.PDF_DOWNLOAD,
}


async def submit_application(
    ward_code: str,
    listing_id: int,
    profile: ApplicantProfile,
    is_premium: bool,
) -> SubmissionResult:
    """
    申請を実行する。
    - is_premium=False: PDF生成のみ（ダウンロード用）
    - is_premium=True:  設定に応じてWebフォーム送信 or PDF+メール
    """
    config = WARD_SUBMISSION_CONFIG.get(ward_code, DEFAULT_SUBMISSION)
    method = config.get("method", SubmissionMethod.PDF_DOWNLOAD)

    if not is_premium and method == SubmissionMethod.WEB_FORM:
        # 非プレミアムはWebフォーム自動送信不可 → PDF生成に降格
        method = SubmissionMethod.PDF_DOWNLOAD

    if method == SubmissionMethod.PDF_DOWNLOAD:
        return await _generate_pdf_only(ward_code, listing_id, profile, config)
    elif method == SubmissionMethod.WEB_FORM:
        return await _submit_web_form(ward_code, listing_id, profile, config)
    else:
        return SubmissionResult(
            success=False,
            method=method,
            message="この区の自動申請方法はまだサポートされていません。",
        )


async def _generate_pdf_only(ward_code, listing_id, profile, config) -> SubmissionResult:
    from .form_filler import fill_pdf_form
    form_url = config.get("form_url")
    if not form_url:
        return SubmissionResult(
            success=False,
            method=SubmissionMethod.PDF_DOWNLOAD,
            message="申請書PDFのURLが設定されていません。",
        )
    try:
        pdf_bytes = await fill_pdf_form(form_url, profile)
        return SubmissionResult(
            success=True,
            method=SubmissionMethod.PDF_DOWNLOAD,
            message="申請書PDFを生成しました。印刷して郵送または窓口へご提出ください。",
            pdf_bytes=pdf_bytes,
        )
    except Exception as e:
        return SubmissionResult(
            success=False,
            method=SubmissionMethod.PDF_DOWNLOAD,
            message=f"PDF生成に失敗しました: {e}",
        )


async def _submit_web_form(ward_code, listing_id, profile, config) -> SubmissionResult:
    """Playwright でWebフォームを自動送信（プレミアム限定）"""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(config["form_url"], timeout=30000)

            # フィールドへの入力
            field_map = config.get("fields", {})
            profile_data = {
                "name": profile.full_name,
                "kana": profile.full_name_kana,
                "birth": profile.birth_date,
                "address": profile.address,
                "phone": profile.phone,
                "email": profile.email,
            }
            for key, selector in field_map.items():
                value = profile_data.get(key, "")
                if value:
                    try:
                        await page.fill(f"[name={selector}]", value)
                    except Exception:
                        pass

            # 送信
            submit_sel = config.get("submit_button", "input[type=submit]")
            await page.click(submit_sel)
            await page.wait_for_load_state("networkidle", timeout=15000)

            # 受付番号の取得（ページから抽出）
            receipt = None
            import re
            body = await page.inner_text("body")
            m = re.search(r"受付番号[：:\s]*([\w\-]+)", body)
            if m:
                receipt = m.group(1)

            await browser.close()
            return SubmissionResult(
                success=True,
                method=SubmissionMethod.WEB_FORM,
                message="申請が完了しました。",
                receipt_number=receipt,
            )
    except Exception as e:
        return SubmissionResult(
            success=False,
            method=SubmissionMethod.WEB_FORM,
            message=f"自動申請に失敗しました: {e}",
        )
