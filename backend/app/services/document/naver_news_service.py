"""NAVER API HUB 뉴스 검색 연동 서비스입니다."""

import json
import os
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.models.analysis_request import AnalysisRequest


NAVER_NEWS_ENDPOINT = "https://naverapihub.apigw.ntruss.com/search/v1/news"
MAX_ARTICLE_COUNT = 10
MAX_SUMMARY_LENGTH = 180
REQUEST_TIMEOUT_SECONDS = 10
SEARCH_SORT_ORDER = "date"
RESPONSE_FORMAT = "json"


class NaverNewsSearchError(RuntimeError):
    """네이버 뉴스 API를 호출할 수 없을 때 사용합니다."""


def _strip_highlight_tags(value: str) -> str:
    return " ".join(unescape(re.sub(r"</?b>", "", value)).split())


def _to_compact_summary(value: str) -> str:
    """검색 API의 기사 설명을 화면용 핵심 요약 길이로 정리한다."""
    normalized = _strip_highlight_tags(value)
    if len(normalized) <= MAX_SUMMARY_LENGTH:
        return normalized
    sentence_end = max(normalized.rfind(mark, 0, MAX_SUMMARY_LENGTH) for mark in (".", "!", "?"))
    if sentence_end > MAX_SUMMARY_LENGTH // 2:
        return normalized[: sentence_end + 1]
    return f"{normalized[:MAX_SUMMARY_LENGTH].rstrip()}…"


def _parse_pub_date(value: str) -> datetime:
    return parsedate_to_datetime(value)


class NaverNewsService:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None) -> None:
        self.client_id = client_id or os.getenv("NAVER_API_HUB_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("NAVER_API_HUB_CLIENT_SECRET")

    def search(self, analysis_request: AnalysisRequest) -> dict[str, Any]:
        if not self.client_id or not self.client_secret:
            raise NaverNewsSearchError("네이버 뉴스 검색 API 인증 정보가 설정되지 않았습니다.")

        search_query = f"{analysis_request.industry} {analysis_request.keyword}"
        articles: list[dict[str, str | int]] = []
        seen_urls: set[str] = set()
        payload = self._request_page(query=search_query)
        for item in payload.get("items", []):
            article = self._to_article(item, rank=len(articles) + 1)
            if article is None or article["originallink"] in seen_urls:
                continue
            seen_urls.add(article["originallink"])
            articles.append(article)
            if len(articles) == MAX_ARTICLE_COUNT:
                break

        return {
            "query": search_query,
            "sort": SEARCH_SORT_ORDER,
            "ranking_basis": "네이버 뉴스 API 최신순 결과",
            "articles": articles,
            "article_count": len(articles),
        }

    def _request_page(self, query: str) -> dict[str, Any]:
        url = f"{NAVER_NEWS_ENDPOINT}?{urlencode(self._build_query_params(query))}"
        request = Request(
            url,
            headers={
                "X-NCP-APIGW-API-KEY-ID": self.client_id,
                "X-NCP-APIGW-API-KEY": self.client_secret,
            },
        )
        try:
            with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise NaverNewsSearchError("네이버 뉴스 검색 결과를 가져오지 못했습니다.") from error

    @staticmethod
    def _build_query_params(query: str) -> dict[str, str | int]:
        return {
            "query": query,
            "display": MAX_ARTICLE_COUNT,
            "start": 1,
            "sort": SEARCH_SORT_ORDER,
            "format": RESPONSE_FORMAT,
        }

    @staticmethod
    def _to_article(item: dict[str, Any], rank: int) -> dict[str, str | int] | None:
        try:
            published_at = _parse_pub_date(item["pubDate"])
        except (KeyError, TypeError, ValueError):
            return None

        original_link = item.get("originallink") or item.get("link")
        if not original_link:
            return None

        return {
            "rank": rank,
            "title": _strip_highlight_tags(item.get("title", "")),
            "summary": _to_compact_summary(item.get("description", "")),
            "published_at": published_at.isoformat(),
            "originallink": original_link,
            "naver_link": item.get("link", original_link),
        }
