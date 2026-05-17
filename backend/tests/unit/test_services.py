from unittest.mock import MagicMock

import pytest

from services.kompatibilnost import izracunaj_kompatibilnost
from services.pitanje_service import (
    PitanjeService, ValidationError,
    MAX_PITANJA_PO_KATEGORIJI_I_TEZINI,
)
from services.upitnik_service import UpitnikService

class TestPitanjeServiceValidacije:

    def _service_s_mockom(self, **mock_kwargs):
        mock = MagicMock()

        mock.exists_with_text.return_value = False
        mock.count_by_category_and_weight.return_value = 0
        mock.get_by_id.return_value = None
        for k, v in mock_kwargs.items():
            getattr(mock, k).return_value = v
        return PitanjeService(repository=mock), mock

    def test_odbija_tekst_bez_upitnika(self):
        svc, _ = self._service_s_mockom()
        with pytest.raises(ValidationError, match="završiti upitnikom"):
            svc.create_pitanje(
                tekst_pitanja="Voliš li tišinu",
                kategorija="buka", tip_odgovora="skala_1_5", tezina=2,
            )

    def test_prihvaca_tekst_s_upitnikom(self, monkeypatch):
        svc, mock = self._service_s_mockom()
        mock.create.return_value = MagicMock(pitanje_id=1)
        monkeypatch.setattr("services.pitanje_service.db.session.commit", lambda: None)

        svc.create_pitanje(
            tekst_pitanja="Voliš li tišinu?",
            kategorija="buka", tip_odgovora="skala_1_5", tezina=2,
        )
        mock.create.assert_called_once()

    def test_odbija_duplikat_teksta(self):
        svc, _ = self._service_s_mockom(exists_with_text=True)
        with pytest.raises(ValidationError, match="identičnim tekstom"):
            svc.create_pitanje(
                tekst_pitanja="Voliš li tišinu?",
                kategorija="buka", tip_odgovora="skala_1_5", tezina=2,
            )

    def test_odbija_visoku_tezinu_za_lowprio_kategoriju(self):
        svc, _ = self._service_s_mockom()
        with pytest.raises(ValidationError, match="visokoprioritetne"):
            svc.create_pitanje(
                tekst_pitanja="Voliš li tišinu?",
                kategorija="buka",
                tip_odgovora="skala_1_5", tezina=5,
            )

    def test_dozvoljava_visoku_tezinu_za_highprio_kategoriju(self, monkeypatch):
        svc, mock = self._service_s_mockom()
        mock.create.return_value = MagicMock(pitanje_id=1)
        monkeypatch.setattr("services.pitanje_service.db.session.commit", lambda: None)
        svc.create_pitanje(
            tekst_pitanja="Smeta li ti nered?",
            kategorija="urednost",
            tip_odgovora="skala_1_5", tezina=5,
        )
        mock.create.assert_called_once()

    def test_odbija_kreiranje_kad_je_kvota_puna(self):
        svc, _ = self._service_s_mockom(
            count_by_category_and_weight=MAX_PITANJA_PO_KATEGORIJI_I_TEZINI,
        )
        with pytest.raises(ValidationError, match="Maksimalno"):
            svc.create_pitanje(
                tekst_pitanja="Još jedno pitanje?",
                kategorija="navike", tip_odgovora="skala_1_5", tezina=2,
            )

    def test_odbija_nedozvoljenu_kategoriju(self):
        svc, _ = self._service_s_mockom()
        with pytest.raises(ValidationError, match="Kategorija"):
            svc.create_pitanje(
                tekst_pitanja="Pitanje?",
                kategorija="izmisljena", tip_odgovora="skala_1_5", tezina=1,
            )

    def test_odbija_neispravnu_tezinu(self):
        svc, _ = self._service_s_mockom()
        with pytest.raises(ValidationError, match="Težina"):
            svc.create_pitanje(
                tekst_pitanja="Pitanje?",
                kategorija="navike", tip_odgovora="skala_1_5", tezina=7,
            )

