"""Jedinični testovi prezentacijskog sloja (Routes/Controllers).

Sloj odgovoran: `backend/routes/*.py`.
Mock-iramo SERVIS preko `monkeypatch` — testiramo SAMO da ruta:
  - mapira HTTP request → service call sa pravim parametrima
  - mapira service rezultat ↔ HTTP response (status code, JSON shape)
  - hvata ValidationError → 400

Servis se ne izvršava (mock), baza se ne dira.
"""
import json
from unittest.mock import MagicMock

import pytest
from flask_jwt_extended import create_access_token

from services.pitanje_service import ValidationError


@pytest.fixture
def auth_header(app):
    """JWT bez stvaranja stvarnog korisnika — dovoljno je da postoji token.

    Za jedinične testove ruta NE TREBAMO stvarnog korisnika u bazi; jedino
    što testiramo je da Flask-JWT-Extended prihvati token i da ruta odgovori.
    """
    with app.app_context():
        token = create_access_token(identity="1")
    return {"Authorization": f"Bearer {token}"}


class TestPitanjeRoutes:
    """Testira rute šifrarnika sa mock servisom."""

    def test_get_lista_vraca_servis_rezultat(self, app, client, auth_header,
                                             monkeypatch):
        mock_pitanje = MagicMock()
        mock_pitanje.to_dict.return_value = {
            "pitanje_id": 1, "tekst_pitanja": "P?",
            "kategorija": "buka", "tip_odgovora": "skala_1_5",
            "tezina": 2, "aktivno": True,
        }
        mock_svc = MagicMock()
        mock_svc.list_pitanja.return_value = [mock_pitanje]
        monkeypatch.setattr("routes.pitanje._service", mock_svc)

        resp = client.get("/api/pitanja-admin", headers=auth_header)

        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert data[0]["pitanje_id"] == 1
        mock_svc.list_pitanja.assert_called_once()

    def test_get_lista_prosljeduje_search_query(self, app, client, auth_header,
                                                monkeypatch):
        mock_svc = MagicMock()
        mock_svc.list_pitanja.return_value = []
        monkeypatch.setattr("routes.pitanje._service", mock_svc)

        client.get("/api/pitanja-admin?search=tišina&only_active=true",
                   headers=auth_header)

        kwargs = mock_svc.list_pitanja.call_args.kwargs
        assert kwargs["search"] == "tišina"
        assert kwargs["only_active"] is True

    def test_post_kreira_i_vraca_201(self, app, client, auth_header, monkeypatch):
        mock_pitanje = MagicMock()
        mock_pitanje.to_dict.return_value = {"pitanje_id": 42}
        mock_svc = MagicMock()
        mock_svc.create_pitanje.return_value = mock_pitanje
        monkeypatch.setattr("routes.pitanje._service", mock_svc)

        resp = client.post(
            "/api/pitanja-admin",
            headers={**auth_header, "Content-Type": "application/json"},
            data=json.dumps({
                "tekst_pitanja": "Pitanje?",
                "kategorija": "buka", "tip_odgovora": "skala_1_5",
                "tezina": 2,
            }),
        )

        assert resp.status_code == 201
        assert resp.get_json()["pitanje_id"] == 42
        mock_svc.create_pitanje.assert_called_once()

    def test_post_validation_error_vraca_400(self, app, client, auth_header,
                                             monkeypatch):
        mock_svc = MagicMock()
        mock_svc.create_pitanje.side_effect = ValidationError("Pravilo X.")
        monkeypatch.setattr("routes.pitanje._service", mock_svc)

        resp = client.post(
            "/api/pitanja-admin",
            headers={**auth_header, "Content-Type": "application/json"},
            data=json.dumps({
                "tekst_pitanja": "P?", "kategorija": "buka",
                "tip_odgovora": "skala_1_5", "tezina": 2,
            }),
        )

        assert resp.status_code == 400
        assert "Pravilo X." in resp.get_json()["error"]

    def test_put_filtrira_nedozvoljena_polja(self, app, client, auth_header,
                                             monkeypatch):
        mock_pitanje = MagicMock()
        mock_pitanje.to_dict.return_value = {"pitanje_id": 1}
        mock_svc = MagicMock()
        mock_svc.update_pitanje.return_value = mock_pitanje
        monkeypatch.setattr("routes.pitanje._service", mock_svc)

        client.put(
            "/api/pitanja-admin/1",
            headers={**auth_header, "Content-Type": "application/json"},
            data=json.dumps({
                "tezina": 4,
                "pitanje_id": 999,
                "neki_random_field": "hack",
            }),
        )

        kwargs = mock_svc.update_pitanje.call_args.kwargs
        assert "tezina" in kwargs
        assert kwargs["tezina"] == 4
        assert "pitanje_id" not in kwargs
        assert "neki_random_field" not in kwargs

    def test_delete_vraca_ok(self, app, client, auth_header, monkeypatch):
        mock_svc = MagicMock()
        monkeypatch.setattr("routes.pitanje._service", mock_svc)

        resp = client.delete("/api/pitanja-admin/5", headers=auth_header)

        assert resp.status_code == 200
        assert resp.get_json() == {"ok": True}
        mock_svc.delete_pitanje.assert_called_once_with(5)

    def test_zahtijeva_autentifikaciju(self, client):
        resp = client.get("/api/pitanja-admin")
        assert resp.status_code == 401


