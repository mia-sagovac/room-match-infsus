import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client.js";

const PRAZNI_FILTERI = {
  grad: "", kvart: "", ritam: "", min_urednost: "",
  min_cijena: "", max_cijena: "", max_pusac: "", min_postotak: "",
};

// badge klase za kompatibilnost
function badgeKlasa(p) {
  if (p >= 75) return "badge high";
  if (p >= 50) return "badge med";
  return "badge low";
}

export default function Matches() {
  const navigate = useNavigate();
  const [filteri, setFilteri] = useState(PRAZNI_FILTERI);
  const [rezultati, setRezultati] = useState([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const dohvati = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setMsg({ type: "", text: "" });
    try {
      const params = {};
      for (const [k, v] of Object.entries(filteri)) {
        if (v !== "" && v !== null) params[k] = v;
      }
      const { data } = await api.get("/match/preporuke", { params });
      setRezultati(data);
      if (data.length === 0) {
        setMsg({ type: "muted", text: "Nema rezultata za zadane filtere." });
      }
    } catch (err) {
      setMsg({ type: "error", text: err.response?.data?.error || "Greška." });
    } finally {
      setLoading(false);
    }
  };

  // citanje pri prvom prikazu
  useEffect(() => { dohvati(); }, []);  // dohvacanje preporuka na mountu

  const set = (k) => (e) => setFilteri({ ...filteri, [k]: e.target.value });

  const matchSe = async (korisnik_id) => {
    try {
      const { data } = await api.post("/match", { korisnik_id });
      // if već prihvacen, postoji razgovor — odi u chat. Inače poruka.
      if (data.razgovor_id) {
        navigate(`/chat/${data.razgovor_id}`);
      } else {
        setMsg({
          type: "success",
          text: `Match predložen (${data.postotak_kompatibilnosti}%). Pričekaj odgovor druge strane.`,
        });
      }
    } catch (err) {
      setMsg({ type: "error", text: err.response?.data?.error || "Greška." });
    }
  };

  return (
    <>
      <h2>Pregled cimera</h2>

      <form onSubmit={dohvati} className="card">
        <h3>Filteri</h3>
        <div className="row">
          <div>
            <label>Grad</label>
            <input value={filteri.grad} onChange={set("grad")} />
          </div>
          <div>
            <label>Kvart</label>
            <input value={filteri.kvart} onChange={set("kvart")} />
          </div>
          <div>
            <label>Ritam</label>
            <select value={filteri.ritam} onChange={set("ritam")}>
              <option value="">—</option>
              <option value="rana_ptica">Rana ptica</option>
              <option value="nocna_sova">Noćna sova</option>
              <option value="fleksibilno">Fleksibilno</option>
            </select>
          </div>
        </div>

        <div className="row">
          <div>
            <label>Min. cijena (€)</label>
            <input type="number" min="0" value={filteri.min_cijena} onChange={set("min_cijena")} />
          </div>
          <div>
            <label>Max. cijena (€)</label>
            <input type="number" min="0" value={filteri.max_cijena} onChange={set("max_cijena")} />
          </div>
          <div>
            <label>Min. urednost</label>
            <input type="number" min="1" max="5" value={filteri.min_urednost} onChange={set("min_urednost")} />
          </div>
        </div>

        <div className="row">
          <div>
            <label>Pušač?</label>
            <select value={filteri.max_pusac} onChange={set("max_pusac")}>
              <option value="">Svejedno</option>
              <option value="false">Ne</option>
              <option value="true">Da</option>
            </select>
          </div>
          <div>
            <label>Min. kompatibilnost (%)</label>
            <input type="number" min="0" max="100" value={filteri.min_postotak} onChange={set("min_postotak")} />
          </div>
        </div>

        <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
          <button type="submit" disabled={loading}>{loading ? "..." : "Primijeni filtere"}</button>
          <button type="button" className="secondary" onClick={() => { setFilteri(PRAZNI_FILTERI); }}>
            Resetiraj
          </button>
        </div>
      </form>

      {msg.text && <p className={msg.type}>{msg.text}</p>}

      {rezultati.map((r) => (
        <div key={r.korisnik.korisnik_id} className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h3 style={{ margin: 0 }}>
                {r.korisnik.ime} {r.korisnik.prezime}{" "}
                <span className={badgeKlasa(r.postotak_kompatibilnosti)}>
                  {r.postotak_kompatibilnosti}%
                </span>
              </h3>
              <p className="muted" style={{ margin: "0.25rem 0" }}>
                {r.profil?.grad}{r.profil?.kvart ? `, ${r.profil.kvart}` : ""}
                {r.profil?.dob ? `, ${r.profil.dob} god.` : ""}
                {r.profil?.ritam ? `, ${r.profil.ritam.replace("_", " ")}` : ""}
                {r.profil?.urednost ? `, urednost ${r.profil.urednost}/5` : ""}
                {r.profil?.pusac === true ? ", pušač" : ""}
                {r.profil?.kucni_ljubimci === true ? ", ljubimci" : ""}
              </p>
              {r.profil?.bio && <p style={{ margin: "0.5rem 0" }}>{r.profil.bio}</p>}
            </div>
            <button onClick={() => matchSe(r.korisnik.korisnik_id)}>Predloži match</button>
          </div>
        </div>
      ))}
    </>
  );
}
