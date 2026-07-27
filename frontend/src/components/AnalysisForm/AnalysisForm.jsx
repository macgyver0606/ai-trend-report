import { useState } from "react";
import { generateReport } from "../../services/reportApi";

function validate(form) {
  const errors = {};
  if (!form.keyword.trim()) errors.keyword = "키워드를 입력해 주세요.";
  if (!form.industry.trim()) errors.industry = "산업을 입력해 주세요.";
  return errors;
}

function getErrorMessage(error) {
  if (typeof error?.detail === "string") return error.detail;
  if (Array.isArray(error?.detail)) return error.detail.at(-1)?.msg;
  return "요청을 처리하지 못했습니다.";
}

export default function AnalysisForm({ onSearchComplete }) {
  const [form, setForm] = useState({ keyword: "", industry: "" });
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
      const result = await generateReport(form);
      onSearchComplete(result);
    } catch (error) {
      setErrors({ form: getErrorMessage(error) ?? "입력값을 다시 확인해 주세요." });
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
      <button className="search-button" type="submit" disabled={isSubmitting}>
        <span aria-hidden="true">⌕</span>{isSubmitting ? "리포트를 만들고 있어요" : "LLM 리포트 만들기"}
      </button>
      {errors.form && <p className="form-error" role="alert">{errors.form}</p>}
    </form>
  );
}
