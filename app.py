# app.py — VitalHelp
import os
from flask import Flask
from config import Config
from extensions import db, login_manager, bcrypt
from routes import main_bp, auth_bp, mesures_bp, objectifs_bp, donnees_bp, analyse_bp, partage_bp, public_bp
from flask_wtf.csrf import generate_csrf
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app():
    app = Flask(__name__)
        # Render/Heroku : on est derrière un reverse proxy HTTPS
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mesures_bp)
    app.register_blueprint(objectifs_bp)     
    app.register_blueprint(donnees_bp)
    app.register_blueprint(analyse_bp)
    app.register_blueprint(partage_bp)
    app.register_blueprint(public_bp)

    # Contexte processor pour csrf_token()
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    with app.app_context():
        from models import User, Mesure, Objectif, AnalyseIA, LienPartage
        db.create_all()
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if "users" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("users")]
            if "avatar_url" not in columns:
                try:
                    if db.engine.dialect.name == "sqlite":
                        db.session.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255)"))
                    else:
                        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(255)"))
                    db.session.commit()
                except Exception:
                    db.session.rollback()
        # Handlers d'erreurs personnalisés
        from flask import render_template

        @app.errorhandler(404)
        def page_not_found(e):
            return render_template("errors/404.html"), 404

        @app.errorhandler(403)
        def forbidden(e):
            return render_template("errors/403.html"), 403

        @app.errorhandler(500)
        def server_error(e):
            return render_template("errors/500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)