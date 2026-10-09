import { useState, type ChangeEvent, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

const MIN_PASSWORD = 8;

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ firstName: "", lastName: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const update = (field: keyof typeof form) => (e: ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    // Quick checks here for fast feedback; the server re-validates everything.
    if (form.password.length < MIN_PASSWORD) {
      setError(`Password must be at least ${MIN_PASSWORD} characters.`);
      return;
    }
    if (form.password !== form.confirm) {
      setError("Passwords don't match.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await register({
        first_name: form.firstName,
        last_name: form.lastName,
        email: form.email,
        password: form.password,
        confirm_password: form.confirm,
      });
      navigate("/");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth" onSubmit={handleSubmit}>
      <h1>Create account</h1>
      <div className="row">
        <div>
          <label htmlFor="firstName">First name</label>
          <input id="firstName" autoComplete="given-name" required value={form.firstName} onChange={update("firstName")} />
        </div>
        <div>
          <label htmlFor="lastName">Last name</label>
          <input id="lastName" autoComplete="family-name" required value={form.lastName} onChange={update("lastName")} />
        </div>
      </div>
      <label htmlFor="email">Email</label>
      <input id="email" type="email" autoComplete="email" required value={form.email} onChange={update("email")} />
      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        autoComplete="new-password"
        required
        minLength={MIN_PASSWORD}
        value={form.password}
        onChange={update("password")}
      />
      <label htmlFor="confirm">Confirm password</label>
      <input
        id="confirm"
        type="password"
        autoComplete="new-password"
        required
        value={form.confirm}
        onChange={update("confirm")}
      />
      <button className="btn" type="submit" disabled={submitting}>
        {submitting ? "Creating account…" : "Create account"}
      </button>
      {error && <div className="form-msg error">{error}</div>}
      <p className="note">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </form>
  );
}
