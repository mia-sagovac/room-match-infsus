from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_

from extensions import db
from models import Korisnik, MatchKorisnika, Razgovor
from services.kompatibilnost import izracunaj_kompatibilnost

bp = Blueprint("match", __name__, url_prefix="/api/match")

DOZVOLJENI_STATUSI = {"predlozen", "prihvacen", "odbijen", "istekao"}

def _trenutni_id() -> int:
    return int(get_jwt_identity())

def _bool_filter(value: str | None) -> bool | None:

    if value is None:
        return None
    v = value.strip().lower()
    if v in {"true", "1", "yes", "da"}:
        return True
    if v in {"false", "0", "no", "ne"}:
        return False
    return None

@bp.get("/preporuke")
@jwt_required()
def preporuke():

    ja_id = _trenutni_id()
    ja = db.session.get(Korisnik, ja_id)
    if not ja:
        return jsonify(error="Korisnik ne postoji."), 404

    args = request.args
    f_grad = args.get("grad")
    f_kvart = args.get("kvart")
    f_ritam = args.get("ritam")
    f_max_pusac = _bool_filter(args.get("max_pusac"))
    try:
        f_min_cijena = float(args["min_cijena"]) if args.get("min_cijena") else None
        f_max_cijena = float(args["max_cijena"]) if args.get("max_cijena") else None
        f_min_urednost = int(args["min_urednost"]) if args.get("min_urednost") else None
        f_min_postotak = float(args["min_postotak"]) if args.get("min_postotak") else 0.0
        limit = min(int(args.get("limit", 20)), 100)
    except ValueError:
        return jsonify(error="Neispravan numerički filter."), 400

    kandidati = (Korisnik.query
                 .filter(Korisnik.aktivan.is_(True))
                 .filter(Korisnik.korisnik_id != ja_id)
                 .all())

    rezultati = []
    for k in kandidati:

        if f_grad and (not k.profil or (k.profil.grad or "").lower() != f_grad.lower()):
            continue
        if f_kvart and (not k.profil or (k.profil.kvart or "").lower() != f_kvart.lower()):
            continue
        if f_ritam and (not k.profil or k.profil.ritam != f_ritam):
            continue
        if f_max_pusac is False and (k.profil and k.profil.pusac is True):
            continue
        if f_min_urednost is not None and (not k.profil or (k.profil.urednost or 0) < f_min_urednost):
            continue

        if f_min_cijena is not None and k.preferencija and k.preferencija.max_budzet is not None:
            if float(k.preferencija.max_budzet) < f_min_cijena:
                continue
        if f_max_cijena is not None and k.preferencija and k.preferencija.min_budzet is not None:
            if float(k.preferencija.min_budzet) > f_max_cijena:
                continue

        postotak, breakdown = izracunaj_kompatibilnost(ja, k)
        if postotak < f_min_postotak:
            continue

        rezultati.append({
            "korisnik": k.to_dict(),
            "profil": k.profil.to_dict() if k.profil else None,
            "preferencija": k.preferencija.to_dict() if k.preferencija else None,
            "postotak_kompatibilnosti": postotak,
            "detalji": breakdown,
        })

    rezultati.sort(key=lambda r: r["postotak_kompatibilnosti"], reverse=True)
    return jsonify(rezultati[:limit])

@bp.get("")
@jwt_required()
def moji_matchevi():

    ja_id = _trenutni_id()
    matchevi = (MatchKorisnika.query
                .filter(or_(MatchKorisnika.korisnik1_id == ja_id,
                            MatchKorisnika.korisnik2_id == ja_id))
                .order_by(MatchKorisnika.datum_matchanja.desc())
                .all())
    return jsonify([_obogati_match(m, ja_id) for m in matchevi])

@bp.post("")
@jwt_required()
def kreiraj_match():

    data = request.get_json(silent=True) or {}
    drugi_id = data.get("korisnik_id")
    if not drugi_id:
        return jsonify(error="Polje 'korisnik_id' je obavezno."), 400

    ja_id = _trenutni_id()
    if int(drugi_id) == ja_id:
        return jsonify(error="Ne možeš matchati samog sebe."), 400

    drugi = db.session.get(Korisnik, drugi_id)
    if not drugi or not drugi.aktivan:
        return jsonify(error="Drugi korisnik ne postoji ili nije aktivan."), 404

    k1, k2 = sorted([ja_id, int(drugi_id)])

    postojeci = MatchKorisnika.query.filter_by(korisnik1_id=k1, korisnik2_id=k2).first()
    if postojeci:
        return jsonify(_obogati_match(postojeci, ja_id)), 200

    ja = db.session.get(Korisnik, ja_id)
    postotak, _ = izracunaj_kompatibilnost(ja, drugi)

    match = MatchKorisnika(
        korisnik1_id=k1,
        korisnik2_id=k2,
        postotak_kompatibilnosti=postotak,
        status="predlozen",
    )
    db.session.add(match)
    db.session.commit()
    return jsonify(_obogati_match(match, ja_id)), 201

@bp.patch("/<int:match_id>")
@jwt_required()
def azuriraj_status_matcha(match_id: int):

    data = request.get_json(silent=True) or {}
    novi_status = data.get("status")
    if novi_status not in DOZVOLJENI_STATUSI:
        return jsonify(error=f"Status mora biti jedno od {sorted(DOZVOLJENI_STATUSI)}."), 400

    ja_id = _trenutni_id()
    match = db.session.get(MatchKorisnika, match_id)
    if not match:
        return jsonify(error="Match ne postoji."), 404
    if ja_id not in (match.korisnik1_id, match.korisnik2_id):
        return jsonify(error="Nemaš pristup ovom match-u."), 403

    match.status = novi_status

    if novi_status == "prihvacen" and not match.razgovor:
        razgovor = Razgovor(match_id=match.match_id)
        db.session.add(razgovor)

    db.session.commit()
    return jsonify(_obogati_match(match, ja_id))

def _obogati_match(match: MatchKorisnika, ja_id: int) -> dict:

    drugi_id = match.korisnik2_id if match.korisnik1_id == ja_id else match.korisnik1_id
    drugi = db.session.get(Korisnik, drugi_id)

    rezultat = match.to_dict()
    rezultat["drugi_korisnik"] = drugi.to_dict() if drugi else None
    if drugi and drugi.profil:
        rezultat["drugi_profil"] = drugi.profil.to_dict()
    rezultat["razgovor_id"] = match.razgovor.razgovor_id if match.razgovor else None
    return rezultat
