import unittest

from app.services.ai.prompts import build_news_report_prompt


class NewsReportPromptTests(unittest.TestCase):
    def test_prompt_contains_only_article_data_and_evidence_ids(self):
        prompt = build_news_report_prompt(
            "투자",
            "반도체",
            [{"rank": 1, "title": "반도체 투자 확대", "summary": "설비 투자를 확대한다.", "published_at": "2026-07-25T09:00:00+09:00", "originallink": "https://news.example.com/1"}],
        )

        self.assertIn("키워드: 투자", prompt)
        self.assertIn('"id": "A01"', prompt)
        self.assertIn("입력 기사에 없는 사실은 작성하지 마세요", prompt)
