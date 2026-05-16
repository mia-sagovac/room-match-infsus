"""Preferencije korisnika prema potencijalnom cimeru."""
from extensions import db


class Preferencija(db.Model):
    __tablename__ = "preferencija"

    preferencija_id = db.Column(db.Integer, primary_key=True)
    korisnik_id = db.Column(db.Integer,
                            db.ForeignKey("korisnik.korisnik_id", ondelete="CASCADE"),
                            nullable=False, unique=True)
    min_budzet = db.Column(db.Numeric(10, 2))
    max_budzet = db.Column(db.Numeric(10, 2))
    zeljeni_grad = db.Column(db.String(100))
    zeljeni_kvart = db.Column(db.String(100))
    trazi_pusaca = db.Column(db.Boolean)
    zeljeni_ritam = db.Column(db.String(20))
    min_urednost = db.Column(db.Integer)

    korisnik = db.relationship("Korisnik", back_populates="preferencija")

    def to_dict(self) -> dict:
        return {
            "preferencija_id": self.preferencija_id,
            "korisnik_id": self.korisnik_id,
            "min_budzet": float(self.min_budzet) if self.min_budzet is not None else None,
            "max_budzet": float(self.max_budzet) if self.max_budzet is not None else None,
            "zeljeni_grad": self.zeljeni_grad,
            "zeljeni_kvart": self.zeljeni_kvart,
            "trazi_pusaca": self.trazi_pusaca,
            "zeljeni_ritam": self.zeljeni_ritam,
            "min_urednost": self.min_urednost,
        }
