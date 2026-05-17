from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from extensions import db
from models import Razgovor, Poruka, MatchKorisnika

bp = Blueprint("razgovor", __name__, url_prefix="/api/razgovori")

def _trenutni_id() -> int:
    return int(get_jwt_identity())

def _smije_pristupiti(razgovor: Razgovor, ja_id: int) -> bool:
    m = razgovor.match
    return m is not None and ja_id in (m.korisnik1_id, m.korisnik2_id)

@bp.get("")
@jwt_required()
def moji_razgovori():
    ja_id = _trenutni_id()
    razgovori = (Razgovor.query
                 .join(MatchKorisnika, Razgovor.match_id == MatchKorisnika.match_id)
                 .filter(or_(MatchKorisnika.korisnik1_id == ja_id,
                             MatchKorisnika.korisnik2_id == ja_id))
                 .order_by(Razgovor.kreiran.desc())
                 .all())

    rezultat = []
    for r in razgovori:
        m = r.match
        drugi_id = m.korisnik2_id if m.korisnik1_id == ja_id else m.korisnik1_id
        zadnja = (Poruka.query
                  .filter_by(razgovor_id=r.razgovor_id)
                  .order_by(Poruka.vrijeme_slanja.desc())
                  .first())
        rezultat.append({
            **r.to_dict(),
            "drugi_korisnik_id": drugi_id,
            "postotak_kompatibilnosti": float(m.postotak_kompatibilnosti),
            "zadnja_poruka": zadnja.to_dict() if zadnja else None,
        })
    return jsonify(rezultat)

@bp.get("/<int:razgovor_id>/poruke")
@jwt_required()
def poruke_razgovora(razgovor_id: int):
    ja_id = _trenutni_id()
    razgovor = db.session.get(Razgovor, razgovor_id)
    if not razgovor:
        return jsonify(error="Razgovor ne postoji."), 404
    if not _smije_pristupiti(razgovor, ja_id):
        return jsonify(error="Nemaš pristup ovom razgovoru."), 403

    Poruka.query.filter(
        Poruka.razgovor_id == razgovor_id,
        Poruka.posiljalac_id != ja_id,
        Poruka.procitana.is_(False),
    ).update({"procitana": True}, synchronize_session=False)
    db.session.commit()

    poruke = (Poruka.query
              .filter_by(razgovor_id=razgovor_id)
              .order_by(Poruka.vrijeme_slanja.asc())
              .all())
    return jsonify([p.to_dict() for p in poruke])

@bp.post("/<int:razgovor_id>/poruke")
@jwt_required()
def posalji_poruku(razgovor_id: int):
    data = request.get_json(silent=True) or {}
    sadrzaj = (data.get("sadrzaj") or "").strip()
    if not sadrzaj:
        return jsonify(error="Sadržaj poruke ne smije biti prazan."), 400
    if len(sadrzaj) > 5000:
        return jsonify(error="Poruka je predugačka (max 5000 znakova)."), 400

    ja_id = _trenutni_id()
    razgovor = db.session.get(Razgovor, razgovor_id)
    if not razgovor:
        return jsonify(error="Razgovor ne postoji."), 404
    if not _smije_pristupiti(razgovor, ja_id):
        return jsonify(error="Nemaš pristup ovom razgovoru."), 403
    if not razgovor.aktivan:
        return jsonify(error="Razgovor je zatvoren."), 400

    poruka = Poruka(
        razgovor_id=razgovor_id,
        posiljalac_id=ja_id,
        sadrzaj=sadrzaj,
    )
    db.session.add(poruka)
    db.session.commit()
    return jsonify(poruka.to_dict()), 201
