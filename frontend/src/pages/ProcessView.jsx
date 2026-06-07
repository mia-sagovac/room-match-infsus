import React, { useState, useEffect } from "react";
import api from "../api/client.js";

const CAMUNDA = "http://localhost:8080/engine-rest";

export default function ProcessView() {
    const [instanceId, setInstanceId] = useState(null);
    const [aktivanKorak, setAktivanKorak] = useState(null);
    const [task, setTask] = useState(null);
    const [zavrsen, setZavrsen] = useState(false);
    const [poruka, setPoruka] = useState("");
    const [odabraniId, setOdabraniId] = useState("");
    const [filterGrad, setFilterGrad] = useState("");
    const [filterRitam, setFilterRitam] = useState("");

    useEffect(() => {
        const spremljeni = localStorage.getItem("process_instance_id");
        if (spremljeni) {
            setInstanceId(spremljeni);
            osvjezi(spremljeni);
        }
    }, []);

    const pokreniProces = async () => {
        setPoruka("");
        const res = await api.post("/proces/pokreni");
        const id = res.data.process_instance_id;
        setInstanceId(id);
        setZavrsen(false);
        localStorage.setItem("process_instance_id", id);
        await osvjezi(id);
    };

    const dohvatiTask = async (id) => {
        const res = await fetch(`${CAMUNDA}/task?processInstanceId=${id}`);
        const tasks = await res.json();
        return tasks.length > 0 ? tasks[0] : null;
    };

    const osvjezi = async (id) => {
        setPoruka("");
        const stanje = await api.get(`/proces/stanje/${id}`);
        if (stanje.data.status === "zavrsen") {
            setZavrsen(true);
            setTask(null);
            setAktivanKorak(null);
            return;
        }
        const t = await dohvatiTask(id);
        setTask(t);
        setAktivanKorak(t ? t.name : "(servisni korak / cekanje)");
    };

    const completeTask = async (variables = {}) => {
        if (!task) return;
        await fetch(`${CAMUNDA}/task/${task.id}/complete`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ variables }),
        });
        await osvjezi(instanceId);
    };

    const korelirajPoruku = async (prihvacen) => {
        await fetch(`${CAMUNDA}/message`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                messageName: "odgovorMatcha",
                processInstanceId: instanceId,
                processVariables: {
                    match_prihvacen: { value: prihvacen, type: "Boolean" },
                },
            }),
        });
        await osvjezi(instanceId);
    };

    const renderAkcije = () => {
        const naziv = task?.name;

        if (naziv === "Registracija/Prijava") {
            return (
                <div>
                    <button onClick={() => completeTask({ profil_popunjen: { value: true, type: "Boolean" } })}>
                        Profil popunjen -> dalje
                    </button>
                    <button onClick={() => completeTask({ profil_popunjen: { value: false, type: "Boolean" } })}>
                        Profil nije popunjen
                    </button>
                </div>
            );
        }

        if (naziv === "Popuni profil") {
            return <button onClick={() => completeTask()}>Profil popunjen</button>;
        }

        if (naziv === "Ispuni upitnik") {
            return <button onClick={() => completeTask()}>Upitnik ispunjen</button>;
        }

        if (naziv === "Pregled preporuka + filtriranje") {
            return (
                <div>
                    <input
                        type="number"
                        placeholder="ID odabranog korisnika"
                        value={odabraniId}
                        onChange={(e) => setOdabraniId(e.target.value)}
                    />
                    <button
                        disabled={!odabraniId}
                        onClick={() =>
                            completeTask({
                                odabrao_cimera: { value: true, type: "Boolean" },
                                odabrani_korisnik_id: { value: Number(odabraniId), type: "Integer" },
                            })
                        }
                    >
                        Odaberi cimera
                    </button>
                </div>
            );
        }

        if (naziv === "Promijeni filtere") {
            return (
                <div>
                    <input placeholder="Grad" value={filterGrad} onChange={(e) => setFilterGrad(e.target.value)} />
                    <input placeholder="Ritam" value={filterRitam} onChange={(e) => setFilterRitam(e.target.value)} />
                    <button
                        onClick={() => {
                            const v = { nastavi_traziti: { value: true, type: "Boolean" } };
                            if (filterGrad) v.filter_grad = { value: filterGrad, type: "String" };
                            if (filterRitam) v.filter_ritam = { value: filterRitam, type: "String" };
                            completeTask(v);
                        }}
                    >
                        Primijeni filtere
                    </button>
                </div>
            );
        }

        if (naziv === "Otvori chat") {
            return <button onClick={() => completeTask()}>Otvori chat -> zavrsi</button>;
        }

        return (
            <div>
                <p>Cekanje odgovora na zahtjev za match.</p>
                <button onClick={() => korelirajPoruku(true)}>Match prihvacen</button>
                <button onClick={() => korelirajPoruku(false)}>Match odbijen</button>
            </div>
        );
    };

    return (
        <div>
            <h2>Proces pronalaska cimera</h2>

            {!instanceId ? (
                <button onClick={pokreniProces}>Pokreni proces</button>
            ) : zavrsen ? (
                <div>
                    <p>Proces je zavrsen.</p>
                    <p>ID procesa: {instanceId}</p>
                    <button
                        onClick={() => {
                            localStorage.removeItem("process_instance_id");
                            setInstanceId(null);
                            setZavrsen(false);
                        }}
                    >
                        Novi proces
                    </button>
                </div>
            ) : (
                <div>
                    <p>
                        Trenutni korak: <strong>{aktivanKorak}</strong>
                    </p>
                    <p>ID procesa: {instanceId}</p>
                    {renderAkcije()}
                    <button onClick={() => osvjezi(instanceId)}>Osvjezi</button>
                </div>
            )}

            {poruka && <p>{poruka}</p>}
        </div>
    );
}