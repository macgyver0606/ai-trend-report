"""분석 요청에 사용하는 입력 모델입니다."""

from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    """사용자가 제출한 뉴스 검색 조건."""

    keyword: str = Field(..., description="분석할 자유 입력 키워드")
    industry: str = Field(..., description="분석 대상 산업")

    @field_validator("keyword", "industry")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("필수 입력 항목입니다.")
        return normalized
