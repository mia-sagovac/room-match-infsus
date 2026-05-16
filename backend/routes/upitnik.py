"""Upitnik — pitanja i odgovori. UC: Ispunjavanje upitnika."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Pitanje, Upitnik, OdgovorUpitnika

bp = Blueprint("upitnik", __name__, url_prefix="/api")


def _trenutni_id() -> int:
    return int(get_jwt_identity())


@bp.get("/pitanja")
@jwt_required()
def lista_pitanja():
    pitanja = (Pitanje.query
               .filter_by(aktivno=True)
               .order_by(Pitanje.kategorija, Pitanje.pitanje_id)
               .all())
    return jsonify([p.to_dict() for p in pitanja])


@bp.get("/upitnik")
@jwt_required()
def moj_upitnik():
    """Vrati najnoviju verziju mojeg upitnika (ako postoji)."""
    upitnik = (Upitnik.query
               .filter_by(korisnik_id=_trenutni_id())
               .order_by(Upitnik.verzija.desc(), Upitnik.datum_ispunjavanja.desc())
               .first())
    return jsonify(upitnik.to_dict() if upitnik else None)


@bp.post("/upitnik")
@jwt_required()
def spremi_upitnik():
    """Stvori novi upitnik s odgovorima.

    Očekuje: { "odgovori": [{"pitanje_id": 1, "vrijednost": "5"}, ...] }
    Svaka iteracija pravi novi `upitnik` s incrementiranom verzijom.
    """
    data = request.get_json(silent=True) or {}
    odgovori_raw = data.get("odgovori")

    if not isinstance(odgovori_raw, list) or not odgovori_raw:
        return jsonify(error="Polje 'odgovori' mora biti neprazna lista."), 400

    korisnik_id = _trenutni_id()

    zadnji = (Upitnik.query
              .filter_by(korisnik_id=korisnik_id)
              .order_by(Upitnik.verzija.desc())
              .first())
    sljedeca_verzija = (zadnji.verzija + 1) if zadnji else 1

    upitnik = Upitnik(korisnik_id=korisnik_id, verzija=sljedeca_verzija)
    db.session.add(upitnik)
    db.session.flush()

    vidjena_pitanja: set[int] = set()
    for o in odgovori_raw:
        pid = o.get("pitanje_id")
        vr = o.get("vrijednost")
        if pid is None or vr is None:
            db.session.rollback()
            return jsonify(error="Svaki odgovor treba 'pitanje_id' i 'vrijednost'."), 400
        if pid in vidjena_pitanja:
            db.session.rollback()
            return jsonify(error=f"Duplicirano pitanje_id={pid}."), 400
        vidjena_pitanja.add(pid)

        if not db.session.get(Pitanje, pid):
            db.session.rollback()
            return jsonify(error=f"Pitanje {pid} ne postoji."), 400

        db.session.add(OdgovorUpitnika(
            upitnik_id=upitnik.upitnik_id,
            pitanje_id=pid,
            vrijednost=str(vr)[:500],
        ))

    db.session.commit()
    return jsonify(upitnik.to_dict()), 201
