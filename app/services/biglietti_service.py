from datetime import datetime
from typing import List, Tuple
from sqlalchemy import and_
from ..models import Biglietto, Film, Proiezione, Sala, Posto, Ordine, db
from ..cloudinary_utils import upload_pdf_to_cloudinary
from ..pdf_utils import genera_biglietto_pdf
from ..dto.biglietto_dto import BigliettoDTO


class BigliettiService:
    @staticmethod
    def acquista_biglietto(user_id, projection_id, biglietti_data, ordine_id):
        biglietti_acquistati = []
        ticket_ids = []

        for biglietto_data in biglietti_data:
            biglietto = Biglietto(
                id_proiezione=projection_id,
                id_utente=user_id,
                id_posto=biglietto_data['id_posto'],
                id_ordine=ordine_id,
                nome_ospite=biglietto_data.get('nome_ospite'),
                cognome_ospite=biglietto_data.get('cognome_ospite')
            )
            db.session.add(biglietto)
            db.session.flush()
            ticket_ids.append(biglietto.id)
            biglietti_acquistati.append(biglietto)

        tickets_info = (
            db.session.query(Biglietto, Film, Proiezione, Sala, Posto)
            .join(Proiezione, Biglietto.id_proiezione == Proiezione.id)
            .join(Film, Proiezione.id_film == Film.id)
            .join(Sala, Proiezione.id_sala == Sala.id)
            .join(Posto, Biglietto.id_posto == Posto.id)
            .filter(Biglietto.id.in_(ticket_ids))
            .all()
        )

        pdf_buffer = genera_biglietto_pdf(tickets_info, ordine_id)
        pdf_url = upload_pdf_to_cloudinary(pdf_buffer, f"ticket{ordine_id}{datetime.now()}")

        return ticket_ids, pdf_url

    @staticmethod
    def get_user_tickets(user_id: int) -> Tuple[List[BigliettoDTO], List[BigliettoDTO]]:
        now = datetime.now()
        tickets = db.session.query(
            Biglietto, Film, Proiezione, Sala, Ordine
        ).join(Proiezione, Biglietto.id_proiezione == Proiezione.id) \
            .join(Film, Proiezione.id_film == Film.id) \
            .join(Sala, Proiezione.id_sala == Sala.id) \
            .join(Ordine, Biglietto.id_ordine == Ordine.id) \
            .filter(Biglietto.id_utente == user_id) \
            .order_by(Proiezione.data_ora.desc()) \
            .all()

        upcoming_tickets = []
        past_tickets = []

        for ticket, film, proiezione, sala, ordine in tickets:
            posto = Posto.query.filter_by(id=ticket.id_posto).first()
            ticket_dto = BigliettoDTO.from_models(ticket, film, proiezione, sala, ordine, posto)

            if proiezione.data_ora > now:
                upcoming_tickets.append(ticket_dto)
            else:
                past_tickets.append(ticket_dto)

        return upcoming_tickets, past_tickets

    @staticmethod
    def get_ticket_pdfs(user_id: int) -> List[str]:
        orders = Ordine.query.filter_by(id_utente=user_id).all()
        return [order.pdf_url for order in orders if order.pdf_url]

    @staticmethod
    def get_ticket_pdf_url(ticket_id: int, user_id: int) -> str:
        ticket = Biglietto.query.filter(
            and_(
                Biglietto.id == ticket_id,
                Biglietto.id_utente == user_id
            )
        ).first()

        if not ticket:
            raise ValueError('Ticket not found')

        order = Ordine.query.get(ticket.id_ordine)
        if not order or not order.pdf_url:
            raise ValueError('PDF not found')

        return order.pdf_url

    @staticmethod
    def delete_ticket(ticket_id: int, user_id: int):
        ticket = Biglietto.query.filter(
            and_(
                Biglietto.id == ticket_id,
                Biglietto.id_utente == user_id
            )
        ).first()

        if not ticket:
            raise ValueError('Ticket not found')

        proiezione = Proiezione.query.get(ticket.id_proiezione)
        if proiezione.data_ora < datetime.now():
            raise ValueError('Cannot delete ticket for past projections')

        db.session.delete(ticket)
        db.session.commit()
