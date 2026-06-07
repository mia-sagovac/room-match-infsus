import React, { useState } from "react";

export default function ProcessView() {
  const [instanceId, setInstanceId] = useState(null);
  const [aktivan_korak, setAktivniKorak] = useState(null);

  const pokreniProces = async () => {
    const res = await api.post("/api/proces/pokreni");
    const id = res.data.process_instance_id;
    setInstanceId(id);
    localStorage.setItem("process_instance_id", id);
    pratistanje(id);
  };

  const pratistanje = async (id) => {
    const res = await api.get(`/api/proces/stanje/${id}`);
    const aktivnosti = res.data.childActivityInstances || [];
    if (aktivnosti.length > 0) {
      setAktivniKorak(aktivnosti[0].activityName);
    }
  };

  return (
    <div>
      <h2>Proces pronalaska cimera</h2>
      {!instanceId ? (
        <button onClick={pokreniProces}>Pokreni proces</button>
      ) : (
        <div>
          <p>Trenutni korak: <strong>{aktivan_korak}</strong></p>
          <p>ID procesa: {instanceId}</p>
          <button onClick={() => pratistanje(instanceId)}>Osvježi</button>
        </div>
      )}
    </div>
  );
}