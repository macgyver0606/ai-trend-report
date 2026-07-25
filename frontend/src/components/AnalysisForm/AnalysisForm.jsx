import { useMemo, useState } from "react";
import { searchNews } from "../../services/reportApi";

function dateValue(value) { return value.toISOString().slice(0, 10); }

function getDefaultDates() {
  const endDate = new Date();
  const startDate = new Date(endDate);
  startDate.setMonth(startDate.getMonth() - 1);
  return { start_date: dateValue(startDate), end_date: dateValue(endDate) };
}

function validate(form) {
  const errors = {};
  if (!form.keyword.trim()) errors.keyword = "키워드를 입력해 주세요.";
  if (!form.industry.trim()) errors.industry = "산업을 입력해 주세요.";
  if (!form.start_date || !form.end_date) {
    errors.period = "검색 시작일과 종료일을 선택해 주세요.";
  } else {
    const days = Math.floor((new Date(`${form.end_date}T00:00:00`) - new Date(`${form.start_date}T00:00:00`)) / 86400000) + 1;
    if (days < 7 || days > 92) errors.period = "검색 기간은 7일 이상 3개월 이하여야 합니다.";
  }
  return errors;
}

export default function AnalysisForm({ onSearchComplete }) {
  const initialForm = useMemo(() => ({ keyword: "", industry: "", ...getDefaultDates() }), []);
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange({ target: { name, value } }) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const nextErrors = validate(form);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    setIsSubmitting(true);
    try {
      const result = await searchNews(form);
      onSearchComplete(result);
    } catch (error) {
      const message = Array.isArray(error?.detail) ? error.detail.at(-1)?.msg : "요청을 처리하지 못했습니다.";
      setErrors({ form: message ?? "입력값을 다시 확인해 주세요." });
    } finally { setIsSubmitting(false); }
  }

  return (
    <form className="search-form" onSubmit={handleSubmit} noValidate>
      <div className="field field-keyword">
        <label htmlFor="keyword">관심 키워드</label>
        <input id="keyword" name="keyword" value={form.keyword} onChange={handleChange} placeholder="예: 투자, 생성형 AI" aria-describedby={errors.keyword ? "keyword-error" : undefined} />
        {errors.keyword && <span id="keyword-error" className="field-error" role="alert">{errors.keyword}</span>}
      </div>
      <div className="field field-industry">
        <label htmlFor="industry">산업군</label>
        <input id="industry" name="industry" value={form.industry} onChange={handleChange} placeholder="예: 반도체" aria-describedby={errors.industry ? "industry-error" : undefined} />
        {errors.industry && <span id="industry-error" className="field-error" role="alert">{errors.industry}</span>}
      </div>
      <div className="field field-date">
        <label htmlFor="start_date">검색 시작일</label>
        <input id="start_date" name="start_date" type="date" value={form.start_date} onChange={handleChange} />
      </div>
      <div className="field field-date">
        <label htmlFor="end_date">검색 종료일</label>
        <input id="end_date" name="end_date" type="date" value={form.end_date} onChange={handleChange} aria-describedby={errors.period ? "period-error" : undefined} />
        {errors.period && <span id="period-error" className="field-error" role="alert">{errors.period}</span>}
      </div>
      <button className="search-button" type="submit" disabled={isSubmitting}>
        <span aria-hidden="true">⌕</span>{isSubmitting ? "뉴스를 찾고 있어요" : "뉴스 검색"}
      </button>
      {errors.form && <p className="form-error" role="alert">{errors.form}</p>}
    </form>
  );
}
