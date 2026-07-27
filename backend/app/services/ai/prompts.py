"""뉴스 기반 LLM 리포트 프롬프트입니다."""

import json
from typing import Any


SYSTEM_PROMPT = """
당신은 마케터와 기획자를 위한 한국 산업 뉴스 분석 도우미입니다.
제공된 기사 데이터만 근거로 분석하고, 기사에 없는 사실·수치·원인·전망을 추측하지 마세요.
사실 요약과 해석을 구분하고, 모든 핵심 이슈에 근거 기사 ID를 하나 이상 연결하세요.
제목과 요약만으로 판단하기 어려운 경우에는 단정하지 말고 한계에 기록하세요.
응답은 반드시 요청받은 JSON 형식만 사용하며 한국어로 작성하세요.
""".strip()


def build_news_report_prompt(keyword: str, industry: str, articles: list[dict[str, Any]]) -> str:
    """검색 결과를 근거 ID가 있는 LLM 입력으로 정리한다."""
    prompt_articles = [
        {"id": f"A{article['rank']:02d}", "title": article["title"], "summary": article["summary"], "published_at": article["published_at"], "url": article["originallink"]}
        for article in articles
    ]
    return f"""
[분석 조건]
- 키워드: {keyword}
- 산업군: {industry}
- 데이터 소스: 네이버 뉴스
- 정렬 기준: 최신순
- 분석 기사 수: {len(prompt_articles)}건

[기사 목록]
{json.dumps(prompt_articles, ensure_ascii=False)}

[분석 작업]
1. 전체 기사 흐름을 3문장 이내로 요약하세요.
2. 반복되는 핵심 이슈를 최대 3개 도출하세요.
3. 각 이슈에 기사 근거 기반 사실 요약과 마케터·기획자 관점의 의미를 작성하세요.
4. 키워드 또는 산업군과 직접 관련성이 낮은 기사는 제외하고 이유를 작성하세요.
5. 기사 제목과 요약만 사용했으므로 분석 한계를 반드시 작성하세요.

[중요 규칙]
- 입력 기사에 없는 사실은 작성하지 마세요.
- 모든 핵심 이슈에는 기사 ID를 하나 이상 연결하세요.
- 기사 ID는 A01 형식의 입력값만 사용하세요.
""".strip()
