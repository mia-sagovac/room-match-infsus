import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/client.js";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    lozinka: "",
    ime: "",
    prezime: "",
    tip: "ostalo",
    fakultet: "",
    smjer: "",
    godina_studija: "",
    tvrtka: "",
    pozicija: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // setaj formu na input promjene
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  // submit forme
  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // salji samo polja relevantna za odabrani tip
    const payload = {
      email: form.email,
      lozinka: form.lozinka,
      ime: form.ime,
      prezime: form.prezime,
      tip: form.tip,
    };
    if (form.tip === "student") {
      payload.fakultet = form.fakultet;
      payload.smjer = form.smjer || null;
      payload.godina_studija = form.godina_studija ? Number(form.godina_studija) : null;
    } else if (form.tip === "zaposleni") {
      payload.tvrtka = form.tvrtka;
      payload.pozicija = form.pozicija || null;
    }

    // pokušaj registracije
    try {
      const { data } = await api.post("/auth/register", payload);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("korisnik", JSON.stringify(data.korisnik));
      navigate("/profile");
    } catch (err) {
      setError(err.response?.data?.error || "Greška pri registraciji.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 500, margin: "2rem auto" }}>
      <h2>Registracija</h2>
      <form onSubmit={submit}>
        <div className="row">
          <div>
            <label>Ime</label>
            <input value={form.ime} onChange={set("ime")} required />
          </div>
          <div>
            <label>Prezime</label>
            <input value={form.prezime} onChange={set("prezime")} required />
          </div>
        </div>

        <label>Email</label>
        <input type="email" value={form.email} onChange={set("email")} required />

        <label>Lozinka (min. 8 znakova, slova + brojevi)</label>
        <input type="password" value={form.lozinka} onChange={set("lozinka")} required />

        <label>Tip korisnika</label>
        <select value={form.tip} onChange={set("tip")}>
          <option value="student">Student</option>
          <option value="zaposleni">Zaposleni</option>
          <option value="ostalo">Ostalo</option>
        </select>

        {form.tip === "student" && (
          <>
            <label>Fakultet</label>
            <input value={form.fakultet} onChange={set("fakultet")} required />
            <div className="row">
              <div>
                <label>Smjer</label>
                <input value={form.smjer} onChange={set("smjer")} />
              </div>
              <div>
                <label>Godina studija (1-7)</label>
                <input type="number" min="1" max="7" value={form.godina_studija}
                       onChange={set("godina_studija")} />
              </div>
            </div>
          </>
        )}

        {form.tip === "zaposleni" && (
          <>
            <label>Tvrtka</label>
            <input value={form.tvrtka} onChange={set("tvrtka")} required />
            <label>Pozicija</label>
            <input value={form.pozicija} onChange={set("pozicija")} />
          </>
        )}

        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading} style={{ marginTop: "1rem", width: "100%" }}>
          {loading ? "..." : "Registriraj se"}
        </button>
      </form>
      <p className="muted" style={{ marginTop: "1rem" }}>
        Već imaš račun? <Link to="/login">Prijavi se</Link>
      </p>
    </div>
  );
}
