"""SQLAlchemy modeli — mapirani 1:1 na shemu iz CreateBaze.txt."""
from .korisnik import Korisnik, Student, Zaposleni
from .profil import Profil
from .preferencija import Preferencija
from .pitanje import Pitanje
from .upitnik import Upitnik, OdgovorUpitnika
from .match import MatchKorisnika
from .razgovor import Razgovor
from .poruka import Poruka
from .oglas import Oglas

__all__ = [
    "Korisnik", "Student", "Zaposleni",
    "Profil", "Preferencija",
    "Pitanje", "Upitnik", "OdgovorUpitnika",
    "MatchKorisnika", "Razgovor", "Poruka", "Oglas",
]
