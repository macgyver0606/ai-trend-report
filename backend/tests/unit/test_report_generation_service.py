import unittest
from unittest.mock import MagicMock, patch

from app.models.report import NewsReport
from app.services.ai.report_generation_service import ReportGenerationService


class ReportSchemaTests(unittest.TestCase):
    def test_schema_forbids_unknown_properties_at_every_object_level(self):
        schema = NewsReport.model_json_schema()

        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["$defs"]["ReportIssue"]["additionalProperties"])
        self.assertFalse(schema["$defs"]["ExcludedArticle"]["additionalProperties"])


class ReportGenerationServiceTests(unittest.TestCase):
    def test_generate_uses_responses_parse_with_pydantic_model(self):
        report = NewsReport(
            overall_summary="반도체 투자 확대 흐름입니다.",
            key_issues=[
                {
                    "title": "투자 확대",
                    "fact_summary": "설비 투자가 확대되고 있습니다.",
                    "planning_implication": "공급망 대응을 검토해야 합니다.",
                    "evidence_article_ids": ["A01"],
                }
            ],
            excluded_articles=[],
            limitations=["검색 결과 기사만 분석했습니다."],
        )
        parsed_response = MagicMock(output_parsed=report)
        client = MagicMock()
        client.responses.parse.return_value = parsed_response
        articles = [
            {
                "rank": 1,
                "title": "반도체 투자 확대",
                "summary": "설비 투자를 확대한다.",
                "published_at": "2026-07-25T09:00:00+09:00",
                "originallink": "https://news.example.com/1",
            }
        ]

        with patch("openai.OpenAI", return_value=client):
            result = ReportGenerationService(api_key="test-key", model="gpt-5.4-nano").generate("투자", "반도체", articles)

        self.assertEqual(result, report)
        client.responses.parse.assert_called_once()
        request = client.responses.parse.call_args.kwargs
        self.assertEqual(request["model"], "gpt-5.4-nano")
        self.assertIs(request["text_format"], NewsReport)
        self.assertTrue(request["store"] is False)
