from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from .. import db, login_manager
from flask_login import login_user, current_user, logout_user

bp = Blueprint('autenticazione', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Carica l'utente dal DB.


@bp.route('/status')
def auth_status():
    if current_user.is_authenticated:
        return jsonify({
            'isAuthenticated': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'nome': current_user.nome
            }
        })
    return jsonify({'isAuthenticated': False}), 401


@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():  # Controlla email duplicata.
        return jsonify({'error': 'Email already registered'}), 400

    user = User(
        nome=data['nome'],
        cognome=data['cognome'],
        email=data['email'],
        password=generate_password_hash(data['password'])  # Hash password.
    )
    db.session.add(user)  # Aggiunge utente.
    db.session.commit()  # Salva nel DB.
    return jsonify({'message': 'User registered successfully'}), 201


# Login utente.
@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):  # Controlla credenziali.
        login_user(user)
        return jsonify({
            'message': 'Logged in successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'nome': user.nome
            }
        })
    return jsonify({'error': 'Invalid credentials'}), 401


@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()  # Questa funzione di Flask-Login rimuove la sessione
    return jsonify({'message': 'Logged out successfully'})