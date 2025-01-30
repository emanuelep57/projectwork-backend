from datetime import datetime
from ..models import Proiezione
from ..dto.proiezione_dto import ProiezioneDTO


# Prendo tutte le proiezioni future.
class ProiezioneService:
    @staticmethod
    def get_proiezioni(film_id: int):
        now = datetime.now()
        proiezioni = Proiezione.query \
            .filter_by(id_film=film_id) \
            .filter(Proiezione.data_ora > now) \
            .order_by(Proiezione.data_ora) \
            .all()

        return [ProiezioneDTO.from_model(p) for p in proiezioni]
