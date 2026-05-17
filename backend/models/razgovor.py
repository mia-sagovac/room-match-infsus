from datetime import datetime

from extensions import db

class Razgovor(db.Model):
    __tablename__ = "razgovor"

    razgovor_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer,
                         db.ForeignKey("match_korisnika.match_id", ondelete="CASCADE"),
                         nullable=False, unique=True)
    kreiran = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    aktivan = db.Column(db.Boolean, nullable=False, default=True)

    match = db.relationship("MatchKorisnika", back_populates="razgovor")
    poruke = db.relationship("Poruka", back_populates="razgovor",
                             cascade="all, delete-orphan",
                             order_by="Poruka.vrijeme_slanja")

    def to_dict(self) -> dict:
        return {
            "razgovor_id": self.razgovor_id,
            "match_id": self.match_id,
            "kreiran": self.kreiran.isoformat() if self.kreiran else None,
            "aktivan": self.aktivan,
        }
