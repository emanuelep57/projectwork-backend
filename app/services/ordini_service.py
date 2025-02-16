from datetime import datetime
from typing import List, Dict

from flask import current_app
from flask_login import current_user
from sqlalchemy import and_

from ..models import Ordine, Biglietto, Proiezione, db, Film, Posto, Sala
from ..dto.ordini_dto import OrdineDTO
from ..utils.pdf_utils import genera_biglietto_pdf
from ..utils.cloudinary_utils import upload_pdf_to_cloudinary


class OrdiniService:
    @staticmethod
    def create_order(user_id: int, projection_id: int) -> Ordine:
        ordine = Ordine(
            id_utente=user_id,
            id_proiezione=projection_id,
            data_acquisto=datetime.now()
        )
        db.session.add(ordine)
        db.session.flush()
        return ordine

    @staticmethod
    def get_ordini_utente() -> List['OrdineDTO']:
        try:
            # Query principale per ottenere ordini e relazioni
            ordini = db.session.query(
                Ordine, Proiezione, Film, Sala
            ).join(
                Proiezione, Ordine.id_proiezione == Proiezione.id
            ).join(
                Film, Proiezione.id_film == Film.id
            ).join(
                Sala, Proiezione.id_sala == Sala.id
            ).filter(
                Ordine.id_utente == current_user.id
            ).order_by(
                Ordine.data_acquisto.desc()
            ).all()

            # Query per ottenere i biglietti relativi
            biglietti = db.session.query(
                Biglietto, Posto
            ).join(
                Posto, Biglietto.id_posto == Posto.id
            ).filter(
                Biglietto.id_ordine.in_([ordine.id for ordine, _, _, _ in ordini])
            ).all()

            # Organizza i biglietti per ordine
            biglietti_per_ordine = {}
            for biglietto, posto in biglietti:
                biglietti_per_ordine.setdefault(biglietto.id_ordine, []).append((biglietto, posto))

            # Crea i DTO
            return [
                OrdineDTO.da_modello(
                    ordine=ordine,
                    proiezione=proiezione,
                    film=film,
                    sala=sala,
                    biglietti=biglietti_per_ordine.get(ordine.id, [])
                )
                for ordine, proiezione, film, sala in ordini
            ]
        except Exception as e:
            current_app.logger.error(f"Error fetching orders: {str(e)}")
            return []

    @staticmethod
    def elimina_ordine(ordine_id: int, user_id: int) -> None:
        ordine = Ordine.query.filter(
            and_(
                Ordine.id == ordine_id,
                Ordine.id_utente == user_id
            )
        ).first()

        if not ordine:
            raise ValueError('Ordine non trovato')

        proiezione = Proiezione.query.get(ordine.id_proiezione)
        if proiezione.data_ora < datetime.now():
            raise ValueError('Non puoi eliminare un ordine per una proiezione passata')

        Biglietto.query.filter_by(id_ordine=ordine_id).delete()
        db.session.delete(ordine)
        db.session.commit()

    @staticmethod
    def aggiungi_biglietti(ordine_id: int, user_id: int, biglietti_data: List[Dict]) -> str:
        ordine = Ordine.query.filter(
            and_(
                Ordine.id == ordine_id,
                Ordine.id_utente == user_id
            )
        ).first()

        if not ordine:
            raise ValueError('Ordine non trovato')

        proiezione = Proiezione.query.get(ordine.id_proiezione)
        if proiezione.data_ora < datetime.now():
            raise ValueError('Non puoi modificare un ordine per una proiezione passata')

        posti_richiesti = [b['id_posto'] for b in biglietti_data]
        posti_occupati = Biglietto.query.filter(
            and_(
                Biglietto.id_proiezione == ordine.id_proiezione,
                Biglietto.id_posto.in_(posti_richiesti),
                Biglietto.id_ordine != ordine.id
            )
        ).all()

        if posti_occupati:
            raise ValueError('Alcuni posti selezionati non sono più disponibili')

        for biglietto_data in biglietti_data:
            nuovo_biglietto = Biglietto(
                id_proiezione=ordine.id_proiezione,
                id_utente=user_id,
                id_posto=biglietto_data['id_posto'],
                id_ordine=ordine.id,
                nome_ospite=biglietto_data.get('nome_ospite'),
                cognome_ospite=biglietto_data.get('cognome_ospite')
            )
            db.session.add(nuovo_biglietto)

        db.session.flush()

        pdf_url = OrdiniService._genera_pdf_ordine(ordine.id)
        ordine.pdf_url = pdf_url
        db.session.commit()

        return pdf_url

    @staticmethod
    def rimuovi_posto(ordine_id: int, user_id: int, id_posto: int) -> str:
        ordine = Ordine.query.filter(
            and_(
                Ordine.id == ordine_id,
                Ordine.id_utente == user_id
            )
        ).first()

        if not ordine:
            raise ValueError('Ordine non trovato')

        proiezione = Proiezione.query.get(ordine.id_proiezione)
        if proiezione.data_ora < datetime.now():
            raise ValueError('Non puoi modificare un ordine per una proiezione passata')

        biglietto = Biglietto.query.filter(
            and_(
                Biglietto.id_ordine == ordine_id,
                Biglietto.id_posto == id_posto,
                Biglietto.id_utente == user_id
            )
        ).first()

        if not biglietto:
            raise ValueError('Biglietto non trovato')

        num_biglietti = Biglietto.query.filter_by(id_ordine=ordine_id).count()
        if num_biglietti <= 1:
            raise ValueError('Non puoi rimuovere l\'ultimo posto di un ordine')

        db.session.delete(biglietto)
        db.session.flush()

        pdf_url = OrdiniService._genera_pdf_ordine(ordine_id)
        ordine.pdf_url = pdf_url
        db.session.commit()

        return pdf_url

    @staticmethod
    def _genera_pdf_ordine(ordine_id: int) -> str:
        tickets_info = (
            db.session.query(Biglietto, Film, Proiezione, Sala, Posto)
            .join(Proiezione, Biglietto.id_proiezione == Proiezione.id)
            .join(Film, Proiezione.id_film == Film.id)
            .join(Sala, Proiezione.id_sala == Sala.id)
            .join(Posto, Biglietto.id_posto == Posto.id)
            .filter(Biglietto.id_ordine == ordine_id)
            .all()
        )

        pdf_buffer = genera_biglietto_pdf(tickets_info, ordine_id)
        return upload_pdf_to_cloudinary(pdf_buffer, f"ticket{ordine_id}{datetime.now()}")