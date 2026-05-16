import { useEffect, useState } from "react";
import api from "../api/client.js";
import Modal from "./components/Modal.jsx";

const PRAZAN_PROFIL = {
  grad: "", kvart: "", dob: "", spol: "", pusac: false,
  urednost: 3, ritam: "fleksibilno", kucni_ljubimci: false,
  zivotni_stil: "", bio: "", profilna_slika_url: "",
};

const PRAZNE_PREF = {
  min_budzet: "", max_budzet: "",
  zeljeni_grad: "", zeljeni_kvart: "",
  trazi_pusaca: null, zeljeni_ritam: "",
  min_urednost: "",
};

export default function Profile() {
  const [profil, setProfil] = useState(PRAZAN_PROFIL);
  const [pref, setPref] = useState(PRAZNE_PREF);
  const [msg, setMsg] = useState({ type: "", text: "" });
  const [modal, setModal] = useState({ isOpen: false, type: "", title: "", message: "" });
  const [loading, setLoading] = useState(true);

  // učitaj profil i preferencije pri mountu
  useEffect(() => {
    Promise.all([api.get("/profil"), api.get("/preferencija")])
      .then(([p, pr]) => {
        if (p.data) setProfil({ ...PRAZAN_PROFIL, ...p.data });
        if (pr.data) setPref({ ...PRAZNE_PREF, ...pr.data });
      })
      .catch((err) => setMsg({ type: "error", text: err.response?.data?.error || "Greška." }))
      .finally(() => setLoading(false));
  }, []);

  // funkcije za update statea na input promjene
  const setProf = (k) => (e) => {
    const v = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setProfil({ ...profil, [k]: v });
  };
  const setP = (k) => (e) => {
    let v = e.target.value;
    if (e.target.type === "checkbox") v = e.target.checked;
    setPref({ ...pref, [k]: v });
  };

  // pretvori prazni string u null + parsiraj brojeve prije slanja
  const cisto = (obj, brojcana = []) => {
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      if (v === "" || v === undefined) {
        out[k] = null;
      } else if (brojcana.includes(k)) {
        out[k] = v === null ? null : Number(v);
      } else {
        out[k] = v;
      }
    }
    return out;
  };

  // spremi profil
  const spremiProfil = async (e) => {
    e.preventDefault();
    setMsg({ type: "", text: "" });
    try {
      const { data } = await api.put(
        "/profil",
        cisto(profil, ["dob", "urednost"])
      );
      setProfil({ ...PRAZAN_PROFIL, ...data });
      setModal({
        isOpen: true,
        type: "success",
        title: "Profil ažuriran",
        message: "Tvoji podaci su uspješno spremljeni.",
      });
    } catch (err) {
      setModal({
        isOpen: true,
        type: "error",
        title: "Greška",
        message: err.response?.data?.error || "Greška pri spremanju.",
      });
    }
  };

  // spremi preferencije
  const spremiPref = async (e) => {
    e.preventDefault();
    setMsg({ type: "", text: "" });
    try {
      const { data } = await api.put(
        "/preferencija",
        cisto(pref, ["min_budzet", "max_budzet", "min_urednost"])
      );
      setPref({ ...PRAZNE_PREF, ...data });
      setModal({
        isOpen: true,
        type: "success",
        title: "Preferencije ažurirane",
        message: "Tvoje preferencije su uspješno spremljene.",
      });
    } catch (err) {
      setModal({
        isOpen: true,
        type: "error",
        title: "Greška",
        message: err.response?.data?.error || "Greška pri spremanju.",
      });
    }
  };

  // prikaz ucitavanja
  if (loading) return <p>Učitavanje...</p>;

  return (
    <>
      <h2>Moj profil</h2>
      {msg.text && <p className={msg.type}>{msg.text}</p>}

      <form onSubmit={spremiProfil} className="card">
        <h3>Osobni podaci i navike</h3>
        <div className="row">
          <div>
            <label>Grad</label>
            <input value={profil.grad ?? ""} onChange={setProf("grad")} />
          </div>
          <div>
            <label>Kvart</label>
            <input value={profil.kvart ?? ""} onChange={setProf("kvart")} />
          </div>
        </div>

        <div className="row">
          <div>
            <label>Dob (16-99)</label>
            <input type="number" min="16" max="99"
                   value={profil.dob ?? ""} onChange={setProf("dob")} />
          </div>
          <div>
            <label>Spol</label>
            <select value={profil.spol ?? ""} onChange={setProf("spol")}>
              <option value="">—</option>
              <option value="M">M</option>
              <option value="Ž">Ž</option>
              <option value="ostalo">ostalo</option>
            </select>
          </div>
        </div>

        <div className="row">
          <div>
            <label>Urednost (1-5)</label>
            <input type="number" min="1" max="5"
                   value={profil.urednost ?? ""} onChange={setProf("urednost")} />
          </div>
          <div>
            <label>Ritam</label>
            <select value={profil.ritam ?? "fleksibilno"} onChange={setProf("ritam")}>
              <option value="rana_ptica">Rana ptica</option>
              <option value="nocna_sova">Noćna sova</option>
              <option value="fleksibilno">Fleksibilno</option>
            </select>
          </div>
        </div>

        <div className="row">
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input type="checkbox" style={{ width: "auto" }}
                   checked={!!profil.pusac} onChange={setProf("pusac")} />
            Pušač
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input type="checkbox" style={{ width: "auto" }}
                   checked={!!profil.kucni_ljubimci} onChange={setProf("kucni_ljubimci")} />
            Kućni ljubimci
          </label>
        </div>

        <label>Životni stil</label>
        <input value={profil.zivotni_stil ?? ""} onChange={setProf("zivotni_stil")} />

        <label>O meni</label>
        <textarea rows="3" value={profil.bio ?? ""} onChange={setProf("bio")} />

        <button type="submit" style={{ marginTop: "1rem" }}>Spremi profil</button>
      </form>

      <form onSubmit={spremiPref} className="card">
        <h3>Preferencije za cimera</h3>
        <div className="row">
          <div>
            <label>Min. budžet (€)</label>
            <input type="number" min="0" step="0.01"
                   value={pref.min_budzet ?? ""} onChange={setP("min_budzet")} />
          </div>
          <div>
            <label>Max. budžet (€)</label>
            <input type="number" min="0" step="0.01"
                   value={pref.max_budzet ?? ""} onChange={setP("max_budzet")} />
          </div>
        </div>

        <div className="row">
          <div>
            <label>Željeni grad</label>
            <input value={pref.zeljeni_grad ?? ""} onChange={setP("zeljeni_grad")} />
          </div>
          <div>
            <label>Željeni kvart</label>
            <input value={pref.zeljeni_kvart ?? ""} onChange={setP("zeljeni_kvart")} />
          </div>
        </div>

        <div className="row">
          <div>
            <label>Min. urednost (1-5)</label>
            <input type="number" min="1" max="5"
                   value={pref.min_urednost ?? ""} onChange={setP("min_urednost")} />
          </div>
          <div>
            <label>Željeni ritam</label>
            <select value={pref.zeljeni_ritam ?? ""} onChange={setP("zeljeni_ritam")}>
              <option value="">—</option>
              <option value="rana_ptica">Rana ptica</option>
              <option value="nocna_sova">Noćna sova</option>
              <option value="fleksibilno">Fleksibilno</option>
            </select>
          </div>
          <div>
            <label>Pušač cimer?</label>
            <select
              value={pref.trazi_pusaca === null || pref.trazi_pusaca === undefined ? "" : String(pref.trazi_pusaca)}
              onChange={(e) =>
                setPref({ ...pref, trazi_pusaca: e.target.value === "" ? null : e.target.value === "true" })
              }>
              <option value="">Svejedno</option>
              <option value="true">Da</option>
              <option value="false">Ne</option>
            </select>
          </div>
        </div>

        <button type="submit" style={{ marginTop: "1rem" }}>Spremi preferencije</button>
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
