import { useState } from "react";
import ProgressBar from "./ProgressBar";
import QuestionCard from "./QuestionCard";
import { errorMessage } from "../api";

// Shows many questions a few at a time, with Back / Next and a final Submit button.
// questions: [{ id, text, hint, options: [{ value, label }] }]
export default function QuestionFlow({ questions, pageSize, onSubmit, submitLabel = "Submit", legend }) {
  const [answers, setAnswers] = useState({});
  const [page, setPage] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const pages = Math.ceil(questions.length / pageSize);
  const answered = questions.filter((q) => answers[q.id]).length;
  const visible = questions.slice(page * pageSize, page * pageSize + pageSize);
  const isLast = page === pages - 1;

  function go(nextPage) {
    setPage(nextPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function setAnswer(id, value) {
    setAnswers({ ...answers, [id]: value });
    setError("");
  }

  async function handleSubmit() {
    const firstMissing = questions.findIndex((q) => !answers[q.id]);
    if (firstMissing !== -1) {
      setError(`${questions.length - answered} question(s) are not answered yet. Please answer all questions.`);
      go(Math.floor(firstMissing / pageSize));
      return;
    }
    setBusy(true);
    setError("");
    try {
      await onSubmit(answers);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <ProgressBar value={answered} max={questions.length} label={`${answered} of ${questions.length} answered`} />
      {legend && <p className="muted">{legend}</p>}
      {error && <div className="alert alert-error">{error}</div>}

      {visible.map((q, i) => (
        <QuestionCard
          key={q.id}
          number={page * pageSize + i + 1}
          question={q}
          value={answers[q.id]}
          onChange={(v) => setAnswer(q.id, v)}
        />
      ))}

      <div className="flow-nav">
        <button className="btn btn-outline" onClick={() => go(page - 1)} disabled={page === 0 || busy}>
          Back
        </button>
        <span className="muted">
          Page {page + 1} of {pages}
        </span>
        {isLast ? (
          <button className="btn btn-primary" onClick={handleSubmit} disabled={busy}>
            {busy ? "Saving..." : submitLabel}
          </button>
        ) : (
          <button className="btn btn-primary" onClick={() => go(page + 1)}>
            Next
          </button>
        )}
      </div>
    </>
  );
}
