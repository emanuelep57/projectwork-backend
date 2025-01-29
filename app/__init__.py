import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv

# caricamento del file dotenv
load_dotenv()

# inizializzo le estensioni
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # App configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"]
        }
    })

    # passo l'istanza alle varie estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Registrazione blueprints
    from app.routes import autenticazione, film, proiezioni, biglietti, posti, ordini
    app.register_blueprint(autenticazione.bp, url_prefix='/api/auth')
    app.register_blueprint(film.bp, url_prefix='/api/films')
    app.register_blueprint(proiezioni.bp, url_prefix='/api/proiezioni')
    app.register_blueprint(biglietti.bp, url_prefix='/api/biglietti')
    app.register_blueprint(ordini.bp, url_prefix='/api/ordini')
    app.register_blueprint(posti.bp, url_prefix='/api/posti')

    return app
