from datetime import datetime

from extensions import db

class Upitnik(db.Model):
    __tablename__ = "upitnik"

    upitnik_id = db.Column(db.Integer, primary_key=True)
    korisnik_id = db.Column(db.Integer,
                            db.ForeignKey("korisnik.korisnik_id", ondelete="CASCADE"),
                            nullable=False)
    datum_ispunjavanja = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    verzija = db.Column(db.Integer, nullable=False, default=1)

    korisnik = db.relationship("Korisnik", back_populates="upitnici")
    odgovori = db.relationship("OdgovorUpitnika", back_populates="upitnik",
                               cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "upitnik_id": self.upitnik_id,
            "korisnik_id": self.korisnik_id,
            "datum_ispunjavanja": self.datum_ispunjavanja.isoformat() if self.datum_ispunjavanja else None,
            "verzija": self.verzija,
            "odgovori": [o.to_dict() for o in self.odgovori],
        }

class OdgovorUpitnika(db.Model):
    __tablename__ = "odgovor_upitnika"

    odgovor_id = db.Column(db.Integer, primary_key=True)
    upitnik_id = db.Column(db.Integer,
                           db.ForeignKey("upitnik.upitnik_id", ondelete="CASCADE"),
                           nullable=False)
    pitanje_id = db.Column(db.Integer,
                           db.ForeignKey("pitanje.pitanje_id", ondelete="RESTRICT"),
                           nullable=False)
    vrijednost = db.Column(db.String(500), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("upitnik_id", "pitanje_id", name="uq_upitnik_pitanje"),
    )

    upitnik = db.relationship("Upitnik", back_populates="odgovori")
    pitanje = db.relationship("Pitanje")

    def to_dict(self) -> dict:
        return {
            "odgovor_id": self.odgovor_id,
            "upitnik_id": self.upitnik_id,
            "pitanje_id": self.pitanje_id,
            "vrijednost": self.vrijednost,
        }
