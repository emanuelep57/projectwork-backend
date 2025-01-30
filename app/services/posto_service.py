from ..models import Posto, Biglietto, Proiezione, Sala
from ..dto.posto_dto import PostoDTO, PostoOccupatoDTO


class PostoService:
    @staticmethod
    def get_posti_proiezione(id_proiezione: int) -> list[PostoDTO]:
        posti = Posto.query.join(Sala, Sala.id == Posto.id_sala) \
            .join(Proiezione, Proiezione.id_sala == Sala.id) \
            .filter(Proiezione.id == id_proiezione).all()

        return [PostoDTO.from_model(posto) for posto in posti]

    @staticmethod
    def get_posti_occupati(projection_id: int) -> list[PostoOccupatoDTO]:
        posti_occupati = Posto.query \
            .join(Biglietto, Biglietto.id_posto == Posto.id) \
            .filter(Biglietto.id_proiezione == projection_id) \
            .all()

        return [PostoOccupatoDTO.from_model(posto) for posto in posti_occupati]
