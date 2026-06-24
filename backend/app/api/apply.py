import base64
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import Response
from sqlmodel import Session
from pydantic import BaseModel

from ..db import get_session
from ..models import HousingListing
from ..services import ApplicantProfile, fill_pdf_form, submit_application, SubmissionResult

router = APIRouter(prefix="/apply", tags=["apply"])


class ApplyRequest(BaseModel):
    listing_id: int
    profile: dict
    premium_token: str | None = None  # Google Play課金検証トークン


class ApplyResponse(BaseModel):
    success: bool
    method: str
    message: str
    receipt_number: str | None = None
    pdf_base64: str | None = None      # PDF生成時はBase64エンコードして返す


@router.post("/fill-pdf", summary="申請書PDF自動記入（無料）")
async def fill_application_pdf(
    listing_id: int,
    profile_data: dict,
    session: Session = Depends(get_session),
) -> Response:
    """
    指定の住宅の申請書PDFにユーザー情報を自動入力して返す。
    全ユーザー無料で利用可能。
    """
    listing = session.get(HousingListing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not listing.application_form_url:
        raise HTTPException(status_code=422, detail="申請書PDFのURLが登録されていません")

    profile = ApplicantProfile(profile_data)
    pdf_bytes = await fill_pdf_form(listing.application_form_url, profile)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="application_{listing_id}.pdf"'},
    )


@router.post("/submit", response_model=ApplyResponse, summary="自動申請（プレミアム）")
async def submit(
    req: ApplyRequest,
    session: Session = Depends(get_session),
) -> ApplyResponse:
    """
    住宅の申請を自動実行する。
    - 無料: PDF生成のみ（印刷・郵送は手動）
    - プレミアム: Webフォームへ自動送信
    """
    listing = session.get(HousingListing, req.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    is_premium = await _verify_premium_token(req.premium_token)
    profile = ApplicantProfile(req.profile)

    result: SubmissionResult = await submit_application(
        ward_code=listing.ward_code,
        listing_id=req.listing_id,
        profile=profile,
        is_premium=is_premium,
    )

    pdf_b64 = base64.b64encode(result.pdf_bytes).decode() if result.pdf_bytes else None

    return ApplyResponse(
        success=result.success,
        method=result.method,
        message=result.message,
        receipt_number=result.receipt_number,
        pdf_base64=pdf_b64,
    )


async def _verify_premium_token(token: str | None) -> bool:
    """
    Google Play Billing のレシートトークンを検証する。
    本番では Google Play Developer API を使って検証する。
    """
    if not token:
        return False
    # TODO: Google Play Developer API で purchaseToken を検証
    # https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.products/get
    return len(token) > 10  # 開発中はトークンが存在すれば通す
