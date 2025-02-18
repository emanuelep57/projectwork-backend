from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource, fields
from ..models import User
from .. import db, login_manager
from flask_login import login_user, current_user, logout_user


auth_ns = Namespace("auth", description="Operazioni di autenticazione")

# Definizione dei modelli per la documentazione openAPI
utente_model = auth_ns.model("Utente", {
    "id": fields.Integer(description="ID utente"),
    "email": fields.String(description="Email dell'utente"),
    "nome": fields.String(description="Nome dell'utente"),
    "cognome": fields.String(description="Cognome dell'utente"),
})

registrazione_model = auth_ns.model("Registrazione", {
    "nome": fields.String(required=True, description="Nome utente"),
    "cognome": fields.String(required=True, description="Cognome utente"),
    "email": fields.String(required=True, description="Email utente"),
    "password": fields.String(required=True, description="Password utente"),
})

login_model = auth_ns.model("Login", {
    "email": fields.String(required=True, description="Email utente"),
    "password": fields.String(required=True, description="Password utente"),
})


# carica l'utente
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_ns.route("/status")
class AuthStatus(Resource):
    @auth_ns.response(200, "Successo", utente_model)
    @auth_ns.response(401, "Non autenticato")
    def get(self):
        """Verifica lo stato dell'utente, se autenticato o meno"""
        if current_user.is_authenticated:
            return {
                "isAuthenticated": True,
                "user": {
                    "id": current_user.id,
                    "email": current_user.email,
                    "nome": current_user.nome,
                    "cognome": current_user.cognome,
                },
            }
        return {"isAuthenticated": False}, 401


@auth_ns.route("/registrazione")
class Registrazione(Resource):
    @auth_ns.expect(registrazione_model)
    @auth_ns.response(201, "Utente registrato con successo")
    @auth_ns.response(400, "Email già registrata")
    def post(self):
        """Registra un nuovo utente"""
        data = request.json
        if User.query.filter_by(email=data["email"]).first():
            return {"errore": "Email già registrata"}, 400

        user = User(
            nome=data["nome"],
            cognome=data["cognome"],
            email=data["email"],
            password=generate_password_hash(data["password"]),
        )
        db.session.add(user)
        db.session.commit()
        return {"messaggio": "Registrazione avvenuta con successo"}, 201


@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, "Login effettuato con successo", utente_model)
    @auth_ns.response(401, "Credenziali non valide")
    def post(self):
        """Effettua il login dell'utente"""
        data = request.json
        user = User.query.filter_by(email=data["email"]).first()
        if user and check_password_hash(user.password, data["password"]):
            login_user(user)
            return {
                "messaggio": "Log in avvenuto con successo",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nome": user.nome,
                    "cognome": user.cognome,
                },
            }
        return {"errore": "Credenziali non valide"}, 401


@auth_ns.route("/logout")
class Logout(Resource):
    @auth_ns.response(200, "Logout effettuato con successo")
    def post(self):
        """Effettua il logout dell'utente"""
        logout_user()
        return {"message": "Logout avvenuto con successo"}, 200
