"""Oglas za stan/sobu koji korisnik objavljuje."""
from datetime import datetime

from extensions import db


class Oglas(db.Model):
    __tablename__ = "oglas"

    oglas_id = db.Column(db.Integer, primary_key=True)
    korisnik_id = db.Column(db.Integer,
                            db.ForeignKey("korisnik.korisnik_id", ondelete="CASCADE"),
                            nullable=False)
    naslov = db.Column(db.String(300), nullable=False)
    opis = db.Column(db.Text)
    cijena = db.Column(db.Numeric(10, 2), nullable=False)
    adresa = db.Column(db.String(300))
    grad = db.Column(db.String(100), nullable=False)
    kvart = db.Column(db.String(100))
    broj_soba = db.Column(db.Integer)
    dostupno_od = db.Column(db.Date)
    aktivan = db.Column(db.Boolean, nullable=False, default=True)
    kreiran = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    korisnik = db.relationship("Korisnik", back_populates="oglasi")

    def to_dict(self) -> dict:
        return {
            "oglas_id": self.oglas_id,
            "korisnik_id": self.korisnik_id,
            "naslov": self.naslov,
            "opis": self.opis,
            "cijena": float(self.cijena),
            "adresa": self.adresa,
            "grad": self.grad,
            "kvart": self.kvart,
            "broj_soba": self.broj_soba,
            "dostupno_od": self.dostupno_od.isoformat() if self.dostupno_od else None,
            "aktivan": self.aktivan,
            "kreiran": self.kreiran.isoformat() if self.kreiran else None,
        }
