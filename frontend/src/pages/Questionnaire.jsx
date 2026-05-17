import { useEffect, useState } from "react";
import api from "../api/client.js";
import Modal from "./components/Modal.jsx";

export default function Questionnaire() {
  const [pitanja, setPitanja] = useState([]);
  const [odgovori, setOdgovori] = useState({});
  const [msg, setMsg] = useState({ type: "", text: "" });
  const [modal, setModal] = useState({ isOpen: false, type: "", title: "", message: "" });
  const [loading, setLoading] = useState(true);

  // učitaj pitanja i odgovore pri mountu
  useEffect(() => {
    Promise.all([api.get("/pitanja"), api.get("/upitnik")])
      .then(([p, u]) => {
        setPitanja(p.data);
        if (u.data?.odgovori) {
          const map = {};
          for (const o of u.data.odgovori) map[o.pitanje_id] = o.vrijednost;
          setOdgovori(map);
        }
      })
      .catch((err) => setMsg({ type: "error", text: err.response?.data?.error || "Greška." }))
      .finally(() => setLoading(false));
  }, []);

  // funkcija za update odgovora na input promjene
  const set = (pid, v) => setOdgovori({ ...odgovori, [pid]: v });

  // submit upitnika
  const submit = async (e) => {
    e.preventDefault();
    setMsg({ type: "", text: "" });

    const lista = pitanja
      .filter((p) => odgovori[p.pitanje_id] !== undefined && odgovori[p.pitanje_id] !== "")
      .map((p) => ({ pitanje_id: p.pitanje_id, vrijednost: String(odgovori[p.pitanje_id]) }));

    if (lista.length === 0) {
      setModal({
        isOpen: true,
        type: "error",
        title: "Nisu svi odgovori",
        message: "Odgovori barem na jedno pitanje.",
      });
      return;
    }

    try {
      await api.post("/upitnik", { odgovori: lista });
      setModal({
        isOpen: true,
        type: "success",
        title: "Upitnik spreman",
        message: "Upitnik je spreman! Kompatibilnost je preračunata.",
      });
    } catch (err) {
      setModal({
        isOpen: true,
        type: "error",
        title: "Greška",
        message: err.response?.data?.error || "Greška.",
      });
    }
  };

  // prikaz ucitavanja i poruka o nedostatku pitanja
  if (loading) return <p>Učitavanje...</p>;
  if (pitanja.length === 0) return <p className="muted">Trenutno nema aktivnih pitanja.</p>;

  return (
    <>
      <h2>Upitnik kompatibilnosti</h2>
      <p className="muted">
        Odgovori se koriste za izračun kompatibilnosti s drugim korisnicima. Možeš ih
        u bilo kojem trenutku ažurirati, sustav sprema novu verziju upitnika.
      </p>

      {msg.text && <p className={msg.type}>{msg.text}</p>}

      <form onSubmit={submit}>
        {pitanja.map((p) => (
          <div key={p.pitanje_id} className="card">
            <strong>{p.tekst_pitanja}</strong>
            <p className="muted" style={{ margin: "0.25rem 0 0.75rem" }}>
              Kategorija: {p.kategorija}, Težina: {p.tezina}/5
            </p>

            {p.tip_odgovora === "skala_1_5" && (
              <select value={odgovori[p.pitanje_id] ?? ""} onChange={(e) => set(p.pitanje_id, e.target.value)}>
                <option value="">-</option>
                {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            )}

            {p.tip_odgovora === "da_ne" && (
              <select value={odgovori[p.pitanje_id] ?? ""} onChange={(e) => set(p.pitanje_id, e.target.value)}>
                <option value="">-</option>
                <option value="da">Da</option>
                <option value="ne">Ne</option>
              </select>
            )}

            {(p.tip_odgovora === "tekst" || p.tip_odgovora === "visestruki_izbor") && (
              <input
                value={odgovori[p.pitanje_id] ?? ""}
                onChange={(e) => set(p.pitanje_id, e.target.value)}
                maxLength="500"
              />
            )}
          </div>
        ))}

        <button type="submit">Spremi odgovore</button>
      </form>

      <Modal
        isOpen={modal.isOpen}
        type={modal.type}
        title={modal.title}
        message={modal.message}
        onClose={() => setModal({ ...modal, isOpen: false })}
      />
    </>
  );
}
