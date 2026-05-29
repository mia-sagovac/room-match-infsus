import json

import pytest
from flask_jwt_extended import create_access_token

from extensions import db

@pytest.fixture
def headers(app, kreiraj_korisnika):

    with app.app_context():
        k = kreiraj_korisnika(email="int@test.com")
        token = create_access_token(identity=str(k.korisnik_id))
        return {"Authorization": f"Bearer {token}",
                "Content-Type": "application/json"}, k.korisnik_id

class TestPitanjeKrozSveSlojeve:

    def test_post_validacija_pa_get_pa_put_pa_delete(self, client, headers):
        h, _ = headers

        r = client.post("/api/pitanja-admin", headers=h, data=json.dumps({
            "tekst_pitanja": "Voliš li tišinu navečer?",
            "kategorija": "navike",
            "tip_odgovora": "skala_1_5",
            "tezina": 2,
        }))
        assert r.status_code == 201, r.get_data(as_text=True)
        created_id = r.get_json()["pitanje_id"]

        r = client.get(f"/api/pitanja-admin/{created_id}", headers=h)
        assert r.status_code == 200
        assert r.get_json()["tekst_pitanja"] == "Voliš li tišinu navečer?"

        r = client.put(f"/api/pitanja-admin/{created_id}", headers=h, data=json.dumps({
            "tezina": 3,
        }))
        assert r.status_code == 200
        assert r.get_json()["tezina"] == 3

        r = client.get("/api/pitanja-admin?search=tišinu", headers=h)
        assert r.status_code == 200
        assert any(p["pitanje_id"] == created_id for p in r.get_json())

        r = client.delete(f"/api/pitanja-admin/{created_id}", headers=h)
        assert r.status_code == 200

        r = client.get(f"/api/pitanja-admin/{created_id}", headers=h)
        assert r.status_code == 404

    def test_validacija_p1_tekst_bez_upitnika(self, client, headers):
        h, _ = headers
        r = client.post("/api/pitanja-admin", headers=h, data=json.dumps({
            "tekst_pitanja": "Bez upitnika",
            "kategorija": "navike",
            "tip_odgovora": "skala_1_5",
            "tezina": 2,
        }))
        assert r.status_code == 400
        assert "?" in r.get_json()["error"]

    def test_validacija_p3_tezina_kategorija(self, client, headers):

        h, _ = headers
        r = client.post("/api/pitanja-admin", headers=h, data=json.dumps({
            "tekst_pitanja": "Provokativno pitanje?",
            "kategorija": "navike",
            "tip_odgovora": "skala_1_5",
            "tezina": 5,
        }))
        assert r.status_code == 400
        assert "visokoprioritetne" in r.get_json()["error"]

    def test_validacija_p2_duplikat(self, client, headers):
        h, _ = headers
        payload = {
            "tekst_pitanja": "Voliš li psećeg lika?",
            "kategorija": "ostalo",
            "tip_odgovora": "da_ne",
            "tezina": 2,
        }
        r1 = client.post("/api/pitanja-admin", headers=h, data=json.dumps(payload))
        assert r1.status_code == 201

        payload["tekst_pitanja"] = "VOLIŠ LI PSEĆEG LIKA?"
        r2 = client.post("/api/pitanja-admin", headers=h, data=json.dumps(payload))
        assert r2.status_code == 400
        assert "identičnim tekstom" in r2.get_json()["error"]

