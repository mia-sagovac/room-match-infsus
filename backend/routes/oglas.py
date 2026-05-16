"""Oglasi za stanove/sobe — CRUD."""
from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Oglas

bp = Blueprint("oglas", __name__, url_prefix="/api/oglasi")


def _trenutni_id() -> int:
    return int(get_jwt_identity())


@bp.get("")
@jwt_required()
def lista_oglasa():
    """Aktivni oglasi s opcionalnim filterima."""
    args = request.args
    q = Oglas.query.filter_by(aktivan=True)

    if args.get("grad"):
        q = q.filter(Oglas.grad.ilike(args["grad"]))
    if args.get("kvart"):
        q = q.filter(Oglas.kvart.ilike(args["kvart"]))

    try:
        if args.get("max_cijena"):
            q = q.filter(Oglas.cijena <= float(args["max_cijena"]))
        if args.get("min_soba"):
            q = q.filter(Oglas.broj_soba >= int(args["min_soba"]))
    except ValueError:
        return jsonify(error="Neispravan numerički filter."), 400

    oglasi = q.order_by(Oglas.kreiran.desc()).limit(100).all()
    return jsonify([o.to_dict() for o in oglasi])


@bp.post("")
@jwt_required()
def kreiraj_oglas():
    data = request.get_json(silent=True) or {}

    obavezna = ("naslov", "cijena", "grad")
    if not all(data.get(p) for p in obavezna):
        return jsonify(error=f"Obavezna polja: {obavezna}."), 400

    try:
        cijena = float(data["cijena"])
    except (TypeError, ValueError):
        return jsonify(error="Cijena mora biti broj."), 400
    if cijena <= 0:
        return jsonify(error="Cijena mora biti > 0."), 400

    broj_soba = data.get("broj_soba")
    if broj_soba is not None and not (1 <= int(broj_soba) <= 10):
        return jsonify(error="broj_soba mora biti između 1 i 10."), 400

    dostupno_od = None
    if data.get("dostupno_od"):
        try:
            dostupno_od = date.fromisoformat(data["dostupno_od"])
        except ValueError:
            return jsonify(error="dostupno_od mora biti u formatu YYYY-MM-DD."), 400

    oglas = Oglas(
        korisnik_id=_trenutni_id(),
        naslov=data["naslov"][:300],
        opis=data.get("opis"),
        cijena=cijena,
        adresa=(data.get("adresa") or None),
        grad=data["grad"][:100],
        kvart=(data.get("kvart") or None),
        broj_soba=broj_soba,
        dostupno_od=dostupno_od,
    )
    db.session.add(oglas)
    db.session.commit()
    return jsonify(oglas.to_dict()), 201


@bp.delete("/<int:oglas_id>")
@jwt_required()
def obrisi_oglas(oglas_id: int):
    """Soft delete — postavi aktivan = False (vlasnik samo)."""
    oglas = db.session.get(Oglas, oglas_id)
    if not oglas:
        return jsonify(error="Oglas ne postoji."), 404
    if oglas.korisnik_id != _trenutni_id():
        return jsonify(error="Nemaš pravo brisati ovaj oglas."), 403

    oglas.aktivan = False
    db.session.commit()
    return jsonify(ok=True)
