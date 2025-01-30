from ..models import Film
from ..dto.film_dto import FilmDTO


class FilmService:
    @staticmethod
    # Recupera tutti i film dal database e ritorna una lista di film convertiti in dto
    def get_film():
        films = Film.query.all()
        return [FilmDTO.from_model(film) for film in films]

    @staticmethod
    # Recupera un film specifico
    def get_film_per_id(film_id: int):
        film = Film.query.get(film_id)
        return FilmDTO.from_model(film) if film else None
