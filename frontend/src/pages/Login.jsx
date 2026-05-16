import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/client.js";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [lozinka, setLozinka] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // submit login forme
  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", { email, lozinka });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("korisnik", JSON.stringify(data.korisnik));
      navigate("/matches");
    } catch (err) {
      setError(err.response?.data?.error || "Greška pri prijavi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 400, margin: "3rem auto" }}>
      <h2>Prijava</h2>
      <form onSubmit={submit}>
        <label>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label>Lozinka</label>
        <input type="password" value={lozinka} onChange={(e) => setLozinka(e.target.value)} required />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading} style={{ marginTop: "1rem", width: "100%" }}>
          {loading ? "..." : "Prijavi se"}
        </button>
      </form>
      <p className="muted" style={{ marginTop: "1rem" }}>
        Nemaš račun? <Link to="/register">Registriraj se</Link>
      </p>
    </div>
  );
}
