from dataclasses import dataclass
from typing import List


@dataclass
class FilmDTO:
    id: int
    titolo: str
    regista: str
    url_copertina: str
    durata: int
    descrizione: str
    generi: List[str]

    @classmethod
    def from_model(cls, film):
        return cls(
            id=film.id,
            titolo=film.titolo,
            regista=film.regista,
            url_copertina=film.url_copertina,
            durata=film.durata,
            descrizione=film.descrizione,
            generi=film.generi
        )

    def to_dict(self):
        return {
            'id': self.id,
            'titolo': self.titolo,
            'regista': self.regista,
            'url_copertina': self.url_copertina,
            'durata': self.durata,
            'descrizione': self.descrizione,
            'generi': self.generi
        }
