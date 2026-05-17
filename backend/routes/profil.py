from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Profil, Preferencija

bp = Blueprint("profil", __name__, url_prefix="/api")

PROFIL_POLJA = {
    "grad", "kvart", "dob", "spol", "pusac", "urednost", "ritam",
    "kucni_ljubimci", "zivotni_stil", "bio", "profilna_slika_url",
}
PREF_POLJA = {
    "min_budzet", "max_budzet", "zeljeni_grad", "zeljeni_kvart",
    "trazi_pusaca", "zeljeni_ritam", "min_urednost",
}

DOZVOLJENI_RITAM = {"rana_ptica", "nocna_sova", "fleksibilno"}

def _trenutni_id() -> int:
    return int(get_jwt_identity())

@bp.get("/profil")
@jwt_required()
def moj_profil():
    profil = Profil.query.filter_by(korisnik_id=_trenutni_id()).first()
    return jsonify(profil.to_dict() if profil else None)

@bp.put("/profil")
@jwt_required()
def azuriraj_profil():
    data = request.get_json(silent=True) or {}
    korisnik_id = _trenutni_id()

    profil = Profil.query.filter_by(korisnik_id=korisnik_id).first()
    if not profil:
        profil = Profil(korisnik_id=korisnik_id)
        db.session.add(profil)

    for polje in PROFIL_POLJA:
        if polje in data:
            setattr(profil, polje, data[polje])

    if profil.dob is not None and not (16 <= profil.dob <= 99):
        return jsonify(error="Dob mora biti između 16 i 99."), 400
    if profil.urednost is not None and not (1 <= profil.urednost <= 5):
        return jsonify(error="Urednost mora biti između 1 i 5."), 400
    if profil.ritam and profil.ritam not in DOZVOLJENI_RITAM:
        return jsonify(error=f"Ritam mora biti jedno od: {sorted(DOZVOLJENI_RITAM)}."), 400

    db.session.commit()
    return jsonify(profil.to_dict())

@bp.get("/preferencija")
@jwt_required()
def moja_preferencija():
    pref = Preferencija.query.filter_by(korisnik_id=_trenutni_id()).first()
    return jsonify(pref.to_dict() if pref else None)

@bp.put("/preferencija")
@jwt_required()
def azuriraj_preferenciju():
    data = request.get_json(silent=True) or {}
    korisnik_id = _trenutni_id()

    pref = Preferencija.query.filter_by(korisnik_id=korisnik_id).first()
    if not pref:
        pref = Preferencija(korisnik_id=korisnik_id)
        db.session.add(pref)

    for polje in PREF_POLJA:
        if polje in data:
            setattr(pref, polje, data[polje])

    if pref.min_budzet is not None and pref.min_budzet < 0:
        return jsonify(error="min_budzet mora biti >= 0."), 400
    if pref.max_budzet is not None and pref.max_budzet < 0:
        return jsonify(error="max_budzet mora biti >= 0."), 400
    if (pref.min_budzet is not None and pref.max_budzet is not None
            and pref.min_budzet > pref.max_budzet):
        return jsonify(error="min_budzet ne smije biti veći od max_budzet."), 400
    if pref.min_urednost is not None and not (1 <= pref.min_urednost <= 5):
        return jsonify(error="min_urednost mora biti između 1 i 5."), 400
    if pref.zeljeni_ritam and pref.zeljeni_ritam not in DOZVOLJENI_RITAM:
        return jsonify(error=f"Ritam mora biti jedno od: {sorted(DOZVOLJENI_RITAM)}."), 400

    db.session.commit()
    return jsonify(pref.to_dict())
