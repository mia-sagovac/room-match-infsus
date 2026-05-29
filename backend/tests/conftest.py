import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.dirname(HERE)
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-not-for-production")
os.environ.setdefault("FRONTEND_ORIGIN", "http://localhost:5173")

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from config import Config
from extensions import db, bcrypt
from models import Korisnik, Pitanje

class TestConfig(Config):

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    JWT_SECRET_KEY = "test-secret-not-for-production"
    SQLALCHEMY_ENGINE_OPTIONS = {}

@pytest.fixture(scope="function")
def app():

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):

    return app.test_client()

@pytest.fixture
def session(app):

    return db.session

@pytest.fixture
def kreiraj_korisnika(session):

    def _factory(email: str = "test@example.com", ime: str = "Test",
                 prezime: str = "Korisnik", lozinka: str = "test1234",
                 tip: str = "ostalo", aktivan: bool = True) -> Korisnik:
        k = Korisnik(
            email=email,
            lozinka_hash=bcrypt.generate_password_hash(lozinka).decode(),
            ime=ime, prezime=prezime, tip=tip, aktivan=aktivan,
        )
        session.add(k)
        session.commit()
        return k
    return _factory

@pytest.fixture
def kreiraj_pitanje(session):

    def _factory(tekst: str = "Voliš li tišinu navečer?",
                 kategorija: str = "navike", tip: str = "skala_1_5",
                 tezina: int = 3, aktivno: bool = True) -> Pitanje:
        p = Pitanje(tekst_pitanja=tekst, kategorija=kategorija,
                    tip_odgovora=tip, tezina=tezina, aktivno=aktivno)
        session.add(p)
        session.commit()
        return p
    return _factory

@pytest.fixture
def auth_headers(app, kreiraj_korisnika):

    def _factory(email: str = "auth@example.com", **kwargs):
        with app.app_context():
            k = kreiraj_korisnika(email=email, **kwargs)
            token = create_access_token(identity=str(k.korisnik_id))
        return {"Authorization": f"Bearer {token}"}, k
    return _factory