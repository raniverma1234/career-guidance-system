import { useEffect, useState } from "react";
import { useAuth } from "../AuthContext";
import api, { errorMessage } from "../api";
import ProgressBar from "../components/ProgressBar";
import { completeness } from "../profileUtils";

const EDUCATION = ["B.Tech", "M.Tech", "BCA", "MCA", "B.Sc", "M.Sc", "BBA", "MBA", "Diploma", "Other"];

function toForm(u) {
  const text = (v) => (v === null || v === undefined ? "" : String(v));
  return {
    name: text(u.name),
    age: text(u.age),
    education: text(u.education),
    branch: text(u.branch),
    semester: text(u.semester),
    cgpa: text(u.cgpa),
    career_goal: text(u.career_goal),
    interests: text(u.interests),
    projects: text(u.projects),
    certifications: text(u.certifications),
    experience: text(u.experience),
  };
}

// numbers: empty box -> null, otherwise a number
const num = (v) => (String(v).trim() === "" ? null : Number(v));
// text: empty box -> null
const str = (v) => (v.trim() === "" ? null : v.trim());

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [form, setForm] = useState(() => toForm(user));
  const [careers, setCareers] = useState([]);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  // the list of careers for the "career goal" box
  useEffect(() => {
    api
      .get("/careers")
      .then((res) => setCareers(res.data.map((c) => c.career_name)))
      .catch(() => setCareers([]));
  }, []);

  function update(field) {
    return (e) => {
      setForm({ ...form, [field]: e.target.value });
      setSaved(false);
    };
  }

  function validate() {
    if (form.name.trim().length < 2) return "Please enter your full name.";
    const age = num(form.age);
    if (age !== null && (age < 10 || age > 100)) return "Age must be between 10 and 100.";
    const sem = num(form.semester);
    if (sem !== null && (!Number.isInteger(sem) || sem < 1 || sem > 12)) return "Semester must be a whole number from 1 to 12.";
    const cgpa = num(form.cgpa);
    if (cgpa !== null && (cgpa < 0 || cgpa > 10)) return "CGPA must be between 0 and 10.";
    return "";
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const problem = validate();
    if (problem) {
      setError(problem);
      setSaved(false);
      return;
    }
    setError("");
    setBusy(true);
    try {
      const res = await api.put("/profile/me", {
        name: form.name.trim(),
        age: num(form.age),
        education: str(form.education),
        branch: str(form.branch),
        semester: num(form.semester),
        cgpa: num(form.cgpa),
        career_goal: str(form.career_goal),
        interests: str(form.interests),
        projects: str(form.projects),
        certifications: str(form.certifications),
        experience: str(form.experience),
      });
      updateUser(res.data);
      setSaved(true);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  // keep the current value in the lists even if it is not one of the usual choices
  const educationOptions = form.education && !EDUCATION.includes(form.education) ? [form.education, ...EDUCATION] : EDUCATION;
  const careerOptions = form.career_goal && !careers.includes(form.career_goal) ? [form.career_goal, ...careers] : careers;

  return (
    <div className="page-narrow">
      <div className="page-head">
        <h1>Your profile</h1>
        <p className="muted">The more complete your profile, the better your recommendations and roadmap.</p>
      </div>

      <ProgressBar value={completeness(form)} label="Profile completeness" />

      {saved && <div className="alert alert-success">Profile saved.</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <form className="card" onSubmit={handleSubmit} noValidate>
        <div className="form-grid">
          <div className="field full">
            <label htmlFor="name">Full name</label>
            <input id="name" value={form.name} onChange={update("name")} />
          </div>
          <div className="field">
            <label htmlFor="age">Age</label>
            <input id="age" type="number" min="10" max="100" value={form.age} onChange={update("age")} />
          </div>
          <div className="field">
            <label htmlFor="education">Education</label>
            <select id="education" value={form.education} onChange={update("education")}>
              <option value="">Select...</option>
              {educationOptions.map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="branch">Branch</label>
            <input id="branch" placeholder="CSE" value={form.branch} onChange={update("branch")} />
          </div>
          <div className="field">
            <label htmlFor="semester">Semester</label>
            <input id="semester" type="number" min="1" max="12" placeholder="7" value={form.semester} onChange={update("semester")} />
          </div>
          <div className="field">
            <label htmlFor="cgpa">CGPA</label>
            <input id="cgpa" type="number" step="0.01" min="0" max="10" placeholder="7.8" value={form.cgpa} onChange={update("cgpa")} />
          </div>
          <div className="field">
            <label htmlFor="career_goal">Career goal</label>
            <select id="career_goal" value={form.career_goal} onChange={update("career_goal")}>
              <option value="">Not decided yet</option>
              {careerOptions.map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
          </div>
          <div className="field full">
            <label htmlFor="interests">Interests</label>
            <input id="interests" placeholder="Data analysis, AI, Technology" value={form.interests} onChange={update("interests")} />
            <div className="hint">Separate with commas.</div>
          </div>
          <div className="field full">
            <label htmlFor="projects">Projects</label>
            <textarea id="projects" placeholder="Sales dashboard in Excel, Employee analytics in Python" value={form.projects} onChange={update("projects")} />
          </div>
          <div className="field full">
            <label htmlFor="certifications">Certifications</label>
            <textarea id="certifications" placeholder="Google Data Analytics (Coursera)" value={form.certifications} onChange={update("certifications")} />
          </div>
          <div className="field full">
            <label htmlFor="experience">Experience</label>
            <textarea id="experience" placeholder="Internship, training or club work" value={form.experience} onChange={update("experience")} />
          </div>
        </div>
        <button className="btn btn-primary" disabled={busy}>
          {busy ? "Saving..." : "Save profile"}
        </button>
      </form>
    </div>
  );
}
