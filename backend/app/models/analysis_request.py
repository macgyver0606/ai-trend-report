"""분석 요청에 사용하는 입력 모델입니다."""

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator


MIN_PERIOD_DAYS = 7
MAX_PERIOD_DAYS = 92


class AnalysisRequest(BaseModel):
    """사용자가 제출한 분석 조건.

    기간은 시작일과 종료일을 모두 포함해 7일 이상 3개월(최대 92일) 이하여야 한다.
    """

    keyword: str = Field(..., description="분석할 자유 입력 키워드")
    industry: str = Field(..., description="분석 대상 산업")
    start_date: date = Field(..., description="검색 시작일")
    end_date: date = Field(..., description="검색 종료일")

    @field_validator("keyword", "industry")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("필수 입력 항목입니다.")
        return normalized

    @model_validator(mode="after")
    def validate_period(self) -> "AnalysisRequest":
        if self.start_date > self.end_date:
            raise ValueError("검색 시작일은 종료일보다 빠르거나 같아야 합니다.")

        period_days = (self.end_date - self.start_date).days + 1
        if not MIN_PERIOD_DAYS <= period_days <= MAX_PERIOD_DAYS:
            raise ValueError("검색 기간은 7일 이상 3개월 이하여야 합니다.")
        return self
