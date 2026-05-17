import { useEffect, useState } from "react";
import api from "../api/client.js";


export default function UpitnikAdmin() {
  const [upitnici, setUpitnici] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [pitanjaLookup, setPitanjaLookup] = useState([]);
  const [korisniciLookup, setKorisniciLookup] = useState([]);
  const [kompletnost, setKompletnost] = useState(null);
  const [msg, setMsg] = useState({ type: "", text: "" });


  useEffect(() => {
    Promise.all([
      api.get("/pitanja-admin?only_active=false").then((r) => setPitanjaLookup(r.data)),
      api.get("/upitnici-admin/korisnici").then((r) => setKorisniciLookup(r.data)),
    ]).catch((err) => setErr(err));
    dohvatiListu();
  }, []);

  useEffect(() => {
    if (selectedId) {
      dohvatiDetalje(selectedId);
      dohvatiKompletnost(selectedId);
    } else {
      setDetail(null);
      setKompletnost(null);
    }
  }, [selectedId]);


  const setErr = (err) => setMsg({ type: "error", text: err.response?.data?.error || "Greška." });
  const setOk = (text) => setMsg({ type: "success", text });

  const dohvatiListu = async () => {
    try {
      const { data } = await api.get("/upitnici-admin", {
        params: { search: search || undefined },
      });
      setUpitnici(data);
    } catch (err) { setErr(err); }
  };

  const dohvatiDetalje = async (id) => {
    try {
      const { data } = await api.get(`/upitnici-admin/${id}`);
      setDetail(data);
    } catch (err) { setErr(err); }
  };

  const dohvatiKompletnost = async (id) => {
    try {
      const { data } = await api.get(`/upitnici-admin/${id}/kompletnost`);
      setKompletnost(data);
    } catch (err) { /* nije fatalno */ }
  };

  const noviUpitnik = async () => {
    if (korisniciLookup.length === 0) {
      setErr({ response: { data: { error: "Nema dostupnih korisnika za FK." } } });
      return;
    }
    const kid = prompt(
      "Unesi korisnik_id za novi upitnik (vidi listu desno).\n" +
      "Primjer: " + korisniciLookup.slice(0, 3).map((k) =>
        `${k.korisnik_id}=${k.prezime}`).join(", ")
    );
    if (!kid) return;
    try {
      const { data } = await api.post("/upitnici-admin", {
        korisnik_id: Number(kid),
      });
      setOk("Upitnik kreiran.");
      await dohvatiListu();
      setSelectedId(data.upitnik_id);
    } catch (err) { setErr(err); }
  };

  const obrisiUpitnik = async () => {
    if (!selectedId) return;
    if (!confirm("Obrisati ovaj upitnik i sve odgovore?")) return;
    try {
      await api.delete(`/upitnici-admin/${selectedId}`);
      setOk("Upitnik obrisan.");
      setSelectedId(null);
      dohvatiListu();
    } catch (err) { setErr(err); }
  };

  const promijeniKorisnika = async (novi_kid) => {
    if (!selectedId || !novi_kid) return;
    try {
      await api.put(`/upitnici-admin/${selectedId}`, { korisnik_id: Number(novi_kid) });
      setOk("Vlasnik upitnika promijenjen.");
      dohvatiDetalje(selectedId);
      dohvatiListu();
    } catch (err) { setErr(err); }
  };

  const dodajOdgovor = async () => {
    if (pitanjaLookup.length === 0) return;
    const koristena = new Set((detail?.odgovori || []).map((o) => o.pitanje_id));
    const slobodno = pitanjaLookup.find((p) => !koristena.has(p.pitanje_id));
    if (!slobodno) {
      setErr({ response: { data: { error: "Nema više pitanja za dodavanje." } } });
      return;
    }
    try {
      await api.post(`/upitnici-admin/${selectedId}/odgovori`, {
        pitanje_id: slobodno.pitanje_id,
        vrijednost: slobodno.tip_odgovora === "skala_1_5" ? "3"
                    : slobodno.tip_odgovora === "da_ne" ? "ne"
                    : "—",
      });
      dohvatiDetalje(selectedId);
      dohvatiKompletnost(selectedId);
    } catch (err) { setErr(err); }
  };

  const izmijeniOdgovor = async (odgovor_id, polje, vrijednost) => {
    try {
      const payload = { [polje]: polje === "pitanje_id" ? Number(vrijednost) : vrijednost };
      await api.put(`/upitnici-admin/odgovori/${odgovor_id}`, payload);
      dohvatiDetalje(selectedId);
      dohvatiKompletnost(selectedId);
    } catch (err) { setErr(err); }
  };

  const obrisiOdgovor = async (odgovor_id) => {
    if (!confirm("Obrisati odgovor?")) return;
    try {
      await api.delete(`/upitnici-admin/odgovori/${odgovor_id}`);
      dohvatiDetalje(selectedId);
      dohvatiKompletnost(selectedId);
    } catch (err) { setErr(err); }
  };

  return (
    <>
      <h2>Master-Detail: Upitnici</h2>

      {msg.text && <p className={msg.type}>{msg.text}</p>}

      <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: "1rem" }}>
        {/* Lijevo: lista master entiteta + pretraga */}
        <aside>
          <div className="card">
            <h3>Lista upitnika</h3>
            <input value={search} onChange={(e) => setSearch(e.target.value)}
                   placeholder="Pretraži po imenu/emailu"
                   onKeyDown={(e) => e.key === "Enter" && dohvatiListu()} />
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
              <button onClick={dohvatiListu} style={{ flex: 1 }}>Pretraži</button>
              <button onClick={noviUpitnik} style={{ flex: 1 }}>Novi</button>
            </div>

            <div style={{ marginTop: "1rem", maxHeight: "60vh", overflowY: "auto" }}>
              {upitnici.length === 0 && <p className="muted">Nema upitnika.</p>}
              {upitnici.map((u) => (
                <div
                  key={u.upitnik_id}
                  onClick={() => setSelectedId(u.upitnik_id)}
                  style={{
                    padding: "0.5rem",
                    cursor: "pointer",
                    borderLeft: u.upitnik_id === selectedId
                      ? "4px solid #2563eb" : "4px solid transparent",
                    background: u.upitnik_id === selectedId ? "#eff6ff" : "transparent",
                    borderRadius: "4px",
                    marginBottom: "0.25rem",
                  }}>
                  <div style={{ fontWeight: 500 }}>#{u.upitnik_id} v{u.verzija}</div>
                  <div className="muted" style={{ fontSize: "0.85rem" }}>
                    {u.korisnik?.ime} {u.korisnik?.prezime}
                  </div>
                  <div className="muted" style={{ fontSize: "0.8rem" }}>
                    {u.broj_odgovora} odgovor(a)
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Desno: master forma + detail tablica */}
        <main>
          {!detail ? (
            <p className="muted">Odaberi upitnik s liste ili kreiraj novi.</p>
          ) : (
            <>
              {/* MASTER (zaglavlje) */}
              <div className="card">
                <h3>Zaglavlje — Upitnik #{detail.upitnik_id}</h3>

                <div className="row">
                  <div style={{ flex: 2 }}>
                    <label>Korisnik (FK)</label>
                    <select
                      value={detail.korisnik_id}
                      onChange={(e) => promijeniKorisnika(e.target.value)}>
                      {korisniciLookup.map((k) => (
                        <option key={k.korisnik_id} value={k.korisnik_id}>
                          {k.ime} {k.prezime} ({k.email})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label>Verzija</label>
                    <input value={detail.verzija} disabled />
                  </div>
                  <div>
                    <label>Datum</label>
                    <input value={(detail.datum_ispunjavanja || "").substring(0, 10)} disabled />
                  </div>
                </div>

                {kompletnost && (
                  <p className="muted" style={{ marginTop: "0.5rem" }}>
                    Obavezna pitanja: <strong>{kompletnost.broj_odgovorenih_obaveznih}/{kompletnost.broj_obaveznih}</strong>
                    {kompletnost.kompletan
                      ? <span style={{ color: "#059669", marginLeft: "0.5rem" }}> ✓ kompletan</span>
                      : kompletnost.broj_obaveznih > 0 && (
                        <span style={{ color: "#dc2626", marginLeft: "0.5rem" }}>
                          ✗ nedostaju odgovori
                        </span>
                      )}
                  </p>
                )}

                <button className="danger" onClick={obrisiUpitnik}
                        style={{ marginTop: "0.5rem" }}>
                  Obriši cijeli upitnik
                </button>
              </div>

              {/* DETAIL (odgovori) */}
              <div className="card">
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <h3>Detalji — Odgovori</h3>
                  <button onClick={dodajOdgovor}>+ Dodaj odgovor</button>
                </div>

                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #d1d5db", textAlign: "left" }}>
                      <th style={{ padding: "0.5rem", width: "50%" }}>Pitanje (FK)</th>
                      <th style={{ padding: "0.5rem" }}>Vrijednost</th>
                      <th style={{ padding: "0.5rem" }}>Tip</th>
                      <th style={{ padding: "0.5rem" }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {detail.odgovori.length === 0 && (
                      <tr><td colSpan="4" className="muted"
                            style={{ padding: "1rem", textAlign: "center" }}>
                        Nema odgovora. Kliknite + da dodate.
                      </td></tr>
                    )}
                    {detail.odgovori.map((o) => {
                      const p = pitanjaLookup.find((p) => p.pitanje_id === o.pitanje_id);
                      return (
                        <tr key={o.odgovor_id} style={{ borderBottom: "1px solid #e5e7eb" }}>
                          <td style={{ padding: "0.5rem" }}>
                            <select value={o.pitanje_id}
                                    onChange={(e) => izmijeniOdgovor(o.odgovor_id, "pitanje_id", e.target.value)}>
                              {pitanjaLookup.map((pp) => (
                                <option key={pp.pitanje_id} value={pp.pitanje_id}>
                                  {pp.tekst_pitanja.length > 60
                                    ? pp.tekst_pitanja.slice(0, 60) + "…"
                                    : pp.tekst_pitanja}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td style={{ padding: "0.5rem" }}>
                            {p?.tip_odgovora === "skala_1_5" ? (
                              <select value={o.vrijednost}
                                      onChange={(e) => izmijeniOdgovor(o.odgovor_id, "vrijednost", e.target.value)}>
                                {[1, 2, 3, 4, 5].map((n) =>
                                  <option key={n} value={n}>{n}</option>)}
                              </select>
                            ) : p?.tip_odgovora === "da_ne" ? (
                              <select value={o.vrijednost.toLowerCase()}
                                      onChange={(e) => izmijeniOdgovor(o.odgovor_id, "vrijednost", e.target.value)}>
                                <option value="da">da</option>
                                <option value="ne">ne</option>
                              </select>
                            ) : (
                              <input value={o.vrijednost}
                                     onBlur={(e) => izmijeniOdgovor(o.odgovor_id, "vrijednost", e.target.value)}
                                     defaultValue={o.vrijednost} />
                            )}
                          </td>
                          <td style={{ padding: "0.5rem" }} className="muted">
                            {p?.tip_odgovora || "—"}
                          </td>
                          <td style={{ padding: "0.5rem" }}>
                            <button className="danger" onClick={() => obrisiOdgovor(o.odgovor_id)}
                                    style={{ padding: "0.25rem 0.5rem", fontSize: "0.85rem" }}>
                              ✕
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </main>
      </div>
    </>
  );
}
