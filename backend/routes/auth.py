import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from email_validator import validate_email, EmailNotValidError

from extensions import db, bcrypt
from models import Korisnik, Student, Zaposleni

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

DOZVOLJENI_TIPOVI = {"student", "zaposleni", "ostalo"}

def _validiraj_lozinku(lozinka: str) -> str | None:

    if len(lozinka) < 8:
        return "Lozinka mora imati barem 8 znakova."
    if not re.search(r"[A-Za-z]", lozinka) or not re.search(r"\d", lozinka):
        return "Lozinka mora sadržavati slova i brojeve."
    return None

@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    lozinka = data.get("lozinka") or ""
    ime = (data.get("ime") or "").strip()
    prezime = (data.get("prezime") or "").strip()
    tip = (data.get("tip") or "ostalo").strip()

    if not all([email, lozinka, ime, prezime]):
        return jsonify(error="Email, lozinka, ime i prezime su obavezni."), 400

    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError as e:
        return jsonify(error=f"Neispravan email: {e}"), 400

    if tip not in DOZVOLJENI_TIPOVI:
        return jsonify(error=f"Nepoznat tip korisnika: {tip}"), 400

    pwd_err = _validiraj_lozinku(lozinka)
    if pwd_err:
        return jsonify(error=pwd_err), 400

    if Korisnik.query.filter_by(email=email).first():
        return jsonify(error="Email je već registriran."), 409

    korisnik = Korisnik(
        email=email,
        lozinka_hash=bcrypt.generate_password_hash(lozinka).decode(),
        ime=ime,
        prezime=prezime,
        tip=tip,
    )
    db.session.add(korisnik)
    db.session.flush()

    if tip == "student":
        fakultet = (data.get("fakultet") or "").strip()
        if not fakultet:
            db.session.rollback()
            return jsonify(error="Za studenta je obavezan fakultet."), 400
        db.session.add(Student(
            korisnik_id=korisnik.korisnik_id,
            fakultet=fakultet,
            smjer=(data.get("smjer") or "").strip() or None,
            godina_studija=data.get("godina_studija"),
        ))
    elif tip == "zaposleni":
        tvrtka = (data.get("tvrtka") or "").strip()
        if not tvrtka:
            db.session.rollback()
            return jsonify(error="Za zaposlenog je obavezna tvrtka."), 400
        db.session.add(Zaposleni(
            korisnik_id=korisnik.korisnik_id,
            tvrtka=tvrtka,
            pozicija=(data.get("pozicija") or "").strip() or None,
        ))

    db.session.commit()

    token = create_access_token(identity=str(korisnik.korisnik_id))
    return jsonify(access_token=token, korisnik=korisnik.to_dict(include_email=True)), 201

@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    lozinka = data.get("lozinka") or ""

    if not email or not lozinka:
        return jsonify(error="Email i lozinka su obavezni."), 400

    korisnik = Korisnik.query.filter_by(email=email).first()
    if not korisnik or not bcrypt.check_password_hash(korisnik.lozinka_hash, lozinka):
        return jsonify(error="Neispravan email ili lozinka."), 401

    if not korisnik.aktivan:
        return jsonify(error="Račun je deaktiviran."), 403

    token = create_access_token(identity=str(korisnik.korisnik_id))
    return jsonify(access_token=token, korisnik=korisnik.to_dict(include_email=True)), 200

@bp.get("/me")
@jwt_required()
def me():
    korisnik_id = int(get_jwt_identity())
    korisnik = db.session.get(Korisnik, korisnik_id)
    if not korisnik:
        return jsonify(error="Korisnik ne postoji."), 404

    data = korisnik.to_dict(include_email=True)
    if korisnik.student:
        data["student"] = korisnik.student.to_dict()
    if korisnik.zaposleni:
        data["zaposleni"] = korisnik.zaposleni.to_dict()
    return jsonify(data)
