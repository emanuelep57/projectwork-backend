from dataclasses import dataclass
from typing import Optional, List
from app.dto.biglietto_dto import BigliettoDTO


@dataclass
class OrdineDTO:
    id: int
    data_acquisto: str
    pdf_url: Optional[str]
    proiezione: dict
    biglietti: List[BigliettoDTO]

    @classmethod
    def da_modello(cls, ordine, proiezione, film, sala, biglietti):
        return cls(
            id=ordine.id,
            data_acquisto=ordine.data_acquisto.isoformat(),
            pdf_url=ordine.pdf_url,
            proiezione={
                'id': proiezione.id,
                'film_id': film.id,
                'film_titolo': film.titolo,
                'data_ora': proiezione.data_ora.isoformat(),
                'costo': float(proiezione.costo),
            },
            biglietti=[
                BigliettoDTO.from_models(ticket, film, proiezione, sala, ordine, posto)
                for ticket, posto in biglietti
            ]
        )

    def to_dict(self):
        return {
            'id': self.id,
            'data_acquisto': self.data_acquisto,
            'pdf_url': self.pdf_url,
            'proiezione': self.proiezione,
            'biglietti': [biglietto.to_dict() for biglietto in self.biglietti]
        }