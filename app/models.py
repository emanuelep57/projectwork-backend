from datetime import datetime
from . import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ENUM, ARRAY
from sqlalchemy import Index

GenereFilm = ENUM(
    'Azione', 'Avventura', 'Commedia', 'Drammatico', 'Horror',
    'Thriller', 'Fantascienza', 'Fantasy', 'Animazione',
    'Documentario', 'Romantico',
    name='generefilm',
    create_type=True
)


class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column('id_film', db.Integer, primary_key=True)
    titolo = db.Column(db.String(50), nullable=False, unique=True)
    regista = db.Column(db.String(50), nullable=False)
    durata = db.Column(db.Integer, nullable=True)
    url_copertina = db.Column(db.String(255), nullable=False)
    descrizione = db.Column(db.String(500), nullable=False)
    generi = db.Column(ARRAY(GenereFilm), nullable=False)

    proiezioni = db.relationship('Proiezione', back_populates='film', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_film_titolo', 'titolo'),
    )


class User(UserMixin, db.Model):
    __tablename__ = 'utente'
    id = db.Column('id_utente', db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    ordini = db.relationship('Ordine', back_populates='utente', cascade='all, delete-orphan')
    biglietti = db.relationship('Biglietto', back_populates='utente', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_user_email', 'email'),
    )

    def __init__(self, nome, cognome, email, password):
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.password = password


class Sala(db.Model):
    __tablename__ = 'sala'
    id = db.Column('id_sala', db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    numero_posti = db.Column(db.Integer, nullable=False)

    proiezioni = db.relationship('Proiezione', back_populates='sala', cascade='all, delete-orphan')
    posti = db.relationship('Posto', back_populates='sala', cascade='all, delete-orphan')


class Proiezione(db.Model):
    __tablename__ = 'proiezione'
    id = db.Column('id_proiezione', db.Integer, primary_key=True)
    id_film = db.Column(db.Integer, db.ForeignKey('film.id_film'), nullable=False)
    id_sala = db.Column(db.Integer, db.ForeignKey('sala.id_sala'), nullable=False)
    data_ora = db.Column(db.DateTime, nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)

    film = db.relationship('Film', back_populates='proiezioni')
    sala = db.relationship('Sala', back_populates='proiezioni')
    biglietti = db.relationship('Biglietto', back_populates='proiezione', cascade='all, delete-orphan')
    ordini = db.relationship('Ordine', back_populates='proiezione', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_proiezione_film_sala', 'id_film', 'id_sala'),
        Index('idx_proiezione_data', 'data_ora'),
    )


class Ordine(db.Model):
    __tablename__ = 'ordine'
    id = db.Column('id_ordine', db.Integer, primary_key=True)
    id_utente = db.Column(db.Integer, db.ForeignKey('utente.id_utente'), nullable=False)
    id_proiezione = db.Column(db.Integer, db.ForeignKey('proiezione.id_proiezione'), nullable=False)
    data_acquisto = db.Column(db.DateTime, nullable=False, default=datetime.now())

    utente = db.relationship('User', back_populates='ordini')
    proiezione = db.relationship('Proiezione', back_populates='ordini')
    biglietti = db.relationship('Biglietto', back_populates='ordine', cascade='all, delete-orphan')
    pdf_url = db.Column(db.String(255))

    __table_args__ = (
        Index('idx_ordine_utente', 'id_utente'),
        Index('idx_ordine_proiezione', 'id_proiezione'),
    )


class Biglietto(db.Model):
    __tablename__ = 'biglietto'
    id = db.Column('id_biglietto', db.Integer, primary_key=True)
    id_proiezione = db.Column(db.Integer, db.ForeignKey('proiezione.id_proiezione'), nullable=False)
    id_utente = db.Column(db.Integer, db.ForeignKey('utente.id_utente'), nullable=False)
    id_posto = db.Column(db.Integer, db.ForeignKey('posto.id_posto'), nullable=False)
    id_ordine = db.Column(db.Integer, db.ForeignKey('ordine.id_ordine'), nullable=False)
    nome_ospite = db.Column(db.String(50))
    cognome_ospite = db.Column(db.String(50))

    proiezione = db.relationship('Proiezione', back_populates='biglietti')
    utente = db.relationship('User', back_populates='biglietti')
    posto = db.relationship('Posto', back_populates='biglietti')
    ordine = db.relationship('Ordine', back_populates='biglietti')

    __table_args__ = (
        Index('idx_biglietto_proiezione', 'id_proiezione'),
        Index('idx_biglietto_utente', 'id_utente'),
    )


class Posto(db.Model):
    __tablename__ = 'posto'
    id = db.Column('id_posto', db.Integer, primary_key=True)
    id_sala = db.Column(db.Integer, db.ForeignKey('sala.id_sala'), nullable=False)
    fila = db.Column(db.String(1), nullable=False)
    numero = db.Column(db.Integer, nullable=False)

    sala = db.relationship('Sala', back_populates='posti')
    biglietti = db.relationship('Biglietto', back_populates='posto')

    __table_args__ = (
        Index('idx_posto_sala', 'id_sala'),
        db.UniqueConstraint('id_sala', 'fila', 'numero', name='uq_sala_fila_numero'),
    )
