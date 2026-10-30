import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

const FEATURES = [
  { icon: "🎯", title: "Career recommendations", text: "Find roles that fit your skills and interests, with a match score and an explanation." },
  { icon: "📊", title: "Skill gap analysis", text: "See what you already have, what to improve and what to learn, in priority order." },
  { icon: "🗺️", title: "Personalised roadmap", text: "A month-by-month plan that adapts to the skills you already know." },
  { icon: "🛠️", title: "Project ideas", text: "Build projects with datasets, expected output and time estimates." },
  { icon: "📄", title: "Resume analyzer", text: "Upload your resume and see missing keywords and weak sections." },
  { icon: "💬", title: "AI career assistant", text: "Ask questions and get answers based on your own profile." },
];

const STEPS = [
  "Create your profile",
  "Take the skill and interest tests",
  "Get career suggestions",
  "Follow your roadmap and track progress",
];

export default function Home() {
  const { user } = useAuth();

  return (
    <>
      <section className="hero">
        <span className="pill">AI + Machine Learning + Data Analytics</span>
        <h1>Find the career path that fits you, and the skills to get there</h1>
        <p>
          Tell us about your education, skills and interests. We suggest suitable career paths, show
          your skill gaps and build a learning roadmap with projects.
        </p>
        <div className="hero-actions">
          {user ? (
            <Link to="/dashboard" className="btn btn-primary">
              Go to my dashboard
            </Link>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary">
                Get started, it is free
              </Link>
              <Link to="/login" className="btn btn-outline">
                I already have an account
              </Link>
            </>
          )}
        </div>
      </section>

      <section className="section">
        <h2>Everything in one place</h2>
        <div className="grid-3">
          {FEATURES.map((f) => (
            <div className="card feature" key={f.title}>
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p className="muted">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>How it works</h2>
        <ol className="steps">
          {STEPS.map((s, i) => (
            <li key={s}>
              <span className="step-number">{i + 1}</span>
              <span>{s}</span>
            </li>
          ))}
        </ol>
      </section>
    </>
  );
}
