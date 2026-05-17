import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/client.js";

// trenutnog korisnikovog ID-a iz localstoragea, null ako nije parsirano ili nema korisnika
function trenutniId() {
  try {
    return JSON.parse(localStorage.getItem("korisnik") || "{}").korisnik_id;
  } catch {
    return null;
  }
}

export default function Chat() {
  const { razgovorId } = useParams();
  const navigate = useNavigate();
  const [razgovori, setRazgovori] = useState([]);
  const [matchevi, setMatchevi] = useState([]);  // za prihvaćanje predloženih
  const [poruke, setPoruke] = useState([]);
  const [novaPoruka, setNovaPoruka] = useState("");
  const [error, setError] = useState("");
  const krajChata = useRef(null);
  const jaId = trenutniId();

  // citaj razgovore + matcheve
  const ucitajListe = () => {
    Promise.all([api.get("/razgovori"), api.get("/match")])
      .then(([r, m]) => {
        setRazgovori(r.data);
        setMatchevi(m.data);
      })
      .catch((err) => setError(err.response?.data?.error || "Greška."));
  };
  useEffect(() => { ucitajListe(); }, []);

  // citaj poruke odabranog razgovora + auto-poll svakih 5s
  useEffect(() => {
    if (!razgovorId) {
      setPoruke([]);
      return;
    }
    const fetchMsgs = () => {
      api.get(`/razgovori/${razgovorId}/poruke`)
        .then((res) => setPoruke(res.data))
        .catch((err) => setError(err.response?.data?.error || "Greška."));
    };
    fetchMsgs();
    const id = setInterval(fetchMsgs, 5000);
    return () => clearInterval(id);
  }, [razgovorId]);

  // auto-scroll dolje - ipak ne treba
  /*
  useEffect(() => {
    krajChata.current?.scrollIntoView({ behavior: "smooth" });
  }, [poruke]);*/

  const posalji = async (e) => {
    e.preventDefault();
    if (!novaPoruka.trim()) return;
    try {
      const { data } = await api.post(`/razgovori/${razgovorId}/poruke`, { sadrzaj: novaPoruka });
      setPoruke([...poruke, data]);
      setNovaPoruka("");
    } catch (err) {
      setError(err.response?.data?.error || "Greška pri slanjem.");
    }
  };

  const imeSugovornika = (razgovor) => {
    const match = matchevi.find((m) => String(m.razgovor_id) === String(razgovor.razgovor_id));
    if (match?.drugi_korisnik) {
      return `${match.drugi_korisnik.ime} ${match.drugi_korisnik.prezime}`;
    }
    return `Razgovor #${razgovor.razgovor_id}`;
  };

  // odgovri na match (pass/fail)
  const odgovoriNaMatch = async (match_id, status) => {
    try {
      const { data } = await api.patch(`/match/${match_id}`, { status });
      ucitajListe();
      if (status === "prihvacen" && data.razgovor_id) {
        navigate(`/chat/${data.razgovor_id}`);
      }
    } catch (err) {
      setError(err.response?.data?.error || "Greška.");
    }
  };

  // razdvoji predlozene matcheve gdje sam ja primatelj
  const predlozeniMeni = matchevi.filter(
    (m) => m.status === "predlozen" && m.korisnik2_id === jaId
  );

  return (
    <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: "1rem", minHeight: "70vh" }}>
      <aside>
        <h3>Razgovori</h3>
        {razgovori.length === 0 && <p className="muted">Još nemaš razgovora.</p>}
        {razgovori.map((r) => (
          <div
            key={r.razgovor_id}
            className="card"
            style={{
              cursor: "pointer",
              padding: "0.75rem",
              borderLeft: String(r.razgovor_id) === razgovorId ? "4px solid #2563eb" : "4px solid transparent",
            }}
            onClick={() => navigate(`/chat/${r.razgovor_id}`)}
          >
            <strong>{imeSugovornika(r)}</strong>
            <div className="muted" style={{ fontSize: "0.85rem" }}>
              Kompatibilnost: {r.postotak_kompatibilnosti}%
            </div>
            {r.zadnja_poruka && (
              <div className="muted" style={{ fontSize: "0.85rem", marginTop: "0.25rem" }}>
                {r.zadnja_poruka.sadrzaj.slice(0, 40)}
                {r.zadnja_poruka.sadrzaj.length > 40 ? "…" : ""}
              </div>
            )}
          </div>
        ))}

        {predlozeniMeni.length > 0 && (
          <>
            <h3 style={{ marginTop: "1.5rem" }}>Predloženi matchevi</h3>
            {predlozeniMeni.map((m) => (
              <div key={m.match_id} className="card" style={{ padding: "0.75rem" }}>
                <strong>
                  {m.drugi_korisnik?.ime} {m.drugi_korisnik?.prezime}
                </strong>
                <div className="muted" style={{ fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                  Kompatibilnost: {m.postotak_kompatibilnosti}%
                </div>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button onClick={() => odgovoriNaMatch(m.match_id, "prihvacen")}>Prihvati</button>
                  <button className="secondary" onClick={() => odgovoriNaMatch(m.match_id, "odbijen")}>
                    Odbij
                  </button>
                </div>
              </div>
            ))}
          </>
        )}
      </aside>

      <main>
        {error && <p className="error">{error}</p>}

        {!razgovorId ? (
          <p className="muted">Odaberi razgovor s lijeve strane.</p>
        ) : (
          <div className="card" style={{ display: "flex", flexDirection: "column", height: "70vh" }}>
            <div style={{ flex: 1, overflowY: "auto", padding: "0.5rem" }}>
              {poruke.length === 0 && <p className="muted">Još nema poruka. Pošalji prvu!</p>}
              {poruke.map((p) => {
                const moja = p.posiljalac_id === jaId;
                return (
                  <div key={p.poruka_id}
                       style={{ display: "flex", justifyContent: moja ? "flex-end" : "flex-start", margin: "0.5rem 0" }}>
                    <div style={{
                      background: moja ? "var(--primary-purple)" : "var(--surface-soft)",
                      color: moja ? "white" : "var(--text-dark)",
                      padding: "0.5rem 0.85rem",
                      borderRadius: "12px",
                      maxWidth: "70%",
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                    }}>
                      {p.sadrzaj}
                      <div style={{ fontSize: "0.7rem", opacity: 0.7, marginTop: "0.25rem" }}>
                        {new Date(p.vrijeme_slanja).toLocaleString("hr-HR")}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={krajChata} />
            </div>

            <form onSubmit={posalji} style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
              <input
                value={novaPoruka}
                onChange={(e) => setNovaPoruka(e.target.value)}
                placeholder="Napiši poruku..."
                maxLength="5000"
              />
              <button type="submit" disabled={!novaPoruka.trim()}>Pošalji</button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
