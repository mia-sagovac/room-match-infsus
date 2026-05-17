from __future__ import annotations

from extensions import db
from models import Upitnik, OdgovorUpitnika, Korisnik, Pitanje
from repositories import UpitnikRepository, PitanjeRepository
from services.pitanje_service import ValidationError

class UpitnikService:

    def __init__(self,
                 upitnik_repo: UpitnikRepository | None = None,
                 pitanje_repo: PitanjeRepository | None = None):
        self.repo = upitnik_repo or UpitnikRepository()
        self.pitanje_repo = pitanje_repo or PitanjeRepository()

    def list_upitnici(self, korisnik_id: int | None = None,
                      search_korisnik: str | None = None) -> list[Upitnik]:
        return self.repo.list_all(korisnik_id=korisnik_id,
                                  search_korisnik=search_korisnik)

    def get_upitnik(self, upitnik_id: int) -> Upitnik:
        u = self.repo.get_by_id(upitnik_id)
        if not u:
            raise ValidationError(f"Upitnik {upitnik_id} ne postoji.")
        return u

    def create_upitnik(self, *, korisnik_id: int,
                       odgovori: list[dict] | None = None) -> Upitnik:

        self._validate_korisnik(korisnik_id)

        verzija = self.repo.next_version_for(korisnik_id)
        upitnik = self.repo.create(korisnik_id=korisnik_id, verzija=verzija)

        if odgovori:
            self._add_odgovori_batch(upitnik, odgovori)

        db.session.commit()
        return upitnik

    def update_upitnik(self, upitnik_id: int, *,
                       korisnik_id: int | None = None) -> Upitnik:
        u = self.get_upitnik(upitnik_id)
        if korisnik_id is not None and korisnik_id != u.korisnik_id:
            self._validate_korisnik(korisnik_id)
            u = self.repo.update(u, korisnik_id=korisnik_id)
        db.session.commit()
        return u

    def delete_upitnik(self, upitnik_id: int) -> None:
        u = self.get_upitnik(upitnik_id)
        self.repo.delete(u)
        db.session.commit()

    def add_odgovor(self, upitnik_id: int, pitanje_id: int,
                    vrijednost: str) -> OdgovorUpitnika:
        upitnik = self.get_upitnik(upitnik_id)

        for o in upitnik.odgovori:
            if o.pitanje_id == pitanje_id:
                raise ValidationError(
                    f"Odgovor na pitanje {pitanje_id} već postoji u ovom upitniku."
                )

        pitanje = self.pitanje_repo.get_by_id(pitanje_id)
        if not pitanje:
            raise ValidationError(f"Pitanje {pitanje_id} ne postoji.")

        self._validate_format_odgovora(vrijednost, pitanje)

        o = self.repo.add_odgovor(upitnik_id, pitanje_id, vrijednost)
        db.session.commit()
        return o

    def update_odgovor(self, odgovor_id: int, *,
                       vrijednost: str | None = None,
                       pitanje_id: int | None = None) -> OdgovorUpitnika:
        odgovor = self.repo.get_odgovor(odgovor_id)
        if not odgovor:
            raise ValidationError(f"Odgovor {odgovor_id} ne postoji.")

        target_pitanje_id = pitanje_id or odgovor.pitanje_id
        pitanje = self.pitanje_repo.get_by_id(target_pitanje_id)
        if not pitanje:
            raise ValidationError(f"Pitanje {target_pitanje_id} ne postoji.")

        if pitanje_id is not None and pitanje_id != odgovor.pitanje_id:
            upitnik = self.get_upitnik(odgovor.upitnik_id)
            for o in upitnik.odgovori:
                if o.odgovor_id != odgovor.odgovor_id and o.pitanje_id == pitanje_id:
                    raise ValidationError(
                        f"Odgovor na pitanje {pitanje_id} već postoji u ovom upitniku."
                    )

        nova_vrijednost = vrijednost if vrijednost is not None else odgovor.vrijednost
        self._validate_format_odgovora(nova_vrijednost, pitanje)

        changes = {}
        if pitanje_id is not None:
            changes["pitanje_id"] = pitanje_id
        if vrijednost is not None:
            changes["vrijednost"] = vrijednost[:500]
        o = self.repo.update_odgovor(odgovor, **changes)
        db.session.commit()
        return o

    def delete_odgovor(self, odgovor_id: int) -> None:
        odgovor = self.repo.get_odgovor(odgovor_id)
        if not odgovor:
            raise ValidationError(f"Odgovor {odgovor_id} ne postoji.")
        self.repo.delete_odgovor(odgovor)
        db.session.commit()

    def provjeri_kompletnost(self, upitnik_id: int) -> dict:

        upitnik = self.get_upitnik(upitnik_id)
        obavezna = [p for p in self.pitanje_repo.list_all(only_active=True)
                    if p.tezina >= 4]
        odgovoreni_pid = {o.pitanje_id for o in upitnik.odgovori}
        nedostaju = [p.to_dict() for p in obavezna
                     if p.pitanje_id not in odgovoreni_pid]
        return {
            "kompletan": len(nedostaju) == 0,
            "broj_obaveznih": len(obavezna),
            "broj_odgovorenih_obaveznih": len(obavezna) - len(nedostaju),
            "nedostaju_pitanja": nedostaju,
        }

    def _validate_korisnik(self, korisnik_id: int) -> None:
        k = db.session.get(Korisnik, korisnik_id)
        if not k:
            raise ValidationError(f"Korisnik {korisnik_id} ne postoji.")
        if not k.aktivan:
            raise ValidationError(f"Korisnik {korisnik_id} nije aktivan.")

    def _add_odgovori_batch(self, upitnik: Upitnik, odgovori: list[dict]) -> None:
        vidjena: set[int] = set()
        for o in odgovori:
            pid = o.get("pitanje_id")
            vr = o.get("vrijednost")
            if pid is None or vr is None:
                raise ValidationError("Svaki odgovor treba 'pitanje_id' i 'vrijednost'.")
            if pid in vidjena:
                raise ValidationError(f"Duplicirano pitanje_id={pid} u jednom upitniku.")
            vidjena.add(pid)

            pitanje = self.pitanje_repo.get_by_id(pid)
            if not pitanje:
                raise ValidationError(f"Pitanje {pid} ne postoji.")
            self._validate_format_odgovora(vr, pitanje)

            self.repo.add_odgovor(upitnik.upitnik_id, pid, str(vr))

    @staticmethod
    def _validate_format_odgovora(vrijednost, pitanje: Pitanje) -> None:

        if vrijednost is None or str(vrijednost).strip() == "":
            raise ValidationError(
                f"Vrijednost odgovora za pitanje {pitanje.pitanje_id} ne smije biti prazna."
            )
        v = str(vrijednost).strip()

        if pitanje.tip_odgovora == "skala_1_5":
            try:
                n = int(v)
            except ValueError:
                raise ValidationError(
                    f"Pitanje '{pitanje.tekst_pitanja[:40]}…' očekuje broj 1–5, dobiven: '{v}'."
                )
            if not (1 <= n <= 5):
                raise ValidationError(
                    f"Pitanje '{pitanje.tekst_pitanja[:40]}…' očekuje broj 1–5, dobiven: {n}."
                )

        elif pitanje.tip_odgovora == "da_ne":
            if v.lower() not in {"da", "ne"}:
                raise ValidationError(
                    f"Pitanje '{pitanje.tekst_pitanja[:40]}…' očekuje 'da' ili 'ne', dobiven: '{v}'."
                )

        elif pitanje.tip_odgovora in {"tekst", "visestruki_izbor"}:
            if len(v) > 500:
                raise ValidationError(
                    f"Vrijednost odgovora je predugačka (max 500 znakova)."
                )

        else:
            raise ValidationError(
                f"Nepoznat tip_odgovora '{pitanje.tip_odgovora}' za pitanje {pitanje.pitanje_id}."
            )
