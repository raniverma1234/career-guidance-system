import { useEffect, useState } from "react";
import { useAuth } from "../AuthContext";
import api from "../api";

const COMING_NEXT = [
  "Profile and skill assessment",
  "Interest test",
  "Career recommendations",
  "Skill gaps, comparison and roadmap",
  "Projects and progress tracker",
  "Resume analyzer and role explorer",
  "AI career assistant",
];

// small check that the website can talk to the backend
function BackendStatus() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    api
      .get("/")
      .then(() => setStatus("ok"))
      .catch(() => setStatus("error"));
  }, []);

  if (status === "checking") return <span className="badge">Checking...</span>;
  if (status === "ok") return <span className="badge badge-ok">Connected</span>;
  return <span className="badge badge-bad">Not reachable</span>;
}

export default function Dashboard() {
  const { user } = useAuth();

  return (
    <>
      <h1>Welcome, {user.name.split(" ")[0]}!</h1>
      <p className="muted">
        Your account is ready. The next steps of the website are being added one by one.
      </p>

      <div className="grid-2">
        <div className="card">
          <h3>Your account</h3>
          <dl className="details">
            <dt>Name</dt>
            <dd>{user.name}</dd>
            <dt>Email</dt>
            <dd>{user.email}</dd>
            <dt>Role</dt>
            <dd>
              <span className="badge">{user.role}</span>
            </dd>
            <dt>Backend</dt>
            <dd>
              <BackendStatus />
            </dd>
          </dl>
        </div>

        <div className="card">
          <h3>Coming next</h3>
          <ul className="checklist">
            {COMING_NEXT.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
}
