from __future__ import annotations

from extensions import db
from models import Pitanje
from repositories import PitanjeRepository

DOZVOLJENE_KATEGORIJE = {
    "navike", "urednost", "pusenje", "ritam_spavanja",
    "ljubimci", "buka", "drustvenost", "ostalo",
}

VISOKOPRIORITETNE_KATEGORIJE = {"urednost", "pusenje", "ritam_spavanja"}

DOZVOLJENI_TIPOVI_ODGOVORA = {"skala_1_5", "da_ne", "tekst", "visestruki_izbor"}

MAX_PITANJA_PO_KATEGORIJI_I_TEZINI = 5

class ValidationError(Exception):

    pass

class PitanjeService:

    def __init__(self, repository: PitanjeRepository | None = None):

        self.repo = repository or PitanjeRepository()

    def list_pitanja(self, only_active: bool = True,
                     search: str | None = None) -> list[Pitanje]:
        return self.repo.list_all(only_active=only_active, search=search)

    def get_pitanje(self, pitanje_id: int) -> Pitanje:
        p = self.repo.get_by_id(pitanje_id)
        if not p:
            raise ValidationError(f"Pitanje {pitanje_id} ne postoji.")
        return p

    def create_pitanje(self, *, tekst_pitanja: str, kategorija: str,
                       tip_odgovora: str, tezina: int,
                       aktivno: bool = True) -> Pitanje:
        self._validate_polja(tekst_pitanja, kategorija, tip_odgovora, tezina)
        self._validate_jedinstven_tekst(tekst_pitanja, exclude_id=None)
        self._validate_kapacitet_kategorije(kategorija, tezina,
                                            postojeci_id=None)
        p = self.repo.create(
            tekst_pitanja=tekst_pitanja,
            kategorija=kategorija,
            tip_odgovora=tip_odgovora,
            tezina=tezina,
            aktivno=aktivno,
        )
        db.session.commit()
        return p

    def update_pitanje(self, pitanje_id: int, **changes) -> Pitanje:
        p = self.get_pitanje(pitanje_id)

        novi_tekst = changes.get("tekst_pitanja", p.tekst_pitanja)
        nova_kat = changes.get("kategorija", p.kategorija)
        novi_tip = changes.get("tip_odgovora", p.tip_odgovora)
        nova_tez = changes.get("tezina", p.tezina)

        self._validate_polja(novi_tekst, nova_kat, novi_tip, nova_tez)
        if novi_tekst.strip().lower() != (p.tekst_pitanja or "").strip().lower():
            self._validate_jedinstven_tekst(novi_tekst, exclude_id=p.pitanje_id)
        if (nova_kat, nova_tez) != (p.kategorija, p.tezina):
            self._validate_kapacitet_kategorije(nova_kat, nova_tez,
                                                postojeci_id=p.pitanje_id)

        p = self.repo.update(p, **changes)
        db.session.commit()
        return p

    def delete_pitanje(self, pitanje_id: int) -> None:
        p = self.get_pitanje(pitanje_id)
        self.repo.delete(p)
        db.session.commit()

    @staticmethod
    def _validate_polja(tekst: str, kat: str, tip: str, tez: int) -> None:

        if not tekst or not tekst.strip():
            raise ValidationError("Tekst pitanja je obavezan.")
        if len(tekst) > 1000:
            raise ValidationError("Tekst pitanja je predugačak (max 1000 znakova).")

        if not tekst.strip().endswith("?"):
            raise ValidationError("Tekst pitanja mora završiti upitnikom '?'.")

        if kat not in DOZVOLJENE_KATEGORIJE:
            raise ValidationError(
                f"Kategorija '{kat}' nije dozvoljena. "
                f"Dozvoljene: {sorted(DOZVOLJENE_KATEGORIJE)}."
            )
        if tip not in DOZVOLJENI_TIPOVI_ODGOVORA:
            raise ValidationError(
                f"Tip odgovora '{tip}' nije dozvoljen. "
                f"Dozvoljeni: {sorted(DOZVOLJENI_TIPOVI_ODGOVORA)}."
            )
        if not isinstance(tez, int) or not (1 <= tez <= 5):
            raise ValidationError("Težina mora biti cijeli broj 1–5.")

        if tez >= 4 and kat not in VISOKOPRIORITETNE_KATEGORIJE:
            raise ValidationError(
                f"Težina {tez} dozvoljena je samo za visokoprioritetne kategorije "
                f"({sorted(VISOKOPRIORITETNE_KATEGORIJE)}); kategorija '{kat}' nije."
            )

    def _validate_jedinstven_tekst(self, tekst: str, exclude_id: int | None) -> None:

        if self.repo.exists_with_text(tekst, exclude_id=exclude_id):
            raise ValidationError(
                "Pitanje s identičnim tekstom (ignorirajući velika/mala slova) već postoji."
            )

    def _validate_kapacitet_kategorije(self, kategorija: str, tezina: int,
                                       postojeci_id: int | None) -> None:

        broj = self.repo.count_by_category_and_weight(kategorija, tezina)
        if postojeci_id is not None:
            p = self.repo.get_by_id(postojeci_id)
            if p and p.kategorija == kategorija and p.tezina == tezina:
                broj -= 1
        if broj >= MAX_PITANJA_PO_KATEGORIJI_I_TEZINI:
            raise ValidationError(
                f"Već postoji {broj} pitanja kategorije '{kategorija}' s težinom "
                f"{tezina}. Maksimalno {MAX_PITANJA_PO_KATEGORIJI_I_TEZINI}."
            )
