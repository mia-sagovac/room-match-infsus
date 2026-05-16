"""Korisnik + Student/Zaposleni specijalizacije.

Mapira tablice `korisnik`, `student`, `zaposleni`. ENUM `tip_korisnika`
postoji u Postgresu, u SQLAlchemy ga predstavljamo kao String s validacijom
na Marshmallow nivou (jednostavnije od native ENUM mapiranja).
"""
from datetime import date, datetime

from extensions import db


class Korisnik(db.Model):
    __tablename__ = "korisnik"

    korisnik_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    lozinka_hash = db.Column(db.String(255), nullable=False)
    ime = db.Column(db.String(100), nullable=False)
    prezime = db.Column(db.String(100), nullable=False)
    datum_registracije = db.Column(db.Date, nullable=False, default=date.today)
    tip = db.Column(db.String(20), nullable=False, default="ostalo")
    aktivan = db.Column(db.Boolean, nullable=False, default=True)
    zadnja_aktivnost = db.Column(db.DateTime, default=datetime.utcnow)

    profil = db.relationship("Profil", uselist=False, back_populates="korisnik",
                             cascade="all, delete-orphan")
    preferencija = db.relationship("Preferencija", uselist=False, back_populates="korisnik",
                                   cascade="all, delete-orphan")
    student = db.relationship("Student", uselist=False, back_populates="korisnik",
                              cascade="all, delete-orphan")
    zaposleni = db.relationship("Zaposleni", uselist=False, back_populates="korisnik",
                                cascade="all, delete-orphan")
    upitnici = db.relationship("Upitnik", back_populates="korisnik",
                               cascade="all, delete-orphan")
    oglasi = db.relationship("Oglas", back_populates="korisnik",
                             cascade="all, delete-orphan")

    def to_dict(self, include_email: bool = False) -> dict:
        data = {
            "korisnik_id": self.korisnik_id,
            "ime": self.ime,
            "prezime": self.prezime,
            "tip": self.tip,
            "datum_registracije": self.datum_registracije.isoformat() if self.datum_registracije else None,
            "aktivan": self.aktivan,
        }
        if include_email:
            data["email"] = self.email
        return data


class Student(db.Model):
    __tablename__ = "student"

    korisnik_id = db.Column(db.Integer, db.ForeignKey("korisnik.korisnik_id", ondelete="CASCADE"),
                            primary_key=True)
    fakultet = db.Column(db.String(200), nullable=False)
    smjer = db.Column(db.String(200))
    godina_studija = db.Column(db.Integer)

    korisnik = db.relationship("Korisnik", back_populates="student")

    def to_dict(self) -> dict:
        return {
            "fakultet": self.fakultet,
            "smjer": self.smjer,
            "godina_studija": self.godina_studija,
        }


class Zaposleni(db.Model):
    __tablename__ = "zaposleni"

    korisnik_id = db.Column(db.Integer, db.ForeignKey("korisnik.korisnik_id", ondelete="CASCADE"),
                            primary_key=True)
    tvrtka = db.Column(db.String(200), nullable=False)
    pozicija = db.Column(db.String(200))

    korisnik = db.relationship("Korisnik", back_populates="zaposleni")

    def to_dict(self) -> dict:
        return {"tvrtka": self.tvrtka, "pozicija": self.pozicija}
