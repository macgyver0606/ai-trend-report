"""분석 요청 검증과 관련한 공통 함수입니다."""

from app.models.analysis_request import AnalysisRequest


def normalize_analysis_request(request: AnalysisRequest) -> dict[str, str | int]:
    """검증이 끝난 요청을 API 응답에 안전한 형식으로 변환한다."""
    return {
        "keyword": request.keyword,
        "industry": request.industry,
        "start_date": request.start_date.isoformat(),
        "end_date": request.end_date.isoformat(),
    }
