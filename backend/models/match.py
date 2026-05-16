"""Match između dvojice korisnika sa izračunatim postotkom kompatibilnosti."""
from datetime import datetime

from extensions import db


class MatchKorisnika(db.Model):
    __tablename__ = "match_korisnika"

    match_id = db.Column(db.Integer, primary_key=True)
    korisnik1_id = db.Column(db.Integer,
                             db.ForeignKey("korisnik.korisnik_id", ondelete="CASCADE"),
                             nullable=False)
    korisnik2_id = db.Column(db.Integer,
                             db.ForeignKey("korisnik.korisnik_id", ondelete="CASCADE"),
                             nullable=False)
    postotak_kompatibilnosti = db.Column(db.Numeric(5, 2), nullable=False)
    datum_matchanja = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="predlozen")

    __table_args__ = (
        db.UniqueConstraint("korisnik1_id", "korisnik2_id", name="uq_match_par"),
    )

    razgovor = db.relationship("Razgovor", uselist=False, back_populates="match",
                               cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "korisnik1_id": self.korisnik1_id,
            "korisnik2_id": self.korisnik2_id,
            "postotak_kompatibilnosti": float(self.postotak_kompatibilnosti),
            "datum_matchanja": self.datum_matchanja.isoformat() if self.datum_matchanja else None,
            "status": self.status,
        }
