from flask import Blueprint
from flask_restx import Namespace, Resource, fields
from ..services.film_service import FilmService

bp = Blueprint('film', __name__)
film_ns = Namespace('film', description='Operazioni sui film')

# Definizione dei modelli per la documentazione openAPI
film_model = film_ns.model('Film', {
    'id': fields.Integer(description='ID del film'),
    'titolo': fields.String(description='Titolo del film'),
    'regista': fields.String(description='Regista del film'),
    'url_copertina': fields.String(description='URL della copertina del film'),
    'durata': fields.Integer(description='Durata del film in minuti'),
    'descrizione': fields.String(description='Breve sinossi del film'),
    'generi': fields.List(fields.String, description='Generi del film')
})


@film_ns.route('/')
class FilmList(Resource):
    @film_ns.response(200, 'Successo', [film_model])
    def get(self):
        """Recupera la lista di tutti i film"""
        films = FilmService.get_film()
        return [film.to_dict() for film in films]


@film_ns.route('/<int:film_id>')
@film_ns.param('film_id', 'ID del film')
class Film(Resource):
    @film_ns.response(200, 'Successo', film_model)
    @film_ns.response(404, 'Film non trovato')
    def get(self, film_id):
        """Recupera un film specifico tramite ID"""
        film = FilmService.get_film_per_id(film_id)
        if not film:
            film_ns.abort(404, message='Film non trovato')
        return film.to_dict()