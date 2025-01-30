from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PostoInBigliettoDTO:
    id: int
    fila: str
    numero: int
    nome_ospite: Optional[str]
    cognome_ospite: Optional[str]

    @classmethod
    def from_model(cls, posto, biglietto):
        return cls(
            id=posto.id,
            fila=posto.fila,
            numero=posto.numero,
            nome_ospite=biglietto.nome_ospite,
            cognome_ospite=biglietto.cognome_ospite
        )


@dataclass
class BigliettoDTO:
    id_biglietto: int
    film_titolo: str
    film_copertina: str
    sala_nome: str
    data_ora: str
    costo: float
    posti: List[PostoInBigliettoDTO]
    pdf_url: Optional[str]

    @classmethod
    def from_models(cls, ticket, film, proiezione, sala, ordine, posto):
        return cls(
            id_biglietto=ticket.id,
            film_titolo=film.titolo,
            film_copertina=film.url_copertina,
            sala_nome=sala.nome,
            data_ora=proiezione.data_ora.isoformat(),
            costo=float(proiezione.costo),
            posti=[PostoInBigliettoDTO.from_model(posto, ticket)],
            pdf_url=ordine.pdf_url
        )
