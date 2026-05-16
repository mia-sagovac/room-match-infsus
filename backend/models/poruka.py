"""Pojedinačna poruka u razgovoru."""
from datetime import datetime

from extensions import db


class Poruka(db.Model):
    __tablename__ = "poruka"

    poruka_id = db.Column(db.Integer, primary_key=True)
    razgovor_id = db.Column(db.Integer,
                            db.ForeignKey("razgovor.razgovor_id", ondelete="CASCADE"),
                            nullable=False)
    posiljalac_id = db.Column(db.Integer,
                              db.ForeignKey("korisnik.korisnik_id", ondelete="SET NULL"),
                              nullable=False)
    sadrzaj = db.Column(db.Text, nullable=False)
    vrijeme_slanja = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    procitana = db.Column(db.Boolean, nullable=False, default=False)

    razgovor = db.relationship("Razgovor", back_populates="poruke")

    def to_dict(self) -> dict:
        return {
            "poruka_id": self.poruka_id,
            "razgovor_id": self.razgovor_id,
            "posiljalac_id": self.posiljalac_id,
            "sadrzaj": self.sadrzaj,
            "vrijeme_slanja": self.vrijeme_slanja.isoformat() if self.vrijeme_slanja else None,
            "procitana": self.procitana,
        }
