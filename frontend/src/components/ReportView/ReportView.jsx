export default function ReportView({ report }) {
  if (!report) return null;

  return (
    <section className="report-section" aria-labelledby="report-heading">
      <p className="section-kicker">03 · REPORT</p>
      <h2 id="report-heading">LLM 핵심 리포트</h2>
      <p className="report-summary">{report.overall_summary}</p>
      <div className="issue-grid">
        {report.key_issues.map((issue) => (
          <article className="issue-card" key={issue.title}>
            <h3>{issue.title}</h3>
            <p><strong>사실 요약</strong>{issue.fact_summary}</p>
            <p><strong>기획 시사점</strong>{issue.planning_implication}</p>
            <div className="evidence-list">{issue.evidence_article_ids.map((id) => <span key={id}>{id}</span>)}</div>
          </article>
        ))}
      </div>
      <div className="report-limits"><strong>분석 한계</strong><ul>{report.limitations.map((item) => <li key={item}>{item}</li>)}</ul></div>
    </section>
  );
}
