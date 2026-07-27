import json
import unittest
from unittest.mock import MagicMock, patch

from app.models.analysis_request import AnalysisRequest
from app.services.document.naver_news_service import NaverNewsService


class NaverNewsServiceTests(unittest.TestCase):
    def test_search_returns_latest_articles_with_compact_summary(self):
        payload = {
            "items": [
                {"title": "<b>AI</b> 반도체", "description": "<b>반도체</b> 기사", "pubDate": "Fri, 24 Jul 2026 09:00:00 +0900", "originallink": "https://news.example.com/1", "link": "https://n.news.naver.com/1"},
                {"title": "중복 기사", "description": "중복", "pubDate": "Fri, 24 Jul 2026 08:00:00 +0900", "originallink": "https://news.example.com/1", "link": "https://n.news.naver.com/1"},
                {"title": "두 번째 기사", "description": "핵심 내용을 전달하는 기사 요약입니다.", "pubDate": "Mon, 01 Jun 2026 08:00:00 +0900", "originallink": "https://news.example.com/2", "link": "https://n.news.naver.com/2"},
            ]
        }
        response = MagicMock()
        response.read.return_value = json.dumps(payload).encode("utf-8")
        response.__enter__.return_value = response
        request = AnalysisRequest(keyword="AI", industry="반도체")

        with patch("app.services.document.naver_news_service.urlopen", return_value=response):
            result = NaverNewsService("id", "secret").search(request)

        self.assertEqual(result["article_count"], 2)
        self.assertEqual(result["articles"][0]["title"], "AI 반도체")
        self.assertEqual(result["articles"][0]["summary"], "반도체 기사")
        self.assertEqual(result["articles"][0]["rank"], 1)

    def test_to_article_skips_an_item_without_a_valid_publish_date(self):
        article = NaverNewsService._to_article(
            {"title": "발행일 없는 기사", "originallink": "https://news.example.com/1"},
            rank=1,
        )

        self.assertIsNone(article)
