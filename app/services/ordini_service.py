# services/ordini_service.py
from datetime import datetime
from typing import List, Tuple

from flask import current_app
from flask_login import current_user
from sqlalchemy import and_
from ..models import Ordine, Biglietto, Proiezione, db, Film, Posto, Sala
from ..dto.ordini_dto import OrdineDTO


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
            ordini = db.session.query(
                Ordine, Proiezione, Film, Sala
            ).join(Proiezione, Ordine.id_proiezione == Proiezione.id) \
                .join(Film, Proiezione.id_film == Film.id) \
                .join(Sala, Proiezione.id_sala == Sala.id) \
                .filter(Ordine.id_utente == current_user.id) \
                .order_by(Ordine.data_acquisto.desc()) \
                .all()

            # Recuperiamo tutti i biglietti in una sola query
            biglietti = db.session.query(Biglietto, Posto).join(Posto, Biglietto.id_posto == Posto.id).filter(
                Biglietto.id_ordine.in_([ordine.id for ordine, _, _, _ in ordini])
            ).all()

            # Raggruppiamo i biglietti per ordine
            biglietti_dict = {}
            for biglietto, posto in biglietti:
                biglietti_dict.setdefault(biglietto.id_ordine, []).append((biglietto, posto))

            # Creiamo il DTO
            return [
                OrdineDTO.da_modello(ordine, proiezione, film, sala, biglietti_dict.get(ordine.id, []))
                for ordine, proiezione, film, sala in ordini
            ]

        except Exception as e:
            current_app.logger.error(f"Error fetching orders: {str(e)}")
            return []

    @staticmethod
    def cambia_proiezione_e_posti(order_id: int, user_id: int, new_projection_id: int, new_seats: List[dict]):
        # Verifica che l'ordine esista e appartenga all'utente
        ordine = Ordine.query.filter(
            and_(
                Ordine.id == order_id,
                Ordine.id_utente == user_id
            )
        ).first()

        if not ordine:
            raise ValueError("Ordine non trovato")

        # Verifica che la proiezione sia futura
        old_projection = Proiezione.query.get(ordine.id_proiezione)
        new_projection = Proiezione.query.get(new_projection_id)

        if not new_projection:
            raise ValueError("Nuova proiezione non trovata")

        if old_projection.data_ora < datetime.now():
            raise ValueError("Non puoi modificare un ordine per una proiezione passata")

        if new_projection.data_ora < datetime.now():
            raise ValueError("Non puoi spostare l'ordine a una proiezione passata")

        # Verifica che i nuovi posti siano disponibili
        posti_occupati = Biglietto.query.filter_by(id_proiezione=new_projection_id).all()
        posti_occupati_ids = [b.id_posto for b in posti_occupati]

        for new_seat in new_seats:
            if new_seat['id_posto'] in posti_occupati_ids:
                raise ValueError(f"Il posto {new_seat['id_posto']} è già occupato")

        # Aggiorna i biglietti esistenti
        biglietti = Biglietto.query.filter_by(id_ordine=order_id).all()

        if len(biglietti) != len(new_seats):
            raise ValueError("Il numero di nuovi posti non corrisponde al numero di biglietti esistenti")

        try:
            for i, biglietto in enumerate(biglietti):
                biglietto.id_proiezione = new_projection_id
                biglietto.id_posto = new_seats[i]['id_posto']
                if 'nome_ospite' in new_seats[i]:
                    biglietto.nome_ospite = new_seats[i]['nome_ospite']
                if 'cognome_ospite' in new_seats[i]:
                    biglietto.cognome_ospite = new_seats[i]['cognome_ospite']

            ordine.id_proiezione = new_projection_id
            db.session.commit()

            return True, "Proiezione e posti cambiati con successo"

        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Errore durante l'aggiornamento: {str(e)}")

    @staticmethod
    def cambia_posti(order_id: int, user_id: int, new_seats: List[dict]) -> Tuple[bool, str]:
        # Verifica che l'ordine esista e appartenga all'utente
        ordine = Ordine.query.filter(
            and_(
                Ordine.id == order_id,
                Ordine.id_utente == user_id
            )
        ).first()

        if not ordine:
            raise ValueError("Ordine non trovato")

        # Verifica che la proiezione sia futura
        projection = Proiezione.query.get(ordine.id_proiezione)
        if projection.data_ora < datetime.now():
            raise ValueError("Non puoi modificare i posti per una proiezione passata")

        # Verifica che i nuovi posti siano disponibili
        posti_occupati = Biglietto.query.filter_by(id_proiezione=ordine.id_proiezione).all()
        posti_occupati_ids = [b.id_posto for b in posti_occupati]

        for new_seat in new_seats:
            if new_seat['id_posto'] in posti_occupati_ids:
                raise ValueError(f"Il posto {new_seat['id_posto']} è già occupato")

        # Aggiorna i biglietti esistenti
        biglietti = Biglietto.query.filter_by(id_ordine=order_id).all()

        if len(biglietti) != len(new_seats):
            raise ValueError("Il numero di nuovi posti non corrisponde al numero di biglietti esistenti")

        try:
            for i, biglietto in enumerate(biglietti):
                biglietto.id_posto = new_seats[i]['id_posto']
                if 'nome_ospite' in new_seats[i]:
                    biglietto.nome_ospite = new_seats[i]['nome_ospite']
                if 'cognome_ospite' in new_seats[i]:
                    biglietto.cognome_ospite = new_seats[i]['cognome_ospite']

            db.session.commit()

            return True, "Posti cambiati con successo"

        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Errore durante l'aggiornamento: {str(e)}")
