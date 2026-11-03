import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errorMessage } from "../api";
import Bars from "../components/Bars";
import QuestionFlow from "../components/QuestionFlow";

function normalize(q) {
  return {
    id: q.id,
    text: q.text,
    hint: "",
    options: q.options.map((o) => ({ value: o, label: o })),
  };
}

export default function InterestAssessment() {
  const [state, setState] = useState({ loading: true, error: "", questions: [], saved: null });
  const [result, setResult] = useState(null);
  const [retake, setRetake] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get("/assessment/questions"),
      api.get("/assessment/interests/result").catch(() => null), // 404 = not taken yet
    ])
      .then(([q, r]) =>
        setState({
          loading: false,
          error: "",
          questions: q.data.interest_questions.map(normalize),
          saved: r ? r.data.interests : null,
        })
      )
      .catch((err) => setState({ loading: false, error: errorMessage(err), questions: [], saved: null }));
  }, []);

  async function submit(answers) {
    const body = Object.entries(answers).map(([question_id, answer]) => ({ question_id, answer }));
    const res = await api.post("/assessment/interests", body);
    setResult(res.data.interests);
    setRetake(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (state.loading) return <div className="center-note">Loading questions...</div>;
  if (state.error) return <div className="alert alert-error">{state.error}</div>;

  const shown = result || state.saved;

  return (
    <div className="page-narrow">
      <div className="page-head">
        <h1>Interest test</h1>
        <p className="muted">There are no right or wrong answers. Tell us what you enjoy.</p>
      </div>

      {shown && !retake ? (
        <div className="card">
          <h2>Your interests</h2>
          <p className="muted">How strongly each area matches what you enjoy.</p>
          <Bars items={shown.map((i) => ({ label: i.area, value: i.percent }))} max={100} suffix="%" />
          <div className="result-actions">
            <Link to="/dashboard" className="btn btn-primary">
              Back to dashboard
            </Link>
            <button className="btn btn-outline" onClick={() => setRetake(true)}>
              Retake the test
            </button>
          </div>
        </div>
      ) : (
        <>
          {shown && <div className="alert alert-info">Submitting again replaces your earlier answers.</div>}
          <QuestionFlow
            questions={state.questions}
            pageSize={5}
            onSubmit={submit}
            submitLabel="See my interests"
            legend="1 = strongly disagree, 5 = strongly agree"
          />
        </>
      )}
    </div>
  );
}
