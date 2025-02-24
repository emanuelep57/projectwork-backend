from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PostoInBigliettoDTO:
    id_posto: int
    fila: str
    numero: int
    nome_ospite: Optional[str] = None
    cognome_ospite: Optional[str] = None

    @classmethod
    def from_model(cls, posto, biglietto):
        return cls(
            id_posto=posto.id,
            fila=posto.fila,
            numero=posto.numero,
            nome_ospite=biglietto.nome_ospite,
            cognome_ospite=biglietto.cognome_ospite
        )


@dataclass
class BigliettoDTO:
    id: int
    posti: List[dict]
    nome_ospite: Optional[str] = None
    cognome_ospite: Optional[str] = None

    # qui ho reso film, proiezione, sala e ordine opzionali
    @classmethod
    def from_models(cls, ticket, film=None, proiezione=None, sala=None, ordine=None, posto=None):

        if posto is None:
            raise ValueError("posto parameter is required")

        posti_list = [posto] if not isinstance(posto, list) else posto

        posti_dict = [{
            'id': p.id,
            'fila': p.fila,
            'numero': p.numero,
            'nome_ospite': ticket.nome_ospite,
            'cognome_ospite': ticket.cognome_ospite
        } for p in posti_list]

        return cls(
            id=ticket.id,
            posti=posti_dict,
            nome_ospite=ticket.nome_ospite,
            cognome_ospite=ticket.cognome_ospite
        )

    def to_dict(self):
        return {
            'id': self.id,
            'posti': self.posti,
            'nome_ospite': self.nome_ospite,
            'cognome_ospite': self.cognome_ospite
        }
