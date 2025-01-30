from flask import Blueprint, jsonify
from ..services.film_service import FilmService

bp = Blueprint('film', __name__)


@bp.route('/', methods=['GET'])
def get_films():
    films = FilmService.get_film()
    # Converto ogni film in un dizionario e poi in JSON
    # per restituirlo al client
    return jsonify([film.to_dict() for film in films])


@bp.route('/<int:film_id>', methods=['GET'])
def get_film(film_id):
    film = FilmService.get_film_per_id(film_id)
    if not film:
        return jsonify({'errore': 'Film non trovato'}), 404
    return jsonify(film.to_dict())
