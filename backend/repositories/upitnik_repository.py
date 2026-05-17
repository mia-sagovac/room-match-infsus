from __future__ import annotations

from sqlalchemy.orm import joinedload

from extensions import db
from models import Upitnik, OdgovorUpitnika, Korisnik

class UpitnikRepository:

    @staticmethod
    def get_by_id(upitnik_id: int) -> Upitnik | None:
        return (Upitnik.query
                .options(joinedload(Upitnik.odgovori))
                .filter_by(upitnik_id=upitnik_id)
                .first())

    @staticmethod
    def list_all(korisnik_id: int | None = None,
                 search_korisnik: str | None = None) -> list[Upitnik]:

        q = Upitnik.query.options(joinedload(Upitnik.korisnik))

        if korisnik_id is not None:
            q = q.filter_by(korisnik_id=korisnik_id)

        if search_korisnik:
            like = f"%{search_korisnik.lower()}%"
            q = (q.join(Korisnik)
                  .filter((Korisnik.ime.ilike(like))
                          | (Korisnik.prezime.ilike(like))
                          | (Korisnik.email.ilike(like))))

        return q.order_by(Upitnik.datum_ispunjavanja.desc()).all()

    @staticmethod
    def next_version_for(korisnik_id: int) -> int:
        zadnji = (Upitnik.query
                  .filter_by(korisnik_id=korisnik_id)
                  .order_by(Upitnik.verzija.desc())
                  .first())
        return (zadnji.verzija + 1) if zadnji else 1

    @staticmethod
    def get_odgovor(odgovor_id: int) -> OdgovorUpitnika | None:
        return db.session.get(OdgovorUpitnika, odgovor_id)

    @staticmethod
    def create(korisnik_id: int, verzija: int) -> Upitnik:
        u = Upitnik(korisnik_id=korisnik_id, verzija=verzija)
        db.session.add(u)
        db.session.flush()
        return u

    @staticmethod
    def update(upitnik: Upitnik, **changes) -> Upitnik:
        for k, v in changes.items():
            if hasattr(upitnik, k) and v is not None:
                setattr(upitnik, k, v)
        db.session.flush()
        return upitnik

    @staticmethod
    def delete(upitnik: Upitnik) -> None:

        db.session.delete(upitnik)
        db.session.flush()

    @staticmethod
    def add_odgovor(upitnik_id: int, pitanje_id: int,
                    vrijednost: str) -> OdgovorUpitnika:
        o = OdgovorUpitnika(
            upitnik_id=upitnik_id,
            pitanje_id=pitanje_id,
            vrijednost=str(vrijednost)[:500],
        )
        db.session.add(o)
        db.session.flush()
        return o

    @staticmethod
    def update_odgovor(odgovor: OdgovorUpitnika, **changes) -> OdgovorUpitnika:
        for k, v in changes.items():
            if hasattr(odgovor, k) and v is not None:
                setattr(odgovor, k, v)
        db.session.flush()
        return odgovor

    @staticmethod
    def delete_odgovor(odgovor: OdgovorUpitnika) -> None:
        db.session.delete(odgovor)
        db.session.flush()
