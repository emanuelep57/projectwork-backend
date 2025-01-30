from datetime import datetime
from dataclasses import dataclass
from ..models import Sala, Proiezione


@dataclass
class ProiezioneDTO:
    id: int
    data_ora: datetime
    costo: float
    sala: str

    @classmethod
    def from_model(cls, proiezione: Proiezione):
        sala_nome = Sala.query.get(proiezione.id_sala).nome
        return cls(
            id=proiezione.id,
            data_ora=proiezione.data_ora,
            costo=proiezione.costo,
            sala=sala_nome
        )

    def to_dict(self):
        return {
            'id': self.id,
            'data_ora': self.data_ora.isoformat(),
            'costo': self.costo,
            'sala': self.sala
        }
