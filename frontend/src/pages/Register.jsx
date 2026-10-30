import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { errorMessage } from "../api";

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", age: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  // same rules as the backend, so students see problems before sending
  function validate() {
    if (form.name.trim().length < 2) return "Please enter your full name.";
    if (!/^\S+@\S+\.\S+$/.test(form.email.trim())) return "Please enter a valid email address.";
    if (form.age && (Number(form.age) < 10 || Number(form.age) > 100)) return "Age must be between 10 and 100.";
    if (form.password.length < 6) return "Password must be at least 6 characters.";
    if (form.password !== form.confirm) return "The two passwords do not match.";
    return "";
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const problem = validate();
    if (problem) {
      setError(problem);
      return;
    }
    setError("");
    setBusy(true);
    try {
      await register(form);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card auth-card">
      <h1>Create your account</h1>
      <p className="muted">It takes a minute. Then we build your career plan.</p>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="name">Full name</label>
          <input id="name" autoComplete="name" placeholder="Rani Verma" value={form.name} onChange={update("name")} />
        </div>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" autoComplete="email" placeholder="you@example.com" value={form.email} onChange={update("email")} />
        </div>
        <div className="field">
          <label htmlFor="age">Age (optional)</label>
          <input id="age" type="number" min="10" max="100" placeholder="21" value={form.age} onChange={update("age")} />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete="new-password" placeholder="At least 6 characters" value={form.password} onChange={update("password")} />
        </div>
        <div className="field">
          <label htmlFor="confirm">Confirm password</label>
          <input id="confirm" type="password" autoComplete="new-password" placeholder="Type it again" value={form.confirm} onChange={update("confirm")} />
        </div>
        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p className="auth-switch">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
