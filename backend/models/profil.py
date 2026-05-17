from datetime import datetime

from extensions import db

class Profil(db.Model):
    __tablename__ = "profil"

    profil_id = db.Column(db.Integer, primary_key=True)
    korisnik_id = db.Column(db.Integer,
                            db.ForeignKey("korisnik.korisnik_id", ondelete="CASCADE"),
                            nullable=False, unique=True)
    grad = db.Column(db.String(100))
    kvart = db.Column(db.String(100))
    dob = db.Column(db.Integer)
    spol = db.Column(db.String(20))
    pusac = db.Column(db.Boolean, default=False)
    urednost = db.Column(db.Integer)
    ritam = db.Column(db.String(20), default="fleksibilno")
    kucni_ljubimci = db.Column(db.Boolean, default=False)
    zivotni_stil = db.Column(db.String(200))
    bio = db.Column(db.Text)
    profilna_slika_url = db.Column(db.String(500))
    azurirano = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    korisnik = db.relationship("Korisnik", back_populates="profil")

    def to_dict(self) -> dict:
        return {
            "profil_id": self.profil_id,
            "korisnik_id": self.korisnik_id,
            "grad": self.grad,
            "kvart": self.kvart,
            "dob": self.dob,
            "spol": self.spol,
            "pusac": self.pusac,
            "urednost": self.urednost,
            "ritam": self.ritam,
            "kucni_ljubimci": self.kucni_ljubimci,
            "zivotni_stil": self.zivotni_stil,
            "bio": self.bio,
            "profilna_slika_url": self.profilna_slika_url,
            "azurirano": self.azurirano.isoformat() if self.azurirano else None,
        }
