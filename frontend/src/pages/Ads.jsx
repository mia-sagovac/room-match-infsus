import { useEffect, useState } from "react";
import api from "../api/client.js";

const PRAZAN_OGLAS = {
  naslov: "", opis: "", cijena: "",
  adresa: "", grad: "", kvart: "",
  broj_soba: "", dostupno_od: "",
};

// trenutnog korisnikovog ID-a iz localstoragea, null ako nije parsirano ili nema korisnika
function trenutniId() {
  try {
    return JSON.parse(localStorage.getItem("korisnik") || "{}").korisnik_id;
  } catch {
    return null;
  }
}

export default function Ads() {
  const [oglasi, setOglasi] = useState([]);
  const [filteri, setFilteri] = useState({ grad: "", max_cijena: "", min_soba: "" });
  const [novi, setNovi] = useState(PRAZAN_OGLAS);
  const [showForm, setShowForm] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });
  const jaId = trenutniId();

  // dohvat oglasa s backend API-jem, filteri kao query parametri
  const dohvati = async () => {
    try {
      const params = {};
      for (const [k, v] of Object.entries(filteri)) {
        if (v !== "") params[k] = v;
      }
      const { data } = await api.get("/oglasi", { params });
      setOglasi(data);
    } catch (err) {
      setMsg({ type: "error", text: err.response?.data?.error || "Greška." });
    }
  };

  useEffect(() => { dohvati(); }, []);  // dohvati oglase na mountu

  const setF = (k) => (e) => setFilteri({ ...filteri, [k]: e.target.value });
  const setO = (k) => (e) => setNovi({ ...novi, [k]: e.target.value });

  const kreiraj = async (e) => {
    e.preventDefault();
    setMsg({ type: "", text: "" });

    const payload = { ...novi };
    payload.cijena = Number(payload.cijena);
    payload.broj_soba = payload.broj_soba ? Number(payload.broj_soba) : null;
    if (!payload.opis) 
      delete payload.opis;
    if (!payload.adresa) 
      delete payload.adresa;
    if (!payload.kvart) 
      delete payload.kvart;
    if (!payload.dostupno_od) 
      delete payload.dostupno_od;

    // validacija na klijentu
    if (payload.naslov.trim() === "") {
      setMsg({ type: "error", text: "Naslov je obavezan." });
      return;
    }
    if (isNaN(payload.cijena) || payload.cijena <= 0) {
      setMsg({ type: "error", text: "Cijena mora biti pozitivan broj." });
      return;
    }
    if (payload.broj_soba !== null && (isNaN(payload.broj_soba) || payload.broj_soba < 1 || payload.broj_soba > 10)) {
      setMsg({ type: "error", text: "Broj soba mora biti između 1 i 10." });
      return;
    }
    if (payload.dostupno_od && isNaN(Date.parse(payload.dostupno_od))) {
      setMsg({ type: "error", text: "Neispravan datum za 'Dostupno od'." });
      return;
    }
    if (payload.grad.trim() === "") {
      setMsg({ type: "error", text: "Grad je obavezan." });
      return;
    }
    try {
      await api.post("/oglasi", payload);
      setNovi(PRAZAN_OGLAS);
      setShowForm(false);
      setMsg({ type: "success", text: "Oglas kreiran." });
      dohvati();
    } catch (err) {
      setMsg({ type: "error", text: err.response?.data?.error || "Greška." });
    }
  };

  // brisanje oglasa
  const obrisi = async (oglas_id) => {
    if (!confirm("Obrisati oglas?")) return;
    try {
      await api.delete(`/oglasi/${oglas_id}`);
      dohvati();
    } catch (err) {
      setMsg({ type: "error", text: err.response?.data?.error || "Greška." });
    }
  };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>Oglasi za stanove</h2>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Odustani" : "Novi oglas"}
        </button>
      </div>

      {msg.text && <p className={msg.type}>{msg.text}</p>}

      {showForm && (
        <form onSubmit={kreiraj} className="card">
          <h3>Novi oglas</h3>
          <label>Naslov *</label>
          <input value={novi.naslov} onChange={setO("naslov")} required maxLength="300" />

          <label>Opis</label>
          <textarea rows="3" value={novi.opis} onChange={setO("opis")} />

          <div className="row">
            <div>
              <label>Cijena (€) *</label>
              <input type="number" min="0.01" step="0.01" value={novi.cijena} onChange={setO("cijena")} required />
            </div>
            <div>
              <label>Broj soba (1-10)</label>
              <input type="number" min="1" max="10" value={novi.broj_soba} onChange={setO("broj_soba")} />
            </div>
            <div>
              <label>Dostupno od</label>
              <input type="date" value={novi.dostupno_od} onChange={setO("dostupno_od")} />
            </div>
          </div>

          <div className="row">
            <div>
              <label>Grad *</label>
              <input value={novi.grad} onChange={setO("grad")} required maxLength="100" />
            </div>
            <div>
              <label>Kvart</label>
              <input value={novi.kvart} onChange={setO("kvart")} maxLength="100" />
            </div>
          </div>

          <label>Adresa</label>
          <input value={novi.adresa} onChange={setO("adresa")} maxLength="300" />

          <button type="submit" style={{ marginTop: "1rem" }}>Objavi oglas</button>
        </form>
      )}

      <form onSubmit={(e) => { e.preventDefault(); dohvati(); }} className="card">
        <h3>Filteri</h3>
        <div className="row">
          <div>
            <label>Grad</label>
            <input value={filteri.grad} onChange={setF("grad")} />
          </div>
          <div>
            <label>Max. cijena (€)</label>
            <input type="number" min="0" value={filteri.max_cijena} onChange={setF("max_cijena")} />
          </div>
          <div>
            <label>Min. soba</label>
            <input type="number" min="1" value={filteri.min_soba} onChange={setF("min_soba")} />
          </div>
        </div>
        <button type="submit" style={{ marginTop: "1rem" }}>Primijeni</button>
      </form>

      {oglasi.length === 0 && <p className="muted">Nema oglasa za prikaz.</p>}

      {oglasi.map((o) => (
        <div key={o.oglas_id} className="card">
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div>
              <h3 style={{ margin: 0 }}>{o.naslov}</h3>
              <p className="muted" style={{ margin: "0.25rem 0" }}>
                {o.grad}{o.kvart ? `, ${o.kvart}` : ""}
                {o.adresa ? `, ${o.adresa}` : ""}
                {o.broj_soba ? `, ${o.broj_soba} sobe` : ""}
                {o.dostupno_od ? `, od ${o.dostupno_od}` : ""}
              </p>
              {o.opis && <p style={{ margin: "0.5rem 0" }}>{o.opis}</p>}
              <strong>{o.cijena.toFixed(2)} €</strong>
            </div>
            {o.korisnik_id === jaId && (
              <button className="danger" onClick={() => obrisi(o.oglas_id)}>Obriši</button>
            )}
          </div>
        </div>
      ))}
    </>
  );
}
