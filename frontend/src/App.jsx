import { useState } from "react";

import AnalysisForm from "./components/AnalysisForm/AnalysisForm";

export default function App() {
  const [searchResult, setSearchResult] = useState(null);

  return (
    <main className="app-shell">
      <header className="hero">
        <div className="brand-mark" aria-hidden="true"><span>✦</span></div>
        <div>
          <p className="eyebrow">MARKET INTELLIGENCE</p>
          <h1>뉴스 &amp; 트렌드 리포트</h1>
          <p className="hero-copy">필요한 산업 뉴스만 모아, 빠르게 시장의 흐름을 살펴보세요.</p>
        </div>
      </header>

      <section className="search-panel" aria-labelledby="search-heading">
        <div className="section-heading">
          <div>
            <p className="section-kicker">01 · SEARCH</p>
            <h2 id="search-heading">검색 조건 설정</h2>
          </div>
          <p className="help-text">최근 한 달이 기본으로 설정돼요.</p>
        </div>
        <AnalysisForm onSearchComplete={setSearchResult} />
      </section>

      {searchResult && (
        <section className="result-section" aria-live="polite" aria-labelledby="result-heading">
          <div className="result-header">
            <div>
              <p className="section-kicker">02 · RESULTS</p>
              <h2 id="result-heading">뉴스 검색 결과</h2>
              <p className="result-query"><strong>{searchResult.query}</strong>에 관한 최신 뉴스예요.</p>
            </div>
            <div className="result-meta">
              <span className="count-badge">{searchResult.article_count}건</span>
              <span className="sort-label">최신순</span>
            </div>
          </div>
          {searchResult.articles.length === 0 ? (
            <div className="empty-state"><span aria-hidden="true">⌕</span><h3>조건에 맞는 뉴스가 없어요.</h3><p>키워드를 조금 더 넓게 바꾸거나 검색 기간을 늘려 보세요.</p></div>
          ) : (
            <ol className="article-list">
              {searchResult.articles.map((article) => (
                <li className="article-card" key={article.originallink}>
                  <span className="article-rank">{String(article.rank).padStart(2, "0")}</span>
                  <div className="article-content">
                    <p className="article-date">{article.published_at.slice(0, 10)}</p>
                    <a href={article.originallink} target="_blank" rel="noreferrer">{article.title}<span className="external-link" aria-label="새 탭에서 열기">↗</span></a>
                    <p>{article.description || "기사 요약이 제공되지 않았습니다."}</p>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </section>
      )}
    </main>
  );
}
