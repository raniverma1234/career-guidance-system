import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errorMessage } from "../api";
import Bars from "../components/Bars";
import QuestionFlow from "../components/QuestionFlow";

function normalize(q) {
  return {
    id: q.id,
    text: q.text,
    hint: q.type === "rating" ? "1 = not comfortable, 5 = very comfortable" : "",
    options: q.options.map((o) => ({ value: o, label: o })),
  };
}

export default function SkillAssessment() {
  const [state, setState] = useState({ loading: true, error: "", questions: [], saved: [] });
  const [result, setResult] = useState(null); // levels right after submitting
  const [retake, setRetake] = useState(false);

  useEffect(() => {
    Promise.all([api.get("/assessment/questions"), api.get("/profile/skills")])
      .then(([q, s]) =>
        setState({ loading: false, error: "", questions: q.data.skill_questions.map(normalize), saved: s.data })
      )
      .catch((err) => setState({ loading: false, error: errorMessage(err), questions: [], saved: [] }));
  }, []);

  async function submit(answers) {
    const body = Object.entries(answers).map(([question_id, answer]) => ({ question_id, answer }));
    const res = await api.post("/assessment/skills", body);
    setResult(res.data.skills.map((s) => ({ label: s.skill_name, value: s.level })));
    setRetake(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (state.loading) return <div className="center-note">Loading questions...</div>;
  if (state.error) return <div className="alert alert-error">{state.error}</div>;

  const shown = result || (state.saved.length ? state.saved.map((s) => ({ label: s.skill_name, value: s.level })) : null);

  return (
    <div className="page-narrow">
      <div className="page-head">
        <h1>Skill assessment</h1>
        <p className="muted">
          Answer honestly. Your answers decide your skill levels, which are used for career matches, skill gaps and
          your roadmap.
        </p>
      </div>

      {shown && !retake ? (
        <div className="card">
          <h2>Your skill levels</h2>
          <p className="muted">Levels are calculated from your answers (0 to 10).</p>
          <Bars items={[...shown].sort((a, b) => b.value - a.value)} max={10} suffix="/10" />
          <div className="result-actions">
            <Link to="/assessment/interests" className="btn btn-primary">
              Next: interest test
            </Link>
            <button className="btn btn-outline" onClick={() => setRetake(true)}>
              Retake the test
            </button>
          </div>
        </div>
      ) : (
        <>
          {shown && <div className="alert alert-info">Submitting again replaces your earlier answers.</div>}
          <QuestionFlow questions={state.questions} pageSize={7} onSubmit={submit} submitLabel="Submit answers" />
        </>
      )}
    </div>
  );
}
