from __future__ import annotations

from typing import Iterable

from sqlalchemy import func

from extensions import db
from models import Pitanje

class PitanjeRepository:

    @staticmethod
    def get_by_id(pitanje_id: int) -> Pitanje | None:
        return db.session.get(Pitanje, pitanje_id)

    @staticmethod
    def list_all(only_active: bool = True, search: str | None = None) -> list[Pitanje]:
        q = Pitanje.query
        if only_active:
            q = q.filter_by(aktivno=True)
        if search:
            like = f"%{search.lower()}%"
            q = q.filter(func.lower(Pitanje.tekst_pitanja).like(like))
        return q.order_by(Pitanje.kategorija, Pitanje.pitanje_id).all()

    @staticmethod
    def exists_with_text(tekst: str, exclude_id: int | None = None) -> bool:

        q = Pitanje.query.filter(func.lower(Pitanje.tekst_pitanja) == tekst.lower().strip())
        if exclude_id is not None:
            q = q.filter(Pitanje.pitanje_id != exclude_id)
        return db.session.query(q.exists()).scalar()

    @staticmethod
    def count_by_category_and_weight(kategorija: str, tezina: int) -> int:
        return Pitanje.query.filter_by(kategorija=kategorija, tezina=tezina).count()

    @staticmethod
    def create(tekst_pitanja: str, kategorija: str, tip_odgovora: str,
               tezina: int, aktivno: bool = True) -> Pitanje:
        p = Pitanje(
            tekst_pitanja=tekst_pitanja.strip(),
            kategorija=kategorija,
            tip_odgovora=tip_odgovora,
            tezina=tezina,
            aktivno=aktivno,
        )
        db.session.add(p)
        db.session.flush()
        return p

    @staticmethod
    def update(pitanje: Pitanje, **changes) -> Pitanje:
        for k, v in changes.items():
            if hasattr(pitanje, k) and v is not None:
                setattr(pitanje, k, v)
        db.session.flush()
        return pitanje

    @staticmethod
    def delete(pitanje: Pitanje) -> None:
        db.session.delete(pitanje)
        db.session.flush()
