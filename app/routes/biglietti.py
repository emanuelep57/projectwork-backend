from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_
from datetime import datetime
from .ordini import create_order
from ..cloudinary_utils import upload_pdf_to_cloudinary
from ..genera_pdf import genera_biglietto_pdf
from ..models import (
    Proiezione,
    Posto,
    Biglietto,
    Film,
    Sala,
    db, Ordine
)


bp = Blueprint('biglietti', __name__)


@bp.route('/acquisto', methods=['POST'])
@login_required
def acquista_biglietto():
    data = request.json

    if not data.get('biglietti'):
        return jsonify({'error': 'No tickets provided'}), 400

    try:
        # Create order
        ordine = create_order(
            user_id=current_user.id,
            projection_id=data['id_proiezione']
        )

        # Create tickets
        biglietti_acquistati = []
        ticket_ids = []
        for biglietto_data in data['biglietti']:
            biglietto = Biglietto(
                id_proiezione=data['id_proiezione'],
                id_utente=current_user.id,
                id_posto=biglietto_data['id_posto'],
                id_ordine=ordine.id,
                nome_ospite=biglietto_data.get('nome_ospite'),
                cognome_ospite=biglietto_data.get('cognome_ospite')
            )
            db.session.add(biglietto)
            db.session.flush()  # Get the ID without committing
            ticket_ids.append(biglietto.id)
            biglietti_acquistati.append(biglietto)

        # Generate PDF
        tickets_info = (
            db.session.query(Biglietto, Film, Proiezione, Sala, Posto)
            .join(Proiezione, Biglietto.id_proiezione == Proiezione.id)
            .join(Film, Proiezione.id_film == Film.id)
            .join(Sala, Proiezione.id_sala == Sala.id)
            .join(Posto, Biglietto.id_posto == Posto.id)
            .filter(Biglietto.id.in_(ticket_ids))
            .all()
        )

        pdf_buffer = genera_biglietto_pdf(tickets_info, ordine.id)
        pdf_url = upload_pdf_to_cloudinary(pdf_buffer, "ticket"+str(ordine.id)+str(datetime.now()))

        ordine.pdf_url = pdf_url
        db.session.commit()

        return jsonify({
            'ticket_ids': ticket_ids,
            'pdf_urls': [pdf_url]
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Purchase error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['GET'])
@login_required
def get_user_tickets():
    try:
        now = datetime.now()

        tickets = db.session.query(
            Biglietto, Film, Proiezione, Sala, Ordine
        ).join(Proiezione, Biglietto.id_proiezione == Proiezione.id) \
            .join(Film, Proiezione.id_film == Film.id) \
            .join(Sala, Proiezione.id_sala == Sala.id) \
            .join(Ordine, Biglietto.id_ordine == Ordine.id) \
            .filter(Biglietto.id_utente == current_user.id) \
            .order_by(Proiezione.data_ora.desc()) \
            .all()

        upcoming_tickets = []
        past_tickets = []

        for ticket, film, proiezione, sala, ordine in tickets:
            ticket_info = {
                'id_biglietto': ticket.id,
                'film_titolo': film.titolo,
                'film_copertina': film.url_copertina,
                'sala_nome': sala.nome,
                'data_ora': proiezione.data_ora.isoformat(),
                'costo': proiezione.costo,
                'posti': [
                    {
                        'id': ticket.id_posto,
                        'fila': posto.fila,
                        'numero': posto.numero,
                        'nome_ospite': ticket.nome_ospite,
                        'cognome_ospite': ticket.cognome_ospite
                    } for posto in Posto.query.filter_by(id=ticket.id_posto).all()
                ],
                'pdf_url': ordine.pdf_url  # Now get PDF URL from the order
            }

            if proiezione.data_ora > now:
                upcoming_tickets.append(ticket_info)
            else:
                past_tickets.append(ticket_info)

        return jsonify({
            'upcoming_tickets': upcoming_tickets,
            'past_tickets': past_tickets
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching tickets: {str(e)}")
        return jsonify({'error': 'Failed to retrieve tickets'}), 500


@bp.route('/pdfs', methods=['GET'])
@login_required
def get_ticket_pdfs():
    try:
        orders = Ordine.query.filter_by(id_utente=current_user.id).all()
        pdf_urls = [order.pdf_url for order in orders if order.pdf_url]

        return jsonify({
            'pdf_urls': pdf_urls
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving ticket PDFs: {str(e)}")
        return jsonify({'error': 'Failed to retrieve ticket PDFs'}), 500


@bp.route('/<int:ticket_id>/pdf-url', methods=['GET'])
@login_required
def get_ticket_pdf_url(ticket_id):
    try:
        ticket = Biglietto.query.filter(
            and_(
                Biglietto.id == ticket_id,
                Biglietto.id_utente == current_user.id
            )
        ).first()

        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        # Find the order associated with the ticket
        order = Ordine.query.get(ticket.id_ordine)

        if not order or not order.pdf_url:
            return jsonify({'error': 'PDF not found'}), 404

        return jsonify({
            'pdf_url': order.pdf_url
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error retrieving ticket PDF: {str(e)}")
        return jsonify({'error': 'Failed to retrieve ticket PDF'}), 500


@bp.route('/tickets/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    """
    Delete a ticket if it's for a future projection.

    Args:
    - ticket_id: ID of the ticket to be deleted

    Returns:
    - Success message if ticket is deleted
    - Error message if deletion is not possible
    """
    try:
        # Find the ticket
        ticket = Biglietto.query.filter(
            and_(
                Biglietto.id == ticket_id,
                Biglietto.id_utente == current_user.id
            )
        ).first()

        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        # Check if projection is in the future
        proiezione = Proiezione.query.get(ticket.id_proiezione)
        if proiezione.data_ora < datetime.now():
            return jsonify({'error': 'Cannot delete ticket for past projections'}), 400

        # Delete the ticket
        db.session.delete(ticket)
        db.session.commit()

        return jsonify({'message': 'Ticket successfully deleted'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ticket: {str(e)}")
        return jsonify({'error': 'Failed to delete ticket'}), 500
