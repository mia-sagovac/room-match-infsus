from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from services.pitanje_service import PitanjeService, ValidationError

bp = Blueprint("pitanje", __name__, url_prefix="/api/pitanja-admin")

_service = PitanjeService()

@bp.get("")
@jwt_required()
def lista_pitanja():
    only_active = request.args.get("only_active", "false").lower() in {"true", "1", "yes"}
    search = request.args.get("search") or None
    try:
        pitanja = _service.list_pitanja(only_active=only_active, search=search)
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    return jsonify([p.to_dict() for p in pitanja])

@bp.get("/<int:pitanje_id>")
@jwt_required()
def dohvati_pitanje(pitanje_id: int):
    try:
        p = _service.get_pitanje(pitanje_id)
    except ValidationError as e:
        return jsonify(error=str(e)), 404
    return jsonify(p.to_dict())

@bp.post("")
@jwt_required()
def kreiraj_pitanje():
    data = request.get_json(silent=True) or {}
    try:
        p = _service.create_pitanje(
            tekst_pitanja=data.get("tekst_pitanja", ""),
            kategorija=data.get("kategorija", "ostalo"),
            tip_odgovora=data.get("tip_odgovora", "skala_1_5"),
            tezina=int(data.get("tezina", 1)),
            aktivno=bool(data.get("aktivno", True)),
        )
    except (ValidationError, TypeError) as e:
        return jsonify(error=str(e)), 400
    return jsonify(p.to_dict()), 201

@bp.put("/<int:pitanje_id>")
@jwt_required()
def izmijeni_pitanje(pitanje_id: int):
    data = request.get_json(silent=True) or {}
    dozvoljena = {"tekst_pitanja", "kategorija", "tip_odgovora", "tezina", "aktivno"}
    changes = {k: v for k, v in data.items() if k in dozvoljena}
    if "tezina" in changes and changes["tezina"] is not None:
        try:
            changes["tezina"] = int(changes["tezina"])
        except (TypeError, ValueError):
            return jsonify(error="Težina mora biti broj."), 400
    try:
        p = _service.update_pitanje(pitanje_id, **changes)
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    return jsonify(p.to_dict())

@bp.delete("/<int:pitanje_id>")
@jwt_required()
def obrisi_pitanje(pitanje_id: int):
    try:
        _service.delete_pitanje(pitanje_id)
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    return jsonify(ok=True)