class TestUpitnikAdminRoutes:

    def test_post_kreira_upitnik(self, app, client, auth_header, monkeypatch):
        mock_u = MagicMock()
        mock_u.to_dict.return_value = {"upitnik_id": 7, "verzija": 1}
        mock_svc = MagicMock()
        mock_svc.create_upitnik.return_value = mock_u
        monkeypatch.setattr("routes.upitnik_admin._service", mock_svc)

        resp = client.post(
            "/api/upitnici-admin",
            headers={**auth_header, "Content-Type": "application/json"},
            data=json.dumps({"korisnik_id": 42}),
        )

        assert resp.status_code == 201
        assert resp.get_json()["upitnik_id"] == 7
        kwargs = mock_svc.create_upitnik.call_args.kwargs
        assert kwargs["korisnik_id"] == 42

    def test_post_bez_korisnik_id_vraca_400(self, app, client, auth_header):
        resp = client.post(
            "/api/upitnici-admin",
            headers={**auth_header, "Content-Type": "application/json"},
            data=json.dumps({}),
        )
        assert resp.status_code == 400

    def test_post_odgovora_prosljeduje_servisu(self, app, client, auth_header,
                                                monkeypatch):
        mock_o = MagicMock()
        mock_o.to_dict.return_value = {"odgovor_id": 1, "vrijednost": "3"}
        mock_svc = MagicMock()
        mock_svc.add_odgovor.return_value = mock_o
        monkeypatch.setattr("routes.upitnik_admin._service", mock_svc)

        resp = client.post(
            "/api/upitnici-admin/5/odgovori",
            headers={**auth_header, "Content-Type": "application/json"},
            data=json.dumps({"pitanje_id": 10, "vrijednost": "3"}),
        )

        assert resp.status_code == 201
        mock_svc.add_odgovor.assert_called_once_with(
            upitnik_id=5, pitanje_id=10, vrijednost="3",
        )

    def test_validation_error_iz_servisa_postaje_400(self, app, client,
                                                     auth_header, monkeypatch):
        mock_svc = MagicMock()
        mock_svc.add_odgovor.side_effect = ValidationError("Format nije OK.")
        monkeypatch.setattr("routes.upitnik_admin._service", mock_svc)

        resp = client.post(
            "/api/upitnici-admin/5/odgovori",
            headers={**auth_header, "Content-Type": "application/json"},
            data=json.dumps({"pitanje_id": 10, "vrijednost": "bla"}),
        )
        assert resp.status_code == 400
        assert "Format nije OK." in resp.get_json()["error"]
