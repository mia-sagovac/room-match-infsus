"""Master-detail šifrarnik za Upitnike.

Prefiks `/api/upitnici-admin` — odvojen od korisničke rute `/api/upitnik`
(koja postoji za UC "Ispunjavanje upitnika"). Ovdje se administrira upitnike
kao master-detail strukturu sa CRUD-om na header-u i pojedinačnim odgovorima.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from services.upitnik_service import UpitnikService
from services.pitanje_service import ValidationError
from extensions import db
from models import Korisnik

bp = Blueprint("upitnik_admin", __name__, url_prefix="/api/upitnici-admin")

_service = UpitnikService()


def _err(exc: Exception, code: int = 400):
    return jsonify(error=str(exc)), code


@bp.get("/korisnici")
@jwt_required()
def korisnici_za_dropdown():
    """Lookup endpoint za FK dropdown 'korisnik' u headeru master forme."""
    search = (request.args.get("search") or "").strip().lower()
    q = Korisnik.query.filter(Korisnik.aktivan.is_(True))
    if search:
        like = f"%{search}%"
        q = q.filter((Korisnik.ime.ilike(like))
                     | (Korisnik.prezime.ilike(like))
                     | (Korisnik.email.ilike(like)))
    korisnici = q.order_by(Korisnik.prezime, Korisnik.ime).limit(50).all()
    return jsonify([
        {"korisnik_id": k.korisnik_id, "ime": k.ime,
         "prezime": k.prezime, "email": k.email}
        for k in korisnici
    ])


@bp.get("")
@jwt_required()
def lista_upitnika():
    korisnik_id = request.args.get("korisnik_id", type=int)
    search = request.args.get("search") or None
    upitnici = _service.list_upitnici(korisnik_id=korisnik_id, search_korisnik=search)

    rezultat = []
    for u in upitnici:
        d = u.to_dict()
        if u.korisnik:
            d["korisnik"] = {
                "korisnik_id": u.korisnik.korisnik_id,
                "ime": u.korisnik.ime, "prezime": u.korisnik.prezime,
            }
        d["broj_odgovora"] = len(u.odgovori)
        rezultat.append(d)
    return jsonify(rezultat)


@bp.get("/<int:upitnik_id>")
@jwt_required()
def dohvati_upitnik(upitnik_id: int):
    try:
        u = _service.get_upitnik(upitnik_id)
    except ValidationError as e:
        return _err(e, 404)

    out = u.to_dict()
    if u.korisnik:
        out["korisnik"] = {
            "korisnik_id": u.korisnik.korisnik_id,
            "ime": u.korisnik.ime, "prezime": u.korisnik.prezime,
            "email": u.korisnik.email,
        }
    return jsonify(out)


@bp.post("")
@jwt_required()
def kreiraj_upitnik():
    data = request.get_json(silent=True) or {}
    korisnik_id = data.get("korisnik_id")
    if not korisnik_id:
        return jsonify(error="Polje 'korisnik_id' je obavezno."), 400
    try:
        u = _service.create_upitnik(
            korisnik_id=int(korisnik_id),
            odgovori=data.get("odgovori") or [],
        )
    except (ValidationError, ValueError) as e:
        return _err(e)
    return jsonify(u.to_dict()), 201


@bp.put("/<int:upitnik_id>")
@jwt_required()
def izmijeni_upitnik(upitnik_id: int):
    data = request.get_json(silent=True) or {}
    try:
        kid = data.get("korisnik_id")
        u = _service.update_upitnik(upitnik_id,
                                    korisnik_id=int(kid) if kid is not None else None)
    except (ValidationError, ValueError) as e:
        return _err(e)
    return jsonify(u.to_dict())


@bp.delete("/<int:upitnik_id>")
@jwt_required()
def obrisi_upitnik(upitnik_id: int):
    try:
        _service.delete_upitnik(upitnik_id)
    except ValidationError as e:
        return _err(e)
    return jsonify(ok=True)


@bp.post("/<int:upitnik_id>/odgovori")
@jwt_required()
def dodaj_odgovor(upitnik_id: int):
    data = request.get_json(silent=True) or {}
    try:
        o = _service.add_odgovor(
            upitnik_id=upitnik_id,
            pitanje_id=int(data["pitanje_id"]),
            vrijednost=data.get("vrijednost", ""),
        )
    except (ValidationError, KeyError, ValueError) as e:
        return _err(e)
    return jsonify(o.to_dict()), 201


@bp.put("/odgovori/<int:odgovor_id>")
@jwt_required()
def izmijeni_odgovor(odgovor_id: int):
    data = request.get_json(silent=True) or {}
    try:
        o = _service.update_odgovor(
            odgovor_id,
            vrijednost=data.get("vrijednost"),
            pitanje_id=int(data["pitanje_id"]) if data.get("pitanje_id") else None,
        )
    except (ValidationError, ValueError) as e:
        return _err(e)
    return jsonify(o.to_dict())


@bp.delete("/odgovori/<int:odgovor_id>")
@jwt_required()
def obrisi_odgovor(odgovor_id: int):
    try:
        _service.delete_odgovor(odgovor_id)
    except ValidationError as e:
        return _err(e)
    return jsonify(ok=True)


@bp.get("/<int:upitnik_id>/kompletnost")
@jwt_required()
def provjeri_kompletnost(upitnik_id: int):
    try:
        report = _service.provjeri_kompletnost(upitnik_id)
    except ValidationError as e:
        return _err(e, 404)
    return jsonify(report)