class TestUpitnikServiceValidacije:

    def _service(self, upitnik_mock=None, pitanje_mock=None):
        u_mock = upitnik_mock or MagicMock()
        p_mock = pitanje_mock or MagicMock()
        return UpitnikService(upitnik_repo=u_mock, pitanje_repo=p_mock), u_mock, p_mock

    def test_validira_format_skala_1_5_odbija_string(self):
        svc, u_mock, p_mock = self._service()
        u_mock.get_by_id.return_value = MagicMock(odgovori=[])
        p_mock.get_by_id.return_value = MagicMock(
            pitanje_id=1, tekst_pitanja="Voliš li tišinu?",
            tip_odgovora="skala_1_5",
        )
        with pytest.raises(ValidationError, match="broj 1–5"):
            svc.add_odgovor(upitnik_id=1, pitanje_id=1, vrijednost="ne znam")

    def test_validira_format_skala_1_5_odbija_van_raspona(self):
        svc, u_mock, p_mock = self._service()
        u_mock.get_by_id.return_value = MagicMock(odgovori=[])
        p_mock.get_by_id.return_value = MagicMock(
            pitanje_id=1, tekst_pitanja="P?", tip_odgovora="skala_1_5",
        )
        with pytest.raises(ValidationError, match="broj 1–5"):
            svc.add_odgovor(upitnik_id=1, pitanje_id=1, vrijednost="7")

    def test_validira_format_da_ne(self, monkeypatch):
        svc, u_mock, p_mock = self._service()
        u_mock.get_by_id.return_value = MagicMock(odgovori=[])
        p_mock.get_by_id.return_value = MagicMock(
            pitanje_id=2, tekst_pitanja="Pušiš?", tip_odgovora="da_ne",
        )
        monkeypatch.setattr("services.upitnik_service.db.session.commit", lambda: None)

        for vr in ["da", "DA", "Ne", "ne"]:
            u_mock.add_odgovor.return_value = MagicMock()
            svc.add_odgovor(upitnik_id=1, pitanje_id=2, vrijednost=vr)

        with pytest.raises(ValidationError, match="'da' ili 'ne'"):
            svc.add_odgovor(upitnik_id=1, pitanje_id=2, vrijednost="možda")

    def test_odbija_duplikat_pitanja_u_istom_upitniku(self):
        svc, u_mock, p_mock = self._service()
        postojeci_odgovor = MagicMock(odgovor_id=10, pitanje_id=1)
        u_mock.get_by_id.return_value = MagicMock(odgovori=[postojeci_odgovor])
        p_mock.get_by_id.return_value = MagicMock(
            pitanje_id=1, tekst_pitanja="P?", tip_odgovora="skala_1_5",
        )
        with pytest.raises(ValidationError, match="već postoji"):
            svc.add_odgovor(upitnik_id=1, pitanje_id=1, vrijednost="3")

class TestKompatibilnost:

    def _korisnik_s_profilom(self, **profil_atts):
        from types import SimpleNamespace
        defaults = dict(urednost=None, ritam=None, pusac=None, kucni_ljubimci=None,
                        grad=None, kvart=None, dob=None, spol=None, bio=None)
        defaults.update(profil_atts)
        profil = SimpleNamespace(**defaults)
        return SimpleNamespace(
            korisnik_id=1, profil=profil, preferencija=None, upitnici=[],
        )

    def test_identicni_profili_visoki_score(self):
        k1 = self._korisnik_s_profilom(
            urednost=4, ritam="fleksibilno", pusac=False, kucni_ljubimci=False,
        )
        k2 = self._korisnik_s_profilom(
            urednost=4, ritam="fleksibilno", pusac=False, kucni_ljubimci=False,
        )
        postotak, breakdown = izracunaj_kompatibilnost(k1, k2)
        assert breakdown["profil"] == 30
        assert postotak > 50

    def test_suprotni_ritmovi_nula_za_taj_segment(self):
        k1 = self._korisnik_s_profilom(urednost=3, ritam="rana_ptica",
                                       pusac=False, kucni_ljubimci=False)
        k2 = self._korisnik_s_profilom(urednost=3, ritam="nocna_sova",
                                       pusac=False, kucni_ljubimci=False)
        _, breakdown = izracunaj_kompatibilnost(k1, k2)

        assert breakdown["profil"] == 20

    def test_postotak_uvijek_u_rasponu_0_100(self):

        from types import SimpleNamespace
        k = SimpleNamespace(korisnik_id=1, profil=None, preferencija=None, upitnici=[])
        postotak, _ = izracunaj_kompatibilnost(k, k)
        assert 0 <= postotak <= 100
