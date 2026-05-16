"""RoomMatch backend — Flask app factory.

Pokretanje:
    flask --app app run --debug --port 5000

Ili u IDE-u: postavi `FLASK_APP=app.py` kao Run/Debug konfiguraciju.
"""
from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError

from .config import Config
from .extensions import db, jwt, bcrypt, cors
from .routes import ALL_BLUEPRINTS


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ekstenzije
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}},
        supports_credentials=False,  # JWT u Authorization headeru, ne cookie
    )

    # Modeli moraju biti importani prije nego što SQLAlchemy registrira tablice
    import models  # noqa: F401

    # Blueprintovi
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    # Health check
    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "roommatch-backend"}

    # Root ruta
    @app.get("/")
    def root():
        return {"message": "Pokrenut backend"}
    @app.errorhandler(SQLAlchemyError)
    def _db_err(err):
        db.session.rollback()
        app.logger.exception("DB error")
        return jsonify(error="Greška u bazi podataka."), 500

    @app.errorhandler(404)
    def _404(_):
        return jsonify(error="Nije pronađeno."), 404

    @app.errorhandler(405)
    def _405(_):
        return jsonify(error="Metoda nije dozvoljena."), 405

    @app.errorhandler(500)
    def _500(_):
        return jsonify(error="Interna greška servera."), 500

    return app


# Modul-level instanca za `flask --app app run`
app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
