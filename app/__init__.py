import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv
from flask_restx import Api
import json
from decimal import Decimal

# caricamento del file dotenv
load_dotenv()

# inizializzo le estensioni
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def create_app():
    app = Flask(__name__)
    app.json_encoder = DecimalEncoder
    api = Api(app, version="1.0", title="Cinema API", description="Gestione di utenti, film e prenotazioni")

    # App configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['RESTX_JSON'] = {'cls': DecimalEncoder}

    # Configurazione dei cookie di sessione
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True

    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": ["https://projectwork-frontend.vercel.app"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept",
                              "Origin", "X-Requested-With"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"],
            "max_age": 3600
        }
    })

    # passo l'istanza alle varie estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes import autenticazione, film, proiezioni, biglietti, posti, ordini

    # registrazione API
    api.add_namespace(autenticazione.auth_ns, path="/api/auth")
    api.add_namespace(film.film_ns, path='/api/films')
    api.add_namespace(proiezioni.proiezioni_ns, path='/api/proiezioni')
    api.add_namespace(biglietti.biglietti_ns, path='/api/biglietti')
    api.add_namespace(ordini.ordini_ns, path='/api/ordini')
    api.add_namespace(posti.posti_ns, path='/api/posti')

    return app
