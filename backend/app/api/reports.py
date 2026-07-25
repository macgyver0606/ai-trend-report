"""리포트 요청 API입니다."""

from fastapi import APIRouter, HTTPException, status

from app.core.validators import normalize_analysis_request
from app.models.analysis_request import AnalysisRequest
from app.services.document.naver_news_service import NaverNewsSearchError, NaverNewsService


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/validate")
def validate_analysis_request(request: AnalysisRequest) -> dict:
    """분석을 시작하기 전 입력 조건을 검증한다.

    DART·RSS·LLM 연결은 다음 기능 단계에서 이 API 흐름에 추가한다.
    """
    return {
        "valid": True,
        "analysis_request": normalize_analysis_request(request),
    }


@router.post("/search")
def search_news(request: AnalysisRequest) -> dict:
    """입력 조건으로 네이버 뉴스 API를 검색하고 기간에 맞는 최신 기사 5건을 반환한다."""
    try:
        result = NaverNewsService().search(request)
    except NaverNewsSearchError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return {"analysis_request": normalize_analysis_request(request), **result}
