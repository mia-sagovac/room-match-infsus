import { useEffect, useState } from "react";
import api from "../api/client.js";

const PRAZNO = {
    tekst_pitanja: "",
    kategorija: "navike",
    tip_odgovora: "skala_1_5",
    tezina: 1,
    aktivno: true,
};

const KATEGORIJE = [
    "navike", "cistoca", "budzet", "drustveni_zivot",
    "osobnost", "zivotni_stil", "ostalo",
];

const TIPOVI_ODGOVORA = ["skala_1_5", "da_ne", "tekst", "visestruki_izbor"];


export default function Pitanja() {
    const [pitanja, setPitanja] = useState([]);
    const [search, setSearch] = useState("");
    const [onlyActive, setOnlyActive] = useState(false);
    const [editing, setEditing] = useState(null);
    const [msg, setMsg] = useState({ type: "", text: "" });
    const [loading, setLoading] = useState(false);

    const dohvati = async () => {
        setLoading(true);
        setMsg({ type: "", text: "" });
        try {
            const { data } = await api.get("/pitanja-admin", {
                params: {
                    search: search || undefined,
                    only_active: onlyActive ? "true" : "false",
                },
            });
            setPitanja(data);
        } catch (err) {
            setMsg({ type: "error", text: err.response?.data?.error || "Greška pri dohvatu." });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { dohvati(); }, []);

    const startNew = () => setEditing({ ...PRAZNO });
    const startEdit = (p) => setEditing({ ...p });
    const cancelEdit = () => setEditing(null);
    const setField = (k) => (e) => {
        const v = e.target.type === "checkbox" ? e.target.checked : e.target.value;
        setEditing({ ...editing, [k]: v });
    };

    const spremi = async (e) => {
        e.preventDefault();
        setMsg({ type: "", text: "" });
        const payload = {
            ...editing,
            tezina: Number(editing.tezina),
        };
        try {
            if (editing.pitanje_id) {
                await api.put(`/pitanja-admin/${editing.pitanje_id}`, payload);
                setMsg({ type: "success", text: "Pitanje ažurirano." });
            } else {
                await api.post("/pitanja-admin", payload);
                setMsg({ type: "success", text: "Pitanje kreirano." });
            }
            setEditing(null);
            dohvati();
        } catch (err) {
            setMsg({ type: "error", text: err.response?.data?.error || "Greška pri spremanju." });
        }
    };

    const obrisi = async (pid) => {
        if (!confirm("Obrisati ovo pitanje?")) return;
        setMsg({ type: "", text: "" });
        try {
            await api.delete(`/pitanja-admin/${pid}`);
            setMsg({ type: "success", text: "Pitanje obrisano." });
            dohvati();
        } catch (err) {
            setMsg({ type: "error", text: err.response?.data?.error || "Greška pri brisanju." });
        }
    };

    return (
        <>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h2>Šifrarnik</h2>
                <button onClick={startNew} disabled={editing !== null}>Novo pitanje</button>
            </div>

            {msg.text && <p className={msg.type}>{msg.text}</p>}

            {editing !== null && (
                <form onSubmit={spremi} className="card">
                    <h3>{editing.pitanje_id ? `Uredi pitanje #${editing.pitanje_id}` : "Novo pitanje"}</h3>

                    <label>Tekst pitanja *</label>
                    <input value={editing.tekst_pitanja} onChange={setField("tekst_pitanja")} required
                           maxLength="1000" placeholder="npr. Voliš li tišinu navečer?" />

                    <div className="row">
                        <div>
                            <label>Kategorija *</label>
                            <select value={editing.kategorija} onChange={setField("kategorija")}>
                                {KATEGORIJE.map((k) => <option key={k} value={k}>{k}</option>)}
                            </select>
                        </div>
                        <div>
                            <label>Tip odgovora *</label>
                            <select value={editing.tip_odgovora} onChange={setField("tip_odgovora")}>
                                {TIPOVI_ODGOVORA.map((t) => <option key={t} value={t}>{t}</option>)}
                            </select>
                        </div>
                        <div>
                            <label>Težina (1–5) *</label>
                            <input type="number" min="1" max="5" value={editing.tezina} onChange={setField("tezina")} required />
                        </div>
                    </div>

                    <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <input type="checkbox" style={{ width: "auto" }}
                               checked={!!editing.aktivno} onChange={setField("aktivno")} />
                        Aktivno (uključeno u upitnike)
                    </label>

                    <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
                        <button type="submit">{editing.pitanje_id ? "Spremi izmjene" : "Kreiraj"}</button>
                        <button type="button" className="secondary" onClick={cancelEdit}>Odustani</button>
                    </div>
                </form>
            )}

            <form onSubmit={(e) => { e.preventDefault(); dohvati(); }} className="card">
                <div className="row">
                    <div style={{ flex: 2 }}>
                        <label>Pretraga teksta</label>
                        <input value={search} onChange={(e) => setSearch(e.target.value)}
                               placeholder="npr. tišinu" />
                    </div>
                    <div>
                        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "1.5rem" }}>
                            <input type="checkbox" style={{ width: "auto" }}
                                   checked={onlyActive} onChange={(e) => setOnlyActive(e.target.checked)} />
                            Samo aktivna
                        </label>
                    </div>
                    <div>
                        <label>&nbsp;</label>
                        <button type="submit" disabled={loading}>
                            {loading ? "..." : "Pretraži"}
                        </button>
                    </div>
                </div>
            </form>

            <div className="card">
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                    <tr style={{ borderBottom: "2px solid #d1d5db", textAlign: "left" }}>
                        <th style={{ padding: "0.5rem" }}>ID</th>
                        <th style={{ padding: "0.5rem" }}>Tekst</th>
                        <th style={{ padding: "0.5rem" }}>Kategorija</th>
                        <th style={{ padding: "0.5rem" }}>Tip</th>
                        <th style={{ padding: "0.5rem", textAlign: "center" }}>Težina</th>
                        <th style={{ padding: "0.5rem", textAlign: "center" }}>Aktivno</th>
                        <th style={{ padding: "0.5rem" }}></th>
                    </tr>
                    </thead>
                    <tbody>
                    {pitanja.length === 0 && (
                        <tr><td colSpan="7" className="muted" style={{ padding: "1rem", textAlign: "center" }}>
                            Nema pitanja za prikaz.
                        </td></tr>
                    )}
                    {pitanja.map((p) => (
                        <tr key={p.pitanje_id} style={{ borderBottom: "1px solid #e5e7eb" }}>
                            <td style={{ padding: "0.5rem" }}>{p.pitanje_id}</td>
                            <td style={{ padding: "0.5rem" }}>{p.tekst_pitanja}</td>
                            <td style={{ padding: "0.5rem" }}><span className="badge">{p.kategorija}</span></td>
                            <td style={{ padding: "0.5rem" }} className="muted">{p.tip_odgovora}</td>
                            <td style={{ padding: "0.5rem", textAlign: "center" }}>{p.tezina}/5</td>
                            <td style={{ padding: "0.5rem", textAlign: "center" }}>
                                {p.aktivno ? "✓" : "—"}
                            </td>
                            <td style={{ padding: "0.5rem", display: "flex", gap: "0.25rem" }}>
                                <button className="secondary" onClick={() => startEdit(p)}
                                        style={{ padding: "0.25rem 0.5rem", fontSize: "0.85rem" }}>
                                    Uredi
                                </button>
                                <button className="danger" onClick={() => obrisi(p.pitanje_id)}
                                        style={{ padding: "0.25rem 0.5rem", fontSize: "0.85rem" }}>
                                    Obriši
                                </button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </>
    );
}