from extensions import db

class Pitanje(db.Model):
    __tablename__ = "pitanje"

    pitanje_id = db.Column(db.Integer, primary_key=True)
    tekst_pitanja = db.Column(db.Text, nullable=False)
    kategorija = db.Column(db.String(30), nullable=False, default="ostalo")
    tip_odgovora = db.Column(db.String(30), nullable=False, default="skala_1_5")
    tezina = db.Column(db.Integer, nullable=False, default=1)
    aktivno = db.Column(db.Boolean, default=True)

    def to_dict(self) -> dict:
        return {
            "pitanje_id": self.pitanje_id,
            "tekst_pitanja": self.tekst_pitanja,
            "kategorija": self.kategorija,
            "tip_odgovora": self.tip_odgovora,
            "tezina": self.tezina,
            "aktivno": self.aktivno,
        }
