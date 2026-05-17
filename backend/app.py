from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError

from config import Config
from extensions import db, jwt, bcrypt, cors
from routes import ALL_BLUEPRINTS

def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}},
        supports_credentials=False,
    )

    import models

    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "roommatch-backend"}

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

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
