"""Jedinični testovi sloja za pristup podacima (Repository).

Sloj odgovoran: `backend/repositories/*.py`.
Mock-iramo NIŠTA (osim baze – koja je svojim postojanjem in-memory SQLite,
što je dovoljno za izolaciju od produkcije). Testiramo samo da repositoryji
ispravno čitaju/pišu u bazu.
"""
import pytest

from repositories import PitanjeRepository, UpitnikRepository


class TestPitanjeRepository:
    """Sloj DA (data access) — Pitanje."""

    def test_create_pohranjuje_pitanje(self, app):
        with app.app_context():
            p = PitanjeRepository.create(
                tekst_pitanja="Voliš li tišinu?",
                kategorija="buka",
                tip_odgovora="skala_1_5",
                tezina=3,
            )
            assert p.pitanje_id is not None
            assert PitanjeRepository.get_by_id(p.pitanje_id) is not None

    def test_get_by_id_vraca_none_za_nepostojece(self, app):
        with app.app_context():
            assert PitanjeRepository.get_by_id(99999) is None

    def test_list_all_filter_aktivno(self, app, kreiraj_pitanje):
        with app.app_context():
            kreiraj_pitanje(tekst="Aktivno?", aktivno=True)
            kreiraj_pitanje(tekst="Neaktivno?", aktivno=False)

            samo_aktivna = PitanjeRepository.list_all(only_active=True)
            sva = PitanjeRepository.list_all(only_active=False)

            assert len(samo_aktivna) == 1
            assert len(sva) == 2

    def test_list_all_search_case_insensitive(self, app, kreiraj_pitanje):
        with app.app_context():
            kreiraj_pitanje(tekst="Voliš li PSE?")
            kreiraj_pitanje(tekst="Voliš li mačke?")

            rez = PitanjeRepository.list_all(only_active=False, search="pse")
            assert len(rez) == 1
            assert "PSE" in rez[0].tekst_pitanja

    def test_exists_with_text_case_insensitive(self, app, kreiraj_pitanje):
        with app.app_context():
            p = kreiraj_pitanje(tekst="Voliš li tišinu?")

            assert PitanjeRepository.exists_with_text("VOLIŠ LI TIŠINU?")
            assert PitanjeRepository.exists_with_text("voliš li tišinu?")
            assert not PitanjeRepository.exists_with_text("Voliš li tišinu?",
                                                          exclude_id=p.pitanje_id)
            assert not PitanjeRepository.exists_with_text("Nepostojeći tekst?")

    def test_count_by_category_and_weight(self, app, kreiraj_pitanje):
        with app.app_context():
            kreiraj_pitanje(tekst="P1?", kategorija="urednost", tezina=4)
            kreiraj_pitanje(tekst="P2?", kategorija="urednost", tezina=4)
            kreiraj_pitanje(tekst="P3?", kategorija="urednost", tezina=3)

            assert PitanjeRepository.count_by_category_and_weight("urednost", 4) == 2
            assert PitanjeRepository.count_by_category_and_weight("urednost", 3) == 1
            assert PitanjeRepository.count_by_category_and_weight("buka", 4) == 0

    def test_update_mijenja_polja(self, app, kreiraj_pitanje):
        with app.app_context():
            p = kreiraj_pitanje(tekst="Staro?", tezina=2)
            PitanjeRepository.update(p, tekst_pitanja="Novo?", tezina=4)

            osvjezeno = PitanjeRepository.get_by_id(p.pitanje_id)
            assert osvjezeno.tekst_pitanja == "Novo?"
            assert osvjezeno.tezina == 4

    def test_delete_uklanja_iz_baze(self, app, kreiraj_pitanje):
        with app.app_context():
            p = kreiraj_pitanje(tekst="Za brisanje?")
            pid = p.pitanje_id

            PitanjeRepository.delete(p)
            assert PitanjeRepository.get_by_id(pid) is None


class TestUpitnikRepository:
    """Sloj DA — Upitnik + OdgovorUpitnika."""

    def test_create_i_get_upitnik(self, app, kreiraj_korisnika):
        with app.app_context():
            k = kreiraj_korisnika()
            u = UpitnikRepository.create(korisnik_id=k.korisnik_id, verzija=1)

            dohvacen = UpitnikRepository.get_by_id(u.upitnik_id)
            assert dohvacen is not None
            assert dohvacen.korisnik_id == k.korisnik_id

    def test_next_version_inkrementira(self, app, kreiraj_korisnika):
        with app.app_context():
            k = kreiraj_korisnika()
            assert UpitnikRepository.next_version_for(k.korisnik_id) == 1

            UpitnikRepository.create(korisnik_id=k.korisnik_id, verzija=1)
            from extensions import db
            db.session.commit()

            assert UpitnikRepository.next_version_for(k.korisnik_id) == 2

    def test_add_odgovor_povezuje_sa_upitnikom(self, app, kreiraj_korisnika,
                                               kreiraj_pitanje):
        with app.app_context():
            k = kreiraj_korisnika()
            u = UpitnikRepository.create(korisnik_id=k.korisnik_id, verzija=1)
            p = kreiraj_pitanje()

            o = UpitnikRepository.add_odgovor(u.upitnik_id, p.pitanje_id, "3")
            assert o.odgovor_id is not None

            dohvacen = UpitnikRepository.get_by_id(u.upitnik_id)
            assert len(dohvacen.odgovori) == 1
            assert dohvacen.odgovori[0].vrijednost == "3"

    def test_delete_upitnika_brise_kaskadno(self, app, kreiraj_korisnika,
                                            kreiraj_pitanje):
        with app.app_context():
            k = kreiraj_korisnika()
            u = UpitnikRepository.create(korisnik_id=k.korisnik_id, verzija=1)
            p = kreiraj_pitanje()
            o = UpitnikRepository.add_odgovor(u.upitnik_id, p.pitanje_id, "3")
            oid = o.odgovor_id

            UpitnikRepository.delete(u)
            assert UpitnikRepository.get_odgovor(oid) is None

    def test_list_all_filtrira_po_korisniku(self, app, kreiraj_korisnika):
        with app.app_context():
            k1 = kreiraj_korisnika(email="a@x.com")
            k2 = kreiraj_korisnika(email="b@x.com")
            UpitnikRepository.create(korisnik_id=k1.korisnik_id, verzija=1)
            UpitnikRepository.create(korisnik_id=k2.korisnik_id, verzija=1)
            from extensions import db
            db.session.commit()

            samo_k1 = UpitnikRepository.list_all(korisnik_id=k1.korisnik_id)
            assert len(samo_k1) == 1
            assert samo_k1[0].korisnik_id == k1.korisnik_id
