"""NAVER API HUB 뉴스 검색 연동 서비스입니다."""

import json
import os
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.models.analysis_request import AnalysisRequest


NAVER_NEWS_URL = "https://naverapihub.apigw.ntruss.com/search/v1/news"
PAGE_SIZE = 100
MAX_SEARCH_RESULTS = 1_000
MAX_SELECTED_ARTICLES = 5


class NaverNewsSearchError(RuntimeError):
    """네이버 뉴스 API를 호출할 수 없을 때 사용합니다."""


def _strip_highlight_tags(value: str) -> str:
    return re.sub(r"</?b>", "", value).strip()


def _parse_pub_date(value: str) -> datetime:
    return parsedate_to_datetime(value)


class NaverNewsService:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None) -> None:
        self.client_id = client_id or os.getenv("NAVER_API_HUB_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("NAVER_API_HUB_CLIENT_SECRET")

    def search(self, analysis_request: AnalysisRequest) -> dict[str, Any]:
        if not self.client_id or not self.client_secret:
            raise NaverNewsSearchError("네이버 뉴스 검색 API 인증 정보가 설정되지 않았습니다.")

        query = f"{analysis_request.industry} {analysis_request.keyword}"
        matched_articles: list[dict[str, str | int]] = []
        seen_urls: set[str] = set()
        reached_start_date = False

        for start in range(1, MAX_SEARCH_RESULTS + 1, PAGE_SIZE):
            payload = self._request_page(query=query, start=start)
            items = payload.get("items", [])
            if not items:
                break

            for item in items:
                try:
                    published_at = _parse_pub_date(item["pubDate"])
                except (KeyError, TypeError, ValueError):
                    continue

                published_date = published_at.date()
                if published_date < analysis_request.start_date:
                    reached_start_date = True
                    continue
                if published_date > analysis_request.end_date:
                    continue

                original_link = item.get("originallink") or item.get("link")
                if not original_link or original_link in seen_urls:
                    continue
                seen_urls.add(original_link)

                matched_articles.append(
                    {
                        "rank": len(matched_articles) + 1,
                        "title": _strip_highlight_tags(item.get("title", "")),
                        "description": _strip_highlight_tags(item.get("description", "")),
                        "published_at": published_at.isoformat(),
                        "originallink": original_link,
                        "naver_link": item.get("link", original_link),
                    }
                )
                if len(matched_articles) == MAX_SELECTED_ARTICLES:
                    break

            if len(matched_articles) == MAX_SELECTED_ARTICLES or reached_start_date or len(items) < PAGE_SIZE:
                break

        return {
            "query": query,
            "sort": "date",
            "ranking_basis": "네이버 뉴스 API 최신순 결과",
            "articles": matched_articles,
            "article_count": len(matched_articles),
        }

    def _request_page(self, query: str, start: int) -> dict[str, Any]:
        url = f"{NAVER_NEWS_URL}?{urlencode({'query': query, 'display': PAGE_SIZE, 'start': start, 'sort': 'date', 'format': 'json'})}"
        request = Request(
            url,
            headers={
                "X-NCP-APIGW-API-KEY-ID": self.client_id,
                "X-NCP-APIGW-API-KEY": self.client_secret,
            },
        )
        try:
            with urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise NaverNewsSearchError("네이버 뉴스 검색 결과를 가져오지 못했습니다.") from error
