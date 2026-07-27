"""OpenAI를 이용해 뉴스 검색 결과에서 구조화된 리포트를 생성합니다."""

import os
from typing import Any

from app.models.report import NewsReport
from app.services.ai.prompts import SYSTEM_PROMPT, build_news_report_prompt


class LLMReportError(RuntimeError):
    """LLM 리포트를 생성할 수 없을 때 사용합니다."""


class ReportGenerationService:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL")

    def generate(self, keyword: str, industry: str, articles: list[dict[str, Any]]) -> NewsReport:
        if not self.api_key or not self.model:
            raise LLMReportError("LLM 리포트 설정이 없습니다. OPENAI_API_KEY와 OPENAI_MODEL을 확인해 주세요.")
        if not articles:
            raise LLMReportError("분석할 뉴스 기사가 없습니다.")

        try:
            from openai import APIError, APITimeoutError, OpenAI
        except ImportError as error:
            raise LLMReportError("OpenAI SDK가 설치되지 않았습니다.") from error

        try:
            response = OpenAI(api_key=self.api_key).responses.parse(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=build_news_report_prompt(keyword, industry, articles),
                text_format=NewsReport,
                store=False,
            )
            report = response.output_parsed
            if report is None:
                raise ValueError("구조화된 LLM 응답이 비어 있습니다.")
        except (APIError, APITimeoutError, TypeError, ValueError) as error:
            raise LLMReportError("LLM 리포트를 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.") from error

        self._validate_evidence_ids(report, articles)
        return report

    @staticmethod
    def _validate_evidence_ids(report: NewsReport, articles: list[dict[str, Any]]) -> None:
        valid_ids = {f"A{article['rank']:02d}" for article in articles}
        for issue in report.key_issues:
            if not set(issue.evidence_article_ids).issubset(valid_ids):
                raise LLMReportError("LLM 응답에 존재하지 않는 기사 근거 ID가 포함되었습니다.")
        for excluded in report.excluded_articles:
            if excluded.article_id not in valid_ids:
                raise LLMReportError("LLM 응답에 존재하지 않는 제외 기사 ID가 포함되었습니다.")
