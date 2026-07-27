"""리포트 요청 API입니다."""

from fastapi import APIRouter

from app.core.validators import normalize_analysis_request
from app.models.analysis_request import AnalysisRequest
from app.services.ai.report_generation_service import LLMReportError, ReportGenerationService
from app.services.document.naver_news_service import NaverNewsSearchError, NaverNewsService
from app.utils.errors import raise_upstream_service_error


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
    """입력 조건으로 네이버 최신 뉴스 10건을 검색한다."""
    try:
        search_result = NaverNewsService().search(request)
    except NaverNewsSearchError as error:
        raise_upstream_service_error(error)

    return {"analysis_request": normalize_analysis_request(request), **search_result}


@router.post("/generate")
def generate_report(request: AnalysisRequest) -> dict:
    """최신 뉴스 10건을 수집하고 근거가 연결된 LLM 리포트를 생성한다."""
    try:
        search_result = NaverNewsService().search(request)
        if not search_result["articles"]:
            return {
                "analysis_request": normalize_analysis_request(request),
                **search_result,
                "report": None,
            }
        report = ReportGenerationService().generate(request.keyword, request.industry, search_result["articles"])
    except (NaverNewsSearchError, LLMReportError) as error:
        raise_upstream_service_error(error)

    return {
        "analysis_request": normalize_analysis_request(request),
        **search_result,
        "report": report.model_dump(),
    }