class TestUpitnikMasterDetailKrozSveSlojeve:

    def test_pun_zivotni_ciklus(self, app, client, headers, kreiraj_korisnika,
                                kreiraj_pitanje):
        h, _ = headers

        with app.app_context():
            drugi_korisnik = kreiraj_korisnika(email="drugi@test.com")
            p1 = kreiraj_pitanje(tekst="Voliš li mir?", tip="skala_1_5")
            p2 = kreiraj_pitanje(tekst="Pušiš li?", tip="da_ne", kategorija="zivotni_stil")
            korisnik_id = drugi_korisnik.korisnik_id
            p1_id, p2_id = p1.pitanje_id, p2.pitanje_id

        r = client.post("/api/upitnici-admin", headers=h, data=json.dumps({
            "korisnik_id": korisnik_id,
        }))
        assert r.status_code == 201, r.get_data(as_text=True)
        upitnik_id = r.get_json()["upitnik_id"]

        r = client.post(f"/api/upitnici-admin/{upitnik_id}/odgovori",
                        headers=h, data=json.dumps({
                "pitanje_id": p1_id, "vrijednost": "4",
            }))
        assert r.status_code == 201
        odg1_id = r.get_json()["odgovor_id"]

        r = client.post(f"/api/upitnici-admin/{upitnik_id}/odgovori",
                        headers=h, data=json.dumps({
                "pitanje_id": p2_id, "vrijednost": "ne",
            }))
        assert r.status_code == 201

        r = client.get(f"/api/upitnici-admin/{upitnik_id}", headers=h)
        assert r.status_code == 200
        data = r.get_json()
        assert len(data["odgovori"]) == 2
        assert data["korisnik"]["korisnik_id"] == korisnik_id

        r = client.get("/api/upitnici-admin?search=Korisnik", headers=h)
        assert r.status_code == 200
        ids = [u["upitnik_id"] for u in r.get_json()]
        assert upitnik_id in ids

        r = client.put(f"/api/upitnici-admin/odgovori/{odg1_id}",
                       headers=h, data=json.dumps({"vrijednost": "5"}))
        assert r.status_code == 200
        assert r.get_json()["vrijednost"] == "5"

        r = client.delete(f"/api/upitnici-admin/odgovori/{odg1_id}", headers=h)
        assert r.status_code == 200

        r = client.get(f"/api/upitnici-admin/{upitnik_id}", headers=h)
        assert len(r.get_json()["odgovori"]) == 1

        r = client.delete(f"/api/upitnici-admin/{upitnik_id}", headers=h)
        assert r.status_code == 200

    def test_validacija_u1_format_odgovora(self, app, client, headers,
                                           kreiraj_korisnika, kreiraj_pitanje):
        h, _ = headers
        with app.app_context():
            k = kreiraj_korisnika(email="val@test.com")
            p = kreiraj_pitanje(tekst="P?", tip="skala_1_5")
            kid, pid = k.korisnik_id, p.pitanje_id

        r = client.post("/api/upitnici-admin", headers=h,
                        data=json.dumps({"korisnik_id": kid}))
        upitnik_id = r.get_json()["upitnik_id"]

        r = client.post(f"/api/upitnici-admin/{upitnik_id}/odgovori",
                        headers=h, data=json.dumps({
                "pitanje_id": pid, "vrijednost": "tri",
            }))
        assert r.status_code == 400
        assert "broj 1–5" in r.get_json()["error"]

    def test_validacija_u2_duplikat_pitanja(self, app, client, headers,
                                            kreiraj_korisnika, kreiraj_pitanje):
        h, _ = headers
        with app.app_context():
            k = kreiraj_korisnika(email="dup@test.com")
            p = kreiraj_pitanje(tekst="P?", tip="skala_1_5")
            kid, pid = k.korisnik_id, p.pitanje_id

        r = client.post("/api/upitnici-admin", headers=h,
                        data=json.dumps({"korisnik_id": kid}))
        upitnik_id = r.get_json()["upitnik_id"]

        r = client.post(f"/api/upitnici-admin/{upitnik_id}/odgovori",
                        headers=h, data=json.dumps({
                "pitanje_id": pid, "vrijednost": "3",
            }))
        assert r.status_code == 201

        r = client.post(f"/api/upitnici-admin/{upitnik_id}/odgovori",
                        headers=h, data=json.dumps({
                "pitanje_id": pid, "vrijednost": "5",
            }))
        assert r.status_code == 400
        assert "već postoji" in r.get_json()["error"]

class TestPunRegistracijskiFlow:

    def test_register_login_create_pitanje_create_upitnik(self, client):

        r = client.post("/api/auth/register",
                        headers={"Content-Type": "application/json"},
                        data=json.dumps({
                            "email": "flow@test.com",
                            "lozinka": "test1234",
                            "ime": "Flow", "prezime": "Test",
                            "tip": "ostalo",
                        }))
        assert r.status_code == 201, r.get_data(as_text=True)
        token = r.get_json()["access_token"]
        h = {"Authorization": f"Bearer {token}",
             "Content-Type": "application/json"}

        r = client.get("/api/auth/me", headers=h)
        assert r.status_code == 200
        moj_id = r.get_json()["korisnik_id"]

        r = client.post("/api/pitanja-admin", headers=h, data=json.dumps({
            "tekst_pitanja": "End-to-end pitanje?",
            "kategorija": "navike", "tip_odgovora": "da_ne", "tezina": 1,
        }))
        assert r.status_code == 201
        pid = r.get_json()["pitanje_id"]

        r = client.post("/api/upitnici-admin", headers=h, data=json.dumps({
            "korisnik_id": moj_id,
            "odgovori": [{"pitanje_id": pid, "vrijednost": "da"}],
        }))
        assert r.status_code == 201
        upitnik_id = r.get_json()["upitnik_id"]

        r = client.get("/api/upitnici-admin", headers=h)
        assert any(u["upitnik_id"] == upitnik_id for u in r.get_json())