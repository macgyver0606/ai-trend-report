"""LLM 뉴스 리포트의 구조화된 출력 모델입니다."""

from pydantic import BaseModel, ConfigDict, Field


class StrictReportModel(BaseModel):
    """OpenAI Structured Outputs에서 사용하는 닫힌 JSON 객체 모델입니다."""

    model_config = ConfigDict(extra="forbid")


class ReportIssue(StrictReportModel):
    title: str = Field(..., description="반복되는 핵심 이슈의 제목")
    fact_summary: str = Field(..., description="기사 근거 기반 사실 요약")
    planning_implication: str = Field(..., description="마케터·기획자 관점의 의미")
    evidence_article_ids: list[str] = Field(..., min_length=1, description="근거 기사 ID")


class ExcludedArticle(StrictReportModel):
    article_id: str
    reason: str


class NewsReport(StrictReportModel):
    overall_summary: str = Field(..., description="전체 기사 흐름을 3문장 이내로 요약")
    key_issues: list[ReportIssue] = Field(..., min_length=1, max_length=3)
    excluded_articles: list[ExcludedArticle] = Field(..., description="관련성이 낮아 제외한 기사")
    limitations: list[str] = Field(..., min_length=1, description="분석의 한계")
